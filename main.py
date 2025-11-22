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

import os
import home
import allpages
import theme
from nicegui import app, ui
from dotenv import load_dotenv

# Importar serviços de autenticação
from services.auth_service import require_auth, get_current_user, logout
from pages.login_page import create_login_page

# Carregar variáveis de ambiente
load_dotenv()

# Criar página de login
create_login_page()

# Página principal com autenticação
@ui.page('/')
@require_auth
def index_page() -> None:
    user = get_current_user()
    
    # Header com informações do usuário e logout
    with ui.header().classes('items-center justify-between bg-primary'):
        with ui.row().classes('w-full items-center'):
            # Logo e título à esquerda
            ui.label('GenAI4Data Security Manager').classes('text-xl font-bold text-white')
            
            # Espaçamento
            ui.space()
            
            # Informações do usuário e logout à direita
            with ui.row().classes('items-center gap-4'):
                # Mostrar foto se disponível
                picture = user.get('picture', '')
                if picture:
                    ui.image(picture).classes('w-8 h-8 rounded-full')
                
                # Nome e email do usuário
                with ui.column().classes('gap-0'):
                    ui.label(user.get("name", "User")).classes('text-white text-sm font-medium')
                    ui.label(user.get("email", "")).classes('text-white text-xs opacity-80')
                
                # Botão de logout
                ui.button('Logout', on_click=logout).props('flat color=white')
    
    # Conteúdo principal com o frame do tema
    with theme.frame('Homepage'):
        # Mensagem de boas-vindas personalizada
        ui.label(f'Welcome back, {user.get("name", "User")}!').classes('text-2xl mb-4')
        
        # Conteúdo da home
        home.content()

# Criar todas as outras páginas com autenticação
def create_protected_pages():
    """Cria todas as páginas protegidas com autenticação"""
    original_create = allpages.create
    
    def protected_create():
        # Aplicar autenticação em todas as páginas criadas por allpages
        pages = original_create()
        
        # Se allpages retornar lista de páginas, aplicar proteção
        if pages:
            for page in pages:
                if hasattr(page, '__wrapped__'):
                    page.__wrapped__ = require_auth(page.__wrapped__)
        
        return pages
    
    # Substituir função original
    allpages.create = protected_create
    allpages.create()

# Chamar criação de páginas protegidas
create_protected_pages()

# Configuração do servidor
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='GenAI4Data Security Manager - RLS & CLS for BigQuery',
        host='0.0.0.0',  # Importante para Cloud Run
        port=int(os.getenv('PORT', 8080)),  # Porta do Cloud Run
        storage_secret=os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production'),
        favicon='🔐',
        reload=False  # Desabilitar reload em produção
    )
