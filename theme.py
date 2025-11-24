"""
Theme template for consistent page layout
"""
from nicegui import ui, app
from menu import menu

def frame(navtitle: str):
    """
    Create a page frame with navigation
    """
    ui.colors(primary='#4285F4')
    
    with ui.header():
        with ui.row().classes('w-full items-center'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label('GenAI4Data - Security Manager').classes('font-bold')
            ui.label(f'| {navtitle}').classes('text-white')
            
            ui.space()
            
            user_info = app.storage.user.get('user_info', {})
            if user_info:
                ui.label(f"Your Role:").classes('text-white')
                role_color = {
                    'OWNER': 'red',
                    'ADMIN': 'orange', 
                    'EDITOR': 'blue',
                    'VIEWER': 'green'
                }.get(user_info.get('role', 'VIEWER'), 'gray')
                
                ui.badge(user_info.get('role', 'VIEWER'), color=role_color)
                
                ui.button('LOGOUT', 
                         on_click=lambda: ui.run_javascript('window.location.href = "/login"'),
                         color='red').classes('ml-2')
    
    # Drawer lateral com menu
    left_drawer = ui.left_drawer(value=False, fixed=False).classes('bg-gray-50')
    with left_drawer:
        ui.label('Navigation').classes('text-h6 q-mt-md q-mb-md')
        menu()
    
    # Footer
    with ui.footer().classes('bg-gray-100'):
        with ui.row().classes('w-full justify-between items-center'):
            ui.label('Copyright 2024 CCW Latam - Concept Prototype').classes('text-gray-600')
            
            if user_info:
                session_info = f"Session: {user_info.get('role', 'VIEWER')} | {user_info.get('email', '')}"
                ui.label(session_info).classes('text-gray-600')
    
    # Retornar um contexto manager válido
    return ui.column().classes('w-full')
