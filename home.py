"""
Home page content - Enterprise Data Security Platform
"""
from nicegui import ui, app

def content():
    """Home page content"""
    user_info = app.storage.user.get('user_info', {})
    
    with ui.column().classes('w-full p-8 gap-8'):
        # Card de boas-vindas do usuário
        with ui.card().classes('w-full max-w-4xl mx-auto').style(
            'background: rgba(15, 25, 35, 0.9); '
            'border: 1px solid rgba(0, 243, 255, 0.3); '
            'box-shadow: 0 0 30px rgba(0, 243, 255, 0.15);'
        ):
            with ui.row().classes('items-center gap-6 p-8'):
                # Avatar do usuário
                with ui.avatar(size='xl', color='green').style(
                    'width: 80px; '
                    'height: 80px; '
                    'font-size: 2rem; '
                    'box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);'
                ):
                    ui.label(user_info.get('name', 'User')[0].upper()).classes('text-white text-3xl')
                
                with ui.column().classes('gap-2'):
                    ui.label(f'Welcome back, {user_info.get("name", "User")}!').classes('text-3xl font-bold').style(
                        'color: #ffffff;'
                    )
                    ui.label(user_info.get('email', '')).classes('text-base').style(
                        'color: #94a3b8;'
                    )
                    with ui.row().classes('gap-4 mt-2'):
                        if user_info.get('department') and user_info.get('department') != 'Not set':
                            ui.label(f'📁 {user_info.get("department")}').classes('text-sm').style(
                                'color: #64748b; '
                                'background: rgba(0, 243, 255, 0.1); '
                                'padding: 4px 12px; '
                                'border-radius: 6px; '
                                'border: 1px solid rgba(0, 243, 255, 0.2);'
                            )
                        if user_info.get('company') and user_info.get('company') != 'Not set':
                            ui.label(f'🏢 {user_info.get("company")}').classes('text-sm').style(
                                'color: #64748b; '
                                'background: rgba(0, 243, 255, 0.1); '
                                'padding: 4px 12px; '
                                'border-radius: 6px; '
                                'border: 1px solid rgba(0, 243, 255, 0.2);'
                            )
        
        # Separador com efeito
        ui.html('<div style="width: 100%; height: 1px; background: linear-gradient(90deg, transparent, rgba(0, 243, 255, 0.3), transparent); margin: 2rem 0;"></div>')
        
        # Título e descrição principal
        with ui.column().classes('w-full max-w-5xl mx-auto gap-6 text-center'):
            # Título principal
            ui.label('Enterprise Data Security Platform').classes('text-4xl font-bold').style(
                'color: #00f3ff; '
                'text-shadow: 0 0 20px rgba(0, 243, 255, 0.3); '
                'letter-spacing: -0.02em;'
            )
            
            # Descrição
            ui.label(
                'Advanced Row-Level and Column-Level Security management for BigQuery. '
                'Protect your data with enterprise-grade access controls, granular permissions, '
                'and comprehensive audit trails.'
            ).classes('text-lg leading-relaxed max-w-3xl mx-auto').style(
                'color: #94a3b8; '
                'line-height: 1.8;'
            )
            
            # Features em cards
            with ui.row().classes('gap-6 mt-8 justify-center flex-wrap w-full'):
                # Card 1 - RLS
                with ui.card().classes('w-72 p-6').style(
                    'background: rgba(15, 25, 35, 0.8); '
                    'border: 1px solid rgba(0, 243, 255, 0.2); '
                    'transition: all 0.3s ease;'
                ).on('mouseenter', lambda: None).on('mouseleave', lambda: None):
                    with ui.column().classes('items-center gap-4'):
                        ui.icon('shield', size='3rem').style('color: #00f3ff;')
                        ui.label('Row-Level Security').classes('text-xl font-bold text-center').style('color: #ffffff;')
                        ui.label('Control data access at the row level based on user attributes and policies.').classes('text-sm text-center').style('color: #94a3b8; line-height: 1.6;')
                
                # Card 2 - CLS
                with ui.card().classes('w-72 p-6').style(
                    'background: rgba(15, 25, 35, 0.8); '
                    'border: 1px solid rgba(0, 243, 255, 0.2); '
                    'transition: all 0.3s ease;'
                ):
                    with ui.column().classes('items-center gap-4'):
                        ui.icon('visibility_off', size='3rem').style('color: #00f3ff;')
                        ui.label('Column-Level Security').classes('text-xl font-bold text-center').style('color: #ffffff;')
                        ui.label('Restrict sensitive columns and apply dynamic data masking policies.').classes('text-sm text-center').style('color: #94a3b8; line-height: 1.6;')
                
                # Card 3 - Audit
                with ui.card().classes('w-72 p-6').style(
                    'background: rgba(15, 25, 35, 0.8); '
                    'border: 1px solid rgba(0, 243, 255, 0.2); '
                    'transition: all 0.3s ease;'
                ):
                    with ui.column().classes('items-center gap-4'):
                        ui.icon('history', size='3rem').style('color: #00f3ff;')
                        ui.label('Audit & Compliance').classes('text-xl font-bold text-center').style('color: #ffffff;')
                        ui.label('Track all security changes with comprehensive audit logs and reports.').classes('text-sm text-center').style('color: #94a3b8; line-height: 1.6;')
            
            # Call to action (opcional)
            with ui.row().classes('gap-4 mt-8 justify-center'):
                ui.button('Manage RLS Policies', icon='shield', on_click=lambda: ui.navigate.to('/rls')).props('size=lg').style(
                    'background: rgba(0, 243, 255, 0.2); '
                    'color: #00f3ff; '
                    'border: 1px solid rgba(0, 243, 255, 0.4); '
                    'padding: 12px 32px; '
                    'font-weight: 700; '
                    'text-transform: none;'
                )
                ui.button('Manage CLS Policies', icon='visibility_off', on_click=lambda: ui.navigate.to('/cls')).props('size=lg').style(
                    'background: rgba(0, 243, 255, 0.2); '
                    'color: #00f3ff; '
                    'border: 1px solid rgba(0, 243, 255, 0.4); '
                    'padding: 12px 32px; '
                    'font-weight: 700; '
                    'text-transform: none;'
                )
