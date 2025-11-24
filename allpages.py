"""
All pages registration - Complete version matching menu.py routes
"""
from nicegui import ui, app

def create():
    """Register all application pages"""
    
    # ==================== RLS Pages ====================
    
    @ui.page('/createrlsusers/')
    def create_rls_users():
        from theme import frame
        user_info = app.storage.user.get('user_info', {})
        
        with frame('Create RLS for Users'):
            ui.label('Create Row Level Security for Users').classes('text-2xl font-bold mb-4')
            ui.label('Define access policies based on individual user emails.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
                ui.label('You will be able to:').classes('mt-2 font-semibold')
                ui.label('• Create policies for specific users')
                ui.label('• Define data access rules')
                ui.label('• Apply filters to BigQuery tables')
    
    @ui.page('/createrlsgroups/')
    def create_rls_groups():
        from theme import frame
        
        with frame('Create RLS for Groups'):
            ui.label('Create Row Level Security for Groups').classes('text-2xl font-bold mb-4')
            ui.label('Define access policies based on user groups.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    @ui.page('/assignuserstopolicy/')
    def assign_users_to_policy():
        from theme import frame
        
        with frame('Assign Users to Policy'):
            ui.label('Assign Users to RLS Policy').classes('text-2xl font-bold mb-4')
            ui.label('Map users to existing security policies.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    @ui.page('/assignvaluestogroup/')
    def assign_values_to_group():
        from theme import frame
        
        with frame('Assign Values to Groups'):
            ui.label('Assign Values to Security Groups').classes('text-2xl font-bold mb-4')
            ui.label('Define which data values each group can access.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    # ==================== CLS Pages ====================
    
    @ui.page('/clstaxonomies/')
    def cls_taxonomies():
        from theme import frame
        
        with frame('Manage Taxonomies'):
            ui.label('Data Classification Taxonomies').classes('text-2xl font-bold mb-4')
            ui.label('Create and manage data classification hierarchies.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    @ui.page('/clspolicytags/')
    def cls_policy_tags():
        from theme import frame
        
        with frame('Manage Policy Tags'):
            ui.label('Column-Level Security Policy Tags').classes('text-2xl font-bold mb-4')
            ui.label('Define security tags for column-level access control.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    @ui.page('/clsapplytags/')
    def cls_apply_tags():
        from theme import frame
        
        with frame('Apply Tags to Columns'):
            ui.label('Apply Security Tags to BigQuery Columns').classes('text-2xl font-bold mb-4')
            ui.label('Map policy tags to specific table columns.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    @ui.page('/clsschemabrowser/')
    def cls_schema_browser():
        from theme import frame
        
        with frame('Schema Browser'):
            ui.label('BigQuery Schema Browser').classes('text-2xl font-bold mb-4')
            ui.label('Browse and explore your BigQuery schemas with applied security tags.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('This feature is under development').classes('text-orange-600')
    
    # ==================== Admin Pages ====================
    
    @ui.page('/controlaccess/')
    def control_access_page():
        from theme import frame
        user_info = app.storage.user.get('user_info', {})
        role = user_info.get('role', 'VIEWER')
        
        with frame('Control Access'):
            if role not in ['OWNER', 'ADMIN']:
                with ui.column().classes('items-center mt-8'):
                    ui.icon('lock', size='64px', color='red')
                    ui.label('Access Denied').classes('text-2xl font-bold text-red-600')
                    ui.label('Only OWNER and ADMIN roles can access this page.').classes('text-gray-600')
                return
            
            ui.label('User Access Management').classes('text-2xl font-bold mb-4')
            
            # Users table
            with ui.card().classes('w-full p-4'):
                ui.label('Authorized Users').classes('text-lg font-semibold mb-2')
                
                columns = [
                    {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                    {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'center'},
                    {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'}
                ]
                
                rows = [
                    {'email': 'lucas.carvalhal@sysmanager.com.br', 'name': 'Lucas Carvalhal', 'role': 'OWNER', 'status': 'Active'},
                    {'email': 'admin@sysmanager.com.br', 'name': 'Admin User', 'role': 'ADMIN', 'status': 'Active'},
                ]
                
                ui.table(columns=columns, rows=rows, row_key='email').classes('w-full')
                
                with ui.row().classes('mt-4 gap-2'):
                    ui.button('Add User', icon='person_add', color='primary')
                    ui.button('Manage Roles', icon='admin_panel_settings', color='secondary')
    
    @ui.page('/auditlogs/')
    def audit_logs_page():
        from theme import frame
        user_info = app.storage.user.get('user_info', {})
        role = user_info.get('role', 'VIEWER')
        
        with frame('Audit Logs'):
            if role not in ['OWNER', 'ADMIN']:
                with ui.column().classes('items-center mt-8'):
                    ui.icon('lock', size='64px', color='red')
                    ui.label('Access Denied').classes('text-2xl font-bold text-red-600')
                    ui.label('Only OWNER and ADMIN roles can view audit logs.').classes('text-gray-600')
                return
            
            ui.label('System Audit Logs').classes('text-2xl font-bold mb-4')
            
            with ui.card().classes('w-full p-4'):
                ui.label('Recent Activity').classes('text-lg font-semibold mb-4')
                
                # Sample logs
                logs = [
                    {'timestamp': '2024-11-23 22:15:00', 'email': 'lucas.carvalhal@sysmanager.com.br', 'action': 'USER_LOGIN', 'status': 'SUCCESS'},
                    {'timestamp': '2024-11-23 22:10:00', 'email': 'admin@sysmanager.com.br', 'action': 'POLICY_CREATED', 'status': 'SUCCESS'},
                    {'timestamp': '2024-11-23 22:05:00', 'email': 'lucas.carvalhal@sysmanager.com.br', 'action': 'USER_ADDED', 'status': 'SUCCESS'},
                ]
                
                for log in logs[:5]:  # Show only 5 recent logs
                    with ui.card().classes('w-full p-3 mb-2 bg-gray-50'):
                        with ui.row().classes('items-center'):
                            ui.icon('schedule', size='sm').classes('text-gray-500')
                            ui.label(log['timestamp']).classes('text-sm text-gray-600')
                            ui.label('|').classes('mx-2 text-gray-400')
                            ui.label(log['email']).classes('text-sm')
                            ui.label('|').classes('mx-2 text-gray-400')
                            ui.label(log['action']).classes('text-sm font-semibold')
                            ui.space()
                            color = 'green' if log['status'] == 'SUCCESS' else 'red'
                            ui.badge(log['status'], color=color)
    
    print("✓ All pages registered successfully")
