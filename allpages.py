"""
All pages registration - Simplified but functional
"""
from nicegui import ui

def create():
    """Register all application pages with error handling"""
    
    # RLS Pages
    @ui.page('/rls')
    def rls_page():
        from theme import frame
        with frame('Row Level Security'):
            ui.label('RLS Management').classes('text-2xl font-bold')
            ui.label('Select an option from the menu').classes('text-gray-600')
    
    # CLS Pages  
    @ui.page('/cls')
    def cls_page():
        from theme import frame
        with frame('Column Level Security'):
            ui.label('CLS Management').classes('text-2xl font-bold')
            ui.label('Select an option from the menu').classes('text-gray-600')
    
    # Control Access (já criamos separadamente)
    try:
        from pages import control_access
        control_access.create()
    except:
        @ui.page('/control_access')
        def control_access_fallback():
            ui.label('Control Access - Loading Error')
    
    # Audit Logs
    @ui.page('/audit_logs')
    def audit_logs_page():
        from theme import frame
        with frame('Audit Logs'):
            ui.label('Audit Logs').classes('text-2xl font-bold')
            ui.label('Feature in development').classes('text-gray-600')

    print("✓ Basic pages registered")
