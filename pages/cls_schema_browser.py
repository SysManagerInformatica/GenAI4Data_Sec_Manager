"""
CLS Schema Browser Page
Browse BigQuery schemas and view applied policy tags
"""

from nicegui import ui
import theme
from config import Config
from services.bigquery_cls_service import BigQueryCLSService


class CLSSchemaBrowser:
    def __init__(self):
        self.bigquery_service = BigQueryCLSService(Config.PROJECT_ID)
    
    def run(self):
        with theme.frame('CLS - Schema Browser'):
            ui.label('🔍 Schema Browser').classes('text-3xl font-bold mb-4')
            ui.label('Browse your BigQuery datasets, tables, and columns with applied policy tags').classes('text-gray-600 mb-6')
            
            # Get datasets
            datasets = self.bigquery_service.list_datasets()
            
            if not datasets:
                ui.label('⚠️ No datasets found in this project.').classes('text-gray-500')
                return
            
            # Browse datasets
            for dataset in datasets:
                with ui.expansion(f"📁 {dataset['dataset_id']}", icon='folder').classes('w-full'):
                    with ui.column().classes('gap-2 p-2'):
                        # Dataset info
                        ui.label(f"Location: {dataset['location']}").classes('text-sm text-gray-600')
                        if dataset['description']:
                            ui.label(f"Description: {dataset['description']}").classes('text-sm text-gray-600')
                        ui.label(f"Tables: {dataset['table_count']}").classes('text-sm text-gray-600')
                        
                        ui.separator()
                        
                        # Tables
                        tables = self.bigquery_service.list_tables(dataset['dataset_id'])
                        
                        if tables:
                            for table in tables:
                                with ui.expansion(f"  📊 {table['table_id']}", icon='table_chart').classes('w-full'):
                                    with ui.column().classes('gap-2 p-2'):
                                        # Table info
                                        ui.label(f"Type: {table['table_type']}").classes('text-sm text-gray-600')
                                        ui.label(f"Rows: {table['num_rows']:,}").classes('text-sm text-gray-600')
                                        if table['description']:
                                            ui.label(f"Description: {table['description']}").classes('text-sm text-gray-600')
                                        
                                        ui.separator()
                                        
                                        # Schema
                                        schema = self.bigquery_service.get_table_schema(
                                            dataset['dataset_id'],
                                            table['table_id']
                                        )
                                        
                                        if schema:
                                            # Statistics
                                            stats = self.bigquery_service.get_tagged_columns_count(
                                                dataset['dataset_id'],
                                                table['table_id']
                                            )
                                            
                                            with ui.card().classes('w-full bg-blue-50 mb-2'):
                                                ui.label('Column Statistics').classes('font-bold')
                                                ui.label(f"Total: {stats['total_columns']} | Tagged: {stats['tagged_columns']} ({stats['percentage_tagged']}%)").classes('text-sm')
                                            
                                            # Columns table
                                            columns = [
                                                {'name': 'name', 'label': 'Column', 'field': 'name', 'align': 'left'},
                                                {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
                                                {'name': 'mode', 'label': 'Mode', 'field': 'mode', 'align': 'left'},
                                                {'name': 'tags', 'label': 'Policy Tags', 'field': 'tags', 'align': 'left'},
                                            ]
                                            
                                            rows = []
                                            for col in schema:
                                                tag_display = '🏷️ ' + col['policy_tags'][0] if col['policy_tags'] else '⚪ No tag'
                                                rows.append({
                                                    'name': col['name'],
                                                    'type': col['type'],
                                                    'mode': col['mode'],
                                                    'tags': tag_display
                                                })
                                            
                                            ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')
                        else:
                            ui.label('No tables in this dataset').classes('text-sm text-gray-500')
