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
from nicegui import ui

@contextmanager
def frame(navtitle: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#4285F4', secondary='#AECBFA', accent='#1967D2', positive='#34A853', negative='#EA4335')
    
    with ui.header(elevated=True).classes(replace='row items-center justify-between').classes('bg-blue-500') as header:
        # Lado esquerdo - Menu e título
        with ui.row().classes('items-center'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label('GenAI4Data - Security Manager').classes('font-bold text-white')
        
        # Lado direito - Botão de Logout
        ui.button('LOGOUT', on_click=lambda: ui.run_javascript('window.location.href="/login"')).props('color=red push').classes('font-bold')
    
    with ui.left_drawer().classes('bg-white') as left_drawer:
        menu()
    
    with ui.footer().classes('bg-blue-500 w-full') as footer:
        ui.label('Copyright 2024 CCW Latam - Concept Prototype').classes('font-bold text-white')
    
    with ui.column().classes('w-full p-4'):
        yield
