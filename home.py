"""
Home page content - Enterprise Data Security Platform
"""
from nicegui import ui, app

def content():
    """Home page content"""
    user_info = app.storage.user.get('user_info', {})
    
    with ui.column().classes('w-full p-6 gap-6').style('max-width: 1400px; margin: 0 auto;'):
        
        # Card de boas-vindas SUPER COMPACTO e centralizado
        with ui.card().classes('w-full').style(
            'background: linear-gradient(135deg, rgba(15, 25, 35, 0.95) 0%, rgba(10, 20, 30, 0.9) 100%); '
            'border: 1px solid rgba(0, 243, 255, 0.25); '
            'box-shadow: 0 0 25px rgba(0, 243, 255, 0.1); '
            'padding: 1rem 1.5rem;'  # ← PADDING REDUZIDO
        ):
            with ui.row().classes('items-center justify-center gap-3 w-full'):  # ← CENTRALIZADO
                # Avatar compacto
                with ui.avatar(size='md', color='green').style(
                    'width: 50px; '  # ← MENOR
                    'height: 50px; '
                    'font-size: 1.25rem; '
                    'box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);'
                ):
                    ui.label(user_info.get('name', 'User')[0].upper()).classes('text-white text-xl')
                
                # Informações do usuário - CENTRALIZADO
                with ui.column().classes('gap-0').style('text-align: center;'):
                    ui.label(f'Welcome back, {user_info.get("name", "User")}!').classes('text-lg font-bold').style(
                        'color: #ffffff;'
                    )
                    ui.label(user_info.get('email', '')).classes('text-xs').style(
                        'color: #94a3b8;'
                    )
                
                # Badges compactos (se houver)
                if user_info.get('department') and user_info.get('department') != 'Not set':
                    ui.label(f'📁 {user_info.get("department")}').classes('text-xs').style(
                        'color: #94a3b8; '
                        'background: rgba(0, 243, 255, 0.08); '
                        'padding: 4px 10px; '
                        'border-radius: 4px; '
                        'border: 1px solid rgba(0, 243, 255, 0.15); '
                        'white-space: nowrap;'
                    )
        
        # Separador decorativo
        ui.html('<div style="width: 100%; height: 1px; background: linear-gradient(90deg, transparent, rgba(0, 243, 255, 0.3), transparent); margin: 1rem 0;"></div>')
        
        # Seção principal - CENTRALIZADO
        with ui.column().classes('w-full gap-4').style('align-items: center; text-align: center;'):
            
            # Título principal
            ui.label('Enterprise Data Security Platform').classes('text-4xl font-bold').style(
                'color: #00f3ff; '
                'text-shadow: 0 0 20px rgba(0, 243, 255, 0.3); '
                'letter-spacing: -0.02em; '
                'text-align: center;'
            )
            
            # Descrição
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
            
            # Grid de Features - 5 CARDS INTERATIVOS
            with ui.column().classes('gap-4 mt-6 w-full').style('max-width: 1200px;'):
                
                # Primeira linha - 3 cards
                with ui.row().classes('gap-4 justify-center flex-wrap w-full'):
                    
                    # Card 1 - RLS (com hover effect)
                    card_rls = ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); '
                        'cursor: pointer;'
                    ).classes('hover-card')
                    
                    # JavaScript para hover effect
                    card_rls.on('mouseenter', lambda: None)
                    card_rls.on('mouseleave', lambda: None)
                    
                    with card_rls:
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('shield', size='2.5rem').style('color: #00f3ff; transition: all 0.3s ease;').classes('card-icon')
                            ui.label('Row-Level Security').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Control data access at the row level based on user attributes and policies.').classes('text-xs').style(
                                'color: #94a3b8; line-height: 1.5;'
                            )
                    
                    # Card 2 - CLS
                    card_cls = ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); '
                        'cursor: pointer;'
                    )
                    
                    with card_cls:
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('visibility_off', size='2.5rem').style('color: #00f3ff; transition: all 0.3s ease;')
                            ui.label('Column-Level Security').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Restrict sensitive columns and control field-level access permissions.').classes('text-xs').style(
                                'color: #94a3b8; line-height: 1.5;'
                            )
                    
                    # Card 3 - Data Masking
                    card_masking = ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); '
                        'cursor: pointer;'
                    )
                    
                    with card_masking:
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('masks', size='2.5rem').style('color: #00f3ff; transition: all 0.3s ease;')
                            ui.label('Data Masking').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Apply dynamic data masking to protect sensitive information from unauthorized users.').classes('text-xs').style(
                                'color: #94a3b8; line-height: 1.5;'
                            )
                
                # Segunda linha - 2 cards centralizados
                with ui.row().classes('gap-4 justify-center flex-wrap w-full mt-2'):
                    
                    # Card 4 - IAM Policy Control
                    card_iam = ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); '
                        'cursor: pointer;'
                    )
                    
                    with card_iam:
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('admin_panel_settings', size='2.5rem').style('color: #00f3ff; transition: all 0.3s ease;')
                            ui.label('IAM Policy Control').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Manage Identity and Access Management policies for datasets and resources.').classes('text-xs').style(
                                'color: #94a3b8; line-height: 1.5;'
                            )
                    
                    # Card 5 - Audit & Compliance
                    card_audit = ui.card().style(
                        'background: rgba(15, 25, 35, 0.85); '
                        'border: 1px solid rgba(0, 243, 255, 0.2); '
                        'width: 280px; '
                        'padding: 1.5rem; '
                        'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); '
                        'cursor: pointer;'
                    )
                    
                    with card_audit:
                        with ui.column().classes('items-center gap-3 text-center'):
                            ui.icon('history', size='2.5rem').style('color: #00f3ff; transition: all 0.3s ease;')
                            ui.label('Audit & Compliance').classes('text-lg font-bold').style('color: #ffffff;')
                            ui.label('Track all security changes with comprehensive audit logs and compliance reports.').classes('text-xs').style(
                                'color: #94a3b8; line-height: 1.5;'
                            )
        
        # CSS para efeitos hover nos cards
        ui.add_head_html('''
            <style>
                /* Hover effect para todos os cards */
                .q-card {
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                }
                
                .q-card:hover {
                    transform: translateY(-8px) scale(1.02) !important;
                    border-color: rgba(0, 243, 255, 0.5) !important;
                    box-shadow: 
                        0 0 30px rgba(0, 243, 255, 0.3),
                        0 10px 40px rgba(0, 0, 0, 0.5) !important;
                    background: rgba(15, 25, 35, 0.95) !important;
                }
                
                /* Efeito no ícone durante hover */
                .q-card:hover .q-icon {
                    transform: scale(1.15) rotate(5deg) !important;
                    filter: drop-shadow(0 0 15px rgba(0, 243, 255, 0.6)) !important;
                }
                
                /* Animação suave */
                .q-icon {
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                }
            </style>
        ''')
