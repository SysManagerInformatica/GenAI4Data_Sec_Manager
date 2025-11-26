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
        
        # Atualizar grid de colunas
        self.refresh_columns_grid()
    
    def refresh_columns_grid(self):
        """Atualiza grid de colunas"""
        if self.columns_grid and self.table_columns:
            # Adicionar informação de masking type
            grid_data = []
            for col in self.table_columns:
                mask_type = self.masking_config.get(col['name'], 'none')
                grid_data.append({
                    'column_name': col['name'],
                    'data_type': col['type'],
                    'mask_type': mask_type,
                    'preview': self.get_mask_preview(col['name'], col['type'], mask_type)
                })
            
            self.columns_grid.options['rowData'] = grid_data
            self.columns_grid.update()
    
    def get_mask_preview(self, column_name, data_type, mask_type):
        """Retorna preview do mascaramento"""
        previews = {
            'none': 'Real data',
            'hash': '8d969eef6ecad3c2...',
            'null': 'NULL',
            'partial': '123.XXX.XXX-10',
            'round': '80000.00 (rounded)',
            'default': '***CONFIDENTIAL***'
        }
        return previews.get(mask_type, 'Real data')
    
    def apply_mask_to_column(self, column_name, mask_type):
        """Aplica tipo de mask em uma coluna"""
        self.masking_config[column_name] = mask_type
        self.refresh_columns_grid()
        ui.notify(f"Masking '{mask_type}' applied to column '{column_name}'", type="positive")
    
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
            mask_type = self.masking_config.get(col_name, 'none')
            
            if mask_type == 'none':
                # Sem mascaramento
                select_columns.append(f"  {col_name}")
            elif mask_type == 'hash':
                # Hash SHA256
                select_columns.append(f"  TO_BASE64(SHA256(CAST({col_name} AS STRING))) AS {col_name}")
            elif mask_type == 'null':
                # NULL
                select_columns.append(f"  NULL AS {col_name}")
            elif mask_type == 'partial':
                # Mascaramento parcial (primeiros e últimos caracteres)
                select_columns.append(f"  CONCAT(SUBSTR(CAST({col_name} AS STRING), 1, 3), '***', SUBSTR(CAST({col_name} AS STRING), -2)) AS {col_name}")
            elif mask_type == 'round':
                # Arredondamento (para números)
                select_columns.append(f"  ROUND({col_name} / 10000) * 10000 AS {col_name}")
            elif mask_type == 'default':
                # Valor padrão
                select_columns.append(f"  '***CONFIDENTIAL***' AS {col_name}")
        
        # Montar SQL completo
        sql = f"""-- Masked view for {self.selected_table}
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{view_name}` AS
SELECT
{chr(10).join(select_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`;"""
        
        # Mostrar SQL no dialog
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label('Generated SQL').classes('text-h6 font-bold mb-4')
            ui.code(sql, language='sql').classes('w-full')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('Copy SQL', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{sql}`)')).props('color=primary')
        
        sql_dialog.open()
        
        # Guardar SQL para criação
        self.generated_sql = sql
    
    def create_view(self):
        """Cria a view no BigQuery"""
        if not hasattr(self, 'generated_sql'):
            ui.notify("Please generate SQL first", type="warning")
            return
        
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
                    'masked_columns': list(self.masking_config.keys()),
                    'authorized_users': self.authorized_users
                }
            )
            
            ui.notify(f"✅ Masked view '{view_name}' created successfully!", type="positive")
            
            # Aplicar RLS se houver usuários autorizados
            if self.authorized_users:
                self.apply_rls_to_view(view_name)
            
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
    
    def apply_rls_to_view(self, view_name):
        """Aplica RLS na view para usuários autorizados"""
        # TODO: Implementar RLS na view se necessário
        pass
    
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
                    ui.label('Select columns and masking type').classes('text-caption mb-4')
                    
                    # Grid de colunas
                    self.columns_grid = ui.aggrid({
                        'columnDefs': [
                            {'field': 'column_name', 'headerName': 'Column', 'filter': True, 'minWidth': 200},
                            {'field': 'data_type', 'headerName': 'Type', 'filter': True, 'minWidth': 100},
                            {
                                'field': 'mask_type',
                                'headerName': 'Masking Type',
                                'cellEditor': 'agSelectCellEditor',
                                'cellEditorParams': {
                                    'values': ['none', 'hash', 'null', 'partial', 'round', 'default']
                                },
                                'editable': True,
                                'minWidth': 150
                            },
                            {'field': 'preview', 'headerName': 'Preview', 'minWidth': 200},
                        ],
                        'rowData': [],
                        'defaultColDef': {'sortable': True, 'resizable': True},
                    }).classes('w-full h-96 ag-theme-quartz')
                    
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
                
                # STEP 4: Access Control (Optional)
                with ui.step('Access Control (Optional)'):
                    ui.label('Add users who should see real data (all others see masked)').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-2 items-end'):
                        self.user_email_input = ui.input(
                            label='User Email',
                            placeholder='user@example.com'
                        ).classes('flex-1')
                        ui.button('ADD USER', icon='add', on_click=self.add_authorized_user).props('color=primary')
                    
                    ui.label('Authorized Users:').classes('font-bold mt-4 mb-2')
                    with ui.card().classes('w-full min-h-32'):
                        self.authorized_users_container = ui.column().classes('w-full gap-1')
                        self.refresh_authorized_users_list()
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 5: Review and Create
                with ui.step('Review and Create'):
                    ui.label('Review configuration and create masked view').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        ui.button('GENERATE SQL', icon='code', on_click=self.generate_sql).props('color=blue')
                        ui.button('CREATE VIEW', icon='check_circle', on_click=self.create_view).props('color=positive')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
    
    def run(self):
        pass  # Já renderizado no __init__
