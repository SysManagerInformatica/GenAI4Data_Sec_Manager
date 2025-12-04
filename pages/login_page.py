"""
Página de Login com Google OAuth Completo - Visual Dark Mode Data Fortress (FINAL)
"""
from nicegui import ui, app
import os
import requests
from google.cloud import bigquery
from datetime import datetime
import json

# --- CONFIGURAÇÕES ---
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
    """Cria a página de login e callback com visual Dark Tech"""

    # --- 1. CSS GLOBAL (Visual "Data Fortress") ---
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');

            /* Reset e Base */
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
                background-color: #0F172A; /* Navy Dark fallback */
                color: white;
            }

            /* Fundo Tech com Grid e Glow Central */
            .tech-bg {
                background-color: #0F172A;
                background-image:
                    radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.15) 0%, transparent 60%), /* Glow azul no meio */
                    linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), /* Máscara escura */
                    linear-gradient(#1e293b 1px, transparent 1px), /* Grid linhas */
                    linear-gradient(90deg, #1e293b 1px, transparent 1px); /* Grid colunas */
                background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
                min-height: 100vh;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }

            /* Card Estilo Vidro (Glassmorphism) */
            .glass-card {
                background: rgba(30, 41, 59, 0.6);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 80px rgba(56, 189, 248, 0.15); /* Glow externo */
                border-radius: 24px;
            }

            /* Título com Gradiente */
            .text-gradient {
                background: linear-gradient(to right, #ffffff 0%, #a5b4fc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }

            /* Botão Google Customizado */
            .google-btn-custom {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid transparent;
                font-weight: 600;
            }
            .google-btn-custom:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(255, 255, 255, 0.4);
            }
        </style>
    ''')

    # --- 2. PÁGINA DE LOGIN (/login) ---
    @ui.page('/login')
    def login_page():
        
        # Função para iniciar OAuth
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

        # Layout Visual
        with ui.column().classes('tech-bg'): # Fundo Tech aplicado
            
            # Card Central
            with ui.card().classes('glass-card w-full max-w-[480px] p-12 items-center text-center gap-1'):

                # Ícone BigQuery + Shield (SVG inline para garantir o visual)
                with ui.element('div').classes('relative mb-8 flex justify-center'):
                    # Glow azul atrás do ícone
                    ui.element('div').classes('absolute inset-0 bg-cyan-500 blur-3xl opacity-20 rounded-full w-24 h-24')
                    
                    # SVG Combinado
                    ui.html('''
                        <div style="position: relative; width: 80px; height: 80px;">
                            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" fill="#4285F4"/>
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="rgba(255,255,255,0.2)" stroke-width="0.5"/>
                                <path d="M11 7H13V17H11V7Z" fill="white"/>
                                <path d="M7 10H9V17H7V10Z" fill="white"/>
                                <path d="M15 13H17V17H15V13Z" fill="white"/>
                            </svg>
                            <div style="position: absolute; bottom: -5px; right: -5px; background: #0F172A; border-radius: 50%; padding: 4px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="#38BDF8">
                                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                                </svg>
                            </div>
                        </div>
                    ''')

                # Título Principal
                ui.label('GenAI4Data - Security Manager').classes('text-2xl text-gradient mb-2 tracking-tight')

                # Subtítulo (Correção: Cor Ciano Claro e visível)
                ui.label('Seamless Security for BigQuery Datasets').classes(
                    'font-mono text-sm text-cyan-300 mb-10 tracking-wide opacity-90'
                )

                # Botão de Login (Branco, Pílula)
                with ui.button(on_click=google_login) \
                        .classes('google-btn-custom w-full bg-white text-gray-900 rounded-full py-3.5 px-6 flex items-center justify-center gap-3 mb-8 shadow-lg'):
                    
                    # Logo do Google Colorido
                    ui.html('''
                        <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"/>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                    ''')
                    ui.label('Sign in with Google').classes('text-base font-bold')

                # Rodapé do Card
                ui.separator().classes('bg-gray-700/50 mb-6 w-3/4 mx-auto')
                
                with ui.row().classes('text-xs text-gray-400 justify-center items-center gap-1'):
                    ui.label('Powered by Sys Manager |')
                    ui.label('Partner Google Cloud').classes('text-gray-300 font-semibold')


    # --- 3. PÁGINA DE CALLBACK (Lógica + Visual Dark) ---
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        
        # Container com o mesmo fundo Tech para consistência
        with ui.column().classes('tech-bg'):
            
            # --- CENÁRIO DE ERRO OAUTH ---
            if error:
                with ui.card().classes('glass-card p-10 items-center text-center border-red-500/30'):
                    ui.icon('error', size='4rem', color='#EF4444').classes('mb-4')
                    ui.label('Authentication Error').classes('text-2xl font-bold text-red-400')
                    ui.label(f'Google returned: {error}').classes('text-sm text-gray-300 font-mono mt-2 bg-black/20 p-2 rounded')
                    ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                        .classes('mt-6 bg-red-600 text-white rounded-full px-6')
                return
            
            # --- CENÁRIO DE SUCESSO (LOADING & LÓGICA) ---
            if code:
                # Loading Spinner Visual
                with ui.column().classes('items-center gap-6') as loading_container:
                    ui.spinner(size='4rem', color='#38BDF8', thickness=4)
                    ui.label('Verifying Credentials...').classes('text-cyan-300 animate-pulse font-mono text-lg')
                
                # --- LÓGICA DE BACKEND ---
                # 1. Troca do Code pelo Token
                token_url = "https://oauth2.googleapis.com/token"
                token_data = {
                    'code': code,
                    'client_id': GOOGLE_CLIENT_ID,
                    'client_secret': GOOGLE_CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'grant_type': 'authorization_code'
                }
                
                try:
                    token_response = requests.post(token_url, data=token_data)
                    
                    if token_response.status_code != 200:
                        raise Exception(f"Token Exchange Failed: {token_response.text}")
                    
                    tokens = token_response.json()
                    
                    # 2. Obter Info do Usuário
                    user_info_response = requests.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
                    )
                    
                    if user_info_response.status_code != 200:
                        raise Exception(f"User Info Failed: {user_info_response.text}")
                    
                    user_info = user_info_response.json()
                    email = user_info.get('email', '')
                    
                    # 3. Verificação de Domínio
                    domain = email.split('@')[1] if '@' in email else ''
                    
                    if domain not in ALLOWED_DOMAINS:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-red-500/30'):
                                ui.icon('domain_disabled', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Access Denied').classes('text-2xl font-bold text-red-400 mb-2')
                                ui.label(f'The domain @{domain} is not authorized.').classes('text-gray-300 mb-4')
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                    .classes('mt-4 bg-gray-700 rounded-full px-6')
                        return
                    
                    # 4. Consulta no BigQuery
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
                    
                    # 5. Usuário não encontrado
                    if not results:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-orange-500/30'):
                                ui.icon('person_off', size='4rem', color='#F97316').classes('mb-4')
                                ui.label('User Not Registered').classes('text-2xl font-bold text-orange-400 mb-2')
                                ui.label('You are not registered in the security database.').classes('text-gray-300 mb-4')
                                ui.label('Contact: admin@sysmanager.com.br').classes('text-xs text-cyan-400 font-mono')
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                    .classes('mt-6 bg-gray-700 rounded-full px-6')
                        return
                    
                    user_data = results[0]
                    
                    # 6. Usuário Inativo
                    if not user_data.is_active:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center border-red-500/30'):
                                ui.icon('lock_clock', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Account Deactivated').classes('text-2xl font-bold text-red-400')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4')
                        return
                    
                    # 7. Login Sucesso: Atualizar BD e Logar
                    update_query = """
                        UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                        SET last_login = CURRENT_TIMESTAMP()
                        WHERE email = @email
                    """
                    client.query(update_query, job_config=job_config).result()
                    
                    # Auditoria
                    audit_details = json.dumps({
                        "user_name": user_data.name or user_info.get('name', ''),
                        "user_role": user_data.role,
                        "login_method": "Google OAuth"
                    })
                    
                    audit_query = """
                        INSERT INTO `sys-googl-cortex-security.rls_manager.audit_logs`
                        (timestamp, user_email, action, resource_type, resource_name, details, status)
                        VALUES
                        (CURRENT_TIMESTAMP(), @email, 'USER_LOGIN', 'AUTH', 'LOGIN_SYSTEM', PARSE_JSON(@details), 'SUCCESS')
                    """
                    audit_job_config = bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter("email", "STRING", email),
                            bigquery.ScalarQueryParameter("details", "STRING", audit_details)
                        ]
                    )
                    client.query(audit_query, job_config=audit_job_config).result()
                    
                    # 8. Salvar Sessão
                    app.storage.user['authenticated'] = True
                    app.storage.user['user_info'] = {
                        'user_id': user_data.user_id,
                        'email': email,
                        'name': user_data.name or user_info.get('name', email),
                        'role': user_data.role,
                        'picture': user_info.get('picture', '')
                    }
                    
                    # 9. Redirecionar para Home
                    ui.run_javascript('window.location.href = "/"')
                    
                except Exception as e:
                    # Tratamento de erro genérico
                    loading_container.clear()
                    with loading_container:
                        with ui.card().classes('glass-card p-8 items-center text-center max-w-lg border-red-500/30'):
                            ui.icon('bug_report', size='4rem', color='#F97316').classes('mb-4')
                            ui.label('System Error').classes('text-xl font-bold text-orange-400 mb-2')
                            ui.label(str(e)).classes('text-xs text-red-200 font-mono bg-red-900/30 p-3 rounded w-full break-all mb-4')
                            ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"')) \
                                .classes('bg-white text-gray-900 rounded-full px-6 hover:bg-gray-200')
            else:
                # Sem código, sem erro (acesso direto indevido ao callback)
                ui.run_javascript('window.location.href = "/login"')
