"""
Control Access - User Management Page
"""
from nicegui import ui, app
from google.cloud import bigquery
from datetime import datetime
import os

PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')

def create():
    @ui.page('/control_access')
    def control_access_page():
        from theme import frame
        
        # Check permissions
        user_info = app.storage.user.get('user_info', {})
        user_role = user_info.get('role', 'VIEWER')
        
        with frame('Control Access'):
            if user_role not in ['OWNER', 'ADMIN']:
                with ui.column().classes('w-full items-center mt-8'):
                    ui.icon('lock', size='64px', color='red')
                    ui.label('Access Denied').classes('text-2xl font-bold text-red-600')
                    ui.label('You need OWNER or ADMIN role to access this page').classes('text-gray-600')
                return
            
            ui.label('User Management').classes('text-2xl font-bold mb-4')
            
            # Create tabs correctly - removed duplicate 'name' argument
            with ui.tabs().classes('w-full') as tabs:
                users_tab = ui.tab('Users', icon='people')
                add_user_tab = ui.tab('Add User', icon='person_add')
                if user_role == 'OWNER':
                    roles_tab = ui.tab('Roles', icon='admin_panel_settings')
            
            with ui.tab_panels(tabs, value=users_tab).classes('w-full'):
                # Users Panel
                with ui.tab_panel(users_tab):
                    # Search bar
                    search_input = ui.input('Search users...', on_change=lambda: load_users()).props('clearable').classes('w-full max-w-md mb-4')
                    
                    # Users table container
                    users_container = ui.column().classes('w-full')
                    
                    def load_users():
                        users_container.clear()
                        with users_container:
                            try:
                                client = bigquery.Client(project=PROJECT_ID)
                                query = """
                                    SELECT user_id, email, name, role, department, company, is_active, last_login
                                    FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                                    ORDER BY name
                                """
                                
                                results = list(client.query(query).result())
                                
                                if results:
                                    # Create data for the table
                                    columns = [
                                        {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                                        {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'center'},
                                        {'name': 'department', 'label': 'Department', 'field': 'department', 'align': 'left'},
                                        {'name': 'company', 'label': 'Company', 'field': 'company', 'align': 'left'},
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
                                            'company': user.company or 'Not set',
                                            'status': 'Active' if user.is_active else 'Inactive',
                                            'user_id': user.user_id
                                        })
                                    
                                    # Create table
                                    table = ui.table(
                                        columns=columns,
                                        rows=rows,
                                        row_key='email',
                                        pagination={'rowsPerPage': 10}
                                    ).classes('w-full')
                                    
                                    # Add actions slot
                                    table.add_slot('body-cell-status', '''
                                        <q-td :props="props">
                                            <q-badge :color="props.value === 'Active' ? 'green' : 'red'">
                                                {{ props.value }}
                                            </q-badge>
                                        </q-td>
                                    ''')
                                    
                                    table.add_slot('body-cell-actions', '''
                                        <q-td :props="props">
                                            <q-btn size="sm" color="primary" round dense flat icon="edit" @click="$parent.$emit('edit', props.row)">
                                                <q-tooltip>Edit user</q-tooltip>
                                            </q-btn>
                                            <q-btn size="sm" color="red" round dense flat icon="delete" @click="$parent.$emit('delete', props.row)">
                                                <q-tooltip>Delete user</q-tooltip>
                                            </q-btn>
                                        </q-td>
                                    ''')
                                    
                                    # Handle events
                                    def handle_edit(e):
                                        ui.notify(f'Edit user: {e.args["email"]}', color='info')
                                    
                                    def handle_delete(e):
                                        ui.notify(f'Delete user: {e.args["email"]}', color='warning')
                                    
                                    table.on('edit', handle_edit)
                                    table.on('delete', handle_delete)
                                    
                                else:
                                    ui.label('No users found').classes('text-gray-500')
                                    
                            except Exception as e:
                                ui.notification(f'Error loading users: {str(e)}', color='red')
                    
                    # Load users on page load
                    load_users()
                
                # Add User Panel
                with ui.tab_panel(add_user_tab):
                    with ui.card().classes('w-full max-w-2xl'):
                        ui.label('Add New User').classes('text-xl font-bold mb-4')
                        
                        with ui.column().classes('w-full gap-4'):
                            email_input = ui.input('Email', placeholder='user@example.com').classes('w-full')
                            name_input = ui.input('Name', placeholder='Full Name').classes('w-full')
                            
                            role_select = ui.select(
                                'Role',
                                options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER'],
                                value='VIEWER'
                            ).classes('w-full')
                            
                            department_input = ui.input('Department', placeholder='e.g., IT, Sales').classes('w-full')
                            company_input = ui.input('Company', placeholder='Company Name').classes('w-full')
                            
                            def add_user():
                                if not email_input.value:
                                    ui.notify('Email is required', color='red')
                                    return
                                
                                try:
                                    client = bigquery.Client(project=PROJECT_ID)
                                    
                                    # Insert new user
                                    query = """
                                        INSERT INTO `sys-googl-cortex-security.rls_manager.authorized_users`
                                        (user_id, email, name, role, department, company, is_active, created_at, created_by)
                                        VALUES
                                        (GENERATE_UUID(), @email, @name, @role, @department, @company, TRUE, CURRENT_TIMESTAMP(), @created_by)
                                    """
                                    
                                    job_config = bigquery.QueryJobConfig(
                                        query_parameters=[
                                            bigquery.ScalarQueryParameter("email", "STRING", email_input.value),
                                            bigquery.ScalarQueryParameter("name", "STRING", name_input.value or None),
                                            bigquery.ScalarQueryParameter("role", "STRING", role_select.value),
                                            bigquery.ScalarQueryParameter("department", "STRING", department_input.value or None),
                                            bigquery.ScalarQueryParameter("company", "STRING", company_input.value or None),
                                            bigquery.ScalarQueryParameter("created_by", "STRING", user_info.get('email', ''))
                                        ]
                                    )
                                    
                                    client.query(query, job_config=job_config).result()
                                    
                                    ui.notify(f'User {email_input.value} added successfully', color='green')
                                    
                                    # Clear form
                                    email_input.value = ''
                                    name_input.value = ''
                                    role_select.value = 'VIEWER'
                                    department_input.value = ''
                                    company_input.value = ''
                                    
                                except Exception as e:
                                    ui.notify(f'Error adding user: {str(e)}', color='red')
                            
                            ui.button('Add User', on_click=add_user, icon='person_add').classes('mt-4')
                
                # Roles Panel (OWNER only)
                if user_role == 'OWNER':
                    with ui.tab_panel(roles_tab):
                        ui.label('Role Permissions').classes('text-xl font-bold mb-4')
                        
                        with ui.column().classes('w-full gap-4'):
                            # Role cards
                            roles_info = [
                                ('OWNER', 'red', 'Full system control', [
                                    'Manage all users and roles',
                                    'Create/edit/delete all policies',
                                    'View all audit logs',
                                    'System configuration'
                                ]),
                                ('ADMIN', 'orange', 'Administrative access', [
                                    'Create/edit/delete policies',
                                    'View all audit logs',
                                    'Cannot manage users'
                                ]),
                                ('EDITOR', 'blue', 'Edit permissions', [
                                    'Create new policies',
                                    'Edit own policies',
                                    'View limited audit logs'
                                ]),
                                ('VIEWER', 'green', 'Read-only access', [
                                    'View policies',
                                    'View own audit logs',
                                    'No edit permissions'
                                ])
                            ]
                            
                            for role, color, description, permissions in roles_info:
                                with ui.card().classes('w-full'):
                                    with ui.row().classes('items-center gap-4'):
                                        ui.badge(role, color=color)
                                        ui.label(description).classes('text-lg')
                                    
                                    ui.separator()
                                    
                                    with ui.column().classes('gap-1 mt-2'):
                                        for perm in permissions:
                                            ui.label(f'• {perm}').classes('text-sm text-gray-600')
