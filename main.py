"""
================================================================================
  GenAI4Data Security Manager
  Module: Main Application Entry Point
================================================================================
  Version:      2.1.0
  Release Date: 2024-12-15
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Main application entry point and server initialization. Handles NiceGUI
  server configuration, authentication routing, multi-language system,
  static file serving, and page registration.
================================================================================
"""

import os
import sys
from nicegui import ui, app
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from typing import Dict, Any

# Configuração de porta
PORT = int(os.environ.get('PORT', 8080))
STORAGE_SECRET = os.environ.get('SESSION_SECRET', 'default-secret-key')

# Configurar storage
app.storage.secret = STORAGE_SECRET

# ========================================
# Dark Mode Global
# ========================================
ui.dark_mode().enable()
print("✓ Dark mode enabled globally")

# ========================================
# LANGUAGE SYSTEM  # <- NOVO
# ========================================

def detect_browser_language(request: Request) -> str:
    """
    Detect browser language from Accept-Language header
    Returns: Language code ('pt', 'en', 'es')
    """
    accept_language = request.headers.get('accept-language', '')
    
    # Parse Accept-Language header
    if accept_language:
        # Format: "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        languages = accept_language.lower().split(',')
        
        for lang in languages:
            # Remove quality values (q=0.9)
            lang_code = lang.split(';')[0].strip()
            
            # Extract main language code
            if lang_code.startswith('pt'):
                return 'pt'
            elif lang_code.startswith('es'):
                return 'es'
            elif lang_code.startswith('en'):
                return 'en'
    
    # Default to English
    return 'en'


@app.post('/api/set-language')  # <- NOVO
async def set_language(request: Request):
    """
    API endpoint to set user's preferred language
    
    Request body:
        {
            "language": "pt" | "en" | "es"
        }
    
    Returns:
        {
            "status": "success",
            "language": "pt"
        }
    """
    try:
        # Parse JSON body
        body = await request.json()
        language = body.get('language', 'en')
        
        # Validate language
        valid_languages = ['pt', 'en', 'es']
        if language not in valid_languages:
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': f'Invalid language. Must be one of: {valid_languages}'
                }
            )
        
        # Save to user storage
        app.storage.user['language'] = language
        
        print(f"✓ Language set to: {language}")
        
        return JSONResponse(
            content={
                'status': 'success',
                'language': language
            }
        )
    
    except Exception as e:
        print(f"✗ Error setting language: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': str(e)
            }
        )


@app.get('/api/get-language')  # <- NOVO
async def get_language():
    """
    API endpoint to get user's current language
    
    Returns:
        {
            "language": "pt"
        }
    """
    language = app.storage.user.get('language', 'en')
    
    return JSONResponse(
        content={
            'language': language
        }
    )


def init_user_language(request: Request = None):  # <- NOVO
    """
    Initialize user language on first visit
    - Check if language already set in session
    - If not, detect from browser
    """
    # Check if language already set
    if 'language' not in app.storage.user:
        # Detect from browser
        if request:
            detected_lang = detect_browser_language(request)
        else:
            detected_lang = 'en'
        
        app.storage.user['language'] = detected_lang
        print(f"✓ Language initialized: {detected_lang}")


# ========================================
# Static Files
# ========================================

# Montar diretório static para servir arquivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')
    print("✓ Static directory mounted successfully")
else:
    print(f"✗ Warning: Static directory not found at {static_dir}")

# ========================================
# Login Page (HTML Puro)
# ========================================

@app.get('/login', response_class=HTMLResponse)
async def serve_login_html(request: Request):  # <- MODIFICADO: adicionado request
    """Serve a página HTML pura do login"""
    
    # Initialize language on first visit  # <- NOVO
    init_user_language(request)
    
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'login.html')
    
    if not os.path.exists(html_path):
        print(f"✗ Error: login.html not found at {html_path}")
        return HTMLResponse(
            content="<h1>Login page not found</h1><p>Please contact administrator</p>", 
            status_code=404
        )
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Injeta as variáveis de ambiente
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
        REDIRECT_URI = os.getenv('REDIRECT_URI', '')
        
        html_content = html_content.replace('{{GOOGLE_CLIENT_ID}}', GOOGLE_CLIENT_ID)
        html_content = html_content.replace('{{REDIRECT_URI}}', REDIRECT_URI)
        
        print("✓ Login HTML served successfully")
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        print(f"✗ Error serving login HTML: {e}")
        return HTMLResponse(
            content=f"<h1>Error loading login page</h1><p>{str(e)}</p>", 
            status_code=500
        )

# ========================================
# Login Callback
# ========================================

# Tentar importar login page (agora só registra o /callback)
try:
    from pages.login_page import create_login_page
    create_login_page()
    print("✓ Login callback page created successfully")
except Exception as e:
    print(f"✗ Error creating login callback: {e}")
    # Login callback é crítico
    
    @ui.page('/callback')
    def emergency_callback():
        ui.label('System Error - Could not load login callback').classes('text-red-600')
        ui.label(str(e)).classes('text-sm')

# ========================================
# Theme and Home
# ========================================

# Tentar importar theme e home
try:
    from theme import frame
    from home import content as home_content
    print("✓ Theme and home imported successfully")
except Exception as e:
    print(f"✗ Error importing theme/home: {e}")
    frame = lambda x: ui.column()
    home_content = lambda: ui.label('Welcome to GenAI4Data Security Manager')

# ========================================
# All Pages
# ========================================

# Tentar criar outras páginas (não crítico)
try:
    import allpages
    allpages.create()
    print("✓ All pages created successfully")
except Exception as e:
    print(f"✗ Warning: Could not load all pages: {e}")
    # Não é crítico, podemos continuar

# ========================================
# Dataset IAM Manager (Fallback)
# ========================================

try:
    from pages.dataset_iam_manager import DatasetIAMManager
    
    @ui.page('/datasetiammanager/')
    def dataset_iam_manager_page():
        if not app.storage.user.get('authenticated', False):
            ui.run_javascript('window.location.href = "/login"')
            return
        DatasetIAMManager()
    
    print("✓ Dataset IAM Manager route registered successfully")
except Exception as e:
    print(f"✗ Warning: Could not register Dataset IAM Manager: {e}")

# ========================================
# Home Page
# ========================================

@ui.page('/')
def home():
    if not app.storage.user.get('authenticated', False):
        ui.run_javascript('window.location.href = "/login"')
        return
    
    # Initialize language if not set  # <- NOVO
    if 'language' not in app.storage.user:
        app.storage.user['language'] = 'en'
    
    try:
        with frame('Home'):
            home_content()
    except Exception as e:
        ui.label('Error loading home page').classes('text-red-600')
        ui.label(str(e))

# ========================================
# Health Check
# ========================================

@ui.page('/health')
def health():
    ui.label('Service is running on port ' + str(PORT))
    ui.label('Static login: ' + ('✓ Enabled' if os.path.exists(static_dir) else '✗ Disabled'))
    
    # Show current language  # <- NOVO
    current_lang = app.storage.user.get('language', 'not set')
    ui.label(f'Current language: {current_lang}')

# ========================================
# Startup
# ========================================

print(f"Starting NiceGUI on port {PORT}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print("✓ Multi-language system enabled")  # <- NOVO

ui.run(
    port=PORT,
    host='0.0.0.0',
    title='GenAI4Data Security Manager',
    favicon='🔒',
    storage_secret=STORAGE_SECRET,
    reload=False
)
