"""
================================================================================
  GenAI4Data Security Manager
  Module: UI Theme & Navigation Framework
================================================================================
  Version:      2.1.0
  Release Date: 2024-12-05
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  HUD/Sci-Fi themed UI framework with multi-language support, providing
  consistent page layout, navigation menu, and language selector across
  all application pages.
================================================================================
"""

from nicegui import ui, app
from contextlib import contextmanager
from typing import Optional

# ============================================
# LANGUAGE HELPER FUNCTIONS  # <- NOVO
# ============================================

def get_current_language() -> str:
    """
    Get current language from session storage
    Returns: Language code ('pt', 'en', 'es')
    """
    return app.storage.user.get('language', 'en')


def get_text(key: str, **kwargs) -> str:
    """
    Get translated text for current language
    
    Args:
        key: Translation key
        **kwargs: Optional formatting parameters
    
    Returns:
        Translated text
    
    Example:
        >>> get_text('home_welcome')
        'Bem-vindo de volta,'
        >>> get_text('header_user_role', role='ADMIN')
        'Sua Função: ADMIN'
    """
    try:
        from translations import get_text as _get_text
        lang = get_current_language()
        return _get_text(lang, key, **kwargs)
    except ImportError:
        # Fallback se translations.py não existir
        return key
    except Exception as e:
        print(f"Error getting translation for '{key}': {e}")
        return key


# ============================================
# THEME FUNCTIONS
# ============================================

def _apply_global_theme():
    """Aplica estilos globais do tema HUD/Sci-Fi + Language Selector"""
    ui.add_head_html('''
        <style>
            :root {
                --hud-color: #00f3ff;
                --bg-primary: #0a0f1a;
                --bg-secondary: #050810;
                --text-main: #ffffff;
                --text-dim: #94a3b8;
            }

            /* Fundo Global */
            body, .nicegui-content {
                background: linear-gradient(135deg, #0a0f1a 0%, #050810 50%, #0a0f1a 100%) !important;
                color: var(--text-main) !important;
            }

            /* Grid sutil de fundo */
            body::before {
                content: '';
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background-image: 
                    linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
                background-size: 50px 50px;
                opacity: 0.5;
                pointer-events: none;
                z-index: 0;
            }

            /* Header Customizado */
            .q-header {
                background: linear-gradient(90deg, #0a0f1a 0%, #1a2535 100%) !important;
                border-bottom: 1px solid rgba(0, 243, 255, 0.3) !important;
                box-shadow: 0 4px 20px rgba(0, 243, 255, 0.15) !important;
            }

            /* Drawer/Sidebar */
            .q-drawer {
                background: rgba(10, 15, 26, 0.95) !important;
                border-right: 1px solid rgba(0, 243, 255, 0.3) !important;
                backdrop-filter: blur(10px) !important;
            }

            /* Cards */
            .q-card {
                background: rgba(15, 25, 35, 0.9) !important;
                border: 1px solid rgba(0, 243, 255, 0.2) !important;
                box-shadow: 0 0 20px rgba(0, 243, 255, 0.1) !important;
            }

            /* Botões */
            .q-btn {
                border-radius: 6px !important;
                text-transform: none !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }

            .q-btn--flat {
                color: var(--hud-color) !important;
            }

            .q-btn--flat:hover {
                background: rgba(0, 243, 255, 0.1) !important;
            }

            /* Badges */
            .q-badge {
                border: 1px solid currentColor !important;
                font-weight: 700 !important;
                padding: 4px 10px !important;
                border-radius: 4px !important;
            }

            /* Menu Items */
            .q-item {
                color: var(--text-dim) !important;
                border-radius: 8px !important;
                margin: 4px 8px !important;
                transition: all 0.3s ease !important;
            }

            .q-item:hover {
                background: rgba(0, 243, 255, 0.1) !important;
                color: var(--hud-color) !important;
                transform: translateX(4px) !important;
            }

            /* Links */
            a {
                color: var(--hud-color) !important;
                text-decoration: none !important;
                transition: all 0.3s ease !important;
            }

            a:hover {
                color: #ffffff !important;
                text-shadow: 0 0 10px rgba(0, 243, 255, 0.5) !important;
            }

            /* Footer */
            .q-footer {
                background: rgba(10, 15, 26, 0.98) !important;
                border-top: 1px solid rgba(0, 243, 255, 0.2) !important;
                backdrop-filter: blur(10px) !important;
            }

            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 243, 255, 0.2);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: var(--hud-color);
            }

            /* Labels/Text */
            .text-h6, .text-lg, .font-bold {
                color: var(--text-main) !important;
            }

            .text-gray-600, .text-gray-500 {
                color: var(--text-dim) !important;
            }

            /* Inputs e Fields */
            .q-field__control {
                background: rgba(15, 25, 35, 0.5) !important;
                border: 1px solid rgba(0, 243, 255, 0.2) !important;
                border-radius: 6px !important;
            }

            .q-field__control:hover {
                border-color: rgba(0, 243, 255, 0.5) !important;
            }

            /* Tabelas */
            .q-table {
                background: rgba(15, 25, 35, 0.8) !important;
            }

            .q-table thead {
                background: rgba(0, 243, 255, 0.05) !important;
            }

            .q-table tbody tr:hover {
                background: rgba(0, 243, 255, 0.08) !important;
            }

            /* ========================================
               LANGUAGE SELECTOR STYLES  <- NOVO
               ======================================== */
            
            .language-selector {
                display: flex;
                gap: 8px;
                align-items: center;
                background: rgba(5, 10, 15, 0.7);
                padding: 6px 10px;
                border-radius: 6px;
                border: 1px solid rgba(0, 243, 255, 0.2);
                backdrop-filter: blur(10px);
            }

            .flag-btn {
                width: 28px;
                height: 28px;
                cursor: pointer;
                border-radius: 4px;
                border: 2px solid transparent;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(255, 255, 255, 0.05);
                padding: 4px;
            }

            .flag-btn:hover {
                border-color: rgba(0, 243, 255, 0.5);
                transform: scale(1.1);
                box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
            }

            .flag-btn.active {
                border-color: var(--hud-color);
                background: rgba(0, 243, 255, 0.1);
                box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
            }

            .flag-btn svg {
                width: 100%;
                height: 100%;
                border-radius: 2px;
            }

            /* Animação de fade para troca de idioma */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-5px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .fade-in {
                animation: fadeIn 0.3s ease-out;
            }
        </style>
    ''')
    
    # JavaScript para gerenciar idioma  <- NOVO
    ui.add_head_html('''
        <script>
            // ========================================
            // LANGUAGE MANAGEMENT SYSTEM
            // ========================================
            
            /**
             * Change application language
             * @param {string} lang - Language code ('pt', 'en', 'es')
             */
            async function changeLanguage(lang) {
                console.log('Changing language to:', lang);
                
                try {
                    // Salvar no localStorage
                    localStorage.setItem('preferred_language', lang);
                    
                    // Atualizar no servidor via fetch
                    const response = await fetch('/api/set-language', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ language: lang })
                    });
                    
                    if (response.ok) {
                        console.log('Language saved to server:', lang);
                        
                        // Recarregar página para aplicar traduções
                        window.location.reload();
                    } else {
                        console.error('Failed to save language:', response.status);
                        // Ainda assim recarrega para tentar aplicar
                        window.location.reload();
                    }
                } catch (error) {
                    console.error('Error changing language:', error);
                    // Recarrega de qualquer forma
                    window.location.reload();
                }
            }
            
            /**
             * Initialize language system on page load
             */
            function initLanguageSystem() {
                // Carregar idioma salvo do localStorage
                const savedLang = localStorage.getItem('preferred_language');
                
                if (savedLang) {
                    console.log('Loaded language from localStorage:', savedLang);
                    
                    // Atualizar bandeiras ativas
                    updateFlagButtons(savedLang);
                }
            }
            
            /**
             * Update active flag button
             * @param {string} activeLang - Active language code
             */
            function updateFlagButtons(activeLang) {
                // Remove active de todos
                document.querySelectorAll('.flag-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Adiciona active no atual
                const activeBtn = document.getElementById('flag-' + activeLang);
                if (activeBtn) {
                    activeBtn.classList.add('active');
                }
            }
            
            // Inicializar quando DOM carregar
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initLanguageSystem);
            } else {
                initLanguageSystem();
            }
            
            console.log('Language system initialized');
        </script>
    ''')
    
    # Configurar cores do Quasar
    ui.colors(
        primary='#00f3ff',
        secondary='#5B9FED',
        accent='#00f3ff',
        dark='#0a0f1a',
        positive='#10b981',
        negative='#ef4444',
        info='#3b82f6',
        warning='#f59e0b'
    )
    
    # Ativar dark mode
    ui.dark_mode().enable()


def _create_language_selector():  # <- NOVO
    """
    Create language selector with flags
    Returns: NiceGUI element with flags
    """
    current_lang = get_current_language()
    
    with ui.element('div').classes('language-selector') as selector:
        # Flag Brasil 🇧🇷
        with ui.element('button').props('id=flag-pt onclick="changeLanguage(\'pt\')"').classes(
            f'flag-btn {"active" if current_lang == "pt" else ""}'
        ).tooltip('Português'):
            ui.html('''
                <svg viewBox="0 0 36 24" xmlns="http://www.w3.org/2000/svg">
                    <rect width="36" height="24" fill="#009739"/>
                    <path d="M18 3 L33 12 L18 21 L3 12 Z" fill="#FFDF00"/>
                    <circle cx="18" cy="12" r="4.5" fill="#002776"/>
                    <path d="M14 12 Q18 10, 22 12 Q18 14, 14 12" fill="#FFFFFF" opacity="0.9"/>
                </svg>
            ''')
        
        # Flag USA 🇺🇸
        with ui.element('button').props('id=flag-en onclick="changeLanguage(\'en\')"').classes(
            f'flag-btn {"active" if current_lang == "en" else ""}'
        ).tooltip('English'):
            ui.html('''
                <svg viewBox="0 0 36 24" xmlns="http://www.w3.org/2000/svg">
                    <rect width="36" height="24" fill="#FFFFFF"/>
                    <rect y="0" width="36" height="2" fill="#B22234"/>
                    <rect y="4" width="36" height="2" fill="#B22234"/>
                    <rect y="8" width="36" height="2" fill="#B22234"/>
                    <rect y="12" width="36" height="2" fill="#B22234"/>
                    <rect y="16" width="36" height="2" fill="#B22234"/>
                    <rect y="20" width="36" height="2" fill="#B22234"/>
                    <rect width="14" height="12" fill="#3C3B6E"/>
                    <circle cx="3" cy="2" r="0.8" fill="#FFFFFF"/>
                    <circle cx="7" cy="2" r="0.8" fill="#FFFFFF"/>
                    <circle cx="11" cy="2" r="0.8" fill="#FFFFFF"/>
                    <circle cx="3" cy="6" r="0.8" fill="#FFFFFF"/>
                    <circle cx="7" cy="6" r="0.8" fill="#FFFFFF"/>
                    <circle cx="11" cy="6" r="0.8" fill="#FFFFFF"/>
                    <circle cx="3" cy="10" r="0.8" fill="#FFFFFF"/>
                    <circle cx="7" cy="10" r="0.8" fill="#FFFFFF"/>
                    <circle cx="11" cy="10" r="0.8" fill="#FFFFFF"/>
                </svg>
            ''')
        
        # Flag España 🇪🇸
        with ui.element('button').props('id=flag-es onclick="changeLanguage(\'es\')"').classes(
            f'flag-btn {"active" if current_lang == "es" else ""}'
        ).tooltip('Español'):
            ui.html('''
                <svg viewBox="0 0 36 24" xmlns="http://www.w3.org/2000/svg">
                    <rect width="36" height="24" fill="#AA151B"/>
                    <rect y="6" width="36" height="12" fill="#F1BF00"/>
                </svg>
            ''')
    
    return selector


@contextmanager
def frame(navtitle: str):
    """
    Create a page frame with navigation - HUD/Sci-Fi Theme + Multi-Language
    
    Args:
        navtitle: Page title to display in header
    
    Yields:
        Main content column
    """
    
    # Aplicar tema global
    _apply_global_theme()
    
    # Get user info
    user_info = app.storage.user.get('user_info', {})
    
    # Header com tema tech
    with ui.header().style(
        'background: linear-gradient(90deg, #0a0f1a 0%, #1a2535 100%); '
        'border-bottom: 1px solid rgba(0, 243, 255, 0.3); '
        'box-shadow: 0 4px 20px rgba(0, 243, 255, 0.15);'
    ):
        with ui.row().classes('w-full items-center px-4 gap-4'):
            # Título principal
            ui.label(get_text('app_name')).classes('font-bold text-lg').style(  # <- TRADUZIDO
                'color: #00f3ff; text-shadow: 0 0 10px rgba(0, 243, 255, 0.3);'
            )
            
            # Subtítulo da página
            ui.label(f'| {navtitle}').classes('text-white')
            
            ui.space()
            
            # Language Selector  # <- NOVO
            _create_language_selector()
            
            # Botão de logout
            if user_info:
                ui.button(
                    get_text('header_logout').upper(),  # <- TRADUZIDO
                    icon='logout',
                    on_click=lambda: ui.run_javascript('window.location.href = "/login"')
                ).props('flat').style(
                    'color: #ef4444; font-weight: 700;'
                ).classes('hover:bg-red-900/20')
    
    # Left drawer SEMPRE ABERTA
    left_drawer = ui.left_drawer(value=True, fixed=True).style(
        'background: rgba(10, 15, 26, 0.95); '
        'border-right: 1px solid rgba(0, 243, 255, 0.3); '
        'backdrop-filter: blur(10px);'
    )
    
    with left_drawer:
        # Título da navegação
        ui.label('Navigation').classes('text-h6 q-mt-md q-mb-md q-ml-md').style(
            'color: #00f3ff; '
            'font-weight: 800; '
            'letter-spacing: 0.05em; '
            'font-size: 0.875rem; '
            'text-transform: uppercase;'
        )
        
        # Separador decorativo
        ui.html('<div style="width: 80%; height: 1px; background: rgba(0, 243, 255, 0.2); margin: 8px auto 16px;"></div>')
        
        # Menu items (será traduzido em menu.py)
        try:
            from menu import menu
            menu()
        except Exception as e:
            print(f"Error loading menu: {e}")
            # Fallback menu
            with ui.column().classes('gap-2 p-2'):
                ui.link(f'🏠 {get_text("nav_home")}', '/').classes('text-lg').style(  # <- TRADUZIDO
                    'color: #94a3b8; '
                    'padding: 12px 16px; '
                    'border-radius: 8px; '
                    'display: block;'
                )
    
    # Main content area
    with ui.column().classes('w-full').style('position: relative; z-index: 1;') as main_content:
        yield main_content
    
    # Footer com tema tech
    with ui.footer().style(
        'background: rgba(10, 15, 26, 0.98); '
        'border-top: 1px solid rgba(0, 243, 255, 0.2); '
        'backdrop-filter: blur(10px);'
    ):
        with ui.row().classes('w-full justify-between items-center px-6 py-3'):
            # Copyright
            ui.label(
                f'{get_text("footer_powered")} Sys Manager | Partner Google Cloud - Concept Prototype'  # <- TRADUZIDO
            ).classes('text-sm').style(
                'color: #64748b; '
                'font-family: "JetBrains Mono", monospace; '
                'font-size: 0.75rem;'
            )
            
            # Session info
            if user_info:
                role = user_info.get('role', 'VIEWER')
                email = user_info.get('email', '')
                session_info = f"{get_text('footer_session').upper()}: {role} | {email}"  # <- TRADUZIDO
                
                ui.label(session_info).classes('text-sm').style(
                    'color: #64748b; '
                    'font-family: "JetBrains Mono", monospace; '
                    'font-size: 0.75rem;'
                )
