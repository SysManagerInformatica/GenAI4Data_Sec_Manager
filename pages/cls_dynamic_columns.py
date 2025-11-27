import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from services.audit_service import AuditService

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DynamicColumnSecurity:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Dynamic Column Security"
        
        self.selected_dataset = None
        self.selected_table = None
        self.table_columns = []
        self.hidden_columns = []  # Lista de colunas a serem OCULTAS
        self.apply_policy_tags = False
        self.selected_policy_tag = None
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Dynamic Column Security').classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        """Lista datasets do projeto"""
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error listing datasets: {e}", type="negative")
            return []
    
    def get_tables(self, dataset_id):
        """Lista tabelas do dataset"""
        try:
            tables = client.list_tables(dataset_id)
            return [table.table_id for table in tables]
        except Exception as e:
            ui.notify(f"Error listing tables: {e}", type="negative")
            return []
    
    def get_table_schema(self, dataset_id, table_id):
        """Obtém schema da tabela"""
        try:
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)
            
            columns = []
            for field in table.schema:
                columns.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            return columns
        except Exception as e:
            ui.notify(f"Error getting schema: {e}", type="negative")
            return []
    
    def get_policy_tags(self):
        """Lista policy tags disponíveis"""
        try:
            from google.cloud import datacatalog_v1
            
            policy_client = datacatalog_v1.PolicyTagManagerClient()
            location = "us-central1"
            
            parent = f"projects/{self.project_id}/locations/{location}"
            taxonomies = policy_client.list_taxonomies(parent=parent)
            
            tags = {}
            for taxonomy in taxonomies:
                policy_tags = policy_client.list_policy_tags(parent=taxonomy.name)
                for tag in policy_tags:
                    tags[tag.display_name] = tag.name
            
            return tags
        except Exception as e:
            print(f"Error getting policy tags: {e}")
            return {}
    
    def on_dataset_change(self, dataset_id):
        """Quando seleciona dataset"""
        self.selected_dataset = dataset_id
        tables = self.get_tables(dataset_id)
        self.table_select.options = tables
        self.table_select.value = None
        self.table_select.update()
    
    def on_table_change(self, table_id):
        """Quando seleciona tabela"""
        self.selected_table = table_id
        self.table_columns = self.get_table_schema(self.selected_dataset, table_id)
        self.hidden_columns = []
    
    def render_columns_selection(self):
        """Renderiza seleção de colunas para ocultar"""
        if not self.columns_container or not self.table_columns:
            return
        
        self.columns_container.clear()
        
        with self.columns_container:
            ui.label(f"Select columns to HIDE in the view ({len(self.table_columns)} columns available):").classes('text-sm font-bold mb-2')
            
            with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                for col in self.table_columns:
                    with ui.card().classes('w-full p-3 mb-2'):
                        with ui.row().classes('w-full items-center gap-4'):
                            # Checkbox para ocultar
                            checkbox = ui.checkbox(
                                text='',
                                value=col['name'] in self.hidden_columns,
                                on_change=lambda e, c=col['name']: self.toggle_hidden_column(c, e.value)
                            )
                            
                            # Nome e tipo da coluna
                            with ui.column().classes('flex-1'):
                                ui.label(col['name']).classes('font-bold text-base')
                                ui.label(f"Type: {col['type']}").classes('text-xs text-grey-6')
                            
                            # Status
                            status_label = ui.label('Visible' if col['name'] not in self.hidden_columns else 'Hidden')
                            status_label.classes('text-sm px-3 py-1 rounded')
                            if col['name'] in self.hidden_columns:
                                status_label.classes('bg-red-100 text-red-600')
                            else:
                                status_label.classes('bg-green-100 text-green-600')
    
    def toggle_hidden_column(self, column_name, is_hidden):
        """Toggle coluna oculta"""
        if is_hidden and column_name not in self.hidden_columns:
            self.hidden_columns.append(column_name)
            ui.notify(f"Column '{column_name}' will be HIDDEN", type="info")
        elif not is_hidden and column_name in self.hidden_columns:
            self.hidden_columns.remove(column_name)
            ui.notify(f"Column '{column_name}' will be VISIBLE", type="info")
        
        # Refresh display
        self.render_columns_selection()
    
    def generate_view_sql(self):
        """Gera SQL da view"""
        if not self.selected_dataset or not self.selected_table:
            ui.notify("Please select dataset and table first", type="warning")
            return
        
        if not self.hidden_columns:
            ui.notify("⚠️ No columns selected to hide! View will have all columns.", type="warning")
        
        # Colunas visíveis (todas MENOS as ocultas)
        visible_columns = [col['name'] for col in self.table_columns if col['name'] not in self.hidden_columns]
        
        if not visible_columns:
            ui.notify("❌ Cannot hide ALL columns!", type="negative")
            return
        
        view_name = f"vw_{self.selected_table}_restricted"
        
        sql = f"""-- Restricted view for {self.selected_table}
-- Hidden columns: {', '.join(self.hidden_columns) if self.hidden_columns else 'none'}
-- Created: {self.get_current_timestamp()}
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(visible_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`;"""
        
        # Mostrar dialog
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label('Generated SQL').classes('text-h6 font-bold mb-4')
            
            # Resumo
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('📊 View Summary:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View name: {view_name}').classes('text-xs')
                ui.label(f'  • Visible columns: {len(visible_columns)}').classes('text-xs')
                ui.label(f'  • Hidden columns: {len(self.hidden_columns)}').classes('text-xs')
            
            if self.hidden_columns:
                with ui.card().classes('w-full bg-red-50 p-3 mb-4'):
                    ui.label('🚫 Columns HIDDEN from view:').classes('font-bold text-sm mb-2')
                    for col in self.hidden_columns:
                        ui.label(f'  • {col}').classes('text-xs')
            
            ui.code(sql, language='sql').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('Copy SQL', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{sql}`)')).props('color=primary')
        
        sql_dialog.open()
        self.generated_sql = sql
    
    def create_view(self):
        """Cria a view no BigQuery"""
        if not hasattr(self, 'generated_sql'):
            ui.notify("Please generate SQL first", type="warning")
            return
        
        try:
            # Criar view
            query_job = client.query(self.generated_sql)
            query_job.result()
            
            view_name = f"vw_{self.selected_table}_restricted"
            
            # Aplicar Policy Tags se solicitado
            if self.apply_policy_tags and self.selected_policy_tag and self.hidden_columns:
                self.apply_tags_to_hidden_columns(view_name)
            
            # Log audit
            self.audit_service.log_action(
                action='CREATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='SUCCESS',
                details={
                    'source_table': f"{self.selected_dataset}.{self.selected_table}",
                    'view_name': view_name,
                    'hidden_columns': self.hidden_columns,
                    'visible_columns': len(self.table_columns) - len(self.hidden_columns),
                    'policy_tags_applied': self.apply_policy_tags
                }
            )
            
            ui.notify(f"✅ View '{view_name}' created successfully!", type="positive")
            
            # Mostrar guia de uso
            self.show_usage_guide()
            
        except Exception as e:
            self.audit_service.log_action(
                action='CREATE_RESTRICTED_VIEW',
                resource_type='RESTRICTED_VIEW',
                resource_name=f"{self.selected_dataset}.vw_{self.selected_table}_restricted",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error creating view: {e}", type="negative")
    
    def apply_tags_to_hidden_columns(self, view_name):
        """Aplica Policy Tags nas colunas que ainda existem na view (proteção extra)"""
        try:
            # Aqui você pode implementar lógica adicional se necessário
            # Por enquanto, apenas notifica
            ui.notify("ℹ️ Policy Tags feature can be configured separately", type="info")
        except Exception as e:
            print(f"Error applying policy tags: {e}")
    
    def show_usage_guide(self):
        """Mostra guia de uso"""
        with ui.dialog() as guide_dialog, ui.card().classes('w-full max-w-3xl'):
            ui.label('✅ View Created Successfully!').classes('text-h5 font-bold text-green-600 mb-4')
            
            view_name = f"vw_{self.selected_table}_restricted"
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('📊 View Information:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View name: {view_name}').classes('text-xs')
                ui.label(f'  • Visible columns: {len(self.table_columns) - len(self.hidden_columns)}').classes('text-xs')
                ui.label(f'  • Hidden columns: {len(self.hidden_columns)}').classes('text-xs')
            
            with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                ui.label('👑 Full Access (use original table):').classes('font-bold text-sm mb-1')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.{self.selected_table}`;", language='sql').classes('w-full text-xs')
                ui.label('→ See ALL columns including hidden ones').classes('text-xs text-grey-7 mt-1')
            
            with ui.card().classes('w-full bg-orange-50 p-3 mb-2'):
                ui.label('👁️ Restricted Access (use view):').classes('font-bold text-sm mb-1')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.{view_name}`;", language='sql').classes('w-full text-xs')
                ui.label(f'→ See only {len(self.table_columns) - len(self.hidden_columns)} columns (hidden columns not accessible)').classes('text-xs text-grey-7 mt-1')
            
            if self.hidden_columns:
                with ui.card().classes('w-full bg-red-50 p-3 mb-4'):
                    ui.label('🚫 Hidden Columns:').classes('font-bold text-sm mb-2')
                    for col in self.hidden_columns:
                        ui.label(f'  • {col}').classes('text-xs')
            
            with ui.card().classes('w-full bg-yellow-50 p-3 mt-4'):
                ui.label('ℹ️ Management:').classes('text-sm font-bold mb-1')
                ui.label('• To modify hidden columns, use "Manage Dynamic Views"').classes('text-xs')
                ui.label('• To delete this view, use "Manage Dynamic Views"').classes('text-xs')
                ui.label('• Original table remains unchanged').classes('text-xs')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=guide_dialog.close).props('color=primary')
        
        guide_dialog.open()
    
    def get_current_timestamp(self):
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def render_ui(self):
        with theme.frame('Dynamic Column Security'):
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                # STEP 1: Select Source
                with ui.step('Select Source Table'):
                    ui.label('Choose the table to create a restricted view').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        datasets = self.get_datasets()
                        ui.select(
                            options=datasets,
                            label='Dataset',
                            on_change=lambda e: self.on_dataset_change(e.value)
                        ).classes('flex-1')
                        
                        self.table_select = ui.select(
                            options=[],
                            label='Table',
                            on_change=lambda e: self.on_table_change(e.value)
                        ).classes('flex-1')
                    
                    with ui.stepper_navigation():
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 2: Select Columns to Hide
                with ui.step('Select Columns to Hide'):
                    ui.label('Check the columns you want to HIDE from the view').classes('text-caption mb-4')
                    
                    self.columns_container = ui.column().classes('w-full')
                    
                    # Info box
                    with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                        ui.label('ℹ️ How it works:').classes('text-sm font-bold mb-2')
                        with ui.column().classes('gap-1'):
                            ui.label('• Checked columns will be HIDDEN (not in view)').classes('text-xs')
                            ui.label('• Unchecked columns will be VISIBLE (in view)').classes('text-xs')
                            ui.label('• Original table remains unchanged').classes('text-xs')
                            ui.label('• Users with full access use the original table').classes('text-xs')
                            ui.label('• Restricted users use the view').classes('text-xs')
                    
                    # Botão para carregar colunas
                    ui.button(
                        'LOAD COLUMNS',
                        icon='refresh',
                        on_click=self.render_columns_selection
                    ).props('color=primary').classes('mt-2')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 3: Review and Create
                with ui.step('Review and Create'):
                    ui.label('Review configuration and create restricted view').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        ui.button('GENERATE SQL', icon='code', on_click=self.generate_view_sql).props('color=blue')
                        ui.button('CREATE VIEW', icon='check_circle', on_click=self.create_view).props('color=positive')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
    
    def run(self):
        pass
