"""
Audit Logs Page
View and filter security audit logs
"""

from nicegui import ui
import theme
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
        with theme.frame('Audit Logs'):
            ui.label('📊 Audit Logs').classes('text-3xl font-bold mb-4')
            ui.label('Track all security operations and changes').classes('text-gray-600 mb-6')
            
            # Statistics cards
            self.stats_container = ui.row().classes('gap-4 mb-6 w-full')
            self.render_statistics()
            
            # Filters
            with ui.card().classes('w-full mb-4'):
                ui.label('🔍 Filters').classes('text-xl font-bold mb-3')
                
                with ui.row().classes('gap-4 items-end'):
                    # Date range filter
                    date_options = [
                        'last_hour',
                        'today', 
                        'last_7_days',
                        'last_30_days'
                    ]
                    ui.select(
                        label='Date Range',
                        options=date_options,
                        value='last_7_days',
                        on_change=lambda e: self.update_filter('date_range', e.value)
                    ).classes('w-48')
                    
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
                        label='Action',
                        options=action_options,
                        value='ALL',
                        on_change=lambda e: self.update_filter('action', e.value)
                    ).classes('w-64')
                    
                    # Refresh button
                    ui.button('🔄 Refresh', on_click=self.refresh_logs).props('color=primary')
            
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
                    ui.label('Total Actions').classes('text-sm text-gray-600')
                    ui.label(str(stats.get('total_actions', 0))).classes('text-3xl font-bold text-blue-600')
                
                # Success rate
                with ui.card().classes('p-4'):
                    ui.label('Success Rate').classes('text-sm text-gray-600')
                    success_rate = stats.get('success_rate', 0)
                    color = 'text-green-600' if success_rate >= 95 else 'text-yellow-600' if success_rate >= 80 else 'text-red-600'
                    ui.label(f"{success_rate}%").classes(f'text-3xl font-bold {color}')
                
                # Failed actions
                with ui.card().classes('p-4'):
                    ui.label('Failed Actions').classes('text-sm text-gray-600')
                    ui.label(str(stats.get('failed_actions', 0))).classes('text-3xl font-bold text-red-600')
                
                # Unique users
                with ui.card().classes('p-4'):
                    ui.label('Active Users').classes('text-sm text-gray-600')
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
                ui.label(f'📋 Recent Activities (showing {len(logs)} logs)').classes('text-xl font-bold mb-4')
                
                for log in logs:
                    self.render_log_card(log)
            else:
                ui.label('⚠️ No audit logs found with current filters').classes('text-gray-500 text-center mt-8')
    
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
                        ui.label(f"👤 User: {log['user_email']}")
                        ui.label(f"📦 Resource: {log['resource_name']} ({log['resource_type']})")
                        
                        if log.get('taxonomy'):
                            ui.label(f"📁 Taxonomy: {log['taxonomy']}")
                        
                        if log.get('error_message'):
                            ui.label(f"⚠️ Error: {log['error_message']}").classes('text-red-600')
                
                # Timestamp
                with ui.column().classes('text-right'):
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    ui.label(timestamp.strftime('%Y-%m-%d')).classes('text-sm text-gray-500')
                    ui.label(timestamp.strftime('%H:%M:%S')).classes('text-sm font-mono text-gray-700')
