import os
from nicegui import ui, app
from pages.login_page import create_login_page
from theme import frame
from home import content as home_content
import allpages

# Configuração de porta
PORT = int(os.environ.get('PORT', 8080))
STORAGE_SECRET = os.environ.get('SESSION_SECRET', 'default-secret-key')

# Configurar storage
app.storage.secret = STORAGE_SECRET

# Criar páginas de login
create_login_page()

# Criar todas as outras páginas
allpages.create()

# Página inicial
@ui.page('/')
def home():
    if not app.storage.user.get('authenticated', False):
        ui.run_javascript('window.location.href = "/login"')
        return
    
    with frame('Home'):
        home_content()

# IMPORTANTE: Sempre executar, sem condição if __name__
print(f"Starting NiceGUI on port {PORT}")
ui.run(
    port=PORT,
    host='0.0.0.0',
    title='GenAI4Data Security Manager',
    favicon='🔒',
    storage_secret=STORAGE_SECRET,
    reload=False  # Importante para produção
)
