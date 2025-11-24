"""
Theme template for consistent page layout
"""
from nicegui import ui, app
from contextlib import contextmanager

@contextmanager
def frame(navtitle: str):
    """Create a page frame with navigation"""
    ui.colors(primary='#4285F4')
    
    # Header
    with ui.header():
        with ui.row().classes('w-full items-center'):
            # Menu button and title
            menu_button = ui.button(icon='menu').props('flat color=white')
            ui.label('GenAI4Data - Security Manager').classes('font-bold')
            ui.label(f'| {navtitle}').classes('text-white')
            
            ui.space()
            
            # User info and logout
            user_info = app.storage.user.get('user_info', {})
            if user_info:
                ui.label("Your Role:").classes('text-white')
                role = user_info.get('role', 'VIEWER')
                role_color = {
                    'OWNER': 'red',
                    'ADMIN': 'orange',
                    'EDITOR': 'blue',
                    'VIEWER': 'green'
                }.get(role, 'gray')
                ui.badge(role, color=role_color)
                ui.button('LOGOUT', 
                         on_click=lambda: ui.run_javascript('window.location.href = "/login"'),
                         color='red').classes('ml-2')
    
    # Left drawer with menu
    left_drawer = ui.left_drawer(value=False, fixed=False).classes('bg-gray-50')
    menu_button.on_click(left_drawer.toggle)
    
    with left_drawer:
        ui.label('Navigation').classes('text-h6 q-mt-md q-mb-md')
        try:
            from menu import menu
            menu()
        except:
            ui.link('Home', '/').classes('text-lg')
    
    # Main content area
    with ui.column().classes('w-full') as main_content:
        yield main_content
    
    # Footer
    with ui.footer().classes('bg-gray-100'):
        with ui.row().classes('w-full justify-between items-center'):
            ui.label('Copyright 2024 CCW Latam - Concept Prototype').classes('text-gray-600')
            if user_info:
                session_info = f"Session: {user_info.get('role', 'VIEWER')} | {user_info.get('email', '')}"
                ui.label(session_info).classes('text-gray-600')
