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
        self.all_user_entries = []
        
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
            
            # Security status card
            self.security_status_container = ui.column().classes('w-full mb-4')
            
            # ✅ TABS PARA ORGANIZAR
            with ui.tabs().classes('w-full') as tabs:
                tab_users = ui.tab('Current Users', icon='people')
                tab_add = ui.tab('Add New User', icon='person_add')
            
            with ui.tab_panels(tabs, value=tab_users).classes('w-full'):
                # ✅ TAB 1: CURRENT USERS
                with ui.tab_panel(tab_users):
                    # Campo de busca
                    with ui.row().classes('w-full items-center gap-2 mb-3'):
                        self.search_input = ui.input(
                            placeholder='Search by email...',
                            on_change=self.filter_users
                        ).classes('flex-1').props('outlined dense clearable')
                        
                        ui.icon('search', size='sm', color='primary')
                    
                    # Label com contagem
                    self.users_count_label = ui.label('').classes('text-sm text-gray-600 mb-2')
                    
                    # Lista de usuários (SEM limite de altura, vai crescer conforme necessário)
                    with ui.scroll_area().classes('w-full').style('max-height: 500px;'):
                        self.users_container = ui.column().classes('w-full gap-2')
                
                # ✅ TAB 2: ADD NEW USER
                with ui.tab_panel(tab_add):
                    with ui.card().classes('w-full bg-green-50 p-6'):
                        ui.label('➕ Add New User to Dataset').classes('font-bold text-xl mb-4')
                        
                        ui.label('Grant access to a user by entering their email address and selecting a role.').classes('text-sm text-gray-700 mb-4')
                        
                        with ui.column().classes('w-full gap-4'):
                            self.new_user_email = ui.input(
                                label='Email Address',
                                placeholder='user@company.com'
                            ).classes('w-full').props('outlined')
                            
                            self.new_user_role = ui.select(
                                label='Role',
                                options=list(self.ROLES.keys()),
                                value='READER'
                            ).classes('w-full').props('outlined')
                            
                            # Mostrar descrição do role selecionado
                            self.role_description = ui.label('').classes('text-sm text-gray-600 italic')
                            
                            # Atualizar descrição quando mudar o role
                            def update_role_description():
                                role = self.new_user_role.value
                                role_info = self.ROLES.get(role, {})
                                self.role_description.set_text(
                                    f"{role_info.get('label', '')} - {role_info.get('description', '')}"
                                )
                            
                            self.new_user_role.on('update:model-value', update_role_description)
                            update_role_description()  # Inicializar
                            
                            ui.button(
                                'ADD USER',
                                icon='person_add',
                                on_click=self.add_user
                            ).classes('w-full').props('color=positive size=lg')
            
            ui.separator().classes('my-4')
            
            # Botões de ação
            with ui.row().classes('w-full justify-end gap-2'):
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
                elif user_count == 0:
                    security_status = '✅ No Direct Access'
                elif authorized_views_count > 0:
                    security_status = '🔐 Has Authorized Views'
                else:
                    security_status = '⚠️ Has Direct Access'
                
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
        print("=" * 80)
        print("🟢 MANAGE_PERMISSIONS CALLED!")
        print("=" * 80)
        
        rows = await self.datasets_grid.get_selected_rows()
        print(f"Selected rows: {rows}")
        
        if not rows:
            print("❌ No dataset selected!")
            ui.notify('No dataset selected', type="warning")
            return
        
        dataset_info = rows[0]
        self.selected_dataset = dataset_info['dataset_id']
        print(f"✅ Selected dataset: {self.selected_dataset}")
        
        n = ui.notification('Loading permissions...', spinner=True, timeout=None)
        
        try:
            # Atualizar título
            self.dialog_title.set_text(f'Manage IAM: {self.selected_dataset}')
            print(f"✅ Dialog title set")
            
            # Atualizar info card
            await self.update_info_card(dataset_info)
            print(f"✅ Info card updated")
            
            # Atualizar security status
            await self.update_security_status(dataset_info)
            print(f"✅ Security status updated")
            
            # Carregar usuários
            print(f"🔵 About to call load_users()...")
            await self.load_users()
            print(f"✅ load_users() completed")
            
            n.dismiss()
            self.manage_dialog.open()
            print(f"✅ Dialog opened")
            
        except Exception as e:
            n.dismiss()
            print(f"❌ ERROR in manage_permissions: {e}")
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
                ui.label(f"  • Total Users: {dataset_info['users']}").classes('text-sm')
                ui.label(f"  • Owners: {dataset_info['owners']}").classes('text-sm')
                ui.label(f"  • Authorized Views: {dataset_info['authorized_views']}").classes('text-sm')
                ui.label(f"  • Status: {dataset_info['security_status']}").classes('text-sm font-bold')
    
    async def update_security_status(self, dataset_info):
        """Atualiza status de segurança"""
        self.security_status_container.clear()
        
        with self.security_status_container:
            is_views = dataset_info['type'] == 'Views'
            has_users = dataset_info['users'] > 0
            
            if is_views:
                # Dataset de views - OK ter usuários
                with ui.card().classes('w-full bg-green-50 p-4'):
                    ui.label('✅ Views Dataset').classes('font-bold text-green-700 mb-2')
                    ui.label('• Users should have access to this dataset').classes('text-sm')
                    ui.label('• Contains protected views with masking/CLS').classes('text-sm')
            
            elif not has_users:
                # Dataset origem sem usuários - IDEAL
                with ui.card().classes('w-full bg-green-50 p-4'):
                    ui.label('✅ Secure Configuration').classes('font-bold text-green-700 mb-2')
                    ui.label('• No users have direct access').classes('text-sm')
                    ui.label('• Access controlled via authorized views').classes('text-sm')
            
            else:
                # Dataset origem COM usuários - AVISO
                with ui.card().classes('w-full bg-orange-50 p-4'):
                    ui.label('⚠️ Security Recommendation').classes('font-bold text-orange-700 mb-2')
                    ui.label(f'• {dataset_info["users"]} user(s) have direct access').classes('text-sm')
                    ui.label('• Consider moving users to views dataset').classes('text-sm')
                    
                    # Verificar se existe dataset _views
                    views_dataset = f"{dataset_info['dataset_id']}_views"
                    ui.label(f'• Recommended: Grant access to {views_dataset} instead').classes('text-sm font-bold')
    
    async def load_users(self):
        """Carrega lista de usuários"""
        print("=" * 80)
        print("🔴 LOAD_USERS CALLED!")
        print(f"Dataset: {self.selected_dataset}")
        print("=" * 80)
        
        # Limpar container e busca
        self.users_container.clear()
        self.search_input.value = ''
        print("✅ Container cleared")
        
        try:
            dataset_ref = client.dataset(self.selected_dataset)
            dataset_obj = await run.io_bound(client.get_dataset, dataset_ref)
            print(f"✅ Dataset object retrieved")
            
            # Debug: Ver TODOS os entries
            print(f"Total access entries: {len(dataset_obj.access_entries)}")
            
            user_entries = []
            for entry in dataset_obj.access_entries:
                print(f"  Entry type: {entry.entity_type}, Role: {entry.role}")
                if entry.entity_type == 'userByEmail':
                    user_entries.append(entry)
                    print(f"    ✅ User: {entry.entity_id}")
            
            print(f"Filtered user entries: {len(user_entries)}")
            
            # ✅ Salvar para usar no filtro
            self.all_user_entries = user_entries
            
            # Atualizar contagem
            self.users_count_label.set_text(f'Showing {len(user_entries)} of {len(user_entries)} users')
            
            if not user_entries:
                print("⚠️ No users found - showing empty message")
                with self.users_container:
                    with ui.card().classes('w-full bg-gray-50 p-4'):
                        ui.icon('people_off', size='48px', color='gray').classes('mx-auto mb-2')
                        ui.label('No users with permissions').classes('text-gray-500 text-center')
                return
            
            # Criar cards para cada usuário
            print(f"🔵 Creating cards for {len(user_entries)} users...")
            self.render_user_cards(user_entries)
            
            print(f"✅ All cards created successfully")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ ERROR in load_users: {e}")
            with self.users_container:
                ui.label(f'Error loading users: {e}').classes('text-red-600')
            traceback.print_exc()
    
    def render_user_cards(self, user_entries):
        """Renderiza cards de usuários"""
        with self.users_container:
            for i, entry in enumerate(user_entries):
                print(f"  Creating card {i+1} for: {entry.entity_id}")
                
                with ui.card().classes('w-full p-4 bg-white border-2'):
                    with ui.row().classes('w-full items-center justify-between'):
                        # User info
                        with ui.column().classes('flex-1'):
                            with ui.row().classes('items-center gap-2 mb-1'):
                                ui.icon('person', size='24px', color='blue')
                                ui.label(entry.entity_id).classes('font-bold text-base')
                            
                            role_info = self.ROLES.get(entry.role, {
                                'label': entry.role,
                                'description': '',
                                'color': 'bg-gray-100 text-gray-700'
                            })
                            
                            with ui.row().classes('items-center gap-2'):
                                ui.label(role_info['label']).classes(
                                    f"text-sm px-3 py-1 rounded {role_info['color']}"
                                )
                                ui.label(role_info['description']).classes('text-xs text-gray-600')
                        
                        # Remove button
                        def make_remove(user_email, user_role):
                            async def remove():
                                await self.remove_user(user_email, user_role)
                            return remove
                        
                        ui.button(
                            'REMOVE',
                            icon='delete',
                            on_click=make_remove(entry.entity_id, entry.role)
                        ).props('flat color=negative')
    
    def filter_users(self):
        """Filtra usuários baseado na busca"""
        search_term = self.search_input.value.lower() if self.search_input.value else ''
        
        # Recriar a lista filtrada
        self.users_container.clear()
        
        if not hasattr(self, 'all_user_entries') or not self.all_user_entries:
            return
        
        filtered_users = [
            entry for entry in self.all_user_entries
            if search_term in entry.entity_id.lower()
        ]
        
        # Atualizar contagem
        total = len(self.all_user_entries)
        showing = len(filtered_users)
        self.users_count_label.set_text(f'Showing {showing} of {total} users')
        
        if not filtered_users:
            with self.users_container:
                with ui.card().classes('w-full bg-gray-50 p-4'):
                    ui.icon('search_off', size='48px', color='gray').classes('mx-auto mb-2')
                    ui.label('No users found').classes('text-gray-500 text-center')
            return
        
        # Criar cards para usuários filtrados
        self.render_user_cards(filtered_users)
    
    async def add_user(self):
        """Adiciona usuário ao dataset"""
        email = self.new_user_email.value.strip()
        role = self.new_user_role.value
        
        if not email or '@' not in email:
            ui.notify('Please enter a valid email address', type="warning")
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
                    ui.notify(f'User already has {entry.role} access', type="warning")
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
            ui.notify(f'✅ {email} added with {role} role', type="positive")
            
            # Limpar input
            self.new_user_email.value = ''
            
            # Refresh
            await self.load_users()
            self.load_datasets()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def remove_user(self, email, role):
        """Remove usuário do dataset"""
        # Confirmar remoção
        with ui.dialog() as confirm_dialog, ui.card().classes('w-full max-w-md'):
            ui.label('⚠️ Confirm Removal').classes('text-h6 font-bold text-orange-600 mb-4')
            
            with ui.card().classes('w-full bg-orange-50 p-3 mb-4'):
                ui.label(f'User: {email}').classes('text-sm font-bold')
                ui.label(f'Role: {role}').classes('text-sm')
                ui.label(f'Dataset: {self.selected_dataset}').classes('text-sm')
            
            ui.label('This action will remove all permissions for this user on this dataset.').classes('text-sm mb-2')
            ui.label('Are you sure?').classes('text-sm font-bold')
            
            async def execute_removal():
                confirm_dialog.close()
                await self.execute_remove_user(email, role)
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=confirm_dialog.close).props('flat')
                ui.button('REMOVE', on_click=execute_removal).props('color=negative')
        
        confirm_dialog.open()
    
    async def execute_remove_user(self, email, role):
        """Executa remoção do usuário"""
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
            ui.notify(f'✅ {email} removed successfully', type="positive")
            
            # Refresh
            await self.load_users()
            self.load_datasets()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f'Error: {e}', type="negative")
            traceback.print_exc()
    
    async def refresh_permissions(self):
        """Refresh permissões"""
        await self.load_users()
        ui.notify('Refreshed', type="positive")
    
    def render_ui(self):
        with theme.frame('Dataset IAM Manager'):
            with ui.card().classes('w-full'):
                ui.label("Dataset IAM Manager").classes('text-h5 font-bold mb-4')
                
                with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                    ui.label('🔐 Manage Dataset Permissions:').classes('font-bold text-sm mb-2')
                    ui.label('• Add or remove users from datasets').classes('text-xs')
                    ui.label('• Control who can access your data').classes('text-xs')
                    ui.label('• Assign appropriate roles (Reader, Writer, Owner)').classes('text-xs')
                
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
                    ui.button(
                        "MANAGE IAM",
                        icon="admin_panel_settings",
                        on_click=lambda: self.manage_permissions()
                    ).props('color=primary')
                
                # Carregar datasets ao iniciar
                self.load_datasets()
    
    def run(self):
        pass
