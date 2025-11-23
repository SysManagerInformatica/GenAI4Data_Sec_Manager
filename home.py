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

from nicegui import ui, app
from services.auth_service import get_current_user

def content() -> None:
    user = get_current_user()
    
    # CARD COM INFORMAÇÕES DO USUÁRIO E BADGE DO ROLE
    with ui.card().classes('w-full mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-100 shadow-lg'):
        with ui.row().classes('items-center justify-between w-full'):
            # Lado esquerdo - Informações do usuário
            with ui.row().classes('items-center gap-4'):
                # Ícone ou foto do usuário
                picture = user.get('picture', '')
                if picture:
                    ui.image(picture).classes('w-16 h-16 rounded-full')
                else:
                    ui.icon('account_circle', size='64px', color='primary')
                
                # Detalhes do usuário
                with ui.column().classes('gap-0'):
                    ui.label(f'Welcome back, {user.get("name", "User")}!').classes('text-2xl font-bold text-gray-800')
                    ui.label(user.get('email', '')).classes('text-gray-600')
                    if user.get('department'):
                        ui.label(f'Department: {user.get("department")}').classes('text-sm text-gray-500')
                    if user.get('company'):
                        ui.label(f'Company: {user.get("company")}').classes('text-sm text-gray-500')
            
            # Lado direito - Badge do Role e Logout
            with ui.column().classes('items-center gap-3'):
                # BADGE DO ROLE GRANDE E VISÍVEL
                role = user.get('role', 'VIEWER')
                role_colors = {
                    'OWNER': 'red-7',
                    'ADMIN': 'orange-7', 
                    'EDITOR': 'green-7',
                    'VIEWER': 'blue-7'
                }
                role_descriptions = {
                    'OWNER': 'Full System Access',
                    'ADMIN': 'Administrative Access',
                    'EDITOR': 'Edit Permissions',
                    'VIEWER': 'Read-Only Access'
                }
                
                ui.label('Your Role:').classes('text-xs text-gray-600')
                ui.button(role, color=role_colors.get(role, 'gray')).props('push glossy no-caps').classes('text-lg font-bold px-6 py-2')
                ui.label(role_descriptions.get(role, '')).classes('text-xs text-gray-500')
                
                # Botão de Logout
                ui.button('🚪 LOGOUT', on_click=lambda: app.storage.user.clear() or ui.run_javascript('window.location.href="/login"')).props('color=red push').classes('mt-2')
    
    # Card de Permissões
    with ui.expansion('View My Permissions', icon='security').classes('w-full mb-6'):
        with ui.card().classes('w-full'):
            role = user.get('role', 'VIEWER')
            
            if role == 'OWNER':
                ui.label('✅ Create, Edit, Delete all RLS/CLS policies').classes('text-green-600')
                ui.label('✅ Manage all users and permissions').classes('text-green-600')
                ui.label('✅ View complete audit logs').classes('text-green-600')
                ui.label('✅ Full administrative control').classes('text-green-600')
            elif role == 'ADMIN':
                ui.label('✅ Create, Edit, Delete RLS/CLS policies').classes('text-green-600')
                ui.label('✅ Manage users (cannot delete)').classes('text-green-600')
                ui.label('✅ View audit logs').classes('text-green-600')
                ui.label('❌ Cannot modify OWNER users').classes('text-red-600')
            elif role == 'EDITOR':
                ui.label('✅ Create and Edit RLS/CLS policies').classes('text-green-600')
                ui.label('✅ View existing policies').classes('text-green-600')
                ui.label('❌ Cannot delete policies').classes('text-red-600')
                ui.label('❌ Cannot view audit logs').classes('text-red-600')
            else:  # VIEWER
                ui.label('✅ View RLS/CLS policies').classes('text-blue-600')
                ui.label('❌ Cannot create or modify policies').classes('text-red-600')
                ui.label('❌ Cannot view audit logs').classes('text-red-600')
                ui.label('❌ Read-only access').classes('text-red-600')
    
    # CONTEÚDO ORIGINAL DA PÁGINA
    with ui.row().classes('w-full justify-center'):
        with ui.column().classes('w-full max-w-5xl items-center'):
            ui.label('Welcome to GenAI4Data Security Manager').classes('text-4xl font-bold text-center my-4 text-primary')
            ui.label('A tool to simplify Row-Level Security (RLS) creation in BigQuery.').classes('text-xl text-center text-bold text-gray-700 mb-8')
            
            with ui.card().classes('mt-8 p-6 rounded-lg shadow-xl w-full md:w-3/4 lg:w-2/3'):
                ui.label('Key Features').classes('text-2xl font-semibold mb-6 text-center')
                
                with ui.grid(columns=3).classes('gap-8 w-full justify-center'):
                    with ui.column().classes('items-center text-center'):
                        ui.icon('shield', size='3em', color='#3b82f6')
                        ui.label('Enhanced Security').classes('text-lg font-medium mt-2')
                        ui.label('Easily define row-level access control.').classes('text-sm text-gray-600 px-4')
                    
                    with ui.column().classes('items-center text-center'):
                        ui.icon('speed', size='3em', color='#3b82f6')
                        ui.label('Streamlined Workflow').classes('text-lg font-medium mt-2')
                        ui.label('Intuitive interface for quick RLS setup.').classes('text-sm text-gray-600 px-4')
                    
                    with ui.column().classes('items-center text-center'):
                        ui.icon('link', size='3em', color='#3b82f6')
                        ui.label('BigQuery Integration').classes('text-lg font-medium mt-2')
                        ui.label('Seamlessly connects with your BigQuery datasets.').classes('text-sm text-gray-600 px-4')
