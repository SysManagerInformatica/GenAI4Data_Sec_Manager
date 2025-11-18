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
        self.page_title = "Assign Values to Row Level Policy"

        self.selected_policy_name = None
        self.selected_policy_dataset = None
        self.selected_policy_table = None
        self.selected_policy_field = None
        self.selected_policy_group_email = None
        self.selected_policy = {}

        self.filter_values = []

        self.headers()
        self.stepper_setup()

    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Assign Values to Row Level Policy').classes('text-primary text-center text-bold')

    def stepper_setup(self):
        self.stepper = ui.stepper().props("vertical").classes("w-full")
        self.step1_title = "Select Policy"
        self.step2_title = "Insert Filter Values"

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

        if not self.filter_values:
            ui.notify("Please select at least one filter value.", type="warning")
            return

        try:
            insert_statements = []
            for filter_value in self.filter_values:
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
                    'filter_values': self.filter_values,
                    'filter_count': len(self.filter_values)
                }
            )

            with ui.dialog() as dialog, ui.card():
                ui.label('Filter Values inserted successfully!').classes('text-positive font-bold')
                with ui.row().classes('w-full justify-center'):
                    ui.button('Close', on_click=ui.navigate.reload)
            dialog.open()

        except GoogleAPIError as error:
            # Log failure
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
                    'filter_count': len(self.filter_values)
                }
            )
            ui.notify(f"Error inserting data: {error}", type="negative")
            
        except Exception as error:
            # Log exception
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
            ui.label(f"Add Filter Values for Group: {self.selected_policy_group_email}")
            self.filter_input = ui.input(label="Filter Value").classes('w-full')
            ui.button(f"Add Filter", on_click=self.add_filter)
            self.grid_2 = ui.aggrid({
                'columnDefs': [
                    {'field': 'Filter Values', 'filter': 'agTextColumnFilter'},
                ],
                'rowData': [],
                'rowSelection': 'multiple', # Enable multiple row selection
            }).classes('max-h-160 ag-theme-quartz').on('rowSelected', self.get_selected_filters)

            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button("Insert", icon="enhanced_encryption", on_click=self.run_insert_values_to_group)

    def run(self):
        with theme.frame('Assign Values to Policy'):
            pass
