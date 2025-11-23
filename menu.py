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
