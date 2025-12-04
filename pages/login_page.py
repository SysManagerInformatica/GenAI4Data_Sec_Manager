"""
Página de Login com Google OAuth - Visual Hexagonal Tech (CORRIGIDO)
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
    """Cria a página de login e callback com visual Hexagonal Tech"""

    # --- 1. CSS GLOBAL (FORÇADO COM !important) ---
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');

            /* Reset FORÇADO */
            html, body {
                height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                font-family: 'Inter', sans-serif !important;
                background-color: #0A1929 !important;
                color: white !important;
                overflow-x: hidden !important;
            }

            /* Força o container principal do NiceGUI */
            .nicegui-content {
                background-color: #0A1929 !important;
                min-height: 100vh !important;
            }

            /* Fundo Hexagonal Tech */
            .tech-bg-hex {
                background-color: #0A1929 !important;
                position: relative !important;
                min-height: 100vh !important;
                width: 100% !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                overflow: hidden !important;
                padding: 2rem !important;
            }

            /* SVG Hexagonal Pattern */
            .tech-bg-hex::before {
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                background-image: url("data:image/svg+xml,%3Csvg width='100' height='87' viewBox='0 0 100 87' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M25 0l25 14.43V43.3L25 57.74 0 43.3V14.43L25 0zm0 2.89L2 16.32v25.76L25 54.85l23-13.77V16.32L25 2.89z' fill='%231e3a5f' fill-opacity='0.4'/%3E%3C/svg%3E") !important;
                background-size: 100px 87px !important;
                opacity: 0.6 !important;
                z-index: 0 !important;
            }

            /* Glow Central Animado */
            .tech-bg-hex::after {
                content: '' !important;
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                width: 800px !important;
                height: 800px !important;
                background: radial-gradient(circle, rgba(100, 150, 255, 0.15) 0%, rgba(150, 100, 255, 0.08) 40%, transparent 70%) !important;
                border-radius: 50% !important;
                z-index: 0 !important;
                animation: pulse-glow 8s ease-in-out infinite !important;
            }

            @keyframes pulse-glow {
                0%, 100% { opacity: 0.6; transform: translate(-50%, -50%) scale(1); }
                50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.05); }
            }

            /* Card Glassmorphism */
            .glass-card {
                background: rgba(20, 40, 70, 0.5) !important;
                backdrop-filter: blur(30px) !important;
                -webkit-backdrop-filter: blur(30px) !important;
                border: 1.5px solid rgba(100, 150, 255, 0.2) !important;
                box-shadow: 
                    0 0 60px rgba(100, 150, 255, 0.2),
                    inset 0 0 20px rgba(100, 150, 255, 0.05) !important;
                border-radius: 24px !important;
                position: relative !important;
                z-index: 10 !important;
            }

            /* Título Gradiente */
            .text-gradient-white {
                background: linear-gradient(to right, #ffffff 0%, #e0e7ff 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
            }

            /* Subtítulo */
            .subtitle-mono {
                font-family: 'JetBrains Mono', monospace !important;
                color: #a5b4fc !important;
                font-size: 0.875rem !important;
                letter-spacing: 0.05em !important;
                opacity: 0.9 !important;
            }

            /* Botão Google */
            .google-btn-custom {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                border: 1px solid transparent !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15) !important;
            }
            .google-btn-custom:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 12px 35px rgba(255, 255, 255, 0.3) !important;
            }

            /* Footer */
            .footer-text {
                color: rgba(255, 255, 255, 0.5) !important;
                font-size: 0.75rem !important;
            }
            .footer-text-highlight {
                color: rgba(255, 255, 255, 0.8) !important;
                font-weight: 600 !important;
            }
        </style>
    ''')

    # --- 2. PÁGINA DE LOGIN ---
    @ui.page('/login')
    def login_page():
        # Remove qualquer padding/margin padrão da página
        ui.query('body').style('margin: 0; padding: 0; background: #0A1929;')
        
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

        # Container principal com fundo hexagonal
        with ui.element('div').classes('tech-bg-hex').style('min-height: 100vh; width: 100%;'):
            
            # Card Central
            with ui.card().classes('glass-card w-full max-w-[520px] p-12 items-center text-center gap-1').style('margin: auto;'):

                # Ícone BigQuery + Shield
                with ui.element('div').classes('relative mb-8 flex justify-center'):
                    ui.element('div').classes('absolute inset-0 bg-blue-500 blur-3xl opacity-30 rounded-full w-32 h-32')
                    
                    ui.html('''
                        <div style="position: relative; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center;">
                            <svg width="90" height="90" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" fill="#4285F4" opacity="0.9"/>
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="rgba(255,255,255,0.3)" stroke-width="0.4"/>
                                <path d="M11 7H13V17H11V7Z" fill="white" opacity="0.95"/>
                                <path d="M7 10H9V17H7V10Z" fill="white" opacity="0.95"/>
                                <path d="M15 13H17V17H15V13Z" fill="white" opacity="0.95"/>
                            </svg>
                            <div style="position: absolute; bottom: -8px; right: -8px; background: #0A1929; border-radius: 50%; padding: 5px; border: 2px solid rgba(100, 150, 255, 0.3);">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="#38BDF8">
                                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                                </svg>
                            </div>
                        </div>
                    ''')

                # Título
                ui.label('GenAI4Data - Security Manager').classes('text-3xl text-gradient-white mb-2')

                # Subtítulo
                ui.label('Seamless Security for BigQuery Datasets').classes('subtitle-mono mb-10')

                # Botão Google
                with ui.button(on_click=google_login).classes('google-btn-custom w-full bg-white text-gray-900 rounded-full py-4 px-8 flex items-center justify-center gap-3 mb-8'):
                    ui.html('''
                        <svg width="22" height="22" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"/>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                    ''')
                    ui.label('Sign in with Google').classes('text-base font-bold')

                # Rodapé
                ui.separator().classes('bg-white/10 mb-6 w-3/4 mx-auto')
                
                with ui.row().classes('justify-center items-center gap-1.5'):
                    ui.label('Powered by Sys Manager |').classes('footer-text')
                    ui.label('Partner Google Cloud').classes('footer-text-highlight')


    # --- 3. PÁGINA DE CALLBACK ---
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        ui.query('body').style('margin: 0; padding: 0; background: #0A1929;')
        
        with ui.element('div').classes('tech-bg-hex'):
            
            if error:
                with ui.card().classes('glass-card p-10 items-center text-center border-red-500/30 max-w-md'):
                    ui.icon('error', size='4rem', color='#EF4444').classes('mb-4')
                    ui.label('Authentication Error').classes('text-2xl font-bold text-red-400')
                    ui.label(f'Google returned: {error}').classes('text-sm text-gray-300 font-mono mt-2 bg-black/20 p-2 rounded')
                    ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-6 bg-red-600 text-white rounded-full px-6 py-2')
                return
            
            if code:
                with ui.column().classes('items-center gap-6') as loading_container:
                    ui.spinner(size='4rem', color='#38BDF8', thickness=4)
                    ui.label('Verifying Credentials...').classes('text-cyan-300 animate-pulse font-mono text-lg')
                
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
                    
                    user_info_response = requests.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
                    )
                    
                    if user_info_response.status_code != 200:
                        raise Exception(f"User Info Failed: {user_info_response.text}")
                    
                    user_info = user_info_response.json()
                    email = user_info.get('email', '')
                    
                    domain = email.split('@')[1] if '@' in email else ''
                    
                    if domain not in ALLOWED_DOMAINS:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-red-500/30'):
                                ui.icon('domain_disabled', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Access Denied').classes('text-2xl font-bold text-red-400 mb-2')
                                ui.label(f'The domain @{domain} is not authorized.').classes('text-gray-300 mb-4')
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4 bg-gray-700 rounded-full px-6 py-2')
                        return
                    
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
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center max-w-md border-orange-500/30'):
                                ui.icon('person_off', size='4rem', color='#F97316').classes('mb-4')
                                ui.label('User Not Registered').classes('text-2xl font-bold text-orange-400 mb-2')
                                ui.label('You are not registered in the security database.').classes('text-gray-300 mb-4')
                                ui.label('Contact: admin@sysmanager.com.br').classes('text-xs text-cyan-400 font-mono')
                                ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-6 bg-gray-700 rounded-full px-6 py-2')
                        return
                    
                    user_data = results[0]
                    
                    if not user_data.is_active:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card p-8 items-center text-center border-red-500/30 max-w-md'):
                                ui.icon('lock_clock', size='4rem', color='#EF4444').classes('mb-4')
                                ui.label('Account Deactivated').classes('text-2xl font-bold text-red-400')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('mt-4 rounded-full px-6 py-2')
                        return
                    
                    update_query = """
                        UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                        SET last_login = CURRENT_TIMESTAMP()
                        WHERE email = @email
                    """
                    client.query(update_query, job_config=job_config).result()
                    
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
                    
                    app.storage.user['authenticated'] = True
                    app.storage.user['user_info'] = {
                        'user_id': user_data.user_id,
                        'email': email,
                        'name': user_data.name or user_info.get('name', email),
                        'role': user_data.role,
                        'picture': user_info.get('picture', '')
                    }
                    
                    ui.run_javascript('window.location.href = "/"')
                    
                except Exception as e:
                    loading_container.clear()
                    with loading_container:
                        with ui.card().classes('glass-card p-8 items-center text-center max-w-lg border-red-500/30'):
                            ui.icon('bug_report', size='4rem', color='#F97316').classes('mb-4')
                            ui.label('System Error').classes('text-xl font-bold text-orange-400 mb-2')
                            ui.label(str(e)).classes('text-xs text-red-200 font-mono bg-red-900/30 p-3 rounded w-full break-all mb-4')
                            ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).classes('bg-white text-gray-900 rounded-full px-6 py-2 hover:bg-gray-200')
            else:
                ui.run_javascript('window.location.href = "/login"')
