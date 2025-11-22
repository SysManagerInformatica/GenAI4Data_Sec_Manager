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
from services.auth_service import get_current_user, logout

def content() -> None:
    user = get_current_user()
    
    # BARRA SUPERIOR COM INFORMAÇÕES DO USUÁRIO E LOGOUT
    with ui.row().classes('w-full justify-between items-center mb-6 p-4 bg-gray-100 rounded-lg'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('account_circle', size='32px', color='primary')
            with ui.column().classes('gap-0'):
                ui.label(user.get('name', 'User')).classes('font-bold text-sm')
                ui.label(user.get('email', '')).classes('text-xs text-gray-600')
        
        ui.button('LOGOUT', on_click=logout).props('color=red-7 push').classes('font-bold')
    
    # CONTEÚDO ORIGINAL DA PÁGINA
    with ui.row().classes('w-full justify-center'):
        with ui.column().classes('w-full max-w-5xl items-center'):  # Responsive width, centered content
            ui.label('Welcome to GenAI4Data Security Manager').classes('text-4xl font-bold text-center my-4 text-primary') # Larger title, spacing, color
            ui.label('A tool to simplify Row-Level Security (RLS) creation in BigQuery.').classes('text-xl text-center text-bold text-gray-700 mb-8') # Subtitle, color, spacing
            
            with ui.card().classes('mt-8 p-6 rounded-lg shadow-xl w-full md:w-3/4 lg:w-2/3'):  # Responsive card width, rounded corners, better shadow
                ui.label('Key Features').classes('text-2xl font-semibold mb-6 text-center')  # Centered title
                
                with ui.grid(columns=3).classes('gap-8 w-full justify-center'):  # Use ui.grid for responsive columns
                    with ui.column().classes('items-center text-center'): # Center column content
                        ui.icon('shield', size='3em', color='#3b82f6')  # Nice blue color (Tailwind's blue-500)
                        ui.label('Enhanced Security').classes('text-lg font-medium mt-2') # Spacing
                        ui.label('Easily define row-level access control.').classes('text-sm text-gray-600 px-4') # Added padding for better readability
                    
                    with ui.column().classes('items-center text-center'):
                        ui.icon('speed', size='3em', color='#3b82f6')
                        ui.label('Streamlined Workflow').classes('text-lg font-medium mt-2')
                        ui.label('Intuitive interface for quick RLS setup.').classes('text-sm text-gray-600 px-4')
                    
                    with ui.column().classes('items-center text-center'):
                        ui.icon('link', size='3em', color='#3b82f6')
                        ui.label('BigQuery Integration').classes('text-lg font-medium mt-2')
                        ui.label('Seamlessly connects with your BigQuery datasets.').classes('text-sm text-gray-600 px-4')
