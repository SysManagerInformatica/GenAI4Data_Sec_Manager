"""
RLS Manager - COMPLETE AND UNIFIED - FINAL FIXED
Manage RLS-protected views, users, and filters in one place

VERSION: 3.2 - FINAL FIXES
Date: 15/12/2024
Author: Lucas Carvalhal - Sys Manager

FIXES:
- Filter value now optional when adding users
- Detects existing RLS filters from VIEW SQL
- Improved filter extraction from WHERE clause
"""

import theme
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from services.audit_service import AuditService
from services.rls_views_service import RLSViewsService
import asyncio
import traceback
import re


config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class ManageRLSViews:
    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.rls_service = RLSViewsService(config.PROJECT_ID)
        
        self.selected_dataset = None
        self.rls_views = []
        self.views_grid = None
        self.dataset_select = None
        
        self.current_view = None
        self.current_policy_name = None
        self.current_view_sql = None
        
        # User management
        self.user_list = []
        self.selected_users = set()
        self.user_container = None
        
        # Filter management
        self.filter_list = []
        self.selected_filters = set()
        self.filter_container = None
        
        self.headers()
    
    def headers(self):
        ui.page_title("RLS Manager - Complete")
        ui.label("Complete RLS Management").classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [d.dataset_id for d in datasets if not d.dataset_id.endswith('_views')]
        except Exception as e:
            print(f"Error getting datasets: {e}")
            return []
    
    async def on_dataset_change(self, e):
        self.selected_dataset = e.value
        
        n = ui.notification("Loading RLS views...", spinner=True, timeout=None)
        try:
            self.rls_views = await run.io_bound(
                self.rls_service.list_rls_views,
                self.selected_dataset
            )
            
            if self.views_grid:
                self.views_grid.options['rowData'] = self.rls_views
                self.views_grid.update()
            
            n.dismiss()
            ui.notify(f"✅ Loaded {len(self.rls_views)} RLS views", type="positive")
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    def get_policy_name_from_view(self, view_name: str) -> str:
        """
        Extract policy name from view name
        vw_tb_headcount_executivo_diretoria -> tb_headcount_executivo_diretoria
        """
        return view_name.replace('vw_', '')
    
    def get_view_sql(self, dataset: str, view_name: str) -> str:
        """Get the SQL definition of a view"""
        try:
            table_ref = client.dataset(dataset).table(view_name)
            table = client.get_table(table_ref)
            return table.view_query
        except Exception as e:
            print(f"[ERROR] get_view_sql: {e}")
            return ""
    
    def extract_rls_filters_from_sql(self, view_sql: str) -> list:
        """
        Extract RLS filter conditions from VIEW SQL
        
        Example SQL:
        CREATE VIEW ... AS
        SELECT * FROM table
        WHERE campo IN (
          SELECT username FROM policies_filters
          WHERE policy_name = 'xxx' AND campo = 'valor'
        )
        
        Returns: [
            {'field': 'campo', 'operator': '=', 'value': 'valor'},
            ...
        ]
        """
        filters = []
        
        try:
            # Extract WHERE clause
            where_match = re.search(r'\bWHERE\b(.*?)(?:$|;)', view_sql, re.IGNORECASE | re.DOTALL)
            if not where_match:
                print("[DEBUG] No WHERE clause found")
                return filters
            
            where_clause = where_match.group(1).strip()
            print(f"[DEBUG] WHERE clause: {where_clause[:200]}")
            
            # Pattern 1: Direct conditions (campo = 'valor')
            # Look for conditions like: campo = 'valor' or campo IN ('val1', 'val2')
            direct_patterns = [
                r"(\w+)\s*=\s*'([^']+)'",  # campo = 'valor'
                r"(\w+)\s*!=\s*'([^']+)'",  # campo != 'valor'
                r"(\w+)\s*>\s*'?(\d+)'?",  # campo > 5000
                r"(\w+)\s*<\s*'?(\d+)'?",  # campo < 5000
                r"(\w+)\s*>=\s*'?(\d+)'?",  # campo >= 5000
                r"(\w+)\s*<=\s*'?(\d+)'?",  # campo <= 5000
                r"(\w+)\s+LIKE\s+'([^']+)'",  # campo LIKE '%valor%'
            ]
            
            for pattern in direct_patterns:
                matches = re.finditer(pattern, where_clause, re.IGNORECASE)
                for match in matches:
                    field = match.group(1)
                    value = match.group(2)
                    
                    # Determine operator from pattern
                    if '!=' in pattern:
                        operator = '!='
                    elif '>=' in pattern:
                        operator = '>='
                    elif '<=' in pattern:
                        operator = '<='
                    elif '>' in pattern:
                        operator = '>'
                    elif '<' in pattern:
                        operator = '<'
                    elif 'LIKE' in pattern:
                        operator = 'LIKE'
                    else:
                        operator = '='
                    
                    filters.append({
                        'field': field,
                        'operator': operator,
                        'value': value
                    })
            
            # Pattern 2: RLS pattern with policies_filters
            # campo IN (SELECT username FROM policies_filters WHERE campo = 'valor')
            rls_pattern = r"(\w+)\s+IN\s*\(\s*SELECT.*?WHERE.*?(\w+)\s*=\s*'([^']+)'"
            rls_matches = re.finditer(rls_pattern, where_clause, re.IGNORECASE | re.DOTALL)
            
            for match in rls_matches:
                field = match.group(1)
                filter_field = match.group(2)
                filter_value = match.group(3)
                
                filters.append({
                    'field': field,
                    'operator': 'IN',
                    'value': f'(RLS: {filter_field}={filter_value})',
                    'rls_field': filter_field,
                    'rls_value': filter_value
                })
            
            print(f"[DEBUG] Extracted {len(filters)} filters: {filters}")
            return filters
            
        except Exception as e:
            print(f"[ERROR] extract_rls_filters_from_sql: {e}")
            traceback.print_exc()
            return []
    
    def load_users_from_policies_filters(self, policy_name: str, dataset: str, table: str) -> list:
        """
        Load users from policies_filters table
        Returns list of dicts with user info
        """
        try:
            query = f"""
            SELECT DISTINCT 
                username,
                filter_value,
                field_id,
                CAST(created_at AS STRING) as created_at
            FROM `{config.FILTER_TABLE}`
            WHERE rls_type = 'users'
              AND policy_name LIKE '%{policy_name}%'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{dataset}'
              AND table_id = '{table}'
            ORDER BY username, filter_value
            """
            
            query_job = client.query(query)
            results = []
            
            for row in query_job:
                results.append({
                    'username': row.username,
                    'filter_value': row.filter_value if row.filter_value else '(All data)',
                    'field_id': row.field_id if row.field_id else '-',
                    'created_at': row.created_at
                })
            
            print(f"[DEBUG] Loaded {len(results)} user assignments for policy {policy_name}")
            return results
            
        except Exception as e:
            print(f"[ERROR] load_users_from_policies_filters: {e}")
            traceback.print_exc()
            return []
    
    def load_groups_from_policies_filters(self, policy_name: str, dataset: str, table: str) -> list:
        """
        Load groups from policies_filters table
        Returns list of dicts with group info
        """
        try:
            query = f"""
            SELECT DISTINCT 
                rls_group as group_email,
                filter_value,
                field_id,
                CAST(created_at AS STRING) as created_at
            FROM `{config.FILTER_TABLE}`
            WHERE rls_type = 'group'
              AND policy_name LIKE '%{policy_name}%'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{dataset}'
              AND table_id = '{table}'
            ORDER BY rls_group, filter_value
            """
            
            query_job = client.query(query)
            results = []
            
            for row in query_job:
                results.append({
                    'group_email': row.group_email,
                    'filter_value': row.filter_value if row.filter_value else '(All data)',
                    'field_id': row.field_id if row.field_id else '-',
                    'created_at': row.created_at
                })
            
            print(f"[DEBUG] Loaded {len(results)} group assignments for policy {policy_name}")
            return results
            
        except Exception as e:
            print(f"[ERROR] load_groups_from_policies_filters: {e}")
            traceback.print_exc()
            return []
    
    def get_unique_filter_values(self, policy_name: str, dataset: str, table: str) -> list:
        """Get unique filter values for this policy from policies_filters table"""
        try:
            query = f"""
            SELECT DISTINCT filter_value
            FROM `{config.FILTER_TABLE}`
            WHERE policy_name LIKE '%{policy_name}%'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{dataset}'
              AND table_id = '{table}'
              AND filter_value IS NOT NULL
              AND filter_value != ''
            ORDER BY filter_value
            """
            
            query_job = client.query(query)
            results = [row.filter_value for row in query_job]
            
            print(f"[DEBUG] Found {len(results)} unique filter values from policies_filters: {results}")
            return results
            
        except Exception as e:
            print(f"[ERROR] get_unique_filter_values: {e}")
            return []
    
    def get_table_fields(self, dataset: str, table: str) -> list:
        """Get available fields from source table"""
        try:
            table_ref = client.dataset(dataset).table(table)
            table_obj = client.get_table(table_ref)
            
            fields = [field.name for field in table_obj.schema]
            print(f"[DEBUG] Found {len(fields)} fields in {dataset}.{table}")
            return fields
            
        except Exception as e:
            print(f"[ERROR] get_table_fields: {e}")
            return ['diretoria']  # Default fallback
    
    async def edit_view(self):
        """Edit selected RLS view"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify("No view selected", type="warning")
            return
        
        view_info = rows[0]
        self.current_view = view_info
        
        # Extract policy name
        self.current_policy_name = self.get_policy_name_from_view(view_info['view_name'])
        
        print(f"[DEBUG] Editing view: {view_info['view_name']}")
        print(f"[DEBUG] Policy name: {self.current_policy_name}")
        print(f"[DEBUG] Dataset: {view_info['view_dataset']}")
        print(f"[DEBUG] Base dataset: {view_info['base_dataset']}")
        print(f"[DEBUG] Base table: {view_info['base_table']}")
        
        # Load data
        n = ui.notification("Loading policy data...", spinner=True, timeout=None)
        try:
            # Get VIEW SQL
            self.current_view_sql = await run.io_bound(
                self.get_view_sql,
                view_info['view_dataset'],
                view_info['view_name']
            )
            
            # Extract filters from SQL
            sql_filters = await run.io_bound(
                self.extract_rls_filters_from_sql,
                self.current_view_sql
            )
            
            # Load users
            user_assignments = await run.io_bound(
                self.load_users_from_policies_filters,
                self.current_policy_name,
                view_info['base_dataset'],
                view_info['base_table']
            )
            
            # Load groups
            group_assignments = await run.io_bound(
                self.load_groups_from_policies_filters,
                self.current_policy_name,
                view_info['base_dataset'],
                view_info['base_table']
            )
            
            # Load unique filter values from policies_filters
            filter_values = await run.io_bound(
                self.get_unique_filter_values,
                self.current_policy_name,
                view_info['base_dataset'],
                view_info['base_table']
            )
            
            # Load table fields
            table_fields = await run.io_bound(
                self.get_table_fields,
                view_info['base_dataset'],
                view_info['base_table']
            )
            
            n.dismiss()
            
            # Open edit dialog
            self.open_edit_dialog(
                view_info, 
                user_assignments, 
                group_assignments, 
                filter_values, 
                table_fields,
                sql_filters
            )
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error loading data: {e}", type="negative")
            traceback.print_exc()
    
    def open_edit_dialog(self, view_info, user_assignments, group_assignments, filter_values, table_fields, sql_filters):
        """Open dialog to edit RLS view"""
        
        with ui.dialog() as edit_dialog, ui.card().classes('w-full max-w-7xl max-h-[90vh] overflow-hidden'):
            ui.label(f"Edit RLS View: {view_info['view_name']}").classes('text-h5 font-bold mb-4')
            
            # View info card
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("📋 View Information").classes('font-bold mb-2')
                ui.label(f"Dataset: {view_info['view_dataset']}").classes('text-sm')
                ui.label(f"Source: {view_info['base_dataset']}.{view_info['base_table']}").classes('text-sm')
                ui.label(f"Policy: {self.current_policy_name}").classes('text-sm')
                ui.label(f"Type: {view_info.get('view_type', 'RLS')}").classes('text-sm font-bold text-purple-600')
            
            # Tabs
            with ui.tabs().classes('w-full') as tabs:
                tab_users = ui.tab("👥 Users & Groups", icon='people')
                tab_filters = ui.tab("🔍 Filters", icon='filter_list')
            
            # ✅ Add scroll area for tab panels
            with ui.scroll_area().classes('w-full h-[60vh]'):
                with ui.tab_panels(tabs, value=tab_users).classes('w-full'):
                    # ========== USERS TAB ==========
                    with ui.tab_panel(tab_users):
                        ui.label("Manage Authorized Users & Groups").classes('font-bold mb-4')
                        
                        # Current assignments
                        with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                            ui.label(f"📊 Current Assignments: {len(user_assignments)} users, {len(group_assignments)} groups").classes('font-bold')
                        
                        # Existing users/groups grid
                        with ui.row().classes('w-full gap-4 mb-4'):
                            # Users column
                            with ui.column().classes('flex-1'):
                                ui.label("👤 User Assignments").classes('font-bold mb-2')
                                
                                if user_assignments:
                                    users_grid = ui.aggrid({
                                        'columnDefs': [
                                            {'field': 'username', 'headerName': 'User Email', 'checkboxSelection': True, 'filter': True},
                                            {'field': 'filter_value', 'headerName': 'Filter Value', 'filter': True},
                                            {'field': 'field_id', 'headerName': 'Field', 'filter': True},
                                        ],
                                        'rowData': user_assignments,
                                        'rowSelection': 'multiple',
                                    }).classes('w-full h-64 ag-theme-quartz')
                                    
                                    async def delete_selected_users():
                                        rows = await users_grid.get_selected_rows()
                                        if not rows:
                                            ui.notify("No users selected", type="warning")
                                            return
                                        
                                        for row in rows:
                                            await run.io_bound(
                                                self.delete_user_assignment,
                                                row['username'],
                                                row['filter_value'] if row['filter_value'] != '(All data)' else ''
                                            )
                                        
                                        ui.notify(f"✅ Deleted {len(rows)} user assignments", type="positive")
                                        edit_dialog.close()
                                        await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
                                    
                                    ui.button("DELETE SELECTED", icon="delete", on_click=delete_selected_users).props('color=negative flat')
                                else:
                                    ui.label("No user assignments yet").classes('text-gray-500 italic')
                            
                            # Groups column
                            with ui.column().classes('flex-1'):
                                ui.label("👥 Group Assignments").classes('font-bold mb-2')
                                
                                if group_assignments:
                                    groups_grid = ui.aggrid({
                                        'columnDefs': [
                                            {'field': 'group_email', 'headerName': 'Group Email', 'checkboxSelection': True, 'filter': True},
                                            {'field': 'filter_value', 'headerName': 'Filter Value', 'filter': True},
                                            {'field': 'field_id', 'headerName': 'Field', 'filter': True},
                                        ],
                                        'rowData': group_assignments,
                                        'rowSelection': 'multiple',
                                    }).classes('w-full h-64 ag-theme-quartz')
                                    
                                    async def delete_selected_groups():
                                        rows = await groups_grid.get_selected_rows()
                                        if not rows:
                                            ui.notify("No groups selected", type="warning")
                                            return
                                        
                                        for row in rows:
                                            await run.io_bound(
                                                self.delete_group_assignment,
                                                row['group_email'],
                                                row['filter_value'] if row['filter_value'] != '(All data)' else ''
                                            )
                                        
                                        ui.notify(f"✅ Deleted {len(rows)} group assignments", type="positive")
                                        edit_dialog.close()
                                        await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
                                    
                                    ui.button("DELETE SELECTED", icon="delete", on_click=delete_selected_groups).props('color=negative flat')
                                else:
                                    ui.label("No group assignments yet").classes('text-gray-500 italic')
                        
                        ui.separator()
                        
                        # ✅ FIXED: Add new users/groups section with optional filter
                        ui.label("➕ Add New Assignments").classes('font-bold text-lg mb-2 mt-4')
                        
                        with ui.card().classes('w-full bg-blue-50 p-4'):
                            ui.label("Add User or Group").classes('font-bold mb-2')
                            
                            with ui.row().classes('w-full gap-2'):
                                user_type_select = ui.select(
                                    options=['user', 'group'],
                                    label="Type",
                                    value='user'
                                ).classes('w-32')
                                
                                user_email_input = ui.input(
                                    label="Email",
                                    placeholder="user@example.com"
                                ).classes('flex-1')
                            
                            # ✅ FIXED: Filter value is now optional
                            with ui.row().classes('w-full gap-2 mt-2'):
                                # Add "(No filter - All data)" option
                                filter_options = ['(No filter - All data)'] + (filter_values if filter_values else [])
                                
                                filter_value_select = ui.select(
                                    options=filter_options,
                                    label="Filter Value (optional)",
                                    value=filter_options[0]
                                ).classes('flex-1')
                                
                                async def add_user_assignment():
                                    email = user_email_input.value.strip()
                                    filter_val = filter_value_select.value
                                    user_type = user_type_select.value
                                    
                                    if not email or '@' not in email:
                                        ui.notify("Invalid email", type="warning")
                                        return
                                    
                                    # If "No filter" selected, use empty string
                                    if filter_val == '(No filter - All data)':
                                        filter_val = ''
                                    
                                    success = await run.io_bound(
                                        self.add_user_to_policy,
                                        email,
                                        filter_val,
                                        user_type
                                    )
                                    
                                    if success:
                                        ui.notify(f"✅ Added {email}", type="positive")
                                        user_email_input.value = ''
                                        edit_dialog.close()
                                        await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
                                    else:
                                        ui.notify("Failed to add user", type="negative")
                                
                                ui.button("ADD", icon="add", on_click=add_user_assignment).props('color=primary')
                            
                            # Info note
                            with ui.card().classes('w-full bg-yellow-50 p-2 mt-2'):
                                ui.label("ℹ️ Select 'No filter' to give user access to all data without restrictions.").classes('text-xs')
                    
                    # ========== FILTERS TAB ==========
                    with ui.tab_panel(tab_filters):
                        ui.label("Manage Filter Values").classes('font-bold mb-4')
                        
                        # ✅ FIXED: Show filters from VIEW SQL
                        with ui.card().classes('w-full bg-purple-50 p-4 mb-4'):
                            ui.label(f"🔍 Active RLS Filters (from VIEW SQL): {len(sql_filters)}").classes('font-bold mb-2')
                            if sql_filters:
                                for f in sql_filters:
                                    filter_text = f"{f['field']} {f['operator']} {f['value']}"
                                    ui.label(f"  • {filter_text}").classes('text-sm font-mono')
                            else:
                                ui.label("No active filters in VIEW SQL").classes('text-gray-500 italic')
                        
                        # Current filter values from policies_filters
                        with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                            ui.label(f"📊 Filter Values (from policies_filters): {len(filter_values)}").classes('font-bold mb-2')
                            if filter_values:
                                for fv in filter_values[:10]:
                                    ui.label(f"  • {fv}").classes('text-sm')
                                if len(filter_values) > 10:
                                    ui.label(f"  ... and {len(filter_values) - 10} more").classes('text-sm italic')
                            else:
                                ui.label("No filter values in policies_filters table").classes('text-gray-500 italic')
                        
                        # ✅ Add filter with operator
                        ui.label("➕ Add New Filter Rule").classes('font-bold text-lg mb-2')
                        
                        with ui.card().classes('w-full bg-green-50 p-4'):
                            ui.label("Define Filter Condition").classes('font-bold mb-2')
                            
                            with ui.row().classes('w-full gap-2'):
                                field_select = ui.select(
                                    options=table_fields,
                                    label="Field",
                                    value=table_fields[0] if table_fields else 'diretoria'
                                ).classes('w-48')
                                
                                operator_select = ui.select(
                                    options=['=', '!=', '>', '<', '>=', '<=', 'LIKE'],
                                    label="Operator",
                                    value='='
                                ).classes('w-32')
                                
                                value_input = ui.input(
                                    label="Value",
                                    placeholder="e.g., Information Technology"
                                ).classes('flex-1')
                                
                                async def add_filter_rule():
                                    field = field_select.value
                                    operator = operator_select.value
                                    value = value_input.value.strip()
                                    
                                    if not value:
                                        ui.notify("Enter filter value", type="warning")
                                        return
                                    
                                    # Construct filter expression
                                    if operator == 'LIKE':
                                        filter_expression = f"{field} LIKE '%{value}%'"
                                    else:
                                        filter_expression = f"{field} {operator} '{value}'"
                                    
                                    ui.notify(
                                        f"ℹ️ Filter rule '{filter_expression}' ready. Add users in Users tab.",
                                        type="info",
                                        timeout=5000
                                    )
                                    
                                    # Add to filter_values for user assignment
                                    if value not in filter_values:
                                        filter_values.append(value)
                                        # Update the select options
                                        new_options = ['(No filter - All data)'] + filter_values
                                        filter_value_select.options = new_options
                                        filter_value_select.update()
                                    
                                    value_input.value = ''
                                
                                ui.button("ADD FILTER", icon="add", on_click=add_filter_rule).props('color=primary')
                        
                        with ui.card().classes('w-full bg-yellow-50 p-3 mt-4'):
                            ui.label("ℹ️ Filter Expression Examples:").classes('text-sm font-bold mb-2')
                            ui.label("• diretoria = 'TI'").classes('text-xs')
                            ui.label("• salario > '5000'").classes('text-xs')
                            ui.label("• regiao LIKE '%Sul%'").classes('text-xs')
                            ui.label("• idade >= '30'").classes('text-xs')
            
            # Dialog buttons
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button("CLOSE", on_click=edit_dialog.close).props('flat')
                ui.button("REFRESH", icon="refresh", on_click=lambda: [edit_dialog.close(), self.edit_view()]).props('color=primary')
        
        edit_dialog.open()
    
    def add_user_to_policy(self, email: str, filter_value: str, user_type: str) -> bool:
        """Add user/group to policy in policies_filters table"""
        try:
            # Use empty string if filter_value is empty
            filter_val = filter_value if filter_value else ''
            
            if user_type == 'user':
                query = f"""
                INSERT INTO `{config.FILTER_TABLE}` 
                (rls_type, policy_name, project_id, dataset_id, table_id, field_id, filter_value, username, created_at)
                VALUES
                ('users', '{self.current_policy_name}', '{self.project_id}', 
                 '{self.current_view["base_dataset"]}', '{self.current_view["base_table"]}', 
                 'diretoria', '{filter_val}', '{email}', CURRENT_TIMESTAMP())
                """
            else:  # group
                query = f"""
                INSERT INTO `{config.FILTER_TABLE}` 
                (rls_type, policy_name, project_id, dataset_id, table_id, field_id, filter_value, rls_group, created_at)
                VALUES
                ('group', '{self.current_policy_name}', '{self.project_id}', 
                 '{self.current_view["base_dataset"]}', '{self.current_view["base_table"]}', 
                 'diretoria', '{filter_val}', '{email}', CURRENT_TIMESTAMP())
                """
            
            query_job = client.query(query)
            query_job.result()
            
            self.audit_service.log_action(
                action='ADD_USER_TO_RLS_POLICY',
                resource_type='RLS_USER_ASSIGNMENT',
                resource_name=f"{email} → {self.current_policy_name}",
                status='SUCCESS',
                details={
                    'email': email,
                    'type': user_type,
                    'filter_value': filter_val if filter_val else '(All data)',
                    'policy_name': self.current_policy_name
                }
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] add_user_to_policy: {e}")
            traceback.print_exc()
            
            self.audit_service.log_action(
                action='ADD_USER_TO_RLS_POLICY',
                resource_type='RLS_USER_ASSIGNMENT',
                resource_name=f"{email} → {self.current_policy_name}",
                status='FAILED',
                error_message=str(e)
            )
            
            return False
    
    def delete_user_assignment(self, username: str, filter_value: str) -> bool:
        """Delete user assignment from policies_filters table"""
        try:
            # Handle empty filter_value
            if filter_value == '':
                filter_condition = "AND filter_value = ''"
            else:
                filter_condition = f"AND filter_value = '{filter_value}'"
            
            query = f"""
            DELETE FROM `{config.FILTER_TABLE}`
            WHERE rls_type = 'users'
              AND policy_name LIKE '%{self.current_policy_name}%'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{self.current_view["base_dataset"]}'
              AND table_id = '{self.current_view["base_table"]}'
              AND username = '{username}'
              {filter_condition}
            """
            
            query_job = client.query(query)
            query_job.result()
            
            self.audit_service.log_action(
                action='DELETE_USER_FROM_RLS_POLICY',
                resource_type='RLS_USER_ASSIGNMENT',
                resource_name=f"{username} → {self.current_policy_name}",
                status='SUCCESS'
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] delete_user_assignment: {e}")
            traceback.print_exc()
            return False
    
    def delete_group_assignment(self, group_email: str, filter_value: str) -> bool:
        """Delete group assignment from policies_filters table"""
        try:
            # Handle empty filter_value
            if filter_value == '':
                filter_condition = "AND filter_value = ''"
            else:
                filter_condition = f"AND filter_value = '{filter_value}'"
            
            query = f"""
            DELETE FROM `{config.FILTER_TABLE}`
            WHERE rls_type = 'group'
              AND policy_name LIKE '%{self.current_policy_name}%'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{self.current_view["base_dataset"]}'
              AND table_id = '{self.current_view["base_table"]}'
              AND rls_group = '{group_email}'
              {filter_condition}
            """
            
            query_job = client.query(query)
            query_job.result()
            
            self.audit_service.log_action(
                action='DELETE_GROUP_FROM_RLS_POLICY',
                resource_type='RLS_GROUP_ASSIGNMENT',
                resource_name=f"{group_email} → {self.current_policy_name}",
                status='SUCCESS'
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] delete_group_assignment: {e}")
            traceback.print_exc()
            return False
    
    async def delete_selected_views(self):
        """Delete selected RLS views"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify("No views selected", type="warning")
            return
        
        view_names = [f"{row['view_dataset']}.{row['view_name']}" for row in rows]
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label("⚠️ Confirm Deletion").classes('text-h6 font-bold text-red-600 mb-4')
            ui.label(f"Delete {len(view_names)} RLS view(s)?").classes('mb-2')
            
            for name in view_names[:10]:
                ui.label(f"  • {name}").classes('text-sm')
            if len(view_names) > 10:
                ui.label(f"  ... and {len(view_names)-10} more").classes('text-sm italic')
            
            ui.label("This action cannot be undone!").classes('text-red-600 font-bold mt-4')
            
            async def execute_deletion():
                success = 0
                failed = 0
                
                for view in rows:
                    try:
                        # Delete view
                        result = await run.io_bound(
                            self.rls_service.delete_rls_view,
                            view['view_dataset'],
                            view['view_name']
                        )
                        
                        if result:
                            success += 1
                        else:
                            failed += 1
                    except Exception as e:
                        print(f"[ERROR] Deleting view: {e}")
                        failed += 1
                
                confirm_dialog.close()
                
                if success > 0:
                    ui.notify(f"✅ {success} view(s) deleted", type="positive")
                if failed > 0:
                    ui.notify(f"❌ {failed} failed", type="negative")
                
                # Refresh grid
                await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button("CANCEL", on_click=confirm_dialog.close).props('flat')
                ui.button("DELETE", icon="delete_forever", on_click=execute_deletion).props('color=negative')
        
        confirm_dialog.open()
    
    async def refresh_views(self):
        """Refresh views list"""
        if self.selected_dataset:
            await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
        else:
            ui.notify("Select a dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('RLS Manager - Complete'):
            with ui.card().classes('w-full'):
                ui.label("🔐 RLS Manager - Complete").classes('text-h5 font-bold mb-4')
                
                # Dataset selector
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    self.dataset_select = ui.select(
                        options=self.get_datasets(),
                        label="Select Dataset",
                        on_change=self.on_dataset_change
                    ).classes('flex-1')
                    
                    ui.button("REFRESH", icon="refresh", on_click=self.refresh_views).props('flat')
                
                # Grid
                ui.separator()
                ui.label("RLS Views").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'view_name', 'headerName': 'View Name', 'checkboxSelection': True, 'filter': True, 'minWidth': 300},
                        {'field': 'view_type', 'headerName': 'Type', 'filter': True, 'minWidth': 100},
                        {'field': 'view_dataset', 'headerName': 'Dataset', 'filter': True, 'minWidth': 180},
                        {'field': 'base_table', 'headerName': 'Source Table', 'filter': True, 'minWidth': 180},
                        {'field': 'created_at', 'headerName': 'Created', 'filter': True, 'minWidth': 160},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                # Action buttons
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("MANAGE USERS & FILTERS", icon="edit", on_click=self.edit_view).props('color=primary')
                    ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_views).props('color=negative')
                    ui.button("CREATE NEW RLS VIEW", icon="add_circle", on_click=lambda: ui.navigate.to('/rls/create-view')).props('color=positive outline')
    
    def run(self):
        """Entry point called by allpages.py"""
        self.render_ui()
