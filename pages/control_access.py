"""
Control Access - User Management Page
"""
from nicegui import ui, app
from google.cloud import bigquery
from datetime import datetime
import os
import json

PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')

class ControlAccess:
    def __init__(self):
        self.client = None
        self.current_users = []
        
    def run(self):
        """Main run method called by allpages"""
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
            
            # Initialize BigQuery client
            try:
                self.client = bigquery.Client(project=PROJECT_ID)
            except Exception as e:
                ui.notification(f'Error connecting to BigQuery: {str(e)}', color='red')
            
            # Main content
            ui.label('User Management').classes('text-2xl font-bold mb-4')
            
            # Create tabs
            with ui.tabs().classes('w-full') as tabs:
                users_tab = ui.tab('Users', icon='people')
                add_user_tab = ui.tab('Add User', icon='person_add')
                if user_role == 'OWNER':
                    roles_tab = ui.tab('Roles', icon='admin_panel_settings')
            
            with ui.tab_panels(tabs, value=users_tab).classes('w-full'):
                # Users Panel
                with ui.tab_panel(users_tab):
                    self.create_users_panel()
                
                # Add User Panel
                with ui.tab_panel(add_user_tab):
                    self.create_add_user_panel(user_info)
                
                # Roles Panel (OWNER only)
                if user_role == 'OWNER':
                    with ui.tab_panel(roles_tab):
                        self.create_roles_panel()
    
    def create_users_panel(self):
        """Create the users list panel"""
        # Search bar
        search_container = ui.row().classes('w-full mb-4')
        with search_container:
            search_input = ui.input('Search users...', placeholder='Email, name, or role').props('clearable').classes('flex-1')
            refresh_btn = ui.button(icon='refresh', on_click=lambda: self.load_users(users_container))
        
        # Users table container
        users_container = ui.column().classes('w-full')
        
        # Load users initially
        self.load_users(users_container, search_input)
    
    def load_users(self, container, search_input=None):
        """Load users from BigQuery"""
        container.clear()
        
        with container:
            try:
                if self.client:
                    query = """
                        SELECT user_id, email, name, role, department, company, is_active, last_login
                        FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                        ORDER BY name
                    """
                    
                    results = list(self.client.query(query).result())
                    self.current_users = results
                    
                    if results:
                        # Create table
                        columns = [
                            {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left', 'sortable': True},
                            {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left', 'sortable': True},
                            {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'center'},
                            {'name': 'department', 'label': 'Department', 'field': 'department', 'align': 'left'},
                            {'name': 'company', 'label': 'Company', 'field': 'company', 'align': 'left'},
                            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},
                            {'name': 'last_login', 'label': 'Last Login', 'field': 'last_login', 'align': 'center'},
                            {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center'}
                        ]
                        
                        rows = []
                        for user in results:
                            last_login = str(user.last_login)[:19] if user.last_login else 'Never'
                            rows.append({
                                'email': user.email,
                                'name': user.name or 'Not set',
                                'role': user.role,
                                'department': user.department or 'Not set',
                                'company': user.company or 'Not set',
                                'status': 'Active' if user.is_active else 'Inactive',
                                'last_login': last_login,
                                'user_id': user.user_id,
                                'is_active': user.is_active
                            })
                        
                        table = ui.table(
                            columns=columns,
                            rows=rows,
                            row_key='email',
                            pagination={'rowsPerPage': 10, 'sortBy': 'name'}
                        ).classes('w-full')
                        
                        # Add custom slots for formatting
                        table.add_slot('body-cell-role', '''
                            <q-td :props="props">
                                <q-badge :color="props.value === 'OWNER' ? 'red' : 
                                               props.value === 'ADMIN' ? 'orange' : 
                                               props.value === 'EDITOR' ? 'blue' : 'green'">
                                    {{ props.value }}
                                </q-badge>
                            </q-td>
                        ''')
                        
                        table.add_slot('body-cell-status', '''
                            <q-td :props="props">
                                <q-badge :color="props.value === 'Active' ? 'green' : 'red'">
                                    {{ props.value }}
                                </q-badge>
                            </q-td>
                        ''')
                        
                        table.add_slot('body-cell-actions', '''
                            <q-td :props="props">
                                <q-btn size="sm" color="primary" round dense flat icon="edit" 
                                       @click="$parent.$emit('edit', props.row)">
                                    <q-tooltip>Edit user</q-tooltip>
                                </q-btn>
                                <q-btn size="sm" color="red" round dense flat icon="delete" 
                                       @click="$parent.$emit('delete', props.row)">
                                    <q-tooltip>Delete user</q-tooltip>
                                </q-btn>
                            </q-td>
                        ''')
                        
                        # Handle events
                        def handle_edit(e):
                            self.edit_user(e.args)
                        
                        def handle_delete(e):
                            self.delete_user(e.args)
                        
                        table.on('edit', handle_edit)
                        table.on('delete', handle_delete)
                        
                        # Statistics
                        with ui.row().classes('mt-4 gap-4'):
                            ui.badge(f'Total Users: {len(results)}', color='blue')
                            active_count = sum(1 for u in results if u.is_active)
                            ui.badge(f'Active: {active_count}', color='green')
                            ui.badge(f'Inactive: {len(results) - active_count}', color='red')
                    else:
                        ui.label('No users found').classes('text-gray-500')
                else:
                    # Fallback if no BigQuery connection
                    ui.label('Unable to connect to database').classes('text-red-500')
                    
            except Exception as e:
                ui.notification(f'Error loading users: {str(e)}', color='red')
                # Show sample data as fallback
                self.show_sample_data(container)
    
    def show_sample_data(self, container):
        """Show sample data when BigQuery is not available"""
        ui.label('Showing sample data (BigQuery not connected)').classes('text-orange-500 mb-2')
        
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
    
    def create_add_user_panel(self, current_user_info):
        """Create the add user panel"""
        with ui.card().classes('w-full max-w-2xl'):
            ui.label('Add New User').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('w-full gap-4'):
                email_input = ui.input('Email *', placeholder='user@example.com').classes('w-full')
                name_input = ui.input('Name', placeholder='Full Name').classes('w-full')
                
                role_select = ui.select(
                    'Role *',
                    options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER'],
                    value='VIEWER'
                ).classes('w-full')
                
                department_input = ui.input('Department', placeholder='e.g., IT, Sales').classes('w-full')
                company_input = ui.input('Company', placeholder='Company Name').classes('w-full')
                
                def add_user():
                    # Validate
                    if not email_input.value:
                        ui.notify('Email is required', color='red')
                        return
                    
                    if '@' not in email_input.value:
                        ui.notify('Invalid email format', color='red')
                        return
                    
                    try:
                        if self.client:
                            # Check if user already exists
                            check_query = """
                                SELECT COUNT(*) as count
                                FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                                WHERE email = @email
                            """
                            
                            job_config = bigquery.QueryJobConfig(
                                query_parameters=[
                                    bigquery.ScalarQueryParameter("email", "STRING", email_input.value)
                                ]
                            )
                            
                            result = list(self.client.query(check_query, job_config=job_config).result())
                            if result[0].count > 0:
                                ui.notify(f'User {email_input.value} already exists', color='orange')
                                return
                            
                            # Insert new user
                            insert_query = """
                                INSERT INTO `sys-googl-cortex-security.rls_manager.authorized_users`
                                (user_id, email, name, role, department, company, is_active, created_at, created_by)
                                VALUES
                                (GENERATE_UUID(), @email, @name, @role, @department, @company, TRUE, 
                                 CURRENT_TIMESTAMP(), @created_by)
                            """
                            
                            job_config = bigquery.QueryJobConfig(
                                query_parameters=[
                                    bigquery.ScalarQueryParameter("email", "STRING", email_input.value),
                                    bigquery.ScalarQueryParameter("name", "STRING", name_input.value or None),
                                    bigquery.ScalarQueryParameter("role", "STRING", role_select.value),
                                    bigquery.ScalarQueryParameter("department", "STRING", department_input.value or None),
                                    bigquery.ScalarQueryParameter("company", "STRING", company_input.value or None),
                                    bigquery.ScalarQueryParameter("created_by", "STRING", current_user_info.get('email', ''))
                                ]
                            )
                            
                            self.client.query(insert_query, job_config=job_config).result()
                            
                            # Log the action
                            self.log_audit('USER_ADDED', current_user_info.get('email', ''), 
                                         f'Added user: {email_input.value} with role: {role_select.value}', 'SUCCESS')
                            
                            ui.notify(f'User {email_input.value} added successfully', color='green')
                            
                            # Clear form
                            email_input.value = ''
                            name_input.value = ''
                            role_select.value = 'VIEWER'
                            department_input.value = ''
                            company_input.value = ''
                        else:
                            ui.notify('Database connection not available', color='red')
                            
                    except Exception as e:
                        ui.notify(f'Error adding user: {str(e)}', color='red')
                
                ui.button('Add User', on_click=add_user, icon='person_add', color='primary').classes('mt-4')
                
                # Help text
                with ui.card().classes('mt-4 p-4 bg-blue-50'):
                    ui.label('Note:').classes('font-semibold')
                    ui.label('• Email must be from an authorized domain')
                    ui.label('• Users will need to login with Google OAuth')
                    ui.label('• Role determines access permissions in the system')
    
    def create_roles_panel(self):
        """Create the roles management panel"""
        ui.label('Role Permissions').classes('text-xl font-bold mb-4')
        
        with ui.column().classes('w-full gap-4'):
            roles_info = [
                ('OWNER', 'red', 'Full system control', [
                    'Manage all users and roles',
                    'Create/edit/delete all policies',
                    'View all audit logs',
                    'System configuration',
                    'Delete other users'
                ]),
                ('ADMIN', 'orange', 'Administrative access', [
                    'Create/edit/delete policies',
                    'View all audit logs',
                    'Cannot manage users',
                    'Cannot change system settings'
                ]),
                ('EDITOR', 'blue', 'Edit permissions', [
                    'Create new policies',
                    'Edit own policies only',
                    'View limited audit logs',
                    'Cannot manage users'
                ]),
                ('VIEWER', 'green', 'Read-only access', [
                    'View policies only',
                    'View own audit logs only',
                    'No edit permissions',
                    'Cannot create or modify anything'
                ])
            ]
            
            for role, color, description, permissions in roles_info:
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-4 mb-2'):
                        ui.badge(role, color=color).props('text-color=white')
                        ui.label(description).classes('text-lg font-semibold')
                    
                    ui.separator()
                    
                    with ui.column().classes('gap-1 mt-2'):
                        for perm in permissions:
                            with ui.row().classes('items-center gap-2'):
                                icon = 'check_circle' if 'Cannot' not in perm else 'cancel'
                                color = 'green' if 'Cannot' not in perm else 'red'
                                ui.icon(icon, color=color, size='sm')
                                ui.label(perm).classes('text-sm text-gray-600')
    
    def edit_user(self, user_data):
        """Edit user dialog"""
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Edit User: {user_data["email"]}').classes('text-xl font-bold mb-4')
            
            name_input = ui.input('Name', value=user_data.get('name', '')).classes('w-full mb-2')
            role_select = ui.select('Role', 
                                   options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER'],
                                   value=user_data.get('role', 'VIEWER')).classes('w-full mb-2')
            dept_input = ui.input('Department', value=user_data.get('department', '')).classes('w-full mb-2')
            company_input = ui.input('Company', value=user_data.get('company', '')).classes('w-full mb-2')
            
            active_switch = ui.switch('Active', value=user_data.get('is_active', True))
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Save', on_click=lambda: [
                    self.save_user_changes(user_data['email'], name_input.value, role_select.value,
                                          dept_input.value, company_input.value, active_switch.value),
                    dialog.close()
                ], color='primary')
        
        dialog.open()
    
    def save_user_changes(self, email, name, role, dept, company, is_active):
        """Save user changes to BigQuery"""
        try:
            if self.client:
                update_query = """
                    UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                    SET name = @name, role = @role, department = @dept, 
                        company = @company, is_active = @is_active,
                        updated_at = CURRENT_TIMESTAMP()
                    WHERE email = @email
                """
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("email", "STRING", email),
                        bigquery.ScalarQueryParameter("name", "STRING", name),
                        bigquery.ScalarQueryParameter("role", "STRING", role),
                        bigquery.ScalarQueryParameter("dept", "STRING", dept),
                        bigquery.ScalarQueryParameter("company", "STRING", company),
                        bigquery.ScalarQueryParameter("is_active", "BOOL", is_active)
                    ]
                )
                
                self.client.query(update_query, job_config=job_config).result()
                ui.notify(f'User {email} updated successfully', color='green')
        except Exception as e:
            ui.notify(f'Error updating user: {str(e)}', color='red')
    
    def delete_user(self, user_data):
        """Delete user confirmation dialog"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Confirm Delete').classes('text-xl font-bold mb-4')
            ui.label(f'Are you sure you want to delete user: {user_data["email"]}?').classes('mb-4')
            ui.label('This action cannot be undone.').classes('text-red-500 text-sm')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Delete', on_click=lambda: [
                    self.perform_delete(user_data['email']),
                    dialog.close()
                ], color='red')
        
        dialog.open()
    
    def perform_delete(self, email):
        """Actually delete the user"""
        try:
            if self.client:
                delete_query = """
                    DELETE FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                    WHERE email = @email
                """
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("email", "STRING", email)
                    ]
                )
                
                self.client.query(delete_query, job_config=job_config).result()
                ui.notify(f'User {email} deleted successfully', color='green')
        except Exception as e:
            ui.notify(f'Error deleting user: {str(e)}', color='red')
    
    def log_audit(self, action, user_email, details, status):
        """Log action to audit logs"""
        try:
            if self.client:
                audit_query = """
                    INSERT INTO `sys-googl-cortex-security.rls_manager.audit_logs`
                    (timestamp, user_email, action, resource_type, resource_name, 
                     taxonomy, details, status, error_message)
                    VALUES
                    (CURRENT_TIMESTAMP(), @email, @action, 'USER_MANAGEMENT', 'CONTROL_ACCESS',
                     NULL, PARSE_JSON(@details), @status, NULL)
                """
                
                details_json = json.dumps({
                    'description': details,
                    'timestamp': datetime.now().isoformat()
                })
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("email", "STRING", user_email),
                        bigquery.ScalarQueryParameter("action", "STRING", action),
                        bigquery.ScalarQueryParameter("details", "STRING", details_json),
                        bigquery.ScalarQueryParameter("status", "STRING", status)
                    ]
                )
                
                self.client.query(audit_query, job_config=job_config).result()
        except Exception as e:
            print(f"Error logging audit: {str(e)}")
