"""
Página de Login com Google OAuth
"""
from nicegui import ui, app
import os
from services.auth_service import check_user_in_db, register_audit_log

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def create_login_page():
    """Cria a página de login"""
    
    @ui.page('/login')
    def login_page():
        # Estilo da página
        ui.query('body').style('''
            background: linear-gradient(135deg, #4285F4 0%, #34A853 50%, #FBBC05 100%);
            font-family: 'Google Sans', Arial, sans-serif;
        ''')
        
        with ui.column().classes('absolute-center items-center'):
            with ui.card().classes('p-12 shadow-2xl rounded-lg'):
                # Logo
                ui.icon('security', size='64px', color='#4285F4').classes('mb-4')
                
                # Título
                ui.label('GenAI4Data - Security Manager').classes('text-3xl font-bold text-center mb-2')
                ui.label('RLS & CLS for BigQuery').classes('text-lg text-gray-600 text-center mb-8')
                
                ui.separator()
                
                # Botão Google OAuth
                def google_login():
                    # URL de autorização do Google
                    auth_url = (
                        "https://accounts.google.com/o/oauth2/v2/auth?"
                        f"client_id={GOOGLE_CLIENT_ID}&"
                        f"redirect_uri={REDIRECT_URI}&"
                        "response_type=code&"
                        "scope=openid%20email%20profile&"
                        "access_type=online&"
                        "prompt=select_account"
                    )
                    ui.run_javascript(f'window.location.href = "{auth_url}"')
                
                # Botão estilizado do Google
                with ui.button(on_click=google_login).classes('w-full bg-white hover:bg-gray-100'):
                    with ui.row().classes('items-center justify-center gap-2'):
                        ui.html('''
                        <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                            <g fill="none">
                                <path d="M17.6 9.2l-.1-1.8H9v3.4h4.8C13.6 12 13 13 12 13.6v2.2h3a8.8 8.8 0 0 0 2.6-6.6z" fill="#4285F4"/>
                                <path d="M9 18c2.4 0 4.5-.8 6-2.2l-3-2.2a5.4 5.4 0 0 1-8-2.9H1V13a9 9 0 0 0 8 5z" fill="#34A853"/>
                                <path d="M4 10.7a5.4 5.4 0 0 1 0-3.4V5H1a9 9 0 0 0 0 8l3-2.3z" fill="#FBBC05"/>
                                <path d="M9 3.6c1.3 0 2.5.4 3.4 1.3L15 2.3A9 9 0 0 0 1 5l3 2.4a5.4 5.4 0 0 1 5-3.7z" fill="#EA4335"/>
                            </g>
                        </svg>
                        ''')
                        ui.label('Sign in with Google').classes('text-gray-700 font-medium')
                
                ui.label('© 2024 Sys Manager Informática').classes('text-xs text-gray-500 text-center mt-6')
    
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        """Página de callback do OAuth"""
        
        if error:
            ui.label(f'Erro na autenticação: {error}').classes('text-red-500')
            ui.button('Voltar', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
            return
        
        if code:
            # Trocar código por token
            import requests
            
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'code': code,
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            try:
                # Obter tokens
                token_response = requests.post(token_url, data=token_data)
                tokens = token_response.json()
                
                # Obter informações do usuário
                user_info_response = requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {tokens["access_token"]}'}
                )
                user_info = user_info_response.json()
                
                # Verificar se usuário está autorizado no banco
                db_user = check_user_in_db(user_info['email'])
                
                if db_user:
                    # Usuário autorizado - fazer login
                    app.storage.user['authenticated'] = True
                    app.storage.user['user_info'] = {
                        'email': user_info['email'],
                        'name': user_info.get('name', user_info['email']),
                        'picture': user_info.get('picture', ''),
                        'role': db_user['role']
                    }
                    
                    # Registrar login no audit
                    register_audit_log('USER_LOGIN', user_info['email'], 'Successful Google OAuth login')
                    
                    ui.run_javascript('window.location.href = "/"')
                else:
                    # Usuário não autorizado
                    with ui.column().classes('absolute-center items-center'):
                        ui.icon('block', size='64px', color='red')
                        ui.label('Acesso Negado').classes('text-2xl font-bold text-red-600')
                        ui.label(f'O email {user_info["email"]} não está autorizado.').classes('text-lg')
                        ui.label('Contate o administrador do sistema.').classes('text-gray-600')
                        ui.button('Voltar ao Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
                        
            except Exception as e:
                ui.label(f'Erro ao processar autenticação: {e}').classes('text-red-500')
                ui.button('Tentar novamente', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
        else:
            ui.run_javascript('window.location.href = "/login"')
