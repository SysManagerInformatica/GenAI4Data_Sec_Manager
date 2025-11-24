"""
All pages registration - Simplified but complete
"""
from nicegui import ui, app

def create():
    """Register all application pages"""
    
    # ==================== RLS Pages ====================
    @ui.page('/rls')
    def rls_main():
        from theme import frame
        with frame('Row Level Security'):
            ui.label('RLS Management').classes('text-2xl font-bold mb-4')
            with ui.grid(columns=2).classes('w-full gap-4'):
                ui.card().classes('p-4 cursor-pointer hover:shadow-lg').on('click', lambda: ui.run_javascript('window.location.href="/rls/users"')).content = lambda: (
                    ui.icon('person_add', size='48px', color='primary'),
                    ui.label('Create RLS for Users').classes('text-lg font-semibold')
                )
                ui.card().classes('p-4 cursor-pointer hover:shadow-lg').on('click', lambda: ui.run_javascript('window.location.href="/rls/groups"')).content = lambda: (
                    ui.icon('group_add', size='48px', color='primary'),
                    ui.label('Create RLS for Groups').classes('text-lg font-semibold')
                )
    
    @ui.page('/rls/users')
    def rls_users():
        from theme import frame
        with frame('RLS - Users'):
            ui.label('Create RLS Policy for Users').classes('text-2xl font-bold mb-4')
            ui.label('This feature allows you to create Row Level Security policies based on individual users.').classes('text-gray-600')
            # Placeholder for actual functionality
            ui.notification('Feature in development', color='info')
    
    @ui.page('/rls/groups')
    def rls_groups():
        from theme import frame
        with frame('RLS - Groups'):
            ui.label('Create RLS Policy for Groups').classes('text-2xl font-bold mb-4')
            ui.label('This feature allows you to create Row Level Security policies based on user groups.').classes('text-gray-600')
            # Placeholder for actual functionality
            ui.notification('Feature in development', color='info')
    
    # ==================== CLS Pages ====================
    @ui.page('/cls')
    def cls_main():
        from theme import frame
        with frame('Column Level Security'):
            ui.label('CLS Management').classes('text-2xl font-bold mb-4')
            with ui.grid(columns=2).classes('w-full gap-4'):
                ui.card().classes('p-4 cursor-pointer hover:shadow-lg').on('click', lambda: ui.run_javascript('window.location.href="/cls/taxonomies"')).content = lambda: (
                    ui.icon('category', size='48px', color='primary'),
                    ui.label('Manage Taxonomies').classes('text-lg font-semibold')
                )
                ui.card().classes('p-4 cursor-pointer hover:shadow-lg').on('click', lambda: ui.run_javascript('window.location.href="/cls/tags"')).content = lambda: (
                    ui.icon('label', size='48px', color='primary'),
                    ui.label('Policy Tags').classes('text-lg font-semibold')
                )
    
    @ui.page('/cls/taxonomies')
    def cls_taxonomies():
        from theme import frame
        with frame('CLS - Taxonomies'):
            ui.label('Manage Taxonomies').classes('text-2xl font-bold mb-4')
            ui.label('Create and manage data classification taxonomies.').classes('text-gray-600')
            # Placeholder for actual functionality
            ui.notification('Feature in development', color='info')
    
    @ui.page('/cls/tags')
    def cls_tags():
        from theme import frame
        with frame('CLS - Policy Tags'):
            ui.label('Manage Policy Tags').classes('text-2xl font-bold mb-4')
            ui.label('Create and apply policy tags to columns.').classes('text-gray-600')
            # Placeholder for actual functionality
            ui.notification('Feature in development', color='info')
    
    # ==================== Admin Pages ====================
    @ui.page('/control_access')
    def control_access_page():
        from theme import frame
        user_info = app.storage.user.get('user_info', {})
        role = user_info.get('role', 'VIEWER')
        
        with frame('Control Access'):
            if role not in ['OWNER', 'ADMIN']:
                ui.icon('lock', size='64px', color='red').classes('mx-auto')
                ui.label('Access Denied').classes('text-2xl font-bold text-red-600 text-center')
                ui.label('Only OWNER and ADMIN roles can access this page.').classes('text-gray-600 text-center')
                return
            
            ui.label('User Management').classes('text-2xl font-bold mb-4')
            
            # Simple user table placeholder
            with ui.card().classes('w-full p-4'):
                ui.label('Authorized Users').classes('text-lg font-semibold mb-2')
                
                # Sample data
                users_data = [
                    ['lucas.carvalhal@sysmanager.com.br', 'Lucas Carvalhal', 'OWNER', 'Active'],
                    ['admin@sysmanager.com.br', 'Admin User', 'ADMIN', 'Active'],
                ]
                
                columns = [
                    {'name': 'email', 'label': 'Email', 'field': 'email'},
                    {'name': 'name', 'label': 'Name', 'field': 'name'},
                    {'name': 'role', 'label': 'Role', 'field': 'role'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'}
                ]
                
                rows = [
                    {'email': user[0], 'name': user[1], 'role': user[2], 'status': user[3]}
                    for user in users_data
                ]
                
                ui.table(columns=columns, rows=rows, row_key='email').classes('w-full')
                
                with ui.row().classes('mt-4'):
                    ui.button('Add User', icon='person_add', color='primary')
                    ui.button('Edit Roles', icon='edit', color='secondary')
    
    @ui.page('/audit_logs')
    def audit_logs_page():
        from theme import frame
        user_info = app.storage.user.get('user_info', {})
        role = user_info.get('role', 'VIEWER')
        
        with frame('Audit Logs'):
            if role not in ['OWNER', 'ADMIN']:
                ui.icon('lock', size='64px', color='red').classes('mx-auto')
                ui.label('Access Denied').classes('text-2xl font-bold text-red-600 text-center')
                ui.label('Only OWNER and ADMIN roles can view audit logs.').classes('text-gray-600 text-center')
                return
            
            ui.label('System Audit Logs').classes('text-2xl font-bold mb-4')
            
            # Sample audit log
            with ui.card().classes('w-full p-4'):
                ui.label('Recent Activity').classes('text-lg font-semibold mb-2')
                
                logs = [
                    {'time': '2024-11-23 22:15:00', 'user': 'lucas.carvalhal@sysmanager.com.br', 'action': 'USER_LOGIN', 'status': 'SUCCESS'},
                    {'time': '2024-11-23 22:10:00', 'user': 'admin@sysmanager.com.br', 'action': 'POLICY_CREATED', 'status': 'SUCCESS'},
                ]
                
                for log in logs:
                    with ui.card().classes('w-full p-2 mb-2'):
                        with ui.row().classes('items-center'):
                            ui.label(log['time']).classes('text-sm text-gray-600')
                            ui.label('|').classes('mx-2')
                            ui.label(log['user']).classes('text-sm')
                            ui.label('|').classes('mx-2')
                            ui.label(log['action']).classes('text-sm font-semibold')
                            ui.space()
                            color = 'green' if log['status'] == 'SUCCESS' else 'red'
                            ui.badge(log['status'], color=color)
    
    print("✓ All pages registered successfully")
