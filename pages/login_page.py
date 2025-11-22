"""
Página de Login Simplificada
"""
from nicegui import ui, app
import os

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def create_login_page():
    """Cria a página de login"""
    
    @ui.page('/login')
    def login_page():
        with ui.column().classes('absolute-center items-center'):
            with ui.card().classes('p-12 shadow-2xl'):
                ui.label('GenAI4Data - Security Manager').classes('text-3xl font-bold text-center mb-2')
                ui.label('RLS & CLS for BigQuery').classes('text-lg text-gray-600 text-center mb-8')
                
                def google_login():
                    auth_url = (
                        "https://accounts.google.com/o/oauth2/v2/auth?"
                        f"client_id={GOOGLE_CLIENT_ID}&"
                        f"redirect_uri={REDIRECT_URI}&"
                        "response_type=code&"
                        "scope=openid%20email%20profile&"
                        "access_type=online"
                    )
                    ui.run_javascript(f'window.location.href = "{auth_url}"')
                
                ui.button('Sign in with Google', on_click=google_login).classes('w-full')
    
    @ui.page('/callback')
    def callback_page(code: str = None):
        if code:
            # Login simplificado para teste
            app.storage.user['authenticated'] = True
            app.storage.user['user_info'] = {
                'email': 'test@sysmanager.com.br',
                'name': 'Test User',
                'role': 'OWNER'
            }
            ui.run_javascript('window.location.href = "/"')
        else:
            ui.label('Erro no login')
