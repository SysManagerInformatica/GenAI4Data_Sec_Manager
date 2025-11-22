"""
Serviço de Autenticação Google OAuth
"""
from nicegui import ui, app
from functools import wraps
import os
import json
import requests
from google.cloud import bigquery
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

bq_client = bigquery.Client(project=PROJECT_ID)

def require_auth(func):
    """Decorator para proteger páginas - requer autenticação"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not app.storage.user.get('authenticated'):
            ui.run_javascript('window.location.href = "/login"')
            return
        return func(*args, **kwargs)
    return wrapper

def verify_google_token(token):
    """Verifica token do Google"""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        return idinfo
    except ValueError:
        return None

def check_user_in_db(email):
    """Verifica se usuário existe no BigQuery e retorna dados"""
    query = f"""
    SELECT email, name, role, status
    FROM `{PROJECT_ID}.rls_manager.users`
    WHERE email = @email AND status = 'ACTIVE'
    LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
    )
    
    try:
        result = list(bq_client.query(query, job_config=job_config).result())
        if result:
            return dict(result[0])
    except Exception as e:
        print(f"Erro ao verificar usuário: {e}")
    
    return None

def get_current_user():
    """Retorna dados do usuário atual da sessão"""
    return app.storage.user.get('user_info', {})

def logout():
    """Limpa sessão e faz logout"""
    app.storage.user.clear()
    ui.run_javascript('window.location.href = "/login"')

def register_audit_log(action, user_email, details=""):
    """Registra ação no audit log"""
    try:
        query = f"""
        INSERT INTO `{PROJECT_ID}.rls_manager.audit_logs`
        (log_id, action, user_email, details, timestamp)
        VALUES
        (GENERATE_UUID(), @action, @user_email, @details, CURRENT_TIMESTAMP())
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("action", "STRING", action),
                bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
                bigquery.ScalarQueryParameter("details", "STRING", details)
            ]
        )
        
        bq_client.query(query, job_config=job_config).result()
    except Exception as e:
        print(f"Erro ao registrar audit log: {e}")
