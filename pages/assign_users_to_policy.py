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

        self.headers()
        self.stepper_setup()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Assign Users to Row Level Policy').classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Select Policy"
        self.step2_title = "Insert Users and Filters"

        with self.stepper:
            self.step1()
            self.step2()

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
        if not self.user_list:
            ui.notify("Please add at least one user email.", type="warning")
            return

        if not self.filter_values:
            ui.notify("Please select at least one filter value.", type="warning")
            return

        try:
            insert_statements = []
            for user in self.user_list:
                for filter_value in self.filter_values:
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

            # Log success for each user assignment
            for user in self.user_list:
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
                        'filter_values': self.filter_values,
                        'filter_count': len(self.filter_values)
                    }
                )

            with ui.dialog() as dialog, ui.card():
                ui.label('Users and Filters inserted successfully!').classes('text-positive font-bold')
                with ui.row().classes('w-full justify-center'):
                    ui.button('Close', on_click=ui.navigate.reload)
            dialog.open()

        except GoogleAPIError as error:
            # Log failure
            self.audit_service.log_action(
                action='ASSIGN_USER_TO_POLICY',
                resource_type='USER_ASSIGNMENT',
                resource_name=f"multiple_users → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'user_count': len(self.user_list),
                    'policy_name': self.selected_policy_name,
                    'dataset': self.selected_policy_dataset,
                    'table': self.selected_policy_table
                }
            )
            ui.notify(f"Error inserting data: {error}", type="negative")
            
        except Exception as error:
            # Log exception
            self.audit_service.log_action(
                action='ASSIGN_USER_TO_POLICY',
                resource_type='USER_ASSIGNMENT',
                resource_name=f"multiple_users → {self.selected_policy_name}",
                status='FAILED',
                error_message=str(error),
                details={
                    'user_count': len(self.user_list),
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

        self.selected_policy = [dict(row) for row in rows]
        self.step1_next_button.set_visibility(True)

    def update_policy_values(self):
        if not self.selected_policy:
            ui.notify("No policy selected.", type="warning")
            return

        self.selected_policy_name = self.selected_policy[0]['Policy Name']
        self.selected_policy_dataset = self.selected_policy[0]['Dataset ID']
        self.selected_policy_table = self.selected_policy[0]['Table Name']
        self.selected_policy_field = self.selected_policy[0]['Field ID']
       

        # self.fetch_distinct_values()
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
                    {'field': 'Field ID', 'filter': 'agTextColumnFilter'}
                ],
                'rowData': self.policy_list,
                'rowSelection': 'single',
            }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_row)

            with ui.stepper_navigation():
                self.step1_next_button = ui.button("NEXT", icon="arrow_forward_ios",
                                                    on_click=self.update_policy_values)
                self.step1_next_button.set_visibility(False)

    def add_user(self):
        email = self.user_input.value.strip()
        if "@" in email and "." in email:
            if email not in self.user_list:
                self.user_list.append(email)
                self.grid_1.options['rowData'] = [{"User email": u} for u in self.user_list]
                self.grid_1.update()
                self.user_input.value = ''
            else:
                ui.notify("User already added.", type="warning")
        else:
            ui.notify("Invalid email address.", type="warning")

    def add_filter(self):
        filter_value = self.filter_input.value.strip()
        if filter_value:
            if filter_value not in self.filter_values:
                self.filter_values.append(filter_value)
                self.grid_2.options['rowData'] = [{"Filter Values": f} for f in self.filter_values]
                self.grid_2.update()
                self.filter_input.value = ''
            else:
                ui.notify("Filter already added.", type="warning")
        else:
            ui.notify("Invalid filter value.", type="warning")

    async def get_selected_filters(self):
        rows = await self.grid_2.get_selected_rows()
        self.filter_values = [row['Filter Values'] for row in rows] if rows else []
        if not rows:
            ui.notify('No filters selected.', type="warning")

    def step2(self):
        with ui.step(self.step2_title):
            with ui.row().classes('w-full justify-center'):
                with ui.grid(columns=2).classes('gap-8 w-full justify-center'):
                    with ui.column().classes('items-left text-left'):
                        ui.label("Add User Emails:")
                        self.user_input = ui.input(placeholder="user@example.com").classes('w-full')
                        ui.button("Add User", on_click=self.add_user)

                        self.grid_1 = ui.aggrid({
                            'columnDefs': [
                                {'field': 'User email', 'filter': 'agTextColumnFilter'},
                            ],
                            'rowData': [],
                            'rowSelection': 'multiple',
                        }).classes('max-h-160 ag-theme-quartz')

                    with ui.column().classes('items-left text-left'):
                        ui.label("Add Filter Values:")
                        self.filter_input = ui.input().classes('w-full')
                        ui.button("Add Filter", on_click=self.add_filter)
                        self.grid_2 = ui.aggrid({
                            'columnDefs': [
                                {'field': 'Filter Values', 'checkboxSelection': True, 'filter': 'agTextColumnFilter'},
                            ],
                            'rowData': [],
                            'rowSelection': 'multiple',
                        }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_filters)

            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button("Insert", icon="enhanced_encryption", on_click=self.run_insert_users_and_values)

    def run(self):
        with theme.frame('Assign Users to Policy'):
            pass  # The stepper is already created in the constructor
