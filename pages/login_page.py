"""
Página de Login com Google OAuth Completo
"""
from nicegui import ui, app
import os
import requests

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
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
            # Trocar código por token REAL
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'code': code,
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            try:
                # Obter token
                token_response = requests.post(token_url, data=token_data)
                tokens = token_response.json()
                
                # Obter informações do usuário REAL
                user_info_response = requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {tokens["access_token"]}'}
                )
                user_info = user_info_response.json()
                
                # Salvar usuário REAL
                app.storage.user['authenticated'] = True
                app.storage.user['user_info'] = {
                    'email': user_info.get('email'),
                    'name': user_info.get('name', user_info.get('email')),
                    'picture': user_info.get('picture', ''),
                    'role': 'OWNER'  # Você pode verificar no BigQuery depois
                }
                
                ui.run_javascript('window.location.href = "/"')
                
            except Exception as e:
                ui.label(f'Erro: {str(e)}')
                ui.button('Voltar', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
        else:
            ui.label('Erro no login')
