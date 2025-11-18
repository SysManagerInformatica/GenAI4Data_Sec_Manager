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
from wonderwords import RandomWord
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService


config = Config()
r = RandomWord()


client = bigquery.Client(project=config.PROJECT_ID)


class RLSCreateforGroups:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.table_list = None
        self.field_list = None

        self.page_title = "Create Row Level Policy - Groups"
        self.headers()

        self.stepper = ui.stepper().props("vertical").classes("w-full")

        self.step1_title = "Select Dataset"
        self.step2_title = "Select Table"
        self.step3_title = "Select Field"
        self.step4_title = "Enter the Group"
        self.step5_title = "Review and Run"


        self.selected_dataset = None
        self.selected_table = None
        self.selected_field = None
        self.group_assignment = None
        self.randon_word = r.word(include_parts_of_speech=["nouns", "adjectives"], word_min_length=3, word_max_length=8)
        self.policy_name = None

    def _update_selected_dataset(self, e):
        if not e.value:
            return  
        self.selected_dataset = e.value
        self.step1_next_button.set_visibility(True) 

    def _update_selected_table(self, e):
        self.selected_table = e.value
        self.step2_next_button.set_visibility(bool(e.value)) 

    def _update_selected_field(self, e):
        self.selected_field = e.value
        self.step3_next_button.set_visibility(bool(e.value))

    def _update_group_assignment(self, e):
        self.group_assignment = e.value
        self.step4_next_button.set_visibility(bool(e.value))

    def _step1_next_button_visibility(self):
         self.step1_next_button.set_visibility(bool(self.selected_dataset)) 


    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Create Row Level Security for Groups').classes('text-primary text-center text-bold') 


    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except GoogleAPIError as e:
            ui.notify(f"Error fetching datasets: {e}", type="negative")
            return []  # Return empty list on error
        except Exception as e:
            ui.notify(f"An unexpected error occurred: {e}", type="negative")
            return []


    def get_tables_in_dataset(self):
        if not self.selected_dataset:
            ui.notify("Please select a dataset first.", type="warning")
            return

        try:
            tables = client.list_tables(self.selected_dataset)
            table_ids = [table.table_id for table in tables]
            self.table_list.options = table_ids
            self.table_list.value = None  
            self.table_list.update()
            self.stepper.next()
            self.step2_next_button.set_visibility(False)
        except NotFound:
            ui.notify(f"Dataset not found: {self.selected_dataset}", type="negative")
        except GoogleAPIError as e:
            ui.notify(f"Error fetching tables: {e}", type="negative")
        except Exception as e:
            ui.notify(f"An unexpected error occurred: {e}", type="negative")



    def get_fields_in_table(self):
        if not self.selected_table:
            ui.notify("Please select a table first.", type="warning")
            return

        try:
            table_ref = client.dataset(self.selected_dataset).table(self.selected_table)
            table = client.get_table(table_ref)
            fields = [[schema_field.name, schema_field.field_type, schema_field.description] for schema_field in table.schema]
            self.field_list.options = fields
            self.field_list.value = None 
            self.field_list.update()
            self.stepper.next()
            self.step3_next_button.set_visibility(False) 
        except NotFound:
            ui.notify(f"Table not found: {self.selected_table}", type="negative")
        except GoogleAPIError as e:
            ui.notify(f"Error fetching fields: {e}", type="negative")
        except Exception as e:
            ui.notify(f"An unexpected error occurred: {e}", type="negative")

    def get_resume(self):
        if not self.selected_field:
            ui.notify("Please select a field first.", type="warning")
            return


        self.policy_name = f'{self.selected_dataset}_{self.selected_table}_{self.selected_field[0]}_{self.randon_word}'
        self.resume.content = f""" 
            ###**The following Row Level Security Policy will be created:**<br>

            **Policy Name**: {self.policy_name}<br>
            **Project ID**: {self.project_id}<br>
            **Dataset ID**: {self.selected_dataset}<br>
            **Table ID**: {self.selected_table}<br>
            **Field ID**: {self.selected_field[0]}<br>
            **Group Email**: {self.group_assignment}<br>
            <br>
            **Code**:

        """

        self.code.content = (
            f"CREATE OR REPLACE ROW ACCESS POLICY\n"
            f"  `{self.policy_name}`\n"
            f"ON\n"
            f"  `{self.project_id}.{self.selected_dataset}.{self.selected_table}`\n"
            f"GRANT TO (\"group:{self.group_assignment}\")\n"  
            f"FILTER USING ({self.selected_field[0]} IN\n"
            f"  (SELECT CAST(filter_value AS {self.selected_field[1]})\n"
            f"   FROM `{config.FILTER_TABLE}`\n" 
            f"   WHERE rls_type = 'group'\n"
            f"   AND policy_name = '{self.policy_name}'\n"
            f"   AND project_id = '{self.project_id}'\n"
            f"   AND dataset_id = '{self.selected_dataset}'\n"
            f"   AND table_id = '{self.selected_table}'\n"
            f"   AND field_id = '{self.selected_field[0]}'\n"
            f"   AND rls_group = '{self.group_assignment}'));"
        )
        self.stepper.next()

    def run_creation_policy(self):
        try:
            # Create RLS policy
            query_job = client.query(self.code.content)
            query_job.result()
            
            # Insert into policy table
            query_insert_into_policy_table = f"""
                INSERT INTO `{config.POLICY_TABLE}` (policy_type, policy_name, project_id, dataset_id, table_name, field_id, group_email)
                VALUES
                ('group', '{self.policy_name}', '{self.project_id}', '{self.selected_dataset}', '{self.selected_table}', '{self.selected_field[0]}', '{self.group_assignment}')  
            """
            query_job = client.query(query_insert_into_policy_table)
            query_job.result()
            
            # Log success
            self.audit_service.log_action(
                action='CREATE_RLS_POLICY_GROUP',
                resource_type='RLS_POLICY',
                resource_name=self.policy_name,
                status='SUCCESS',
                details={
                    'policy_type': 'group',
                    'dataset': self.selected_dataset,
                    'table': self.selected_table,
                    'field': self.selected_field[0],
                    'field_type': self.selected_field[1],
                    'group_email': self.group_assignment,
                    'filter_condition': f"{self.selected_field[0]} IN (SELECT filter_value WHERE rls_group = '{self.group_assignment}')"
                }
            )
            
            with ui.dialog() as dialog, ui.card():
                ui.label(f'Row Level Policy Created on {self.selected_table}.{self.selected_field[0]} successfully!').classes(replace='text-positive').classes('font-bold')
                with ui.row().classes('w-full justify-center'):  
                    ui.button('Close', on_click=ui.navigate.reload)  
            dialog.open()
            
        except GoogleAPIError as error:
            # Log failure
            self.audit_service.log_action(
                action='CREATE_RLS_POLICY_GROUP',
                resource_type='RLS_POLICY',
                resource_name=self.policy_name if self.policy_name else 'unknown',
                status='FAILED',
                error_message=str(error),
                details={
                    'dataset': self.selected_dataset,
                    'table': self.selected_table,
                    'field': self.selected_field[0] if self.selected_field else 'unknown',
                    'group_email': self.group_assignment
                }
            )
            ui.notify(f"Error creating row-level access policy: {error}", type="negative")
            
        except Exception as error:
            # Log exception
            self.audit_service.log_action(
                action='CREATE_RLS_POLICY_GROUP',
                resource_type='RLS_POLICY',
                resource_name=self.policy_name if self.policy_name else 'unknown',
                status='FAILED',
                error_message=str(error),
                details={
                    'dataset': self.selected_dataset,
                    'table': self.selected_table,
                    'field': self.selected_field[0] if self.selected_field else 'unknown',
                    'group_email': self.group_assignment
                }
            )
            ui.notify(f"An unexpected error occurred: {error}", type="negative")
            

    def step1(self):
        with ui.step(self.step1_title):
            dataset_list = self.get_datasets()
            ui.select(dataset_list, label="Select Dataset", on_change=self._update_selected_dataset)
            with ui.stepper_navigation():
                self.step1_next_button = ui.button("NEXT", icon="arrow_forward_ios", on_click=self.get_tables_in_dataset)
                self.step1_next_button.set_visibility(False)

    def step2(self):
        with ui.step(self.step2_title):
            self.table_list = ui.select([], label="Select Table", on_change=self._update_selected_table)
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step2_next_button = ui.button("NEXT", icon="arrow_forward_ios", on_click=self.get_fields_in_table)

                self.step2_next_button.set_visibility(False)
            return
        
    def step3(self):
        with ui.step(self.step3_title):
            self.field_list = ui.select([], label="Select Field", on_change=self._update_selected_field)
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step3_next_button = ui.button("NEXT", icon="arrow_forward_ios", on_click=self.stepper.next)

                self.step3_next_button.set_visibility(False)
            return

    def step4(self):
        with ui.step(self.step4_title):
            self.group_assignment = ui.input(placeholder="Enter the group email", on_change=self._update_group_assignment).props("size=50")
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step4_next_button = ui.button("NEXT", icon="arrow_forward_ios", on_click=self.get_resume)

                self.step4_next_button.set_visibility(False)
            return
        
    def step5(self):
        with ui.step(self.step5_title):
            self.resume = ui.markdown().classes(replace='text-primary')
            self.code = ui.code(content='', language="SQL")  
            with ui.stepper_navigation():
                ui.button("BACK", icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button("CREATE", icon="policy", on_click=self.run_creation_policy)
            return

    def run(self):
        with theme.frame('Create'):
            with self.stepper:
                self.step1()
                self.step2()
                self.step3()
                self.step4()
                self.step5()
