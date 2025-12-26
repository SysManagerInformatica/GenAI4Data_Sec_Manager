"""
================================================================================
  GenAI4Data Security Manager
  Module: Navigation Menu System
================================================================================
  Version:      3.1.0
  Release Date: 2024-12-26
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Simplified navigation menu with unified RLS and CLS interfaces.
  
  Changes (v3.1.0):
  - Removed Policy Tags and Taxonomies menu items (deprecated)
  - CLS menu now shows only Protected Views options
  - Cleaner, more focused navigation
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
    user = get_current_user()
    
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
            ui.query('.q-expansion-item__toggle-icon').style('color: #10b981 !important;')
            
            # 1. Create Views
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsusers/')):
                with ui.item_section().props('avatar'):
                    ui.icon('add_box').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Create Views').classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('5-step wizard to create RLS views').props('caption').style('font-size: 11px; color: #10b981;')
            
            # 2. Assign to Policy
            with ui.item(on_click=lambda: ui.navigate.to('/assignuserstopolicy/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment_ind').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Assign to Policy').classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('Users, Groups & Service Accounts').props('caption').style('font-size: 11px; color: #10b981;')
            
            ui.separator().classes('my-2').style('background-color: #334155;')
            
            # 3. Create RLS for Groups (legacy)
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsgroups/')):
                with ui.item_section().props('avatar'):
                    ui.icon('groups').style('color: #10b981; opacity: 0.5;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_groups')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #64748b;')
                    ui.item_label('Legacy - Group policies').props('caption').style('font-size: 11px; color: #64748b;')
            
            # 4. Assign Values to Groups (legacy)
            with ui.item(on_click=lambda: ui.navigate.to('/assignvaluestogroup/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment').style('color: #10b981; opacity: 0.5;')
                with ui.item_section():
                    ui.item_label(get_text('menu_rls_assign_values')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #64748b;')
                    ui.item_label('Legacy - Group values').props('caption').style('font-size: 11px; color: #64748b;')
        
        # ========================================
        # COLUMN LEVEL SECURITY - AMARELO (SIMPLIFIED)
        # ========================================
        with ui.expansion(
            get_text('nav_cls'),
            caption='Click to Expand',
            icon='security'
        ).classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            
            # 1. Create Protected View (CLS + Masking)
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamiccolumns/')):
                with ui.item_section().props('avatar'):
                    ui.icon('add_circle').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_create_view')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('CLS + Masking wizard').props('caption').style('font-size: 11px; color: #f59e0b;')
            
            # 2. Manage Protected Views (RLS + CLS Integrated)
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamicmanage/')):
                with ui.item_section().props('avatar'):
                    ui.icon('settings').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_manage_views')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('RLS + CLS integrated').props('caption').style('font-size: 11px; color: #10b981;')
            
            ui.separator().classes('my-2').style('background-color: #334155;')
            
            # 3. Schema Browser
            with ui.item(on_click=lambda: ui.navigate.to('/clsschemabrowser/')):
                with ui.item_section().props('avatar'):
                    ui.icon('search').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label(get_text('menu_cls_schema')).classes(
                        replace='text-bold'
                    ).style('font-size: 14px; color: #94a3b8;')
                    ui.item_label('Browse BigQuery schemas').props('caption').style('font-size: 11px; color: #64748b;')
        
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
