"""
================================================================================
  GenAI4Data Security Manager
  Module: Page Router & Registration System
================================================================================
  Version:      3.1.0
  Release Date: 2024-12-26
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Central page routing and registration system for all application pages
  including RLS, CLS, IAM, and Audit modules with fallback support for
  missing page implementations.
  
  Changes (v3.1.0):
  - Removed Policy Tags and Taxonomies routes (deprecated)
  - CLS now uses only Protected Views approach
================================================================================
"""

from nicegui import ui

# ============================================
# RLS PAGES
# ============================================

try:
    from pages.create_views import RLSCreateforUsers
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

# ============================================
# CLS PAGES (Protected Views Only)
# ============================================

# Schema Browser
try:
    from pages.cls_schema_browser import CLSSchemaBrowser
except:
    class CLSSchemaBrowser:
        def run(self):
            from theme import frame
            with frame('Schema Browser'):
                ui.label('BigQuery Schema Browser').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Create Protected View (CLS + Masking)
try:
    from pages.cls_dynamic_columns import DynamicColumnSecurity
except:
    class DynamicColumnSecurity:
        def run(self):
            from theme import frame
            with frame('Create Protected View'):
                ui.label('Create Protected View').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Manage Protected Views (RLS + CLS Integrated)
try:
    from pages.cls_dynamic_manage import DynamicColumnManage
except:
    class DynamicColumnManage:
        def run(self):
            from theme import frame
            with frame('Manage Protected Views'):
                ui.label('Manage Protected Views').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# ============================================
# IAM PAGES
# ============================================

# Dataset IAM Manager
try:
    from pages.dataset_iam_manager import DatasetIAMManager
except:
    class DatasetIAMManager:
        def run(self):
            from theme import frame
            with frame('Dataset IAM Manager'):
                ui.label('Dataset IAM Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# Project IAM Manager
try:
    from pages.project_iam_manager import ProjectIAMManager
except:
    class ProjectIAMManager:
        def run(self):
            from theme import frame
            with frame('Project IAM Manager'):
                ui.label('Project IAM Manager').classes('text-2xl font-bold mb-4')
                ui.label('This feature is under development').classes('text-orange-600')

# ============================================
# AUDIT & ACCESS CONTROL
# ============================================

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


# ============================================
# ROUTE REGISTRATION
# ============================================

def create() -> None:
    """Register all application routes"""
    
    # ========== RLS Pages ==========
    
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

    # ========== CLS Pages (Protected Views Only) ==========

    def cls_schema_browser_page():
        cls_instance = CLSSchemaBrowser()
        cls_instance.run()
    ui.page('/clsschemabrowser/')(cls_schema_browser_page)

    def cls_dynamic_columns_page():
        cls_instance = DynamicColumnSecurity()
        cls_instance.run()
    ui.page('/clsdynamiccolumns/')(cls_dynamic_columns_page)

    def cls_dynamic_manage_page():
        cls_instance = DynamicColumnManage()
        cls_instance.run()
    ui.page('/clsdynamicmanage/')(cls_dynamic_manage_page)

    # ========== IAM Pages ==========

    def dataset_iam_manager_page():
        iam_instance = DatasetIAMManager()
        iam_instance.run()
    ui.page('/datasetiammanager/')(dataset_iam_manager_page)

    def project_iam_manager_page():
        iam_instance = ProjectIAMManager()
        iam_instance.run()
    ui.page('/projectiammanager/')(project_iam_manager_page)

    # ========== Audit & Access ==========

    def audit_logs_page():
        audit_instance = AuditLogs()
        audit_instance.run()
    ui.page('/auditlogs/')(audit_logs_page)

    def control_access_page():
        control_instance = ControlAccess()
        control_instance.run()
    ui.page('/controlaccess/')(control_access_page)


if __name__ == '__main__':
    create()
