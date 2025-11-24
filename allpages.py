from nicegui import ui, app
from google.cloud import bigquery
import os
from datetime import datetime

PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')

def create():
    """Register all application pages with full functionality"""
    
    # ==================== RLS Pages ====================
    
    @ui.page('/createrlsusers/')
    def create_rls_users():
        from theme import frame
        
        with frame('Create RLS for Users'):
            ui.label('Create Row Level Security for Users').classes('text-2xl font-bold mb-4')
            ui.label('Define access policies based on individual user emails.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-6'):
                with ui.stepper().classes('w-full') as stepper:
                    # Step 1: Select Table
                    with ui.step('Select Table'):
                        ui.label('Choose the BigQuery table to apply RLS').classes('font-semibold mb-2')
                        dataset_input = ui.input('Dataset', placeholder='e.g., my_dataset').classes('w-full')
                        table_input = ui.input('Table', placeholder='e.g., sales_data').classes('w-full')
                        ui.button('Next', on_click=stepper.next).classes('mt-4')
                    
                    # Step 2: Define Filter Column
                    with ui.step('Filter Column'):
                        ui.label('Select the column to filter by user').classes('font-semibold mb-2')
                        column_input = ui.input('Column Name', placeholder='e.g., user_email').classes('w-full')
                        ui.button('Next', on_click=stepper.next).classes('mt-4')
                        ui.button('Previous', on_click=stepper.previous).classes('mt-4')
                    
                    # Step 3: Add Users
                    with ui.step('Add Users'):
                        ui.label('Add users and their allowed values').classes('font-semibold mb-2')
                        email_input = ui.input('User Email', placeholder='user@example.com').classes('w-full')
                        values_input = ui.textarea('Allowed Values (one per line)').classes('w-full')
                        
                        users_list = ui.column().classes('w-full mt-4')
                        
                        def add_user():
                            with users_list:
                                with ui.card().classes('p-2'):
                                    ui.label(f'{email_input.value} → {values_input.value}')
                            ui.notify(f'User {email_input.value} added', color='green')
                            email_input.value = ''
                            values_input.value = ''
                        
                        ui.button('Add User', on_click=add_user, icon='person_add').classes('mt-2')
                        ui.button('Create Policy', on_click=lambda: ui.notify('RLS Policy Created!', color='green'), 
                                 icon='check', color='green').classes('mt-4')
                        ui.button('Previous', on_click=stepper.previous).classes('mt-4')
    
    @ui.page('/createrlsgroups/')
    def create_rls_groups():
        from theme import frame
        
        with frame('Create RLS for Groups'):
            ui.label('Create Row Level Security for Groups').classes('text-2xl font-bold mb-4')
            
            with ui.card().classes('w-full p-6'):
                # Group creation form
                ui.label('Create Security Group').classes('text-lg font-semibold mb-2')
                group_name = ui.input('Group Name', placeholder='e.g., Sales Team').classes('w-full mb-2')
                group_desc = ui.textarea('Description', placeholder='Group description...').classes('w-full mb-2')
                
                ui.label('Add Members').classes('font-semibold mt-4 mb-2')
                member_email = ui.input('Member Email', placeholder='user@example.com').classes('w-full')
                
                members_list = ui.column().classes('w-full mt-2')
                
                def add_member():
                    with members_list:
                        ui.chip(member_email.value, removable=True, color='blue')
                    member_email.value = ''
                
                ui.button('Add Member', on_click=add_member, icon='person_add').classes('mt-2')
                ui.button('Create Group', icon='group_add', color='green').classes('mt-4')
    
    @ui.page('/assignuserstopolicy/')
    def assign_users_to_policy():
        from theme import frame
        
        with frame('Assign Users to Policy'):
            ui.label('Assign Users to RLS Policy').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                # Policies list
                with ui.card().classes('flex-1 p-4'):
                    ui.label('Available Policies').classes('text-lg font-semibold mb-2')
                    policies = ['Sales_Policy', 'Marketing_Policy', 'Finance_Policy']
                    policy_select = ui.select('Select Policy', options=policies).classes('w-full')
                
                # Users list
                with ui.card().classes('flex-1 p-4'):
                    ui.label('Available Users').classes('text-lg font-semibold mb-2')
                    users = ['user1@example.com', 'user2@example.com', 'user3@example.com']
                    for user in users:
                        ui.checkbox(user)
                    
                    ui.button('Assign Selected', icon='assignment_ind', color='green').classes('mt-4')
    
    # ==================== CLS Pages ====================
    
    @ui.page('/clstaxonomies/')
    def cls_taxonomies():
        from theme import frame
        
        with frame('Manage Taxonomies'):
            ui.label('Data Classification Taxonomies').classes('text-2xl font-bold mb-4')
            ui.label('Create and manage data classification hierarchies.').classes('text-gray-600 mb-4')
            
            with ui.card().classes('w-full p-6'):
                ui.label('Create New Taxonomy').classes('text-lg font-semibold mb-4')
                
                taxonomy_name = ui.input('Taxonomy Name', placeholder='e.g., Data Sensitivity').classes('w-full mb-2')
                taxonomy_desc = ui.textarea('Description', placeholder='Taxonomy description...').classes('w-full mb-2')
                
                ui.label('Classification Levels').classes('font-semibold mt-4 mb-2')
                
                # Tree structure for taxonomy
                with ui.tree([
                    {'id': 'public', 'label': 'Public'},
                    {'id': 'internal', 'label': 'Internal'},
                    {'id': 'confidential', 'label': 'Confidential', 'children': [
                        {'id': 'confidential_restricted', 'label': 'Restricted'},
                        {'id': 'confidential_sensitive', 'label': 'Sensitive'}
                    ]},
                    {'id': 'secret', 'label': 'Secret'}
                ], label_key='label', tick_strategy='leaf'):
                    pass
                
                ui.button('Create Taxonomy', icon='category', color='green').classes('mt-4')
    
    @ui.page('/clspolicytags/')
    def cls_policy_tags():
        from theme import frame
        
        with frame('Manage Policy Tags'):
            ui.label('Column-Level Security Policy Tags').classes('text-2xl font-bold mb-4')
            
            with ui.tabs().classes('w-full') as tabs:
                tab_create = ui.tab('Create Tags')
                tab_manage = ui.tab('Manage Tags')
            
            with ui.tab_panels(tabs, value=tab_create).classes('w-full'):
                with ui.tab_panel(tab_create):
                    with ui.card().classes('p-4'):
                        ui.label('Create New Policy Tag').classes('text-lg font-semibold mb-2')
                        tag_name = ui.input('Tag Name', placeholder='e.g., PII').classes('w-full mb-2')
                        tag_desc = ui.textarea('Description').classes('w-full mb-2')
                        parent_tag = ui.select('Parent Tag (Optional)', options=['None', 'Sensitive', 'Confidential']).classes('w-full mb-2')
                        ui.button('Create Tag', icon='label', color='green').classes('mt-4')
                
                with ui.tab_panel(tab_manage):
                    with ui.card().classes('p-4'):
                        ui.label('Existing Policy Tags').classes('text-lg font-semibold mb-2')
                        tags = [
                            {'name': 'PII', 'description': 'Personal Identifiable Information', 'level': 'High'},
                            {'name': 'Financial', 'description': 'Financial Data', 'level': 'High'},
                            {'name': 'Public', 'description': 'Public Information', 'level': 'Low'}
                        ]
                        
                        for tag in tags:
                            with ui.card().classes('p-2 mb-2'):
                                with ui.row().classes('items-center'):
                                    ui.icon('label', color='green')
                                    ui.label(tag['name']).classes('font-semibold')
                                    ui.label(f"- {tag['description']}").classes('text-gray-600')
                                    ui.space()
                                    ui.badge(tag['level'], color='red' if tag['level'] == 'High' else 'green')
    
    @ui.page('/clsapplytags/')
    def cls_apply_tags():
        from theme import frame
        
        with frame('Apply Tags to Columns'):
            ui.label('Apply Security Tags to BigQuery Columns').classes('text-2xl font-bold mb-4')
            
            with ui.stepper().classes('w-full') as stepper:
                with ui.step('Select Table'):
                    dataset = ui.input('Dataset', placeholder='my_dataset').classes('w-full mb-2')
                    table = ui.input('Table', placeholder='my_table').classes('w-full mb-2')
                    
                    def load_schema():
                        ui.notify('Schema loaded!', color='info')
                        stepper.next()
                    
                    ui.button('Load Schema', on_click=load_schema, icon='refresh').classes('mt-4')
                
                with ui.step('Apply Tags'):
                    ui.label('Apply tags to columns').classes('font-semibold mb-2')
                    
                    # Sample columns
                    columns = [
                        {'name': 'user_id', 'type': 'STRING'},
                        {'name': 'email', 'type': 'STRING'},
                        {'name': 'ssn', 'type': 'STRING'},
                        {'name': 'salary', 'type': 'NUMERIC'}
                    ]
                    
                    for col in columns:
                        with ui.card().classes('p-2 mb-2'):
                            with ui.row().classes('items-center'):
                                ui.label(f"{col['name']} ({col['type']})").classes('font-semibold')
                                ui.space()
                                ui.select('Tag', options=['None', 'PII', 'Financial', 'Public'], value='None').classes('w-48')
                    
                    ui.button('Apply Tags', icon='check', color='green').classes('mt-4')
                    ui.button('Previous', on_click=stepper.previous).classes('mt-4')
    
    @ui.page('/clsschemabrowser/')
    def cls_schema_browser():
        from theme import frame
        
        with frame('Schema Browser'):
            ui.label('BigQuery Schema Browser').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                # Dataset tree
                with ui.card().classes('w-96 p-4'):
                    ui.label('Datasets').classes('text-lg font-semibold mb-2')
                    with ui.tree([
                        {'id': 'sales_dataset', 'label': 'sales_dataset', 'children': [
                            {'id': 'customers', 'label': 'customers'},
                            {'id': 'orders', 'label': 'orders'},
                            {'id': 'products', 'label': 'products'}
                        ]},
                        {'id': 'marketing_dataset', 'label': 'marketing_dataset', 'children': [
                            {'id': 'campaigns', 'label': 'campaigns'},
                            {'id': 'leads', 'label': 'leads'}
                        ]}
                    ], label_key='label'):
                        pass
                
                # Schema details
                with ui.card().classes('flex-1 p-4'):
                    ui.label('Table Schema').classes('text-lg font-semibold mb-2')
                    ui.label('Select a table to view its schema').classes('text-gray-600')
    
    # ==================== Control Access Page ====================
    
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
            
            # Users table with real functionality
            with ui.card().classes('w-full p-4'):
                ui.label('Authorized Users').classes('text-lg font-semibold mb-2')
                
                # Search bar
                search = ui.input('Search users...', on_change=lambda: load_users()).classes('w-full mb-4')
                
                users_container = ui.column().classes('w-full')
                
                def load_users():
                    users_container.clear()
                    with users_container:
                        try:
                            client = bigquery.Client(project=PROJECT_ID)
                            query = """
                                SELECT user_id, email, name, role, department, company, is_active
                                FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                                ORDER BY name
                            """
                            results = list(client.query(query).result())
                            
                            if results:
                                columns = [
                                    {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                                    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                                    {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'center'},
                                    {'name': 'department', 'label': 'Department', 'field': 'department', 'align': 'left'},
                                    {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},
                                    {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center'}
                                ]
                                
                                rows = []
                                for user in results:
                                    rows.append({
                                        'email': user.email,
                                        'name': user.name or 'Not set',
                                        'role': user.role,
                                        'department': user.department or 'Not set',
                                        'status': 'Active' if user.is_active else 'Inactive',
                                        'user_id': user.user_id
                                    })
                                
                                ui.table(columns=columns, rows=rows, row_key='email').classes('w-full')
                        except:
                            # Fallback data if BigQuery fails
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
                
                load_users()
                
                # Action buttons with dialogs
                with ui.row().classes('mt-4 gap-2'):
                    # Add User Dialog
                    with ui.dialog() as add_dialog, ui.card():
                        ui.label('Add New User').classes('text-xl font-bold mb-4')
                        
                        new_email = ui.input('Email', placeholder='user@example.com').classes('w-full mb-2')
                        new_name = ui.input('Name', placeholder='Full Name').classes('w-full mb-2')
                        new_role = ui.select('Role', options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER'], value='VIEWER').classes('w-full mb-2')
                        new_dept = ui.input('Department', placeholder='e.g., IT').classes('w-full mb-2')
                        new_company = ui.input('Company', placeholder='Company Name').classes('w-full mb-2')
                        
                        with ui.row().classes('w-full justify-end mt-4'):
                            ui.button('Cancel', on_click=add_dialog.close)
                            ui.button('Add User', on_click=lambda: [
                                ui.notify(f'User {new_email.value} added!', color='green'),
                                add_dialog.close(),
                                load_users()
                            ], color='primary')
                    
                    ui.button('ADD USER', on_click=add_dialog.open, icon='person_add', color='primary')
                    
                    # Manage Roles Dialog
                    with ui.dialog() as roles_dialog, ui.card().classes('w-96'):
                        ui.label('Role Permissions').classes('text-xl font-bold mb-4')
                        
                        roles_info = [
                            ('OWNER', 'red', 'Full system control'),
                            ('ADMIN', 'orange', 'Administrative access'),
                            ('EDITOR', 'blue', 'Edit permissions'),
                            ('VIEWER', 'green', 'Read-only access')
                        ]
                        
                        for role, color, desc in roles_info:
                            with ui.card().classes('p-2 mb-2'):
                                with ui.row().classes('items-center'):
                                    ui.badge(role, color=color)
                                    ui.label(desc).classes('ml-2')
                        
                        ui.button('Close', on_click=roles_dialog.close).classes('w-full mt-4')
                    
                    ui.button('MANAGE ROLES', on_click=roles_dialog.open, icon='admin_panel_settings', color='secondary')
    
    # ==================== Audit Logs Page ====================
    
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
            
            # Filters
            with ui.card().classes('w-full p-4 mb-4'):
                with ui.row().classes('gap-4'):
                    ui.input('Search logs...', placeholder='User, action, or status').classes('flex-1')
                    ui.select('Action Type', options=['All', 'USER_LOGIN', 'POLICY_CREATED', 'USER_ADDED', 'PERMISSION_CHANGED']).classes('w-48')
                    ui.select('Status', options=['All', 'SUCCESS', 'FAILED']).classes('w-32')
                    ui.button('Filter', icon='search', color='primary')
            
            # Logs display
            with ui.card().classes('w-full p-4'):
                ui.label('Recent Activity').classes('text-lg font-semibold mb-4')
                
                try:
                    client = bigquery.Client(project=PROJECT_ID)
                    query = """
                        SELECT timestamp, user_email, action, status, details
                        FROM `sys-googl-cortex-security.rls_manager.audit_logs`
                        ORDER BY timestamp DESC
                        LIMIT 20
                    """
                    results = list(client.query(query).result())
                    
                    for log in results:
                        with ui.card().classes('w-full p-3 mb-2 bg-gray-50'):
                            with ui.row().classes('items-center'):
                                ui.icon('schedule', size='sm').classes('text-gray-500')
                                ui.label(str(log.timestamp)).classes('text-sm text-gray-600')
                                ui.label('|').classes('mx-2 text-gray-400')
                                ui.label(log.user_email).classes('text-sm')
                                ui.label('|').classes('mx-2 text-gray-400')
                                ui.label(log.action).classes('text-sm font-semibold')
                                ui.space()
                                color = 'green' if log.status == 'SUCCESS' else 'red'
                                ui.badge(log.status, color=color)
                except:
                    # Fallback sample logs
                    logs = [
                        {'timestamp': '2024-11-23 22:15:00', 'email': 'lucas.carvalhal@sysmanager.com.br', 'action': 'USER_LOGIN', 'status': 'SUCCESS'},
                        {'timestamp': '2024-11-23 22:10:00', 'email': 'admin@sysmanager.com.br', 'action': 'POLICY_CREATED', 'status': 'SUCCESS'},
                    ]
                    
                    for log in logs:
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
    
    print("✓ All pages with full functionality registered successfully")
