# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# "IMPORTANT: This application is a prototype and should be used for experimental purposes only.
# It is not intended for production use. 
# This software is provided 'as is' without warranty of any kind, express or implied, including but not limited to the warranties 
# of merchantability, fitness for a particular purpose and noninfringement. 
# In no event shall Google or the developers be liable for any claim, damages or other liability, whether in an action of contract, 
# tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software. 
# Google is not responsible for the functionality, reliability, or security of this prototype. 
# Use of this tool is at your own discretion and risk."

from nicegui import ui
from services.auth_service import require_auth, get_current_user, register_audit_log, check_permission
from pages.create_rls_users import RLSCreateforUsers
from pages.create_rls_groups import RLSCreateforGroups
from pages.assign_users_to_policy import RLSAssignUserstoPolicy
from pages.assign_values_to_group import RLSAssignValuestoGroup
from pages.cls_taxonomies import CLSTaxonomies
from pages.cls_policy_tags import CLSPolicyTags
from pages.cls_apply_tags import CLSApplyTags
from pages.cls_schema_browser import CLSSchemaBrowser
from pages.audit_logs import AuditLogs
from pages.control_access import ControlAccess  # NOVO IMPORT

def show_access_denied(resource_name: str, required_permission: str):
    """Mostra página de acesso negado"""
    user = get_current_user()
    
    with ui.column().classes('absolute-center items-center'):
        ui.icon('lock', size='64px', color='red')
        ui.label('Access Denied').classes('text-2xl font-bold text-red-600 mb-4')
        
        with ui.card().classes('p-6'):
            ui.label(f'Resource: {resource_name}').classes('text-lg font-semibold mb-2')
            ui.label(f'Required Permission: {required_permission}').classes('text-gray-600 mb-2')
            ui.label(f'Your Role: {user.get("role", "Unknown")}').classes('text-gray-600 mb-4')
            
            ui.label('You do not have permission to access this resource.').classes('text-gray-600 mb-2')
            ui.label('Please contact your administrator if you believe you should have access.').classes('text-sm text-gray-500')
        
        ui.button('Back to Home', on_click=lambda: ui.run_javascript('window.location.href = "/"')).classes('mt-4')

def create() -> None:
    # ==================== RLS Pages ====================
    
    @ui.page('/createrlsusers/')
    @require_auth
    def create_rls_page_for_users():
        user = get_current_user()
        
        # Verificar permissão de criação
        if not check_permission(user.get('role'), 'RLS_POLICIES', 'can_create'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access RLS Create Users - Role: {user.get("role")}', 'DENIED')
            show_access_denied('RLS Create Users', 'can_create')
            return
        
        register_audit_log('ACCESS_RLS_USERS_PAGE', user.get('email', ''), 
                         f'Accessed RLS Create for Users page - Role: {user.get("role")}', 'SUCCESS')
        rls_instance = RLSCreateforUsers()
        rls_instance.run()
    
    @ui.page('/createrlsgroups/')
    @require_auth
    def create_rls_page_for_groups():
        user = get_current_user()
        
        # Verificar permissão de criação
        if not check_permission(user.get('role'), 'RLS_POLICIES', 'can_create'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access RLS Create Groups - Role: {user.get("role")}', 'DENIED')
            show_access_denied('RLS Create Groups', 'can_create')
            return
        
        register_audit_log('ACCESS_RLS_GROUPS_PAGE', user.get('email', ''), 
                         f'Accessed RLS Create for Groups page - Role: {user.get("role")}', 'SUCCESS')
        rls_instance = RLSCreateforGroups()
        rls_instance.run()
    
    @ui.page('/assignuserstopolicy/')
    @require_auth
    def assign_users_to_policy():
        user = get_current_user()
        
        # Verificar permissão de edição
        if not check_permission(user.get('role'), 'RLS_POLICIES', 'can_edit'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access Assign Users to Policy - Role: {user.get("role")}', 'DENIED')
            show_access_denied('Assign Users to Policy', 'can_edit')
            return
        
        register_audit_log('ACCESS_ASSIGN_USERS_PAGE', user.get('email', ''), 
                         f'Accessed Assign Users to Policy page - Role: {user.get("role")}', 'SUCCESS')
        rls_instance = RLSAssignUserstoPolicy()
        rls_instance.run()
    
    @ui.page('/assignvaluestogroup/')
    @require_auth
    def assign_values_to_group():
        user = get_current_user()
        
        # Verificar permissão de edição
        if not check_permission(user.get('role'), 'RLS_POLICIES', 'can_edit'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access Assign Values to Group - Role: {user.get("role")}', 'DENIED')
            show_access_denied('Assign Values to Group', 'can_edit')
            return
        
        register_audit_log('ACCESS_ASSIGN_VALUES_PAGE', user.get('email', ''), 
                         f'Accessed Assign Values to Group page - Role: {user.get("role")}', 'SUCCESS')
        rls_instance = RLSAssignValuestoGroup()
        rls_instance.run()
    
    # ==================== CLS Pages ====================
    
    @ui.page('/clstaxonomies/')
    @require_auth
    def cls_taxonomies_page():
        user = get_current_user()
        
        # Verificar permissão de criação para CLS
        if not check_permission(user.get('role'), 'CLS_POLICIES', 'can_create'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access CLS Taxonomies - Role: {user.get("role")}', 'DENIED')
            show_access_denied('CLS Taxonomies', 'can_create')
            return
        
        register_audit_log('ACCESS_CLS_TAXONOMIES_PAGE', user.get('email', ''), 
                         f'Accessed CLS Taxonomies page - Role: {user.get("role")}', 'SUCCESS')
        cls_instance = CLSTaxonomies()
        cls_instance.run()
    
    @ui.page('/clspolicytags/')
    @require_auth
    def cls_policy_tags_page():
        user = get_current_user()
        
        # Verificar permissão de criação para CLS
        if not check_permission(user.get('role'), 'CLS_POLICIES', 'can_create'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access CLS Policy Tags - Role: {user.get("role")}', 'DENIED')
            show_access_denied('CLS Policy Tags', 'can_create')
            return
        
        register_audit_log('ACCESS_CLS_POLICY_TAGS_PAGE', user.get('email', ''), 
                         f'Accessed CLS Policy Tags page - Role: {user.get("role")}', 'SUCCESS')
        cls_instance = CLSPolicyTags()
        cls_instance.run()
    
    @ui.page('/clsapplytags/')
    @require_auth
    def cls_apply_tags_page():
        user = get_current_user()
        
        # Verificar permissão de edição para CLS
        if not check_permission(user.get('role'), 'CLS_POLICIES', 'can_edit'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access CLS Apply Tags - Role: {user.get("role")}', 'DENIED')
            show_access_denied('CLS Apply Tags', 'can_edit')
            return
        
        register_audit_log('ACCESS_CLS_APPLY_TAGS_PAGE', user.get('email', ''), 
                         f'Accessed CLS Apply Tags page - Role: {user.get("role")}', 'SUCCESS')
        cls_instance = CLSApplyTags()
        cls_instance.run()
    
    @ui.page('/clsschemabrowser/')
    @require_auth
    def cls_schema_browser_page():
        user = get_current_user()
        
        # Schema Browser - apenas visualização, todos com can_view podem acessar
        if not check_permission(user.get('role'), 'CLS_POLICIES', 'can_view'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access CLS Schema Browser - Role: {user.get("role")}', 'DENIED')
            show_access_denied('CLS Schema Browser', 'can_view')
            return
        
        register_audit_log('ACCESS_CLS_SCHEMA_BROWSER_PAGE', user.get('email', ''), 
                         f'Accessed CLS Schema Browser page - Role: {user.get("role")}', 'SUCCESS')
        cls_instance = CLSSchemaBrowser()
        cls_instance.run()
    
    # ==================== Admin Pages ====================
    
    @ui.page('/controlaccess/')
    @require_auth
    def control_access_page():
        user = get_current_user()
        
        # Só OWNER e ADMIN podem gerenciar usuários
        if user.get('role') not in ['OWNER', 'ADMIN']:
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access Control Access - Role: {user.get("role")}', 'DENIED')
            
            with ui.column().classes('absolute-center items-center'):
                ui.icon('admin_panel_settings', size='64px', color='red')
                ui.label('Administrator Access Required').classes('text-2xl font-bold text-red-600 mb-4')
                
                with ui.card().classes('p-6'):
                    ui.label('Control Access Management').classes('text-lg font-semibold mb-2')
                    ui.label(f'Your Role: {user.get("role", "Unknown")}').classes('text-gray-600 mb-2')
                    ui.label('Only OWNER and ADMIN roles can manage user access.').classes('text-gray-600 mb-4')
                    
                    if user.get('role') == 'EDITOR':
                        ui.label('As an EDITOR, you can work with policies but cannot manage users.').classes('text-sm text-gray-500')
                    elif user.get('role') == 'VIEWER':
                        ui.label('As a VIEWER, you have read-only access and cannot manage users.').classes('text-sm text-gray-500')
                
                ui.button('Back to Home', on_click=lambda: ui.run_javascript('window.location.href = "/"')).classes('mt-4')
            return
        
        register_audit_log('ACCESS_CONTROL_ACCESS_PAGE', user.get('email', ''), 
                         f'Accessed Control Access page - Role: {user.get("role")}', 'SUCCESS')
        control_instance = ControlAccess()
        control_instance.run()
    
    @ui.page('/auditlogs/')
    @require_auth
    def audit_logs_page():
        user = get_current_user()
        
        # Verificar permissão específica para audit logs
        if not check_permission(user.get('role'), 'AUDIT_LOGS', 'can_view'):
            register_audit_log('ACCESS_DENIED', user.get('email', ''), 
                             f'Tried to access Audit Logs - Role: {user.get("role")}', 'DENIED')
            
            with ui.column().classes('absolute-center items-center'):
                ui.icon('security', size='64px', color='red')
                ui.label('Restricted Access').classes('text-2xl font-bold text-red-600 mb-4')
                
                with ui.card().classes('p-6'):
                    ui.label('Audit Logs Access').classes('text-lg font-semibold mb-2')
                    ui.label(f'Your Role: {user.get("role", "Unknown")}').classes('text-gray-600 mb-2')
                    ui.label('Only OWNER and ADMIN roles can view audit logs.').classes('text-gray-600 mb-4')
                    
                    if user.get('role') == 'EDITOR':
                        ui.label('As an EDITOR, you can create and modify policies but cannot view audit logs.').classes('text-sm text-gray-500')
                    elif user.get('role') == 'VIEWER':
                        ui.label('As a VIEWER, you have read-only access to policies but cannot view audit logs.').classes('text-sm text-gray-500')
                
                ui.button('Back to Home', on_click=lambda: ui.run_javascript('window.location.href = "/"')).classes('mt-4')
            return
        
        register_audit_log('ACCESS_AUDIT_LOGS_PAGE', user.get('email', ''), 
                         f'Accessed Audit Logs page - Role: {user.get("role")}', 'SUCCESS')
        audit_instance = AuditLogs()
        audit_instance.run()

if __name__ == '__main__':
    create()
