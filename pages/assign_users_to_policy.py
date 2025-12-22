# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
================================================================================
  GenAI4Data Security Manager
  Module: RLS Policy Assignment - Unified Interface
================================================================================
  Version:      3.0.0
  Release Date: 2024-12-22
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Unified interface for managing RLS policies with support for users, groups,
  and service accounts. Includes view field editing and filter management.
  
  New Features (v3.0):
  - Unified interface for Users/Groups/Service Accounts
  - Edit view filter field dynamically
  - Manage filter values with usage statistics
  - Improved UX with tabs and real-time updates
================================================================================
"""

import theme
from theme import get_text
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService
import json
import re

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)

class RLSAssignUserstoPolicy:
    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Assign to Policy - Unified"
        self.selected_policy_name = None
        self.selected_policy_dataset = None
        self.selected_policy_table = None
        self.selected_policy_field = None
        self.selected_policy = {}
        
        # View-related attributes (for RLS views)
        self.selected_view_name = None
        self.selected_views_dataset = None
        self.selected_base_dataset = None
        self.selected_base_table = None
        self.is_rls_view = False
        
        self.existing_policies_grid = None
        self.headers()
        self.stepper_setup()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label("Manage RLS Policy Assignments").classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Step 1: Select Policy"
        self.step2_title = "Step 2: Manage Assignments"

        with self.stepper:
            self.step1()
            self.step2_with_tabs()

    def get_policies(self):
        """Load all RLS policies (both traditional and view-based)"""
        query = f"""
        SELECT
          policy_name as `Policy Name`,
          project_id as `Project ID`,
          dataset_id as `Dataset ID`,
          table_name as `Table Name`,
          field_id as `Field ID`
        FROM `{config.POLICY_TABLE}` 
        WHERE policy_type = 'users'
        ORDER BY policy_name
        """
        try:
            query_job = client.query(query)
            results = [dict(row) for row in query_job]
            return results
        except Exception as e:
            ui.notify(f"Error loading policies: {e}", type="negative")
            return []

    def load_existing_assignments(self):
        """Load ALL assignments (users, groups, service accounts)"""
        if not self.selected_policy_dataset or not self.selected_policy_table:
            return []
        
        query = f"""
        SELECT 
            rls_type,
            COALESCE(username, rls_group, '') as identity,
            filter_value,
            field_id,
            CAST(created_at AS STRING) as created_at
        FROM `{config.FILTER_TABLE}`
        WHERE project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
        ORDER BY rls_type, identity, filter_value
        """
        
        try:
            query_job = client.query(query)
            results = []
            for row in query_job:
                # Determine type label
                if row.rls_type == 'users':
                    type_icon = '👤 User'
                elif row.rls_type == 'group':
                    type_icon = '👥 Group'
                else:
                    type_icon = '🤖 SA'
                
                results.append({
                    'type': type_icon,
                    'rls_type': row.rls_type,
                    'identity': row.identity,
                    'filter_value': row.filter_value if row.filter_value else '(All data)',
                    'field_id': row.field_id,
                    'created_at': row.created_at
                })
            return results
        except Exception as e:
            ui.notify(f"Error loading assignments: {e}", type="negative")
            return []

    def get_filter_value_stats(self):
        """Get statistics about filter value usage"""
        if not self.selected_policy_dataset or not self.selected_policy_table:
            return []
        
        query = f"""
        SELECT 
            filter_value,
            COUNT(DISTINCT COALESCE(username, rls_group)) as user_count,
            COUNT(*) as total_assignments
        FROM `{config.FILTER_TABLE}`
        WHERE project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
          AND filter_value IS NOT NULL
          AND filter_value != ''
        GROUP BY filter_value
        ORDER BY user_count DESC, filter_value
        """
        
        try:
            query_job = client.query(query)
            return [dict(row) for row in query_job]
        except Exception as e:
            print(f"Error getting filter stats: {e}")
            return []

    def get_table_fields(self):
        """Get available fields from the source table"""
        try:
            table_ref = client.dataset(self.selected_policy_dataset).table(self.selected_policy_table)
            table = client.get_table(table_ref)
            return [field.name for field in table.schema]
        except Exception as e:
            print(f"Error getting fields: {e}")
            return []

    def delete_assignment(self, identity, filter_value, rls_type):
        """Delete a single assignment"""
        try:
            # Handle empty filter_value
            filter_condition = "AND filter_value = ''" if not filter_value or filter_value == '(All data)' else f"AND filter_value = '{filter_value}'"
            
            # Determine column to filter by
            identity_column = 'username' if rls_type == 'users' else 'rls_group'
            
            query = f"""
            DELETE FROM `{config.FILTER_TABLE}`
            WHERE rls_type = '{rls_type}'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{self.selected_policy_dataset}'
              AND table_id = '{self.selected_policy_table}'
              AND {identity_column} = '{identity}'
              {filter_condition}
            """
            
            client.query(query).result()
            
            self.audit_service.log_action(
                action='DELETE_ASSIGNMENT',
                resource_type='RLS_ASSIGNMENT',
                resource_name=f"{identity} → {filter_value}",
                status='SUCCESS',
                details={
                    'type': rls_type,
                    'identity': identity,
                    'filter_value': filter_value
                }
            )
            
            ui.notify(f"✅ Deleted: {identity}", type="positive")
            self.refresh_assignments_grid()
            
        except Exception as e:
            ui.notify(f"Error deleting assignment: {e}", type="negative")

    def add_assignment(self, identity_type, email, filter_value):
        """Add assignment (user, group, or SA)"""
        try:
            # Validate email
            if not email or '@' not in email:
                ui.notify("Invalid email/identity", type="warning")
                return False
            
            # Handle empty filter (all data access)
            if filter_value == '(No filter - All data)' or not filter_value:
                filter_value = ''
            
            # Determine columns based on type
            if identity_type == 'user':
                rls_type = 'users'
                identity_column = 'username'
            elif identity_type == 'group':
                rls_type = 'group'
                identity_column = 'rls_group'
            else:  # service account
                rls_type = 'users'  # SAs are treated as users in the system
                identity_column = 'username'
            
            # Insert query
            query = f"""
            INSERT INTO `{config.FILTER_TABLE}` 
            (rls_type, policy_name, project_id, dataset_id, table_id, 
             field_id, filter_value, {identity_column}, created_at)
            VALUES
            ('{rls_type}', '{self.selected_policy_name}', '{self.project_id}', 
             '{self.selected_policy_dataset}', '{self.selected_policy_table}', 
             '{self.selected_policy_field}', '{filter_value}', '{email}', CURRENT_TIMESTAMP())
            """
            
            client.query(query).result()
            
            self.audit_service.log_action(
                action='ADD_ASSIGNMENT',
                resource_type='RLS_ASSIGNMENT',
                resource_name=f"{email} → {filter_value if filter_value else 'All data'}",
                status='SUCCESS',
                details={
                    'type': identity_type,
                    'identity': email,
                    'filter_value': filter_value,
                    'policy': self.selected_policy_name
                }
            )
            
            ui.notify(f"✅ Added: {email}", type="positive")
            return True
            
        except Exception as e:
            ui.notify(f"Error adding assignment: {e}", type="negative")
            return False

    def change_view_field(self, new_field):
        """Change the filter field of the RLS view"""
        try:
            ui.notify("Updating view field...", type="info", timeout=2000)
            
            # Get current view SQL
            view_ref = client.dataset(self.selected_views_dataset).table(self.selected_view_name)
            view = client.get_table(view_ref)
            
            # Extract metadata
            metadata_match = re.search(r'RLS_METADATA:(\{.*\})', view.description)
            if metadata_match:
                rls_metadata = json.loads(metadata_match.group(1))
            else:
                rls_metadata = {}
            
            # Get field type
            table_ref = client.dataset(self.selected_policy_dataset).table(self.selected_policy_table)
            table = client.get_table(table_ref)
            field_type = None
            for schema_field in table.schema:
                if schema_field.name == new_field:
                    field_type = schema_field.field_type
                    break
            
            if not field_type:
                ui.notify(f"Field {new_field} not found in table schema", type="negative")
                return False
            
            # Create new view SQL with updated field
            new_sql = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_views_dataset}.{self.selected_view_name}` AS
            SELECT *
            FROM `{self.project_id}.{self.selected_policy_dataset}.{self.selected_policy_table}`
            WHERE {new_field} IN (
              SELECT CAST(filter_value AS {field_type})
              FROM `{config.FILTER_TABLE}`
              WHERE rls_type = 'users'
                AND project_id = '{self.project_id}'
                AND dataset_id = '{self.selected_policy_dataset}'
                AND table_id = '{self.selected_policy_table}'
                AND field_id = '{new_field}'
                AND username = SESSION_USER()
            );
            """
            
            # Execute
            client.query(new_sql).result()
            
            # Update metadata
            rls_metadata['filter_field'] = new_field
            rls_metadata['filter_field_type'] = field_type
            
            view.description = (
                f"RLS view for users - filters by {new_field}\n"
                f"Base table: {self.selected_policy_dataset}.{self.selected_policy_table}\n\n"
                f"RLS_METADATA:{json.dumps(rls_metadata)}"
            )
            client.update_table(view, ['description'])
            
            # Update policy table
            query = f"""
            UPDATE `{config.POLICY_TABLE}`
            SET field_id = '{new_field}'
            WHERE policy_name = '{self.selected_policy_name}'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{self.selected_policy_dataset}'
              AND table_name = '{self.selected_policy_table}'
            """
            client.query(query).result()
            
            # Update filter table
            query = f"""
            UPDATE `{config.FILTER_TABLE}`
            SET field_id = '{new_field}'
            WHERE policy_name = '{self.selected_policy_name}'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{self.selected_policy_dataset}'
              AND table_id = '{self.selected_policy_table}'
            """
            client.query(query).result()
            
            self.audit_service.log_action(
                action='CHANGE_VIEW_FIELD',
                resource_type='RLS_VIEW',
                resource_name=self.selected_view_name,
                status='SUCCESS',
                details={
                    'old_field': self.selected_policy_field,
                    'new_field': new_field,
                    'view': f"{self.selected_views_dataset}.{self.selected_view_name}"
                }
            )
            
            # Update local state
            self.selected_policy_field = new_field
            
            ui.notify(f"✅ View field changed to: {new_field}", type="positive", timeout=3000)
            return True
            
        except Exception as e:
            ui.notify(f"Error changing field: {e}", type="negative")
            return False

    def refresh_assignments_grid(self):
        """Refresh the assignments grid"""
        if self.existing_policies_grid:
            data = self.load_existing_assignments()
            self.existing_policies_grid.options['rowData'] = data
            self.existing_policies_grid.update()

    async def delete_selected_assignments(self):
        """Delete selected assignments"""
        rows = await self.existing_policies_grid.get_selected_rows()
        if not rows:
            ui.notify("No assignments selected", type="warning")
            return
        
        for row in rows:
            self.delete_assignment(
                row['identity'],
                row['filter_value'],
                row['rls_type']
            )

    async def get_selected_row(self):
        """Handle row selection in step 1"""
        rows = await self.grid_step1.get_selected_rows()
        if not rows:
            self.step1_next_button.set_visibility(False)
            return

        if len(rows) == 1:
            self.selected_policy = [dict(row) for row in rows]
            self.step1_next_button.set_visibility(True)
        else:
            self.step1_next_button.set_visibility(False)

    def update_policy_values(self):
        """Load policy details and check if it's a view"""
        if not self.selected_policy:
            ui.notify("No policy selected", type="warning")
            return

        self.selected_policy_name = self.selected_policy[0]['Policy Name']
        self.selected_policy_dataset = self.selected_policy[0]['Dataset ID']
        self.selected_policy_table = self.selected_policy[0]['Table Name']
        self.selected_policy_field = self.selected_policy[0]['Field ID']
        
        # Check if this is an RLS view
        self.check_if_rls_view()
        
        self.stepper.next()

    def check_if_rls_view(self):
        """Check if the policy is for an RLS view"""
        try:
            # Try to find view in _views dataset
            views_dataset = f"{self.selected_policy_dataset}_views"
            
            # List views in the views dataset
            tables = client.list_tables(views_dataset)
            
            for table in tables:
                if table.table_type == 'VIEW':
                    # Get view details
                    view_ref = client.dataset(views_dataset).table(table.table_id)
                    view = client.get_table(view_ref)
                    
                    # Check if this view matches our policy
                    if view.description and 'RLS_METADATA' in view.description:
                        metadata_match = re.search(r'RLS_METADATA:(\{.*\})', view.description)
                        if metadata_match:
                            metadata = json.loads(metadata_match.group(1))
                            if (metadata.get('policy_name') == self.selected_policy_name or
                                (metadata.get('base_dataset') == self.selected_policy_dataset and
                                 metadata.get('base_table') == self.selected_policy_table)):
                                
                                # This is an RLS view!
                                self.is_rls_view = True
                                self.selected_view_name = table.table_id
                                self.selected_views_dataset = views_dataset
                                self.selected_base_dataset = metadata.get('base_dataset')
                                self.selected_base_table = metadata.get('base_table')
                                return
            
            # Not an RLS view
            self.is_rls_view = False
            
        except Exception as e:
            print(f"Error checking for RLS view: {e}")
            self.is_rls_view = False

    def step1(self):
        """Step 1: Select Policy"""
        with ui.step(self.step1_title):
            ui.label("Select an RLS policy to manage").classes('text-caption text-grey-7 mb-2')
            
            policy_list = self.get_policies()

            self.grid_step1 = ui.aggrid({
                'columnDefs': [
                    {'field': 'Policy Name', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 350},
                    {'field': 'Dataset ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Table Name', 'filter': 'agTextColumnFilter'},
                    {'field': 'Field ID', 'filter': 'agTextColumnFilter'}
                ],
                'rowData': policy_list,
                'rowSelection': 'single',
            }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_row)

            with ui.stepper_navigation():
                self.step1_next_button = ui.button(
                    "NEXT",
                    icon="arrow_forward_ios",
                    on_click=self.update_policy_values
                )
                self.step1_next_button.set_visibility(False)

    def step2_with_tabs(self):
        """Step 2: Manage Assignments with 3 tabs"""
        with ui.step(self.step2_title):
            # Policy info card
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("📋 Selected Policy").classes('font-bold mb-2')
                ui.label().bind_text_from(self, 'selected_policy_name', lambda x: f"Policy: {x if x else 'None'}").classes('text-sm')
                ui.label().bind_text_from(self, 'selected_policy_dataset', lambda x: f"Dataset: {x if x else 'None'}").classes('text-sm')
                ui.label().bind_text_from(self, 'selected_policy_table', lambda x: f"Table: {x if x else 'None'}").classes('text-sm')
                ui.label().bind_text_from(self, 'selected_policy_field', lambda x: f"Filter Field: {x if x else 'None'}").classes('text-sm font-bold text-blue-700')
            
            # Tabs
            with ui.tabs().classes('w-full') as tabs:
                tab_assignments = ui.tab("👥 Assignments", icon='people')
                tab_add = ui.tab("➕ Add New", icon='add_circle')
                tab_config = ui.tab("⚙️ Configuration", icon='settings')
            
            with ui.tab_panels(tabs, value=tab_assignments).classes('w-full'):
                # ========================================
                # TAB 1: CURRENT ASSIGNMENTS
                # ========================================
                with ui.tab_panel(tab_assignments):
                    ui.label("Current Assignments").classes('text-h6 font-bold mb-2')
                    ui.label("Select rows to delete").classes('text-caption text-grey-7 mb-4')
                    
                    existing_data = self.load_existing_assignments()
                    
                    self.existing_policies_grid = ui.aggrid({
                        'columnDefs': [
                            {'field': 'type', 'headerName': 'Type', 'width': 120},
                            {'field': 'identity', 'headerName': 'Identity (Email)', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 300},
                            {'field': 'filter_value', 'headerName': 'Filter Value', 'filter': 'agTextColumnFilter'},
                            {'field': 'created_at', 'headerName': 'Created', 'filter': 'agTextColumnFilter'},
                        ],
                        'rowData': existing_data,
                        'rowSelection': 'multiple',
                    }).classes('w-full max-h-96 ag-theme-quartz')
                    
                    with ui.row().classes('mt-4 gap-2'):
                        ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_assignments).props('color=negative')
                        ui.button("REFRESH", icon="refresh", on_click=self.refresh_assignments_grid).props('flat')
                
                # ========================================
                # TAB 2: ADD NEW (UNIFIED INTERFACE)
                # ========================================
                with ui.tab_panel(tab_add):
                    ui.label("Add New Assignment").classes('text-h6 font-bold mb-2')
                    ui.label("Unified interface for Users, Groups, and Service Accounts").classes('text-caption text-grey-7 mb-4')
                    
                    with ui.card().classes('w-full bg-green-50 p-6'):
                        # Type selector
                        with ui.row().classes('w-full gap-4 items-center mb-4'):
                            ui.label("Type:").classes('font-bold')
                            identity_type_select = ui.select(
                                options=[
                                    {'label': '👤 User', 'value': 'user'},
                                    {'label': '👥 Group', 'value': 'group'},
                                    {'label': '🤖 Service Account', 'value': 'service_account'}
                                ],
                                value='user'
                            ).classes('flex-1').props('emit-value map-options')
                        
                        # Email input
                        with ui.row().classes('w-full gap-4 items-center mb-4'):
                            ui.label("Email:").classes('font-bold w-24')
                            email_input = ui.input(
                                placeholder="user@example.com or group@example.com or sa@project.iam.gserviceaccount.com"
                            ).classes('flex-1')
                        
                        # Filter value selector
                        with ui.row().classes('w-full gap-4 items-center mb-4'):
                            ui.label("Filter:").classes('font-bold w-24')
                            
                            # Get existing filter values
                            stats = self.get_filter_value_stats()
                            filter_options = ['(No filter - All data)'] + [s['filter_value'] for s in stats]
                            
                            filter_value_select = ui.select(
                                options=filter_options,
                                value=filter_options[0]
                            ).classes('flex-1')
                        
                        # Add button
                        async def add_new_assignment():
                            success = await run.io_bound(
                                self.add_assignment,
                                identity_type_select.value,
                                email_input.value,
                                filter_value_select.value
                            )
                            if success:
                                email_input.value = ''
                                self.refresh_assignments_grid()
                        
                        with ui.row().classes('w-full justify-end'):
                            ui.button("ADD ASSIGNMENT", icon="add", on_click=add_new_assignment).props('color=primary')
                    
                    # Info card
                    with ui.card().classes('w-full bg-blue-50 p-4 mt-4'):
                        ui.label("💡 How it works:").classes('font-bold mb-2')
                        ui.label("• Users: Individual user accounts").classes('text-xs')
                        ui.label("• Groups: Email groups (e.g., ti-team@company.com)").classes('text-xs')
                        ui.label("• Service Accounts: System identities (e.g., app@project.iam.gserviceaccount.com)").classes('text-xs')
                        ui.label("• Filter: Restrict data access (or 'No filter' for all data)").classes('text-xs')
                
                # ========================================
                # TAB 3: CONFIGURATION
                # ========================================
                with ui.tab_panel(tab_config):
                    ui.label("Policy Configuration").classes('text-h6 font-bold mb-2')
                    
                    # ========== SECTION 1: EDIT FIELD ==========
                    with ui.card().classes('w-full bg-purple-50 p-6 mb-4'):
                        ui.label("🔧 Edit Filter Field").classes('font-bold text-lg mb-4')
                        
                        if self.is_rls_view:
                            ui.label(f"Current field: {self.selected_policy_field}").classes('text-sm mb-4')
                            
                            # Get available fields
                            available_fields = self.get_table_fields()
                            
                            with ui.row().classes('w-full gap-4 items-center'):
                                ui.label("New field:").classes('font-bold')
                                new_field_select = ui.select(
                                    options=available_fields,
                                    value=self.selected_policy_field
                                ).classes('flex-1')
                                
                                async def change_field():
                                    if new_field_select.value == self.selected_policy_field:
                                        ui.notify("Field is already set to this value", type="info")
                                        return
                                    
                                    success = await run.io_bound(
                                        self.change_view_field,
                                        new_field_select.value
                                    )
                                    if success:
                                        # Refresh page to show new field
                                        ui.navigate.reload()
                                
                                ui.button("CHANGE FIELD", icon="edit", on_click=change_field).props('color=primary')
                            
                            with ui.card().classes('w-full bg-yellow-50 p-3 mt-4'):
                                ui.label("⚠️ Changing the field will:").classes('text-xs font-bold mb-2')
                                ui.label("• Update the RLS view SQL").classes('text-xs')
                                ui.label("• Change how data is filtered").classes('text-xs')
                                ui.label("• Existing assignments remain but use new field").classes('text-xs')
                        else:
                            with ui.card().classes('w-full bg-yellow-50 p-4'):
                                ui.label("ℹ️ Field editing is only available for RLS views").classes('text-sm')
                                ui.label(f"This policy uses traditional RLS (not view-based)").classes('text-xs')
                    
                    # ========== SECTION 2: MANAGE FILTERS ==========
                    with ui.card().classes('w-full bg-orange-50 p-6'):
                        ui.label("🔍 Manage Filter Values").classes('font-bold text-lg mb-4')
                        
                        # Get filter statistics
                        stats = self.get_filter_value_stats()
                        
                        if stats:
                            ui.label(f"Current filter values: {len(stats)}").classes('text-sm font-bold mb-2')
                            
                            # Display filter stats
                            for stat in stats:
                                with ui.row().classes('w-full items-center justify-between p-2 border rounded bg-white'):
                                    with ui.column():
                                        ui.label(stat['filter_value']).classes('font-bold')
                                        ui.label(f"{stat['user_count']} identities, {stat['total_assignments']} assignments").classes('text-xs text-grey-7')
                        else:
                            ui.label("No filter values defined yet").classes('text-sm text-grey-7 italic')
                        
                        # Add new filter value
                        ui.separator().classes('my-4')
                        ui.label("Add new filter value:").classes('font-bold mb-2')
                        
                        with ui.row().classes('w-full gap-2'):
                            new_filter_input = ui.input(placeholder="e.g., TI, RH, Operações").classes('flex-1')
                            
                            def add_filter_info():
                                value = new_filter_input.value.strip()
                                if value:
                                    ui.notify(f"ℹ️ Filter value '{value}' added to dropdown in 'Add New' tab", type="info")
                                    new_filter_input.value = ''
                                    # In reality, this just informs the user - they add it via Add New tab
                                else:
                                    ui.notify("Enter a filter value", type="warning")
                            
                            ui.button("ADD TO DROPDOWN", on_click=add_filter_info).props('color=primary outline')
                        
                        with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                            ui.label("💡 Note: Filter values are added when you assign users").classes('text-xs')
                            ui.label("Use the 'Add New' tab to create assignments with filter values").classes('text-xs')

            # Navigation
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)

    def run(self):
        with theme.frame("Assign to Policy - Unified"):
            pass
