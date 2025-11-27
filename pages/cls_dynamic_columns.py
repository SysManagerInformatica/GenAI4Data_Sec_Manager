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
        self.column_visibility = {}  # {column_name: 'public'/'restricted'/'masked'}
        self.user_access = {
            'full': [],     # vê tudo real
            'masked': [],   # vê restrito com hash
            'public': []    # não vê restrito
        }
        
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
        
        # Inicializar todas como public
        self.column_visibility = {col['name']: 'public' for col in self.table_columns}
    
    def render_column_visibility_config(self):
        """Renderiza configuração de visibilidade das colunas"""
        if not self.columns_container or not self.table_columns:
            return
        
        self.columns_container.clear()
        
        with self.columns_container:
            ui.label(f"Configure visibility for {len(self.table_columns)} columns:").classes('text-sm font-bold mb-2')
            
            with ui.scroll_area().classes('w-full h-96 border rounded p-2'):
                for col in self.table_columns:
                    with ui.card().classes('w-full p-3 mb-2'):
                        with ui.row().classes('w-full items-center gap-4'):
                            # Nome e tipo da coluna
                            with ui.column().classes('flex-1'):
                                ui.label(col['name']).classes('font-bold text-base')
                                ui.label(f"Type: {col['type']}").classes('text-xs text-grey-6')
                            
                            # Seletor de visibilidade
                            visibility_select = ui.select(
                                options={
                                    'public': '👁️ Public (all users see)',
                                    'restricted': '🔒 Restricted (only authorized)',
                                    'masked': '🎭 Restricted + Masked (hash for analysts)'
                                },
                                value=self.column_visibility.get(col['name'], 'public'),
                                label='Visibility Level',
                                on_change=lambda e, c=col['name']: self.update_column_visibility(c, e.value)
                            ).classes('w-80')
    
    def update_column_visibility(self, column_name, visibility):
        """Atualiza visibilidade da coluna"""
        self.column_visibility[column_name] = visibility
        ui.notify(f"Column '{column_name}' set to '{visibility}'", type="info")
    
    def add_user_to_level(self, level):
        """Adiciona usuário a um nível de acesso"""
        email_input = getattr(self, f'{level}_email_input')
        email = email_input.value.strip()
        
        if email and '@' in email:
            if email not in self.user_access[level]:
                self.user_access[level].append(email)
                self.refresh_user_list(level)
                email_input.value = ''
                ui.notify(f"User added to {level} access", type="positive")
            else:
                ui.notify("User already in this level", type="warning")
        else:
            ui.notify("Invalid email", type="warning")
    
    def remove_user_from_level(self, level, email):
        """Remove usuário de um nível"""
        if email in self.user_access[level]:
            self.user_access[level].remove(email)
            self.refresh_user_list(level)
            ui.notify(f"User removed from {level} access", type="info")
    
    def refresh_user_list(self, level):
        """Atualiza lista de usuários de um nível"""
        container = getattr(self, f'{level}_users_container')
        if container:
            container.clear()
            with container:
                if not self.user_access[level]:
                    ui.label("No users added yet").classes('text-grey-5 italic text-sm')
                else:
                    for email in self.user_access[level]:
                        with ui.row().classes('w-full items-center justify-between p-2 border rounded mb-1'):
                            ui.label(email).classes('text-sm flex-1')
                            ui.button(
                                icon='delete',
                                on_click=lambda e=email, l=level: self.remove_user_from_level(l, e)
                            ).props('flat dense size=sm color=negative')
    
    def generate_views_sql(self):
        """Gera SQL das 3 views"""
        if not self.selected_dataset or not self.selected_table:
            ui.notify("Please select dataset and table first", type="warning")
            return
        
        base_name = self.selected_table
        
        # Separar colunas por visibilidade
        public_cols = [col['name'] for col in self.table_columns 
                      if self.column_visibility[col['name']] == 'public']
        restricted_cols = [col['name'] for col in self.table_columns 
                          if self.column_visibility[col['name']] in ['restricted', 'masked']]
        masked_cols = [col['name'] for col in self.table_columns 
                      if self.column_visibility[col['name']] == 'masked']
        
        if not restricted_cols:
            ui.notify("⚠️ No restricted columns configured!", type="warning")
            return
        
        # VIEW 1: FULL (todas colunas)
        all_cols = [col['name'] for col in self.table_columns]
        sql_full = f"""-- VIEW FULL: All columns (for authorized users)
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.vw_{base_name}_full` AS
SELECT
  {(','+chr(10)+'  ').join(all_cols)}
FROM `{self.project_id}.{self.selected_dataset}.{base_name}`;"""
        
        # VIEW 2: MASKED (todas colunas, mas restritas com hash)
        masked_select = []
        for col in self.table_columns:
            if col['name'] in masked_cols:
                masked_select.append(f"TO_BASE64(SHA256(CAST({col['name']} AS STRING))) AS {col['name']}")
            else:
                masked_select.append(col['name'])
        
        sql_masked = f"""-- VIEW MASKED: Restricted columns shown as hash
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.vw_{base_name}_masked` AS
SELECT
  {(','+chr(10)+'  ').join(masked_select)}
FROM `{self.project_id}.{self.selected_dataset}.{base_name}`;"""
        
        # VIEW 3: PUBLIC (apenas colunas públicas)
        sql_public = f"""-- VIEW PUBLIC: Only public columns (restricted columns hidden)
CREATE OR REPLACE VIEW `{self.project_id}.{self.selected_dataset}.vw_{base_name}_public` AS
SELECT
  {(','+chr(10)+'  ').join(public_cols)}
FROM `{self.project_id}.{self.selected_dataset}.{base_name}`;"""
        
        # SQL completo
        full_sql = f"""{sql_full}

{sql_masked}

{sql_public}"""
        
        # Mostrar dialog
        with ui.dialog() as sql_dialog, ui.card().classes('w-full max-w-5xl'):
            ui.label('Generated SQL - 3 Views').classes('text-h6 font-bold mb-4')
            
            # Resumo
            with ui.card().classes('w-full bg-blue-50 p-3 mb-4'):
                ui.label('📊 Views Summary:').classes('font-bold text-sm mb-2')
                ui.label(f'  • vw_{base_name}_full: {len(all_cols)} columns (all real)').classes('text-xs')
                ui.label(f'  • vw_{base_name}_masked: {len(all_cols)} columns ({len(masked_cols)} hashed)').classes('text-xs')
                ui.label(f'  • vw_{base_name}_public: {len(public_cols)} columns (restricted hidden)').classes('text-xs')
            
            with ui.card().classes('w-full bg-purple-50 p-3 mb-4'):
                ui.label('👥 User Assignments:').classes('font-bold text-sm mb-2')
                ui.label(f'  • Full access: {len(self.user_access["full"])} users').classes('text-xs')
                ui.label(f'  • Masked access: {len(self.user_access["masked"])} users').classes('text-xs')
                ui.label(f'  • Public access: {len(self.user_access["public"])} users').classes('text-xs')
            
            ui.code(full_sql, language='sql').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Close', on_click=sql_dialog.close).props('flat')
                ui.button('Copy SQL', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{full_sql}`)')).props('color=primary')
        
        sql_dialog.open()
        self.generated_sql = full_sql
    
    def create_views(self):
        """Cria as 3 views no BigQuery"""
        if not hasattr(self, 'generated_sql'):
            ui.notify("Please generate SQL first", type="warning")
            return
        
        try:
            # Executar SQL
            query_job = client.query(self.generated_sql)
            query_job.result()
            
            # Log audit
            self.audit_service.log_action(
                action='CREATE_DYNAMIC_COLUMN_VIEWS',
                resource_type='DYNAMIC_VIEWS',
                resource_name=f"{self.selected_dataset}.{self.selected_table}",
                status='SUCCESS',
                details={
                    'source_table': f"{self.selected_dataset}.{self.selected_table}",
                    'public_columns': [k for k, v in self.column_visibility.items() if v == 'public'],
                    'restricted_columns': [k for k, v in self.column_visibility.items() if v in ['restricted', 'masked']],
                    'user_assignments': self.user_access
                }
            )
            
            ui.notify(f"✅ 3 views created successfully!", type="positive")
            
            # Mostrar guia de uso
            self.show_usage_guide()
            
        except Exception as e:
            self.audit_service.log_action(
                action='CREATE_DYNAMIC_COLUMN_VIEWS',
                resource_type='DYNAMIC_VIEWS',
                resource_name=f"{self.selected_dataset}.{self.selected_table}",
                status='FAILED',
                error_message=str(e)
            )
            ui.notify(f"Error creating views: {e}", type="negative")
    
    def show_usage_guide(self):
        """Mostra guia de uso das views"""
        with ui.dialog() as guide_dialog, ui.card().classes('w-full max-w-3xl'):
            ui.label('✅ Views Created Successfully!').classes('text-h5 font-bold text-green-600 mb-4')
            ui.label('Usage Guide:').classes('text-h6 font-bold mb-2')
            
            base_name = self.selected_table
            
            with ui.card().classes('w-full bg-green-50 p-3 mb-2'):
                ui.label('👑 FULL ACCESS Users:').classes('font-bold text-sm mb-1')
                for user in self.user_access['full']:
                    ui.label(f'  • {user}').classes('text-xs')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.vw_{base_name}_full`;", language='sql').classes('w-full text-xs')
            
            with ui.card().classes('w-full bg-purple-50 p-3 mb-2'):
                ui.label('🎭 MASKED ACCESS Users:').classes('font-bold text-sm mb-1')
                for user in self.user_access['masked']:
                    ui.label(f'  • {user}').classes('text-xs')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.vw_{base_name}_masked`;", language='sql').classes('w-full text-xs')
            
            with ui.card().classes('w-full bg-blue-50 p-3 mb-2'):
                ui.label('👁️ PUBLIC ACCESS Users:').classes('font-bold text-sm mb-1')
                for user in self.user_access['public']:
                    ui.label(f'  • {user}').classes('text-xs')
                ui.code(f"SELECT * FROM `{self.selected_dataset}.vw_{base_name}_public`;", language='sql').classes('w-full text-xs')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=guide_dialog.close).props('color=primary')
        
        guide_dialog.open()
    
    def render_ui(self):
        with theme.frame('Dynamic Column Security'):
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                # STEP 1: Select Source
                with ui.step('Select Source Table'):
                    ui.label('Choose the table to configure dynamic column security').classes('text-caption mb-4')
                    
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
                
                # STEP 2: Configure Column Visibility
                with ui.step('Configure Column Visibility'):
                    ui.label('Define which columns are sensitive').classes('text-caption mb-4')
                    
                    self.columns_container = ui.column().classes('w-full')
                    
                    # Info box
                    with ui.card().classes('w-full bg-blue-50 p-3 mt-4'):
                        ui.label('ℹ️ Visibility Levels:').classes('text-sm font-bold mb-2')
                        with ui.column().classes('gap-1'):
                            ui.label('• Public: All users see this column').classes('text-xs')
                            ui.label('• Restricted: Only authorized users see real data').classes('text-xs')
                            ui.label('• Restricted + Masked: Analysts see hash, others hidden').classes('text-xs')
                    
                    # Botão para renderizar colunas
                    ui.button(
                        'LOAD COLUMNS',
                        icon='refresh',
                        on_click=self.render_column_visibility_config
                    ).props('color=primary').classes('mt-2')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 3: Assign User Access
                with ui.step('Assign User Access Levels'):
                    ui.label('Assign users to different access levels').classes('text-caption mb-4')
                    
                    with ui.column().classes('w-full gap-4'):
                        # FULL ACCESS
                        with ui.card().classes('w-full p-4 bg-green-50'):
                            ui.label('👑 FULL ACCESS (see all columns real)').classes('font-bold mb-2')
                            with ui.row().classes('w-full gap-2'):
                                self.full_email_input = ui.input(
                                    placeholder='user@company.com'
                                ).classes('flex-1')
                                ui.button(
                                    'ADD',
                                    icon='add',
                                    on_click=lambda: self.add_user_to_level('full')
                                ).props('color=positive')
                            self.full_users_container = ui.column().classes('w-full mt-2')
                            self.refresh_user_list('full')
                        
                        # MASKED ACCESS
                        with ui.card().classes('w-full p-4 bg-purple-50'):
                            ui.label('🎭 MASKED ACCESS (restricted columns as hash)').classes('font-bold mb-2')
                            with ui.row().classes('w-full gap-2'):
                                self.masked_email_input = ui.input(
                                    placeholder='analyst@company.com'
                                ).classes('flex-1')
                                ui.button(
                                    'ADD',
                                    icon='add',
                                    on_click=lambda: self.add_user_to_level('masked')
                                ).props('color=purple')
                            self.masked_users_container = ui.column().classes('w-full mt-2')
                            self.refresh_user_list('masked')
                        
                        # PUBLIC ACCESS
                        with ui.card().classes('w-full p-4 bg-blue-50'):
                            ui.label('👁️ PUBLIC ACCESS (restricted columns hidden)').classes('font-bold mb-2')
                            with ui.row().classes('w-full gap-2'):
                                self.public_email_input = ui.input(
                                    placeholder='viewer@company.com'
                                ).classes('flex-1')
                                ui.button(
                                    'ADD',
                                    icon='add',
                                    on_click=lambda: self.add_user_to_level('public')
                                ).props('color=blue')
                            self.public_users_container = ui.column().classes('w-full mt-2')
                            self.refresh_user_list('public')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
                        ui.button('NEXT', icon='arrow_forward', on_click=stepper.next).props('color=primary')
                
                # STEP 4: Review and Create
                with ui.step('Review and Create'):
                    ui.label('Review configuration and create views').classes('text-caption mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        ui.button('GENERATE SQL', icon='code', on_click=self.generate_views_sql).props('color=blue')
                        ui.button('CREATE VIEWS', icon='check_circle', on_click=self.create_views).props('color=positive')
                    
                    with ui.stepper_navigation():
                        ui.button('BACK', icon='arrow_back', on_click=stepper.previous).props('flat')
    
    def run(self):
        pass
