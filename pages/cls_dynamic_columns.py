import theme
from config import Config
from nicegui import ui
from google.cloud import bigquery
from services.audit_service import AuditService
from datetime import datetime

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DynamicColumnSecurity:
    
    # ✅ TIPOS DE PROTEÇÃO UNIFICADOS (mesmo do manage)
    PROTECTION_TYPES = {
        'VISIBLE': {
            'label': '👁️ Visible',
            'description': 'Real data shown',
            'color': 'bg-green-100 text-green-700'
        },
        'HIDDEN': {
            'label': '🚫 Hidden',
            'description': 'Column excluded (CLS)',
            'color': 'bg-red-100 text-red-700'
        },
        'PARTIAL_MASK': {
            'label': '🎭 Partial Mask',
            'description': 'First/last chars (123.XXX.XX-45)',
            'color': 'bg-purple-100 text-purple-700'
        },
        'HASH': {
            'label': '🔒 Hash',
            'description': 'SHA256 hash',
            'color': 'bg-blue-100 text-blue-700'
        },
        'NULLIFY': {
            'label': '∅ Nullify',
            'description': 'Replace with NULL',
            'color': 'bg-gray-100 text-gray-700'
        },
        'ROUND': {
            'label': '🔢 Round',
            'description': 'Round to 10,000',
            'color': 'bg-yellow-100 text-yellow-700'
        },
        'REDACT': {
            'label': '📝 Redact',
            'description': '[REDACTED]',
            'color': 'bg-orange-100 text-orange-700'
        }
    }

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Create Protected View"
        
        self.selected_dataset = None
        self.selected_table = None
        self.table_columns = []
        self.column_protection = {}  # {column_name: protection_type}
        self.view_name = None
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Create Protected View (Unified CLS + Masking)').classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        """Lista datasets"""
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def get_tables(self, dataset_id):
        """Lista tabelas do dataset"""
        try:
            tables = client.list_tables(dataset_id)
            # Excluir views protegidas
            return [t.table_id for t in tables if not any(t.table_id.endswith(s) for s in ['_restricted', '_masked', '_protected'])]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
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
            ui.notify(f"Error: {e}", type="negative")
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
        
        # Inicializar todas como VISIBLE
        self.column_protection = {col['name']: 'VISIBLE' for col in self.table_columns}
        
        # Sugerir nome para view
        self.view_name = f"vw_{table_id}_protected"
        
        ui.notify(f"Loaded {len(self.table_columns)} columns", type="positive")
    
    def render_columns_config(self):
        """Renderiza configuração de proteção de colunas"""
        if not self.columns_container or not self.table_columns:
            ui.notify("Please select a table first", type="warning")
            return
        
        self.columns_container.clear()
        
        with self.columns_container:
            ui.label(f"Configure protection for {len(self.table_columns)} columns:").classes('text-sm font-bold mb-4')
            
            # Info card
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('ℹ️ Protection Types:').classes('font-bold text-sm mb-2')
                for prot_type, prot_info in self.PROTECTION_TYPES.items():
                    ui.label(f'  • {prot_info["label"]}: {prot_info["description"]}').classes('text-xs')
            
            # Scroll area com colunas
            with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                for col in self.table_columns:
                    with ui.card().classes('w-full p-3 mb-2'):
                        with ui.row().classes('w-full items-center gap-4'):
                            # Nome e tipo
                            with ui.column().classes('w-48'):
                                ui.label(col['name']).classes('font-bold text-base')
                                ui.label(f"{col['type']}").classes('text-xs text-grey-6')
                            
                            # Dropdown de proteção
                            current_protection = self.column_protection.get(col['name'], 'VISIBLE')
                            
                            def make_change_handler(col_name, col_type):
                                def handler(e):
                                    self.column_protection[col_name] = e.value
                                    self.render_columns_config()  # Refresh para atualizar preview
                                return handler
                            
                            protection_select = ui.select(
                                options=list(self.PROTECTION_TYPES.keys()),
                                value=current_protection,
                                on_change=make_change_handler(col['name'], col['type'])
                            ).classes('w-48').props('dense')
                            
                            # Label de status
                            prot_info = self.PROTECTION_TYPES[current_protection]
                            status_label = ui.label(prot_info['label'])
                            status_label.classes(f'text-sm px-3 py-1 rounded {prot_info["color"]}')
                            
                            # Preview
                            preview = self.get_protection_preview(col['name'], col['type'], current_protection)
                            ui.label(preview).classes('flex-1 text-xs text-grey-7 italic')
            
            # Resumo
            visible = len([p for p in self.column_protection.values() if p == 'VISIBLE'])
            hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
            masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
            
            with ui.card().classes('w-full bg-purple-50 p-3 mt-4'):
                ui.label(
                    f'📊 Total: {len(self.table_columns)} | '
                    f'Visible: {visible} | '
                    f'Hidden: {hidden} | '
                    f'Masked: {masked}'
                ).classes('text-sm font-bold')
    
    def get_protection_preview(self, col_name, col_type, protection):
        """Preview do resultado da proteção"""
        if protection == 'VISIBLE':
            if col_type == 'STRING':
                return '→ John Doe'
            elif col_type in ['INTEGER', 'INT64']:
                return '→ 12345'
            elif col_type in ['FLOAT', 'FLOAT64']:
                return '→ 99.99'
            else:
                return '→ real data'
        elif protection == 'HIDDEN':
            return '→ (not in view)'
        elif protection == 'PARTIAL_MASK':
            return '→ 123.XXX.XX-45'
        elif protection == 'HASH':
            return '→ a3f5e9d8b2c1...'
        elif protection == 'NULLIFY':
            return '→ NULL'
        elif protection == 'ROUND':
            if col_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'INT64', 'FLOAT64']:
                return '→ 80000.00'
            else:
                return '→ (N/A for non-numeric)'
        elif protection == 'REDACT':
            return '→ [REDACTED]'
        return ''
    
    def generate_column_sql(self, col_name, col_type, protection):
        """Gera SQL para uma coluna baseado na proteção"""
        if protection == 'VISIBLE':
            return col_name
        
        elif protection == 'HIDDEN':
            return None  # Não incluir
        
        elif protection == 'PARTIAL_MASK':
            return f"CONCAT(SUBSTR(CAST({col_name} AS STRING), 1, 3), '.XXX.XXX-', SUBSTR(CAST({col_name} AS STRING), -2)) AS {col_name}"
        
        elif protection == 'HASH':
            return f"TO_BASE64(SHA256(CAST({col_name} AS STRING))) AS {col_name}"
        
        elif protection == 'NULLIFY':
            return f"NULL AS {col_name}"
        
        elif protection == 'ROUND':
            if col_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'BIGNUMERIC', 'INT64', 'FLOAT64']:
                return f"ROUND({col_name} / 10000) * 10000 AS {col_name}"
            else:
                return col_name  # Não pode arredondar não-numéricos
        
        elif protection == 'REDACT':
            return f"'[REDACTED]' AS {col_name}"
        
        return col_name
    
    def generate_view_sql(self):
        """Gera SQL completo da view"""
        if not self.selected_dataset or not self.selected_table:
            ui.notify("Please select dataset and table first", type="warning")
            return None
        
        if not self.view_name:
            ui.notify("Please enter view name", type="warning")
            return None
        
        # Validar: pelo menos 1 coluna não-hidden
        visible_count = len([p for p in self.column_protection.values() if p != 'HIDDEN'])
        if visible_count == 0:
            ui.notify("❌ Cannot hide ALL columns!", type="negative")
            return None
        
        # Gerar colunas
        select_columns = []
        for col in self.table_columns:
            sql_expr = self.generate_column_sql(col['name'], col['type'], self.column_protection.get(col['name'], 'VISIBLE'))
            if sql_expr:
                select_columns.append(sql_expr)
        
        if not select_columns:
            return None
        
        # Montar SQL completo
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sql = f"""-- Protected view for {self.selected_table}
-- Created: {timestamp}
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.{self.view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(select_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`;"""
        
        return sql
    
    def generate_description(self):
        """Gera descrição com metadata"""
        description_lines = [
            f"Restricted view from {self.selected_table}",
            "",
            "COLUMN_PROTECTION:"
        ]
        
        for col_name, protection in self.column_protection.items():
            if protection != 'VISIBLE':
                description_lines.append(f"{col_name}:{protection}")
        
        return '\n'.join(description_lines)
    
    def preview_sql(self):
        """Mostra preview do SQL"""
        sql = self.generate_view_sql()
        if not sql:
            return
        
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label('SQL Preview').classes('text-h6 font-bold mb-4')
            
            # Resumo
            visible = len([p for p in self.column_protection.values() if p == 'VISIBLE'])
            hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
            masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('📊 View Summary:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View name: {self.view_name}').classes('text-xs')
                ui.label(f'  • Source table: {self.selected_table}').classes('text-xs')
                ui.label(f'  • Visible columns: {visible}').classes('text-xs')
                ui.label(f'  • Hidden columns: {hidden}').classes('text-xs')
                ui.label(f'  • Masked columns: {masked}').classes('text-xs')
            
            # Mostrar colunas protegidas
            protected_cols = {k: v for k, v in self.column_protection.items() if v != 'VISIBLE'}
            if protected_cols:
                with ui.card().classes('w-full bg-purple-50 p-3 mb-4'):
                    ui.label('🛡️ Protected Columns:').classes('font-bold text-sm mb-2')
                    for col_name, prot_type in list(protected_cols.items())[:10]:
                        prot_label = self.PROTECTION_TYPES[prot_type]['label']
                        ui.label(f'  • {col_name} → {prot_label}').classes('text-xs')
                    if len(protected_cols) > 10:
                        ui.label(f'  ... and {len(protected_cols)-10} more').classes('text-xs italic')
            
            # SQL
            with ui.scroll_area().classes('w-full h-96 bg-grey-9 p-4 rounded'):
                ui.code(sql, language='sql').classes('text-white')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('COPY', icon='content_copy', on_click=lambda: ui.clipboard.write(sql)).props('color=primary')
        
        sql_dialog.open()
    
    def create_view(self):
        """Cria a view no BigQuery"""
        sql = self.generate_view_sql()
        if not sql:
            return
        
        try:
            # Criar view
            query_job = client.query(sql)
            query_job.result()
            
            # Atualizar descrição
            description = self.generate_description()
            table_ref = client.dataset(self.selected_dataset).table(self.view_name)
            table = client.get_table(table_ref)
            table.description = description
            client.update_table(table, ['description'])
            
            # Audit log
            visible = len([p for p in self.column_protection.values() if p == 'VISIBLE'])
            hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
            masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
            
            self.audit_service.log_action(
                action='CREATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.selected_dataset}.{self.view_name}",
                status='SUCCESS',
                details={
                    'source_table': f"{self.selected_dataset}.{self.selected_table}",
                    'view_name': self.view_name,
                    'column_protection': self.column_protection,
                    'total_columns': len(self.table_columns),
                    'visible': visible,
                    'hidden': hidden,
                    'masked': masked
                }
            )
            
            ui.notify(f"✅ View '{self.view_name}' created successfully!", type="positive")
            self.show_success_guide()
            
        except Exception as e:
            self.audit_service.log_action(
                action='CREATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.selected_dataset}.{self.view_name}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error: {e}", type="negative")
    
    def show_success_guide(self):
        """Mostra guia após criação"""
        with ui.dialog() as guide_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label('✅ View Created Successfully!').classes('text-h5 font-bold text-green-600 mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('📊 View Information:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View: {self.view_name}').classes('text-xs')
                ui.label(f'  • Dataset: {self.selected_dataset}').classes('text-xs')
                ui.label(f'  • Source: {self.selected_table}').classes('text-xs')
            
            with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                ui.label('📝 Query Example:').classes('font-bold text-sm mb-1')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.{self.view_name}`;", language='sql').classes('w-full text-xs')
            
            with ui.card().classes('w-full bg-yellow-50 p-3 mt-4'):
                ui.label('ℹ️ Next Steps:').classes('text-sm font-bold mb-1')
                ui.label('• Use "Manage Protected Views" to edit column protection').classes('text-xs')
                ui.label('• Add user documentation in the management interface').classes('text-xs')
                ui.label('• Grant access to users via IAM roles').classes('text-xs')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=guide_dialog.close).props('color=primary')
        
        guide_dialog.open()
    
    def render_ui(self):
        with theme.frame('Create Protected View'):
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                # STEP 1: Select Source
                with ui.step('Select Source Table'):
                    ui.label('Choose the table to create a protected view').classes('text-caption mb-4')
                    
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
                
                # STEP 2: Configure Protection
                with ui.step('Configure Column Protection'):
                    ui.label('Set protection type for each column').classes('text-caption mb-4')
                    
                    self.columns_container = ui.column().classes('w-full')
                    
                    ui.button(
                        'LOAD COLUMNS',
                        icon='refresh',
                        on_click=self.render_columns_config
                    ).props('color=primary').classes('mt-2')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 3: Name View
                with ui.step('Name Protected View'):
                    ui.label('Enter name for the protected view').classes('text-caption mb-4')
                    
                    self.view_name_input = ui.input(
                        label='View Name',
                        placeholder='vw_table_protected',
                        on_change=lambda e: setattr(self, 'view_name', e.value)
                    ).classes('w-full')
                    
                    # Preview do que será criado
                    with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                        ui.label('ℹ️ What will be created:').classes('text-sm font-bold mb-2')
                        ui.label('• Single view combining CLS (hide) + Masking').classes('text-xs')
                        ui.label('• Metadata saved in view description').classes('text-xs')
                        ui.label('• Can be edited later in "Manage Protected Views"').classes('text-xs')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 4: Review and Create
                with ui.step('Review and Create'):
                    ui.label('Review configuration and create view').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        ui.button('PREVIEW SQL', icon='code', on_click=self.preview_sql).props('color=blue')
                        ui.button('CREATE VIEW', icon='check_circle', on_click=self.create_view).props('color=positive')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
    
    def run(self):
        pass
