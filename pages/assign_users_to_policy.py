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
  Version:      3.1.0
  Release Date: 2024-12-26
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Unified interface for managing RLS policies with support for users, groups,
  and service accounts. Includes view field editing and filter management.
  
  New Features (v3.1):
  - Lists ALL RLS views from GCP (not just registered policies)
  - Dataset filter to select which datasets to show
  - Auto-discovers views in *_views datasets
  - Creates policy record if view exists but policy doesn't
================================================================================
"""

import theme
from theme import get_text
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError, NotFound
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
        
        # Dataset filter
        self.available_views_datasets = []
        self.selected_datasets_filter = []
        self.dataset_filter_select = None
        
        self.existing_policies_grid = None
        self.grid_step1 = None
        self.headers()
        self.stepper_setup()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label("Manage RLS Policy Assignments").classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Step 1: Select View"
        self.step2_title = "Step 2: Manage Assignments"

        with self.stepper:
            self.step1()
            self.step2_with_tabs()

    def get_views_datasets(self):
        """
        Get all datasets that end with '_views' (RLS views datasets)
        """
        try:
            datasets = list(client.list_datasets())
            views_datasets = []
            
            for dataset in datasets:
                dataset_id = dataset.dataset_id
                # Check if it's a views dataset
                if dataset_id.endswith('_views'):
                    views_datasets.append(dataset_id)
                    print(f"📁 Found views dataset: {dataset_id}")
            
            print(f"✅ Found {len(views_datasets)} views datasets")
            return sorted(views_datasets)
            
        except Exception as e:
            print(f"Error listing datasets: {e}")
            return []

    def get_all_rls_views(self, dataset_filter=None):
        """
        Get ALL RLS views from GCP, optionally filtered by dataset.
        
        This scans actual GCP datasets (ending in _views) and lists all views found.
        """
        try:
            all_views = []
            
            # Get datasets to scan
            if dataset_filter and len(dataset_filter) > 0:
                datasets_to_scan = dataset_filter
            else:
                datasets_to_scan = self.get_views_datasets()
            
            print(f"🔍 Scanning {len(datasets_to_scan)} datasets for views...")
            
            for views_dataset in datasets_to_scan:
                try:
                    tables = list(client.list_tables(views_dataset))
                    
                    for table in tables:
                        if table.table_type == 'VIEW':
                            # Get view details
                            view_ref = client.dataset(views_dataset).table(table.table_id)
                            view = client.get_table(view_ref)
                            
                            # Extract metadata from description
                            base_dataset = None
                            base_table = None
                            filter_field = None
                            
                            if view.description and 'RLS_METADATA' in view.description:
                                try:
                                    metadata_match = re.search(r'RLS_METADATA:(\{.*\})', view.description)
                                    if metadata_match:
                                        metadata = json.loads(metadata_match.group(1))
                                        base_dataset = metadata.get('base_dataset')
                                        base_table = metadata.get('base_table')
                                        filter_field = metadata.get('filter_field')
                                except:
                                    pass
                            
                            # If no metadata, try to infer from view SQL
                            if not base_dataset:
                                # The base dataset is usually the views dataset without "_views"
                                base_dataset = views_dataset.replace('_views', '')
                            
                            if not base_table:
                                # Try to extract from view SQL
                                if view.view_query:
                                    # Look for FROM `project.dataset.table`
                                    match = re.search(r'FROM\s+`[^`]+\.([^`]+)\.([^`]+)`', view.view_query, re.IGNORECASE)
                                    if match:
                                        base_dataset = match.group(1)
                                        base_table = match.group(2)
                            
                            if not filter_field:
                                # Try to extract from WHERE clause
                                if view.view_query:
                                    match = re.search(r'WHERE\s+(\w+)\s+IN', view.view_query, re.IGNORECASE)
                                    if match:
                                        filter_field = match.group(1)
                            
                            view_info = {
                                'View Name': table.table_id,
                                'Views Dataset': views_dataset,
                                'Base Dataset': base_dataset or 'Unknown',
                                'Base Table': base_table or 'Unknown',
                                'Filter Field': filter_field or 'Unknown',
                                'Created': str(view.created)[:19] if view.created else 'Unknown'
                            }
                            
                            all_views.append(view_info)
                            print(f"   📺 Found view: {table.table_id} in {views_dataset}")
                            
                except NotFound:
                    print(f"   ⚠️ Dataset {views_dataset} not found")
                except Exception as e:
                    print(f"   ⚠️ Error scanning {views_dataset}: {e}")
            
            print(f"✅ Found {len(all_views)} total RLS views")
            return all_views
            
        except Exception as e:
            ui.notify(f"Error loading views: {e}", type="negative")
            return []

    def load_existing_assignments(self):
        """Load ALL assignments (users, groups, service accounts) for selected view"""
        if not self.selected_views_dataset or not self.selected_view_name:
            return []
        
        # For views, we query by the base table info stored in policies_filters
        query = f"""
        SELECT 
            rls_type,
            COALESCE(username, rls_group, '') as identity,
            filter_value,
            field_id,
            CAST(created_at AS STRING) as created_at
        FROM `{config.FILTER_TABLE}`
        WHERE project_id = '{self.project_id}'
          AND (
            -- Match by policy name (view name)
            policy_name = '{self.selected_view_name}'
            OR
            -- Match by base table info
            (dataset_id = '{self.selected_base_dataset}' AND table_id = '{self.selected_base_table}')
          )
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
        if not self.selected_base_dataset or not self.selected_base_table:
            return []
        
        query = f"""
        SELECT 
            filter_value,
            COUNT(DISTINCT COALESCE(username, rls_group)) as user_count,
            COUNT(*) as total_assignments
        FROM `{config.FILTER_TABLE}`
        WHERE project_id = '{self.project_id}'
          AND (
            policy_name = '{self.selected_view_name}'
            OR (dataset_id = '{self.selected_base_dataset}' AND table_id = '{self.selected_base_table}')
          )
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
        """Get available fields from the BASE table"""
        try:
            if not self.selected_base_dataset or not self.selected_base_table:
                return []
            table_ref = client.dataset(self.selected_base_dataset).table(self.selected_base_table)
            table = client.get_table(table_ref)
            return [field.name for field in table.schema]
        except Exception as e:
            print(f"Error getting fields: {e}")
            return []
    
    def get_distinct_field_values(self):
        """Get distinct values from the filter field"""
        if not self.selected_policy_field or not self.selected_base_dataset or not self.selected_base_table:
            print(f"DEBUG: Missing values - field:{self.selected_policy_field} dataset:{self.selected_base_dataset} table:{self.selected_base_table}")
            return []
        
        try:
            query = f"""
            SELECT DISTINCT CAST({self.selected_policy_field} AS STRING) as value
            FROM `{self.project_id}.{self.selected_base_dataset}.{self.selected_base_table}`
            WHERE {self.selected_policy_field} IS NOT NULL
            ORDER BY value
            LIMIT 100
            """
            print(f"DEBUG: Executing query to get distinct values from {self.selected_policy_field}")
            results = client.query(query).result()
            values = [row.value for row in results]
            print(f"DEBUG: Found {len(values)} distinct values")
            return values
        except Exception as e:
            print(f"Error getting distinct values: {e}")
            return []
    
    async def show_edit_field_dialog(self):
        """Show dialog to edit filter field"""
        with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label("Edit Filter Field").classes('text-h6 font-bold mb-4')
            
            # Current field info
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label(f"📋 Current Field: {self.selected_policy_field}").classes('font-bold text-blue-700')
                ui.label(f"View: {self.selected_views_dataset}.{self.selected_view_name}").classes('text-sm')
                ui.label(f"Base Table: {self.selected_base_dataset}.{self.selected_base_table}").classes('text-sm')
            
            # Field selector (initially empty)
            with ui.row().classes('w-full gap-4 items-center mb-4'):
                ui.label("New Field:").classes('font-bold w-32')
                new_field_select = ui.select(
                    options=[],
                    value=None
                ).classes('flex-1')
            
            # Load schema button
            def load_schema():
                try:
                    fields = self.get_table_fields()
                    if fields:
                        new_field_select.options = fields
                        new_field_select.value = self.selected_policy_field
                        new_field_select.update()
                        ui.notify(f"✅ Loaded {len(fields)} fields from table schema", type="positive", timeout=2000)
                    else:
                        ui.notify("No fields found in table", type="warning")
                except Exception as e:
                    ui.notify(f"Error loading schema: {e}", type="negative")
            
            with ui.row().classes('w-full justify-start mb-4'):
                ui.button("📊 LOAD SCHEMA", on_click=load_schema).props('color=primary')
            
            # Value selector (initially empty)
            with ui.row().classes('w-full gap-4 items-center mb-4'):
                ui.label("New Value:").classes('font-bold w-32')
                new_value_select = ui.select(
                    options=[],
                    value=None
                ).classes('flex-1')
            
            # Load field values button
            def load_field_values():
                try:
                    if not new_field_select.value:
                        ui.notify("Please select a field first", type="warning")
                        return
                    
                    # Get distinct values from the selected field
                    query = f"""
                    SELECT DISTINCT CAST({new_field_select.value} AS STRING) as value
                    FROM `{self.project_id}.{self.selected_base_dataset}.{self.selected_base_table}`
                    WHERE {new_field_select.value} IS NOT NULL
                    ORDER BY value
                    LIMIT 100
                    """
                    results = client.query(query).result()
                    values = [row.value for row in results]
                    
                    if values:
                        new_value_select.options = values
                        new_value_select.value = values[0] if values else None
                        new_value_select.update()
                        ui.notify(f"✅ Loaded {len(values)} values from field '{new_field_select.value}'", type="positive", timeout=2000)
                    else:
                        ui.notify(f"No values found in field '{new_field_select.value}'", type="warning")
                except Exception as e:
                    ui.notify(f"Error loading field values: {e}", type="negative")
            
            with ui.row().classes('w-full justify-start mb-4'):
                ui.button("🔄 LOAD FIELD VALUES", on_click=load_field_values).props('color=primary')
            
            # Warning card
            with ui.card().classes('w-full bg-yellow-50 p-4 mb-4'):
                ui.label("⚠️ Changing the field will:").classes('text-xs font-bold mb-2')
                ui.label("• Update the RLS view SQL").classes('text-xs')
                ui.label("• Change how data is filtered for all users").classes('text-xs')
                ui.label("• Update all existing assignments to use the new field and value").classes('text-xs')
                ui.label("• The page will reload after the change").classes('text-xs')
            
            # Buttons
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button("CANCEL", on_click=dialog.close).props('flat')
                
                change_button = ui.button("CHANGE FIELD", icon="edit").props('color=primary')
                
                async def confirm_change():
                    print("=== CONFIRM CHANGE CLICKED ===")
                    print(f"New field value: {new_field_select.value}")
                    print(f"New value value: {new_value_select.value}")
                    
                    if not new_field_select.value:
                        print("ERROR: No field selected")
                        ui.notify("Please select a field", type="warning")
                        return
                    
                    if not new_value_select.value:
                        print("ERROR: No value selected")
                        ui.notify("Please select a value for the new field", type="warning")
                        return
                    
                    if new_field_select.value == self.selected_policy_field:
                        print("INFO: Field is the same")
                        ui.notify("Field is already set to this value", type="info")
                        return
                    
                    # Disable button and show loading
                    change_button.props('loading')
                    change_button.disable()
                    
                    try:
                        print("Calling change_view_field...")
                        success = await run.io_bound(
                            self.change_view_field,
                            new_field_select.value,
                            new_value_select.value
                        )
                        
                        print(f"Result: {success}")
                        
                        if success:
                            print("Success! Closing dialog and reloading page...")
                            dialog.close()
                            ui.notify(f"✅ View field changed to: {new_field_select.value} = {new_value_select.value}", type="positive", timeout=3000)
                            # Give time for notification to show before reload
                            await run.io_bound(lambda: __import__('time').sleep(1))
                            ui.navigate.reload()
                        else:
                            print("Failed to change field")
                            ui.notify("❌ Failed to change field.", type="negative")
                            # Re-enable button
                            change_button.props(remove='loading')
                            change_button.enable()
                    except Exception as e:
                        print(f"Exception during change: {e}")
                        ui.notify(f"❌ Error: {e}", type="negative")
                        # Re-enable button
                        change_button.props(remove='loading')
                        change_button.enable()
                
                change_button.on('click', confirm_change)
        
        dialog.open()

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
              AND (
                policy_name = '{self.selected_view_name}'
                OR (dataset_id = '{self.selected_base_dataset}' AND table_id = '{self.selected_base_table}')
              )
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
                    'filter_value': filter_value,
                    'view': self.selected_view_name
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
            
            # Insert query - use view name as policy_name
            query = f"""
            INSERT INTO `{config.FILTER_TABLE}` 
            (rls_type, policy_name, project_id, dataset_id, table_id, 
             field_id, filter_value, {identity_column}, created_at)
            VALUES
            ('{rls_type}', '{self.selected_view_name}', '{self.project_id}', 
             '{self.selected_base_dataset}', '{self.selected_base_table}', 
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
                    'view': self.selected_view_name
                }
            )
            
            ui.notify(f"✅ Added: {email}", type="positive")
            return True
            
        except Exception as e:
            ui.notify(f"Error adding assignment: {e}", type="negative")
            return False

    def change_view_field(self, new_field, new_value):
        """Change the filter field of the RLS view"""
        try:
            print(f"=== CHANGE VIEW FIELD DEBUG ===")
            print(f"New field: {new_field}")
            print(f"New value: {new_value}")
            print(f"Views dataset: {self.selected_views_dataset}")
            print(f"View name: {self.selected_view_name}")
            
            if not self.selected_views_dataset or not self.selected_view_name:
                print("❌ View information missing!")
                return False
            
            # Get current view SQL
            print(f"Getting view: {self.selected_views_dataset}.{self.selected_view_name}")
            view_ref = client.dataset(self.selected_views_dataset).table(self.selected_view_name)
            view = client.get_table(view_ref)
            print(f"View retrieved successfully")
            
            # Extract metadata
            rls_metadata = {}
            if view.description:
                metadata_match = re.search(r'RLS_METADATA:(\{.*\})', view.description)
                if metadata_match:
                    rls_metadata = json.loads(metadata_match.group(1))
            print(f"Metadata: {rls_metadata}")
            
            # Get field type from base table
            table_ref = client.dataset(self.selected_base_dataset).table(self.selected_base_table)
            table = client.get_table(table_ref)
            field_type = None
            for schema_field in table.schema:
                if schema_field.name == new_field:
                    field_type = schema_field.field_type
                    break
            
            if not field_type:
                print(f"Field {new_field} not found in table schema")
                return False
            
            print(f"Field type: {field_type}")
            
            # Create new view SQL with updated field
            new_sql = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_views_dataset}.{self.selected_view_name}` AS
            SELECT *
            FROM `{self.project_id}.{self.selected_base_dataset}.{self.selected_base_table}`
            WHERE {new_field} IN (
              SELECT CAST(filter_value AS {field_type})
              FROM `{config.FILTER_TABLE}`
              WHERE rls_type = 'users'
                AND project_id = '{self.project_id}'
                AND dataset_id = '{self.selected_base_dataset}'
                AND table_id = '{self.selected_base_table}'
                AND field_id = '{new_field}'
                AND username = SESSION_USER()
            );
            """
            
            print(f"Executing SQL to update view...")
            client.query(new_sql).result()
            print(f"View SQL updated successfully")
            
            # Update metadata
            rls_metadata['filter_field'] = new_field
            rls_metadata['filter_field_type'] = field_type
            rls_metadata['base_dataset'] = self.selected_base_dataset
            rls_metadata['base_table'] = self.selected_base_table
            
            view.description = (
                f"RLS view for users - filters by {new_field}\n"
                f"Base table: {self.selected_base_dataset}.{self.selected_base_table}\n\n"
                f"RLS_METADATA:{json.dumps(rls_metadata)}"
            )
            client.update_table(view, ['description'])
            print(f"View metadata updated")
            
            # Update policy table if exists
            query = f"""
            UPDATE `{config.POLICY_TABLE}`
            SET field_id = '{new_field}'
            WHERE policy_name = '{self.selected_view_name}'
              AND project_id = '{self.project_id}'
            """
            print(f"Updating policy table...")
            client.query(query).result()
            
            # Update ALL filter assignments with new field AND new value
            query = f"""
            UPDATE `{config.FILTER_TABLE}`
            SET field_id = '{new_field}',
                filter_value = '{new_value}'
            WHERE policy_name = '{self.selected_view_name}'
              AND project_id = '{self.project_id}'
            """
            print(f"Updating filter table...")
            client.query(query).result()
            print(f"Filter table updated")
            
            self.audit_service.log_action(
                action='CHANGE_VIEW_FIELD',
                resource_type='RLS_VIEW',
                resource_name=self.selected_view_name,
                status='SUCCESS',
                details={
                    'old_field': self.selected_policy_field,
                    'new_field': new_field,
                    'new_value': new_value,
                    'view': f"{self.selected_views_dataset}.{self.selected_view_name}"
                }
            )
            
            # Update local state
            self.selected_policy_field = new_field
            
            print(f"=== CHANGE VIEW FIELD SUCCESS ===")
            return True
            
        except Exception as e:
            print(f"=== CHANGE VIEW FIELD ERROR ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
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
        """Load view details when moving to step 2"""
        if not self.selected_policy:
            ui.notify("No view selected", type="warning")
            return

        selected = self.selected_policy[0]
        
        # Set view info
        self.selected_view_name = selected['View Name']
        self.selected_views_dataset = selected['Views Dataset']
        self.selected_base_dataset = selected['Base Dataset']
        self.selected_base_table = selected['Base Table']
        self.selected_policy_field = selected['Filter Field']
        
        # For compatibility with other methods
        self.selected_policy_name = self.selected_view_name
        self.selected_policy_dataset = self.selected_base_dataset
        self.selected_policy_table = self.selected_base_table
        self.is_rls_view = True
        
        print(f"Selected view: {self.selected_view_name}")
        print(f"Views dataset: {self.selected_views_dataset}")
        print(f"Base: {self.selected_base_dataset}.{self.selected_base_table}")
        print(f"Filter field: {self.selected_policy_field}")
        
        self.stepper.next()

    def refresh_views_list(self):
        """Refresh the views list based on selected dataset"""
        try:
            # Get selected dataset from filter
            selected_dataset = self.dataset_filter_select.value if self.dataset_filter_select else 'All Datasets'
            
            # If "All Datasets" selected, show all
            if selected_dataset == 'All Datasets':
                views_list = self.get_all_rls_views()
            else:
                views_list = self.get_all_rls_views(dataset_filter=[selected_dataset])
            
            # Update grid
            self.grid_step1.options['rowData'] = views_list
            self.grid_step1.update()
            
            ui.notify(f"✅ Found {len(views_list)} RLS views", type="positive", timeout=2000)
            
        except Exception as e:
            ui.notify(f"Error refreshing views: {e}", type="negative")

    def step1(self):
        """Step 1: Select View from GCP"""
        with ui.step(self.step1_title):
            # Header with filter
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label("Select an RLS view to manage").classes('text-caption text-grey-7')
                
                with ui.row().classes('gap-2 items-center'):
                    # Dataset filter dropdown
                    self.available_views_datasets = self.get_views_datasets()
                    
                    # Simple list format for ui.select
                    filter_options = ['All Datasets'] + self.available_views_datasets
                    
                    self.dataset_filter_select = ui.select(
                        options=filter_options,
                        value='All Datasets',
                        label="Filter by Dataset"
                    ).classes('min-w-64').props('dense outlined')
                    
                    ui.button("🔄 REFRESH", on_click=self.refresh_views_list).props('flat size=sm')
            
            # Info card
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label("💡 This list shows ALL RLS views found in your GCP project").classes('text-xs')
                ui.label(f"   Looking in datasets ending with '_views'").classes('text-xs text-grey-7')
            
            # Load initial views
            views_list = self.get_all_rls_views()

            self.grid_step1 = ui.aggrid({
                'columnDefs': [
                    {'field': 'View Name', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 250},
                    {'field': 'Views Dataset', 'filter': 'agTextColumnFilter', 'minWidth': 200},
                    {'field': 'Base Dataset', 'filter': 'agTextColumnFilter'},
                    {'field': 'Base Table', 'filter': 'agTextColumnFilter'},
                    {'field': 'Filter Field', 'filter': 'agTextColumnFilter'},
                    {'field': 'Created', 'filter': 'agTextColumnFilter', 'width': 180}
                ],
                'rowData': views_list,
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
        """Step 2: Manage Assignments with 2 tabs"""
        with ui.step(self.step2_title):
            # View info card
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("📺 Selected View").classes('font-bold mb-2')
                ui.label().bind_text_from(self, 'selected_view_name', lambda x: f"View: {x if x else 'None'}").classes('text-sm')
                ui.label().bind_text_from(self, 'selected_views_dataset', lambda x: f"Views Dataset: {x if x else 'None'}").classes('text-sm')
                
                with ui.row().classes('gap-4'):
                    ui.label().bind_text_from(self, 'selected_base_dataset', lambda x: f"Base Dataset: {x if x else 'None'}").classes('text-sm')
                    ui.label().bind_text_from(self, 'selected_base_table', lambda x: f"Base Table: {x if x else 'None'}").classes('text-sm')
                
                ui.label().bind_text_from(self, 'selected_policy_field', lambda x: f"Filter Field: {x if x else 'None'}").classes('text-sm font-bold text-blue-700')
            
            # Tabs
            with ui.tabs().classes('w-full') as tabs:
                tab_assignments = ui.tab("👥 Assignments", icon='people')
                tab_add = ui.tab("➕ Add New", icon='add_circle')
            
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
                        
                        # EDIT FIELD BUTTON
                        async def open_edit_field_dialog():
                            await self.show_edit_field_dialog()
                        
                        ui.button("EDIT FIELD", icon="edit", on_click=open_edit_field_dialog).props('color=primary outline')
                
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
                                options=['👤 User', '👥 Group', '🤖 Service Account'],
                                value='👤 User'
                            ).classes('flex-1')
                        
                        # Email input
                        with ui.row().classes('w-full gap-4 items-center mb-4'):
                            ui.label("Email:").classes('font-bold w-24')
                            email_input = ui.input(
                                placeholder="user@example.com or group@example.com or sa@project.iam.gserviceaccount.com"
                            ).classes('flex-1')
                        
                        # Filter value selector
                        with ui.row().classes('w-full gap-4 items-center mb-4'):
                            ui.label("Filter:").classes('font-bold w-24')
                            
                            filter_value_select = ui.select(
                                options=['(No filter - All data)'],
                                value='(No filter - All data)'
                            ).classes('flex-1')
                            
                            def load_filter_values():
                                try:
                                    field_values = self.get_distinct_field_values()
                                    stats = self.get_filter_value_stats()
                                    used_values = [s['filter_value'] for s in stats]
                                    
                                    all_values = sorted(set(field_values + used_values))
                                    filter_options = ['(No filter - All data)'] + all_values
                                    
                                    filter_value_select.options = filter_options
                                    filter_value_select.update()
                                    
                                    ui.notify(f"✅ Loaded {len(all_values)} filter values", type="positive", timeout=2000)
                                except Exception as e:
                                    ui.notify(f"Error loading values: {e}", type="negative")
                        
                        with ui.row().classes('w-full justify-start mb-4'):
                            ui.button("🔄 LOAD FILTER VALUES", on_click=load_filter_values).props('color=primary size=sm')
                        
                        async def add_new_assignment():
                            type_map = {
                                '👤 User': 'user',
                                '👥 Group': 'group',
                                '🤖 Service Account': 'service_account'
                            }
                            
                            success = await run.io_bound(
                                self.add_assignment,
                                type_map.get(identity_type_select.value, 'user'),
                                email_input.value,
                                filter_value_select.value
                            )
                            if success:
                                email_input.value = ''
                                self.refresh_assignments_grid()
                        
                        with ui.row().classes('w-full justify-end'):
                            ui.button("ADD ASSIGNMENT", icon="add", on_click=add_new_assignment).props('color=primary')
                    
                    with ui.card().classes('w-full bg-blue-50 p-4 mt-4'):
                        ui.label("💡 How it works:").classes('font-bold mb-2')
                        ui.label("• Users: Individual user accounts").classes('text-xs')
                        ui.label("• Groups: Email groups (e.g., ti-team@company.com)").classes('text-xs')
                        ui.label("• Service Accounts: System identities (e.g., app@project.iam.gserviceaccount.com)").classes('text-xs')
                        ui.label("• Filter: Restrict data access (or 'No filter' for all data)").classes('text-xs')

            # Navigation
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)

    def run(self):
        with theme.frame("Assign to Policy - Unified"):
            pass
