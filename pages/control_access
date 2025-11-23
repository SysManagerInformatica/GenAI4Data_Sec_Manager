"""
Control Access - Gerenciamento de Usuários e Permissões
"""
from nicegui import ui
from google.cloud import bigquery
import os
from datetime import datetime
from services.auth_service import get_current_user, register_audit_log

PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')

class ControlAccess:
    def __init__(self):
        self.client = bigquery.Client(project=PROJECT_ID)
        self.current_user = get_current_user()
        
    def run(self):
        ui.label('Control Access - User Management').classes('text-3xl font-bold mb-4')
        
        # Tabs para diferentes ações
        with ui.tabs() as tabs:
            ui.tab('👥 View Users', name='view')
            ui.tab('➕ Add User', name='add')
            ui.tab('✏️ Edit Permissions', name='edit')
            ui.tab('🔄 Bulk Actions', name='bulk')
        
        with ui.tab_panels(tabs, value='view'):
            # TAB 1: Visualizar Usuários
            with ui.tab_panel('view'):
                self.view_users_panel()
            
            # TAB 2: Adicionar Usuário
            with ui.tab_panel('add'):
                self.add_user_panel()
            
            # TAB 3: Editar Permissões
            with ui.tab_panel('edit'):
                self.edit_permissions_panel()
            
            # TAB 4: Ações em Massa
            with ui.tab_panel('bulk'):
                self.bulk_actions_panel()
    
    def view_users_panel(self):
        """Painel para visualizar todos os usuários"""
        ui.label('Current System Users').classes('text-xl font-semibold mb-4')
        
        # Buscar usuários do BigQuery
        query = """
            SELECT 
                email, name, role, department, company, 
                is_active, last_login, created_at
            FROM `sys-googl-cortex-security.rls_manager.authorized_users`
            ORDER BY 
                CASE role 
                    WHEN 'OWNER' THEN 1 
                    WHEN 'ADMIN' THEN 2 
                    WHEN 'EDITOR' THEN 3 
                    WHEN 'VIEWER' THEN 4 
                END, email
        """
        
        users = self.client.query(query).result()
        
        # Criar tabela de usuários
        columns = [
            {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
            {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
            {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'center'},
            {'name': 'department', 'label': 'Department', 'field': 'department', 'align': 'left'},
            {'name': 'is_active', 'label': 'Status', 'field': 'is_active', 'align': 'center'},
            {'name': 'last_login', 'label': 'Last Login', 'field': 'last_login', 'align': 'left'},
            {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center'}
        ]
        
        rows = []
        for user in users:
            rows.append({
                'email': user.email,
                'name': user.name or 'N/A',
                'role': user.role,
                'department': user.department or 'N/A',
                'is_active': '✅ Active' if user.is_active else '❌ Inactive',
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'actions': user.email  # Usado para identificar a linha
            })
        
        with ui.table(columns=columns, rows=rows, row_key='email').classes('w-full') as table:
            # Adicionar slot para personalizar a coluna de role
            with table.add_slot('body-cell-role'):
                ui.badge('{{ props.row.role }}').props(
                    ':color="props.row.role === \'OWNER\' ? \'red\' : ' +
                    'props.row.role === \'ADMIN\' ? \'orange\' : ' +
                    'props.row.role === \'EDITOR\' ? \'green\' : \'blue\'"'
                )
    
    def add_user_panel(self):
        """Painel para adicionar novo usuário"""
        ui.label('Add New User').classes('text-xl font-semibold mb-4')
        
        with ui.card().classes('w-full max-w-2xl'):
            email = ui.input('Email *', placeholder='user@sysmanager.com.br').classes('w-full')
            name = ui.input('Full Name *', placeholder='John Doe').classes('w-full')
            
            with ui.row().classes('w-full gap-4'):
                role = ui.select('Role *', options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER'], value='VIEWER').classes('flex-1')
                department = ui.input('Department', placeholder='Engineering').classes('flex-1')
            
            company = ui.input('Company', placeholder='Sys Manager', value='Sys Manager').classes('w-full')
            
            def add_user():
                # Validar email
                if not email.value or '@' not in email.value:
                    ui.notify('Please enter a valid email', type='negative')
                    return
                
                # Verificar se usuário já existe
                check_query = f"""
                    SELECT COUNT(*) as count 
                    FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                    WHERE email = '{email.value}'
                """
                
                result = list(self.client.query(check_query).result())[0]
                if result.count > 0:
                    ui.notify(f'User {email.value} already exists', type='negative')
                    return
                
                # Inserir novo usuário
                insert_query = f"""
                    INSERT INTO `sys-googl-cortex-security.rls_manager.authorized_users`
                    (user_id, email, name, role, department, company, created_at, created_by, is_active)
                    VALUES
                    (GENERATE_UUID(), '{email.value}', '{name.value}', '{role.value}', 
                     '{department.value or ""}', '{company.value or ""}', 
                     CURRENT_TIMESTAMP(), '{self.current_user.get("email")}', TRUE)
                """
                
                try:
                    self.client.query(insert_query).result()
                    
                    # Registrar no audit log
                    register_audit_log(
                        'USER_ADDED', 
                        self.current_user.get('email'),
                        f'Added user {email.value} with role {role.value}',
                        'SUCCESS'
                    )
                    
                    ui.notify(f'User {email.value} added successfully!', type='positive')
                    
                    # Limpar campos
                    email.value = ''
                    name.value = ''
                    role.value = 'VIEWER'
                    department.value = ''
                    
                except Exception as e:
                    ui.notify(f'Error adding user: {str(e)}', type='negative')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=lambda: email.set_value('')).props('flat')
                ui.button('Add User', on_click=add_user).props('color=primary')
    
    def edit_permissions_panel(self):
        """Painel para editar permissões de usuários"""
        ui.label('Edit User Permissions').classes('text-xl font-semibold mb-4')
        
        # Buscar lista de usuários
        query = """
            SELECT email, name, role 
            FROM `sys-googl-cortex-security.rls_manager.authorized_users`
            ORDER BY email
        """
        users = list(self.client.query(query).result())
        
        user_options = {u.email: f'{u.name} ({u.email}) - {u.role}' for u in users}
        
        with ui.card().classes('w-full max-w-2xl'):
            selected_user = ui.select(
                'Select User to Edit', 
                options=user_options,
                with_input=True
            ).classes('w-full')
            
            new_role = ui.select('New Role', options=['VIEWER', 'EDITOR', 'ADMIN', 'OWNER']).classes('w-full')
            
            is_active = ui.switch('Active User', value=True)
            
            def update_user():
                if not selected_user.value:
                    ui.notify('Please select a user', type='negative')
                    return
                
                # Não permitir que VIEWER/EDITOR modifique OWNER
                if self.current_user.get('role') not in ['OWNER', 'ADMIN']:
                    ui.notify('You don\'t have permission to modify users', type='negative')
                    return
                
                update_query = f"""
                    UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                    SET role = '{new_role.value}',
                        is_active = {is_active.value},
                        updated_at = CURRENT_TIMESTAMP(),
                        updated_by = '{self.current_user.get("email")}'
                    WHERE email = '{selected_user.value}'
                """
                
                try:
                    self.client.query(update_query).result()
                    
                    register_audit_log(
                        'USER_UPDATED',
                        self.current_user.get('email'),
                        f'Updated user {selected_user.value}: role={new_role.value}, active={is_active.value}',
                        'SUCCESS'
                    )
                    
                    ui.notify(f'User {selected_user.value} updated successfully!', type='positive')
                    
                except Exception as e:
                    ui.notify(f'Error updating user: {str(e)}', type='negative')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Update User', on_click=update_user).props('color=primary')
    
    def bulk_actions_panel(self):
        """Painel para ações em massa"""
        ui.label('Bulk User Actions').classes('text-xl font-semibold mb-4')
        
        with ui.card().classes('w-full'):
            ui.label('Deactivate All Users by Domain').classes('font-semibold')
            
            domain = ui.input('Domain', placeholder='@example.com').classes('w-full')
            
            def deactivate_by_domain():
                if not domain.value:
                    ui.notify('Please enter a domain', type='negative')
                    return
                
                if self.current_user.get('role') != 'OWNER':
                    ui.notify('Only OWNER can perform bulk actions', type='negative')
                    return
                
                # Confirmar ação
                ui.notify(f'This will deactivate all users with domain {domain.value}', type='warning')
                
                query = f"""
                    UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                    SET is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP(),
                        updated_by = '{self.current_user.get("email")}'
                    WHERE email LIKE '%{domain.value}'
                    AND role != 'OWNER'
                """
                
                try:
                    result = self.client.query(query).result()
                    ui.notify(f'Users with domain {domain.value} deactivated', type='positive')
                    
                    register_audit_log(
                        'BULK_DEACTIVATE',
                        self.current_user.get('email'),
                        f'Deactivated all users with domain {domain.value}',
                        'SUCCESS'
                    )
                    
                except Exception as e:
                    ui.notify(f'Error: {str(e)}', type='negative')
            
            ui.button('Deactivate Domain', on_click=deactivate_by_domain).props('color=red')
