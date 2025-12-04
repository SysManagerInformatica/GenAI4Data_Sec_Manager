from nicegui import ui
from services.auth_service import get_current_user

def menu() -> None:
    user = get_current_user()  # Obter usuário atual para verificar role
    
    with ui.list():
        # HOME - AZUL CIANO
        with ui.item(on_click=lambda: ui.navigate.to('/')):
            with ui.item_section().props('avatar'):
                ui.icon('home').style('color: #00f3ff;')  # ← CIANO
            with ui.item_section():
                ui.item_label('Home').classes(replace='text-bold').style('font-size: 16px; color: #ffffff;')
        
        # ROW LEVEL SECURITY - VERDE
        with ui.expansion('Row Level Security', caption='Click to Expand', icon='policy').classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            # Adicionar estilo ao ícone do expansion
            ui.query('.q-expansion-item__toggle-icon').style('color: #10b981 !important;')
            
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsusers/')):
                with ui.item_section().props('avatar'):
                    ui.icon('person').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Create RLS for Users').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsgroups/')):
                with ui.item_section().props('avatar'):
                    ui.icon('groups').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Create RLS for Groups').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            with ui.item(on_click=lambda: ui.navigate.to('/assignuserstopolicy/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment_ind').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Assign Users to Policy').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            with ui.item(on_click=lambda: ui.navigate.to('/assignvaluestogroup/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment').style('color: #10b981;')
                with ui.item_section():
                    ui.item_label('Assign Values to Groups').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
        
        # COLUMN LEVEL SECURITY - AMARELO
        with ui.expansion('Column Level Security', caption='Click to Expand', icon='security').classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            
            # 1. Manage Taxonomies
            with ui.item(on_click=lambda: ui.navigate.to('/clstaxonomies/')):
                with ui.item_section().props('avatar'):
                    ui.icon('folder').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Manage Taxonomies').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 2. Manage Policy Tags
            with ui.item(on_click=lambda: ui.navigate.to('/clspolicytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('label').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Manage Policy Tags').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 3. Apply Tags to Columns
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('build').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Apply Tags to Columns').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 4. Policy Tag Permissions
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplyiam/')):
                with ui.item_section().props('avatar'):
                    ui.icon('admin_panel_settings').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Policy Tag Permissions').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 5. Create Protected View (CLS + Masking Unified)
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamiccolumns/')):
                with ui.item_section().props('avatar'):
                    ui.icon('add_circle').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Create Protected View').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 6. Manage Protected Views
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamicmanage/')):
                with ui.item_section().props('avatar'):
                    ui.icon('settings').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Manage Protected Views').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # 7. Schema Browser
            with ui.item(on_click=lambda: ui.navigate.to('/clsschemabrowser/')):
                with ui.item_section().props('avatar'):
                    ui.icon('search').style('color: #f59e0b;')
                with ui.item_section():
                    ui.item_label('Schema Browser').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
        
        # IAM & SECURITY - VERMELHO
        with ui.expansion('IAM & Security', caption='Click to Expand', icon='admin_panel_settings').classes('w-full text-bold').style('font-size: 16px; color: #ffffff;'):
            
            # Dataset IAM Manager
            with ui.item(on_click=lambda: ui.navigate.to('/datasetiammanager/')):
                with ui.item_section().props('avatar'):
                    ui.icon('storage').style('color: #ef4444;')
                with ui.item_section():
                    ui.item_label('Dataset IAM Manager').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # Project IAM Manager
            with ui.item(on_click=lambda: ui.navigate.to('/projectiammanager/')):
                with ui.item_section().props('avatar'):
                    ui.icon('shield').style('color: #ef4444;')
                with ui.item_section():
                    ui.item_label('Project IAM Manager').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
            
            # Control Access (apenas OWNER e ADMIN)
            if user.get('role') in ['OWNER', 'ADMIN']:
                with ui.item(on_click=lambda: ui.navigate.to('/controlaccess/')):
                    with ui.item_section().props('avatar'):
                        ui.icon('lock').style('color: #ef4444;')
                    with ui.item_section():
                        ui.item_label('Control Access').classes(replace='text-bold').style('font-size: 14px; color: #94a3b8;')
        
        # AUDIT LOGS - ROXO
        with ui.item(on_click=lambda: ui.navigate.to('/auditlogs/')):
            with ui.item_section().props('avatar'):
                ui.icon('history').style('color: #a855f7;')  # ← ROXO
            with ui.item_section():
                ui.item_label('Audit Logs').classes(replace='text-bold').style('font-size: 16px; color: #ffffff;')
