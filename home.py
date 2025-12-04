"""
Home page content - Enterprise Data Security Platform
"""
from nicegui import ui, app

def content():
    """Home page content"""
    user_info = app.storage.user.get('user_info', {})
    
    with ui.column().classes('w-full p-6 gap-6').style('max-width: 1400px; margin: 0 auto;'):
        
        # Card de boas-vindas COMPACTO e elegante
        with ui.card().classes('w-full').style(
            'background: linear-gradient(135deg, rgba(15, 25, 35, 0.95) 0%, rgba(10, 20, 30, 0.9) 100%); '
            'border: 1px solid rgba(0, 243, 255, 0.25); '
            'box-shadow: 0 0 25px rgba(0, 243, 255, 0.1); '
            'padding: 1.5rem 2rem;'
        ):
            with ui.row().classes('items-center gap-4 w-full'):
                # Avatar compacto
                with ui.avatar(size='lg', color='green').style(
                    'width: 60px; '
                    'height: 60px; '
                    'font-size: 1.5rem; '
                    'box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);'
                ):
                    ui.label(user_info.get('name', 'User')[0].upper()).classes('text-white text-2xl')
                
                # Informações do usuário - layout horizontal compacto
                with ui.column().classes('gap-1 flex-grow'):
                    ui.label(f'Welcome back, {user_info.get("name", "User")}!').classes('text-xl font-bold').style(
                        'color: #ffffff;'
                    )
                    ui.label(user_info.get('email', '')).classes('text-sm').style(
                        'color: #94a3b8;'
                    )
                
                # Badges à direita
                with ui.row().classes('gap-2 items-center'):
                    if user_info.get('department') and user_info.get('department') != 'Not set':
                        ui.label(f'📁 {user_info.get("department")}').classes('text-xs').style(
                            'color: #94a3b8; '
                            'background: rgba(0, 243, 255, 0.08); '
                            'padding: 6px 14px; '
                            'border-radius: 6px; '
                            'border: 1px solid rgba(0, 243, 255, 0.15); '
                            'white-space: nowrap;'
                        )
                    if user_info.get('company') and user_info.get('company') != 'Not set':
                        ui.label(f'🏢 {user_info.get("company")}').classes('text-xs').style(
                            'color: #94a3b8; '
                            'background: rgba(0, 243, 255, 0.08); '
                            'padding: 6px 14px; '
                            'border-radius: 6px; '
                            'border: 1px solid rgba(0, 243, 255, 0.15); '
                            'white-space: nowrap;'
                        )
        
        # Separador decorativo
        ui.html('<div style="width: 100%; height: 1px; background: linear-gradient(90deg, transparent, rgba(0, 243, 255, 0.3), transparent); margin: 1.5rem 0;"></div>')
        
        # Seção principal - CENTRALIZADO
        with ui.column().classes('w-full gap-5').style('align-items: center; text-align: center;'):
            
            # Título principal - ALINHADO AO CENTRO
            ui.label('Enterprise Data Security Platform').classes('text-4xl font-bold').style(
                'color: #00f3ff; '
                'text-shadow: 0 0 20px rgba(0, 243, 255, 0.3); '
                'letter-spacing: -0.02em; '
                'text-align: center;'
            )
            
            # Descrição - ALINHADO AO CENTRO
            ui.label(
                'Advanced Row-Level and Column-Level Security management for BigQuery. '
                'Protect your data with enterprise-grade access controls, granular permissions, '
                'data masking, IAM policies, and comprehensive audit trails.'
            ).classes('text-base leading-relaxed').style(
                'color: #94a3b8; '
                'line-height: 1.7; '
                'max-width: 900px; '
                'text-align: center;'
            )
            
            # Grid de Features - 5 CARDS (3 na primeira linha, 2 na segunda)
            with ui.column().classes('gap-4 mt-6 w-full').style('max-width: 1200px;'):
                
                # Primeira linha - 3 cards
                with ui.row().classes('gap-4 justify-center flex-wrap w-full'):
                    
                    # Card 1 - RLS
                    with ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s ease;'
                    ).classes('hover:shadow-lg'):
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('shield', size='2.5rem').style('color: #00f3ff;')
                            ui.label('Row-Level Security').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Control data access at the row level based on user attributes and policies.').classes('text-xs').style(
                                'color: #94a3b8; '
                                'line-height: 1.5;'
                            )
                    
                    # Card 2 - CLS
                    with ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s ease;'
                    ).classes('hover:shadow-lg'):
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('visibility_off', size='2.5rem').style('color: #00f3ff;')
                            ui.label('Column-Level Security').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Restrict sensitive columns and control field-level access permissions.').classes('text-xs').style(
                                'color: #94a3b8; '
                                'line-height: 1.5;'
                            )
                    
                    # Card 3 - Data Masking
                    with ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s ease;'
                    ).classes('hover:shadow-lg'):
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('masks', size='2.5rem').style('color: #00f3ff;')
                            ui.label('Data Masking').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Apply dynamic data masking to protect sensitive information from unauthorized users.').classes('text-xs').style(
                                'color: #94a3b8; '
                                'line-height: 1.5;'
                            )
                
                # Segunda linha - 2 cards centralizados
                with ui.row().classes('gap-4 justify-center flex-wrap w-full mt-2'):
                    
                    # Card 4 - IAM Policy Control
                    with ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s ease;'
                    ).classes('hover:shadow-lg'):
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('admin_panel_settings', size='2.5rem').style('color: #00f3ff;')
                            ui.label('IAM Policy Control').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Manage Identity and Access Management policies for datasets and resources.').classes('text-xs').style(
                                'color: #94a3b8; '
                                'line-height: 1.5;'
                            )
                    
                    # Card 5 - Audit & Compliance
                    with ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s ease;'
                    ).classes('hover:shadow-lg'):
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('history', size='2.5rem').style('color: #00f3ff;')
                            ui.label('Audit & Compliance').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Track all security changes with comprehensive audit logs and compliance reports.').classes('text-xs').style(
                                'color: #94a3b8; '
                                'line-height: 1.5;'
                            )
