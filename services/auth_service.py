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

def check_permission(role, resource, permission):
    """
    Verifica se um role tem permissão específica para um recurso
    
    Args:
        role: Role do usuário (OWNER, ADMIN, EDITOR, VIEWER)
        resource: Recurso a ser acessado (RLS_POLICIES, CLS_POLICIES, AUDIT_LOGS, USERS)
        permission: Tipo de permissão (can_view, can_create, can_edit, can_delete)
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    # Buscar permissão no BigQuery
    try:
        query = f"""
        SELECT {permission}
        FROM `{PROJECT_ID}.rls_manager.role_permissions`
        WHERE role = @role AND resource = @resource
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("role", "STRING", role),
                bigquery.ScalarQueryParameter("resource", "STRING", resource)
            ]
        )
        
        result = list(bq_client.query(query, job_config=job_config).result())
        if result:
            return result[0][0]  # Retorna o valor booleano da permissão
    except Exception as e:
        print(f"Erro ao verificar permissão: {e}")
    
    # Fallback - verificação básica por role
    if role == 'OWNER':
        return True
    elif role == 'ADMIN':
        return permission != 'can_delete' or resource != 'USERS'
    elif role == 'EDITOR':
        return permission in ['can_view', 'can_create', 'can_edit'] and resource != 'AUDIT_LOGS'
    elif role == 'VIEWER':
        return permission == 'can_view' and resource != 'AUDIT_LOGS'
    
    return False

def get_current_user():
    """Retorna dados do usuário atual da sessão"""
    return app.storage.user.get('user_info', {})

def logout():
    """Limpa sessão e faz logout"""
    app.storage.user.clear()
    ui.run_javascript('window.location.href = "/login"')

def register_audit_log(action, user_email, details="", status="SUCCESS"):
    """
    Registra ação no audit log
    
    Args:
        action: Ação realizada
        user_email: Email do usuário
        details: Detalhes da ação
        status: Status da ação (SUCCESS, FAILED, DENIED)
    """
    try:
        query = f"""
        INSERT INTO `{PROJECT_ID}.rls_manager.audit_logs`
        (log_id, action, user_email, details, status, timestamp)
        VALUES
        (GENERATE_UUID(), @action, @user_email, @details, @status, CURRENT_TIMESTAMP())
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("action", "STRING", action),
                bigquery.ScalarQueryParameter("user_email", "STRING", user_email),
                bigquery.ScalarQueryParameter("details", "STRING", details),
                bigquery.ScalarQueryParameter("status", "STRING", status)
            ]
        )
        
        bq_client.query(query, job_config=job_config).result()
    except Exception as e:
        print(f"Erro ao registrar audit log: {e}")
