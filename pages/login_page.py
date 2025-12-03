"""
Página de Login com Google OAuth Completo - Visual Dark Mode Data Fortress
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
    """Cria a página de login com visual Dark Tech"""
    
    # --- CSS COMPARTILHADO (LOGIN + CALLBACK) ---
    # Injetamos isso para garantir que tanto o login quanto as telas de erro tenham o visual correto
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');
            
            body {
                margin: 0;
                font-family: 'Inter', sans-serif;
                background-color: #0F172A; /* Navy Dark */
                color: white;
            }
            
            /* Fundo Tech com Grid */
            .tech-bg {
                background-color: #0F172A;
                background-image: 
                    radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
                    linear-gradient(rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.95)),
                    linear-gradient(#1e293b 1px, transparent 1px),
                    linear-gradient(90deg, #1e293b 1px, transparent 1px);
                background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            /* Card de Vidro */
            .glass-card {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 50px rgba(56, 189, 248, 0.1);
                color: white;
            }
            
            /* Tipografia */
            .text-gradient {
                background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Botão Google Moderno */
            .google-btn-custom {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid rgba(255,255,255,0.1);
                cursor: pointer;
            }
            .google-btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
                background-color: #f8fafc;
            }
        </style>
    ''')

    @ui.page('/login')
    def login_page():
        
        # Função interna de login (Lógica original mantida)
        def google_login():
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

        # --- ESTRUTURA VISUAL ---
        with ui.column().classes('tech-bg w-full p-4'):
            
            # Card Principal
            with ui.card().classes('glass-card w-full max-w-[420px] p-10 rounded-3xl items-center text-center gap-2'):
                
                # Ícone
                with ui.element('div').classes('relative mb-6'):
                    ui.element('div').classes('absolute inset-0 bg-cyan-500 blur-2xl opacity-20 rounded-full')
                    ui.icon('security', size='4rem', color='#38BDF8').classes('relative z-10')

                # Títulos
                ui.label('GenAI4Data').classes('text-3xl font-extrabold text-gradient tracking-tight')
                ui.label('Security Manager').classes('text-xl font-semibold text-gray-400 mb-2')
                
                # Subtítulo RLS & CLS
                ui.label('RLS & CLS for BigQuery').classes(
                    'font-mono text-xs text-cyan-500/80 mb-8 tracking-widest uppercase'
                )

                ui.separator().classes('bg-gray-700/50 mb-8 w-full')

                # Botão Google Customizado (aciona a função google_login)
                with ui.row().classes('google-btn-custom w-full bg-white text-gray-900 rounded-xl py-3.5 px-6 items-center justify-center gap-3 shadow-lg') \
                        .on('click', google_login):
                    
                    # SVG do Google
                    ui.html('''
                        <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"/>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                    ''')
                    ui.label('Sign in with Google').classes('font-bold text-sm tracking-wide')

                # Rodapé de Domínios
                ui.label('Access restricted to authorized domains').classes('text-[10px] text-gray-500 mt-6 font-mono')

    
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        
        # Wrapper principal com o fundo Tech
        with ui.column().classes('tech-bg w-full') as main_container:
            
            # --- TRATAMENTO DE ERRO OAUTH ---
            if error:
                with ui.card().classes('glass-card p-8 items-center text-center border-red-500/30'):
                    ui.icon('error', size='64px', color='#EF4444').classes('mb-4')
                    ui.label('Authentication Error').classes('text-2xl font-bold text-red-400')
                    ui.label(f'Error: {error}').classes('text-sm text-gray-300 font-mono mt-2')
                    ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                        .classes('mt-6 bg-red-600 text-white')
                return
            
            if code:
                # --- LOADING STATE ---
                with ui.column().classes('items-center gap-4') as loading_container:
                    ui.spinner(size='3rem', color='#38BDF8', thickness=3) # Spinner Ciano
                    ui.label('Authenticating with Security Manager...').classes('text-cyan-400 animate-pulse font-mono text-sm')
                
                # --- LÓGICA DE BACKEND (Inalterada, apenas identação) ---
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
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-red-500/30'):
                                ui.icon('domain_disabled', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Access Denied').classes('text-2xl font-bold text-red-400 mb-2')
                                
                                ui.label(f'Email: {email}').classes('text-sm text-gray-300 font-mono bg-black/30 p-2 rounded mb-4')
                                ui.label('This email domain is not authorized.').classes('text-gray-400 mb-4')
                                
                                ui.label('Authorized domains:').classes('font-semibold text-gray-300 text-sm')
                                for d in ALLOWED_DOMAINS:
                                    ui.label(f'@{d}').classes('text-xs text-cyan-400 font-mono')
                            
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                    .classes('mt-6 bg-gray-700 hover:bg-gray-600')
                        return
                    
                    # BUSCAR USUÁRIO NO BIGQUERY
                    client = bigquery.Client(project=PROJECT_ID)
                    query = """
                        SELECT user_id, name, role, department, company, is_active
                        FROM `sys-googl-cortex-security.rls_manager.authorized_users`
                        WHERE email = @email
                        LIMIT 1
                    """
                    job_config = bigquery.QueryJobConfig(
                        query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
                    )
                    results = list(client.query(query, job_config=job_config).result())
                    
                    if not results:
                        # Usuário não cadastrado
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-orange-500/30'):
                                ui.icon('person_add_disabled', size='4rem', color='#F97316').classes('mb-4')
                                ui.label('User Not Registered').classes('text-2xl font-bold text-orange-400 mb-2')
                                
                                ui.label(f'Email: {email}').classes('text-sm text-gray-300 font-mono mb-4')
                                ui.label('You are authorized by domain, but not registered in the system.').classes('text-gray-400 text-sm mb-4')
                                ui.label('Contact Admin: admin@sysmanager.com.br').classes('text-xs text-cyan-400 font-mono')
                                
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                    .classes('mt-6 bg-gray-700')
                        return
                    
                    user_data = results[0]
                    
                    # Verificar se o usuário está ativo
                    if not user_data.is_active:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-red-500/30'):
                                ui.icon('block', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Account Inactive').classes('text-2xl font-bold text-red-400 mb-2')
                                ui.label('Your account has been deactivated by an administrator.').classes('text-gray-400')
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                    .classes('mt-6 bg-gray-700')
                        return
                    
                    # Atualizar last_login e Audit Logs (Lógica mantida igual)
                    update_query = """
                        UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                        SET last_login = CURRENT_TIMESTAMP()
                        WHERE email = @email
                    """
                    client.query(update_query, job_config=job_config).result()
                    
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
                    
                    # Salvar sessão
                    app.storage.user['authenticated'] = True
                    app.storage.user['user_info'] = {
                        'user_id': user_data.user_id,
                        'email': email,
                        'name': user_data.name or user_info.get('name', email),
                        'role': user_data.role,
                        'department': user_data.department,
                        'company': user_data.company,
                        'picture': user_info.get('picture', ''),
                        'login_time': datetime.now().isoformat()
                    }
                    
                    # Redirecionar
                    ui.run_javascript('window.location.href = "/"')
                    
                except Exception as e:
                    loading_container.clear()
                    with loading_container:
                        with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-red-500/30'):
                            ui.icon('error_outline', size='4rem', color='#F97316').classes('mb-4')
                            ui.label('Authentication Failed').classes('text-xl font-bold text-orange-400 mb-2')
                            ui.label('System Error:').classes('text-xs text-gray-400 uppercase tracking-widest')
                            ui.label(str(e)).classes('text-xs text-red-200 font-mono bg-red-900/20 p-3 rounded w-full break-all my-4')
                            ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                .classes('bg-white text-gray-900 hover:bg-gray-200')
            else:
                # Sem código nem erro, volta pro login
                ui.run_javascript('window.location.href = "/login"')
