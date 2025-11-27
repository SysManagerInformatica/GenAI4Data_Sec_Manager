import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService
import re
from datetime import datetime

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class MaskStatus:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "View Masking Status"
        
        self.selected_dataset = None
        self.views_grid = None
        self.all_views = []
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('View Masking Status').classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        """Lista datasets do projeto"""
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error listing datasets: {e}", type="negative")
            return []
    
    def get_views_in_dataset(self, dataset_id):
        """Lista todas as views em um dataset"""
        try:
            tables = client.list_tables(dataset_id)
            views = []
            
            for table in tables:
                # Verificar se é view
                table_ref = client.dataset(dataset_id).table(table.table_id)
                table_obj = client.get_table(table_ref)
                
                if table_obj.table_type == 'VIEW':
                    # Detectar se é masked view
                    is_masked = self.detect_masked_view(table_obj)
                    
                    views.append({
                        'dataset': dataset_id,
                        'view_name': table.table_id,
                        'is_masked': '✅ Yes' if is_masked else '❌ No',
                        'is_masked_bool': is_masked,
                        'created': table_obj.created.strftime('%Y-%m-%d %H:%M:%S') if table_obj.created else 'N/A',
                        'modified': table_obj.modified.strftime('%Y-%m-%d %H:%M:%S') if table_obj.modified else 'N/A',
                        'num_rows': str(table_obj.num_rows) if table_obj.num_rows else '0',
                        'view_query': table_obj.view_query[:100] + '...' if table_obj.view_query and len(table_obj.view_query) > 100 else table_obj.view_query,
                        'full_view_query': table_obj.view_query
                    })
            
            return views
        except Exception as e:
            ui.notify(f"Error listing views: {e}", type="negative")
            return []
    
    def detect_masked_view(self, table_obj):
        """Detecta se é uma view mascarada analisando a query"""
        if not table_obj.view_query:
            return False
        
        query_lower = table_obj.view_query.lower()
        
        # Heurísticas para detectar mascaramento
        masking_patterns = [
            'sha256',
            'to_base64',
            'hash',
            'round(',
            'concat(substr',
            '***',
            'confidential',
            '_masked'
        ]
        
        for pattern in masking_patterns:
            if pattern in query_lower:
                return True
        
        return False
    
    def on_dataset_change(self, dataset_id):
        """Quando seleciona dataset"""
        self.selected_dataset = dataset_id
        self.all_views = self.get_views_in_dataset(dataset_id)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_views_grid(self):
        """Atualiza grid de views"""
        if self.views_grid and self.all_views:
            self.views_grid.options['rowData'] = self.all_views
            self.views_grid.update()
    
    def update_statistics(self):
        """Atualiza cards de estatísticas"""
        total_views = len(self.all_views)
        masked_views = len([v for v in self.all_views if v['is_masked_bool']])
        regular_views = total_views - masked_views
        
        # Atualizar labels dos cards
        if hasattr(self, 'total_views_label'):
            self.total_views_label.set_text(str(total_views))
        if hasattr(self, 'masked_views_label'):
            self.masked_views_label.set_text(str(masked_views))
        if hasattr(self, 'regular_views_label'):
            self.regular_views_label.set_text(str(regular_views))
    
    async def view_details(self):
        """Mostra detalhes da view selecionada"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No view selected', type="warning")
            return
        
        view = rows[0]
        
        # Dialog com detalhes
        with ui.dialog() as details_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'View Details: {view["view_name"]}').classes('text-h5 font-bold mb-4')
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Info básica
                ui.label('Dataset:').classes('font-bold')
                ui.label(view['dataset'])
                
                ui.label('View Name:').classes('font-bold')
                ui.label(view['view_name'])
                
                ui.label('Is Masked:').classes('font-bold')
                ui.label(view['is_masked'])
                
                ui.label('Created:').classes('font-bold')
                ui.label(view['created'])
                
                ui.label('Last Modified:').classes('font-bold')
                ui.label(view['modified'])
                
                ui.label('Approximate Rows:').classes('font-bold')
                ui.label(view['num_rows'])
            
            # Schema
            ui.separator()
            ui.label('Schema:').classes('text-h6 font-bold mt-4 mb-2')
            schema = self.get_view_schema(view['dataset'], view['view_name'])
            
            with ui.scroll_area().classes('w-full h-40'):
                if schema:
                    for field in schema:
                        ui.label(f"• {field['name']} ({field['type']})").classes('text-sm')
                else:
                    ui.label('No schema information available').classes('text-grey-5')
            
            # View Query
            ui.separator()
            ui.label('View Query:').classes('text-h6 font-bold mt-4 mb-2')
            ui.code(view['full_view_query'] or 'N/A', language='sql').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=details_dialog.close).props('flat')
                ui.button(
                    'Copy Query',
                    on_click=lambda: ui.run_javascript(
                        f'navigator.clipboard.writeText(`{view["full_view_query"]}`)'
                    )
                ).props('color=primary')
        
        details_dialog.open()
    
    def get_view_schema(self, dataset_id, view_name):
        """Obtém schema da view"""
        try:
            table_ref = client.dataset(dataset_id).table(view_name)
            table = client.get_table(table_ref)
            
            schema = []
            for field in table.schema:
                schema.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            return schema
        except Exception as e:
            ui.notify(f"Error getting schema: {e}", type="negative")
            return []
    
    async def delete_selected_views(self):
        """Deleta views selecionadas"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No views selected', type="warning")
            return
        
        # Dialog de confirmação
        view_names = [row['view_name'] for row in rows]
        view_list = '\n'.join([f"• {name}" for name in view_names[:10]])
        if len(view_names) > 10:
            view_list += f"\n... and {len(view_names) - 10} more"
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label(f'You are about to delete {len(view_names)} view(s):').classes('mb-2')
            ui.label(view_list).classes('text-sm whitespace-pre mb-4')
            ui.label('This action cannot be undone!').classes('text-red-600 font-bold')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'DELETE',
                    on_click=lambda: self.execute_view_deletion(rows, confirm_dialog)
                ).props('color=negative')
        
        confirm_dialog.open()
    
    def execute_view_deletion(self, views, dialog):
        """Executa deleção das views"""
        success_count = 0
        fail_count = 0
        
        for view in views:
            try:
                # Deletar view
                table_ref = client.dataset(view['dataset']).table(view['view_name'])
                client.delete_table(table_ref)
                
                # Log audit
                self.audit_service.log_action(
                    action='DELETE_MASKED_VIEW',
                    resource_type='MASKED_VIEW',
                    resource_name=f"{view['dataset']}.{view['view_name']}",
                    status='SUCCESS',
                    details={
                        'dataset': view['dataset'],
                        'view_name': view['view_name'],
                        'was_masked': view['is_masked_bool']
                    }
                )
                
                success_count += 1
                
            except Exception as e:
                # Log failure
                self.audit_service.log_action(
                    action='DELETE_MASKED_VIEW',
                    resource_type='MASKED_VIEW',
                    resource_name=f"{view['dataset']}.{view['view_name']}",
                    status='FAILED',
                    error_message=str(e)
                )
                fail_count += 1
        
        # Fechar dialog
        dialog.close()
        
        # Mensagem de resumo
        if success_count > 0:
            ui.notify(f"✅ {success_count} view(s) deleted successfully", type="positive")
        if fail_count > 0:
            ui.notify(f"❌ {fail_count} view(s) failed to delete", type="negative")
        
        # Refresh grid
        self.all_views = self.get_views_in_dataset(self.selected_dataset)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_all(self):
        """Refresh completo"""
        if self.selected_dataset:
            self.all_views = self.get_views_in_dataset(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            ui.notify("Refreshed successfully", type="positive")
        else:
            ui.notify("Please select a dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('View Masking Status'):
            with ui.card().classes('w-full'):
                ui.label("View Masking Status").classes('text-h5 font-bold mb-4')
                
                # Seletor de dataset
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    datasets = self.get_datasets()
                    ui.select(
                        options=datasets,
                        label='Select Dataset',
                        on_change=lambda e: self.on_dataset_change(e.value)
                    ).classes('flex-1')
                    
                    ui.button('REFRESH', icon='refresh', on_click=self.refresh_all).props('flat')
                
                # Cards de estatísticas
                with ui.row().classes('w-full gap-4 mb-4'):
                    with ui.card().classes('flex-1 bg-blue-50'):
                        ui.label('Total Views').classes('text-sm text-grey-7')
                        self.total_views_label = ui.label('0').classes('text-3xl font-bold text-blue-600')
                    
                    with ui.card().classes('flex-1 bg-purple-50'):
                        ui.label('Masked Views').classes('text-sm text-grey-7')
                        self.masked_views_label = ui.label('0').classes('text-3xl font-bold text-purple-600')
                    
                    with ui.card().classes('flex-1 bg-grey-50'):
                        ui.label('Regular Views').classes('text-sm text-grey-7')
                        self.regular_views_label = ui.label('0').classes('text-3xl font-bold text-grey-600')
                
                # Grid de views
                ui.separator()
                ui.label("Views in Dataset").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'view_name', 'headerName': 'View Name', 'checkboxSelection': True, 'filter': 'agTextColumnFilter', 'minWidth': 250},
                        {'field': 'is_masked', 'headerName': 'Masked', 'filter': 'agSetColumnFilter', 'minWidth': 120},
                        {'field': 'created', 'headerName': 'Created', 'filter': 'agDateColumnFilter', 'minWidth': 180},
                        {'field': 'modified', 'headerName': 'Modified', 'filter': 'agDateColumnFilter', 'minWidth': 180},
                        {'field': 'num_rows', 'headerName': 'Rows', 'filter': 'agNumberColumnFilter', 'minWidth': 120},
                        {'field': 'view_query', 'headerName': 'Query Preview', 'filter': 'agTextColumnFilter', 'minWidth': 300},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                # Botões de ação
                with ui.row().classes('mt-2 gap-2'):
                    ui.button("VIEW DETAILS", icon="info", on_click=self.view_details).props('color=primary')
                    ui.button("DELETE SELECTED", icon="delete", on_click=self.delete_selected_views).props('color=negative')
                
                # Info box
                with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                    ui.label('ℹ️ How views are detected as masked:').classes('text-sm font-bold mb-2')
                    with ui.column().classes('gap-1'):
                        ui.label('• Views with SHA256, TO_BASE64, or hashing functions').classes('text-xs')
                        ui.label('• Views with masking patterns (e.g., ROUND, CONCAT, SUBSTR)').classes('text-xs')
                        ui.label('• Views with keywords like "masked", "confidential", or "***"').classes('text-xs')
                        ui.label('• View names containing "_masked" suffix').classes('text-xs')
    
    def run(self):
        pass  # Já renderizado no __init__
