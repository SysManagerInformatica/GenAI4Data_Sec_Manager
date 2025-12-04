import os
import sys
from nicegui import ui, app
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Configuração de porta
PORT = int(os.environ.get('PORT', 8080))
STORAGE_SECRET = os.environ.get('SESSION_SECRET', 'default-secret-key')

# Configurar storage
app.storage.secret = STORAGE_SECRET

# ========================================
# ADICIONAR: Montar diretório static e rota HTML
# ========================================

# Montar diretório static para servir arquivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')
    print("✓ Static directory mounted successfully")
else:
    print(f"✗ Warning: Static directory not found at {static_dir}")

# Rota para servir login.html (HTML PURO - sem NiceGUI)
@app.get('/login', response_class=HTMLResponse)
async def serve_login_html():
    """Serve a página HTML pura do login"""
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
# FIM DAS ADIÇÕES
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

# Tentar importar theme e home
try:
    from theme import frame
    from home import content as home_content
    print("✓ Theme and home imported successfully")
except Exception as e:
    print(f"✗ Error importing theme/home: {e}")
    frame = lambda x: ui.column()
    home_content = lambda: ui.label('Welcome to GenAI4Data Security Manager')

# Tentar criar outras páginas (não crítico)
try:
    import allpages
    allpages.create()
    print("✓ All pages created successfully")
except Exception as e:
    print(f"✗ Warning: Could not load all pages: {e}")
    # Não é crítico, podemos continuar

# ✅ ADICIONAR ROTA DO DATASET IAM MANAGER (FALLBACK)
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

# Página inicial
@ui.page('/')
def home():
    if not app.storage.user.get('authenticated', False):
        ui.run_javascript('window.location.href = "/login"')
        return
    
    try:
        with frame('Home'):
            home_content()
    except Exception as e:
        ui.label('Error loading home page').classes('text-red-600')
        ui.label(str(e))

# Página de teste para verificar se está rodando
@ui.page('/health')
def health():
    ui.label('Service is running on port ' + str(PORT))
    ui.label('Static login: ' + ('✓ Enabled' if os.path.exists(static_dir) else '✗ Disabled'))

# IMPORTANTE: Sempre executar
print(f"Starting NiceGUI on port {PORT}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

ui.run(
    port=PORT,
    host='0.0.0.0',
    title='GenAI4Data Security Manager',
    favicon='🔒',
    storage_secret=STORAGE_SECRET,
    reload=False
)
