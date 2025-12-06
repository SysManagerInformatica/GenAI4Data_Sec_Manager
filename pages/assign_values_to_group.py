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
from theme import get_text  # <- NOVO
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService

config = Config()

client = bigquery.Client(project=config.PROJECT_ID)


class RLSAssignValuestoGroup:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = get_text('rls_assign_groups_page_title')  # <- TRADUZIDO

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
            ui.notify(get_text('msg_error_loading_policies', error=str(e)), type="negative")  # <- TRADUZIDO
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
            
            ui.notify(get_text('msg_group_policy_deleted', group=group_email, filter_value=filter_value), type="positive")  # <- TRADUZIDO
            self.refresh_existing_policies_grid()
            
        except Exception as e:
            ui.notify(get_text('msg_error_deleting_policy', error=str(e)), type="negative")  # <- TRADUZIDO

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
                    ui.label(get_text('msg_no_filters_added')).classes('text-grey-5 italic')  # <- TRADUZIDO
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
                            ).props('flat dense color=negative').tooltip(get_text('tooltip_remove_from_list'))  # <- TRADUZIDO

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
            ui.notify(get_text('msg_filter_removed', filter_value=filter_value), type="info")  # <- TRADUZIDO
            self.refresh_filter_list()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label(get_text('rls_assign_groups_subtitle')).classes('text-primary text-center text-bold')  # <- TRADUZIDO

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = get_text('rls_assign_groups_step1_title')  # <- TRADUZIDO
        self.step2_title = get_text('rls_assign_groups_step2_title')  # <- TRADUZIDO

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
            ui.notify(get_text('msg_error_fetch_policies', error=str(e)), type="negative")  # <- TRADUZIDO
            return []
        except Exception as e:
            ui.notify(get_text('msg_error_unexpected_fetch_policies', error=str(e)), type="negative")  # <- TRADUZIDO
            return []

    def run_insert_values_to_group(self):
        """Insere apenas os filtros SELECIONADOS"""
        if not self.selected_filters:
            ui.notify(get_text('msg_select_at_least_one_filter'), type="warning")  # <- TRADUZIDO
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

            for insert_statement in insert_statements:
                query_job = client.query(insert_statement)
                query_job.result()

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

            ui.notify(get_text('msg_inserted_filters_for_group', count=len(self.selected_filters), group=self.selected_policy_group_email), type="positive")  # <- TRADUZIDO
            
            self.selected_filters.clear()
            
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
            ui.notify(get_text('msg_error_inserting_data', error=str(error)), type="negative")  # <- TRADUZIDO
            
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
            ui.notify(get_text('msg_error_unexpected', error=str(error)), type="negative")  # <- TRADUZIDO

    async def get_selected_row(self):
        rows = await self.grid_step1.get_selected_rows()
        if not rows:
            ui.notify(get_text('msg_no_rows_selected'), type="warning")  # <- TRADUZIDO
            self.step1_next_button.set_visibility(False)
            return

        self.selected_policy = rows
        self.step1_next_button.set_visibility(True)

    def update_policy_values(self):
        if not self.selected_policy:
            ui.notify(get_text('msg_no_policy_selected'), type="warning")  # <- TRADUZIDO
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
                self.step1_next_button = ui.button(get_text('btn_next'), icon="arrow_forward_ios",  # <- TRADUZIDO
                                                    on_click=self.update_policy_values)
                self.step1_next_button.set_visibility(False)

    def add_filter(self):
        filter_value = self.filter_input.value.strip()
        if filter_value:
            if filter_value not in self.filter_values:
                self.filter_values.append(filter_value)
                self.selected_filters.add(filter_value)
                self.filter_input.value = ''
                self.refresh_filter_list()
                ui.notify(get_text('msg_filter_added', filter_value=filter_value), type="positive")  # <- TRADUZIDO
            else:
                ui.notify(get_text('msg_filter_already_added'), type="warning")  # <- TRADUZIDO
        else:
            ui.notify(get_text('msg_invalid_filter'), type="warning")  # <- TRADUZIDO

    async def delete_selected_existing_policy(self):
        """Deleta política selecionada no grid"""
        rows = await self.existing_policies_grid.get_selected_rows()
        if not rows:
            ui.notify(get_text('msg_no_rows_selected_delete'), type="warning")  # <- TRADUZIDO
            return
        
        for row in rows:
            self.delete_policy_from_db(row['group_email'], row['filter_value'])

    def step2_with_tabs(self):
        """Step 2 com duas abas: Existing Policies e Add New"""
        with ui.step(self.step2_title):
            ui.label(get_text('rls_assign_groups_managing_for', group=self.selected_policy_group_email)).classes('text-h6 font-bold mb-2')  # <- TRADUZIDO
            
            with ui.tabs().classes('w-full') as tabs:
                tab_existing = ui.tab(get_text('tab_existing_policies'), icon='list')  # <- TRADUZIDO
                tab_new = ui.tab(get_text('tab_add_new_values'), icon='add_circle')  # <- TRADUZIDO
            
            with ui.tab_panels(tabs, value=tab_existing).classes('w-full'):
                with ui.tab_panel(tab_existing):
                    ui.label(get_text('rls_assign_groups_current_assignments')).classes('text-h6 font-bold mb-4')  # <- TRADUZIDO
                    ui.label(get_text('rls_assign_users_select_delete_desc')).classes('text-caption text-grey-7 mb-2')  # <- TRADUZIDO (reutiliza)
                    
                    existing_data = self.load_existing_policies_from_db()
                    
                    self.existing_policies_grid = ui.aggrid({
                        'columnDefs': [
                            {'field': 'group_email', 'headerName': get_text('col_group_email'), 'checkboxSelection': True, 'filter': 'agTextColumnFilter'},  # <- TRADUZIDO
                            {'field': 'filter_value', 'headerName': get_text('col_filter_value'), 'filter': 'agTextColumnFilter'},  # <- TRADUZIDO
                            {'field': 'policy_name', 'headerName': get_text('col_policy_name'), 'filter': 'agTextColumnFilter'},  # <- TRADUZIDO
                            {'field': 'field_id', 'headerName': get_text('col_field'), 'filter': 'agTextColumnFilter'},  # <- TRADUZIDO
                            {'field': 'created_at', 'headerName': get_text('col_created_at'), 'filter': 'agTextColumnFilter'},  # <- TRADUZIDO
                        ],
                        'rowData': existing_data,
                        'rowSelection': 'multiple',
                    }).classes('w-full max-h-96 ag-theme-quartz')
                    
                    with ui.row().classes('mt-4'):
                        ui.button(get_text('btn_delete_selected'), icon="delete", on_click=self.delete_selected_existing_policy).props('color=negative')  # <- TRADUZIDO
                        ui.button(get_text('btn_refresh'), icon="refresh", on_click=self.refresh_existing_policies_grid).props('flat')  # <- TRADUZIDO
                
                with ui.tab_panel(tab_new):
                    ui.label(get_text('rls_assign_groups_add_new_title')).classes('text-h6 font-bold mb-4')  # <- TRADUZIDO
                    ui.label(get_text('rls_assign_groups_add_new_desc')).classes('text-caption text-grey-7 mb-2')  # <- TRADUZIDO
                    
                    with ui.column().classes('w-full items-center'):
                        with ui.card().classes('w-3/4'):
                            ui.label(get_text('rls_assign_users_add_filters')).classes('font-bold')  # <- TRADUZIDO (reutiliza)
                            
                            with ui.row().classes('w-full gap-2'):
                                self.filter_input = ui.input(placeholder=get_text('placeholder_filter_value')).classes('flex-1')  # <- TRADUZIDO
                                ui.button(get_text('btn_add_filter'), on_click=self.add_filter).props('color=primary')  # <- TRADUZIDO
                            
                            ui.separator()
                            ui.label(get_text('rls_assign_users_filter_list_label')).classes('font-bold text-sm text-grey-7')  # <- TRADUZIDO (reutiliza)
                            
                            with ui.card().classes('w-full min-h-48 max-h-96 overflow-auto'):
                                self.filter_container = ui.column().classes('w-full gap-1')
                                self.refresh_filter_list()

            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)  # <- TRADUZIDO
                ui.button(get_text('btn_insert_selected'), icon="enhanced_encryption", on_click=self.run_insert_values_to_group).props('color=primary')  # <- TRADUZIDO

    def run(self):
        with theme.frame(get_text('rls_assign_groups_frame_title')):  # <- TRADUZIDO
            pass
