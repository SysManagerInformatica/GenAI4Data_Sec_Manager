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
    
    # ✅ TIPOS DE PROTEÇÃO UNIFICADOS (CLS + MASKING)
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
            'description': 'First/last chars (123.XXX.XX-XX)',
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
        self.page_title = "Manage Protected Views"
        
        self.selected_dataset = None
        self.protected_views = []
        self.views_grid = None
        
        # ✅ NOVA ESTRUTURA: {column_name: protection_type}
        self.current_view = None
        self.current_view_dataset = None  # ✅ NOVO: Dataset onde a view está
        self.source_dataset = None  # ✅ NOVO: Dataset da tabela origem
        self.source_table_columns = []
        self.column_protection = {}
        self.authorized_users = []
        
        # Criar dialog de edição UMA VEZ
        self.create_edit_dialog()
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title(self.page_title)
        ui.label('Manage Protected Views (Unified CLS + Masking)').classes('text-primary text-center text-bold')
    
    def create_edit_dialog(self):
        """Cria dialog de edição UMA VEZ - será reutilizado"""
        with ui.dialog() as self.edit_dialog, ui.card().classes('w-full max-w-7xl'):
            self.edit_title = ui.label('').classes('text-h5 font-bold mb-4')
            
            with ui.tabs().classes('w-full') as tabs:
                tab_columns = ui.tab('Column Protection', icon='security')
                tab_users = ui.tab('Add Users', icon='person_add')
            
            with ui.tab_panels(tabs, value=tab_columns).classes('w-full'):
                # TAB 1: Column Protection
                with ui.tab_panel(tab_columns):
                    with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                        ui.label('ℹ️ Configure protection type for each column').classes('font-bold text-sm mb-2')
                        ui.label('• VISIBLE: Real data shown without changes').classes('text-xs')
                        ui.label('• HIDDEN: Column excluded from view (CLS)').classes('text-xs')
                        ui.label('• PARTIAL_MASK: Show first/last chars (123.XXX.XX-45)').classes('text-xs')
                        ui.label('• HASH: Replace with SHA256 hash').classes('text-xs')
                        ui.label('• NULLIFY: Replace with NULL').classes('text-xs')
                        ui.label('• ROUND: Round numbers to 10,000').classes('text-xs')
                        ui.label('• REDACT: Replace with [REDACTED]').classes('text-xs')
                    
                    self.source_label = ui.label('').classes('text-sm font-bold mb-2')
                    
                    # Container para colunas
                    with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                        self.columns_container = ui.column().classes('w-full')
                    
                    # Resumo
                    with ui.card().classes('w-full bg-purple-50 p-3 mt-4'):
                        self.summary_label = ui.label('').classes('text-sm font-bold')
                
                # TAB 2: Add Users
                with ui.tab_panel(tab_users):
                    with ui.card().classes('w-full bg-green-50 p-3 mb-4'):
                        ui.label('✅ Grant access to this view').classes('font-bold text-sm mb-2')
                        ui.label('• Users added here will have BigQuery Data Viewer role on the VIEWS dataset').classes('text-xs')
                        ui.label('• They will NOT have access to the source table').classes('text-xs')
                        ui.label('• Access is granted via IAM policy binding').classes('text-xs')
                    
                    ui.label('Authorized Users:').classes('text-sm font-bold mb-2')
                    
                    # Container para input de usuário
                    self.users_input_container = ui.column().classes('w-full')
                    
                    # Container para lista de usuários
                    self.users_list_container = ui.column().classes('w-full')
            
            # Botões
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('PREVIEW SQL', icon='code', on_click=self.preview_sql).props('flat color=blue')
                ui.button('CANCEL', on_click=self.close_edit_dialog).props('flat')
                ui.button('SAVE CHANGES', icon='save', on_click=self.save_changes_wrapper).props('color=positive')
    
    def close_edit_dialog(self):
        self.edit_dialog.close()
    
    async def save_changes_wrapper(self):
        await self.save_view_changes()
    
    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def get_protected_views(self, dataset_id):
        """✅ Lista views protegidas de AMBOS datasets (origem e _views)"""
        try:
            views = []
            datasets_to_search = [dataset_id]
            
            # ✅ Adicionar dataset _views se existir
            views_dataset = f"{dataset_id}_views"
            try:
                client.get_dataset(views_dataset)
                datasets_to_search.append(views_dataset)
            except:
                pass
            
            for ds in datasets_to_search:
                tables = client.list_tables(ds)
                
                for table in tables:
                    table_ref = client.dataset(ds).table(table.table_id)
                    table_obj = client.get_table(table_ref)
                    
                    if table_obj.table_type != 'VIEW':
                        continue
                    
                    is_protected = False
                    
                    # Detectar por sufixo
                    if any(table.table_id.endswith(suffix) for suffix in ['_restricted', '_masked', '_protected']):
                        is_protected = True
                    
                    # Detectar por metadata
                    if table_obj.description and 'COLUMN_PROTECTION:' in table_obj.description:
                        is_protected = True
                    
                    if not is_protected:
                        continue
                    
                    view_definition = table_obj.view_query
                    source_table = self.extract_source_table(view_definition)
                    source_dataset = self.extract_source_dataset(view_definition) or dataset_id
                    
                    protection_summary = self.analyze_protection(
                        table_obj.description, 
                        table_obj.view_query, 
                        len(table_obj.schema)
                    )
                    
                    authorized_count = len(self.parse_users_from_description(table_obj.description))
                    
                    views.append({
                        'view_name': table.table_id,
                        'view_dataset': ds,  # ✅ NOVO: Dataset da view
                        'source_dataset': source_dataset,  # ✅ NOVO: Dataset da tabela
                        'source_table': source_table,
                        'visible_columns': len(table_obj.schema),
                        'hidden_count': protection_summary['hidden'],
                        'masked_count': protection_summary['masked'],
                        'authorized_users': authorized_count,
                        'created': table_obj.created.strftime('%Y-%m-%d %H:%M') if table_obj.created else 'Unknown',
                        'modified': table_obj.modified.strftime('%Y-%m-%d %H:%M') if table_obj.modified else 'Unknown',
                        'description': table_obj.description or ''
                    })
            
            return views
            
        except Exception as e:
            print(f"[ERROR] get_protected_views: {e}")
            traceback.print_exc()
            ui.notify(f"Error: {e}", type="negative")
            return []
    
    def extract_source_dataset(self, view_query):
        """Extrai dataset da tabela origem"""
        try:
            # Pattern: project.dataset.table
            pattern = r'FROM\s+`[^`]*\.([^`\.]+)\.[^`\.]+`'
            match = re.search(pattern, view_query, re.IGNORECASE)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def analyze_protection(self, description, view_query, visible_count):
        """Analisa tipos de proteção aplicados"""
        summary = {'hidden': 0, 'masked': 0}
        
        if description and 'COLUMN_PROTECTION:' in description:
            lines = description.split('\n')
            in_section = False
            
            for line in lines:
                if 'COLUMN_PROTECTION:' in line:
                    in_section = True
                    continue
                
                if in_section:
                    if line.startswith('AUTHORIZED_USERS:') or (not line.strip() and summary['hidden'] + summary['masked'] > 0):
                        break
                    
                    if ':' in line and line.strip():
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            protection = parts[1].strip()
                            if protection == 'HIDDEN':
                                summary['hidden'] += 1
                            elif protection in ['PARTIAL_MASK', 'HASH', 'NULLIFY', 'ROUND', 'REDACT']:
                                summary['masked'] += 1
        
        if summary['hidden'] == 0 and summary['masked'] == 0 and view_query:
            query_lower = view_query.lower()
            
            if 'sha256' in query_lower or 'to_base64' in query_lower:
                summary['masked'] += 1
            
            if 'concat(substr' in query_lower:
                summary['masked'] += 1
            
            if 'round(' in query_lower and '10000' in query_lower:
                summary['masked'] += 1
            
            if '[redacted]' in query_lower:
                summary['masked'] += 1
        
        return summary
    
    def extract_source_table(self, view_query):
        try:
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
        except:
            return 'Unknown'
    
    def on_dataset_change(self, dataset_id):
        self.selected_dataset = dataset_id
        self.protected_views = self.get_protected_views(dataset_id)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_views_grid(self):
    if self.views_grid:
        self.views_grid.options['rowData'] = self.protected_views
        self.views_grid.update()
    
    def update_statistics(self):
        total = len(self.protected_views)
        if hasattr(self, 'total_views_label'):
            self.total_views_label.set_text(str(total))
    
    async def view_details(self):
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No view selected', type="warning")
            return
        
        view_info = rows[0]
        
        with ui.dialog() as details_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f'View Details: {view_info["view_name"]}').classes('text-h5 font-bold mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-2'):
                ui.label('📊 General Information:').classes('font-bold text-sm mb-2')
                ui.label(f'  • View: {view_info["view_dataset"]}.{view_info["view_name"]}').classes('text-xs font-bold')
                ui.label(f'  • Source: {view_info["source_dataset"]}.{view_info["source_table"]}').classes('text-xs')
                ui.label(f'  • Visible: {view_info["visible_columns"]}').classes('text-xs')
                ui.label(f'  • Hidden: {view_info["hidden_count"]}').classes('text-xs')
                ui.label(f'  • Masked: {view_info["masked_count"]}').classes('text-xs')
                ui.label(f'  • Authorized Users: {view_info["authorized_users"]}').classes('text-xs')
            
            async def open_editor():
                n = ui.notification('Loading schema...', type='info', spinner=True, timeout=None)
                try:
                    await self.edit_view(view_info, parent_dialog=details_dialog)
                except Exception as e:
                    ui.notify(f"Error: {e}", type="negative")
                    traceback.print_exc()
                finally:
                    n.dismiss()
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=details_dialog.close).props('flat')
                ui.button('EDIT VIEW', icon='edit', on_click=open_editor).props('color=primary')
        
        details_dialog.open()
    
    async def edit_view(self, view_info, parent_dialog=None):
        """Carrega view e abre editor"""
        self.current_view = view_info
        self.current_view_dataset = view_info['view_dataset']
        self.source_dataset = view_info['source_dataset']
        
        try:
            source_table = view_info['source_table']
            
            if source_table == 'Unknown':
                ui.notify("⚠️ Cannot determine source table", type="warning")
                if parent_dialog:
                    parent_dialog.close()
                self.ask_source_table(view_info)
                return
            
            # ✅ Buscar tabela no dataset correto
            table_ref = client.dataset(self.source_dataset).table(source_table)
            table_obj = await run.io_bound(client.get_table, table_ref)
            
            self.source_table_columns = []
            for field in table_obj.schema:
                self.source_table_columns.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode
                })
            
            # ✅ Buscar view no dataset correto
            view_ref = client.dataset(self.current_view_dataset).table(view_info['view_name'])
            view_obj = await run.io_bound(client.get_table, view_ref)
            
            self.column_protection = self.parse_protection_from_description(
                view_obj.description,
                view_obj.view_query,
                self.source_table_columns
            )
            
            self.authorized_users = self.parse_users_from_description(view_obj.description)
            
            ui.notify("Schema loaded!", type="positive", timeout=1000)
            
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            traceback.print_exc()
            return
        
        if parent_dialog:
            parent_dialog.close()
        
        self.populate_edit_dialog(view_info['view_name'], source_table)
        self.edit_dialog.open()
    
    def parse_protection_from_description(self, description, view_query, all_columns):
        """Parse proteção do metadata ou inferir da query"""
        protection = {}
        
        if description and 'COLUMN_PROTECTION:' in description:
            lines = description.split('\n')
            in_section = False
            for line in lines:
                if 'COLUMN_PROTECTION:' in line:
                    in_section = True
                    continue
                if in_section:
                    if line.startswith('AUTHORIZED_USERS:') or not line.strip():
                        break
                    if ':' in line:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            col_name = parts[0]
                            prot_type = parts[1]
                            protection[col_name] = prot_type
        
        if not protection:
            view_ref = client.dataset(self.current_view_dataset).table(self.current_view['view_name'])
            view_obj = client.get_table(view_ref)
            view_cols = {field.name for field in view_obj.schema}
            
            for col in all_columns:
                if col['name'] in view_cols:
                    if view_query and f"sha256({col['name'].lower()}" in view_query.lower():
                        protection[col['name']] = 'HASH'
                    elif view_query and f"null as {col['name'].lower()}" in view_query.lower():
                        protection[col['name']] = 'NULLIFY'
                    elif view_query and f"concat(substr" in view_query.lower() and col['name'].lower() in view_query.lower():
                        protection[col['name']] = 'PARTIAL_MASK'
                    else:
                        protection[col['name']] = 'VISIBLE'
                else:
                    protection[col['name']] = 'HIDDEN'
        
        for col in all_columns:
            if col['name'] not in protection:
                protection[col['name']] = 'VISIBLE'
        
        return protection
    
    def populate_edit_dialog(self, view_name, source_table):
        """Popula dialog com dados"""
        self.edit_title.set_text(f'Edit View: {view_name}')
        self.source_label.set_text(f'Source: {self.source_dataset}.{source_table} ({len(self.source_table_columns)} columns)')
        
        self.columns_container.clear()
        
        with self.columns_container:
            for col in self.source_table_columns:
                with ui.card().classes('w-full p-3 mb-2'):
                    with ui.row().classes('w-full items-center gap-4'):
                        with ui.column().classes('w-48'):
                            ui.label(col['name']).classes('font-bold text-base')
                            ui.label(f"{col['type']}").classes('text-xs text-grey-6')
                        
                        current_protection = self.column_protection.get(col['name'], 'VISIBLE')
                        
                        def make_change_handler(col_name):
                            def handler(e):
                                self.column_protection[col_name] = e.value
                                self.update_summary()
                                self.populate_edit_dialog(view_name, source_table)
                            return handler
                        
                        protection_select = ui.select(
                            options=list(self.PROTECTION_TYPES.keys()),
                            value=current_protection,
                            on_change=make_change_handler(col['name'])
                        ).classes('w-48').props('dense')
                        
                        prot_info = self.PROTECTION_TYPES[current_protection]
                        status_label = ui.label(prot_info['label'])
                        status_label.classes(f'text-sm px-3 py-1 rounded {prot_info["color"]}')
                        
                        preview = self.get_protection_preview(col['name'], col['type'], current_protection)
                        ui.label(preview).classes('flex-1 text-xs text-grey-7 italic')
        
        self.update_summary()
        self.populate_users_section()
    
    def get_protection_preview(self, col_name, col_type, protection):
        """Preview do resultado da proteção"""
        if protection == 'VISIBLE':
            return '→ John Doe (real data)'
        elif protection == 'HIDDEN':
            return '→ (not in view)'
        elif protection == 'PARTIAL_MASK':
            return '→ 123.XXX.XX-XX'
        elif protection == 'HASH':
            return '→ a3f5e9d8b2c1...'
        elif protection == 'NULLIFY':
            return '→ NULL'
        elif protection == 'ROUND':
            return '→ 80000.00'
        elif protection == 'REDACT':
            return '→ [REDACTED]'
        return ''
    
    def update_summary(self):
        """Atualiza resumo"""
        visible = len([p for p in self.column_protection.values() if p == 'VISIBLE'])
        hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
        masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
        
        self.summary_label.set_text(
            f'📊 Total: {len(self.source_table_columns)} | '
            f'Visible: {visible} | '
            f'Hidden: {hidden} | '
            f'Masked: {masked}'
        )
    
    def populate_users_section(self):
        """Popula seção de usuários AUTORIZADOS"""
        self.users_input_container.clear()
        self.users_list_container.clear()
        
        with self.users_input_container:
            with ui.row().classes('w-full gap-2 mb-4'):
                user_input = ui.input(placeholder='user@company.com', label='Add authorized user').classes('flex-1')
                
                def add_user():
                    email = user_input.value.strip()
                    if email and '@' in email:
                        if email not in self.authorized_users:
                            self.authorized_users.append(email)
                            user_input.value = ''
                            self.populate_users_section()
                            ui.notify(f"✅ Will grant access to: {email}", type="positive")
                        else:
                            ui.notify("User already authorized", type="warning")
                    else:
                        ui.notify("Invalid email", type="warning")
                
                ui.button('ADD', icon='add', on_click=add_user).props('color=positive')
        
        with self.users_list_container:
            if not self.authorized_users:
                ui.label('No authorized users yet').classes('text-grey-5 italic')
            else:
                for email in self.authorized_users:
                    with ui.row().classes('w-full items-center justify-between p-2 border rounded mb-1 bg-green-50'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle').classes('text-green-600')
                            ui.label(email).classes('text-sm font-bold')
                        
                        def make_remove(user_email):
                            def remove():
                                self.authorized_users.remove(user_email)
                                self.populate_users_section()
                                ui.notify(f"❌ Will revoke access from: {user_email}", type="warning")
                            return remove
                        
                        ui.button(icon='delete', on_click=make_remove(email)).props('flat dense size=sm color=negative')
    
    def parse_users_from_description(self, description):
        """Extrai usuários autorizados"""
        if not description:
            return []
        try:
            if 'AUTHORIZED_USERS:' in description:
                users_text = description.split('AUTHORIZED_USERS:')[1].split('\n')[0]
                emails = [email.strip() for email in users_text.split(',')]
                return [e for e in emails if '@' in e]
        except:
            pass
        return []
    
    def generate_column_sql(self, col_name, col_type, protection):
        """Gera SQL para uma coluna baseado na proteção"""
        if protection == 'VISIBLE':
            return col_name
        elif protection == 'HIDDEN':
            return None
        elif protection == 'PARTIAL_MASK':
            return f"CONCAT(SUBSTR(CAST({col_name} AS STRING), 1, 3), '.XXX.XXX-XX') AS {col_name}"
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
    
    def preview_sql(self):
        """Preview do SQL"""
        if not self.current_view:
            return
        
        sql = self.generate_view_sql()
        if not sql:
            ui.notify("Error generating SQL", type="negative")
            return
        
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label('SQL Preview').classes('text-h6 font-bold mb-4')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                visible = len([p for p in self.column_protection.values() if p not in ['HIDDEN']])
                hidden = len([p for p in self.column_protection.values() if p == 'HIDDEN'])
                masked = len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
                
                ui.label(f'✅ Visible: {visible} | 🚫 Hidden: {hidden} | 🎭 Masked: {masked}').classes('text-sm font-bold')
            
            if self.authorized_users:
                with ui.card().classes('w-full bg-green-50 p-3 mb-4'):
                    ui.label('👥 Authorized Users (will have access to this view):').classes('font-bold text-sm mb-2')
                    for email in self.authorized_users:
                        ui.label(f'  ✅ {email}').classes('text-xs')
            
            with ui.scroll_area().classes('w-full h-96 bg-grey-9 p-4 rounded'):
                ui.code(sql, language='sql').classes('text-white')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('COPY', icon='content_copy', on_click=lambda: ui.clipboard.write(sql)).props('color=primary')
        
        sql_dialog.open()
    
    def generate_view_sql(self):
        """Gera SQL completo da view"""
        if not self.current_view:
            return None
        
        view_name = self.current_view['view_name']
        source_table = self.current_view['source_table']
        
        select_columns = []
        for col in self.source_table_columns:
            sql_expr = self.generate_column_sql(col['name'], col['type'], self.column_protection.get(col['name'], 'VISIBLE'))
            if sql_expr:
                select_columns.append(sql_expr)
        
        if not select_columns:
            return None
        
        # ✅ VIEW no dataset correto
        sql = f"""CREATE OR REPLACE VIEW `{self.project_id}.{self.current_view_dataset}.{view_name}` AS
SELECT
  {(','+chr(10)+'  ').join(select_columns)}
FROM `{self.project_id}.{self.source_dataset}.{source_table}`;"""
        
        return sql
    
    async def grant_view_access(self, view_name):
        """✅ CONCEDE ACESSO VIA AUTHORIZED VIEWS (CROSS-DATASET)"""
        if not self.authorized_users:
            return
        
        try:
            from google.cloud.bigquery import AccessEntry
            
            # 1. Adicionar view como AUTHORIZED no dataset ORIGEM
            source_dataset_ref = client.dataset(self.source_dataset)
            source_dataset = await run.io_bound(client.get_dataset, source_dataset_ref)
            
            access_entries = list(source_dataset.access_entries)
            
            # Authorized view entry
            authorized_view_entry = AccessEntry(
                role=None,
                entity_type='view',
                entity_id={
                    'projectId': self.project_id,
                    'datasetId': self.current_view_dataset,
                    'tableId': view_name
                }
            )
            
            # Verificar se já existe
            view_exists = False
            for entry in access_entries:
                if entry.entity_type == 'view' and isinstance(entry.entity_id, dict):
                    if (entry.entity_id.get('projectId') == self.project_id and
                        entry.entity_id.get('datasetId') == self.current_view_dataset and
                        entry.entity_id.get('tableId') == view_name):
                        view_exists = True
                        break
            
            if not view_exists:
                access_entries.append(authorized_view_entry)
            
            # Atualizar dataset origem
            source_dataset.access_entries = access_entries
            await run.io_bound(client.update_dataset, source_dataset, ['access_entries'])
            
            # 2. Adicionar usuários no dataset de VIEWS
            views_dataset_ref = client.dataset(self.current_view_dataset)
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
            
            ui.notify(
                f"✅ Authorized view configured!\n"
                f"✅ Access granted to {len(self.authorized_users)} user(s)", 
                type="positive", 
                timeout=5000
            )
            
            print(f"""
[INFO] Cross-Dataset Authorized View Configuration:
- Source Dataset: {self.source_dataset} (users blocked)
- Views Dataset: {self.current_view_dataset} (users allowed)
- View: {view_name}
- Users: {', '.join(self.authorized_users)}

Users can query:
SELECT * FROM `{self.project_id}.{self.current_view_dataset}.{view_name}` LIMIT 1000;
            """)
            
        except Exception as e:
            print(f"[ERROR] grant_view_access: {e}")
            traceback.print_exc()
            ui.notify(f"⚠️ IAM update error: {str(e)[:300]}", type="warning", timeout=10000)
    
    async def save_view_changes(self):
        """Salva mudanças + APLICA IAM"""
        if not self.current_view:
            return
        
        visible_count = len([p for p in self.column_protection.values() if p != 'HIDDEN'])
        if visible_count == 0:
            ui.notify("❌ Cannot hide ALL columns!", type="negative")
            return
        
        n = ui.notification('Saving changes...', spinner=True, timeout=None)
        
        try:
            view_name = self.current_view['view_name']
            source_table = self.current_view['source_table']
            
            # 1. Recriar VIEW
            sql = self.generate_view_sql()
            query_job = await run.io_bound(client.query, sql)
            await run.io_bound(query_job.result)
            
            # 2. Atualizar descrição
            description_lines = [
                f"Restricted view from {self.source_dataset}.{source_table}",
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
            
            table_ref = client.dataset(self.current_view_dataset).table(view_name)
            table = await run.io_bound(client.get_table, table_ref)
            table.description = description
            await run.io_bound(client.update_table, table, ['description'])
            
            # 3. ✅ APLICAR IAM (GRANT ACCESS)
            if self.authorized_users:
                await self.grant_view_access(view_name)
            
            # 4. Audit log
            self.audit_service.log_action(
                action='UPDATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.current_view_dataset}.{view_name}",
                status='SUCCESS',
                details={
                    'source_dataset': self.source_dataset,
                    'source_table': source_table,
                    'views_dataset': self.current_view_dataset,
                    'column_protection': self.column_protection,
                    'authorized_users': self.authorized_users,
                    'total_columns': len(self.source_table_columns),
                    'visible': len([p for p in self.column_protection.values() if p not in ['HIDDEN']]),
                    'hidden': len([p for p in self.column_protection.values() if p == 'HIDDEN']),
                    'masked': len([p for p in self.column_protection.values() if p not in ['VISIBLE', 'HIDDEN']])
                }
            )
            
            n.dismiss()
            ui.notify("✅ View updated and access granted!", type="positive")
            self.edit_dialog.close()
            
            # Refresh
            self.protected_views = self.get_protected_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            
        except Exception as e:
            n.dismiss()
            traceback.print_exc()
            self.audit_service.log_action(
                action='UPDATE_PROTECTED_VIEW',
                resource_type='PROTECTED_VIEW',
                resource_name=f"{self.current_view_dataset}.{view_name}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error: {e}", type="negative")
    
    def ask_source_table(self, view_info):
        """Dialog para selecionar tabela origem manualmente"""
        with ui.dialog() as ask_dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('⚠️ Source Table Not Found').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label('Select source table manually:').classes('mb-4')
            
            try:
                tables = client.list_tables(self.source_dataset)
                table_names = [t.table_id for t in tables if not any(t.table_id.endswith(s) for s in ['_restricted', '_masked', '_protected'])]
                
                if not table_names:
                    ui.label('No tables found').classes('text-red-600')
                    ui.button('Close', on_click=ask_dialog.close).props('color=primary')
                    ask_dialog.open()
                    return
                
                table_select = ui.select(options=table_names, label='Source Table', value=table_names[0]).classes('w-full')
                
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
        """Deleta views selecionadas"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify('No views selected', type="warning")
            return
        
        view_names = [f"{row['view_dataset']}.{row['view_name']}" for row in rows]
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-h6 font-bold text-orange-600 mb-4')
            ui.label(f'Delete {len(view_names)} view(s)?').classes('mb-2')
            for name in view_names[:10]:
                ui.label(f'  • {name}').classes('text-sm')
            if len(view_names) > 10:
                ui.label(f'  ... and {len(view_names)-10} more').classes('text-sm')
            ui.label('This cannot be undone!').classes('text-red-600 font-bold mt-4')
            
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
                table_ref = client.dataset(view['view_dataset']).table(view['view_name'])
                client.delete_table(table_ref)
                
                self.audit_service.log_action(
                    action='DELETE_PROTECTED_VIEW',
                    resource_type='PROTECTED_VIEW',
                    resource_name=f"{view['view_dataset']}.{view['view_name']}",
                    status='SUCCESS'
                )
                success += 1
            except Exception as e:
                self.audit_service.log_action(
                    action='DELETE_PROTECTED_VIEW',
                    resource_type='PROTECTED_VIEW',
                    resource_name=f"{view['view_dataset']}.{view['view_name']}",
                    status='FAILED',
                    error_message=str(e)
                )
                failed += 1
        
        dialog.close()
        
        if success > 0:
            ui.notify(f"✅ {success} view(s) deleted", type="positive")
        if failed > 0:
            ui.notify(f"❌ {failed} failed", type="negative")
        
        self.protected_views = self.get_protected_views(self.selected_dataset)
        self.refresh_views_grid()
        self.update_statistics()
    
    def refresh_all(self):
        """Refresh completo"""
        if self.selected_dataset:
            self.protected_views = self.get_protected_views(self.selected_dataset)
            self.refresh_views_grid()
            self.update_statistics()
            ui.notify("Refreshed", type="positive")
        else:
            ui.notify("Select dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('Manage Protected Views'):
            with ui.card().classes('w-full'):
                ui.label("Manage Protected Views (Unified CLS + Masking + IAM)").classes('text-h5 font-bold mb-4')
                
                with ui.card().classes('w-full bg-yellow-50 p-3 mb-4'):
                    ui.label('🔐 Cross-Dataset Security:').classes('font-bold text-sm mb-2')
                    ui.label('• Views are stored in {dataset}_views datasets').classes('text-xs')
                    ui.label('• Users have access to views but NOT to source tables').classes('text-xs')
                    ui.label('• Authorized Views bypass Policy Tags on source tables').classes('text-xs')
                
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    datasets = self.get_datasets()
                    ui.select(
                        options=datasets,
                        label='Select Dataset (will search dataset + dataset_views)',
                        on_change=lambda e: self.on_dataset_change(e.value)
                    ).classes('flex-1')
                    
                    ui.button('REFRESH', icon='refresh', on_click=self.refresh_all).props('flat')
                
                with ui.row().classes('w-full gap-4 mb-4'):
                    with ui.card().classes('flex-1 bg-blue-50'):
                        ui.label('Protected Views').classes('text-sm text-grey-7')
                        self.total_views_label = ui.label('0').classes('text-3xl font-bold text-blue-600')
                
                ui.separator()
                ui.label("Protected Views (from dataset and dataset_views)").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'view_name', 'headerName': 'View Name', 'checkboxSelection': True, 'filter': True, 'minWidth': 280},
                        {'field': 'view_dataset', 'headerName': 'View Dataset', 'filter': True, 'minWidth': 180},
                        {'field': 'source_table', 'headerName': 'Source Table', 'filter': True, 'minWidth': 200},
                        {'field': 'visible_columns', 'headerName': 'Visible', 'filter': True, 'minWidth': 90},
                        {'field': 'hidden_count', 'headerName': 'Hidden', 'filter': True, 'minWidth': 90},
                        {'field': 'masked_count', 'headerName': 'Masked', 'filter': True, 'minWidth': 90},
                        {'field': 'authorized_users', 'headerName': 'Users', 'filter': True, 'minWidth': 90},
                        {'field': 'created', 'headerName': 'Created', 'filter': True, 'minWidth': 140},
                        {'field': 'modified', 'headerName': 'Modified', 'filter': True, 'minWidth': 140},
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
