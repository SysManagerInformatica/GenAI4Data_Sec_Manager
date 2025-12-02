import theme
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from google.cloud.bigquery import AccessEntry
from services.audit_service import AuditService
import traceback
from datetime import datetime

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DatasetIAMManager:
    
    ROLES = {
        'READER': {
            'label': '📖 Reader',
            'description': 'Can read data',
            'color': 'bg-blue-100 text-blue-700'
        },
        'WRITER': {
            'label': '✍️ Writer',
            'description': 'Can read and write data',
            'color': 'bg-green-100 text-green-700'
        },
        'OWNER': {
            'label': '👑 Owner',
            'description': 'Full control',
            'color': 'bg-red-100 text-red-700'
        }
    }

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Dataset IAM Manager"
        
        self.datasets = []
        self.datasets_grid = None
        self.selected_dataset = None
        
        # Dialog para gerenciar permissões
        self.create_manage_dialog()
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Dataset IAM Manager').classes('text-primary text-center text-bold')
    
    def create_manage_dialog(self):
        """Cria dialog para gerenciar permissões"""
        with ui.dialog() as self.manage_dialog, ui.card().classes('w-full max-w-6xl'):
            self.dialog_title = ui.label('').classes('text-h5 font-bold mb-4')
            
            # Info card
            self.info_card_container = ui.column().classes('w-full mb-4')
            
            # Tabs
            with ui.tabs().classes('w-full') as tabs:
                tab_users = ui.tab('Users & Permissions', icon='people')
                tab_security = ui.tab('Security Check', icon='security')
            
            with ui.tab_panels(tabs, value=tab_users).classes('w-full'):
                # TAB 1: Users & Permissions
                with ui.tab_panel(tab_users):
                    ui.label('Current Permissions:').classes('text-sm font-bold mb-2')
                    
                    # Container para lista de usuários
                    with ui.scroll_area().classes('w-full h-96 border rounded p-2 mb-4'):
                        self.users_container = ui.column().classes('w-full')
                    
                    # Adicionar novo usuário
                    ui.separator()
                    ui.label('Add New User:').classes('text-sm font-bold mt-4 mb-2')
                    
                    with ui.row().classes('w-full gap-2'):
                        self.new_user_email = ui.input(
                            placeholder='user@company.com',
                            label='Email'
                        ).classes('flex-1')
                        
                        self.new_user_role = ui.select(
                            options=list(self.ROLES.keys()),
                            value='READER',
                            label='Role'
                        ).classes('w-48')
                        
                        ui.button(
                            'ADD USER',
                            icon='person_add',
                            on_click=self.add_user
                        ).props('color=positive')
                
                # TAB 2: Security Check
                with ui.tab_panel(tab_security):
                    self.security_check_container = ui.column().classes('w-full')
            
            # Botões
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CLOSE', on_click=self.manage_dialog.close).props('flat')
                ui.button('REFRESH', icon='refresh', on_click=self.refresh_permissions).props('color=primary')
    
    def get_datasets(self):
        """Lista todos os datasets"""
        try:
            datasets_list = client.list_datasets()
            datasets = []
            
            for ds in datasets_list:
                dataset_id = ds.dataset_id
                
                # Verificar se é dataset de views
                is_views_dataset = dataset_id.endswith('_views')
                
                # Obter detalhes do dataset
                dataset_ref = client.dataset(dataset_id)
                dataset_obj = client.get_dataset(dataset_ref)
                
                # Contar usuários
                user_count = 0
                owner_count = 0
                authorized_views_count = 0
                
                for entry in dataset_obj.access_entries:
                    if entry.entity_type == 'userByEmail':
                        user_count += 1
                        if entry.role == 'OWNER':
                            owner_count += 1
                    elif entry.entity_type == 'view':
                        authorized_views_count += 1
                
                # Status de segurança
                if is_views_dataset:
                    security_status = '✅ Views Dataset'
                elif authorized_views_count > 0:
                    security_status = '🔐 Has Authorized Views'
                elif owner_count > 0:
                    security_status = '⚠️ Has Owners'
                else:
                    security_status = '✅ Secure'
                
                datasets.append({
                    'dataset_id': dataset_id,
                    'type': 'Views' if is_views_dataset else 'Source',
                    'users': user_count,
                    'owners': owner_count,
                    'authorized_views': authorized_views_count,
                    'security_status': security_status,
                    'created': dataset_obj.created.strftime('%Y-%m-%d %H:%M') if dataset_obj.created else 'Unknown'
                })
            
            return datasets
            
        except Exception as e:
            print(f"[ERROR] get_datasets: {e}")
            traceback.print_exc()
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def load_datasets(self):
        """Carrega datasets no grid"""
        n = ui.notification('Loading datasets...', spinner=True, timeout=None)
        
        try:
            self.datasets = self.get_datasets()
            
            if self.datasets_grid:
                self.datasets_grid.options['rowData'] = self.datasets
                self.datasets_grid.update()
            
            n.dismiss()
            ui.notify(f"✅ Loaded {len(self.datasets)} datasets", type="positive")
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    async def manage_permissions(self):
        """Abre dialog para gerenciar permissões"""
        rows = await self.datasets_grid.get_selected_rows()
        if not rows:
            ui.notify('No dataset selected', type="warning")
            return
        
        dataset_info = rows[0]
        self.selected_dataset = dataset_info['dataset_id']
        
        n = ui.notification('Loading permissions...', spinner=True, timeout=None)
        
        try:
            # Atualizar título
            self.dialog_title.set_text(f'Manage IAM: {self.selected_dataset}')
            
            # Atualizar info card
            await self.update_info_card(dataset_info)
            
            # Carregar usuários
            await self.load_users()
            
            # Carregar security check
            await self.load_security_check()
            
            n.dismiss()
            self.manage_dialog.open()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    async def update_info_card(self, dataset_info):
        """Atualiza card de informações"""
        self.info_card_container.clear()
        
        with self.info_card_container:
            with ui.card().classes('w-full bg-blue-50 p-4'):
                ui.label('📊 Dataset Information:').classes('font-bold mb-2')
                ui.label(f"  • Dataset: {dataset_info['dataset_id']}").classes('text-sm')
                ui.label(f"  • Type: {dataset_info['type']}").classes('text-sm')
                ui.label(f"  • Users: {dataset_info['users']}").classes('text-sm')
                ui.label(f"  • Owners: {dataset_info['owners']}").classes('text-sm')
                ui.label(f"  • Authorized Views: {dataset_info['authorized_views']}").classes('text-sm')
                ui.label(f"  • Status: {dataset_info['security_status']}").classes('text-sm')
    
    async def load_users(self):
        """Carrega lista de usuários"""
        self.users_container.clear()
        
        try:
            dataset_ref = client.dataset(self.selected_dataset)
            dataset_obj = await run.io_bound(client.get_dataset, dataset_ref)
            
            user_entries = [
                entry for entry in dataset_obj.access_entries
                if entry.entity_type == 'userByEmail'
            ]
            
            if not user_entries:
                with self.users_container:
                    ui.label('No users with permissions').classes('text-grey-5 italic')
                return
            
            with self.users_container:
                for entry in user_entries:
                    with ui.card().classes('w-full p-3 mb-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('flex-1'):
                                ui.label(entry.entity_id).classes('font-bold text-base')
                                
                                role_info = self.ROLES.get(entry.role, {
                                    'label': entry.role,
                                    'description': '',
                                    'color': 'bg-gray-100 text-gray-700'
                                })
                                
                                with ui.row().classes('items-center gap-2 mt-1'):
                                    ui.label(role_info['label']).classes(
                                        f"text-xs px-2 py-1 rounded {role_info['color']}"
                                    )
                                    ui.label(role_info['description']).classes('text-xs text-grey-6')
                            
                            def make_remove(user_email, user_role):
                                async def remove():
                                    await self.remove_user(user_email, user_role)
                                return remove
                            
                            ui.button(
                                icon='delete',
                                on_click=make_remove(entry.entity_id, entry.role)
                            ).props('flat dense color=negative')
            
        except Exception as e:
            with self.users_container:
                ui.label(f'Error loading users: {e}').classes('text-red-600')
            traceback.print_exc()
    
    async def load_security_check(self):
        """Carrega verificação de segurança"""
        self.security_check_container.clear()
        
        try:
            dataset_id = self.selected_dataset
            is_views_dataset = dataset_id.endswith('_views')
            
            with self.security_check_container:
                if is_views_dataset:
                    # Dataset de views
                    with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                        ui.label('✅ This is a VIEWS dataset').classes('font-bold mb-2')
                        ui.label('• Users should have access here').classes('text-sm')
                        ui.label('• This dataset contains protected views').classes('text-sm')
                    
                    # Verificar se existe dataset origem
                    source_dataset = dataset_id.replace('_views', '')
                    try:
                        source_ref = client.dataset(source_dataset)
                        source_obj = await run.io_bound(client.get_dataset, source_ref)
                        
                        with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                            ui.label(f'📊 Source Dataset: {source_dataset}').classes('font-bold mb-2')
                            
                            # Verificar authorized views
                            auth_views = [
                                e for e in source_obj.access_entries
                                if e.entity_type == 'view'
                            ]
                            
                            if auth_views:
                                ui.label(f'✅ {len(auth_views)} Authorized View(s) configured').classes('text-sm text-green-700')
                            else:
                                ui.label('⚠️ No Authorized Views configured').classes('text-sm text-orange-700')
                    except:
                        with ui.card().classes('w-full bg-yellow-50 p-4 mb-4'):
                            ui.label(f'⚠️ Source dataset not found: {source_dataset}').classes('font-bold text-orange-700')
                
                else:
                    # Dataset origem
                    dataset_ref = client.dataset(dataset_id)
                    dataset_obj = await run.io_bound(client.get_dataset, dataset_ref)
                    
                    # Verificar usuários
                    user_entries = [
                        e for e in dataset_obj.access_entries
                        if e.entity_type == 'userByEmail'
                    ]
                    
                    if user_entries:
                        with ui.card().classes('w-full bg-orange-50 p-4 mb-4'):
                            ui.label('⚠️ Security Issue Detected!').classes('font-bold text-orange-700 mb-2')
                            ui.label(f'• {len(user_entries)} user(s) have direct access to source dataset').classes('text-sm')
                            ui.label('• Users should only access via VIEWS dataset').classes('text-sm')
                            ui.label('• Click "FIX SECURITY" to auto-configure').classes('text-sm font-bold')
                        
                        async def fix_security():
                            await self.auto_fix_security()
                        
                        ui.button(
                            '🔧 FIX SECURITY (Auto)',
                            icon='build',
                            on_click=fix_security
                        ).props('color=warning size=lg').classes('w-full')
                    
                    else:
                        with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                            ui.label('✅ Security Status: GOOD').classes('font-bold text-green-700 mb-2')
                            ui.label('• No users have direct access').classes('text-sm')
                            ui.label('• Access controlled via VIEWS dataset').classes('text-sm')
                    
                    # Verificar authorized views
                    auth_views = [
                        e for e in dataset_obj.access_entries
                        if e.entity_type == 'view'
                    ]
                    
                    if auth_views:
                        with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                            ui.label('📋 Authorized Views:').classes('font-bold mb-2')
                            for entry in auth_views:
                                view_id = entry.entity_id
                                ui.label(
                                    f"  ✅ {view_id.get('datasetId')}.{view_id.get('tableId')}"
                                ).classes('text-sm')
        
        except Exception as e:
            with self.security_check_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            traceback.print_exc()
    
    async def add_user(self):
        """Adiciona usuário ao dataset"""
        email = self.new_user_email.value.strip()
        role = self.new_user_role.value
        
        if not email or '@' not in email:
            ui.notify('Invalid email', type="warning")
            return
        
        n = ui.notification(f'Adding {email}...', spinner=True, timeout=None)
        
        try:
            dataset_ref = client.dataset(self.selected_dataset)
            dataset_obj = await run.io_bound(client.get_dataset, dataset_ref)
            
            access_entries = list(dataset_obj.access_entries)
            
            # Verificar se já existe
            for entry in access_entries:
                if entry.entity_type == 'userByEmail' and entry.entity_id == email:
                    n.dismiss()
                    ui.notify(f'User already has access with role: {entry.role}', type="warning")
                    return
            
            # Adicionar
            new_entry = AccessEntry(
                role=role,
                entity_type='userByEmail',
                entity_id=email
            )
            
            access_entries.append(new_entry)
            dataset_obj.access_entries = access_entries
            await run.io_bound(client.update_dataset, dataset_obj, ['access_entries'])
            
            # Audit log
            self.audit_service.log_action(
                action='ADD_USER_TO_DATASET',
                resource_type='DATASET_IAM',
                resource_name=f"{self.selected_dataset}",
                status='SUCCESS',
                details={
                    'user': email,
                    'role': role
                }
            )
            
            n.dismiss()
            ui.notify(f'✅ {email} added with role {role}', type="positive")
            
            # Limpar input
            self.new_user_email.value = ''
            
            # Refresh
            await self.load_users()
            await self.load_security_check()
            self.load_datasets()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def remove_user(self, email, role):
        """Remove usuário do dataset"""
        n = ui.notification(f'Removing {email}...', spinner=True, timeout=None)
        
        try:
            dataset_ref = client.dataset(self.selected_dataset)
            dataset_obj = await run.io_bound(client.get_dataset, dataset_ref)
            
            # Remover entrada
            new_entries = [
                entry for entry in dataset_obj.access_entries
                if not (entry.entity_type == 'userByEmail' and entry.entity_id == email)
            ]
            
            dataset_obj.access_entries = new_entries
            await run.io_bound(client.update_dataset, dataset_obj, ['access_entries'])
            
            # Audit log
            self.audit_service.log_action(
                action='REMOVE_USER_FROM_DATASET',
                resource_type='DATASET_IAM',
                resource_name=f"{self.selected_dataset}",
                status='SUCCESS',
                details={
                    'user': email,
                    'role': role
                }
            )
            
            n.dismiss()
            ui.notify(f'✅ {email} removed', type="positive")
            
            # Refresh
            await self.load_users()
            await self.load_security_check()
            self.load_datasets()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def auto_fix_security(self):
        """Corrige automaticamente a segurança do dataset"""
        n = ui.notification('Fixing security...', spinner=True, timeout=None)
        
        try:
            source_dataset_id = self.selected_dataset
            views_dataset_id = f"{source_dataset_id}_views"
            
            # 1. Obter usuários do dataset origem
            source_ref = client.dataset(source_dataset_id)
            source_obj = await run.io_bound(client.get_dataset, source_ref)
            
            users_to_move = [
                entry for entry in source_obj.access_entries
                if entry.entity_type == 'userByEmail'
            ]
            
            if not users_to_move:
                n.dismiss()
                ui.notify('No users to move', type="info")
                return
            
            # 2. Verificar/criar dataset de views
            try:
                views_ref = client.dataset(views_dataset_id)
                views_obj = await run.io_bound(client.get_dataset, views_ref)
            except:
                # Criar dataset de views
                views_dataset = bigquery.Dataset(views_ref)
                views_dataset.location = "us-central1"
                views_dataset.description = f"Protected views from {source_dataset_id}"
                views_obj = await run.io_bound(client.create_dataset, views_dataset)
                ui.notify(f'✅ Created dataset: {views_dataset_id}', type="info")
            
            # 3. Mover usuários
            moved_users = []
            views_entries = list(views_obj.access_entries)
            
            for user_entry in users_to_move:
                # Verificar se já existe no views
                already_exists = any(
                    e.entity_type == 'userByEmail' and e.entity_id == user_entry.entity_id
                    for e in views_entries
                )
                
                if not already_exists:
                    # Adicionar com role READER
                    views_entries.append(AccessEntry(
                        role='READER',
                        entity_type='userByEmail',
                        entity_id=user_entry.entity_id
                    ))
                    moved_users.append(user_entry.entity_id)
            
            # Atualizar views dataset
            if moved_users:
                views_obj.access_entries = views_entries
                await run.io_bound(client.update_dataset, views_obj, ['access_entries'])
            
            # 4. Remover usuários do dataset origem
            source_entries = [
                entry for entry in source_obj.access_entries
                if entry.entity_type != 'userByEmail'
            ]
            
            source_obj.access_entries = source_entries
            await run.io_bound(client.update_dataset, source_obj, ['access_entries'])
            
            # Audit log
            self.audit_service.log_action(
                action='AUTO_FIX_DATASET_SECURITY',
                resource_type='DATASET_IAM',
                resource_name=f"{source_dataset_id}",
                status='SUCCESS',
                details={
                    'users_moved': len(moved_users),
                    'users': moved_users,
                    'from': source_dataset_id,
                    'to': views_dataset_id
                }
            )
            
            n.dismiss()
            
            # Success dialog
            with ui.dialog() as success_dialog, ui.card().classes('w-full max-w-2xl'):
                ui.label('✅ Security Fixed!').classes('text-h5 font-bold text-green-600 mb-4')
                
                with ui.card().classes('w-full bg-green-50 p-4'):
                    ui.label('📊 Summary:').classes('font-bold mb-2')
                    ui.label(f'  • Users moved: {len(moved_users)}').classes('text-sm')
                    ui.label(f'  • From: {source_dataset_id}').classes('text-sm')
                    ui.label(f'  • To: {views_dataset_id}').classes('text-sm')
                    
                    if moved_users:
                        ui.label('  • Users:').classes('text-sm font-bold mt-2')
                        for user in moved_users:
                            ui.label(f'    ✅ {user}').classes('text-xs')
                
                ui.button('OK', on_click=success_dialog.close).props('color=positive')
            
            success_dialog.open()
            
            # Refresh
            await self.load_users()
            await self.load_security_check()
            self.load_datasets()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def refresh_permissions(self):
        """Refresh permissões"""
        await self.load_users()
        await self.load_security_check()
        ui.notify('Refreshed', type="positive")
    
    def render_ui(self):
        with theme.frame('Dataset IAM Manager'):
            with ui.card().classes('w-full'):
                ui.label("Dataset IAM Manager").classes('text-h5 font-bold mb-4')
                
                with ui.card().classes('w-full bg-yellow-50 p-3 mb-4'):
                    ui.label('🔐 IAM Management:').classes('font-bold text-sm mb-2')
                    ui.label('• Manage user permissions for datasets').classes('text-xs')
                    ui.label('• Move users from source to views datasets').classes('text-xs')
                    ui.label('• Auto-fix security configurations').classes('text-xs')
                
                with ui.row().classes('w-full gap-2 mb-4'):
                    ui.button('REFRESH', icon='refresh', on_click=self.load_datasets).props('color=primary')
                
                ui.label("Datasets").classes('text-h6 font-bold mb-2')
                
                self.datasets_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'dataset_id', 'headerName': 'Dataset ID', 'checkboxSelection': True, 'filter': True, 'minWidth': 300},
                        {'field': 'type', 'headerName': 'Type', 'filter': True, 'minWidth': 120},
                        {'field': 'users', 'headerName': 'Users', 'filter': True, 'minWidth': 100},
                        {'field': 'owners', 'headerName': 'Owners', 'filter': True, 'minWidth': 100},
                        {'field': 'authorized_views', 'headerName': 'Auth Views', 'filter': True, 'minWidth': 120},
                        {'field': 'security_status', 'headerName': 'Security Status', 'filter': True, 'minWidth': 250},
                        {'field': 'created', 'headerName': 'Created', 'filter': True, 'minWidth': 150},
                    ],
                    'rowData': [],
                    'rowSelection': 'single',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("MANAGE IAM", icon="admin_panel_settings", on_click=self.manage_permissions).props('color=primary')
                
                # Carregar datasets ao iniciar
                self.load_datasets()
    
    def run(self):
        pass
