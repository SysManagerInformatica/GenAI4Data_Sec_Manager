import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from services.audit_service import AuditService

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DynamicColumnManage:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Manage Dynamic Views"
        
        self.selected_dataset = None
        self.dynamic_views = []
        self.views_grid = None
        
        # Para gerenciamento de usuários
        self.current_view_group = None
        self.user_assignments = {
            'full': [],
            'masked': [],
            'public': []
        }
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Manage Dynamic Column Security Views').classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        """Lista datasets"""
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error listing datasets: {e}", type="negative")
            return []
    
    def get_dynamic_views(self, dataset_id):
        """Lista views dinâmicas (terminam com _full, _masked, _public)"""
        try:
            tables = client.list_tables(dataset_id)
            views = []
            
            # Agrupar por base name
            view_groups = {}
            
            for table in tables:
                table_ref = client.dataset(dataset_id).table(table.table_id)
                table_obj = client.get_table(table_ref)
                
                if table_obj.table_type == 'VIEW':
                    # Detectar se é view dinâmica
                    if table.table_id.endswith('_full'):
                        base_name = table.table_id[:-5]
                        if base_name not in view_groups:
                            view_groups[base_name] = {}
                        view_groups[base_name]['full'] = table.table_id
                    elif table.table_id.endswith('_masked'):
                        base_name = table.table_id[:-7]
                        if base_name not in view_groups:
                            view_groups[base_name] = {}
                        view_groups[base_name]['masked'] = table.table_id
                    elif table.table_id.endswith('_public'):
                        base_name = table.table_id[:-7]
                        if base_name not in view_groups:
                            view_groups[base_name] = {}
                        view_groups[base_name]['public'] = table.table_id
            
            # Converter para lista
            for base_name, view_types in view_groups.items():
                # Só considera como grupo dinâmico se tem pelo menos 2 views
                if len(view_types) >= 2:
                    users_full = self.get_rls_users(dataset_id, view_types.get('full', ''))
                    users_masked = self.get_rls_users(dataset_id, view_types.get('masked', ''))
                    users_public = self.get_rls_users(dataset_id, view_types.get('public', ''))
                    
                    views.append({
                        'base_name': base_name,
                        'full_view': view_types.get('full', ''),
                        'masked_view': view_types.get('masked', ''),
                        'public_view': view_types.get('public', ''),
                        'view_count': len(view_types),
                        'users_full': users_full,
                        'users_masked': users_masked,
                        'users_public': users_public,
                        'total_users': len(users_full) + len(users_masked) + len(users_public)
                    })
            
            return views
        except Exception as e:
            ui.notify(f"Error getting dynamic views: {e}", type="negative")
            return []
    
    def get_rls_users(self, dataset_id, view_name):
        """Obtém usuários com acesso RLS em uma view"""
        if not view_name:
            return []
        
        try:
            # Query para listar RLS policies
            query = f"""
            SELECT filter_predicate
            FROM `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.ROW_ACCESS_POLICIES`
            WHERE table_name = '{view_name}'
            """
            
            result = client.query(query).result()
            for row in result:
                if row.filter_predicate:
                    # Extrair emails do FILTER USING clause
                    # Formato: SESSION_USER() IN ('email1', 'email2')
                    import re
                    emails = re.findall(r"'([^']+@[^']+)'", row.filter_predicate)
                    return emails
            
            return []
        except Exception as e:
            return []
    
    def on_dataset_change(self, dataset_id):
        """Quando seleciona dataset"""
        self.selected_dataset = dataset_id
        self.dynamic_views = self.get_dynamic_views(dataset_id)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_views_grid(self):
        """Atualiza grid"""
        if self.views_grid and self.dynamic_views:
            self.views_grid.options['rowData'] = self.dynamic_views
            self.views_grid.update()
    
    def update_statistics(self):
        """Atualiza estatísticas"""
        total = len(self.dynamic_views)
        
        if hasattr(self, 'total_groups_label'):
            self.total_groups_label.set_text(str(total))
    
    async def view_details(self):
        """Mostra detalhes do grupo de views"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No view group selected', type="warning")
            return
        
        view_group = rows[0]
        
        # Dialog com detalhes
        with ui.dialog() as details_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'View Group: {view_group["base_name"]}').classes('text-h5 font-bold mb-4')
            
            # FULL VIEW
            if view_group['full_view']:
                with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                    ui.label(f'👑 FULL VIEW: {view_group["full_view"]}').classes('font-bold mb-2')
                    ui.label('Users with access:').classes('text-sm font-bold')
                    if view_group['users_full']:
                        for user in view_group['users_full']:
                            ui.label(f'  • {user}').classes('text-xs')
                    else:
                        ui.label('  No users assigned').classes('text-xs text-grey-5')
            
            # MASKED VIEW
            if view_group['masked_view']:
                with ui.card().classes('w-full bg-purple-50 p-3 mb-2'):
                    ui.label(f'🎭 MASKED VIEW: {view_group["masked_view"]}').classes('font-bold mb-2')
                    ui.label('Users with access:').classes('text-sm font-bold')
                    if view_group['users_masked']:
                        for user in view_group['users_masked']:
                            ui.label(f'  • {user}').classes('text-xs')
                    else:
                        ui.label('  No users assigned').classes('text-xs text-grey-5')
            
            # PUBLIC VIEW
            if view_group['public_view']:
                with ui.card().classes('w-full bg-blue-50 p-3 mb-2'):
                    ui.label(f'👁️ PUBLIC VIEW: {view_group["public_view"]}').classes('font-bold mb-2')
                    ui.label('Users with access:').classes('text-sm font-bold')
                    if view_group['users_public']:
                        for user in view_group['users_public']:
                            ui.label(f'  • {user}').classes('text-xs')
                    else:
                        ui.label('  No users assigned').classes('text-xs text-grey-5')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=details_dialog.close).props('flat')
                ui.button('MANAGE USERS', on_click=lambda: [details_dialog.close(), self.manage_users(view_group)]).props('color=primary')
        
        details_dialog.open()
    
    def manage_users(self, view_group):
        """Interface COMPLETA para gerenciar usuários"""
        self.current_view_group = view_group
        
        # Carregar usuários atuais
        self.user_assignments = {
            'full': list(view_group.get('users_full', [])),
            'masked': list(view_group.get('users_masked', [])),
            'public': list(view_group.get('users_public', []))
        }
        
        with ui.dialog() as manage_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label(f'Manage Users: {view_group["base_name"]}').classes('text-h5 font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                # COLUNA 1: FULL ACCESS
                with ui.card().classes('flex-1 bg-green-50 p-4'):
                    ui.label('👑 FULL ACCESS').classes('text-h6 font-bold mb-2')
                    ui.label('Can see all columns (real data)').classes('text-xs text-grey-7 mb-3')
                    
                    # Input para adicionar
                    with ui.row().classes('w-full gap-2 mb-3'):
                        full_input = ui.input(placeholder='user@company.com').classes('flex-1')
                        ui.button(
                            'ADD',
                            icon='add',
                            on_click=lambda: self.add_user_to_level('full', full_input, full_users_container)
                        ).props('flat color=positive size=sm')
                    
                    # Lista de usuários
                    full_users_container = ui.column().classes('w-full gap-1')
                    self.render_user_list('full', full_users_container)
                
                # COLUNA 2: MASKED ACCESS
                with ui.card().classes('flex-1 bg-purple-50 p-4'):
                    ui.label('🎭 MASKED ACCESS').classes('text-h6 font-bold mb-2')
                    ui.label('Restricted columns shown as hash').classes('text-xs text-grey-7 mb-3')
                    
                    # Input para adicionar
                    with ui.row().classes('w-full gap-2 mb-3'):
                        masked_input = ui.input(placeholder='analyst@company.com').classes('flex-1')
                        ui.button(
                            'ADD',
                            icon='add',
                            on_click=lambda: self.add_user_to_level('masked', masked_input, masked_users_container)
                        ).props('flat color=purple size=sm')
                    
                    # Lista de usuários
                    masked_users_container = ui.column().classes('w-full gap-1')
                    self.render_user_list('masked', masked_users_container)
                
                # COLUNA 3: PUBLIC ACCESS
                with ui.card().classes('flex-1 bg-blue-50 p-4'):
                    ui.label('👁️ PUBLIC ACCESS').classes('text-h6 font-bold mb-2')
                    ui.label('Restricted columns hidden').classes('text-xs text-grey-7 mb-3')
                    
                    # Input para adicionar
                    with ui.row().classes('w-full gap-2 mb-3'):
                        public_input = ui.input(placeholder='viewer@company.com').classes('flex-1')
                        ui.button(
                            'ADD',
                            icon='add',
                            on_click=lambda: self.add_user_to_level('public', public_input, public_users_container)
                        ).props('flat color=blue size=sm')
                    
                    # Lista de usuários
                    public_users_container = ui.column().classes('w-full gap-1')
                    self.render_user_list('public', public_users_container)
            
            # Info box
            with ui.card().classes('w-full bg-orange-50 p-3 mt-4'):
                ui.label('ℹ️ How to move users:').classes('text-sm font-bold mb-1')
                ui.label('1. Remove user from current level (trash icon)').classes('text-xs')
                ui.label('2. Add user to desired level (ADD button)').classes('text-xs')
                ui.label('3. Click SAVE CHANGES to apply').classes('text-xs')
            
            # Botões de ação
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=manage_dialog.close).props('flat')
                ui.button(
                    'SAVE CHANGES',
                    icon='save',
                    on_click=lambda: self.save_user_changes(manage_dialog)
                ).props('color=positive')
        
        manage_dialog.open()
    
    def render_user_list(self, level, container):
        """Renderiza lista de usuários de um nível"""
        container.clear()
        
        with container:
            users = self.user_assignments.get(level, [])
            if not users:
                ui.label('No users assigned').classes('text-xs text-grey-5 italic')
            else:
                for user in users:
                    with ui.row().classes('w-full items-center justify-between p-2 border rounded bg-white mb-1'):
                        ui.label(user).classes('text-xs flex-1')
                        ui.button(
                            icon='delete',
                            on_click=lambda u=user, l=level, c=container: self.remove_user_from_level(l, u, c)
                        ).props('flat dense size=sm color=negative')
    
    def add_user_to_level(self, level, input_field, container):
        """Adiciona usuário a um nível"""
        email = input_field.value.strip()
        
        if not email or '@' not in email:
            ui.notify('Invalid email address', type="warning")
            return
        
        # Verificar se já existe em algum nível
        for lvl, users in self.user_assignments.items():
            if email in users:
                ui.notify(f'User already assigned to {lvl.upper()} level', type="warning")
                return
        
        # Adicionar
        self.user_assignments[level].append(email)
        input_field.value = ''
        self.render_user_list(level, container)
        ui.notify(f'User added to {level.upper()} level', type="positive")
    
    def remove_user_from_level(self, level, email, container):
        """Remove usuário de um nível"""
        if email in self.user_assignments[level]:
            self.user_assignments[level].remove(email)
            self.render_user_list(level, container)
            ui.notify(f'User removed from {level.upper()} level', type="info")
    
    def save_user_changes(self, dialog):
        """Salva mudanças de usuários no BigQuery"""
        if not self.current_view_group:
            return
        
        try:
            view_group = self.current_view_group
            base_name = view_group['base_name']
            
            # Atualizar RLS para cada view
            sqls = []
            
            # FULL VIEW
            if view_group['full_view'] and self.user_assignments['full']:
                users_str = "', '".join(self.user_assignments['full'])
                sql_full = f"""
CREATE OR REPLACE ROW ACCESS POLICY rap_{base_name}_full
ON `{self.project_id}.{self.selected_dataset}.{view_group['full_view']}`
GRANT TO ("allAuthenticatedUsers")
FILTER USING (
  SESSION_USER() IN ('{users_str}')
);"""
                sqls.append(sql_full)
            
            # MASKED VIEW
            if view_group['masked_view'] and self.user_assignments['masked']:
                users_str = "', '".join(self.user_assignments['masked'])
                sql_masked = f"""
CREATE OR REPLACE ROW ACCESS POLICY rap_{base_name}_masked
ON `{self.project_id}.{self.selected_dataset}.{view_group['masked_view']}`
GRANT TO ("allAuthenticatedUsers")
FILTER USING (
  SESSION_USER() IN ('{users_str}')
);"""
                sqls.append(sql_masked)
            
            # PUBLIC VIEW
            if view_group['public_view'] and self.user_assignments['public']:
                users_str = "', '".join(self.user_assignments['public'])
                sql_public = f"""
CREATE OR REPLACE ROW ACCESS POLICY rap_{base_name}_public
ON `{self.project_id}.{self.selected_dataset}.{view_group['public_view']}`
GRANT TO ("allAuthenticatedUsers")
FILTER USING (
  SESSION_USER() IN ('{users_str}')
);"""
                sqls.append(sql_public)
            
            # Executar todos os SQLs
            for sql in sqls:
                query_job = client.query(sql)
                query_job.result()
            
            # Log audit
            self.audit_service.log_action(
                action='UPDATE_DYNAMIC_VIEW_USERS',
                resource_type='DYNAMIC_VIEWS',
                resource_name=f"{self.selected_dataset}.{base_name}",
                status='SUCCESS',
                details={
                    'user_assignments': self.user_assignments
                }
            )
            
            ui.notify('✅ User permissions updated successfully!', type="positive")
            dialog.close()
            
            # Refresh grid
            self.dynamic_views = self.get_dynamic_views(self.selected_dataset)
            self.refresh_views_grid()
            
        except Exception as e:
            self.audit_service.log_action(
                action='UPDATE_DYNAMIC_VIEW_USERS',
                resource_type='DYNAMIC_VIEWS',
                resource_name=f"{self.selected_dataset}.{base_name}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f'Error updating permissions: {e}', type="negative")
    
    async def delete_selected_groups(self):
        """Deleta grupos de views selecionados"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No view groups selected', type="warning")
            return
        
        # Dialog confirmação
        group_names = [row['base_name'] for row in rows]
        group_list = '\n'.join([f"• {name} ({row['view_count']} views)" for name, row in zip(group_names, rows)])
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label(f'Delete {len(group_names)} view group(s)?').classes('mb-2')
            ui.label(group_list).classes('text-sm whitespace-pre mb-4')
            ui.label('This will delete ALL views and RLS policies!').classes('text-red-600 font-bold')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'DELETE ALL',
                    on_click=lambda: self.execute_deletion(rows, confirm_dialog)
                ).props('color=negative')
        
        confirm_dialog.open()
    
    def execute_deletion(self, view_groups, dialog):
        """Executa deleção"""
        success = 0
        failed = 0
        
        for group in view_groups:
            try:
                # Deletar cada view do grupo
                for view_type in ['full_view', 'masked_view', 'public_view']:
                    view_name = group.get(view_type)
                    if view_name:
                        table_ref = client.dataset(self.selected_dataset).table(view_name)
                        client.delete_table(table_ref)
                
                # Log audit
                self.audit_service.log_action(
                    action='DELETE_DYNAMIC_VIEW_GROUP',
                    resource_type='DYNAMIC_VIEWS',
                    resource_name=f"{self.selected_dataset}.{group['base_name']}",
                    status='SUCCESS'
                )
                
                success += 1
                
            except Exception as e:
                self.audit_service.log_action(
                    action='DELETE_DYNAMIC_VIEW_GROUP',
                    resource_type='DYNAMIC_VIEWS',
                    resource_name=f"{self.selected_dataset}.{group['base_name']}",
                    status='FAILED',
                    error_message=str(e)
                )
                failed += 1
        
        dialog.close()
        
        if success > 0:
            ui.notify(f"✅ {success} group(s) deleted successfully", type="positive")
        if failed > 0:
            ui.notify(f"❌ {failed} group(s) failed to delete", type="negative")
        
        # Refresh
        self.dynamic_views = self.get_dynamic_views(self.selected_dataset)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_all(self):
        """Refresh completo"""
        if self.selected_dataset:
            self.dynamic_views = self.get_dynamic_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            ui.notify("Refreshed successfully", type="positive")
        else:
            ui.notify("Please select a dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('Manage Dynamic Views'):
            with ui.card().classes('w-full'):
                ui.label("Manage Dynamic Column Security Views").classes('text-h5 font-bold mb-4')
                
                # Seletor de dataset
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    datasets = self.get_datasets()
                    ui.select(
                        options=datasets,
                        label='Select Dataset',
                        on_change=lambda e: self.on_dataset_change(e.value)
                    ).classes('flex-1')
                    
                    ui.button('REFRESH', icon='refresh', on_click=self.refresh_all).props('flat')
                
                # Estatísticas
                with ui.row().classes('w-full gap-4 mb-4'):
                    with ui.card().classes('flex-1 bg-blue-50'):
                        ui.label('Dynamic View Groups').classes('text-sm text-grey-7')
                        self.total_groups_label = ui.label('0').classes('text-3xl font-bold text-blue-600')
                
                # Grid
                ui.separator()
                ui.label("View Groups").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'base_name', 'headerName': 'Base Name', 'checkboxSelection': True, 'filter': True, 'minWidth': 200},
                        {'field': 'view_count', 'headerName': 'Views', 'filter': True, 'minWidth': 80},
                        {'field': 'total_users', 'headerName': 'Total Users', 'filter': True, 'minWidth': 120},
                        {'field': 'full_view', 'headerName': 'Full View', 'filter': True, 'minWidth': 200},
                        {'field': 'masked_view', 'headerName': 'Masked View', 'filter': True, 'minWidth': 200},
                        {'field': 'public_view', 'headerName': 'Public View', 'filter': True, 'minWidth': 200},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                # Botões
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("VIEW DETAILS", icon="info", on_click=self.view_details).props('color=primary')
                    ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_groups).props('color=negative')
    
    def run(self):
        pass
