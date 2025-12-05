"""
Audit Logs Page
View and filter security audit logs
VERSION: 2.1 - Multi-Language Support
"""

from nicegui import ui
import theme
from theme import get_text  # <- NOVO: importar função de tradução
from config import Config
from services.audit_service import AuditService
from datetime import datetime


class AuditLogs:
    def __init__(self):
        self.audit_service = AuditService(Config.PROJECT_ID)
        self.logs_container = None
        self.stats_container = None
        self.filters = {
            'date_range': 'last_7_days',
            'action': 'ALL',
            'user_email': 'ALL'
        }
    
    def run(self):
        with theme.frame(get_text('audit_title')):  # <- TRADUZIDO
            ui.label(f'📊 {get_text("audit_title")}').classes('text-3xl font-bold mb-4')  # <- TRADUZIDO
            ui.label(get_text('audit_subtitle')).classes('text-gray-600 mb-6')  # <- TRADUZIDO
            
            # Statistics cards
            self.stats_container = ui.row().classes('gap-4 mb-6 w-full')
            self.render_statistics()
            
            # Filters
            with ui.card().classes('w-full mb-4'):
                ui.label(f'🔍 {get_text("audit_filters_title")}').classes('text-xl font-bold mb-3')  # <- TRADUZIDO
                
                with ui.row().classes('gap-4 items-end'):
                    # Date range filter
                    date_options = {
                        'last_hour': get_text('audit_filter_last_hour'),  # <- TRADUZIDO
                        'today': get_text('audit_filter_today'),  # <- TRADUZIDO
                        'last_7_days': get_text('audit_filter_last_7_days'),  # <- TRADUZIDO
                        'last_30_days': get_text('audit_filter_last_30_days')  # <- TRADUZIDO
                    }
                    ui.select(
                        label=get_text('audit_filter_date_range'),  # <- TRADUZIDO
                        options=list(date_options.keys()),
                        value='last_7_days',
                        on_change=lambda e: self.update_filter('date_range', e.value)
                    ).classes('w-48').bind_value_to(
                        self, 'filters', lambda v: date_options.get(v, v)
                    )
                    
                    # Action filter
                    action_options = [
                        'ALL',
                        # CLS Actions
                        'CREATE_TAXONOMY', 'UPDATE_TAXONOMY', 'DELETE_TAXONOMY',
                        'CREATE_POLICY_TAG', 'UPDATE_POLICY_TAG', 'DELETE_POLICY_TAG',
                        'APPLY_TAG', 'REMOVE_TAG',
                        # RLS Actions
                        'CREATE_RLS_POLICY_USER', 'CREATE_RLS_POLICY_GROUP',
                        'ASSIGN_USER_TO_POLICY', 'ASSIGN_VALUE_TO_GROUP'
                    ]
                    ui.select(
                        label=get_text('audit_filter_action'),  # <- TRADUZIDO
                        options=action_options,
                        value='ALL',
                        on_change=lambda e: self.update_filter('action', e.value)
                    ).classes('w-64')
                    
                    # Refresh button
                    ui.button(
                        f'🔄 {get_text("btn_refresh")}',  # <- TRADUZIDO
                        on_click=self.refresh_logs
                    ).props('color=primary')
            
            # Logs container
            self.logs_container = ui.column().classes('gap-4 w-full')
            self.refresh_logs()
    
    def render_statistics(self):
        """Render statistics cards"""
        self.stats_container.clear()
        
        with self.stats_container:
            stats = self.audit_service.get_statistics(self.filters['date_range'])
            
            if stats:
                # Total actions
                with ui.card().classes('p-4'):
                    ui.label(get_text('audit_stat_total_actions')).classes('text-sm text-gray-600')  # <- TRADUZIDO
                    ui.label(str(stats.get('total_actions', 0))).classes('text-3xl font-bold text-blue-600')
                
                # Success rate
                with ui.card().classes('p-4'):
                    ui.label(get_text('audit_stat_success_rate')).classes('text-sm text-gray-600')  # <- TRADUZIDO
                    success_rate = stats.get('success_rate', 0)
                    color = 'text-green-600' if success_rate >= 95 else 'text-yellow-600' if success_rate >= 80 else 'text-red-600'
                    ui.label(f"{success_rate}%").classes(f'text-3xl font-bold {color}')
                
                # Failed actions
                with ui.card().classes('p-4'):
                    ui.label(get_text('audit_stat_failed_actions')).classes('text-sm text-gray-600')  # <- TRADUZIDO
                    ui.label(str(stats.get('failed_actions', 0))).classes('text-3xl font-bold text-red-600')
                
                # Unique users
                with ui.card().classes('p-4'):
                    ui.label(get_text('audit_stat_active_users')).classes('text-sm text-gray-600')  # <- TRADUZIDO
                    ui.label(str(stats.get('unique_users', 0))).classes('text-3xl font-bold text-purple-600')
    
    def update_filter(self, filter_name, value):
        """Update filter and refresh"""
        self.filters[filter_name] = value
        self.refresh_logs()
        self.render_statistics()
    
    def refresh_logs(self):
        """Refresh the logs list"""
        self.logs_container.clear()
        
        with self.logs_container:
            logs = self.audit_service.get_recent_logs(limit=50, filters=self.filters)
            
            if logs:
                ui.label(
                    f'📋 {get_text("audit_recent_activities", count=len(logs))}'  # <- TRADUZIDO com formatação
                ).classes('text-xl font-bold mb-4')
                
                for log in logs:
                    self.render_log_card(log)
            else:
                ui.label(
                    f'⚠️ {get_text("audit_no_logs")}'  # <- TRADUZIDO
                ).classes('text-gray-500 text-center mt-8')
    
    def render_log_card(self, log):
        """Render a single log entry"""
        # Determine icon and color based on action
        action_icons = {
            # CLS Actions
            'CREATE_TAXONOMY': '📁',
            'UPDATE_TAXONOMY': '✏️',
            'DELETE_TAXONOMY': '🗑️',
            'CREATE_POLICY_TAG': '🏷️',
            'UPDATE_POLICY_TAG': '✏️',
            'DELETE_POLICY_TAG': '🗑️',
            'APPLY_TAG': '🔐',
            'REMOVE_TAG': '🔓',
            # RLS Actions
            'CREATE_RLS_POLICY_USER': '🔐',
            'CREATE_RLS_POLICY_GROUP': '👥',
            'ASSIGN_USER_TO_POLICY': '👤',
            'ASSIGN_VALUE_TO_GROUP': '📋',
            # System
            'SYSTEM_INIT': '⚙️'
        }
        
        icon = action_icons.get(log['action'], '📝')
        status_icon = '✅' if log['status'] == 'SUCCESS' else '❌'
        status_color = 'text-green-600' if log['status'] == 'SUCCESS' else 'text-red-600'
        
        with ui.card().classes('w-full p-4'):
            with ui.row().classes('items-start justify-between w-full'):
                with ui.column().classes('flex-grow'):
                    # Action title
                    with ui.row().classes('items-center gap-2 mb-2'):
                        ui.label(icon).classes('text-2xl')
                        ui.label(log['action'].replace('_', ' ')).classes('text-lg font-bold')
                        ui.label(status_icon).classes(f'text-xl {status_color}')
                    
                    # Details
                    with ui.column().classes('gap-1 text-sm text-gray-600'):
                        ui.label(f"👤 {get_text('audit_log_user')}: {log['user_email']}")  # <- TRADUZIDO
                        ui.label(f"📦 {get_text('audit_log_resource')}: {log['resource_name']} ({log['resource_type']})")  # <- TRADUZIDO
                        
                        if log.get('taxonomy'):
                            ui.label(f"📁 {get_text('audit_log_taxonomy')}: {log['taxonomy']}")  # <- TRADUZIDO
                        
                        if log.get('error_message'):
                            ui.label(f"⚠️ {get_text('audit_log_error')}: {log['error_message']}").classes('text-red-600')  # <- TRADUZIDO
                
                # Timestamp
                with ui.column().classes('text-right'):
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    ui.label(timestamp.strftime('%Y-%m-%d')).classes('text-sm text-gray-500')
                    ui.label(timestamp.strftime('%H:%M:%S')).classes('text-sm font-mono text-gray-700')
