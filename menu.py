from nicegui import ui
from services.auth_service import get_current_user

def menu() -> None:
    user = get_current_user()  # Obter usuário atual para verificar role
    
    with ui.list():
        # HOME
        with ui.item(on_click=lambda: ui.navigate.to('/')):
            with ui.item_section().props('avatar'):
                ui.icon('home', color='blue-500')
            with ui.item_section():
                ui.item_label('Home').classes(replace='text-primary text-bold').style('font-size:16px')
        
        # ROW LEVEL SECURITY
        with ui.expansion('Row Level Security', caption='Click to Expand', icon='policy').classes('w-full text-primary text-bold').style('font-size:16px'):
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsusers/')):
                with ui.item_section().props('avatar'):
                    ui.icon('person', color='blue-500')
                with ui.item_section():
                    ui.item_label('Create RLS for Users').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/createrlsgroups/')):
                with ui.item_section().props('avatar'):
                    ui.icon('groups', color='blue-500')
                with ui.item_section():
                    ui.item_label('Create RLS for Groups').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/assignuserstopolicy/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment_ind', color='blue-500')
                with ui.item_section():
                    ui.item_label('Assign Users to Policy').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/assignvaluestogroup/')):
                with ui.item_section().props('avatar'):
                    ui.icon('assignment', color='blue-500')
                with ui.item_section():
                    ui.item_label('Assign Values to Groups').classes(replace='text-primary text-bold').style('font-size:14px')
        
        # COLUMN LEVEL SECURITY
        with ui.expansion('Column Level Security', caption='Click to Expand', icon='security').classes('w-full text-primary text-bold').style('font-size:16px'):
            with ui.item(on_click=lambda: ui.navigate.to('/clstaxonomies/')):
                with ui.item_section().props('avatar'):
                    ui.icon('folder', color='green-500')
                with ui.item_section():
                    ui.item_label('Manage Taxonomies').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/clspolicytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('label', color='green-500')
                with ui.item_section():
                    ui.item_label('Manage Policy Tags').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplytags/')):
                with ui.item_section().props('avatar'):
                    ui.icon('build', color='green-500')
                with ui.item_section():
                    ui.item_label('Apply Tags to Columns').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/clsschemabrowser/')):
                with ui.item_section().props('avatar'):
                    ui.icon('search', color='green-500')
                with ui.item_section():
                    ui.item_label('Schema Browser').classes(replace='text-primary text-bold').style('font-size:14px')
            
            # Policy Tag Permissions
            with ui.item(on_click=lambda: ui.navigate.to('/clsapplyiam/')):
                with ui.item_section().props('avatar'):
                    ui.icon('admin_panel_settings', color='green-500')
                with ui.item_section():
                    ui.item_label('Policy Tag Permissions').classes(replace='text-primary text-bold').style('font-size:14px')
            
            # Dynamic Column Security
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamiccolumns/')):
                with ui.item_section().props('avatar'):
                    ui.icon('visibility', color='green-500')
                with ui.item_section():
                    ui.item_label('Dynamic Column Security').classes(replace='text-primary text-bold').style('font-size:14px')
            
            # 🆕 Manage Dynamic Views
            with ui.item(on_click=lambda: ui.navigate.to('/clsdynamicmanage/')):
                with ui.item_section().props('avatar'):
                    ui.icon('settings', color='green-500')
                with ui.item_section():
                    ui.item_label('Manage Dynamic Views').classes(replace='text-primary text-bold').style('font-size:14px')
        
        # DATA MASKING
        with ui.expansion('Data Masking', caption='Click to Expand', icon='masks').classes('w-full text-primary text-bold').style('font-size:16px'):
            with ui.item(on_click=lambda: ui.navigate.to('/maskcreateview/')):
                with ui.item_section().props('avatar'):
                    ui.icon('visibility_off', color='purple-500')
                with ui.item_section():
                    ui.item_label('Create Masked View').classes(replace='text-primary text-bold').style('font-size:14px')
            
            with ui.item(on_click=lambda: ui.navigate.to('/maskstatus/')):
                with ui.item_section().props('avatar'):
                    ui.icon('list', color='purple-500')
                with ui.item_section():
                    ui.item_label('View Masking Status').classes(replace='text-primary text-bold').style('font-size:14px')
        
        # CONTROL ACCESS - Mostrar apenas para OWNER e ADMIN
        if user.get('role') in ['OWNER', 'ADMIN']:
            with ui.item(on_click=lambda: ui.navigate.to('/controlaccess/')):
                with ui.item_section().props('avatar'):
                    ui.icon('admin_panel_settings', color='orange-500')
                with ui.item_section():
                    ui.item_label('Control Access').classes(replace='text-primary text-bold').style('font-size:16px')
        
        # AUDIT LOGS
        with ui.item(on_click=lambda: ui.navigate.to('/auditlogs/')):
            with ui.item_section().props('avatar'):
                ui.icon('history', color='purple-500')
            with ui.item_section():
                ui.item_label('Audit Logs').classes(replace='text-primary text-bold').style('font-size:16px')
