"""
Página de Login com Google OAuth Completo
"""
from nicegui import ui, app
import os
import requests

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Domínios permitidos para acesso
ALLOWED_DOMAINS = [
    'sysmanager.com.br',
    'sysmngr.com',
    'sysmanagerinformatica.com.br'
]

def create_login_page():
    """Cria a página de login"""
    
    @ui.page('/login')
    def login_page():
        # Estilo de fundo
        ui.query('body').style('background: linear-gradient(135deg, #4285F4 0%, #34A853 50%, #FBBC05 100%)')
        
        with ui.column().classes('absolute-center items-center'):
            with ui.card().classes('p-12 shadow-2xl'):
                # Logo e título
                ui.icon('security', size='64px', color='#4285F4').classes('mb-4')
                ui.label('GenAI4Data - Security Manager').classes('text-3xl font-bold text-center mb-2')
                ui.label('RLS & CLS for BigQuery').classes('text-lg text-gray-600 text-center mb-8')
                
                ui.separator()
                
                def google_login():
                    auth_url = (
                        "https://accounts.google.com/o/oauth2/v2/auth?"
                        f"client_id={GOOGLE_CLIENT_ID}&"
                        f"redirect_uri={REDIRECT_URI}&"
                        "response_type=code&"
                        "scope=openid%20email%20profile&"
                        "access_type=online&"
                        "prompt=select_account"  # Força seleção de conta
                    )
                    ui.run_javascript(f'window.location.href = "{auth_url}"')
                
                # Botão de login com ícone do Google
                ui.button('🔐 Sign in with Google', on_click=google_login).classes('w-full')
                
                # Informação sobre domínios permitidos
                ui.label('Access restricted to authorized domains').classes('text-xs text-gray-500 mt-4 text-center')
    
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        # Tratamento de erro do OAuth
        if error:
            with ui.column().classes('absolute-center items-center'):
                ui.icon('error', size='64px', color='red')
                ui.label('Authentication Error').classes('text-2xl font-bold text-red-600')
                ui.label(f'Error: {error}').classes('text-lg')
                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
            return
        
        if code:
            # Mostrar loading
            with ui.column().classes('absolute-center items-center') as loading_container:
                ui.spinner(size='lg')
                ui.label('Authenticating...').classes('mt-4')
            
            # Trocar código por token
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
                
                if token_response.status_code != 200:
                    raise Exception(f"Token error: {token_response.text}")
                
                tokens = token_response.json()
                
                # Obter informações do usuário
                user_info_response = requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {tokens["access_token"]}'}
                )
                
                if user_info_response.status_code != 200:
                    raise Exception(f"User info error: {user_info_response.text}")
                
                user_info = user_info_response.json()
                email = user_info.get('email', '')
                
                # VERIFICAR DOMÍNIO DO EMAIL
                domain = email.split('@')[1] if '@' in email else ''
                
                if domain not in ALLOWED_DOMAINS:
                    loading_container.clear()
                    with loading_container:
                        ui.icon('block', size='64px', color='red')
                        ui.label('Access Denied').classes('text-2xl font-bold text-red-600 mb-4')
                        
                        with ui.card().classes('p-6'):
                            ui.label(f'Email: {email}').classes('text-lg mb-2')
                            ui.label('This email domain is not authorized to access this application.').classes('text-gray-600 mb-4')
                            ui.label('Authorized domains:').classes('font-semibold')
                            for d in ALLOWED_DOMAINS:
                                ui.label(f'• @{d}').classes('ml-4 text-gray-600')
                        
                        ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4')
                    return
                
                # OPCIONAL: Verificar usuário específico no BigQuery
                # from google.cloud import bigquery
                # client = bigquery.Client()
                # query = f"SELECT role FROM `sys-googl-cortex-security.rls_manager.authorized_users` WHERE email = '{email}' AND is_active = TRUE"
                # results = list(client.query(query).result())
                # if not results:
                #     # Mostrar erro de usuário não cadastrado
                #     return
                
                # Se passou nas verificações, fazer login
                app.storage.user['authenticated'] = True
                app.storage.user['user_info'] = {
                    'email': email,
                    'name': user_info.get('name', email),
                    'picture': user_info.get('picture', ''),
                    'role': 'OWNER'  # Ou buscar do BigQuery
                }
                
                # Registrar login no audit log (opcional)
                from services.auth_service import register_audit_log
                register_audit_log('USER_LOGIN', email, f'Successful login via Google OAuth')
                
                ui.run_javascript('window.location.href = "/"')
                
            except Exception as e:
                loading_container.clear()
                with loading_container:
                    ui.icon('error_outline', size='64px', color='orange')
                    ui.label('Authentication Failed').classes('text-2xl font-bold text-orange-600')
                    ui.label('An error occurred during authentication:').classes('text-lg mb-2')
                    ui.label(str(e)).classes('text-sm text-gray-600 font-mono bg-gray-100 p-2 rounded')
                    ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4')
        else:
            # Se não tem código nem erro, voltar ao login
            ui.run_javascript('window.location.href = "/login"')
