import theme
from config import Config
from nicegui import ui, run
from google.cloud import resourcemanager_v3
from google.iam.v1 import policy_pb2
from services.audit_service import AuditService
import traceback
from datetime import datetime

config = Config()


class ProjectIAMManager:
    
    PROJECT_ROLES = {
        'roles/owner': {
            'label': '👑 Owner',
            'description': 'Full control of all resources',
            'color': 'bg-red-100 text-red-700',
            'level': 'danger'
        },
        'roles/editor': {
            'label': '✍️ Editor',
            'description': 'Edit all resources',
            'color': 'bg-orange-100 text-orange-700',
            'level': 'warning'
        },
        'roles/viewer': {
            'label': '👁️ Viewer',
            'description': 'View all resources',
            'color': 'bg-blue-100 text-blue-700',
            'level': 'safe'
        },
        'roles/bigquery.admin': {
            'label': '🔧 BigQuery Admin',
            'description': 'Full BigQuery access',
            'color': 'bg-purple-100 text-purple-700',
            'level': 'warning'
        },
        'roles/bigquery.dataOwner': {
            'label': '📊 BigQuery Data Owner',
            'description': 'Own BigQuery data',
            'color': 'bg-yellow-100 text-yellow-700',
            'level': 'warning'
        },
        'roles/bigquery.dataEditor': {
            'label': '✏️ BigQuery Data Editor',
            'description': 'Edit BigQuery data',
            'color': 'bg-green-100 text-green-700',
            'level': 'safe'
        },
        'roles/bigquery.dataViewer': {
            'label': '📖 BigQuery Data Viewer',
            'description': 'View BigQuery data',
            'color': 'bg-teal-100 text-teal-700',
            'level': 'safe'
        },
        'roles/bigquery.user': {
            'label': '👤 BigQuery User',
            'description': 'Run queries',
            'color': 'bg-cyan-100 text-cyan-700',
            'level': 'safe'
        },
        'roles/bigquery.jobUser': {
            'label': '⚙️ BigQuery Job User',
            'description': 'Run jobs',
            'color': 'bg-indigo-100 text-indigo-700',
            'level': 'safe'
        },
        'roles/datacatalog.categoryAdmin': {
            'label': '📁 Data Catalog Admin',
            'description': 'Manage Data Catalog',
            'color': 'bg-pink-100 text-pink-700',
            'level': 'warning'
        }
    }

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Project IAM Manager"
        
        self.users = []
        self.users_grid = None
        self.selected_user = None
        
        # Dialog para gerenciar roles do usuário
        self.create_manage_dialog()
        
        # Dialog para adicionar novo usuário
        self.create_add_user_dialog()
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Project IAM Manager').classes('text-primary text-center text-bold')
    
    def create_manage_dialog(self):
        """Cria dialog para gerenciar roles de um usuário"""
        with ui.dialog() as self.manage_dialog, ui.card().classes('w-full max-w-5xl'):
            self.dialog_title = ui.label('').classes('text-h5 font-bold mb-4')
            
            # User info card
            self.user_info_container = ui.column().classes('w-full mb-4')
            
            # Current Roles
            ui.label('Current Roles:').classes('text-sm font-bold mb-2')
            
            with ui.scroll_area().classes('w-full h-64 border rounded p-2 mb-4'):
                self.roles_container = ui.column().classes('w-full')
            
            # Add New Role Section
            ui.separator()
            
            with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                ui.label('➕ Add New Role').classes('font-bold text-lg mb-3')
                
                with ui.row().classes('w-full gap-2 items-end'):
                    self.new_role = ui.select(
                        options=list(self.PROJECT_ROLES.keys()),
                        value='roles/bigquery.dataViewer',
                        label='Select Role'
                    ).classes('flex-1').props('emit-value map-options')
                    
                    # Mostrar descrição da role selecionada
                    self.role_description = ui.label('').classes('text-xs text-gray-600 flex-1')
                    
                    ui.button(
                        'ADD ROLE',
                        icon='add',
                        on_click=self.add_role_to_user
                    ).props('color=positive size=md')
                
                # Atualizar descrição quando role muda
                self.new_role.on_value_change(lambda e: self.update_role_description())
                self.update_role_description()
            
            # Botões
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CLOSE', on_click=self.manage_dialog.close).props('flat')
                ui.button('REFRESH', icon='refresh', on_click=self.refresh_user_roles).props('color=primary')
    
    def create_add_user_dialog(self):
        """Cria dialog para adicionar novo usuário"""
        with ui.dialog() as self.add_user_dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('➕ Add New User to Project').classes('text-h5 font-bold mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('ℹ️ Important:').classes('font-bold text-sm mb-2')
                ui.label('• This will grant project-level permissions').classes('text-xs')
                ui.label('• User will have access according to the role assigned').classes('text-xs')
                ui.label('• You can add multiple roles to the same user later').classes('text-xs')
            
            self.add_user_email = ui.input(
                placeholder='user@company.com',
                label='Email Address'
            ).classes('w-full mb-4')
            
            self.add_user_role = ui.select(
                options=list(self.PROJECT_ROLES.keys()),
                value='roles/bigquery.dataViewer',
                label='Initial Role'
            ).classes('w-full mb-2').props('emit-value map-options')
            
            self.add_user_role_desc = ui.label('').classes('text-xs text-gray-600 mb-4')
            self.add_user_role.on_value_change(lambda e: self.update_add_user_role_description())
            self.update_add_user_role_description()
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=self.add_user_dialog.close).props('flat')
                ui.button('ADD USER', icon='person_add', on_click=self.add_new_user).props('color=positive')
    
    def update_role_description(self):
        """Atualiza descrição da role selecionada"""
        role = self.new_role.value
        if role in self.PROJECT_ROLES:
            role_info = self.PROJECT_ROLES[role]
            self.role_description.set_text(f"{role_info['label']}: {role_info['description']}")
    
    def update_add_user_role_description(self):
        """Atualiza descrição da role no dialog de adicionar usuário"""
        role = self.add_user_role.value
        if role in self.PROJECT_ROLES:
            role_info = self.PROJECT_ROLES[role]
            self.add_user_role_desc.set_text(f"{role_info['label']}: {role_info['description']}")
    
    async def get_project_iam_policy(self):
        """Obtém política IAM do projeto"""
        try:
            client_rm = resourcemanager_v3.ProjectsClient()
            request = resourcemanager_v3.GetIamPolicyRequest(
                resource=f"projects/{self.project_id}"
            )
            
            policy = await run.io_bound(client_rm.get_iam_policy, request=request)
            return policy
            
        except Exception as e:
            print(f"[ERROR] get_project_iam_policy: {e}")
            traceback.print_exc()
            return None
    
    async def get_project_users(self):
        """Lista usuários com permissões no projeto"""
        try:
            policy = await self.get_project_iam_policy()
            if not policy:
                return []
            
            users = {}
            for binding in policy.bindings:
                role = binding.role
                for member in binding.members:
                    if member.startswith('user:'):
                        email = member.replace('user:', '')
                        if email not in users:
                            users[email] = []
                        users[email].append(role)
            
            user_list = []
            for email, roles in users.items():
                # Classificar nível de risco
                risk_level = 'safe'
                for role in roles:
                    if role in self.PROJECT_ROLES:
                        level = self.PROJECT_ROLES[role]['level']
                        if level == 'danger':
                            risk_level = 'danger'
                            break
                        elif level == 'warning' and risk_level == 'safe':
                            risk_level = 'warning'
                
                user_list.append({
                    'email': email,
                    'roles_count': len(roles),
                    'roles': ', '.join([r.split('/')[-1] for r in roles[:3]]) + ('...' if len(roles) > 3 else ''),
                    'risk_level': risk_level,
                    'risk_icon': '🔴' if risk_level == 'danger' else '🟡' if risk_level == 'warning' else '🟢',
                    'all_roles': roles  # Para uso interno
                })
            
            return user_list
            
        except Exception as e:
            print(f"[ERROR] get_project_users: {e}")
            traceback.print_exc()
            return []
    
    def load_users(self):
        """Carrega usuários no grid"""
        n = ui.notification('Loading users...', spinner=True, timeout=None)
        
        try:
            import asyncio
            self.users = asyncio.run(self.get_project_users())
            
            if self.users_grid:
                self.users_grid.options['rowData'] = self.users
                self.users_grid.update()
            
            n.dismiss()
            ui.notify(f"✅ Loaded {len(self.users)} users", type="positive")
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    async def manage_user_roles(self):
        """Abre dialog para gerenciar roles de um usuário"""
        rows = await self.users_grid.get_selected_rows()
        if not rows:
            ui.notify('No user selected', type="warning")
            return
        
        user_info = rows[0]
        self.selected_user = user_info['email']
        
        n = ui.notification('Loading user roles...', spinner=True, timeout=None)
        
        try:
            # Atualizar título
            self.dialog_title.set_text(f'Manage Roles: {self.selected_user}')
            
            # Atualizar info card
            await self.update_user_info_card(user_info)
            
            # Carregar roles
            await self.load_user_roles()
            
            n.dismiss()
            self.manage_dialog.open()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    async def update_user_info_card(self, user_info):
        """Atualiza card de informações do usuário"""
        self.user_info_container.clear()
        
        with self.user_info_container:
            risk_color = 'red' if user_info['risk_level'] == 'danger' else 'orange' if user_info['risk_level'] == 'warning' else 'green'
            
            with ui.card().classes(f'w-full bg-{risk_color}-50 p-4'):
                ui.label(f"{user_info['risk_icon']} User Information:").classes('font-bold mb-2')
                ui.label(f"  • Email: {user_info['email']}").classes('text-sm')
                ui.label(f"  • Total Roles: {user_info['roles_count']}").classes('text-sm')
                ui.label(f"  • Risk Level: {user_info['risk_level'].upper()}").classes('text-sm font-bold')
    
    async def load_user_roles(self):
        """Carrega roles do usuário"""
        self.roles_container.clear()
        
        try:
            policy = await self.get_project_iam_policy()
            if not policy:
                with self.roles_container:
                    ui.label('Error loading roles').classes('text-red-600')
                return
            
            user_roles = []
            for binding in policy.bindings:
                if f"user:{self.selected_user}" in binding.members:
                    user_roles.append(binding.role)
            
            if not user_roles:
                with self.roles_container:
                    with ui.card().classes('w-full bg-gray-50 p-4'):
                        ui.icon('lock_open', size='48px', color='gray').classes('mx-auto mb-2')
                        ui.label('No roles assigned').classes('text-gray-500 text-center')
                return
            
            with self.roles_container:
                for role in user_roles:
                    role_info = self.PROJECT_ROLES.get(role, {
                        'label': role,
                        'description': 'Custom role',
                        'color': 'bg-gray-100 text-gray-700',
                        'level': 'safe'
                    })
                    
                    with ui.card().classes('w-full p-3 mb-2 bg-white border-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('flex-1'):
                                ui.label(role_info['label']).classes('font-bold text-sm mb-1')
                                ui.label(role_info['description']).classes('text-xs text-gray-600 mb-1')
                                ui.label(role).classes('text-xs text-gray-400 font-mono')
                            
                            def make_remove(user_role):
                                async def remove():
                                    await self.remove_role_from_user(user_role)
                                return remove
                            
                            ui.button(
                                'REMOVE',
                                icon='delete',
                                on_click=make_remove(role)
                            ).props('flat dense color=negative')
        
        except Exception as e:
            with self.roles_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            traceback.print_exc()
    
    async def add_role_to_user(self):
        """Adiciona role ao usuário"""
        role = self.new_role.value
        
        if not role:
            ui.notify('Please select a role', type="warning")
            return
        
        n = ui.notification(f'Adding {role}...', spinner=True, timeout=None)
        
        try:
            client_rm = resourcemanager_v3.ProjectsClient()
            resource = f"projects/{self.project_id}"
            
            # Get current policy
            request = resourcemanager_v3.GetIamPolicyRequest(resource=resource)
            policy = await run.io_bound(client_rm.get_iam_policy, request=request)
            
            # Check if already has role
            member = f"user:{self.selected_user}"
            for binding in policy.bindings:
                if binding.role == role and member in binding.members:
                    n.dismiss()
                    ui.notify(f'User already has this role', type="warning")
                    return
            
            # Add member to role
            binding_found = False
            for binding in policy.bindings:
                if binding.role == role:
                    binding.members.append(member)
                    binding_found = True
                    break
            
            if not binding_found:
                # Create new binding
                new_binding = policy_pb2.Binding(
                    role=role,
                    members=[member]
                )
                policy.bindings.append(new_binding)
            
            # Set updated policy
            set_request = resourcemanager_v3.SetIamPolicyRequest(
                resource=resource,
                policy=policy
            )
            await run.io_bound(client_rm.set_iam_policy, request=set_request)
            
            # Audit log
            self.audit_service.log_action(
                action='ADD_PROJECT_ROLE',
                resource_type='PROJECT_IAM',
                resource_name=self.project_id,
                status='SUCCESS',
                details={
                    'user': self.selected_user,
                    'role': role
                }
            )
            
            n.dismiss()
            ui.notify(f'✅ Role {role} added', type="positive")
            
            # Refresh
            await self.load_user_roles()
            self.load_users()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def remove_role_from_user(self, role):
        """Remove role do usuário"""
        # Confirmar remoção
        with ui.dialog() as confirm_dialog, ui.card().classes('w-full max-w-md'):
            ui.label('⚠️ Confirm Removal').classes('text-h6 font-bold text-orange-600 mb-4')
            
            role_info = self.PROJECT_ROLES.get(role, {'label': role, 'description': ''})
            
            with ui.card().classes('w-full bg-orange-50 p-3 mb-4'):
                ui.label(f'User: {self.selected_user}').classes('text-sm font-bold')
                ui.label(f'Role: {role_info["label"]}').classes('text-sm')
                ui.label(f'({role})').classes('text-xs text-gray-600')
            
            ui.label('This will remove this role from the user at PROJECT level.').classes('text-sm mb-2')
            ui.label('Are you sure?').classes('text-sm font-bold')
            
            async def execute_removal():
                confirm_dialog.close()
                await self.execute_remove_role(role)
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=confirm_dialog.close).props('flat')
                ui.button('REMOVE', on_click=execute_removal).props('color=negative')
        
        confirm_dialog.open()
    
    async def execute_remove_role(self, role):
        """Executa remoção da role"""
        n = ui.notification(f'Removing {role}...', spinner=True, timeout=None)
        
        try:
            client_rm = resourcemanager_v3.ProjectsClient()
            resource = f"projects/{self.project_id}"
            
            # Get current policy
            request = resourcemanager_v3.GetIamPolicyRequest(resource=resource)
            policy = await run.io_bound(client_rm.get_iam_policy, request=request)
            
            # Remove member from role
            member = f"user:{self.selected_user}"
            for binding in policy.bindings:
                if binding.role == role and member in binding.members:
                    binding.members.remove(member)
                    break
            
            # Set updated policy
            set_request = resourcemanager_v3.SetIamPolicyRequest(
                resource=resource,
                policy=policy
            )
            await run.io_bound(client_rm.set_iam_policy, request=set_request)
            
            # Audit log
            self.audit_service.log_action(
                action='REMOVE_PROJECT_ROLE',
                resource_type='PROJECT_IAM',
                resource_name=self.project_id,
                status='SUCCESS',
                details={
                    'user': self.selected_user,
                    'role': role
                }
            )
            
            n.dismiss()
            ui.notify(f'✅ Role removed successfully', type="positive")
            
            # Refresh
            await self.load_user_roles()
            self.load_users()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def add_new_user(self):
        """Adiciona novo usuário ao projeto"""
        email = self.add_user_email.value.strip()
        role = self.add_user_role.value
        
        if not email or '@' not in email:
            ui.notify('Please enter a valid email address', type="warning")
            return
        
        n = ui.notification(f'Adding {email}...', spinner=True, timeout=None)
        
        try:
            client_rm = resourcemanager_v3.ProjectsClient()
            resource = f"projects/{self.project_id}"
            
            # Get current policy
            request = resourcemanager_v3.GetIamPolicyRequest(resource=resource)
            policy = await run.io_bound(client_rm.get_iam_policy, request=request)
            
            # Add member to role
            member = f"user:{email}"
            binding_found = False
            
            for binding in policy.bindings:
                if binding.role == role:
                    if member in binding.members:
                        n.dismiss()
                        ui.notify(f'User already has this role', type="warning")
                        return
                    binding.members.append(member)
                    binding_found = True
                    break
            
            if not binding_found:
                # Create new binding
                new_binding = policy_pb2.Binding(
                    role=role,
                    members=[member]
                )
                policy.bindings.append(new_binding)
            
            # Set updated policy
            set_request = resourcemanager_v3.SetIamPolicyRequest(
                resource=resource,
                policy=policy
            )
            await run.io_bound(client_rm.set_iam_policy, request=set_request)
            
            # Audit log
            self.audit_service.log_action(
                action='ADD_USER_TO_PROJECT',
                resource_type='PROJECT_IAM',
                resource_name=self.project_id,
                status='SUCCESS',
                details={
                    'user': email,
                    'role': role
                }
            )
            
            n.dismiss()
            ui.notify(f'✅ {email} added with {role}', type="positive")
            
            # Limpar e fechar
            self.add_user_email.value = ''
            self.add_user_dialog.close()
            
            # Refresh
            self.load_users()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def refresh_user_roles(self):
        """Refresh roles do usuário"""
        await self.load_user_roles()
        ui.notify('Refreshed', type="positive")
    
    def render_ui(self):
        with theme.frame('Project IAM Manager'):
            with ui.card().classes('w-full'):
                ui.label("Project IAM Manager").classes('text-h5 font-bold mb-4')
                
                with ui.card().classes('w-full bg-orange-50 p-3 mb-4'):
                    ui.label('⚠️ Project-Level Permissions:').classes('font-bold text-sm mb-2')
                    ui.label('• These permissions apply to the ENTIRE project').classes('text-xs')
                    ui.label('• Users with Owner/Editor roles bypass all dataset restrictions').classes('text-xs')
                    ui.label('• Use dataset-level permissions for better security control').classes('text-xs font-bold')
                
                with ui.row().classes('w-full gap-2 mb-4'):
                    ui.button('REFRESH', icon='refresh', on_click=self.load_users).props('color=primary')
                    ui.button('ADD NEW USER', icon='person_add', on_click=self.add_user_dialog.open).props('color=positive')
                
                ui.label(f"Project: {self.project_id}").classes('text-h6 font-bold mb-2')
                
                self.users_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'email', 'headerName': 'User Email', 'checkboxSelection': True, 'filter': True, 'minWidth': 350},
                        {'field': 'roles_count', 'headerName': 'Roles Count', 'filter': True, 'minWidth': 120},
                        {'field': 'roles', 'headerName': 'Roles Preview', 'filter': True, 'minWidth': 300},
                        {'field': 'risk_icon', 'headerName': 'Risk', 'filter': True, 'minWidth': 80},
                    ],
                    'rowData': [],
                    'rowSelection': 'single',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("MANAGE ROLES", icon="settings", on_click=self.manage_user_roles).props('color=primary')
                
                # Carregar usuários ao iniciar
                self.load_users()
    
    def run(self):
        pass
