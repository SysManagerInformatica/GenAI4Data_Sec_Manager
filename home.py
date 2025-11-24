"""
Home page content
"""
from nicegui import ui, app

def content():
    """Home page content"""
    user_info = app.storage.user.get('user_info', {})
    
    # Card de boas-vindas centralizado
    with ui.row().classes('w-full justify-center mt-8'):
        with ui.card().classes('p-8 bg-gradient-to-r from-blue-50 to-indigo-50'):
            with ui.row().classes('items-center gap-4'):
                # Avatar circle
                with ui.avatar(size='xl', color='green'):
                    ui.label(user_info.get('name', 'User')[0].upper()).classes('text-white text-2xl')
                
                # Welcome text
                with ui.column().classes('gap-0'):
                    ui.label(f"Welcome back, {user_info.get('name', 'User')}!").classes('text-2xl font-bold')
                    ui.label(user_info.get('email', '')).classes('text-gray-600')
                    ui.label(f"Department: {user_info.get('department', 'Not set')}").classes('text-sm text-gray-500')
                    ui.label(f"Company: {user_info.get('company', 'Not set')}").classes('text-sm text-gray-500')
    
    # View permissions expansion
    with ui.row().classes('w-full justify-center mt-6'):
        with ui.expansion('View My Permissions', icon='security').classes('w-full max-w-2xl'):
            role = user_info.get('role', 'VIEWER')
            
            with ui.column().classes('gap-2'):
                ui.label(f"Current Role: {role}").classes('font-bold')
                ui.separator()
                
                if role == 'OWNER':
                    ui.label('✅ Full System Access').classes('text-green-600')
                    ui.label('• Create and manage RLS policies')
                    ui.label('• Create and manage CLS policies')
                    ui.label('• Manage users and permissions')
                    ui.label('• View audit logs')
                    ui.label('• Configure system settings')
                elif role == 'ADMIN':
                    ui.label('✅ Administrative Access').classes('text-orange-600')
                    ui.label('• Create and manage RLS policies')
                    ui.label('• Create and manage CLS policies')
                    ui.label('• View audit logs')
                    ui.label('• Cannot manage users')
                elif role == 'EDITOR':
                    ui.label('✅ Editor Access').classes('text-blue-600')
                    ui.label('• Create RLS policies')
                    ui.label('• Edit own policies')
                    ui.label('• View audit logs (own actions)')
                else:
                    ui.label('✅ Viewer Access').classes('text-gray-600')
                    ui.label('• View RLS policies')
                    ui.label('• View CLS policies')
                    ui.label('• Cannot make changes')
    
    # Main content
    with ui.column().classes('w-full items-center mt-8'):
        ui.label('Welcome to GenAI4Data Security Manager').classes('text-3xl font-bold text-center text-blue-600')
        ui.label('A tool to simplify Row-Level Security (RLS) creation in BigQuery.').classes('text-xl text-center text-gray-600 mt-4')
