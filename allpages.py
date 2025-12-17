"""
================================================================================
  GenAI4Data Security Manager
  Module: Page Router & Registration System
================================================================================
  Version:      2.2.0
  Release Date: 2024-12-14
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Central page routing and registration system for all application pages
  including RLS, CLS, IAM, and Audit modules with fallback support for
  missing page implementations.
================================================================================
"""

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

# ✨ NEW: Custom RLS View Creation
try:
    from pages.create_rls_view import CreateRLSView
except:
    class CreateRLSView:
        def run(self):
            from theme import frame
            with frame('Create Custom RLS View'):
                ui.label('Create Custom RLS View').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# ✨ NEW: Manage RLS Views
try:
    from pages.manage_rls_views import ManageRLSViews
except:
    class ManageRLSViews:
        def run(self):
            from theme import frame
            with frame('Manage RLS Views'):
                ui.label('Manage RLS Views').classes('text-2xl font-bold mb-4')
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

# Policy Tag Permissions
try:
    from pages.cls_apply_iam import CLSPermissionsManager
except:
    class CLSPermissionsManager:
        def run(self):
            from theme import frame
            with frame('Policy Tag Permissions'):
                ui.label('Policy Tag IAM Permissions Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Dynamic Column Security (Create Protected View)
try:
    from pages.cls_dynamic_columns import DynamicColumnSecurity
except:
    class DynamicColumnSecurity:
        def run(self):
            from theme import frame
            with frame('Create Protected View'):
                ui.label('Create Protected View').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Manage Protected Views
try:
    from pages.cls_dynamic_manage import DynamicColumnManage
except:
    class DynamicColumnManage:
        def run(self):
            from theme import frame
            with frame('Manage Protected Views'):
                ui.label('Manage Protected Views').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# ✅ Dataset IAM Manager
try:
    from pages.dataset_iam_manager import DatasetIAMManager
except:
    class DatasetIAMManager:
        def run(self):
            from theme import frame
            with frame('Dataset IAM Manager'):
                ui.label('Dataset IAM Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# ✅ NOVO: Project IAM Manager
try:
    from pages.project_iam_manager import ProjectIAMManager
except:
    class ProjectIAMManager:
        def run(self):
            from theme import frame
            with frame('Project IAM Manager'):
                ui.label('Project IAM Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Audit Logs
try:
    from pages.audit_logs import AuditLogs
except:
    class AuditLogs:
        def run(self):
            from theme import frame
            with frame('Audit Logs'):
                ui.label('System Audit Logs').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Control Access
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

    # ✨ NEW: Custom RLS View Pages
    def create_rls_view_page():
        rls_instance = CreateRLSView()
        rls_instance.run()
    ui.page('/rls/create-view')(create_rls_view_page)

    def manage_rls_views_page():
        rls_instance = ManageRLSViews()
        rls_instance.run()
    ui.page('/rls/manage-views')(manage_rls_views_page)

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

    # Policy Tag Permissions Page
    def cls_apply_iam_page():
        cls_instance = CLSPermissionsManager()
        cls_instance.run()
    ui.page('/clsapplyiam/')(cls_apply_iam_page)

    # Create Protected View (CLS + Masking Unified)
    def cls_dynamic_columns_page():
        cls_instance = DynamicColumnSecurity()
        cls_instance.run()
    ui.page('/clsdynamiccolumns/')(cls_dynamic_columns_page)

    # Manage Protected Views
    def cls_dynamic_manage_page():
        cls_instance = DynamicColumnManage()
        cls_instance.run()
    ui.page('/clsdynamicmanage/')(cls_dynamic_manage_page)

    # ✅ Dataset IAM Manager
    def dataset_iam_manager_page():
        iam_instance = DatasetIAMManager()
        iam_instance.run()
    ui.page('/datasetiammanager/')(dataset_iam_manager_page)

    # ✅ NOVO: Project IAM Manager
    def project_iam_manager_page():
        iam_instance = ProjectIAMManager()
        iam_instance.run()
    ui.page('/projectiammanager/')(project_iam_manager_page)

    # Audit Logs Page
    def audit_logs_page():
        audit_instance = AuditLogs()
        audit_instance.run()
    ui.page('/auditlogs/')(audit_logs_page)

    # Control Access Page
    def control_access_page():
        control_instance = ControlAccess()
        control_instance.run()
    ui.page('/controlaccess/')(control_access_page)


if __name__ == '__main__':
    create()
