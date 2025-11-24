import os
import sys
from nicegui import ui, app

# Configuração de porta
PORT = int(os.environ.get('PORT', 8080))
STORAGE_SECRET = os.environ.get('SESSION_SECRET', 'default-secret-key')

# Configurar storage
app.storage.secret = STORAGE_SECRET

# Tentar importar login page
try:
    from pages.login_page import create_login_page
    create_login_page()
    print("✓ Login pages created successfully")
except Exception as e:
    print(f"✗ Error creating login pages: {e}")
    # Login é crítico, não podemos continuar sem ele
    
    @ui.page('/login')
    def emergency_login():
        ui.label('System Error - Could not load login page').classes('text-red-600')
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
