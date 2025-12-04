"""
Theme template for consistent page layout - HUD/Sci-Fi Style
"""
from nicegui import ui, app
from contextlib import contextmanager

# Aplicar CSS global e configurações de tema
def _apply_global_theme():
    """Aplica estilos globais do tema HUD/Sci-Fi"""
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
        </style>
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


@contextmanager
def frame(navtitle: str):
    """Create a page frame with navigation - HUD/Sci-Fi Theme"""
    
    # Aplicar tema global
    _apply_global_theme()
    
    # Header com tema tech
    with ui.header().style(
        'background: linear-gradient(90deg, #0a0f1a 0%, #1a2535 100%); '
        'border-bottom: 1px solid rgba(0, 243, 255, 0.3); '
        'box-shadow: 0 4px 20px rgba(0, 243, 255, 0.15);'
    ):
        with ui.row().classes('w-full items-center px-4'):
            # Menu button
            menu_button = ui.button(icon='menu').props('flat').style(
                'color: #00f3ff;'
            )
            
            # Título principal
            ui.label('GenAI4Data - Security Manager').classes('font-bold text-lg').style(
                'color: #00f3ff; text-shadow: 0 0 10px rgba(0, 243, 255, 0.3);'
            )
            
            # Subtítulo da página
            ui.label(f'| {navtitle}').classes('text-white')
            
            ui.space()
            
            # User info and logout
            user_info = app.storage.user.get('user_info', {})
            if user_info:
                # Label "Your Role"
                ui.label("Your Role:").classes('text-sm').style('color: #94a3b8;')
                
                # Role badge com cores customizadas
                role = user_info.get('role', 'VIEWER')
                role_colors = {
                    'OWNER': {'bg': 'rgba(239, 68, 68, 0.2)', 'border': '#ef4444', 'text': '#fca5a5'},
                    'ADMIN': {'bg': 'rgba(249, 115, 22, 0.2)', 'border': '#f97316', 'text': '#fdba74'},
                    'EDITOR': {'bg': 'rgba(59, 130, 246, 0.2)', 'border': '#3b82f6', 'text': '#93c5fd'},
                    'VIEWER': {'bg': 'rgba(16, 185, 129, 0.2)', 'border': '#10b981', 'text': '#6ee7b7'}
                }
                colors = role_colors.get(role, {'bg': 'rgba(100, 116, 139, 0.2)', 'border': '#64748b', 'text': '#94a3b8'})
                
                ui.badge(role).style(
                    f'background: {colors["bg"]}; '
                    f'color: {colors["text"]}; '
                    f'border: 1px solid {colors["border"]}; '
                    f'padding: 4px 12px; '
                    f'border-radius: 4px; '
                    f'font-weight: 700; '
                    f'font-size: 0.75rem; '
                    f'letter-spacing: 0.05em;'
                )
                
                # Logout button
                ui.button('LOGOUT', 
                         icon='logout',
                         on_click=lambda: ui.run_javascript('window.location.href = "/login"')).props(
                    'flat'
                ).style(
                    'color: #ef4444; '
                    'font-weight: 700; '
                    'margin-left: 16px;'
                ).classes('hover:bg-red-900/20')
    
    # Left drawer com tema tech
    left_drawer = ui.left_drawer(value=False, fixed=False).style(
        'background: rgba(10, 15, 26, 0.95); '
        'border-right: 1px solid rgba(0, 243, 255, 0.3); '
        'backdrop-filter: blur(10px);'
    )
    menu_button.on_click(left_drawer.toggle)
    
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
        
        # Menu items
        try:
            from menu import menu
            menu()
        except:
            # Fallback menu
            with ui.column().classes('gap-2 p-2'):
                ui.link('🏠 Home', '/').classes('text-lg').style(
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
            ui.label('Copyright 2024 CCW Latam - Concept Prototype').classes('text-sm').style(
                'color: #64748b; '
                'font-family: "JetBrains Mono", monospace; '
                'font-size: 0.75rem;'
            )
            
            # Session info
            if user_info:
                session_info = f"SESSION: {user_info.get('role', 'VIEWER')} | {user_info.get('email', '')}"
                ui.label(session_info).classes('text-sm').style(
                    'color: #64748b; '
                    'font-family: "JetBrains Mono", monospace; '
                    'font-size: 0.75rem;'
                )
