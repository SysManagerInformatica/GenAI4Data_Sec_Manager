"""
Create RLS View Page
Create protected RLS views with custom names and filters

VERSION: 1.0
Date: 14/12/2024
Author: Lucas Carvalhal - Sys Manager
"""

import theme
from theme import get_text
from config import Config
from nicegui import ui
from google.cloud import bigquery
from services.audit_service import AuditService
from services.rls_views_service import RLSViewsService


config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class CreateRLSView:
    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.rls_service = RLSViewsService(config.PROJECT_ID)
        
        self.selected_dataset = None
        self.selected_table = None
        self.view_name = None
        self.view_description = None
        
        self.table_schema = []
        self.filters = []  # [{"field": "col", "operator": "=", "value": "val"}]
        self.users = []  # ["user:email@example.com"]
        self.groups = []  # ["group:team@example.com"]
        
        self.filters_container = None
        self.users_container = None
        
        self.headers()
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        
        with self.stepper:
            self.step1()
            self.step2()
            self.step3()
            self.step4()
            self.step5()
    
    def headers(self):
        ui.page_title("Create RLS View")
        ui.label("Create Protected RLS View").classes('text-primary text-center text-bold')
    
    # ==================== STEP 1: Select Table ====================
    
    def step1(self):
        with ui.step("Step 1: Select Source Table"):
            ui.label("Select the source table to protect with RLS").classes('text-caption text-grey-7 mb-4')
            
            # Dataset selector
            datasets = self.get_datasets()
            ui.select(
                options=datasets,
                label="Dataset",
                on_change=self.on_dataset_change
            ).classes('w-full mb-4')
            
            # Table selector
            self.table_select = ui.select(
                options=[],
                label="Table",
                on_change=self.on_table_change
            ).classes('w-full')
            
            with ui.stepper_navigation():
                self.step1_next = ui.button(
                    "NEXT",
                    icon="arrow_forward",
                    on_click=self.stepper.next
                ).props('color=primary')
                self.step1_next.set_visibility(False)
    
    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [d.dataset_id for d in datasets if not d.dataset_id.endswith('_views')]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def on_dataset_change(self, e):
        self.selected_dataset = e.value
        self.selected_table = None
        self.table_select.value = None
        self.step1_next.set_visibility(False)
        
        # Load tables
        try:
            tables = client.list_tables(self.selected_dataset)
            table_names = [t.table_id for t in tables]
            self.table_select.options = table_names
            self.table_select.update()
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
    
    def on_table_change(self, e):
        self.selected_table = e.value
        if e.value:
            self.step1_next.set_visibility(True)
            # Load schema for later use
            self.table_schema = self.rls_service.get_table_schema(
                self.selected_dataset,
                self.selected_table
            )
    
    # ==================== STEP 2: Name View ====================
    
    def step2(self):
        with ui.step("Step 2: Name Your View"):
            ui.label("Choose a name for the protected view").classes('text-caption text-grey-7 mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("ℹ️ Naming Guidelines").classes('font-bold mb-2')
                ui.label("• Use descriptive names (e.g., vw_sales_ti_team)").classes('text-xs')
                ui.label("• Only letters, numbers, and underscores").classes('text-xs')
                ui.label("• Must start with a letter").classes('text-xs')
                ui.label(f"• Will be created in: {self.selected_dataset}_views").classes('text-xs font-bold text-blue-600')
            
            self.view_name_input = ui.input(
                label="View Name",
                placeholder="vw_my_protected_data",
                on_change=self.validate_view_name
            ).classes('w-full mb-4').props('prefix="vw_"')
            
            ui.input(
                label="Description (optional)",
                placeholder="Protected view for TI team",
                on_change=lambda e: setattr(self, 'view_description', e.value)
            ).classes('w-full')
            
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back", on_click=self.stepper.previous).props('flat')
                self.step2_next = ui.button(
                    "NEXT",
                    icon="arrow_forward",
                    on_click=self.stepper.next
                ).props('color=primary')
                self.step2_next.set_visibility(False)
    
    def validate_view_name(self, e):
        name = e.value.strip()
        if name and name.replace('_', '').isalnum() and name[0].isalpha():
            self.view_name = f"vw_{name}"
            self.step2_next.set_visibility(True)
        else:
            self.step2_next.set_visibility(False)
    
    # ==================== STEP 3: Define Filters ====================
    
    def step3(self):
        with ui.step("Step 3: Define Filters"):
            ui.label("Add filter conditions to restrict data").classes('text-caption text-grey-7 mb-4')
            
            with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                ui.label("💡 Filter Examples").classes('font-bold mb-2')
                ui.label("• diretoria = 'TI' → Only TI department").classes('text-xs')
                ui.label("• region IN ('SP', 'RJ') → Only SP and RJ").classes('text-xs')
                ui.label("• salary > 5000 → Salary above 5000").classes('text-xs')
                ui.label("• You can add multiple filters (they will be combined with AND)").classes('text-xs font-bold')
            
            # Add filter form
            with ui.row().classes('w-full gap-2 mb-4'):
                self.filter_field = ui.select(
                    options=[col['name'] for col in self.table_schema],
                    label="Field"
                ).classes('flex-1')
                
                self.filter_operator = ui.select(
                    options=['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN'],
                    label="Operator",
                    value='='
                ).classes('w-32')
                
                self.filter_value = ui.input(
                    label="Value",
                    placeholder="'TI' or 5000"
                ).classes('flex-1')
                
                ui.button(
                    "ADD FILTER",
                    icon="add",
                    on_click=self.add_filter
                ).props('color=positive')
            
            # Filters list
            ui.label("Applied Filters:").classes('font-bold mb-2')
            self.filters_container = ui.column().classes('w-full gap-2')
            self.refresh_filters()
            
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back", on_click=self.stepper.previous).props('flat')
                ui.button("NEXT", icon="arrow_forward", on_click=self.stepper.next).props('color=primary')
    
    def add_filter(self):
        if not self.filter_field.value or not self.filter_value.value:
            ui.notify("Please fill all fields", type="warning")
            return
        
        self.filters.append({
            'field': self.filter_field.value,
            'operator': self.filter_operator.value,
            'value': self.filter_value.value
        })
        
        self.filter_value.value = ''
        self.refresh_filters()
        ui.notify("Filter added!", type="positive")
    
    def refresh_filters(self):
        self.filters_container.clear()
        
        with self.filters_container:
            if not self.filters:
                ui.label("⚠️ No filters added yet (view will show all rows)").classes('text-orange-600 italic')
            else:
                for i, f in enumerate(self.filters):
                    with ui.card().classes('w-full p-3 bg-blue-50'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label(f"{f['field']} {f['operator']} {f['value']}").classes('font-mono')
                            ui.button(
                                icon="delete",
                                on_click=lambda idx=i: self.remove_filter(idx)
                            ).props('flat dense color=negative')
    
    def remove_filter(self, index):
        self.filters.pop(index)
        self.refresh_filters()
        ui.notify("Filter removed", type="info")
    
    # ==================== STEP 4: Add Users/Groups ====================
    
    def step4(self):
        with ui.step("Step 4: Add Users and Groups"):
            ui.label("Specify who can access this view").classes('text-caption text-grey-7 mb-4')
            
            with ui.card().classes('w-full bg-purple-50 p-4 mb-4'):
                ui.label("👥 Access Control").classes('font-bold mb-2')
                ui.label("• Add individual users: user@example.com").classes('text-xs')
                ui.label("• Add groups: group@example.com").classes('text-xs')
                ui.label("• Only these users/groups will see data (RLS applied)").classes('text-xs font-bold text-purple-600')
            
            # Add user form
            ui.label("Add Users:").classes('font-bold mt-4 mb-2')
            with ui.row().classes('w-full gap-2 mb-4'):
                self.user_input = ui.input(
                    label="User Email",
                    placeholder="user@example.com"
                ).classes('flex-1')
                
                ui.button(
                    "ADD USER",
                    icon="person_add",
                    on_click=self.add_user
                ).props('color=primary')
            
            # Add group form
            ui.label("Add Groups:").classes('font-bold mt-4 mb-2')
            with ui.row().classes('w-full gap-2 mb-4'):
                self.group_input = ui.input(
                    label="Group Email",
                    placeholder="team@example.com"
                ).classes('flex-1')
                
                ui.button(
                    "ADD GROUP",
                    icon="group_add",
                    on_click=self.add_group
                ).props('color=primary')
            
            # Users/Groups list
            ui.separator().classes('my-4')
            ui.label("Authorized Users & Groups:").classes('font-bold mb-2')
            self.users_container = ui.column().classes('w-full gap-2')
            self.refresh_users()
            
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back", on_click=self.stepper.previous).props('flat')
                self.step4_next = ui.button(
                    "NEXT",
                    icon="arrow_forward",
                    on_click=self.stepper.next
                ).props('color=primary')
                self.step4_next.set_visibility(len(self.users) + len(self.groups) > 0)
    
    def add_user(self):
        email = self.user_input.value.strip()
        if not email or '@' not in email:
            ui.notify("Invalid email", type="warning")
            return
        
        user_entry = f"user:{email}"
        if user_entry not in self.users:
            self.users.append(user_entry)
            self.user_input.value = ''
            self.refresh_users()
            ui.notify(f"User {email} added!", type="positive")
        else:
            ui.notify("User already added", type="warning")
    
    def add_group(self):
        email = self.group_input.value.strip()
        if not email or '@' not in email:
            ui.notify("Invalid email", type="warning")
            return
        
        group_entry = f"group:{email}"
        if group_entry not in self.groups:
            self.groups.append(group_entry)
            self.group_input.value = ''
            self.refresh_users()
            ui.notify(f"Group {email} added!", type="positive")
        else:
            ui.notify("Group already added", type="warning")
    
    def refresh_users(self):
        self.users_container.clear()
        
        with self.users_container:
            all_entries = self.users + self.groups
            
            if not all_entries:
                ui.label("⚠️ No users or groups added yet!").classes('text-orange-600 font-bold')
            else:
                for entry in all_entries:
                    with ui.card().classes('w-full p-3 bg-green-50'):
                        with ui.row().classes('w-full items-center justify-between'):
                            icon = "👤" if entry.startswith("user:") else "👥"
                            label = entry.replace("user:", "").replace("group:", "")
                            ui.label(f"{icon} {label}").classes('font-mono')
                            ui.button(
                                icon="delete",
                                on_click=lambda e=entry: self.remove_entry(e)
                            ).props('flat dense color=negative')
        
        # Update step4 next button visibility
        if hasattr(self, 'step4_next'):
            self.step4_next.set_visibility(len(self.users) + len(self.groups) > 0)
    
    def remove_entry(self, entry):
        if entry in self.users:
            self.users.remove(entry)
        if entry in self.groups:
            self.groups.remove(entry)
        self.refresh_users()
        ui.notify("Removed", type="info")
    
    # ==================== STEP 5: Review and Create ====================
    
    def step5(self):
        with ui.step("Step 5: Review and Create"):
            ui.label("Review your RLS view configuration").classes('text-caption text-grey-7 mb-4')
            
            self.review_container = ui.column().classes('w-full gap-4')
            
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back", on_click=self.stepper.previous).props('flat')
                ui.button(
                    "CREATE VIEW",
                    icon="check_circle",
                    on_click=self.create_view
                ).props('color=positive size=lg')
    
    def create_view(self):
        # Show review before creating
        self.show_review()
    
    def show_review(self):
        """Show review dialog"""
        self.review_container.clear()
        
        with self.review_container:
            # Summary cards
            with ui.card().classes('w-full p-4 bg-blue-50'):
                ui.label("📋 Configuration Summary").classes('text-h6 font-bold mb-3')
                
                ui.label(f"View Name: {self.view_name}").classes('font-bold')
                ui.label(f"Dataset: {self.selected_dataset}_views").classes('text-sm')
                ui.label(f"Source: {self.selected_dataset}.{self.selected_table}").classes('text-sm')
                
                if self.view_description:
                    ui.label(f"Description: {self.view_description}").classes('text-sm')
            
            # Filters
            with ui.card().classes('w-full p-4 bg-green-50'):
                ui.label(f"🔍 Filters ({len(self.filters)})").classes('font-bold mb-2')
                if self.filters:
                    for f in self.filters:
                        ui.label(f"• {f['field']} {f['operator']} {f['value']}").classes('font-mono text-sm')
                else:
                    ui.label("No filters (all rows visible)").classes('text-sm italic')
            
            # Users
            with ui.card().classes('w-full p-4 bg-purple-50'):
                ui.label(f"👥 Authorized ({len(self.users) + len(self.groups)})").classes('font-bold mb-2')
                for entry in self.users + self.groups:
                    icon = "👤" if entry.startswith("user:") else "👥"
                    label = entry.replace("user:", "").replace("group:", "")
                    ui.label(f"{icon} {label}").classes('font-mono text-sm')
            
            # SQL Preview
            with ui.card().classes('w-full p-4 bg-gray-50'):
                ui.label("📝 Generated SQL").classes('font-bold mb-2')
                sql = self.generate_preview_sql()
                ui.code(sql, language='sql').classes('text-xs')
            
            # Confirm button
            with ui.row().classes('w-full justify-center gap-4 mt-4'):
                ui.button(
                    "CONFIRM AND CREATE",
                    icon="rocket_launch",
                    on_click=self.execute_creation
                ).props('color=positive size=lg')
    
    def generate_preview_sql(self):
        """Generate SQL preview"""
        where_clauses = []
        for f in self.filters:
            where_clauses.append(f"{f['field']} {f['operator']} {f['value']}")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"
        
        users_list = self.users + self.groups
        grant_to = ", ".join([f'"{u}"' for u in users_list])
        
        sql = f"""-- Step 1: Create View
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}_views.{self.view_name}` AS
SELECT *
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`
WHERE {where_clause};

-- Step 2: Apply RLS Policy
CREATE OR REPLACE ROW ACCESS POLICY `rls_{self.view_name}`
ON `{self.project_id}.{self.selected_dataset}_views.{self.view_name}`
GRANT TO ({grant_to})
FILTER USING (TRUE);

-- Step 3: Configure as Authorized View
-- (Automatic - view will be authorized on {self.selected_dataset})
"""
        return sql
    
    def execute_creation(self):
        """Execute view creation"""
        n = ui.notification("Creating RLS view...", spinner=True, timeout=None)
        
        try:
            # Create view using service
            result = self.rls_service.create_rls_view(
                view_name=self.view_name,
                base_dataset=self.selected_dataset,
                base_table=self.selected_table,
                filters=self.filters,
                users=self.users + self.groups,
                description=self.view_description or ""
            )
            
            if result:
                # Log success
                self.audit_service.log_action(
                    action='CREATE_RLS_VIEW',
                    resource_type='RLS_VIEW',
                    resource_name=self.view_name,
                    status='SUCCESS',
                    details={
                        'view_name': self.view_name,
                        'base_dataset': self.selected_dataset,
                        'base_table': self.selected_table,
                        'filters_count': len(self.filters),
                        'users_count': len(self.users) + len(self.groups),
                        'filters': self.filters,
                        'users': self.users + self.groups
                    }
                )
                
                n.dismiss()
                
                with ui.dialog() as success_dialog, ui.card():
                    ui.label("✅ RLS View Created Successfully!").classes('text-h5 font-bold text-green-600 mb-4')
                    ui.label(f"View: {result}").classes('font-mono mb-4')
                    
                    with ui.card().classes('w-full bg-green-50 p-4'):
                        ui.label("📊 What was created:").classes('font-bold mb-2')
                        ui.label(f"✅ View in dataset: {self.selected_dataset}_views").classes('text-sm')
                        ui.label(f"✅ RLS policy applied").classes('text-sm')
                        ui.label(f"✅ Authorized view configured").classes('text-sm')
                        ui.label(f"✅ Access granted to {len(self.users) + len(self.groups)} users/groups").classes('text-sm')
                    
                    with ui.row().classes('w-full justify-center gap-2 mt-4'):
                        ui.button("CREATE ANOTHER", on_click=lambda: ui.navigate.reload()).props('flat')
                        ui.button("GO TO MANAGE VIEWS", on_click=lambda: ui.navigate.to('/rls/manage-views')).props('color=primary')
                
                success_dialog.open()
            else:
                n.dismiss()
                ui.notify("❌ Error creating view", type="negative")
                
        except Exception as e:
            n.dismiss()
            
            # Log failure
            self.audit_service.log_action(
                action='CREATE_RLS_VIEW',
                resource_type='RLS_VIEW',
                resource_name=self.view_name,
                status='FAILED',
                error_message=str(e)
            )
            
            ui.notify(f"❌ Error: {str(e)}", type="negative")
            import traceback
            traceback.print_exc()
    
    def run(self):
        with theme.frame('RLS - Create Protected View'):
            pass
