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

# "IMPORTANT: This application is a prototype and should be used for experimental purposes only.
# It is not intended for production use. 
# This software is provided 'as is' without warranty of any kind, express or implied, including but not limited to the warranties 
# of merchantability, fitness for a particular purpose and noninfringement. 
# In no event shall Google or the developers be liable for any claim, damages or other liability, whether in an action of contract, 
# tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software. 
# Google is not responsible for the functionality, reliability, or security of this prototype. 
# Use of this tool is at your own discretion and risk."

import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService

config = Config()

# Initialize BigQuery client globally
client = bigquery.Client(project=config.PROJECT_ID)


class RLSAssignValuestoGroup:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Assign Values to Row Level Policy (Groups)"

        self.selected_policy_name = None
        self.selected_policy_dataset = None
        self.selected_policy_table = None
        self.selected_policy_field = None
        self.selected_policy_group_email = None
        self.selected_policy = {}

        self.filter_values = []
        self.selected_filters = set()
        
        self.filter_container = None
        self.existing_policies_grid = None

        self.headers()
        self.stepper_setup()

    def load_existing_policies_from_db(self):
        """Carrega políticas existentes para grupos do banco de dados"""
        if not self.selected_policy_dataset or not self.selected_policy_table:
            return []
        
        query = f"""
        SELECT 
            rls_group as group_email,
            filter_value,
            policy_name,
            field_id,
            CAST(created_at AS STRING) as created_at
        FROM `{config.FILTER_TABLE}`
        WHERE rls_type = 'group'
          AND project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
        ORDER BY rls_group, filter_value
        """
        
        try:
            query_job = client.query(query)
            results = [dict(row) for row in query_job]
            return results
        except Exception as e:
            ui.notify(f"Error loading existing policies: {e}", type="negative")
            return []

    def delete_policy_from_db(self, group_email, filter_value):
        """Deleta política de grupo do BigQuery"""
        query = f"""
        DELETE FROM `{config.FILTER_TABLE}`
        WHERE rls_type = 'group'
          AND project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
          AND rls_group = '{group_email}'
          AND filter_value = '{filter_value}'
        """
        
        try:
            query_job = client.query(query)
            query_job.result()
            
            self.audit_service.log_action(
                action='DELETE_GROUP_POLICY',
                resource_type='GROUP_ASSIGNMENT',
                resource_name=f"{group_email} → {filter_value}",
                status='SUCCESS',
                details={
                    'group_email': group_email,
                    'filter_value': filter_value,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table
                }
            )
            
            ui.notify(f"Policy deleted: {group_email} → {filter_value}", type="positive")
            self.refresh_existing_policies_grid()
            
        except Exception as e:
            ui.notify(f"Error deleting policy: {e}", type="negative")

    def refresh_existing_policies_grid(self):
        """Atualiza o grid de políticas existentes"""
        if self.existing_policies_grid:
            existing_data = self.load_existing_policies_from_db()
            self.existing_policies_grid.options['rowData'] = existing_data
            self.existing_policies_grid.update()

    def refresh_filter_list(self):
        """Atualiza a lista de filtros na UI com checkboxes"""
        if self.filter_container:
            self.filter_container.clear()
            with self.filter_container:
                if not self.filter_values:
                    ui.label("No filters added yet").classes('text-grey-5 italic')
                else:
                    for filter_value in self.filter_values:
                        with ui.row().classes('w-full items-center justify-between p-2 border rounded hover:bg-grey-1'):
                            ui.checkbox(
                                text=filter_value,
                                value=filter_value in self.selected_filters,
                                on_change=lambda e, f=filter_value: self.toggle_filter_selection(f, e.value)
                            ).classes('flex-1')
                            ui.button(
                                icon='delete',
                                on_click=lambda f=filter_value: self.remove_filter_from_list(f)
                            ).props('flat dense color=negative').tooltip('Remove from list')

    def toggle_filter_selection(self, filter_value, is_selected):
        """Toggle seleção de filtro"""
        if is_selected:
            self.selected_filters.add(filter_value)
        else:
            self.selected_filters.discard(filter_value)

    def remove_filter_from_list(self, filter_value):
        """Remove filtro da lista (apenas UI)"""
        if filter_value in self.filter_values:
            self.filter_values.remove(filter_value)
            self.selected_filters.discard(filter_value)
            ui.notify(f"Filter '{filter_value}' removed from list", type="info")
            self.refresh_filter_list()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Assign Values to Row Level Policy (Groups)').classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Select Policy"
        self.step2_title = "Manage Group Assignments"

        with self.stepper:
            self.step1()
            self.step2_with_tabs()

    def get_policies(self):
        query_get_policies = f"""
            SELECT
              `policy_name` as `Policy Name`,
              `project_id` as `Project ID`,
              `dataset_id` as `Dataset ID`,
              `table_name` as `Table Name`,
              `field_id` as `Field ID`,
              `group_email` as `Group Email`
            FROM
              `{config.POLICY_TABLE}` 
            WHERE
              `policy_type` = 'group';
        """
        try:
            query_job = client.query(query_get_policies)
            results = [dict(row) for row in query_job]
            return results
        except GoogleAPIError as e:
            ui.notify(f"Error fetching policies: {e}", type="negative")
            return []
        except Exception as e:
            ui.notify(f"Unexpected error fetching policies: {e}", type="negative")
            return []

    def run_insert_values_to_group(self):
        """Insere apenas os filtros SELECIONADOS"""
        if not self.selected_filters:
            ui.notify("Please select at least one filter value to insert.", type="warning")
            return

        try:
            insert_statements = []
            for filter_value in self.selected_filters:
                insert_statements.append(f"""
                    INSERT INTO `{config.FILTER_TABLE}` 
                    (rls_type, policy_name, project_id, dataset_id, table_id, field_id, filter_value, rls_group)
                    VALUES
                    ('group', '{self.selected_policy_name}', '{self.project_id}', '{self.selected_policy_dataset}', '{self.selected_policy_table}', '{self.selected_policy_field}', '{filter_value}', '{self.selected_policy_group_email}')
                """)

            # Execute all inserts
            for insert_statement in insert_statements:
                query_job = client.query(insert_statement)
                query_job.result()

            # Log success
            self.audit_service.log_action(
                action='ASSIGN_VALUE_TO_GROUP',
                resource_type='GROUP_ASSIGNMENT',
                resource_name=f"{self.selected_policy_group_email} → {self.selected_policy_name}",
                status='SUCCESS',
                details={
                    'group_email': self.selected_policy_group_email,
                    'policy_name': self.selected_policy_name,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table,
                    'field': self.selected_policy_field,
                    'filter_values': list(self.selected_filters),
                    'filter_count': len(self.selected_filters)
                }
            )

            ui.notify(f"Successfully inserted {len(self.selected_filters)} filter values for group {self.selected_policy_group_email}", type="positive")
            
            # Limpar seleções
            self.selected_filters.clear()
            
            # Recarregar grid
            self.refresh_existing_policies_grid()
            self.refresh_filter_list()

        except GoogleAPIError as error:
            self.audit_service.log_action(
                action='ASSIGN_VALUE_TO_GROUP',
                resource_type='GROUP_ASSIGNMENT',
                resource_name=f"{self.selected_policy_group_email} → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'group_email': self.selected_policy_group_email,
                    'policy_name': self.selected_policy_name,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table,
                    'filter_count': len(self.selected_filters)
                }
            )
            ui.notify(f"Error inserting data: {error}", type="negative")
            
        except Exception as error:
            self.audit_service.log_action(
                action='ASSIGN_VALUE_TO_GROUP',
                resource_type='GROUP_ASSIGNMENT',
                resource_name=f"{self.selected_policy_group_email} → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'group_email': self.selected_policy_group_email,
                    'policy_name': self.selected_policy_name
                }
            )
            ui.notify(f"An unexpected error occurred: {error}", type="negative")

    async def get_selected_row(self):
        rows = await self.grid_step1.get_selected_rows()
        if not rows:
            ui.notify('No rows selected.', type="warning")
            self.step1_next_button.set_visibility(False)
            return

        self.selected_policy = rows
        self.step1_next_button.set_visibility(True)

    def update_policy_values(self):
        if not self.selected_policy:
            ui.notify("No policy selected.", type="warning")
            return

        selected_policy = self.selected_policy[0]

        self.selected_policy_name = selected_policy['Policy Name']
        self.selected_policy_dataset = selected_policy['Dataset ID']
        self.selected_policy_table = selected_policy['Table Name']
        self.selected_policy_field = selected_policy['Field ID']
        self.selected_policy_group_email = selected_policy['Group Email']

        self.stepper.next()

    def step1(self):
        with ui.step(self.step1_title):
            self.policy_list = self.get_policies()

            self.grid_step1 = ui.aggrid({
                'columnDefs': [
                    {'field': 'Policy Name', 'checkboxSelection': True, 'filter': 'agTextColumnFilter'},
                    {'field': 'Project ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Dataset ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Table Name', 'filter': 'agTextColumnFilter'},
                    {'field': 'Field ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Group Email', 'filter': 'agTextColumnFilter'},
                ],
                'rowData': self.policy_list,
                'rowSelection': 'single',
            }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_row)

            with ui.stepper_navigation():
                self.step1_next_button = ui.button("NEXT", icon="arrow_forward_ios",
                                                    on_click=self.update_policy_values)
                self.step1_next_button.set_visibility(False)

    def add_filter(self):
        filter_value = self.filter_input.value.strip()
        if filter_value:
            if filter_value not in self.filter_values:
                self.filter_values.append(filter_value)
                self.selected_filters.add(filter_value)  # Adicionar como selecionado por padrão
                self.filter_input.value = ''
                self.refresh_filter_list()
                ui.notify(f"Filter '{filter_value}' added", type="positive")
            else:
                ui.notify("Filter already added.", type="warning")
        else:
            ui.notify("Invalid filter value.", type="warning")

    async def delete_selected_existing_policy(self):
        """Deleta política selecionada no grid"""
        rows = await self.existing_policies_grid.get_selected_rows()
        if not rows:
            ui.notify('No rows selected to delete.', type="warning")
            return
        
        for row in rows:
            self.delete_policy_from_db(row['group_email'], row['filter_value'])

    def step2_with_tabs(self):
        """Step 2 com duas abas: Existing Policies e Add New"""
        with ui.step(self.step2_title):
            ui.label(f"Managing filters for Group: {self.selected_policy_group_email}").classes('text-h6 font-bold mb-2')
            
            with ui.tabs().classes('w-full') as tabs:
                tab_existing = ui.tab('Existing Policies', icon='list')
                tab_new = ui.tab('Add New Values', icon='add_circle')
            
            with ui.tab_panels(tabs, value=tab_existing).classes('w-full'):
                # TAB 1: Existing Policies
                with ui.tab_panel(tab_existing):
                    ui.label("Current Group Policy Assignments").classes('text-h6 font-bold mb-4')
                    ui.label("Select rows and click DELETE to remove from database").classes('text-caption text-grey-7 mb-2')
                    
                    existing_data = self.load_existing_policies_from_db()
                    
                    self.existing_policies_grid = ui.aggrid({
                        'columnDefs': [
                            {'field': 'group_email', 'headerName': 'Group Email', 'checkboxSelection': True, 'filter': 'agTextColumnFilter'},
                            {'field': 'filter_value', 'headerName': 'Filter Value', 'filter': 'agTextColumnFilter'},
                            {'field': 'policy_name', 'headerName': 'Policy Name', 'filter': 'agTextColumnFilter'},
                            {'field': 'field_id', 'headerName': 'Field', 'filter': 'agTextColumnFilter'},
                            {'field': 'created_at', 'headerName': 'Created At', 'filter': 'agTextColumnFilter'},
                        ],
                        'rowData': existing_data,
                        'rowSelection': 'multiple',
                    }).classes('w-full max-h-96 ag-theme-quartz')
                    
                    with ui.row().classes('mt-4'):
                        ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_existing_policy).props('color=negative')
                        ui.button("REFRESH", icon="refresh", on_click=self.refresh_existing_policies_grid).props('flat')
                
                # TAB 2: Add New Values
                with ui.tab_panel(tab_new):
                    ui.label("Add New Filter Values").classes('text-h6 font-bold mb-4')
                    ui.label("Add filters, select checkboxes, then click INSERT").classes('text-caption text-grey-7 mb-2')
                    
                    with ui.column().classes('w-full items-center'):
                        with ui.card().classes('w-3/4'):
                            ui.label("Add Filter Values:").classes('font-bold')
                            
                            with ui.row().classes('w-full gap-2'):
                                self.filter_input = ui.input(placeholder="Tecnologia da Informação").classes('flex-1')
                                ui.button("ADD FILTER", on_click=self.add_filter).props('color=primary')
                            
                            ui.separator()
                            ui.label("Filter Values (check to insert)").classes('font-bold text-sm text-grey-7')
                            
                            with ui.card().classes('w-full min-h-48 max-h-96 overflow-auto'):
                                self.filter_container = ui.column().classes('w-full gap-1')
                                self.refresh_filter_list()

            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button("INSERT SELECTED", icon="enhanced_encryption", on_click=self.run_insert_values_to_group).props('color=primary')

    def run(self):
        with theme.frame('Assign Values to Group Policy'):
            pass
