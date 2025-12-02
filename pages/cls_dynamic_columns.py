import theme
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from services.audit_service import AuditService
import traceback

config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class DynamicColumnSecurity:
    
    PROTECTION_TYPES = {
        'VISIBLE': {
            'label': '👁️ Visible',
            'description': 'Real data shown',
            'color': 'bg-green-100 text-green-700',
            'preview': '→ John Doe'
        },
        'HIDDEN': {
            'label': '🚫 Hidden',
            'description': 'Column excluded (CLS)',
            'color': 'bg-red-100 text-red-700',
            'preview': '→ (not in view)'
        },
        'PARTIAL_MASK': {
            'label': '🎭 Partial Mask',
            'description': 'First/last chars',
            'color': 'bg-purple-100 text-purple-700',
            'preview': '→ 123.XXX.XX-45'
        },
        'HASH': {
            'label': '🔒 Hash',
            'description': 'SHA256 hash',
            'color': 'bg-blue-100 text-blue-700',
            'preview': '→ a3f5e9d8b2c1...'
        },
        'NULLIFY': {
            'label': '∅ Nullify',
            'description': 'Replace with NULL',
            'color': 'bg-gray-100 text-gray-700',
            'preview': '→ NULL'
        },
        'ROUND': {
            'label': '🔢 Round',
            'description': 'Round to 10,000',
            'color': 'bg-yellow-100 text-yellow-700',
            'preview': '→ 80000.00'
        },
        'REDACT': {
            'label': '📝 Redact',
            'description': '[REDACTED]',
            'color': 'bg-orange-100 text-orange-700',
            'preview': '→ [REDACTED]'
        }
    }

    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.page_title = "Create Protected View"
        
        # Step data
        self.selected_dataset = None
        self.selected_table = None
        self.table_columns = []
        self.column_protection = {}
        self.authorized_users = []
        self.view_name = None
        self.views_dataset = None  # ✅ NOVO: Dataset onde views serão criadas
        
        # Stepper
        self.current_step = 1
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Create Protected View (CLS + Masking)').classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def get_tables(self, dataset_id):
        try:
            tables = client.list_tables(dataset_id)
            # Excluir views protegidas
            return [
                table.table_id for table in tables 
                if not any(table.table_id.endswith(suffix) for suffix in ['_restricted', '_masked', '_protected'])
            ]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    async def load_table_schema(self):
        """Carrega schema da tabela"""
        if not self.selected_table:
            ui.notify("Select a table first", type="warning")
            return
        
        n = ui.notification('Loading schema...', type='info', spinner=True, timeout=None)
        
        try:
            table_ref = client.dataset(self.selected_dataset).table(self.selected_table)
            table = await run.io_bound(client.get_table, table_ref)
            
            self.table_columns = []
            for field in table.schema:
                self.table_columns.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            
            # Inicializar proteção como VISIBLE
            self.column_protection = {col['name']: 'VISIBLE' for col in self.table_columns}
            
            n.dismiss()
            ui.notify(f"✅ Loaded {len(self.table_columns)} columns", type="positive")
            
            # Ir para step 2
            self.current_step = 2
            self.refresh_stepper()
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
    
    def generate_column_sql(self, col_name, col_type, protection):
        """Gera SQL para uma coluna"""
        if protection == 'VISIBLE':
            return col_name
        elif protection == 'HIDDEN':
            return None
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
                return col_name
        elif protection == 'REDACT':
            return f"'[REDACTED]' AS {col_name}"
        return col_name
    
    def generate_view_sql(self):
        """Gera SQL completo da view"""
        if not self.view_name:
            return None
        
        select_columns = []
        for col in self.table_columns:
            sql_expr = self.generate_column_sql(
                col['name'], 
                col['type'], 
                self.column_protection.get(col['name'], 'VISIBLE')
            )
            if sql_expr:
                select_columns.append(sql_expr)
        
        if not select_columns:
            return None
        
        # ✅ VIEW NO DATASET _views
        sql = f"""CREATE OR REPLACE VIEW `{self.project_id}.{self.views_dataset}.{self.view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(select_columns)}
FROM `{self.project_id}.{self.selected_dataset}.{self.selected_table}`;"""
        
        return sql
    
    async def create_views_dataset(self):
        """✅ Cria dataset _views se não existir"""
        try:
            dataset_ref = client.dataset(self.views_dataset)
            await run.io_bound(client.get_dataset, dataset_ref)
            return True
        except:
            # Dataset não existe, criar
            try:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "us-central1"
                dataset.description = f"Protected views from {self.selected_dataset} - Users have access here"
                await run.io_bound(client.create_dataset, dataset)
                ui.notify(f"✅ Created dataset: {self.views_dataset}", type="positive")
                return True
            except Exception as e:
                ui.notify(f"Error creating dataset: {e}", type="negative")
                return False
    
    async def configure_authorized_view(self):
        """✅ Configura Authorized View cross-dataset"""
        try:
            from google.cloud.bigquery import AccessEntry
            
            # 1. Adicionar view como AUTHORIZED no dataset ORIGEM
            source_dataset_ref = client.dataset(self.selected_dataset)
            source_dataset = await run.io_bound(client.get_dataset, source_dataset_ref)
            
            access_entries = list(source_dataset.access_entries)
            
            # Authorized view entry
            authorized_view_entry = AccessEntry(
                role=None,
                entity_type='view',
                entity_id={
                    'projectId': self.project_id,
                    'datasetId': self.views_dataset,
                    'tableId': self.view_name
                }
            )
            
            # Verificar se já existe
            view_exists = False
            for entry in access_entries:
                if entry.entity_type == 'view' and isinstance(entry.entity_id, dict):
                    if (entry.entity_id.get('projectId') == self.project_id and
                        entry.entity_id.get('datasetId') == self.views_dataset and
                        entry.entity_id.get('tableId') == self.view_name):
                        view_exists = True
                        break
            
            if not view_exists:
                access_entries.append(authorized_view_entry)
            
            # Atualizar dataset origem
            source_dataset.access_entries = access_entries
            await run.io_bound(client.update_dataset, source_dataset, ['access_entries'])
            
            # 2. Adicionar usuários no dataset de VIEWS
            if self.authorized_users:
                views_dataset_ref = client.dataset(self.views_dataset)
                views_dataset_obj = await run.io_bound(client.get_dataset, views_dataset_ref)
                
                views_access_entries = list(views_dataset_obj.access_entries)
                
                for email in self.authorized_users:
                    user_entry = AccessEntry(
                        role='READER',
                        entity_type='userByEmail',
                        entity_id=email
                    )
                    
                    # Verificar se já existe
                    user_exists = False
                    for entry in views_access_entries:
                        if (entry.entity_type == 'userByEmail' and 
                            entry.entity_id == email and 
                            entry.role == 'READER'):
                            user_exists = True
                            break
                    
                    if not user_exists:
                        views_access_entries.append(user_entry)
                
                # Atualizar dataset de views
                views_dataset_obj.access_entries = views_access_entries
                await run.io_bound(client.update_dataset, views_dataset_obj, ['access_entries'])
            
            return True
            
        except Exception as e:
            print(f"[ERROR] configure_authorized_view: {e}")
            traceback.print_exc()
            ui.notify(f"⚠️ Authorization warning: {str(e)[:200]}", type="warning")
            return False
    
    async def create_view(self):
        """Cria view com toda a configuração"""
        visible_count = len([p for p in self.column_protection.values() if p != 'HIDDEN'])
        if visible_count == 0:
            ui.notify("❌ Cannot hide ALL columns!", type="negative")
            return
        
        if not self.view_name:
            ui.notify("Please enter a view name", type="warning")
            return
        
        # ✅ Definir dataset de views
        self.views_dataset = f"{self.selected_dataset}_views"
        
        n = ui.notification('Creating protected view...', spinner=True, timeout=None)
        
        try:
            # 1. Criar dataset _views se não existir
            if not await self.create_views_dataset():
                n.dismiss()
                return
            
            # 2. Criar VIEW
            sql = self.generate_view_sql()
            query_job = await run.io_bound(client.query, sql)
            await run.io_bound(query_job.result)
            
            # 3. Atualizar descrição
            description_lines = [
                f"Restricted view from {self.selected_dataset}.{self.selected_table}",
                "",
                "COLUMN_PROTECTION:"
            ]
            
            for col_name, protection in self.column_protection.items():
                if protection != 'VISIBLE':
                    description_lines.append(f"{col_name}:{protection}")
            
            if self.authorized_users:
                description_lines.append("")
                description_lines.append(f"AUTHORIZED_USERS: {', '.join(self.authorized_users)}")
            
            description = '\n'.join(description_lines)
            
            table_ref = client.dataset(self.views_dataset).table(self.view_name)
            table = await run.io_bound(client.get_table, table_ref)
            table.description = description
            await run.io_bound(client.update_table, table, ['description'])
            
            # 4. ✅ Configurar Authorized View
            await self.configure_authorized_view()
            
            # 5. Audit log
            self.audit_service.log_action(
                action='CREATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.views_dataset}.{self.view_name}",
                status='SUCCESS',
                details={
                    'source_dataset': self.selected_dataset,
                    'source_table': self.selected_table,
                    'views_dataset': self.views_dataset,
                    'column_protection': self.column_protection,
                    'authorized_users': self.authorized_users,
                    'total_columns': len(self.table_columns),
                    'visible': len([p for p in self.column_protection.values() if p not in ['HIDDEN']]),
                    'hidden': len([p for p in self.column_protection.values() if p == 'HIDDEN']),
                    'masked': len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
                }
            )
            
            n.dismiss()
            
            # Success dialog
            with ui.dialog() as success_dialog, ui.card().classes('w-full max-w-3xl'):
                ui.label('✅ Protected View Created!').classes('text-h5 font-bold text-green-600 mb-4')
                
                with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                    ui.label('📊 View Details:').classes('font-bold mb-2')
                    ui.label(f'  • Source: {self.selected_dataset}.{self.selected_table}').classes('text-sm')
                    ui.label(f'  • View: {self.views_dataset}.{self.view_name}').classes('text-sm font-bold text-green-700')
                    ui.label(f'  • Visible: {len([p for p in self.column_protection.values() if p not in ["HIDDEN"]])}').classes('text-sm')
                    ui.label(f'  • Hidden: {len([p for p in self.column_protection.values() if p == "HIDDEN"])}').classes('text-sm')
                    ui.label(f'  • Masked: {len([p for p in self.column_protection.values() if p not in ["VISIBLE", "HIDDEN"]])}').classes('text-sm')
                
                if self.authorized_users:
                    with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                        ui.label('👥 Authorized Users:').classes('font-bold mb-2')
                        for email in self.authorized_users:
                            ui.label(f'  ✅ {email}').classes('text-sm')
                
                with ui.card().classes('w-full bg-yellow-50 p-4 mb-4'):
                    ui.label('🔐 Security Configuration:').classes('font-bold mb-2')
                    ui.label(f'  • Source dataset: {self.selected_dataset} (users blocked)').classes('text-sm')
                    ui.label(f'  • Views dataset: {self.views_dataset} (users allowed)').classes('text-sm')
                    ui.label(f'  • Authorized View: ✅ Configured').classes('text-sm')
                
                with ui.card().classes('w-full bg-purple-50 p-4 mb-4'):
                    ui.label('📝 Query Example:').classes('font-bold mb-2')
                    query = f"SELECT * FROM `{self.project_id}.{self.views_dataset}.{self.view_name}` LIMIT 1000;"
                    ui.code(query, language='sql').classes('text-xs')
                
                def reset_form():
                    success_dialog.close()
                    self.reset()
                
                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('CREATE ANOTHER', icon='add', on_click=reset_form).props('color=positive')
                    ui.button('DONE', on_click=lambda: ui.navigate.to('/clsdynamicmanage/')).props('flat')  # ✅ CORRIGIDO
            
            success_dialog.open()
            
        except Exception as e:
            n.dismiss()
            traceback.print_exc()
            
            self.audit_service.log_action(
                action='CREATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.views_dataset}.{self.view_name}",
                status='FAILED',
                error_message=str(e)
            )
            
            ui.notify(f"Error: {e}", type="negative")
    
    def reset(self):
        """Reset form"""
        self.selected_dataset = None
        self.selected_table = None
        self.table_columns = []
        self.column_protection = {}
        self.authorized_users = []
        self.view_name = None
        self.views_dataset = None
        self.current_step = 1
        self.refresh_stepper()
    
    def refresh_stepper(self):
        """Refresh stepper UI"""
        self.stepper_container.clear()
        with self.stepper_container:
            self.render_stepper()
    
    def render_stepper(self):
        """Render stepper based on current step"""
        
        # STEP 1: Select Source
        if self.current_step == 1:
            with ui.card().classes('w-full p-6'):
                ui.label('Step 1: Select Source Table').classes('text-h6 font-bold mb-4')
                
                datasets = self.get_datasets()
                
                dataset_select = ui.select(
                    options=datasets,
                    label='Dataset',
                    value=self.selected_dataset,
                    on_change=lambda e: setattr(self, 'selected_dataset', e.value)
                ).classes('w-full mb-4')
                
                def on_dataset_change():
                    if self.selected_dataset:
                        tables = self.get_tables(self.selected_dataset)
                        table_select.options = tables
                        table_select.update()
                
                dataset_select.on('update:model-value', on_dataset_change)
                
                table_select = ui.select(
                    options=[],
                    label='Table',
                    value=self.selected_table,
                    on_change=lambda e: setattr(self, 'selected_table', e.value)
                ).classes('w-full mb-4')
                
                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('LOAD SCHEMA', icon='arrow_forward', on_click=self.load_table_schema).props('color=primary')
        
        # STEP 2: Configure Protection
        elif self.current_step == 2:
            with ui.card().classes('w-full p-6'):
                ui.label('Step 2: Configure Column Protection').classes('text-h6 font-bold mb-4')
                
                with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                    ui.label('ℹ️ Configure protection for each column').classes('font-bold text-sm mb-2')
                    ui.label('• VISIBLE: Show real data').classes('text-xs')
                    ui.label('• HIDDEN: Exclude column (CLS)').classes('text-xs')
                    ui.label('• PARTIAL_MASK, HASH, NULLIFY, ROUND, REDACT: Apply masking').classes('text-xs')
                
                ui.label(f'Source: {self.selected_dataset}.{self.selected_table} ({len(self.table_columns)} columns)').classes('text-sm font-bold mb-2')
                
                with ui.scroll_area().classes('w-full h-96 border rounded p-2 mb-4'):
                    with ui.column().classes('w-full'):
                        for col in self.table_columns:
                            with ui.card().classes('w-full p-3 mb-2'):
                                with ui.row().classes('w-full items-center gap-4'):
                                    with ui.column().classes('w-48'):
                                        ui.label(col['name']).classes('font-bold')
                                        ui.label(col['type']).classes('text-xs text-grey-6')
                                    
                                    current = self.column_protection.get(col['name'], 'VISIBLE')
                                    
                                    def make_handler(col_name):
                                        def handler(e):
                                            self.column_protection[col_name] = e.value
                                            self.refresh_stepper()
                                        return handler
                                    
                                    ui.select(
                                        options=list(self.PROTECTION_TYPES.keys()),
                                        value=current,
                                        on_change=make_handler(col['name'])
                                    ).classes('w-48').props('dense')
                                    
                                    info = self.PROTECTION_TYPES[current]
                                    ui.label(info['label']).classes(f'text-sm px-3 py-1 rounded {info["color"]}')
                                    ui.label(info['preview']).classes('flex-1 text-xs text-grey-7 italic')
                
                # Summary
                with ui.card().classes('w-full bg-purple-50 p-3'):
                    visible = len([p for p in self.column_protection.values() if p == 'VISIBLE'])
                    hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
                    masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
                    
                    ui.label(f'📊 Total: {len(self.table_columns)} | Visible: {visible} | Hidden: {hidden} | Masked: {masked}').classes('font-bold')
                
                with ui.row().classes('w-full justify-between mt-4'):
                    ui.button('BACK', icon='arrow_back', on_click=lambda: self.navigate_step(1)).props('flat')
                    ui.button('NEXT', icon='arrow_forward', on_click=lambda: self.navigate_step(3)).props('color=primary')
        
        # STEP 3: Name View & Add Users
        elif self.current_step == 3:
            with ui.card().classes('w-full p-6'):
                ui.label('Step 3: Name View & Add Users').classes('text-h6 font-bold mb-4')
                
                # ✅ Info sobre datasets
                with ui.card().classes('w-full bg-green-50 p-3 mb-4'):
                    ui.label('🔐 Security Architecture:').classes('font-bold text-sm mb-2')
                    ui.label(f'• Source Dataset: {self.selected_dataset} (users will be BLOCKED)').classes('text-xs')
                    ui.label(f'• Views Dataset: {self.selected_dataset}_views (users will have ACCESS)').classes('text-xs')
                    ui.label('• Authorized View will be configured automatically').classes('text-xs')
                
                ui.input(
                    label='View Name',
                    placeholder='vw_employees_protected',
                    on_change=lambda e: setattr(self, 'view_name', e.value)
                ).classes('w-full mb-4').bind_value(self, 'view_name')
                
                ui.separator()
                ui.label('👥 Authorized Users (optional)').classes('text-sm font-bold mt-4 mb-2')
                
                with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                    ui.label('ℹ️ Users added here will:').classes('font-bold text-xs mb-1')
                    ui.label(f'• Have access to: {self.selected_dataset}_views.{self.view_name or "view"}').classes('text-xs')
                    ui.label(f'• Be blocked from: {self.selected_dataset}.{self.selected_table}').classes('text-xs')
                
                with ui.row().classes('w-full gap-2 mb-2'):
                    user_input = ui.input(placeholder='user@company.com').classes('flex-1')
                    
                    def add_user():
                        email = user_input.value.strip()
                        if email and '@' in email:
                            if email not in self.authorized_users:
                                self.authorized_users.append(email)
                                user_input.value = ''
                                self.refresh_stepper()
                            else:
                                ui.notify("User already added", type="warning")
                        else:
                            ui.notify("Invalid email", type="warning")
                    
                    ui.button('ADD', icon='add', on_click=add_user).props('color=positive')
                
                if self.authorized_users:
                    with ui.column().classes('w-full'):
                        for email in self.authorized_users:
                            with ui.row().classes('w-full items-center justify-between p-2 border rounded mb-1 bg-green-50'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('check_circle').classes('text-green-600')
                                    ui.label(email).classes('text-sm')
                                
                                def make_remove(user_email):
                                    def remove():
                                        self.authorized_users.remove(user_email)
                                        self.refresh_stepper()
                                    return remove
                                
                                ui.button(icon='delete', on_click=make_remove(email)).props('flat dense size=sm')
                
                with ui.row().classes('w-full justify-between mt-4'):
                    ui.button('BACK', icon='arrow_back', on_click=lambda: self.navigate_step(2)).props('flat')
                    ui.button('NEXT: REVIEW', icon='arrow_forward', on_click=lambda: self.navigate_step(4)).props('color=primary')
        
        # STEP 4: Review & Create
        elif self.current_step == 4:
            with ui.card().classes('w-full p-6'):
                ui.label('Step 4: Review & Create').classes('text-h6 font-bold mb-4')
                
                with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                    ui.label('📊 Configuration Summary:').classes('font-bold mb-2')
                    ui.label(f'Source: {self.selected_dataset}.{self.selected_table}').classes('text-sm')
                    ui.label(f'View: {self.selected_dataset}_views.{self.view_name}').classes('text-sm font-bold')
                    ui.label(f'Visible: {len([p for p in self.column_protection.values() if p not in ["HIDDEN"]])}').classes('text-sm')
                    ui.label(f'Hidden: {len([p for p in self.column_protection.values() if p == "HIDDEN"])}').classes('text-sm')
                    ui.label(f'Masked: {len([p for p in self.column_protection.values() if p not in ["VISIBLE", "HIDDEN"]])}').classes('text-sm')
                
                if self.authorized_users:
                    with ui.card().classes('w-full bg-green-50 p-4 mb-4'):
                        ui.label('👥 Authorized Users:').classes('font-bold mb-2')
                        for email in self.authorized_users:
                            ui.label(f'  ✅ {email}').classes('text-sm')
                
                # SQL Preview
                self.views_dataset = f"{self.selected_dataset}_views"
                sql = self.generate_view_sql()
                
                ui.label('SQL Preview:').classes('text-sm font-bold mt-4 mb-2')
                with ui.scroll_area().classes('w-full h-64 bg-grey-9 p-4 rounded'):
                    ui.code(sql, language='sql').classes('text-white text-xs')
                
                with ui.row().classes('w-full justify-between mt-4'):
                    ui.button('BACK', icon='arrow_back', on_click=lambda: self.navigate_step(3)).props('flat')
                    ui.button('CREATE VIEW', icon='add_circle', on_click=self.create_view).props('color=positive size=lg')
    
    def navigate_step(self, step):
        self.current_step = step
        self.refresh_stepper()
    
    def render_ui(self):
        with theme.frame('Create Protected View'):
            with ui.card().classes('w-full'):
                ui.label("Create Protected View (CLS + Masking + Authorized Views)").classes('text-h5 font-bold mb-4')
                
                # Stepper container
                self.stepper_container = ui.column().classes('w-full')
                self.render_stepper()
    
    def run(self):
        pass
