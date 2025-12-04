"""
Página de Login - Apenas Callback (Login HTML é servido pelo main.py)
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
    """Configura apenas o callback (a página /login é HTML servido pelo main.py)"""

    # --- PÁGINA DE CALLBACK ---
    @ui.page('/callback')
    def callback_page(code: str = None, error: str = None):
        
        # CSS do fundo hexagonal
        ui.add_head_html('''
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');

                * { margin: 0 !important; padding: 0 !important; box-sizing: border-box !important; }
                
                html, body {
                    height: 100% !important;
                    font-family: 'Inter', sans-serif !important;
                    overflow: hidden !important;
                }

                .nicegui-content {
                    background-color: #0A1929 !important;
                    min-height: 100vh !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }

                .tech-bg-hex {
                    background: linear-gradient(135deg, #0a1929 0%, #1a2942 50%, #0a1929 100%) !important;
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

                .tech-bg-hex::before {
                    content: '' !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-image: url("data:image/svg+xml,%3Csvg width='100' height='87' viewBox='0 0 100 87' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M25 0l25 14.43V43.3L25 57.74 0 43.3V14.43L25 0zm0 2.89L2 16.32v25.76L25 54.85l23-13.77V16.32L25 2.89z' fill='%232d5a8c' fill-opacity='0.7'/%3E%3C/svg%3E") !important;
                    background-size: 100px 87px !important;
                    opacity: 0.9 !important;
                    z-index: 1 !important;
                }

                .tech-bg-hex::after {
                    content: '' !important;
                    position: absolute !important;
                    top: 50% !important;
                    left: 50% !important;
                    transform: translate(-50%, -50%) !important;
                    width: 1400px !important;
                    height: 1400px !important;
                    background: radial-gradient(circle, rgba(100, 150, 255, 0.3) 0%, rgba(150, 100, 255, 0.2) 30%, rgba(100, 150, 255, 0.1) 50%, transparent 70%) !important;
                    border-radius: 50% !important;
                    z-index: 2 !important;
                    animation: pulse-glow 6s ease-in-out infinite !important;
                }

                @keyframes pulse-glow {
                    0%, 100% { opacity: 0.7; transform: translate(-50%, -50%) scale(1); }
                    50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
                }

                .glass-card {
                    background: rgba(15, 35, 65, 0.7) !important;
                    backdrop-filter: blur(50px) !important;
                    -webkit-backdrop-filter: blur(50px) !important;
                    border: 2px solid rgba(120, 170, 255, 0.4) !important;
                    box-shadow: 0 0 100px rgba(100, 150, 255, 0.4), 0 0 50px rgba(100, 150, 255, 0.3), inset 0 0 40px rgba(100, 150, 255, 0.1) !important;
                    border-radius: 24px !important;
                    position: relative !important;
                    z-index: 100 !important;
                }
            </style>
        ''')
        
        with ui.element('div').classes('tech-bg-hex'):
            
            if error:
                with ui.card().classes('glass-card').style('padding: 2.5rem; max-width: 500px; border-color: rgba(239, 68, 68, 0.5);'):
                    ui.icon('error', size='4rem', color='#EF4444').style('margin-bottom: 1rem;')
                    ui.label('Authentication Error').style('font-size: 1.5rem; font-weight: 700; color: #f87171;')
                    ui.label(f'Google: {error}').style('font-size: 0.875rem; color: #d1d5db; font-family: monospace; background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 0.5rem; margin-top: 0.5rem;')
                    ui.button('Back to Login', on_click=lambda: ui.run_javascript('window.location.href = "/login"')).style('margin-top: 1.5rem; background: #dc2626; color: white; border-radius: 9999px; padding: 0.5rem 1.5rem;')
                return
            
            if code:
                with ui.column().style('display: flex; align-items: center; gap: 1.5rem; z-index: 100;') as loading_container:
                    ui.spinner(size='4rem', color='#60a5fa', thickness=4)
                    ui.label('Verifying Credentials...').style('color: #93c5fd; font-family: monospace; font-size: 1.125rem;')
                
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
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(239, 68, 68, 0.5);'):
                                ui.icon('domain_disabled', size='4rem', color='#EF4444')
                                ui.label('Access Denied').style('font-size: 1.5rem; color: #f87171; font-weight: 700;')
                                ui.label(f'Domain @{domain} not authorized').style('color: #d1d5db;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
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
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(249, 115, 22, 0.5);'):
                                ui.icon('person_off', size='4rem', color='#F97316')
                                ui.label('User Not Registered').style('font-size: 1.5rem; color: #fb923c; font-weight: 700;')
                                ui.label('Contact: admin@sysmanager.com.br').style('color: #67e8f9; font-family: monospace; font-size: 0.75rem;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
                        return
                    
                    user_data = results[0]
                    if not user_data.is_active:
                        loading_container.clear()
                        with loading_container:
                            with ui.card().classes('glass-card').style('padding: 2rem; max-width: 500px; border-color: rgba(239, 68, 68, 0.5);'):
                                ui.icon('lock_clock', size='4rem', color='#EF4444')
                                ui.label('Account Deactivated').style('font-size: 1.5rem; color: #f87171; font-weight: 700;')
                                ui.button('Back', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
                        return
                    
                    # Atualiza last_login
                    update_query = """
                        UPDATE `sys-googl-cortex-security.rls_manager.authorized_users`
                        SET last_login = CURRENT_TIMESTAMP()
                        WHERE email = @email
                    """
                    client.query(update_query, job_config=job_config).result()
                    
                    # Registra no audit log
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
                    
                    # Salva na sessão
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
                        with ui.card().classes('glass-card').style('padding: 2rem; max-width: 600px; border-color: rgba(239, 68, 68, 0.5);'):
                            ui.icon('bug_report', size='4rem', color='#F97316')
                            ui.label('System Error').style('font-size: 1.25rem; color: #fb923c; font-weight: 700;')
                            ui.label(str(e)).style('font-size: 0.75rem; color: #fca5a5; font-family: monospace; background: rgba(127, 29, 29, 0.3); padding: 0.75rem; border-radius: 0.5rem; word-break: break-all;')
                            ui.button('Try Again', on_click=lambda: ui.run_javascript('window.location.href = "/login"'))
            else:
                ui.run_javascript('window.location.href = "/login"')
