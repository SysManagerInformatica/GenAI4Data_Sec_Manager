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
from google.cloud import datacatalog_v1
from google.iam.v1 import iam_policy_pb2, policy_pb2
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService

config = Config()


class CLSPermissionsManager:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.datacatalog_client = datacatalog_v1.PolicyTagManagerClient()
        
        self.page_title = "Policy Tag Permissions Manager"
        
        self.selected_taxonomy = None
        self.selected_policy_tag = None
        self.permissions_grid = None
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Policy Tag Permissions Manager').classes('text-primary text-center text-bold')
    
    def list_taxonomies(self):
        """Lista todas as taxonomias do projeto"""
        try:
            parent = f"projects/{self.project_id}/locations/us-central1"
            request = datacatalog_v1.ListTaxonomiesRequest(parent=parent)
            
            taxonomies = []
            for taxonomy in self.datacatalog_client.list_taxonomies(request=request):
                taxonomies.append({
                    'name': taxonomy.name,
                    'display_name': taxonomy.display_name
                })
            return taxonomies
        except Exception as e:
            ui.notify(f"Error listing taxonomies: {e}", type="negative")
            return []
    
    def list_policy_tags(self, taxonomy_name):
        """Lista policy tags de uma taxonomia"""
        try:
            request = datacatalog_v1.ListPolicyTagsRequest(parent=taxonomy_name)
            
            tags = []
            for tag in self.datacatalog_client.list_policy_tags(request=request):
                tags.append({
                    'name': tag.name,
                    'display_name': tag.display_name
                })
            return tags
        except Exception as e:
            ui.notify(f"Error listing policy tags: {e}", type="negative")
            return []
    
    def get_current_permissions(self, policy_tag_name):
        """Lista permissões atuais"""
        try:
            request = iam_policy_pb2.GetIamPolicyRequest(resource=policy_tag_name)
            policy = self.datacatalog_client.get_iam_policy(request=request)
            
            permissions = []
            for binding in policy.bindings:
                for member in binding.members:
                    # Extrair email de "user:email@example.com"
                    email = member.split(':')[1] if ':' in member else member
                    permissions.append({
                        'member': member,
                        'email': email,
                        'role': binding.role,
                        'role_display': self.format_role_name(binding.role)
                    })
            return permissions
        except Exception as e:
            ui.notify(f"Error getting permissions: {e}", type="negative")
            return []
    
    def format_role_name(self, role):
        """Formata nome da role para exibição"""
        role_map = {
            'roles/datacatalog.categoryFineGrainedReader': 'Fine-Grained Reader (Full Access)',
            'roles/datacatalog.categoryMaskedReader': 'Masked Reader (Returns NULL)',  # ← ATUALIZADO
            'roles/datacatalog.categoryAdmin': 'Category Admin',
            'roles/owner': 'Owner',
            'roles/viewer': 'Viewer'
        }
        return role_map.get(role, role)
    
    def grant_permission(self, user_email, role):
        """Adiciona permissão"""
        if not self.selected_policy_tag:
            ui.notify("Please select a policy tag first", type="warning")
            return
        
        try:
            # Get current policy
            request = iam_policy_pb2.GetIamPolicyRequest(
                resource=self.selected_policy_tag
            )
            policy = self.datacatalog_client.get_iam_policy(request=request)
            
            # Add new member
            member = f"user:{user_email}"
            role_exists = False
            
            for binding in policy.bindings:
                if binding.role == role:
                    if member not in binding.members:
                        binding.members.append(member)
                    role_exists = True
                    break
            
            if not role_exists:
                new_binding = policy_pb2.Binding(
                    role=role,
                    members=[member]
                )
                policy.bindings.append(new_binding)
            
            # Set updated policy
            set_request = iam_policy_pb2.SetIamPolicyRequest(
                resource=self.selected_policy_tag,
                policy=policy
            )
            self.datacatalog_client.set_iam_policy(request=set_request)
            
            # Audit log
            self.audit_service.log_action(
                action='GRANT_POLICY_TAG_PERMISSION',
                resource_type='POLICY_TAG_IAM',
                resource_name=self.selected_policy_tag,
                status='SUCCESS',
                details={
                    'user_email': user_email,
                    'role': role,
                    'policy_tag': self.selected_policy_tag
                }
            )
            
            ui.notify(f"Permission granted to {user_email}", type="positive")
            self.refresh_permissions_grid()
            
        except Exception as e:
            ui.notify(f"Error granting permission: {e}", type="negative")
    
    def revoke_permission(self, user_email, role):
        """Remove permissão"""
        try:
            # Get current policy
            request = iam_policy_pb2.GetIamPolicyRequest(
                resource=self.selected_policy_tag
            )
            policy = self.datacatalog_client.get_iam_policy(request=request)
            
            # Remove member
            member = f"user:{user_email}"
            
            for binding in policy.bindings:
                if binding.role == role:
                    if member in binding.members:
                        binding.members.remove(member)
            
            # Set updated policy
            set_request = iam_policy_pb2.SetIamPolicyRequest(
                resource=self.selected_policy_tag,
                policy=policy
            )
            self.datacatalog_client.set_iam_policy(request=set_request)
            
            # Audit log
            self.audit_service.log_action(
                action='REVOKE_POLICY_TAG_PERMISSION',
                resource_type='POLICY_TAG_IAM',
                resource_name=self.selected_policy_tag,
                status='SUCCESS',
                details={
                    'user_email': user_email,
                    'role': role,
                    'policy_tag': self.selected_policy_tag
                }
            )
            
            ui.notify(f"Permission revoked from {user_email}", type="positive")
            self.refresh_permissions_grid()
            
        except Exception as e:
            ui.notify(f"Error revoking permission: {e}", type="negative")
    
    def refresh_permissions_grid(self):
        """Atualiza grid de permissões"""
        if self.permissions_grid and self.selected_policy_tag:
            permissions = self.get_current_permissions(self.selected_policy_tag)
            self.permissions_grid.options['rowData'] = permissions
            self.permissions_grid.update()
    
    async def delete_selected_permissions(self):
        """Deleta permissões selecionadas"""
        rows = await self.permissions_grid.get_selected_rows()
        if not rows:
            ui.notify('No permissions selected', type="warning")
            return
        
        for row in rows:
            self.revoke_permission(row['email'], row['role'])
    
    def render_ui(self):
        with theme.frame('Policy Tag Permissions'):
            with ui.card().classes('w-full'):
                ui.label("Manage Policy Tag Permissions").classes('text-h5 font-bold mb-4')
                
                # Seletores
                with ui.row().classes('w-full gap-4 mb-4'):
                    taxonomies = self.list_taxonomies()
                    taxonomy_options = {t['display_name']: t['name'] for t in taxonomies}
                    
                    ui.select(
                        options=list(taxonomy_options.keys()),
                        label="Select Taxonomy",
                        on_change=lambda e: self.on_taxonomy_change(taxonomy_options.get(e.value))
                    ).classes('flex-1')
                    
                    self.policy_tag_select = ui.select(
                        options=[],
                        label="Select Policy Tag",
                        on_change=lambda e: self.on_policy_tag_change(e.value)
                    ).classes('flex-1')
                
                # Grid de permissões atuais
                ui.separator()
                ui.label("Current Permissions").classes('text-h6 font-bold mt-4 mb-2')
                
                self.permissions_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'email', 'headerName': 'User Email', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 300},
                        {'field': 'role_display', 'headerName': 'Role', 'filter': 'agTextColumnFilter', 'minWidth': 250},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                }).classes('w-full max-h-96 ag-theme-quartz')
                
                with ui.row().classes('mt-2'):
                    ui.button("REVOKE SELECTED", icon="delete", on_click=self.delete_selected_permissions).props('color=negative')
                    ui.button("REFRESH", icon="refresh", on_click=self.refresh_permissions_grid).props('flat')
                
                # Adicionar nova permissão
                ui.separator()
                ui.label("Grant New Permission").classes('text-h6 font-bold mt-4 mb-2')
                
                with ui.card().classes('w-full p-4'):
                    with ui.column().classes('w-full gap-4'):
                        with ui.row().classes('w-full gap-4 items-end'):
                            self.email_input = ui.input(
                                label="User Email",
                                placeholder="user@example.com"
                            ).classes('flex-1')
                            
                            self.role_select = ui.select(
                                options=[
                                    'roles/datacatalog.categoryFineGrainedReader',
                                    'roles/datacatalog.categoryMaskedReader',  # ← ADICIONADO
                                    'roles/datacatalog.categoryAdmin'
                                ],
                                label="Role",
                                value='roles/datacatalog.categoryFineGrainedReader'
                            ).classes('flex-1')
                            
                            ui.button(
                                "GRANT ACCESS",
                                icon="lock_open",
                                on_click=lambda: self.grant_permission(
                                    self.email_input.value,
                                    self.role_select.value
                                )
                            ).props('color=primary')
                        
                        # ← ADICIONADO: Info box sobre roles
                        with ui.card().classes('w-full bg-blue-50 p-3'):
                            ui.label('ℹ️ Role Information:').classes('text-sm font-bold mb-2')
                            with ui.column().classes('gap-1'):
                                ui.label('• Fine-Grained Reader: User sees real data (e.g., 123.456.789-10)').classes('text-xs')
                                ui.label('• Masked Reader: User sees NULL instead of sensitive data').classes('text-xs text-orange-600')
                                ui.label('• Category Admin: User can manage policy tags and taxonomies').classes('text-xs')
    
    def on_taxonomy_change(self, taxonomy_name):
        """Quando seleciona uma taxonomia"""
        self.selected_taxonomy = taxonomy_name
        
        # Carregar policy tags
        tags = self.list_policy_tags(taxonomy_name)
        tag_options = {t['display_name']: t['name'] for t in tags}
        
        self.policy_tag_select.options = list(tag_options.keys())
        self.policy_tag_select.value = None
        self.policy_tag_select.update()
    
    def on_policy_tag_change(self, policy_tag_display_name):
        """Quando seleciona uma policy tag"""
        # Encontrar o nome completo da tag
        tags = self.list_policy_tags(self.selected_taxonomy)
        for tag in tags:
            if tag['display_name'] == policy_tag_display_name:
                self.selected_policy_tag = tag['name']
                break
        
        # Carregar permissões
        self.refresh_permissions_grid()
    
    def run(self):
        pass  # Já renderizado no __init__
