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
from services.auth_service import require_auth, get_current_user, register_audit_log
from pages.create_rls_users import RLSCreateforUsers
from pages.create_rls_groups import RLSCreateforGroups
from pages.assign_users_to_policy import RLSAssignUserstoPolicy
from pages.assign_values_to_group import RLSAssignValuestoGroup
from pages.cls_taxonomies import CLSTaxonomies
from pages.cls_policy_tags import CLSPolicyTags
from pages.cls_apply_tags import CLSApplyTags
from pages.cls_schema_browser import CLSSchemaBrowser
from pages.audit_logs import AuditLogs

def create() -> None:
    # ==================== RLS Pages ====================
    
    @ui.page('/createrlsusers/')
    @require_auth
    def create_rls_page_for_users():
        user = get_current_user()
        register_audit_log('ACCESS_RLS_USERS_PAGE', user.get('email', ''), 'Accessed RLS Create for Users page')
        rls_instance = RLSCreateforUsers()
        rls_instance.run()
    
    @ui.page('/createrlsgroups/')
    @require_auth
    def create_rls_page_for_groups():
        user = get_current_user()
        register_audit_log('ACCESS_RLS_GROUPS_PAGE', user.get('email', ''), 'Accessed RLS Create for Groups page')
        rls_instance = RLSCreateforGroups()
        rls_instance.run()
    
    @ui.page('/assignuserstopolicy/')
    @require_auth
    def assign_users_to_policy():
        user = get_current_user()
        register_audit_log('ACCESS_ASSIGN_USERS_PAGE', user.get('email', ''), 'Accessed Assign Users to Policy page')
        rls_instance = RLSAssignUserstoPolicy()
        rls_instance.run()
    
    @ui.page('/assignvaluestogroup/')
    @require_auth
    def assign_values_to_group():
        user = get_current_user()
        register_audit_log('ACCESS_ASSIGN_VALUES_PAGE', user.get('email', ''), 'Accessed Assign Values to Group page')
        rls_instance = RLSAssignValuestoGroup()
        rls_instance.run()
    
    # ==================== CLS Pages ====================
    
    @ui.page('/clstaxonomies/')
    @require_auth
    def cls_taxonomies_page():
        user = get_current_user()
        register_audit_log('ACCESS_CLS_TAXONOMIES_PAGE', user.get('email', ''), 'Accessed CLS Taxonomies page')
        cls_instance = CLSTaxonomies()
        cls_instance.run()
    
    @ui.page('/clspolicytags/')
    @require_auth
    def cls_policy_tags_page():
        user = get_current_user()
        register_audit_log('ACCESS_CLS_POLICY_TAGS_PAGE', user.get('email', ''), 'Accessed CLS Policy Tags page')
        cls_instance = CLSPolicyTags()
        cls_instance.run()
    
    @ui.page('/clsapplytags/')
    @require_auth
    def cls_apply_tags_page():
        user = get_current_user()
        register_audit_log('ACCESS_CLS_APPLY_TAGS_PAGE', user.get('email', ''), 'Accessed CLS Apply Tags page')
        cls_instance = CLSApplyTags()
        cls_instance.run()
    
    @ui.page('/clsschemabrowser/')
    @require_auth
    def cls_schema_browser_page():
        user = get_current_user()
        register_audit_log('ACCESS_CLS_SCHEMA_BROWSER_PAGE', user.get('email', ''), 'Accessed CLS Schema Browser page')
        cls_instance = CLSSchemaBrowser()
        cls_instance.run()
    
    # ==================== Audit Logs Page ====================
    
    @ui.page('/auditlogs/')
    @require_auth
    def audit_logs_page():
        user = get_current_user()
        # Verificar se usuário tem permissão para ver audit logs
        if user.get('role') not in ['OWNER', 'ADMIN']:
            ui.notify('Access denied. Only OWNER and ADMIN can view audit logs.', type='negative')
            ui.button('Back to Home', on_click=lambda: ui.run_javascript('window.location.href = "/"'))
            return
        
        register_audit_log('ACCESS_AUDIT_LOGS_PAGE', user.get('email', ''), 'Accessed Audit Logs page')
        audit_instance = AuditLogs()
        audit_instance.run()

if __name__ == '__main__':
    create()
