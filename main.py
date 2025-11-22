# Copyright 2024 Google LLC
# [manter todos os comentários de licença como estão]

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
    
    # Adicionar área do usuário no canto superior direito
    with ui.element('div').classes('absolute top-4 right-4 z-50'):
        with ui.card().classes('p-2 shadow-lg'):
            with ui.row().classes('items-center gap-3'):
                # Foto do perfil se disponível
                picture = user.get('picture', '')
                if picture:
                    ui.image(picture).classes('w-10 h-10 rounded-full')
                else:
                    ui.icon('account_circle', size='40px', color='primary')
                
                # Informações do usuário
                with ui.column().classes('gap-0'):
                    ui.label(user.get("name", "User")).classes('font-bold text-sm')
                    ui.label(user.get("email", "")).classes('text-xs text-gray-600')
                
                # Botão de Logout visível
                ui.button('🚪 Logout', on_click=logout).props('color=red-5 icon=logout').classes('ml-2')
    
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
