import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from services.audit_service import AuditService

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class MaskCreateView:

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Create Masked View"
        
        self.selected_dataset = None
        self.selected_table = None
        self.table_columns = []
        self.masking_config = {}  # {column_name: mask_type}
        self.column_selects = {}  # {column_name: ui.select object}
        self.authorized_users = []
        self.view_name = None
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Create Masked View').classes('text-primary text-center text-bold')
    
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
                    'mode': field.mode,
                    'description': field.description or ''
                })
            return columns
        except Exception as e:
            ui.notify(f"Error getting schema: {e}", type="negative")
            return []
    
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
        
        # Sugerir nome para view
        self.view_name_input.value = f"vw_{table_id}_masked"
        
        # Limpar configuração anterior
        self.masking_config = {}
        self.column_selects = {}
        
        # Renderizar colunas
        self.render_columns_config()
    
    def render_columns_config(self):
        """Renderiza interface de configuração de colunas"""
        if not self.columns_container or not self.table_columns:
            return
        
        self.columns_container.clear()
        
        with self.columns_container:
            ui.label(f"Configure masking for {len(self.table_columns)} columns:").classes('text-sm font-bold mb-2')
            
            # Criar um card scrollable com todas as colunas
            with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                for col in self.table_columns:
                    with ui.card().classes('w-full p-3 mb-2'):
                        with ui.row().classes('w-full items-center gap-4'):
                            # Nome e tipo da coluna
                            with ui.column().classes('flex-1'):
                                ui.label(col['name']).classes('font-bold text-base')
                                ui.label(f"Type: {col['type']}").classes('text-xs text-grey-6')
                            
                            # Seletor de masking type
                            mask_select = ui.select(
                                options={
                                    'none': 'No masking (real data)',
                                    'hash': 'Hash SHA256',
                                    'null': 'NULL',
                                    'partial': 'Partial (first/last chars)',
                                    'round': 'Round (numbers only)',
                                    'default': 'Default value (***)'
                                },
                                value='none',
                                label='Masking Type',
                                on_change=lambda e, c=col['name']: self.update_masking_config(c, e.value)
                            ).classes('w-64')
                            
                            # Guardar referência
                            self.column_selects[col['name']] = mask_select
                            
                            # Preview
                            preview_label = ui.label(self.get_mask_preview(col['name'], col['type'], 'none'))
                            preview_label.classes('text-sm text-grey-7 w-48')
                            
                            # Atualizar preview quando mudar
                            mask_select.on('update:model-value', lambda e, c=col['name'], t=col['type'], p=preview_label: 
                                p.set_text(self.get_mask_preview(c, t, e.args)))
    
    def update_masking_config(self, column_name, mask_type):
        """Atualiza configuração de mascaramento"""
        self.masking_config[column_name] = mask_type
        ui.notify(f"Masking '{mask_type}' set for column '{column_name}'", type="info")
    
    def get_mask_preview(self, column_name, data_type, mask_type):
        """Retorna preview do mascaramento"""
        if mask_type == 'none':
            return '→ Real data'
        elif mask_type == 'hash':
            return '→ 8d969eef6ecad3c2...'
        elif mask_type == 'null':
            return '→ NULL'
        elif mask_type == 'partial':
            return '→ 123.XXX.XXX-10'
        elif mask_type == 'round':
            return '→ 80000.00 (rounded)'
        elif mask_type == 'default':
            return '→ ***CONFIDENTIAL***'
        else:
            return '→ Real data'
    
    def add_authorized_user(self):
        """Adiciona usuário autorizado"""
        email = self.user_email_input.value.strip()
        if email and '@' in email:
            if email not in self.authorized_users:
                self.authorized_users.append(email)
                self.refresh_authorized_users_list()
                self.user_email_input.value = ''
                ui.notify(f"User {email} added to authorized list", type="positive")
            else:
                ui.notify("User already in list", type="warning")
        else:
            ui.notify("Invalid email", type="warning")
    
    def remove_authorized_user(self, email):
        """Remove usuário autorizado"""
        if email in self.authorized_users:
            self.authorized_users.remove(email)
            self.refresh_authorized_users_list()
            ui.notify(f"User {email} removed", type="info")
    
    def refresh_authorized_users_list(self):
        """Atualiza lista de usuários autorizados"""
        if self.authorized_users_container:
            self.authorized_users_container.clear()
            with self.authorized_users_container:
                if not self.authorized_users:
                    ui.label("No authorized users added yet").classes('text-grey-5 italic')
                else:
                    for email in self.authorized_users:
                        with ui.row().classes('w-full items-center justify-between p-2 border rounded'):
                            ui.label(email).classes('flex-1')
                            ui.button(
                                icon='delete',
                                on_click=lambda e=email: self.remove_authorized_user(e)
                            ).props('flat dense color=negative')
    
    def generate_sql(self):
        """Gera SQL da view mascarada"""
        if not self.selected_dataset or not self.selected_table:
            ui.notify("Please select dataset and table first", type="warning")
            return
        
        view_name = self.view_name_input.value.strip()
        if not view_name:
            ui.notify("Please enter view name", type="warning")
            return
        
        # Construir SELECT statement
        select_columns = []
        for col in self.table_columns:
            col_name = col['name']
            col_type = col['type']
            mask_type = self.masking_config.get(col_name, 'none')
            
            if mask_type == 'none':
                # Sem mascaramento
                select_columns.append(f"{col_name}")
            elif mask_type == 'hash':
                # Hash SHA256
                select_columns.append(f"TO_BASE64(SHA256(CAST({col_name} AS STRING))) AS {col_name}")
            elif mask_type == 'null':
                # NULL
                select_columns.append(f"NULL AS {col_name}")
            elif mask_type == 'partial':
                # Mascaramento parcial
                select_columns.append(f"CONCAT(SUBSTR(CAST({col_name} AS STRING), 1, 3), '.XXX.XXX-', SUBSTR(CAST({col_name} AS STRING), -2)) AS {col_name}")
            elif mask_type == 'round':
                # Arredondamento (para números)
                if col_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'BIGNUMERIC', 'INT64', 'FLOAT64']:
                    select_columns.append(f"ROUND({col_name} / 10000) * 10000 AS {col_name}")
                else:
                    select_columns.append(f"{col_name}  -- Cannot round non-numeric type")
            elif mask_type == 'default':
                # Valor padrão
                select_columns.append(f"'***CONFIDENTIAL***' AS {col_name}")
        
        # Montar SQL completo - ✅ CORREÇÃO APLICADA AQUI
        sql = f"""-- Masked view for {self.selected_table}
-- Created: {self.get_current_timestamp()}
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(select_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`;"""
        
        # Mostrar SQL no dialog
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label('Generated SQL').classes('text-h6 font-bold mb-4')
            
            # Resumo de mascaramento
            masked_cols = [k for k, v in self.masking_config.items() if v != 'none']
            if masked_cols:
                with ui.card().classes('w-full bg-purple-50 p-3 mb-4'):
                    ui.label(f'✅ {len(masked_cols)} column(s) will be masked:').classes('font-bold text-sm mb-1')
                    for col in masked_cols[:5]:
                        ui.label(f'  • {col} → {self.masking_config[col]}').classes('text-xs')
                    if len(masked_cols) > 5:
                        ui.label(f'  ... and {len(masked_cols) - 5} more').classes('text-xs')
            else:
                with ui.card().classes('w-full bg-orange-50 p-3 mb-4'):
                    ui.label('⚠️ No columns are being masked! All columns will show real data.').classes('font-bold text-sm text-orange-600')
            
            ui.code(sql, language='sql').classes('w-full')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('Copy SQL', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{sql}`)')).props('color=primary')
        
        sql_dialog.open()
        
        # Guardar SQL para criação
        self.generated_sql = sql
    
    def get_current_timestamp(self):
        """Retorna timestamp atual"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def create_view(self):
        """Cria a view no BigQuery"""
        if not hasattr(self, 'generated_sql'):
            ui.notify("Please generate SQL first", type="warning")
            return
        
        # Verificar se pelo menos uma coluna está sendo mascarada
        masked_cols = [k for k, v in self.masking_config.items() if v != 'none']
        if not masked_cols:
            with ui.dialog() as warning_dialog, ui.card():
                ui.label('⚠️ Warning').classes('text-h6 font-bold text-orange-600 mb-4')
                ui.label('You are creating a view without any masked columns!').classes('mb-2')
                ui.label('All data will be shown as real data.').classes('mb-4')
                ui.label('Do you want to continue?').classes('font-bold')
                
                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Cancel', on_click=warning_dialog.close).props('flat')
                    ui.button('Continue Anyway', on_click=lambda: [warning_dialog.close(), self.execute_create_view()]).props('color=orange')
            
            warning_dialog.open()
            return
        
        self.execute_create_view()
    
    def execute_create_view(self):
        """Executa criação da view"""
        try:
            # Executar SQL
            query_job = client.query(self.generated_sql)
            query_job.result()
            
            view_name = self.view_name_input.value.strip()
            
            # Log audit
            self.audit_service.log_action(
                action='CREATE_MASKED_VIEW',
                resource_type='MASKED_VIEW',
                resource_name=f"{self.selected_dataset}.{view_name}",
                status='SUCCESS',
                details={
                    'source_table': f"{self.selected_dataset}.{self.selected_table}",
                    'view_name': view_name,
                    'masked_columns': {k: v for k, v in self.masking_config.items() if v != 'none'},
                    'total_columns': len(self.table_columns),
                    'masked_count': len([v for v in self.masking_config.values() if v != 'none']),
                    'authorized_users': self.authorized_users
                }
            )
            
            ui.notify(f"✅ Masked view '{view_name}' created successfully!", type="positive")
            
        except Exception as e:
            # Log failure
            self.audit_service.log_action(
                action='CREATE_MASKED_VIEW',
                resource_type='MASKED_VIEW',
                resource_name=f"{self.selected_dataset}.{self.view_name_input.value}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error creating view: {e}", type="negative")
    
    def render_ui(self):
        with theme.frame('Create Masked View'):
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                # STEP 1: Select Source
                with ui.step('Select Source Table'):
                    ui.label('Choose the table you want to create a masked view from').classes('text-caption mb-4')
                    
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
                
                # STEP 2: Configure Masking
                with ui.step('Configure Masking'):
                    ui.label('Select masking type for each column').classes('text-caption mb-4')
                    
                    # Container para colunas
                    self.columns_container = ui.column().classes('w-full')
                    
                    # Info sobre tipos de masking
                    with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                        ui.label('ℹ️ Masking Types:').classes('text-sm font-bold mb-2')
                        with ui.column().classes('gap-1'):
                            ui.label('• none: No masking (real data)').classes('text-xs')
                            ui.label('• hash: SHA256 hash (consistent, one-way)').classes('text-xs')
                            ui.label('• null: Returns NULL').classes('text-xs')
                            ui.label('• partial: Shows first and last characters only').classes('text-xs')
                            ui.label('• round: Rounds numbers to nearest 10,000').classes('text-xs')
                            ui.label('• default: Returns fixed string "***CONFIDENTIAL***"').classes('text-xs')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 3: Name View
                with ui.step('Name Masked View'):
                    ui.label('Enter name for the masked view').classes('text-caption mb-4')
                    
                    self.view_name_input = ui.input(
                        label='View Name',
                        placeholder='vw_table_masked'
                    ).classes('w-full')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 4: Review and Create
                with ui.step('Review and Create'):
                    ui.label('Review configuration and create masked view').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        ui.button('GENERATE SQL', icon='code', on_click=self.generate_sql).props('color=blue')
                        ui.button('CREATE VIEW', icon='check_circle', on_click=self.create_view).props('color=positive')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
    
    def run(self):
        pass  # Já renderizado no __init__
