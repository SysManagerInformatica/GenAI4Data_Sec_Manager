import theme
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from services.audit_service import AuditService
import re
import traceback

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DynamicColumnManage:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Manage Dynamic Views"
        
        self.selected_dataset = None
        self.restricted_views = []
        self.views_grid = None
        
        # Para gerenciamento de colunas e usuários
        self.current_view = None
        self.source_table_columns = []
        self.hidden_columns = []
        self.documented_users = []
        
        # ✅ Criar dialog de edição UMA VEZ no init
        self.create_edit_dialog()
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Manage Restricted Views').classes('text-primary text-center text-bold')
    
    def create_edit_dialog(self):
        """Cria dialog de edição UMA VEZ - será reutilizado"""
        print("[DEBUG] Creating edit dialog in __init__")
        
        with ui.dialog() as self.edit_dialog, ui.card().classes('w-full max-w-6xl'):
            # Título (será atualizado dinamicamente)
            self.edit_title = ui.label('').classes('text-h5 font-bold mb-4')
            
            with ui.tabs().classes('w-full') as tabs:
                tab_columns = ui.tab('Hidden Columns', icon='visibility_off')
                tab_users = ui.tab('User Documentation', icon='people')
            
            with ui.tab_panels(tabs, value=tab_columns).classes('w-full'):
                # TAB 1: Hidden Columns
                with ui.tab_panel(tab_columns):
                    with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                        ui.label('ℹ️ Manage which columns are hidden from this view').classes('font-bold text-sm mb-2')
                        ui.label('• Check to HIDE, uncheck to SHOW').classes('text-xs')
                        ui.label('• Changes take effect after clicking SAVE CHANGES').classes('text-xs')
                    
                    # Label de source (será atualizado)
                    self.source_label = ui.label('').classes('text-sm font-bold mb-2')
                    
                    # Container para colunas (será populado dinamicamente)
                    with ui.scroll_area().classes('w-full h-96 border rounded p-2') as self.columns_scroll:
                        self.columns_container = ui.column().classes('w-full')
                    
                    # Resumo (será atualizado)
                    with ui.card().classes('w-full bg-purple-50 p-3 mt-4'):
                        self.summary_label = ui.label('').classes('text-sm font-bold')
                
                # TAB 2: User Documentation
                with ui.tab_panel(tab_users):
                    with ui.card().classes('w-full bg-orange-50 p-3 mb-4'):
                        ui.label('ℹ️ Document which users should access this view').classes('font-bold text-sm mb-2')
                        ui.label('• This is DOCUMENTATION ONLY (not access control)').classes('text-xs')
                        ui.label('• Helps team know who should use this view').classes('text-xs')
                        ui.label('• Saved in view description metadata').classes('text-xs')
                    
                    ui.label('Recommended Users:').classes('text-sm font-bold mb-2')
                    
                    # Container para input de usuário (será recriado a cada abertura)
                    self.users_input_container = ui.column().classes('w-full')
                    
                    # Container para lista de usuários (será populado dinamicamente)
                    self.users_list_container = ui.column().classes('w-full')
            
            # Botões
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=self.close_edit_dialog).props('flat')
                ui.button('SAVE CHANGES', icon='save', on_click=self.save_changes_wrapper).props('color=positive')
    
    def close_edit_dialog(self):
        """Fecha o dialog de edição"""
        self.edit_dialog.close()
    
    async def save_changes_wrapper(self):
        """Wrapper para salvar mudanças"""
        await self.save_view_changes()
    
    def get_datasets(self):
        """Lista datasets"""
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error listing datasets: {e}", type="negative")
            return []
    
    def get_restricted_views(self, dataset_id):
        """Lista views restritas (terminam com _restricted)"""
        try:
            tables = client.list_tables(dataset_id)
            views = []
            
            for table in tables:
                if table.table_id.endswith('_restricted'):
                    table_ref = client.dataset(dataset_id).table(table.table_id)
                    table_obj = client.get_table(table_ref)
                    
                    if table_obj.table_type == 'VIEW':
                        view_definition = table_obj.view_query
                        source_table = self.extract_source_table(view_definition)
                        view_columns = len(table_obj.schema)
                        
                        hidden_cols = []
                        if source_table and source_table != 'Unknown':
                            hidden_cols = self.get_hidden_columns(dataset_id, table.table_id, source_table)
                        
                        views.append({
                            'view_name': table.table_id,
                            'source_table': source_table,
                            'visible_columns': view_columns,
                            'hidden_columns_count': len(hidden_cols),
                            'hidden_columns': hidden_cols,
                            'created': table_obj.created.strftime('%Y-%m-%d %H:%M') if table_obj.created else 'Unknown',
                            'modified': table_obj.modified.strftime('%Y-%m-%d %H:%M') if table_obj.modified else 'Unknown'
                        })
            
            return views
        except Exception as e:
            ui.notify(f"Error getting restricted views: {e}", type="negative")
            return []
    
    def extract_source_table(self, view_query):
        """Extrai nome da tabela origem da query da view"""
        try:
            view_query = ' '.join(view_query.split())
            patterns = [
                r'FROM\s+`[^`]*\.([^`\.]+)`',
                r'FROM\s+`([^`]+)`',
                r'FROM\s+(\w+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, view_query, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return 'Unknown'
        except Exception as e:
            print(f"[ERROR] Error extracting source table: {e}")
            return 'Unknown'
    
    def get_hidden_columns(self, dataset_id, view_name, source_table):
        """Descobre quais colunas estão ocultas"""
        try:
            view_ref = client.dataset(dataset_id).table(view_name)
            view_obj = client.get_table(view_ref)
            view_cols = {field.name for field in view_obj.schema}
            
            table_ref = client.dataset(dataset_id).table(source_table)
            table_obj = client.get_table(table_ref)
            table_cols = {field.name for field in table_obj.schema}
            
            hidden = list(table_cols - view_cols)
            return hidden
        except Exception as e:
            print(f"Error getting hidden columns: {e}")
            return []
    
    def on_dataset_change(self, dataset_id):
        """Quando seleciona dataset"""
        self.selected_dataset = dataset_id
        self.restricted_views = self.get_restricted_views(dataset_id)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_views_grid(self):
        """Atualiza grid"""
        if self.views_grid and self.restricted_views:
            self.views_grid.options['rowData'] = self.restricted_views
            self.views_grid.update()
    
    def update_statistics(self):
        """Atualiza estatísticas"""
        total = len(self.restricted_views)
        if hasattr(self, 'total_views_label'):
            self.total_views_label.set_text(str(total))
    
    async def view_details(self):
        """Mostra detalhes da view"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No view selected', type="warning")
            return
        
        view_info = rows[0]
        
        with ui.dialog() as details_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'View Details: {view_info["view_name"]}').classes('text-h5 font-bold mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-2'):
                ui.label('📊 General Information:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View name: {view_info["view_name"]}').classes('text-xs')
                ui.label(f'  • Source table: {view_info["source_table"]}').classes('text-xs')
                ui.label(f'  • Visible columns: {view_info["visible_columns"]}').classes('text-xs')
                ui.label(f'  • Hidden columns: {view_info["hidden_columns_count"]}').classes('text-xs')
                ui.label(f'  • Created: {view_info["created"]}').classes('text-xs')
                ui.label(f'  • Modified: {view_info["modified"]}').classes('text-xs')
            
            if view_info['hidden_columns']:
                with ui.card().classes('w-full bg-red-50 p-3 mb-2'):
                    ui.label('🚫 Hidden Columns:').classes('font-bold text-sm mb-2')
                    for col in view_info['hidden_columns']:
                        ui.label(f'  • {col}').classes('text-xs')
            else:
                with ui.card().classes('w-full bg-yellow-50 p-3 mb-2'):
                    ui.label('⚠️ No columns hidden').classes('text-sm')
            
            with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                ui.label('📝 Query Example:').classes('font-bold text-sm mb-2')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.{view_info['view_name']}`;", language='sql').classes('w-full text-xs')
            
            async def open_editor():
                print("[DEBUG] open_editor() called!")
                n = ui.notification('Loading view schema...', type='info', spinner=True, timeout=None)
                try:
                    await self.edit_view(view_info, parent_dialog=details_dialog)
                except Exception as e:
                    ui.notify(f"Error opening editor: {e}", type="negative")
                    print(f"[ERROR] {e}")
                    traceback.print_exc()
                finally:
                    n.dismiss()

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=details_dialog.close).props('flat')
                ui.button('EDIT VIEW', icon='edit', on_click=open_editor).props('color=primary')
        
        details_dialog.open()
    
    async def edit_view(self, view_info, parent_dialog=None):
        """Carrega dados e abre o dialog de edição"""
        print(f"[DEBUG] ===== EDIT_VIEW CALLED =====")
        print(f"[DEBUG] View: {view_info['view_name']}")
        
        self.current_view = view_info
        
        try:
            source_table = view_info['source_table']
            
            if source_table == 'Unknown' or not source_table:
                ui.notify("⚠️ Cannot determine source table", type="warning")
                if parent_dialog:
                    parent_dialog.close()
                self.ask_source_table(view_info)
                return
            
            print(f"[DEBUG] Loading schema for: {source_table}")
            ui.notify(f"Fetching schema...", type="ongoing", timeout=2000)
            
            # Carregar schema
            table_ref = client.dataset(self.selected_dataset).table(source_table)
            table_obj = await run.io_bound(client.get_table, table_ref)
            
            self.source_table_columns = []
            for field in table_obj.schema:
                self.source_table_columns.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            
            self.hidden_columns = list(view_info['hidden_columns'])
            
            # Carregar usuários
            view_ref = client.dataset(self.selected_dataset).table(view_info['view_name'])
            view_obj = await run.io_bound(client.get_table, view_ref)
            self.documented_users = self.parse_users_from_description(view_obj.description)
            
            print(f"[DEBUG] Loaded {len(self.source_table_columns)} columns")
            ui.notify("Schema loaded!", type="positive", timeout=1000)
            
        except Exception as e:
            print(f"[ERROR] {e}")
            traceback.print_exc()
            ui.notify(f"Error: {e}", type="negative")
            return
        
        # Fechar dialog anterior
        if parent_dialog:
            parent_dialog.close()
        
        # Popular dialog
        print("[DEBUG] Populating dialog...")
        self.populate_edit_dialog(view_info['view_name'], source_table)
        
        # Abrir dialog
        print("[DEBUG] Opening dialog...")
        self.edit_dialog.open()
        print("[DEBUG] Dialog opened!")
    
    def populate_edit_dialog(self, view_name, source_table):
        """Popula o dialog com os dados carregados"""
        print("[DEBUG] populate_edit_dialog() called")
        
        # Atualizar título
        self.edit_title.set_text(f'Edit View: {view_name}')
        
        # Atualizar source label
        self.source_label.set_text(f'Source: {source_table} ({len(self.source_table_columns)} columns)')
        
        # Limpar e popular colunas
        self.columns_container.clear()
        
        with self.columns_container:
            for col in self.source_table_columns:
                with ui.card().classes('w-full p-3 mb-2'):
                    with ui.row().classes('w-full items-center gap-4'):
                        is_hidden = col['name'] in self.hidden_columns
                        
                        # Factory para toggle
                        def make_toggle(column_name):
                            def toggle(e):
                                if e.value and column_name not in self.hidden_columns:
                                    self.hidden_columns.append(column_name)
                                    self.update_summary()
                                elif not e.value and column_name in self.hidden_columns:
                                    self.hidden_columns.remove(column_name)
                                    self.update_summary()
                            return toggle
                        
                        ui.checkbox(
                            text='Hide',
                            value=is_hidden,
                            on_change=make_toggle(col['name'])
                        ).classes('w-20')
                        
                        with ui.column().classes('flex-1'):
                            ui.label(col['name']).classes('font-bold text-base')
                            ui.label(f"Type: {col['type']}").classes('text-xs text-grey-6')
                        
                        status = 'HIDDEN' if is_hidden else 'VISIBLE'
                        status_color = 'bg-red-100 text-red-600' if is_hidden else 'bg-green-100 text-green-600'
                        ui.label(status).classes(f'text-sm px-3 py-1 rounded {status_color}')
        
        # Atualizar resumo
        self.update_summary()
        
        # Popular usuários
        self.populate_users_section()
        
        print("[DEBUG] Dialog populated!")
    
    def update_summary(self):
        """Atualiza resumo de colunas"""
        visible = len(self.source_table_columns) - len(self.hidden_columns)
        self.summary_label.set_text(f'📊 Total: {len(self.source_table_columns)} | Visible: {visible} | Hidden: {len(self.hidden_columns)}')
    
    def populate_users_section(self):
        """Popula seção de usuários"""
        # Limpar containers
        self.users_input_container.clear()
        self.users_list_container.clear()
        
        # Input para adicionar
        with self.users_input_container:
            with ui.row().classes('w-full gap-2 mb-4'):
                user_input = ui.input(
                    placeholder='user@company.com',
                    label='Add user email'
                ).classes('flex-1')
                
                def add_user():
                    email = user_input.value.strip()
                    if email and '@' in email:
                        if email not in self.documented_users:
                            self.documented_users.append(email)
                            user_input.value = ''
                            self.populate_users_section()
                            ui.notify(f"Added: {email}", type="positive")
                        else:
                            ui.notify("User already in list", type="warning")
                    else:
                        ui.notify("Invalid email", type="warning")
                
                ui.button('ADD', icon='add', on_click=add_user).props('color=positive')
        
        # Lista de usuários
        with self.users_list_container:
            if not self.documented_users:
                ui.label('No users documented yet').classes('text-grey-5 italic')
            else:
                for email in self.documented_users:
                    with ui.row().classes('w-full items-center justify-between p-2 border rounded mb-1 bg-white'):
                        ui.label(email).classes('text-sm')
                        
                        def make_remove(user_email):
                            def remove():
                                self.documented_users.remove(user_email)
                                self.populate_users_section()
                                ui.notify(f"Removed: {user_email}", type="info")
                            return remove
                        
                        ui.button(icon='delete', on_click=make_remove(email)).props('flat dense size=sm color=negative')
    
    def parse_users_from_description(self, description):
        """Extrai usuários da descrição"""
        if not description:
            return []
        try:
            if 'USERS:' in description:
                users_text = description.split('USERS:')[1].split('\n')[0]
                emails = [email.strip() for email in users_text.split(',')]
                return [e for e in emails if '@' in e]
        except:
            pass
        return []
    
    async def save_view_changes(self):
        """Salva mudanças"""
        if not self.current_view:
            return
        
        visible_columns = [col['name'] for col in self.source_table_columns if col['name'] not in self.hidden_columns]
        
        if not visible_columns:
            ui.notify("❌ Cannot hide ALL columns!", type="negative")
            return
        
        n = ui.notification('Saving changes...', spinner=True, timeout=None)
        
        try:
            view_name = self.current_view['view_name']
            source_table = self.current_view['source_table']
            
            # Recriar view
            sql = f"""CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(visible_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{source_table}`;"""
            
            query_job = await run.io_bound(client.query, sql)
            await run.io_bound(query_job.result)
            
            # Atualizar descrição
            if self.documented_users:
                description = f"Restricted view from {source_table}\nHidden columns: {', '.join(self.hidden_columns)}\nUSERS: {', '.join(self.documented_users)}"
            else:
                description = f"Restricted view from {source_table}\nHidden columns: {', '.join(self.hidden_columns)}"
            
            table_ref = client.dataset(self.selected_dataset).table(view_name)
            table = await run.io_bound(client.get_table, table_ref)
            table.description = description
            await run.io_bound(client.update_table, table, ['description'])
            
            # Log audit
            self.audit_service.log_action(
                action='UPDATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='SUCCESS',
                details={
                    'hidden_columns': self.hidden_columns,
                    'visible_columns': visible_columns,
                    'documented_users': self.documented_users,
                    'total_columns': len(self.source_table_columns)
                }
            )
            
            n.dismiss()
            ui.notify(f"✅ View updated successfully!", type="positive")
            self.edit_dialog.close()
            
            # Refresh
            self.restricted_views = self.get_restricted_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            
        except Exception as e:
            n.dismiss()
            print(f"[ERROR] {e}")
            traceback.print_exc()
            self.audit_service.log_action(
                action='UPDATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error: {e}", type="negative")
    
    def ask_source_table(self, view_info):
        """Pergunta tabela origem"""
        with ui.dialog() as ask_dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('⚠️ Source Table Not Found').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label('Select source table manually:').classes('mb-4')
            
            try:
                tables = client.list_tables(self.selected_dataset)
                table_names = [t.table_id for t in tables if not t.table_id.endswith('_restricted')]
                
                if not table_names:
                    ui.label('No tables found').classes('text-red-600')
                    ui.button('Close', on_click=ask_dialog.close).props('color=primary')
                    ask_dialog.open()
                    return
                
                table_select = ui.select(
                    options=table_names,
                    label='Source Table',
                    value=table_names[0] if table_names else None
                ).classes('w-full')
                
            except Exception as e:
                ui.notify(f"Error: {e}", type="negative")
                ask_dialog.close()
                return
            
            async def continue_action():
                if not table_select.value:
                    ui.notify("Please select a table", type="warning")
                    return
                ask_dialog.close()
                view_info['source_table'] = table_select.value
                await self.edit_view(view_info)
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=ask_dialog.close).props('flat')
                ui.button('Continue', on_click=continue_action).props('color=primary')
        
        ask_dialog.open()
    
    async def delete_selected_views(self):
        """Deleta views"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No views selected', type="warning")
            return
        
        view_names = [row['view_name'] for row in rows]
        view_list = '\n'.join([f"• {name}" for name in view_names])
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label(f'Delete {len(view_names)} view(s)?').classes('mb-2')
            ui.label(view_list).classes('text-sm whitespace-pre mb-4')
            ui.label('This cannot be undone!').classes('text-red-600 font-bold')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button('DELETE', on_click=lambda: self.execute_deletion(rows, confirm_dialog)).props('color=negative')
        
        confirm_dialog.open()
    
    def execute_deletion(self, views, dialog):
        """Executa deleção"""
        success = 0
        failed = 0
        
        for view in views:
            try:
                table_ref = client.dataset(self.selected_dataset).table(view['view_name'])
                client.delete_table(table_ref)
                
                self.audit_service.log_action(
                    action='DELETE_RESTRICTED_VIEW',
                    resource_type='RESTRICTED_VIEW',
                    resource_name=f"{self.selected_dataset}.{view['view_name']}",
                    status='SUCCESS'
                )
                success += 1
            except Exception as e:
                self.audit_service.log_action(
                    action='DELETE_RESTRICTED_VIEW',
                    resource_type='RESTRICTED_VIEW',
                    resource_name=f"{self.selected_dataset}.{view['view_name']}",
                    status='FAILED',
                    error_message=str(e)
                )
                failed += 1
        
        dialog.close()
        
        if success > 0:
            ui.notify(f"✅ {success} view(s) deleted", type="positive")
        if failed > 0:
            ui.notify(f"❌ {failed} failed", type="negative")
        
        self.restricted_views = self.get_restricted_views(self.selected_dataset)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_all(self):
        """Refresh"""
        if self.selected_dataset:
            self.restricted_views = self.get_restricted_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            ui.notify("Refreshed", type="positive")
        else:
            ui.notify("Select dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('Manage Dynamic Views'):
            with ui.card().classes('w-full'):
                ui.label("Manage Restricted Views").classes('text-h5 font-bold mb-4')
                
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    datasets = self.get_datasets()
                    ui.select(
                        options=datasets,
                        label='Select Dataset',
                        on_change=lambda e: self.on_dataset_change(e.value)
                    ).classes('flex-1')
                    
                    ui.button('REFRESH', icon='refresh', on_click=self.refresh_all).props('flat')
                
                with ui.row().classes('w-full gap-4 mb-4'):
                    with ui.card().classes('flex-1 bg-blue-50'):
                        ui.label('Restricted Views').classes('text-sm text-grey-7')
                        self.total_views_label = ui.label('0').classes('text-3xl font-bold text-blue-600')
                
                ui.separator()
                ui.label("Restricted Views").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'view_name', 'headerName': 'View Name', 'checkboxSelection': True, 'filter': True, 'minWidth': 300},
                        {'field': 'source_table', 'headerName': 'Source Table', 'filter': True, 'minWidth': 250},
                        {'field': 'visible_columns', 'headerName': 'Visible Columns', 'filter': True, 'minWidth': 140},
                        {'field': 'hidden_columns_count', 'headerName': 'Hidden Columns', 'filter': True, 'minWidth': 140},
                        {'field': 'created', 'headerName': 'Created', 'filter': True, 'minWidth': 150},
                        {'field': 'modified', 'headerName': 'Modified', 'filter': True, 'minWidth': 150},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("VIEW DETAILS", icon="info", on_click=self.view_details).props('color=primary')
                    ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_views).props('color=negative')
    
    def run(self):
        pass
