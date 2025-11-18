"""
CLS Apply Tags Page
Apply policy tags to BigQuery table columns
"""

from nicegui import ui
import theme
from config import Config
from services.datacatalog_service import DataCatalogService
from services.bigquery_cls_service import BigQueryCLSService
from services.audit_service import AuditService


class CLSApplyTags:
    def __init__(self):
        self.datacatalog_service = DataCatalogService(Config.PROJECT_ID, Config.LOCATION)
        self.bigquery_service = BigQueryCLSService(Config.PROJECT_ID)
        self.audit_service = AuditService(Config.PROJECT_ID)
        self.columns_container = None
        self.selected_dataset = None
        self.selected_table = None
        self.all_tags = []
    
    def run(self):
        with theme.frame('CLS - Apply Tags to Columns'):
            ui.label('🔧 Apply Tags to Columns').classes('text-3xl font-bold mb-4')
            ui.label('Select a table and apply policy tags to sensitive columns').classes('text-gray-600 mb-6')
            
            # Get datasets
            datasets = self.bigquery_service.list_datasets()
            
            if not datasets:
                ui.label('⚠️ No datasets found in this project.').classes('text-gray-500')
                return
            
            # Selectors
            with ui.column().classes('gap-4 mb-4'):
                # Dataset selector
                with ui.row().classes('items-center gap-2'):
                    ui.label('Dataset:').classes('font-bold w-24')
                    dataset_select = ui.select(
                        options=[ds['dataset_id'] for ds in datasets],
                        label='Select dataset',
                        on_change=lambda e: self.on_dataset_change(e.value)
                    ).classes('w-64')
                
                # Table selector
                with ui.row().classes('items-center gap-2'):
                    ui.label('Table:').classes('font-bold w-24')
                    self.table_select = ui.select(
                        options=[],
                        label='Select table',
                        on_change=lambda e: self.on_table_change(e.value)
                    ).classes('w-64')
            
            # Container for columns
            self.columns_container = ui.column().classes('gap-4 w-full')
            
            # Load all available tags
            self.load_all_tags()
    
    def load_all_tags(self):
        """Load all policy tags from all taxonomies"""
        self.all_tags = []
        taxonomies = self.datacatalog_service.list_taxonomies()
        
        for tax in taxonomies:
            tags = self.datacatalog_service.list_policy_tags(tax['name'])
            for tag in tags:
                self.all_tags.append({
                    'display': f"{tax['display_name']} > {tag['display_name']}",
                    'value': tag['name'],
                    'taxonomy': tax['display_name'],
                    'tag': tag['display_name']
                })
    
    def on_dataset_change(self, dataset_id):
        """Handle dataset selection change"""
        self.selected_dataset = dataset_id
        self.selected_table = None
        self.columns_container.clear()
        
        # Load tables
        tables = self.bigquery_service.list_tables(dataset_id)
        self.table_select.options = [t['table_id'] for t in tables]
        self.table_select.update()
    
    def on_table_change(self, table_id):
        """Handle table selection change"""
        self.selected_table = table_id
        self.refresh_columns()
    
    def refresh_columns(self):
        """Refresh the columns list with their current tags"""
        if not self.selected_dataset or not self.selected_table:
            return
        
        self.columns_container.clear()
        
        with self.columns_container:
            # Get statistics
            stats = self.bigquery_service.get_tagged_columns_count(
                self.selected_dataset,
                self.selected_table
            )
            
            # Show statistics
            with ui.card().classes('w-full bg-blue-50'):
                ui.label(f'📊 Table Statistics').classes('text-lg font-bold')
                with ui.row().classes('gap-8 mt-2'):
                    ui.label(f'Total Columns: {stats["total_columns"]}').classes('font-bold')
                    ui.label(f'Tagged: {stats["tagged_columns"]}').classes('text-green-600 font-bold')
                    ui.label(f'Untagged: {stats["untagged_columns"]}').classes('text-orange-600 font-bold')
                    ui.label(f'Coverage: {stats["percentage_tagged"]}%').classes('text-blue-600 font-bold')
            
            ui.separator()
            
            # Get schema
            schema = self.bigquery_service.get_table_schema(
                self.selected_dataset,
                self.selected_table
            )
            
            if schema:
                ui.label(f'📋 Columns in {self.selected_table}').classes('text-xl font-bold mb-2')
                
                for column in schema:
                    with ui.card().classes('w-full'):
                        with ui.row().classes('items-center gap-4 w-full'):
                            # Column info
                            with ui.column().classes('flex-grow'):
                                ui.label(column['name']).classes('text-lg font-bold')
                                ui.label(f"Type: {column['type']} | Mode: {column['mode']}").classes('text-sm text-gray-600')
                                if column['description']:
                                    ui.label(f"📝 {column['description']}").classes('text-sm text-gray-500')
                                if column['policy_tags']:
                                    ui.label(f"🏷️ Current tag: {column['policy_tags'][0]}").classes('text-sm text-blue-600 font-bold')
                            
                            # Tag selector and actions
                            with ui.row().classes('gap-2 items-center'):
                                tag_select = ui.select(
                                    options=[t['display'] for t in self.all_tags],
                                    label='Select tag',
                                    value=self.find_tag_display(column['policy_tags'][0]) if column['policy_tags'] else None
                                ).classes('w-80')
                                
                                # Apply button
                                def make_apply_handler(col, sel):
                                    def apply_tag():
                                        if not sel.value:
                                            ui.notify('⚠️ Please select a tag', type='warning')
                                            return
                                        
                                        selected_tag = next((t for t in self.all_tags if t['display'] == sel.value), None)
                                        if selected_tag:
                                            try:
                                                result = self.bigquery_service.apply_tag_to_column(
                                                    self.selected_dataset,
                                                    self.selected_table,
                                                    col['name'],
                                                    selected_tag['value']
                                                )
                                                
                                                if result:
                                                    # Log success
                                                    self.audit_service.log_action(
                                                        action='APPLY_TAG',
                                                        resource_type='COLUMN',
                                                        resource_name=f"{self.selected_table}.{col['name']} → {selected_tag['display']}",
                                                        status='SUCCESS',
                                                        taxonomy=selected_tag['taxonomy'],
                                                        details={
                                                            'dataset': self.selected_dataset,
                                                            'table': self.selected_table,
                                                            'column': col['name'],
                                                            'tag': selected_tag['display'],
                                                            'tag_path': selected_tag['value']
                                                        }
                                                    )
                                                    
                                                    ui.notify(f'✅ Tag applied to {col["name"]}!', type='positive')
                                                    self.refresh_columns()
                                                else:
                                                    # Log failure
                                                    self.audit_service.log_action(
                                                        action='APPLY_TAG',
                                                        resource_type='COLUMN',
                                                        resource_name=f"{self.selected_table}.{col['name']}",
                                                        status='FAILED',
                                                        taxonomy=selected_tag['taxonomy'],
                                                        error_message='Unknown error applying tag'
                                                    )
                                                    ui.notify('❌ Error applying tag', type='negative')
                                            
                                            except Exception as e:
                                                # Log exception
                                                self.audit_service.log_action(
                                                    action='APPLY_TAG',
                                                    resource_type='COLUMN',
                                                    resource_name=f"{self.selected_table}.{col['name']}",
                                                    status='FAILED',
                                                    error_message=str(e)
                                                )
                                                ui.notify(f'❌ Error: {str(e)}', type='negative')
                                    return apply_tag
                                
                                ui.button('Apply', 
                                         on_click=make_apply_handler(column, tag_select),
                                         icon='check').props('color=positive')
                                
                                # Remove button (if has tag)
                                if column['policy_tags']:
                                    def make_remove_handler(col):
                                        def remove_tag():
                                            try:
                                                # Get current tag info before removing
                                                current_tag_display = self.find_tag_display(col['policy_tags'][0])
                                                current_tag_obj = next((t for t in self.all_tags if t['value'] == col['policy_tags'][0]), None)
                                                
                                                result = self.bigquery_service.remove_tag_from_column(
                                                    self.selected_dataset,
                                                    self.selected_table,
                                                    col['name']
                                                )
                                                
                                                if result:
                                                    # Log success
                                                    self.audit_service.log_action(
                                                        action='REMOVE_TAG',
                                                        resource_type='COLUMN',
                                                        resource_name=f"{self.selected_table}.{col['name']}",
                                                        status='SUCCESS',
                                                        taxonomy=current_tag_obj['taxonomy'] if current_tag_obj else None,
                                                        details={
                                                            'dataset': self.selected_dataset,
                                                            'table': self.selected_table,
                                                            'column': col['name'],
                                                            'removed_tag': current_tag_display
                                                        }
                                                    )
                                                    
                                                    ui.notify(f'✅ Tag removed from {col["name"]}!', type='positive')
                                                    self.refresh_columns()
                                                else:
                                                    # Log failure
                                                    self.audit_service.log_action(
                                                        action='REMOVE_TAG',
                                                        resource_type='COLUMN',
                                                        resource_name=f"{self.selected_table}.{col['name']}",
                                                        status='FAILED',
                                                        error_message='Unknown error removing tag'
                                                    )
                                                    ui.notify('❌ Error removing tag', type='negative')
                                            
                                            except Exception as e:
                                                # Log exception
                                                self.audit_service.log_action(
                                                    action='REMOVE_TAG',
                                                    resource_type='COLUMN',
                                                    resource_name=f"{self.selected_table}.{col['name']}",
                                                    status='FAILED',
                                                    error_message=str(e)
                                                )
                                                ui.notify(f'❌ Error: {str(e)}', type='negative')
                                        return remove_tag
                                    
                                    ui.button('Remove', 
                                             on_click=make_remove_handler(column),
                                             icon='delete').props('flat color=negative')
            else:
                ui.label('⚠️ No columns found in this table.').classes('text-gray-500')
    
    def find_tag_display(self, tag_name):
        """Find the display name for a tag"""
        if not tag_name:
            return None
        tag = next((t for t in self.all_tags if t['value'] == tag_name), None)
        return tag['display'] if tag else None
