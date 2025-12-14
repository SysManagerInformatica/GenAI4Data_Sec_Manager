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
from theme import get_text
from wonderwords import RandomWord
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService
import json


config = Config()
r = RandomWord()

client = bigquery.Client(project=config.PROJECT_ID)


class RLSCreateforGroups:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.table_list = None
        self.field_list = None

        self.page_title = get_text('rls_groups_page_title')
        self.headers()

        self.stepper = ui.stepper().props("vertical").classes("w-full")

        self.step1_title = get_text('rls_users_step1_title')
        self.step2_title = get_text('rls_users_step2_title')
        self.step3_title = get_text('rls_users_step3_title')
        self.step4_title = get_text('rls_groups_step4_title')
        self.step5_title = "Step 5: Customize View Name (Optional)"
        self.step6_title = get_text('rls_users_step4_title')

        self.selected_dataset = None
        self.selected_table = None
        self.selected_field = None
        self.group_assignment = None
        self.randon_word = r.word(include_parts_of_speech=["nouns", "adjectives"], word_min_length=3, word_max_length=8)
        self.policy_name = None
        
        # View-related attributes
        self.view_name = None
        self.views_dataset = None

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
        ui.label(get_text('rls_groups_subtitle')).classes('text-primary text-center text-bold')

    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            # Filter out _views datasets
            return [dataset.dataset_id for dataset in datasets if not dataset.dataset_id.endswith('_views')]
        except GoogleAPIError as e:
            ui.notify(get_text('msg_error_fetch_datasets', error=str(e)), type="negative")
            return []
        except Exception as e:
            ui.notify(get_text('msg_error_unexpected', error=str(e)), type="negative")
            return []

    def get_tables_in_dataset(self):
        if not self.selected_dataset:
            ui.notify(get_text('msg_select_dataset_first'), type="warning")
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
            ui.notify(get_text('msg_dataset_not_found', dataset=self.selected_dataset), type="negative")
        except GoogleAPIError as e:
            ui.notify(get_text('msg_error_fetch_tables', error=str(e)), type="negative")
        except Exception as e:
            ui.notify(get_text('msg_error_unexpected', error=str(e)), type="negative")

    def get_fields_in_table(self):
        if not self.selected_table:
            ui.notify(get_text('msg_select_table_first'), type="warning")
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
            ui.notify(get_text('msg_table_not_found', table=self.selected_table), type="negative")
        except GoogleAPIError as e:
            ui.notify(get_text('msg_error_fetch_fields', error=str(e)), type="negative")
        except Exception as e:
            ui.notify(get_text('msg_error_unexpected', error=str(e)), type="negative")

    def ensure_views_dataset(self):
        """Create views dataset if it doesn't exist"""
        self.views_dataset = f"{self.selected_dataset}_views"
        
        try:
            client.get_dataset(self.views_dataset)
        except NotFound:
            # Create dataset
            dataset = bigquery.Dataset(f"{self.project_id}.{self.views_dataset}")
            dataset.location = "US"  # Adjust if needed
            dataset.description = f"RLS/CLS views for {self.selected_dataset}"
            client.create_dataset(dataset, timeout=30)
            ui.notify(f"✅ Created views dataset: {self.views_dataset}", type="positive", timeout=3000)

    def get_resume(self):
        if not self.selected_field:
            ui.notify(get_text('msg_select_field_first'), type="warning")
            return

        # view_name já foi definido em go_to_review()
        self.policy_name = f'rls_{self.view_name}'
        self.views_dataset = f"{self.selected_dataset}_views"
        
        # UPDATED: Resume shows VIEW creation
        self.resume.content = f""" 
            ###**{get_text('rls_users_review_title')}**<br>

            **🔐 RLS View Architecture (Group-based)**<br>
            **View Name**: {self.view_name}<br>
            **Views Dataset**: {self.views_dataset}<br>
            **Policy Name**: {self.policy_name}<br>
            <br>
            **{get_text('rls_users_review_project_id')}**: {self.project_id}<br>
            **{get_text('rls_users_review_dataset_id')}**: {self.selected_dataset}<br>
            **{get_text('rls_users_review_table_id')}**: {self.selected_table}<br>
            **{get_text('rls_users_review_field_id')}**: {self.selected_field[0]}<br>
            **{get_text('rls_groups_review_group_email')}**: {self.group_assignment}<br>
            <br>
            **ℹ️ How it works:**<br>
            • Original table ({self.selected_table}) remains locked 🔒<br>
            • View created in {self.views_dataset} with dynamic filter<br>
            • Only members of group {self.group_assignment} can access<br>
            • Filter values managed in policies_filters table<br>
            • Original table accessible ONLY to admins<br>
            <br>
            **Next steps:**<br>
            1. Create view → Assign values via "Assign Values to Group"<br>
            2. Optionally apply CLS (masking) via "Manage Protected Views"<br>
            <br>
            **{get_text('rls_users_review_code')}**:
        """

        # ✅ CORRECTED: SQL creates ONLY the VIEW (no ROW ACCESS POLICY)
        self.code.content = (
            f"-- Create RLS View with dynamic filter (group-based)\n"
            f"CREATE OR REPLACE VIEW `{self.project_id}.{self.views_dataset}.{self.view_name}` AS\n"
            f"SELECT *\n"
            f"FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`\n"
            f"WHERE {self.selected_field[0]} IN (\n"
            f"  SELECT CAST(filter_value AS {self.selected_field[1]})\n"
            f"  FROM `{config.FILTER_TABLE}`\n"
            f"  WHERE rls_type = 'group'\n"
            f"    AND policy_name = '{self.policy_name}'\n"
            f"    AND project_id = '{self.project_id}'\n"
            f"    AND dataset_id = '{self.selected_dataset}'\n"
            f"    AND table_id = '{self.selected_table}'\n"
            f"    AND field_id = '{self.selected_field[0]}'\n"
            f"    AND rls_group = '{self.group_assignment}'\n"
            f");\n\n"
            f"-- Note: View uses dynamic filtering for group members\n"
            f"-- Assign filter values via 'Assign Values to Group'\n"
            f"-- Access control: Only members of {self.group_assignment} can query this view"
        )
        self.stepper.next()

    def run_creation_policy(self):
        # ✅ Notificação inicial
        ui.notify("Creating RLS view...", type="info", spinner=True, timeout=2000)
        
        try:
            # Ensure views dataset exists
            self.ensure_views_dataset()
            
            # ✅ Notificação de progresso
            ui.notify("Executing SQL...", type="ongoing", timeout=2000)
            
            # ✅ CORRECTED: Create ONLY the view (no ROW ACCESS POLICY)
            query_job = client.query(self.code.content)
            query_job.result()
            
            ui.notify("Configuring view metadata...", type="ongoing", timeout=2000)
            
            # Update view description with metadata
            view_ref = client.dataset(self.views_dataset).table(self.view_name)
            view = client.get_table(view_ref)
            
            rls_metadata = {
                "type": "RLS_VIEW",
                "rls_type": "group",
                "base_dataset": self.selected_dataset,
                "base_table": self.selected_table,
                "filter_field": self.selected_field[0],
                "filter_field_type": self.selected_field[1],
                "filter_table": config.FILTER_TABLE,
                "group_email": self.group_assignment,
                "created_by": "CREATE_RLS_GROUPS",
                "policy_name": self.policy_name
            }
            
            view.description = (
                f"RLS view for group: {self.group_assignment}\n"
                f"Filters by {self.selected_field[0]}\n"
                f"Base table: {self.selected_dataset}.{self.selected_table}\n\n"
                f"RLS_METADATA:{json.dumps(rls_metadata)}"
            )
            client.update_table(view, ['description'])
            
            # Configure as Authorized View
            from google.cloud.bigquery import AccessEntry
            
            source_dataset_ref = client.dataset(self.selected_dataset)
            source_dataset = client.get_dataset(source_dataset_ref)
            
            access_entries = list(source_dataset.access_entries)
            
            authorized_view_entry = AccessEntry(
                role=None,
                entity_type='view',
                entity_id={
                    'projectId': self.project_id,
                    'datasetId': self.views_dataset,
                    'tableId': self.view_name
                }
            )
            
            # Check if already exists
            view_exists = False
            for entry in access_entries:
                if entry.entity_type == 'view' and isinstance(entry.entity_id, dict):
                    if (entry.entity_id.get('projectId') == self.project_id and
                        entry.entity_id.get('datasetId') == self.views_dataset and
                        entry.entity_id.get('tableId') == self.view_name):
                        view_exists = True
                        break
            
            if not view_exists:
                access_entries.append(authorized_view_entry)
            
            source_dataset.access_entries = access_entries
            client.update_dataset(source_dataset, ['access_entries'])
            
            # Insert into policy table (for backward compatibility)
            # ✅ FIXED: Use ORIGINAL dataset/table (not view dataset/name)
            query_insert_into_policy_table = f"""
                INSERT INTO `{config.POLICY_TABLE}` (policy_type, policy_name, project_id, dataset_id, table_name, field_id, group_email)
                VALUES
                ('group', '{self.policy_name}', '{self.project_id}', '{self.selected_dataset}', '{self.selected_table}', '{self.selected_field[0]}', '{self.group_assignment}')  
            """
            query_job = client.query(query_insert_into_policy_table)
            query_job.result()
            
            # Log success
            self.audit_service.log_action(
                action='CREATE_RLS_VIEW_GROUP',
                resource_type='RLS_VIEW',
                resource_name=f"{self.views_dataset}.{self.view_name}",
                status='SUCCESS',
                details={
                    'policy_type': 'group',
                    'view_name': self.view_name,
                    'views_dataset': self.views_dataset,
                    'base_dataset': self.selected_dataset,
                    'base_table': self.selected_table,
                    'filter_field': self.selected_field[0],
                    'filter_field_type': self.selected_field[1],
                    'group_email': self.group_assignment,
                    'policy_name': self.policy_name,
                    'architecture': 'RLS_VIEW_FILTER_ONLY'
                }
            )
            
            # Success message
            ui.notify("✅ RLS View created successfully!", type="positive", timeout=3000)
            
            # ✅ Sleep curto para garantir que UI processe
            import time
            time.sleep(0.5)
            
            # ✅ Dialog de sucesso - GARANTIDO
            with ui.dialog(value=True) as dialog, ui.card().classes('w-full max-w-2xl'):
                ui.label('✅ RLS View Created Successfully!').classes('text-h5 font-bold text-positive mb-4')
                
                with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                    ui.label('🔐 RLS View Configuration:').classes('font-bold mb-2')
                    ui.label(f'• View: {self.views_dataset}.{self.view_name}').classes('text-sm')
                    ui.label(f'• Filter field: {self.selected_field[0]}').classes('text-sm')
                    ui.label(f'• Authorized group: {self.group_assignment}').classes('text-sm')
                    ui.label(f'• Base table: {self.selected_dataset}.{self.selected_table} (locked 🔒)').classes('text-sm')
                    ui.label(f'• Policy: {self.policy_name}').classes('text-sm')
                
                with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                    ui.label('📋 Next Steps:').classes('font-bold mb-2')
                    ui.label('1. Go to "Assign Values to Group" to define filter values').classes('text-sm')
                    ui.label('2. Add the filter values for this group').classes('text-sm')
                    ui.label('3. Only group members will see the filtered data').classes('text-sm')
                    ui.label('4. Optionally apply CLS (masking) via "Manage Protected Views"').classes('text-sm')
                
                with ui.card().classes('w-full bg-purple-50 p-4 mb-4'):
                    ui.label('💡 Example Usage:').classes('font-bold mb-2')
                    ui.label(f'• Group: {self.group_assignment}').classes('text-sm')
                    ui.label(f'• Assign value: "Tecnologia da Informação"').classes('text-sm')
                    ui.label(f'• Group members query: SELECT * FROM {self.views_dataset}.{self.view_name}').classes('text-sm')
                    ui.label(f'• They see: ONLY rows where {self.selected_field[0]} = "Tecnologia da Informação"').classes('text-sm font-bold text-purple-700')
                
                with ui.row().classes('w-full justify-center'):  
                    ui.button(get_text('btn_close'), on_click=ui.navigate.reload)
            
            # Dialog já está aberto com value=True
            
        except GoogleAPIError as error:
            # Log failure
            self.audit_service.log_action(
                action='CREATE_RLS_VIEW_GROUP',
                resource_type='RLS_VIEW',
                resource_name=f"{self.views_dataset}.{self.view_name}" if self.view_name else 'unknown',
                status='FAILED',
                error_message=str(error),
                details={
                    'dataset': self.selected_dataset,
                    'table': self.selected_table,
                    'field': self.selected_field[0] if self.selected_field else 'unknown',
                    'group_email': self.group_assignment
                }
            )
            ui.notify(get_text('msg_error_create_policy', error=str(error)), type="negative", timeout=10000)
            
        except Exception as error:
            # Log exception
            self.audit_service.log_action(
                action='CREATE_RLS_VIEW_GROUP',
                resource_type='RLS_VIEW',
                resource_name=f"{self.views_dataset}.{self.view_name}" if self.view_name else 'unknown',
                status='FAILED',
                error_message=str(error),
                details={
                    'dataset': self.selected_dataset,
                    'table': self.selected_table,
                    'field': self.selected_field[0] if self.selected_field else 'unknown',
                    'group_email': self.group_assignment
                }
            )
            ui.notify(get_text('msg_error_unexpected', error=str(error)), type="negative", timeout=10000)

    def step1(self):
        with ui.step(self.step1_title):
            dataset_list = self.get_datasets()
            ui.select(dataset_list, label=get_text('rls_users_select_dataset'), on_change=self._update_selected_dataset)
            with ui.stepper_navigation():
                self.step1_next_button = ui.button(get_text('btn_next'), icon="arrow_forward_ios", on_click=self.get_tables_in_dataset)
                self.step1_next_button.set_visibility(False)

    def step2(self):
        with ui.step(self.step2_title):
            self.table_list = ui.select([], label=get_text('rls_users_select_table'), on_change=self._update_selected_table)
            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step2_next_button = ui.button(get_text('btn_next'), icon="arrow_forward_ios", on_click=self.get_fields_in_table)

                self.step2_next_button.set_visibility(False)
            return
        
    def step3(self):
        with ui.step(self.step3_title):
            self.field_list = ui.select([], label=get_text('rls_users_select_field'), on_change=self._update_selected_field)
            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step3_next_button = ui.button(get_text('btn_next'), icon="arrow_forward_ios", on_click=self.stepper.next)

                self.step3_next_button.set_visibility(False)
            return

    def step4(self):
        with ui.step(self.step4_title):
            self.group_assignment = ui.input(
                placeholder=get_text('rls_groups_enter_group_email'),
                on_change=self._update_group_assignment
            ).props("size=50")
            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)
                self.step4_next_button = ui.button(get_text('btn_next'), icon="arrow_forward_ios", on_click=self.stepper.next)

                self.step4_next_button.set_visibility(False)
            return
    
    def step5(self):
        """Step para customizar nome da view"""
        with ui.step(self.step5_title):
            ui.label("Customize the view name (optional)").classes('text-caption text-grey-7 mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("💡 Naming Tips").classes('font-bold mb-2')
                ui.label("• Leave empty for auto-generated name").classes('text-xs')
                ui.label("• Or enter custom name (e.g., vw_rls_finance_team)").classes('text-xs')
                ui.label("• Only letters, numbers, and underscores").classes('text-xs')
                ui.label("• Must start with a letter").classes('text-xs')
            
            self.custom_view_name_input = ui.input(
                label="Custom View Name (leave empty for auto)",
                placeholder="vw_rls_my_custom_name"
            ).classes('w-full').on('input', self.validate_custom_name)
            
            self.view_name_validation_label = ui.label('').classes('text-xs mt-2')
            
            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button(get_text('btn_next'), icon="arrow_forward_ios", on_click=self.go_to_review)

            return
    
    def validate_custom_name(self, e):
        """Valida nome customizado"""
        import re
        name = e.value.strip()
        
        if not name:
            self.view_name_validation_label.text = '✅ Will use auto-generated name'
            self.view_name_validation_label.classes(replace='text-xs mt-2 text-green-600')
            return
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            self.view_name_validation_label.text = '❌ Invalid: Must start with letter, only letters/numbers/underscores'
            self.view_name_validation_label.classes(replace='text-xs mt-2 text-red-600')
        else:
            self.view_name_validation_label.text = f'✅ Valid: Will create {self.selected_dataset}_views.{name}'
            self.view_name_validation_label.classes(replace='text-xs mt-2 text-green-600')
    
    def go_to_review(self):
        """Ir para review com nome customizado ou auto"""
        custom_name = self.custom_view_name_input.value.strip() if hasattr(self, 'custom_view_name_input') else ''
        
        if custom_name:
            import re
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', custom_name):
                ui.notify("Invalid view name. Please fix it before proceeding.", type="warning")
                return
            self.view_name = custom_name
        else:
            # Auto-generate
            self.view_name = f'vw_{self.selected_table}_{self.selected_field[0]}_{self.randon_word}'
        
        self.get_resume()
        
    def step6(self):
        with ui.step(self.step5_title):
            self.resume = ui.markdown().classes(replace='text-primary')
            self.code = ui.code(content='', language="SQL")  
            with ui.stepper_navigation():
                ui.button(get_text('btn_back'), icon="arrow_back_ios", on_click=self.stepper.previous)
                ui.button(get_text('btn_create'), icon="policy", on_click=self.run_creation_policy)
            return

    def run(self):
        with theme.frame(get_text('rls_groups_frame_title')):
            with self.stepper:
                self.step1()
                self.step2()
                self.step3()
                self.step4()
                self.step5()
                self.step6()
