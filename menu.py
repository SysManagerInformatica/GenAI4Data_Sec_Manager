"""
================================================================================
  GenAI4Data Security Manager
  Module: Navigation Menu System
================================================================================
  Version:      2.2.0
  Release Date: 2024-12-14
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Multi-language navigation menu with color-coded security sections (RLS,
  CLS, IAM, Audit) and role-based access control integration.
================================================================================
"""

from nicegui import ui
from services.auth_service import get_current_user
from theme import get_text


def menu() -> None:
    """
    Create navigation menu with color-coded sections
    - HOME: Cyan (#00f3ff)
    - RLS: Green (#10b981)
    - CLS: Yellow (#f59e0b)
    - IAM: Red (#ef4444)
    - AUDIT: Purple (#a855f7)
    """
    user = get_current_user()  # Obter usuário atual para verificar role
    
    with ui.list():
        # ========================================
        # HOME - AZUL CIANO
        # ========================================
        with ui.item(on_click=lambda: ui.navigate.to('/')):
            with ui.item_section().props('avatar'):
                ui.icon('home').style('color: #00f3ff;')
            with ui.item_section():
                ui.item_label(get_text('nav_home')).classes(
                    replace='text-bold'
                ).style('font-size: 16px; color: #ffffff;')
        
        # ========================================
        # ROW LEVEL SECURITY - VERDE
        # ========================================
        with ui.expansion(
            get_text('nav_rls'),
            caption='Click to Expand',
            icon='policy'
        ).classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            # Adicionar estilo ao ícone do expansion
            ui.query('.q-expansion-item__toggle-icon').style('color: #10b981 !important;')
            
            # ========== NEW ARCHITECTURE (Views-based RLS) ==========
            
            # ✨ NEW: Create Custom RLS View
            with ui.item(on_click=lambda: ui.navigate.to('/rls/create-view')):
                with ui.item_section().props('avatar'):
                    ui.icon('add_box').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Create Custom RLS View').classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('New: View-based architecture').props('caption').style('font-size: 11px; color: #10b981;')
            
            # ✨ NEW: Manage RLS Views
            with ui.item(on_click=lambda: ui.navigate.to('/rls/manage-views')):
                with ui.item_section().props('avatar'):
                    ui.icon('view_list').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Manage RLS Views').classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('Edit users, filters & CLS').props('caption').style('font-size: 11px; color: #10b981;')
            
            # Separador visual
            ui.separator().classes('my-2').style('background-color: #334155;')
            
            # ========== LEGACY SYSTEM (Table-based RLS) ==========
            
            # 1. Create RLS for Users
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsusers/')):
                with ui.item_section().props('avatar'):
                    ui.icon('person').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_users')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 2. Create RLS for Groups
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsgroups/')):
                with ui.item_section().props('avatar'):
                    ui.icon('groups').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_groups')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 3. Assign Users to Policy
            with ui.item(on_click=lambda: ui.navigate.to('/assignuserstopolicy/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment_ind').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_assign_users')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 4. Assign Values to Groups
            with ui.item(on_click=lambda: ui.navigate.to('/assignvaluestogroup/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_assign_values')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
        
        # ========================================
        # COLUMN LEVEL SECURITY - AMARELO
        # ========================================
        with ui.expansion(
            get_text('nav_cls'),
            caption='Click to Expand',
            icon='security'
        ).classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            
            # 1. Manage Taxonomies
            with ui.item(on_click=lambda: ui.navigate.to('/clstaxonomies/')):
                with ui.item_section().props('avatar'):
                    ui.icon('folder').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_taxonomies')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 2. Manage Policy Tags
            with ui.item(on_click=lambda: ui.navigate.to('/clspolicytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('label').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_tags')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 3. Apply Tags to Columns
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('build').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_apply')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 4. Policy Tag Permissions
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplyiam/')):
                with ui.item_section().props('avatar'):
                    ui.icon('admin_panel_settings').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_iam')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 5. Create Protected View (CLS + Masking Unified)
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamiccolumns/')):
                with ui.item_section().props('avatar'):
                    ui.icon('add_circle').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_create_view')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 6. Manage Protected Views (✨ UPDATED: Now shows RLS + CLS)
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamicmanage/')):
                with ui.item_section().props('avatar'):
                    ui.icon('settings').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_manage_views')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('RLS + CLS integrated').props('caption').style('font-size: 11px; color: #10b981;')
            
            # 7. Schema Browser
            with ui.item(on_click=lambda: ui.navigate.to('/clsschemabrowser/')):
                with ui.item_section().props('avatar'):
                    ui.icon('search').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_schema')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
        
        # ========================================
        # IAM & SECURITY - VERMELHO
        # ========================================
        with ui.expansion(
            get_text('nav_iam'),
            caption='Click to Expand',
            icon='admin_panel_settings'
        ).classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            
            # 1. Dataset IAM Manager
            with ui.item(on_click=lambda: ui.navigate.to('/datasetiammanager/')):
                with ui.item_section().props('avatar'):
                    ui.icon('storage').style('color: #ef4444;')
                with ui.item_section():
                    ui.item_label(get_text('menu_iam_dataset')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 2. Project IAM Manager
            with ui.item(on_click=lambda: ui.navigate.to('/projectiammanager/')):
                with ui.item_section().props('avatar'):
                    ui.icon('shield').style('color: #ef4444;')
                with ui.item_section():
                    ui.item_label(get_text('menu_iam_project')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
            
            # 3. Control Access (apenas OWNER e ADMIN)
            if user.get('role') in ['OWNER', 'ADMIN']:
                with ui.item(on_click=lambda: ui.navigate.to('/controlaccess/')):
                    with ui.item_section().props('avatar'):
                        ui.icon('lock').style('color: #ef4444;')
                    with ui.item_section():
                        ui.item_label(get_text('menu_iam_control')).classes(
                            replace='text-bold'
                        ).style('font-size: 14px; color: #94a3b8;')
        
        # ========================================
        # AUDIT LOGS - ROXO
        # ========================================
        with ui.item(on_click=lambda: ui.navigate.to('/auditlogs/')):
            with ui.item_section().props('avatar'):
                ui.icon('history').style('color: #a855f7;')
            with ui.item_section():
                ui.item_label(get_text('menu_audit_logs')).classes(
                    replace='text-bold'
                ).style('font-size: 16px; color: #ffffff;')
