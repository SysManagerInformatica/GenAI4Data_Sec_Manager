import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from services.audit_service import AuditService
import re

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
        
        # Para gerenciamento de colunas
        self.current_view = None
        self.source_table_columns = []
        self.hidden_columns = []
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Manage Restricted Views').classes('text-primary text-center text-bold')
    
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
                        # Extrair informações da view
                        view_definition = table_obj.view_query
                        
                        # Tentar descobrir tabela origem
                        source_table = self.extract_source_table(view_definition)
                        
                        # Contar colunas na view
                        view_columns = len(table_obj.schema)
                        
                        # Tentar descobrir colunas ocultas
                        hidden_cols = []
                        if source_table:
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
            # Regex para encontrar FROM `project.dataset.table`
            pattern = r'FROM\s+`[^`]+\.([^`]+)`'
            match = re.search(pattern, view_query, re.IGNORECASE)
            if match:
                return match.group(1)
            return 'Unknown'
        except:
            return 'Unknown'
    
    def get_hidden_columns(self, dataset_id, view_name, source_table):
        """Descobre quais colunas estão ocultas comparando view com tabela origem"""
        try:
            # Schema da view
            view_ref = client.dataset(dataset_id).table(view_name)
            view_obj = client.get_table(view_ref)
            view_cols = {field.name for field in view_obj.schema}
            
            # Schema da tabela origem
            table_ref = client.dataset(dataset_id).table(source_table)
            table_obj = client.get_table(table_ref)
            table_cols = {field.name for field in table_obj.schema}
            
            # Colunas ocultas = na tabela mas não na view
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
        
        # Dialog com detalhes
        with ui.dialog() as details_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'View Details: {view_info["view_name"]}').classes('text-h5 font-bold mb-4')
            
            # Informações gerais
            with ui.card().classes('w-full bg-blue-50 p-3 mb-2'):
                ui.label('📊 General Information:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View name: {view_info["view_name"]}').classes('text-xs')
                ui.label(f'  • Source table: {view_info["source_table"]}').classes('text-xs')
                ui.label(f'  • Visible columns: {view_info["visible_columns"]}').classes('text-xs')
                ui.label(f'  • Hidden columns: {view_info["hidden_columns_count"]}').classes('text-xs')
                ui.label(f'  • Created: {view_info["created"]}').classes('text-xs')
                ui.label(f'  • Modified: {view_info["modified"]}').classes('text-xs')
            
            # Colunas ocultas
            if view_info['hidden_columns']:
                with ui.card().classes('w-full bg-red-50 p-3 mb-2'):
                    ui.label('🚫 Hidden Columns:').classes('font-bold text-sm mb-2')
                    for col in view_info['hidden_columns']:
                        ui.label(f'  • {col}').classes('text-xs')
            else:
                with ui.card().classes('w-full bg-yellow-50 p-3 mb-2'):
                    ui.label('⚠️ No columns hidden (all columns visible in view)').classes('text-sm')
            
            # SQL para consulta
            with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                ui.label('📝 Query Example:').classes('font-bold text-sm mb-2')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.{view_info['view_name']}`;", language='sql').classes('w-full text-xs')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=details_dialog.close).props('flat')
                ui.button('MANAGE COLUMNS', on_click=lambda: [details_dialog.close(), self.manage_columns(view_info)]).props('color=primary')
        
        details_dialog.open()
    
    def manage_columns(self, view_info):
        """Interface para gerenciar colunas ocultas"""
        self.current_view = view_info
        
        # Carregar todas as colunas da tabela origem
        try:
            table_ref = client.dataset(self.selected_dataset).table(view_info['source_table'])
            table_obj = client.get_table(table_ref)
            
            self.source_table_columns = []
            for field in table_obj.schema:
                self.source_table_columns.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            
            self.hidden_columns = list(view_info['hidden_columns'])
            
        except Exception as e:
            ui.notify(f"Error loading source table columns: {e}", type="negative")
            return
        
        # Dialog para gerenciar
        with ui.dialog() as manage_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label(f'Manage Columns: {view_info["view_name"]}').classes('text-h5 font-bold mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('ℹ️ Instructions:').classes('font-bold text-sm mb-2')
                ui.label('• Check columns to HIDE them from the view').classes('text-xs')
                ui.label('• Uncheck columns to make them VISIBLE in the view').classes('text-xs')
                ui.label('• Click SAVE CHANGES to recreate the view with new configuration').classes('text-xs')
            
            # Lista de colunas
            columns_container = ui.column().classes('w-full')
            
            with columns_container:
                ui.label(f'Source table: {view_info["source_table"]} ({len(self.source_table_columns)} columns)').classes('text-sm font-bold mb-2')
                
                with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                    for col in self.source_table_columns:
                        with ui.card().classes('w-full p-3 mb-2'):
                            with ui.row().classes('w-full items-center gap-4'):
                                # Checkbox
                                is_hidden = col['name'] in self.hidden_columns
                                checkbox = ui.checkbox(
                                    text='Hide',
                                    value=is_hidden,
                                    on_change=lambda e, c=col['name']: self.toggle_column_visibility(c, e.value, columns_container)
                                )
                                
                                # Nome e tipo
                                with ui.column().classes('flex-1'):
                                    ui.label(col['name']).classes('font-bold text-base')
                                    ui.label(f"Type: {col['type']}").classes('text-xs text-grey-6')
                                
                                # Status
                                status = 'HIDDEN' if is_hidden else 'VISIBLE'
                                status_label = ui.label(status).classes('text-sm px-3 py-1 rounded')
                                if is_hidden:
                                    status_label.classes('bg-red-100 text-red-600')
                                else:
                                    status_label.classes('bg-green-100 text-green-600')
            
            # Resumo
            with ui.card().classes('w-full bg-purple-50 p-3 mt-4'):
                visible_count = len(self.source_table_columns) - len(self.hidden_columns)
                ui.label(f'📊 Current configuration:').classes('font-bold text-sm mb-2')
                ui.label(f'  • Total columns: {len(self.source_table_columns)}').classes('text-xs')
                ui.label(f'  • Visible in view: {visible_count}').classes('text-xs')
                ui.label(f'  • Hidden from view: {len(self.hidden_columns)}').classes('text-xs')
            
            # Botões
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('CANCEL', on_click=manage_dialog.close).props('flat')
                ui.button(
                    'SAVE CHANGES',
                    icon='save',
                    on_click=lambda: self.save_column_changes(manage_dialog)
                ).props('color=positive')
        
        manage_dialog.open()
    
    def toggle_column_visibility(self, column_name, is_hidden, container):
        """Toggle visibilidade da coluna"""
        if is_hidden and column_name not in self.hidden_columns:
            self.hidden_columns.append(column_name)
        elif not is_hidden and column_name in self.hidden_columns:
            self.hidden_columns.remove(column_name)
    
    def save_column_changes(self, dialog):
        """Salva mudanças e recria a view"""
        if not self.current_view:
            return
        
        # Validação: não pode ocultar todas as colunas
        visible_columns = [col['name'] for col in self.source_table_columns if col['name'] not in self.hidden_columns]
        
        if not visible_columns:
            ui.notify("❌ Cannot hide ALL columns! At least one column must be visible.", type="negative")
            return
        
        try:
            view_name = self.current_view['view_name']
            source_table = self.current_view['source_table']
            
            # Gerar SQL da view
            sql = f"""CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(visible_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{source_table}`;"""
            
            # Executar
            query_job = client.query(sql)
            query_job.result()
            
            # Log audit
            self.audit_service.log_action(
                action='UPDATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='SUCCESS',
                details={
                    'hidden_columns': self.hidden_columns,
                    'visible_columns': visible_columns,
                    'total_columns': len(self.source_table_columns)
                }
            )
            
            ui.notify(f"✅ View '{view_name}' updated successfully!", type="positive")
            dialog.close()
            
            # Refresh
            self.restricted_views = self.get_restricted_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            
        except Exception as e:
            self.audit_service.log_action(
                action='UPDATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error updating view: {e}", type="negative")
    
    async def delete_selected_views(self):
        """Deleta views selecionadas"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No views selected', type="warning")
            return
        
        view_names = [row['view_name'] for row in rows]
        view_list = '\n'.join([f"• {name}" for name in view_names])
        
        # Dialog confirmação
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label(f'Delete {len(view_names)} view(s)?').classes('mb-2')
            ui.label(view_list).classes('text-sm whitespace-pre mb-4')
            ui.label('This action cannot be undone!').classes('text-red-600 font-bold')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'DELETE',
                    on_click=lambda: self.execute_deletion(rows, confirm_dialog)
                ).props('color=negative')
        
        confirm_dialog.open()
    
    def execute_deletion(self, views, dialog):
        """Executa deleção"""
        success = 0
        failed = 0
        
        for view in views:
            try:
                table_ref = client.dataset(self.selected_dataset).table(view['view_name'])
                client.delete_table(table_ref)
                
                # Log audit
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
            ui.notify(f"✅ {success} view(s) deleted successfully", type="positive")
        if failed > 0:
            ui.notify(f"❌ {failed} view(s) failed to delete", type="negative")
        
        # Refresh
        self.restricted_views = self.get_restricted_views(self.selected_dataset)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_all(self):
        """Refresh completo"""
        if self.selected_dataset:
            self.restricted_views = self.get_restricted_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            ui.notify("Refreshed successfully", type="positive")
        else:
            ui.notify("Please select a dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('Manage Dynamic Views'):
            with ui.card().classes('w-full'):
                ui.label("Manage Restricted Views").classes('text-h5 font-bold mb-4')
                
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
                        ui.label('Restricted Views').classes('text-sm text-grey-7')
                        self.total_views_label = ui.label('0').classes('text-3xl font-bold text-blue-600')
                
                # Grid
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
                
                # Botões
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("VIEW DETAILS", icon="info", on_click=self.view_details).props('color=primary')
                    ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_views).props('color=negative')
    
    def run(self):
        pass
