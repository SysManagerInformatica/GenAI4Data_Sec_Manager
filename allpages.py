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

# Tentar importar as páginas originais, criar placeholders se não existirem
try:
    from pages.create_rls_users import RLSCreateforUsers
except:
    class RLSCreateforUsers:
        def run(self):
            from theme import frame
            with frame('Create RLS for Users'):
                ui.label('Create Row Level Security for Users').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.create_rls_groups import RLSCreateforGroups
except:
    class RLSCreateforGroups:
        def run(self):
            from theme import frame
            with frame('Create RLS for Groups'):
                ui.label('Create Row Level Security for Groups').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.assign_users_to_policy import RLSAssignUserstoPolicy
except:
    class RLSAssignUserstoPolicy:
        def run(self):
            from theme import frame
            with frame('Assign Users to Policy'):
                ui.label('Assign Users to Policy').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.assign_values_to_group import RLSAssignValuestoGroup
except:
    class RLSAssignValuestoGroup:
        def run(self):
            from theme import frame
            with frame('Assign Values to Group'):
                ui.label('Assign Values to Groups').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.cls_taxonomies import CLSTaxonomies
except:
    class CLSTaxonomies:
        def run(self):
            from theme import frame
            with frame('Manage Taxonomies'):
                ui.label('Data Classification Taxonomies').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.cls_policy_tags import CLSPolicyTags
except:
    class CLSPolicyTags:
        def run(self):
            from theme import frame
            with frame('Manage Policy Tags'):
                ui.label('Column-Level Security Policy Tags').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.cls_apply_tags import CLSApplyTags
except:
    class CLSApplyTags:
        def run(self):
            from theme import frame
            with frame('Apply Tags to Columns'):
                ui.label('Apply Security Tags to BigQuery Columns').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.cls_schema_browser import CLSSchemaBrowser
except:
    class CLSSchemaBrowser:
        def run(self):
            from theme import frame
            with frame('Schema Browser'):
                ui.label('BigQuery Schema Browser').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# 🆕 NOVO: Policy Tag Permissions
try:
    from pages.cls_apply_iam import CLSPermissionsManager
except:
    class CLSPermissionsManager:
        def run(self):
            from theme import frame
            with frame('Policy Tag Permissions'):
                ui.label('Policy Tag IAM Permissions Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

try:
    from pages.audit_logs import AuditLogs
except:
    class AuditLogs:
        def run(self):
            from theme import frame
            with frame('Audit Logs'):
                ui.label('System Audit Logs').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Importar Control Access (já criamos)
try:
    from pages.control_access import ControlAccess
except:
    class ControlAccess:
        def run(self):
            from theme import frame
            from nicegui import app
            user_info = app.storage.user.get('user_info', {})
            role = user_info.get('role', 'VIEWER')
            
            with frame('Control Access'):
                if role not in ['OWNER', 'ADMIN']:
                    ui.icon('lock', size='64px', color='red').classes('mx-auto')
                    ui.label('Access Denied').classes('text-2xl font-bold text-red-600 text-center')
                    ui.label('Only OWNER and ADMIN roles can access this page.').classes('text-gray-600 text-center')
                    return
                
                ui.label('User Access Management').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')


def create() -> None:
    # RLS Pages
    def create_rls_page_for_users():
        rls_instance = RLSCreateforUsers()
        rls_instance.run()
    ui.page('/createrlsusers/')(create_rls_page_for_users)

    def create_rls_page_for_groups():
        rls_instance = RLSCreateforGroups()
        rls_instance.run()
    ui.page('/createrlsgroups/')(create_rls_page_for_groups)

    def assign_users_to_policy():
        rls_instance = RLSAssignUserstoPolicy()
        rls_instance.run()
    ui.page('/assignuserstopolicy/')(assign_users_to_policy) 

    def assign_values_to_group():
        rls_instance = RLSAssignValuestoGroup()
        rls_instance.run()
    ui.page('/assignvaluestogroup/')(assign_values_to_group) 

    # CLS Pages
    def cls_taxonomies_page():
        cls_instance = CLSTaxonomies()
        cls_instance.run()
    ui.page('/clstaxonomies/')(cls_taxonomies_page)

    def cls_policy_tags_page():
        cls_instance = CLSPolicyTags()
        cls_instance.run()
    ui.page('/clspolicytags/')(cls_policy_tags_page)

    def cls_apply_tags_page():
        cls_instance = CLSApplyTags()
        cls_instance.run()
    ui.page('/clsapplytags/')(cls_apply_tags_page)

    def cls_schema_browser_page():
        cls_instance = CLSSchemaBrowser()
        cls_instance.run()
    ui.page('/clsschemabrowser/')(cls_schema_browser_page)

    # 🆕 NOVO: Policy Tag Permissions Page
    def cls_apply_iam_page():
        cls_instance = CLSPermissionsManager()
        cls_instance.run()
    ui.page('/clsapplyiam/')(cls_apply_iam_page)

    # Audit Logs Page
    def audit_logs_page():
        audit_instance = AuditLogs()
        audit_instance.run()
    ui.page('/auditlogs/')(audit_logs_page)

    # Control Access Page (NOVO)
    def control_access_page():
        control_instance = ControlAccess()
        control_instance.run()
    ui.page('/controlaccess/')(control_access_page)


if __name__ == '__main__':
    create()
