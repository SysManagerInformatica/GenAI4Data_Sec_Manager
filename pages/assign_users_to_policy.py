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


class RLSAssignUserstoPolicy:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Assign Users to Row Level Policy"

        self.selected_policy_name = None
        self.selected_policy_dataset = None
        self.selected_policy_table = None
        self.selected_policy_field = None
        self.selected_policy = {}

        self.user_list = []
        self.filter_values = []
        
        # Para tracking de seleção
        self.selected_users = set()
        self.selected_filters = set()
        
        # Containers para UI
        self.user_container = None
        self.filter_container = None
        self.existing_policies_grid = None

        self.headers()
        self.stepper_setup()

    def load_existing_policies_from_db(self):
        """Carrega TODAS as políticas existentes do banco de dados"""
        if not self.selected_policy_dataset or not self.selected_policy_table:
            return []
        
        query = f"""
        SELECT 
            username,
            filter_value,
            policy_name,
            field_id,
            CAST(created_at AS STRING) as created_at
        FROM `{config.FILTER_TABLE}`
        WHERE rls_type = 'users'
          AND project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
        ORDER BY username, filter_value
        """
        
        try:
            query_job = client.query(query)
            results = [dict(row) for row in query_job]
            return results
        except Exception as e:
            ui.notify(f"Error loading existing policies: {e}", type="negative")
            return []

    def delete_policy_from_db(self, username, filter_value):
        """Deleta política do BigQuery"""
        query = f"""
        DELETE FROM `{config.FILTER_TABLE}`
        WHERE rls_type = 'users'
          AND project_id = '{self.project_id}'
          AND dataset_id = '{self.selected_policy_dataset}'
          AND table_id = '{self.selected_policy_table}'
          AND username = '{username}'
          AND filter_value = '{filter_value}'
        """
        
        try:
            query_job = client.query(query)
            query_job.result()
            
            # Log audit
            self.audit_service.log_action(
                action='DELETE_USER_POLICY',
                resource_type='USER_ASSIGNMENT',
                resource_name=f"{username} → {filter_value}",
                status='SUCCESS',
                details={
                    'username': username,
                    'filter_value': filter_value,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table
                }
            )
            
            ui.notify(f"Policy deleted: {username} → {filter_value}", type="positive")
            # Recarregar grid
            self.refresh_existing_policies_grid()
            
        except Exception as e:
            ui.notify(f"Error deleting policy: {e}", type="negative")

    def delete_rls_policy_from_bigquery(self, policy_name, dataset, table):
        """Deleta a política RLS completa do BigQuery"""
        try:
            # 1. DROP ROW ACCESS POLICY no BigQuery
            query_drop_policy = f"""
            DROP ROW ACCESS POLICY `{policy_name}`
            ON `{self.project_id}.{dataset}.{table}`;
            """
            client.query(query_drop_policy).result()
            
            # 2. Deletar da tabela de políticas
            query_delete_from_policy_table = f"""
            DELETE FROM `{config.POLICY_TABLE}`
            WHERE policy_name = '{policy_name}'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{dataset}'
              AND table_name = '{table}';
            """
            client.query(query_delete_from_policy_table).result()
            
            # 3. Deletar todos os filtros associados
            query_delete_filters = f"""
            DELETE FROM `{config.FILTER_TABLE}`
            WHERE policy_name = '{policy_name}'
              AND project_id = '{self.project_id}'
              AND dataset_id = '{dataset}'
              AND table_id = '{table}';
            """
            client.query(query_delete_filters).result()
            
            # Log success
            self.audit_service.log_action(
                action='DELETE_RLS_POLICY',
                resource_type='RLS_POLICY',
                resource_name=policy_name,
                status='SUCCESS',
                details={
                    'policy_name': policy_name,
                    'dataset': dataset,
                    'table': table,
                    'deleted_from': ['BigQuery', 'policies_table', 'policies_filters']
                }
            )
            
            return True
            
        except Exception as e:
            # Log failure
            self.audit_service.log_action(
                action='DELETE_RLS_POLICY',
                resource_type='RLS_POLICY',
                resource_name=policy_name,
                status='FAILED',
                error_message=str(e),
                details={
                    'policy_name': policy_name,
                    'dataset': dataset,
                    'table': table
                }
            )
            ui.notify(f"Error deleting policy '{policy_name}': {str(e)}", type="negative")
            return False

    async def delete_selected_policies(self):
        """Deleta políticas selecionadas no grid do Step 1"""
        rows = await self.grid_step1.get_selected_rows()
        if not rows:
            ui.notify('No policies selected to delete.', type="warning")
            return
        
        policy_names = [row['Policy Name'] for row in rows]
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f"Delete {len(policy_names)} policy(ies)?").classes('text-h6 mb-2')
            with ui.column().classes('mb-4 max-h-64 overflow-auto'):
                for name in policy_names[:10]:
                    ui.label(f"• {name}").classes('text-sm')
                if len(policy_names) > 10:
                    ui.label(f"... and {len(policy_names) - 10} more").classes('text-sm italic text-grey-7')
            ui.label('⚠️ This will delete the RLS policy from BigQuery and all associated filters!').classes('text-negative font-bold mb-2')
            ui.label('This action cannot be undone.').classes('text-sm text-grey-7 mb-4')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'DELETE', 
                    on_click=lambda: self.execute_policy_deletion(rows, confirm_dialog)
                ).props('color=negative')
        
        confirm_dialog.open()

    def execute_policy_deletion(self, rows, dialog):
        """Executa a deleção das políticas"""
        dialog.close()
        
        success_count = 0
        fail_count = 0
        
        for row in rows:
            policy_name = row['Policy Name']
            dataset = row['Dataset ID']
            table = row['Table Name']
            
            if self.delete_rls_policy_from_bigquery(policy_name, dataset, table):
                success_count += 1
            else:
                fail_count += 1
        
        # Refresh grid
        self.policy_list = self.get_policies()
        self.grid_step1.options['rowData'] = self.policy_list
        self.grid_step1.update()
        
        # Summary message
        if fail_count == 0:
            ui.notify(f"✅ Successfully deleted {success_count} policy(ies)!", type="positive")
        else:
            ui.notify(f"⚠️ Deleted {success_count}, {fail_count} failed.", type="warning")

    # ✅ NOVO MÉTODO: DROP ALL FROM TABLE
    async def drop_all_from_selected_tables(self):
        """Remove TODAS as políticas RLS das tabelas selecionadas (DROP ALL)"""
        rows = await self.grid_step1.get_selected_rows()
        if not rows:
            ui.notify('No policies selected', type="warning")
            return
        
        # Agrupar policies por tabela
        tables_map = {}
        for policy in rows:
            table_key = f"{policy['Dataset ID']}.{policy['Table Name']}"
            if table_key not in tables_map:
                tables_map[table_key] = {
                    'dataset_id': policy['Dataset ID'],
                    'table_name': policy['Table Name'],
                    'policies': []
                }
            tables_map[table_key]['policies'].append(policy['Policy Name'])
        
        # Dialog de confirmação CRÍTICO
        with ui.dialog() as confirm_dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('⚠️ DROP ALL ROW ACCESS POLICIES').classes('text-h5 font-bold text-red-600 mb-4')
            
            with ui.card().classes('w-full bg-red-50 p-4 mb-4 border-2 border-red-500'):
                ui.label('🚨 CRITICAL WARNING').classes('text-red-700 font-bold mb-2')
                ui.label('This will remove ALL Row Access Policies from the selected tables!').classes('text-sm mb-2')
                ui.label('After this action, tables will be ACCESSIBLE TO ALL USERS with table permissions.').classes('text-sm font-bold text-red-600')
            
            ui.label('Affected Tables:').classes('font-bold mb-2')
            
            for table_key, table_info in tables_map.items():
                with ui.card().classes('w-full bg-orange-50 p-3 mb-2'):
                    ui.label(f"📋 {table_key}").classes('font-bold text-sm mb-1')
                    ui.label(f"   Policies to remove: {len(table_info['policies'])}").classes('text-xs text-grey-7')
                    
                    # Mostrar nomes das policies
                    with ui.expansion('Show policy names', icon='list').classes('w-full text-xs'):
                        for policy_name in table_info['policies']:
                            ui.label(f"  • {policy_name}").classes('text-xs')
            
            with ui.card().classes('w-full bg-yellow-50 p-3 mt-4'):
                ui.label('💡 Alternative: If you want to keep access control, create a new policy before dropping these.').classes('text-xs')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'DROP ALL POLICIES',
                    icon='delete_forever',
                    on_click=lambda: self.execute_drop_all(tables_map, confirm_dialog)
                ).props('color=negative')
        
        confirm_dialog.open()

    # ✅ NOVO MÉTODO: EXECUTAR DROP ALL
    def execute_drop_all(self, tables_map, dialog):
        """Executa DROP ALL ROW ACCESS POLICIES para cada tabela"""
        total_policies = 0
        success_tables = 0
        failed_tables = 0
        
        for table_key, table_info in tables_map.items():
            try:
                dataset_id = table_info['dataset_id']
                table_name = table_info['table_name']
                policies_count = len(table_info['policies'])
                
                # DROP ALL para remover todas de uma vez
                sql = f"""DROP ALL ROW ACCESS POLICIES ON `{self.project_id}.{dataset_id}.{table_name}`;"""
                
                print(f"[DEBUG] Executing DROP ALL for {table_key}")
                print(f"[DEBUG] SQL: {sql}")
                
                query_job = client.query(sql)
                query_job.result()
                
                # Deletar da tabela de políticas
                query_delete_policies = f"""
                DELETE FROM `{config.POLICY_TABLE}`
                WHERE project_id = '{self.project_id}'
                  AND dataset_id = '{dataset_id}'
                  AND table_name = '{table_name}'
                  AND policy_name IN ({','.join([f"'{p}'" for p in table_info['policies']])});
                """
                client.query(query_delete_policies).result()
                
                # Deletar filtros associados
                query_delete_filters = f"""
                DELETE FROM `{config.FILTER_TABLE}`
                WHERE project_id = '{self.project_id}'
                  AND dataset_id = '{dataset_id}'
                  AND table_id = '{table_name}'
                  AND policy_name IN ({','.join([f"'{p}'" for p in table_info['policies']])});
                """
                client.query(query_delete_filters).result()
                
                # Log audit
                self.audit_service.log_action(
                    action='DROP_ALL_RLS_POLICIES',
                    resource_type='TABLE',
                    resource_name=f"{dataset_id}.{table_name}",
                    status='SUCCESS',
                    details={
                        'policies_count': policies_count,
                        'policies_removed': table_info['policies'],
                        'warning': 'Table now accessible to all users with table permissions'
                    }
                )
                
                success_tables += 1
                total_policies += policies_count
                
                print(f"[SUCCESS] Dropped {policies_count} policies from {table_key}")
                
            except Exception as e:
                print(f"[ERROR] Failed to drop policies from {table_key}: {e}")
                
                self.audit_service.log_action(
                    action='DROP_ALL_RLS_POLICIES',
                    resource_type='TABLE',
                    resource_name=f"{dataset_id}.{table_name}",
                    status='FAILED',
                    error_message=str(e)
                )
                
                failed_tables += 1
        
        dialog.close()
        
        # Notificações
        if success_tables > 0:
            ui.notify(
                f"✅ Dropped {total_policies} policies from {success_tables} table(s)!",
                type="positive",
                timeout=5000
            )
        
        if failed_tables > 0:
            ui.notify(
                f"❌ Failed to drop policies from {failed_tables} table(s)",
                type="negative",
                timeout=5000
            )
        
        # Refresh grid
        self.policy_list = self.get_policies()
        self.grid_step1.options['rowData'] = self.policy_list
        self.grid_step1.update()

    def refresh_existing_policies_grid(self):
        """Atualiza o grid de políticas existentes"""
        if self.existing_policies_grid:
            existing_data = self.load_existing_policies_from_db()
            self.existing_policies_grid.options['rowData'] = existing_data
            self.existing_policies_grid.update()

    def refresh_user_list(self):
        """Atualiza a lista de usuários na UI com checkboxes"""
        if self.user_container:
            self.user_container.clear()
            with self.user_container:
                if not self.user_list:
                    ui.label("No users added yet").classes('text-grey-5 italic')
                else:
                    for user_email in self.user_list:
                        with ui.row().classes('w-full items-center justify-between p-2 border rounded hover:bg-grey-1'):
                            ui.checkbox(
                                text=user_email,
                                value=user_email in self.selected_users,
                                on_change=lambda e, u=user_email: self.toggle_user_selection(u, e.value)
                            ).classes('flex-1')
                            ui.button(
                                icon='delete',
                                on_click=lambda u=user_email: self.remove_user_from_list(u)
                            ).props('flat dense color=negative').tooltip('Remove from list')

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

    def toggle_user_selection(self, user_email, is_selected):
        """Toggle seleção de usuário"""
        if is_selected:
            self.selected_users.add(user_email)
        else:
            self.selected_users.discard(user_email)

    def toggle_filter_selection(self, filter_value, is_selected):
        """Toggle seleção de filtro"""
        if is_selected:
            self.selected_filters.add(filter_value)
        else:
            self.selected_filters.discard(filter_value)

    def remove_user_from_list(self, email):
        """Remove usuário da lista (apenas UI)"""
        if email in self.user_list:
            self.user_list.remove(email)
            self.selected_users.discard(email)
            ui.notify(f"User {email} removed from list", type="info")
            self.refresh_user_list()

    def remove_filter_from_list(self, filter_value):
        """Remove filtro da lista (apenas UI)"""
        if filter_value in self.filter_values:
            self.filter_values.remove(filter_value)
            self.selected_filters.discard(filter_value)
            ui.notify(f"Filter '{filter_value}' removed from list", type="info")
            self.refresh_filter_list()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Assign Users to Row Level Policy').classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Select Policy"
        self.step2_title = "Manage Assignments"

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
              `field_id` as `Field ID`
            FROM
              `{config.POLICY_TABLE}` 
            WHERE
              `policy_type` = 'users';
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

    def run_insert_users_and_values(self):
        """Insere apenas os usuários e filtros SELECIONADOS"""
        if not self.selected_users:
            ui.notify("Please select at least one user to insert.", type="warning")
            return

        if not self.selected_filters:
            ui.notify("Please select at least one filter to insert.", type="warning")
            return

        try:
            insert_statements = []
            for user in self.selected_users:
                for filter_value in self.selected_filters:
                    insert_statements.append(f"""
                        INSERT INTO `{config.FILTER_TABLE}` 
                        (rls_type, policy_name, project_id, dataset_id, table_id, field_id, filter_value, username)
                        VALUES
                        ('users', '{self.selected_policy_name}', '{self.project_id}', '{self.selected_policy_dataset}', '{self.selected_policy_table}', '{self.selected_policy_field}', '{filter_value}', '{user}')
                    """)

            # Execute all inserts
            for insert_statement in insert_statements:
                query_job = client.query(insert_statement)
                query_job.result()

            # Log success
            for user in self.selected_users:
                self.audit_service.log_action(
                    action='ASSIGN_USER_TO_POLICY',
                    resource_type='USER_ASSIGNMENT',
                    resource_name=f"{user} → {self.selected_policy_name}",
                    status='SUCCESS',
                    details={
                        'user_email': user,
                        'policy_name': self.selected_policy_name,
                        'dataset': self.selected_policy_dataset,
                        'table': self.selected_policy_table,
                        'field': self.selected_policy_field,
                        'filter_values': list(self.selected_filters),
                        'filter_count': len(self.selected_filters)
                    }
                )

            ui.notify(f"Successfully inserted {len(self.selected_users)} users × {len(self.selected_filters)} filters", type="positive")
            
            # Limpar seleções
            self.selected_users.clear()
            self.selected_filters.clear()
            
            # Recarregar grid de políticas existentes
            self.refresh_existing_policies_grid()
            self.refresh_user_list()
            self.refresh_filter_list()

        except GoogleAPIError as error:
            self.audit_service.log_action(
                action='ASSIGN_USER_TO_POLICY',
                resource_type='USER_ASSIGNMENT',
                resource_name=f"multiple_users → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'user_count': len(self.selected_users),
                    'policy_name': self.selected_policy_name,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table
                }
            )
            ui.notify(f"Error inserting data: {error}", type="negative")
            
        except Exception as error:
            self.audit_service.log_action(
                action='ASSIGN_USER_TO_POLICY',
                resource_type='USER_ASSIGNMENT',
                resource_name=f"multiple_users → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'user_count': len(self.selected_users),
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

        # Para avançar, precisa selecionar apenas 1 política
        if len(rows) == 1:
            self.selected_policy = [dict(row) for row in rows]
            self.step1_next_button.set_visibility(True)
        else:
            # Múltiplas seleções são apenas para deletar
            self.step1_next_button.set_visibility(False)

    def update_policy_values(self):
        if not self.selected_policy:
            ui.notify("No policy selected.", type="warning")
            return

        self.selected_policy_name = self.selected_policy[0]['Policy Name']
        self.selected_policy_dataset = self.selected_policy[0]['Dataset ID']
        self.selected_policy_table = self.selected_policy[0]['Table Name']
        self.selected_policy_field = self.selected_policy[0]['Field ID']
        
        self.stepper.next()

    def step1(self):
        with ui.step(self.step1_title):
            ui.label("Select ONE policy to manage, or select MULTIPLE to delete").classes('text-caption text-grey-7 mb-2')
            
            self.policy_list = self.get_policies()

            self.grid_step1 = ui.aggrid({
                'columnDefs': [
                    {'field': 'Policy Name', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 350},
                    {'field': 'Project ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Dataset ID', 'filter': 'agTextColumnFilter'},
                    {'field': 'Table Name', 'filter': 'agTextColumnFilter'},
                    {'field': 'Field ID', 'filter': 'agTextColumnFilter'}
                ],
                'rowData': self.policy_list,
                'rowSelection': 'multiple',
            }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_row)

            with ui.stepper_navigation():
                with ui.row().classes('w-full justify-between'):
                    # Lado esquerdo: Botões DELETE
                    with ui.row().classes('gap-2'):
                        ui.button(
                            "DELETE SELECTED", 
                            icon="delete", 
                            on_click=self.delete_selected_policies
                        ).props('color=negative flat')
                        
                        # ✅ NOVO: Botão DROP ALL FROM TABLE
                        ui.button(
                            "DROP ALL FROM TABLE",
                            icon="delete_forever",
                            on_click=self.drop_all_from_selected_tables
                        ).props('color=red outline').style('border: 2px solid red;').tooltip('⚠️ Removes ALL policies from selected tables')
                    
                    # Lado direito: Botão NEXT
                    self.step1_next_button = ui.button(
                        "NEXT", 
                        icon="arrow_forward_ios",
                        on_click=self.update_policy_values
                    )
                    self.step1_next_button.set_visibility(False)

    def add_user(self):
        email = self.user_input.value.strip()
        if "@" in email and "." in email:
            if email not in self.user_list:
                self.user_list.append(email)
                self.selected_users.add(email)
                self.user_input.value = ''
                self.refresh_user_list()
                ui.notify(f"User {email} added", type="positive")
            else:
                ui.notify("User already added.", type="warning")
        else:
            ui.notify("Invalid email address.", type="warning")

    def add_filter(self):
        filter_value = self.filter_input.value.strip()
        if filter_value:
            if filter_value not in self.filter_values:
                self.filter_values.append(filter_value)
                self.selected_filters.add(filter_value)
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
            self.delete_policy_from_db(row['username'], row['filter_value'])

    def step2_with_tabs(self):
        """Step 2 com duas abas: Existing Policies e Add New"""
        with ui.step(self.step2_title):
            with ui.tabs().classes('w-full') as tabs:
                tab_existing = ui.tab('Existing Policies', icon='list')
                tab_new = ui.tab('Add New Assignments', icon='add_circle')
            
            with ui.tab_panels(tabs, value=tab_existing).classes('w-full'):
                # TAB 1: Existing Policies
                with ui.tab_panel(tab_existing):
                    ui.label("Current Policy Assignments").classes('text-h6 font-bold mb-4')
                    ui.label("Select rows and click DELETE to remove from database").classes('text-caption text-grey-7 mb-2')
                    
                    existing_data = self.load_existing_policies_from_db()
                    
                    self.existing_policies_grid = ui.aggrid({
                        'columnDefs': [
                            {'field': 'username', 'headerName': 'User Email', 'checkboxSelection': True, 'filter': 'agTextColumnFilter'},
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
                
                # TAB 2: Add New Assignments
                with ui.tab_panel(tab_new):
                    ui.label("Add New User-Filter Assignments").classes('text-h6 font-bold mb-4')
                    ui.label("Add users and filters, select checkboxes, then click INSERT").classes('text-caption text-grey-7 mb-2')
                    
                    with ui.row().classes('w-full justify-center'):
                        with ui.grid(columns=2).classes('gap-8 w-full justify-center'):
                            # LEFT SIDE: User Emails
                            with ui.column().classes('items-left text-left w-full'):
                                ui.label("Add User Emails:").classes('font-bold')
                                
                                with ui.row().classes('w-full gap-2'):
                                    self.user_input = ui.input(placeholder="user@example.com").classes('flex-1')
                                    ui.button("ADD USER", on_click=self.add_user).props('color=primary')
                                
                                ui.separator()
                                ui.label("User Email (check to insert)").classes('font-bold text-sm text-grey-7')
                                
                                with ui.card().classes('w-full min-h-48 max-h-96 overflow-auto'):
                                    self.user_container = ui.column().classes('w-full gap-1')
                                    self.refresh_user_list()

                            # RIGHT SIDE: Filter Values
                            with ui.column().classes('items-left text-left w-full'):
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
                ui.button("INSERT SELECTED", icon="enhanced_encryption", on_click=self.run_insert_users_and_values).props('color=primary')

    def run(self):
        with theme.frame('Assign Users to Policy'):
            pass
