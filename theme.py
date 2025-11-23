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

from contextlib import contextmanager
from menu import menu
from nicegui import ui, app
from services.auth_service import get_current_user, register_audit_log

def get_role_color(role: str) -> str:
    """Retorna cor baseada no role do usuário"""
    colors = {
        'OWNER': '#EA4335',  # Vermelho
        'ADMIN': '#FBBC05',  # Amarelo
        'EDITOR': '#34A853', # Verde
        'VIEWER': '#4285F4'  # Azul
    }
    return colors.get(role, '#666666')

def logout():
    """Função de logout com audit log"""
    user = get_current_user()
    register_audit_log('USER_LOGOUT', user.get('email', ''), f'User logged out - Role: {user.get("role")}', 'SUCCESS')
    app.storage.user.clear()
    ui.run_javascript('window.location.href="/login"')

@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#4285F4', secondary='#AECBFA', accent='#1967D2', positive='#34A853', negative='#EA4335')
    
    # Obter informações do usuário
    user = get_current_user()
    user_email = user.get('email', 'Unknown')
    user_name = user.get('name', 'User')
    user_role = user.get('role', 'VIEWER')
    user_picture = user.get('picture', '')
    
    with ui.header(elevated=True).classes(replace='row items-center justify-between').classes('bg-blue-500') as header:
        # Lado esquerdo - Menu e título
        with ui.row().classes('items-center'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label('GenAI4Data - Security Manager').classes('font-bold text-white')
            ui.label(f'| {navtitle}').classes('text-white text-sm opacity-80 ml-2')
        
        # Lado direito - Informações do usuário e Logout
        with ui.row().classes('items-center gap-3'):
            # Foto do perfil (se disponível)
            if user_picture:
                ui.image(user_picture).classes('w-8 h-8 rounded-full')
            else:
                ui.icon('account_circle', size='32px').props('color=white')
            
            # Informações do usuário
            with ui.column().classes('gap-0'):
                ui.label(user_name).classes('text-white text-sm font-medium')
                with ui.row().classes('items-center gap-1'):
                    ui.label(user_email).classes('text-white text-xs opacity-80')
                    # Badge do role com cor específica
                    ui.badge(user_role).props(f'color=white').style(f'background-color: {get_role_color(user_role)}')
            
            # Botão de Logout
            ui.button('LOGOUT', on_click=logout).props('color=red push').classes('font-bold')
    
    with ui.left_drawer().classes('bg-white') as left_drawer:
        # Adicionar informação do role no menu também
        with ui.card().classes('w-full mb-4 p-3 bg-gray-100'):
            ui.label('Current User').classes('text-xs text-gray-600')
            ui.label(user_name).classes('font-bold text-sm')
            ui.badge(user_role).props(f'color=white').style(f'background-color: {get_role_color(user_role)}')
        
        ui.separator()
        
        # Menu normal
        menu()
        
        # Adicionar informações de permissão no final do menu
        ui.separator()
        
        with ui.card().classes('w-full mt-4 p-3 bg-gray-50'):
            ui.label('Permissions').classes('text-xs text-gray-600 mb-2')
            
            # Mostrar permissões baseadas no role
            if user_role == 'OWNER':
                ui.label('✓ Full Access').classes('text-xs text-green-600')
                ui.label('✓ All Operations').classes('text-xs text-green-600')
                ui.label('✓ Audit Logs').classes('text-xs text-green-600')
            elif user_role == 'ADMIN':
                ui.label('✓ Create/Edit/Delete').classes('text-xs text-green-600')
                ui.label('✓ User Management').classes('text-xs text-green-600')
                ui.label('✓ Audit Logs').classes('text-xs text-green-600')
            elif user_role == 'EDITOR':
                ui.label('✓ Create/Edit Policies').classes('text-xs text-green-600')
                ui.label('✗ Delete Policies').classes('text-xs text-red-600')
                ui.label('✗ Audit Logs').classes('text-xs text-red-600')
            elif user_role == 'VIEWER':
                ui.label('✓ View Only').classes('text-xs text-blue-600')
                ui.label('✗ No Modifications').classes('text-xs text-red-600')
                ui.label('✗ Audit Logs').classes('text-xs text-red-600')
    
    with ui.footer().classes('bg-blue-500 w-full') as footer:
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Copyright 2024 CCW Latam - Concept Prototype').classes('font-bold text-white')
            # Adicionar informação de sessão no footer
            ui.label(f'Session: {user_role} | {user_email}').classes('text-white text-xs opacity-80')
    
    with ui.column().classes('w-full p-4'):
        yield
