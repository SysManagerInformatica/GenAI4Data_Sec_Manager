"""
Página de Login com Google OAuth - Visual Hexagonal Tech FINAL
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

ALLOWED_DOMAINS = [
    'sysmanager.com.br',
    'sysmngr.com',
    'sysmanagerinformatica.com.br'
]

def create_login_page():
    """Cria a página de login com visual Hexagonal Tech"""

    # --- CSS GLOBAL COM EFEITOS INTENSIFICADOS ---
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');

            * {
                margin: 0 !important;
                padding: 0 !important;
                box-sizing: border-box !important;
            }

            html, body {
                height: 100% !important;
                font-family: 'Inter', sans-serif !important;
                background-color: #0A1929 !important;
                color: white !important;
                overflow: hidden !important;
            }

            .nicegui-content {
                background-color: #0A1929 !important;
                min-height: 100vh !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Fundo Hexagonal com Efeitos Intensos */
            .tech-bg-hex {
                background-color: #0A1929 !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                overflow: hidden !important;
            }

            /* Padrão Hexagonal (mais visível) */
            .tech-bg-hex::before {
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                background-image: url("data:image/svg+xml,%3Csvg width='100' height='87' viewBox='0 0 100 87' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M25 0l25 14.43V43.3L25 57.74 0 43.3V14.43L25 0zm0 2.89L2 16.32v25.76L25 54.85l23-13.77V16.32L25 2.89z' fill='%232d5a8c' fill-opacity='0.6'/%3E%3C/svg%3E") !important;
                background-size: 100px 87px !important;
                opacity: 0.8 !important;
                z-index: 1 !important;
            }

            /* Glow Central MUITO Intenso */
            .tech-bg-hex::after {
                content: '' !important;
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                width: 1200px !important;
                height: 1200px !important;
                background: radial-gradient(
                    circle, 
                    rgba(100, 150, 255, 0.25) 0%, 
                    rgba(150, 100, 255, 0.15) 30%,
                    rgba(100, 150, 255, 0.08) 50%, 
                    transparent 70%
                ) !important;
                border-radius: 50% !important;
                z-index: 2 !important;
                animation: pulse-glow 6s ease-in-out infinite !important;
            }

            @keyframes pulse-glow {
                0%, 100% { 
                    opacity: 0.7; 
                    transform: translate(-50%, -50%) scale(1); 
                }
                50% { 
                    opacity: 1; 
                    transform: translate(-50%, -50%) scale(1.1); 
                }
            }

            /* Linhas Verticais (efeito circuito) */
            .tech-lines {
                position: absolute !important;
                top: 0 !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 80% !important;
                height: 100% !important;
                background: repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 100px,
                    rgba(100, 150, 255, 0.03) 100px,
                    rgba(100, 150, 255, 0.03) 101px
                ) !important;
                z-index: 1 !important;
            }

            /* Card Glassmorphism Intensificado */
            .glass-card {
                background: rgba(15, 35, 65, 0.6) !important;
                backdrop-filter: blur(40px) !important;
                -webkit-backdrop-filter: blur(40px) !important;
                border: 2px solid rgba(120, 170, 255, 0.3) !important;
                box-shadow: 
                    0 0 80px rgba(100, 150, 255, 0.3),
                    0 0 40px rgba(100, 150, 255, 0.2),
                    inset 0 0 30px rgba(100, 150, 255, 0.08) !important;
                border-radius: 24px !important;
                position: relative !important;
                z-index: 100 !important;
            }

            /* Título com Gradiente Branco */
            .text-gradient-white {
                background: linear-gradient(to right, #ffffff 0%, #c7d2fe 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
            }

            /* Subtítulo Monospace */
            .subtitle-mono {
                font-family: 'JetBrains Mono', monospace !important;
                color: #bfdbfe !important;
                font-size: 0.875rem !important;
                letter-spacing: 0.05em !important;
                opacity: 0.95 !important;
            }

            /* Botão Google - TEXTO VISÍVEL */
            .google-btn-custom {
                background-color: #ffffff !important;
                color: #1f2937 !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                border: none !important;
                font-weight: 600 !important;
                box-shadow: 0 6px 25px rgba(255, 255, 255, 0.2) !important;
                cursor: pointer !important;
            }
            
            .google-btn-custom:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 15px 40px rgba(255, 255, 255, 0.35) !important;
                background-color: #f9fafb !important;
            }

            /* Texto do botão - FORÇAR VISIBILIDADE */
            .google-btn-text {
                color: #1f2937 !important;
                font-size: 1rem !important;
                font-weight: 700 !important;
            }

            /* Footer */
            .footer-text {
                color: rgba(255, 255, 255, 0.6) !important;
                font-size: 0.75rem !important;
            }
            
            .footer-text-highlight {
                color: rgba(255, 255, 255, 0.9) !important;
                font-weight: 600 !important;
            }
        </style>
    ''')

    # --- PÁGINA DE LOGIN ---
    @ui.page('/login')
    def login_page():
        
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

        # Container com fundo hexagonal
        with ui.element('div').classes('tech-bg-hex'):
            
            # Linhas verticais (efeito circuito)
            ui.element('div').classes('tech-lines')
            
            # Card Central
            with ui.card().classes('glass-card').style('width: 520px; max-width: 90%; padding: 3rem; display: flex; flex-direction: column; align-items: center; text-align: center;'):

                # Ícone BigQuery + Shield
                with ui.element('div').style('position: relative; margin-bottom: 2rem; display: flex; justify-content: center;'):
                    # Glow do ícone
                    ui.element('div').style('position: absolute; inset: 0; background: #60a5fa; filter: blur(60px); opacity: 0.4; border-radius: 50%; width: 120px; height: 120px;')
                    
                    ui.html('''
                        <div style="position: relative; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center;">
                            <svg width="90" height="90" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" fill="#4285F4" opacity="0.95"/>
                                <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="rgba(255,255,255,0.4)" stroke-width="0.5"/>
                                <path d="M11 7H13V17H11V7Z" fill="white" opacity="0.98"/>
                                <path d="M7 10H9V17H7V10Z" fill="white" opacity="0.98"/>
                                <path d="M15 13H17V17H15V13Z" fill="white" opacity="0.98"/>
                            </svg>
                            <div style="position: absolute; bottom: -8px; right: -8px; background: #0A1929; border-radius: 50%; padding: 5px; border: 2px solid rgba(120, 170, 255, 0.4);">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="#60a5fa">
                                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                                </svg>
                            </div>
                        </div>
                    ''')

                # Título
                ui.label('GenAI4Data - Security Manager').classes('text-gradient-white').style('font-size: 1.875rem; margin-bottom: 0.5rem;')

                # Subtítulo
                ui.label('Seamless Security for BigQuery Datasets').classes('subtitle-mono').style('margin-bottom: 2.5rem;')

                # Botão Google com texto GARANTIDO visível
                with ui.button(on_click=google_login).classes('google-btn-custom').style(
                    'width: 100%; '
                    'padding: 1rem 2rem; '
                    'border-radius: 9999px; '
                    'display: flex; '
                    'align-items: center; '
                    'justify-content: center; '
                    'gap: 0.75rem; '
                    'margin-bottom: 2rem;'
                ):
                    # Logo Google
                    ui.html('''
                        <svg width="22" height="22" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"/>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                    ''')
                    # Texto do botão - GARANTIDO VISÍVEL
                    ui.html('<span style="color: #1f2937 !important; font-weight: 700 !important; font-size: 1rem !important;">Sign in with Google</span>')

                # Separador
                ui.separator().style('background: rgba(255, 255, 255, 0.15); margin-bottom: 1.5rem; width: 75%;')
                
                # Footer
                with ui.row().style('display: flex; justify-content: center; align-items: center; gap: 0.375rem;'):
                    ui.label('Powered by Sys Manager |').classes('footer-text')
                    ui.label('Partner Google Cloud').classes('footer-text-highlight')


    # --- PÁGINA DE CALLBACK (mesmo visual) ---
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        
        with ui.element('div').classes('tech-bg-hex'):
            ui.element('div').classes('tech-lines')
            
            if error:
                with ui.card().classes('glass-card').style('padding: 2.5rem; max-width: 500px; display: flex; flex-direction: column; align-items: center; text-align: center; border-color: rgba(239, 68, 68, 0.3);'):
                    ui.icon('error', size='4rem', color='#EF4444').style('margin-bottom: 1rem;')
                    ui.label('Authentication Error').style('font-size: 1.5rem; font-weight: 700; color: #f87171; margin-bottom: 0.5rem;')
                    ui.label(f'Google returned: {error}').style('font-size: 0.875rem; color: #d1d5db; font-family: monospace; background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 0.5rem; margin-top: 0.5rem;')
                    ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).style('margin-top: 1.5rem; background: #dc2626; color: white; border-radius: 9999px; padding: 0.5rem 1.5rem;')
                return
            
            if code:
                with ui.column().style('display: flex; align-items: center; gap: 1.5rem;') as loading_container:
                    ui.spinner(size='4rem', color='#60a5fa', thickness=4)
                    ui.label('Verifying Credentials...').style('color: #93c5fd; font-family: monospace; font-size: 1.125rem; animation: pulse 2s ease-in-out infinite;')
                
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
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(239, 68, 68, 0.3);'):
                                ui.icon('domain_disabled', size='4rem', color='#EF4444')
                                ui.label('Access Denied').style('font-size: 1.5rem; color: #f87171; font-weight: 700;')
                                ui.label(f'Domain @{domain} not authorized').style('color: #d1d5db;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).style('border-radius: 9999px; padding: 0.5rem 1.5rem;')
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
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(249, 115, 22, 0.3);'):
                                ui.icon('person_off', size='4rem', color='#F97316')
                                ui.label('User Not Registered').style('font-size: 1.5rem; color: #fb923c; font-weight: 700;')
                                ui.label('Contact: admin@sysmanager.com.br').style('color: #67e8f9; font-family: monospace; font-size: 0.75rem;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
                        return
                    
                    user_data = results[0]
                    if not user_data.is_active:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(239, 68, 68, 0.3);'):
                                ui.icon('lock_clock', size='4rem', color='#EF4444')
                                ui.label('Account Deactivated').style('font-size: 1.5rem; color: #f87171; font-weight: 700;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
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
                        with ui.card().classes('glass-card').style('padding: 2rem; max-width: 600px; border-color: rgba(239, 68, 68, 0.3);'):
                            ui.icon('bug_report', size='4rem', color='#F97316')
                            ui.label('System Error').style('font-size: 1.25rem; color: #fb923c; font-weight: 700;')
                            ui.label(str(e)).style('font-size: 0.75rem; color: #fca5a5; font-family: monospace; background: rgba(127, 29, 29, 0.3); padding: 0.75rem; border-radius: 0.5rem; width: 100%; word-break: break-all;')
                            ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).style('background: white; color: #1f2937; border-radius: 9999px; padding: 0.5rem 1.5rem;')
            else:
                ui.run_javascript('window.location.href = "/login"')
