"""
Página de Login com Google OAuth Completo
"""
from nicegui import ui, app
import os
import requests
from google.cloud import bigquery
from datetime import datetime
import json

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')

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
                
                # BUSCAR USUÁRIO NO BIGQUERY E VERIFICAR ROLE
                client = bigquery.Client(project=PROJECT_ID)
                
                # Query para buscar usuário
                query = """
                    SELECT user_id, name, role, department, company, is_active
                    FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                    WHERE email = @email
                    LIMIT 1
                """
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("email", "STRING", email)
                    ]
                )
                
                results = list(client.query(query, job_config=job_config).result())
                
                if not results:
                    # Usuário não cadastrado no sistema
                    loading_container.clear()
                    with loading_container:
                        ui.icon('person_add_disabled', size='64px', color='orange')
                        ui.label('User Not Registered').classes('text-2xl font-bold text-orange-600 mb-4')
                        
                        with ui.card().classes('p-6'):
                            ui.label(f'Email: {email}').classes('text-lg mb-2')
                            ui.label('Your email domain is authorized but you are not registered in the system.').classes('text-gray-600 mb-4')
                            ui.label('Please contact the administrator to register your account.').classes('text-gray-600')
                            ui.label('Admin contact: admin@sysmanager.com.br').classes('text-sm text-gray-500 mt-2')
                        
                        ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4')
                    return
                
                user_data = results[0]
                
                # Verificar se o usuário está ativo
                if not user_data.is_active:
                    loading_container.clear()
                    with loading_container:
                        ui.icon('block', size='64px', color='red')
                        ui.label('Account Inactive').classes('text-2xl font-bold text-red-600 mb-4')
                        
                        with ui.card().classes('p-6'):
                            ui.label(f'Email: {email}').classes('text-lg mb-2')
                            ui.label('Your account has been deactivated.').classes('text-gray-600 mb-4')
                            ui.label('Please contact the administrator to reactivate your account.').classes('text-gray-600')
                        
                        ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4')
                    return
                
                # Atualizar last_login
                update_query = """
                    UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                    SET last_login = CURRENT_TIMESTAMP()
                    WHERE email = @email
                """
                client.query(update_query, job_config=job_config).result()
                
                # Registrar login no audit log com estrutura correta
                audit_details = json.dumps({
                    "user_name": user_data.name or user_info.get('name', ''),
                    "user_role": user_data.role,
                    "department": user_data.department,
                    "company": user_data.company,
                    "login_method": "Google OAuth"
                })
                
                audit_query = """
                    INSERT INTO `sys-googl-cortex-security.rls_manager.audit_logs`
                    (timestamp, user_email, action, resource_type, resource_name, taxonomy, details, status, error_message)
                    VALUES
                    (CURRENT_TIMESTAMP(), @email, 'USER_LOGIN', 'AUTH', 'LOGIN_SYSTEM', NULL, PARSE_JSON(@details), 'SUCCESS', NULL)
                """
                
                audit_job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("email", "STRING", email),
                        bigquery.ScalarQueryParameter("details", "STRING", audit_details)
                    ]
                )
                client.query(audit_query, job_config=audit_job_config).result()
                
                # Salvar dados completos do usuário na sessão
                app.storage.user['authenticated'] = True
                app.storage.user['user_info'] = {
                    'user_id': user_data.user_id,
                    'email': email,
                    'name': user_data.name or user_info.get('name', email),
                    'role': user_data.role,  # ROLE REAL DO BANCO!
                    'department': user_data.department,
                    'company': user_data.company,
                    'picture': user_info.get('picture', ''),
                    'login_time': datetime.now().isoformat()
                }
                
                # Redirecionar para home
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
