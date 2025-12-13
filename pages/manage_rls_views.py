"""
Manage RLS Views Page
Manage existing RLS-protected views

VERSION: 1.0
Date: 14/12/2024
Author: Lucas Carvalhal - Sys Manager
"""

import theme
from theme import get_text
from config import Config
from nicegui import ui, run
from google.cloud import bigquery
from services.audit_service import AuditService
from services.rls_views_service import RLSViewsService
import asyncio


config = Config()
client = bigquery.Client(project=config.PROJECT_ID)


class ManageRLSViews:
    def __init__(self):
        self.project_id = config.PROJECT_ID
        self.audit_service = AuditService(config.PROJECT_ID)
        self.rls_service = RLSViewsService(config.PROJECT_ID)
        
        self.selected_dataset = None
        self.rls_views = []
        self.views_grid = None
        self.dataset_select = None
        
        self.current_view = None
        
        self.headers()
        self.render_ui()
    
    def headers(self):
        ui.page_title("Manage RLS Views")
        ui.label("Manage RLS-Protected Views").classes('text-primary text-center text-bold')
    
    def get_datasets(self):
        try:
            datasets = list(client.list_datasets())
            return [d.dataset_id for d in datasets if not d.dataset_id.endswith('_views')]
        except Exception as e:
            print(f"Error getting datasets: {e}")
            return []
    
    async def on_dataset_change(self, e):
        self.selected_dataset = e.value
        
        n = ui.notification("Loading RLS views...", spinner=True, timeout=None)
        try:
            self.rls_views = await run.io_bound(
                self.rls_service.list_rls_views,
                self.selected_dataset
            )
            
            if self.views_grid:
                self.views_grid.options['rowData'] = self.rls_views
                self.views_grid.update()
            
            n.dismiss()
            ui.notify(f"✅ Loaded {len(self.rls_views)} RLS views", type="positive")
            
        except Exception as e:
            n.dismiss()
            ui.notify(f"Error: {e}", type="negative")
            import traceback
            traceback.print_exc()
    
    async def edit_view(self):
        """Edit selected view"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify("No view selected", type="warning")
            return
        
        view_info = rows[0]
        self.current_view = view_info
        
        with ui.dialog() as edit_dialog, ui.card().classes('w-full max-w-4xl'):
            ui.label(f"Edit RLS View: {view_info['view_name']}").classes('text-h5 font-bold mb-4')
            
            # View info
            with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                ui.label("📋 View Information").classes('font-bold mb-2')
                ui.label(f"Dataset: {view_info['view_dataset']}").classes('text-sm')
                ui.label(f"Source: {view_info['base_dataset']}.{view_info['base_table']}").classes('text-sm')
                ui.label(f"Created: {view_info['created_at']}").classes('text-sm')
            
            with ui.tabs().classes('w-full') as tabs:
                tab_users = ui.tab("👥 Users & Groups", icon='people')
                tab_filters = ui.tab("🔍 Filters", icon='filter_list')
            
            with ui.tab_panels(tabs, value=tab_users).classes('w-full'):
                # Users tab
                with ui.tab_panel(tab_users):
                    ui.label("Authorized Users & Groups").classes('font-bold mb-4')
                    
                    # Add user/group
                    with ui.row().classes('w-full gap-2 mb-4'):
                        user_type = ui.select(
                            options=['user', 'group'],
                            label="Type",
                            value='user'
                        ).classes('w-32')
                        
                        user_email = ui.input(
                            label="Email",
                            placeholder="user@example.com"
                        ).classes('flex-1')
                        
                        def add_user_to_view():
                            email = user_email.value.strip()
                            if not email or '@' not in email:
                                ui.notify("Invalid email", type="warning")
                                return
                            
                            entry = f"{user_type.value}:{email}"
                            if entry not in view_info['users']:
                                view_info['users'].append(entry)
                                user_email.value = ''
                                refresh_users_list()
                                ui.notify(f"{user_type.value.title()} added!", type="positive")
                            else:
                                ui.notify("Already added", type="warning")
                        
                        ui.button(
                            "ADD",
                            icon="add",
                            on_click=add_user_to_view
                        ).props('color=primary')
                    
                    # Users list
                    users_container = ui.column().classes('w-full gap-2')
                    
                    def refresh_users_list():
                        users_container.clear()
                        with users_container:
                            if not view_info['users']:
                                ui.label("No users/groups added").classes('text-gray-500 italic')
                            else:
                                for entry in view_info['users']:
                                    with ui.card().classes('w-full p-3 bg-green-50'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            icon = "👤" if entry.startswith("user:") else "👥"
                                            label = entry.replace("user:", "").replace("group:", "")
                                            ui.label(f"{icon} {label}").classes('font-mono')
                                            
                                            def make_remove_handler(e):
                                                def remove():
                                                    view_info['users'].remove(e)
                                                    refresh_users_list()
                                                    ui.notify("Removed", type="info")
                                                return remove
                                            
                                            ui.button(
                                                icon="delete",
                                                on_click=make_remove_handler(entry)
                                            ).props('flat dense color=negative')
                    
                    refresh_users_list()
                
                # Filters tab
                with ui.tab_panel(tab_filters):
                    ui.label("Filter Conditions").classes('font-bold mb-4')
                    
                    # Add filter
                    schema = self.rls_service.get_table_schema(
                        view_info['base_dataset'],
                        view_info['base_table']
                    )
                    
                    with ui.row().classes('w-full gap-2 mb-4'):
                        filter_field = ui.select(
                            options=[col['name'] for col in schema],
                            label="Field"
                        ).classes('flex-1')
                        
                        filter_op = ui.select(
                            options=['=', '!=', '>', '<', '>=', '<=', 'LIKE'],
                            label="Operator",
                            value='='
                        ).classes('w-32')
                        
                        filter_val = ui.input(
                            label="Value",
                            placeholder="'value'"
                        ).classes('flex-1')
                        
                        def add_filter_to_view():
                            if not filter_field.value or not filter_val.value:
                                ui.notify("Fill all fields", type="warning")
                                return
                            
                            new_filter = {
                                'field': filter_field.value,
                                'operator': filter_op.value,
                                'value': filter_val.value
                            }
                            
                            view_info['filters'].append(new_filter)
                            filter_val.value = ''
                            refresh_filters_list()
                            ui.notify("Filter added!", type="positive")
                        
                        ui.button(
                            "ADD FILTER",
                            icon="add",
                            on_click=add_filter_to_view
                        ).props('color=primary')
                    
                    # Filters list
                    filters_container = ui.column().classes('w-full gap-2')
                    
                    def refresh_filters_list():
                        filters_container.clear()
                        with filters_container:
                            if not view_info['filters']:
                                ui.label("No filters (all rows visible)").classes('text-orange-600 italic')
                            else:
                                for i, f in enumerate(view_info['filters']):
                                    with ui.card().classes('w-full p-3 bg-blue-50'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            ui.label(f"{f['field']} {f['operator']} {f['value']}").classes('font-mono')
                                            
                                            def make_remove_filter_handler(idx):
                                                def remove():
                                                    view_info['filters'].pop(idx)
                                                    refresh_filters_list()
                                                    ui.notify("Filter removed", type="info")
                                                return remove
                                            
                                            ui.button(
                                                icon="delete",
                                                on_click=make_remove_filter_handler(i)
                                            ).props('flat dense color=negative')
                    
                    refresh_filters_list()
            
            # Save buttons
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button("CANCEL", on_click=edit_dialog.close).props('flat')
                
                async def save_changes():
                    n = ui.notification("Saving changes...", spinner=True, timeout=None)
                    try:
                        # Update users
                        users_updated = await run.io_bound(
                            self.rls_service.update_rls_view_users,
                            view_info['view_dataset'],
                            view_info['view_name'],
                            view_info['users']
                        )
                        
                        # Update filters
                        filters_updated = await run.io_bound(
                            self.rls_service.update_rls_view_filters,
                            view_info['view_dataset'],
                            view_info['view_name'],
                            view_info['filters'],
                            view_info['base_dataset'],
                            view_info['base_table']
                        )
                        
                        n.dismiss()
                        
                        if users_updated and filters_updated:
                            self.audit_service.log_action(
                                action='UPDATE_RLS_VIEW',
                                resource_type='RLS_VIEW',
                                resource_name=view_info['view_name'],
                                status='SUCCESS',
                                details={
                                    'view': view_info['view_name'],
                                    'users_count': len(view_info['users']),
                                    'filters_count': len(view_info['filters'])
                                }
                            )
                            
                            ui.notify("✅ Changes saved!", type="positive")
                            edit_dialog.close()
                            
                            # Refresh grid
                            await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
                        else:
                            ui.notify("❌ Error saving changes", type="negative")
                    
                    except Exception as e:
                        n.dismiss()
                        ui.notify(f"Error: {e}", type="negative")
                        import traceback
                        traceback.print_exc()
                
                ui.button(
                    "SAVE CHANGES",
                    icon="save",
                    on_click=save_changes
                ).props('color=positive')
        
        edit_dialog.open()
    
    async def delete_selected_views(self):
        """Delete selected views"""
        rows = await self.views_grid.get_selected_rows()
        if not rows:
            ui.notify("No views selected", type="warning")
            return
        
        view_names = [f"{row['view_dataset']}.{row['view_name']}" for row in rows]
        
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label("⚠️ Confirm Deletion").classes('text-h6 font-bold text-red-600 mb-4')
            ui.label(f"Delete {len(view_names)} RLS view(s)?").classes('mb-2')
            
            for name in view_names[:10]:
                ui.label(f"  • {name}").classes('text-sm')
            if len(view_names) > 10:
                ui.label(f"  ... and {len(view_names)-10} more").classes('text-sm italic')
            
            ui.label("This action cannot be undone!").classes('text-red-600 font-bold mt-4')
            
            async def execute_deletion():
                success = 0
                failed = 0
                
                for view in rows:
                    try:
                        result = await run.io_bound(
                            self.rls_service.delete_rls_view,
                            view['view_dataset'],
                            view['view_name']
                        )
                        
                        if result:
                            self.audit_service.log_action(
                                action='DELETE_RLS_VIEW',
                                resource_type='RLS_VIEW',
                                resource_name=view['view_name'],
                                status='SUCCESS'
                            )
                            success += 1
                        else:
                            failed += 1
                    except Exception as e:
                        self.audit_service.log_action(
                            action='DELETE_RLS_VIEW',
                            resource_type='RLS_VIEW',
                            resource_name=view['view_name'],
                            status='FAILED',
                            error_message=str(e)
                        )
                        failed += 1
                
                confirm_dialog.close()
                
                if success > 0:
                    ui.notify(f"✅ {success} view(s) deleted", type="positive")
                if failed > 0:
                    ui.notify(f"❌ {failed} failed", type="negative")
                
                # Refresh grid
                await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button("CANCEL", on_click=confirm_dialog.close).props('flat')
                ui.button(
                    "DELETE",
                    icon="delete_forever",
                    on_click=execute_deletion
                ).props('color=negative')
        
        confirm_dialog.open()
    
    async def refresh_views(self):
        """Refresh views list"""
        if self.selected_dataset:
            await self.on_dataset_change(type('obj', (object,), {'value': self.selected_dataset})())
        else:
            ui.notify("Select a dataset first", type="warning")
    
    def render_ui(self):
        with theme.frame('RLS - Manage Protected Views'):
            with ui.card().classes('w-full'):
                ui.label("🔐 RLS-Protected Views").classes('text-h5 font-bold mb-4')
                
                with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
                    ui.label("ℹ️ RLS Views Architecture").classes('font-bold mb-2')
                    ui.label("• Views are stored in {dataset}_views datasets").classes('text-xs')
                    ui.label("• Each view has RLS policy with SPECIFIC users (not allAuthenticatedUsers)").classes('text-xs')
                    ui.label("• Users access ONLY the view, NOT the source table").classes('text-xs')
                    ui.label("• Can combine RLS + CLS on the same view").classes('text-xs font-bold text-blue-600')
                
                # Dataset selector
                with ui.row().classes('w-full gap-4 mb-4 items-center'):
                    self.dataset_select = ui.select(
                        options=self.get_datasets(),
                        label="Select Dataset",
                        on_change=self.on_dataset_change
                    ).classes('flex-1')
                    
                    ui.button(
                        "REFRESH",
                        icon="refresh",
                        on_click=self.refresh_views
                    ).props('flat')
                
                # Grid
                ui.separator()
                ui.label("RLS Views").classes('text-h6 font-bold mt-4 mb-2')
                
                self.views_grid = ui.aggrid({
                    'columnDefs': [
                        {'field': 'view_name', 'headerName': 'View Name', 'checkboxSelection': True, 'filter': True, 'minWidth': 250},
                        {'field': 'view_dataset', 'headerName': 'Dataset', 'filter': True, 'minWidth': 180},
                        {'field': 'base_table', 'headerName': 'Source Table', 'filter': True, 'minWidth': 180},
                        {
                            'field': 'users',
                            'headerName': 'Users/Groups',
                            'filter': True,
                            'minWidth': 100,
                            'valueGetter': 'data.users ? data.users.length : 0'
                        },
                        {
                            'field': 'filters',
                            'headerName': 'Filters',
                            'filter': True,
                            'minWidth': 100,
                            'valueGetter': 'data.filters ? data.filters.length : 0'
                        },
                        {'field': 'created_at', 'headerName': 'Created', 'filter': True, 'minWidth': 160},
                    ],
                    'rowData': [],
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'resizable': True},
                }).classes('w-full h-96 ag-theme-quartz')
                
                # Action buttons
                with ui.row().classes('mt-2 gap-2'):
                    ui.button(
                        "EDIT VIEW",
                        icon="edit",
                        on_click=self.edit_view
                    ).props('color=primary')
                    
                    ui.button(
                        "DELETE SELECTED",
                        icon="delete",
                        on_click=self.delete_selected_views
                    ).props('color=negative')
                    
                    ui.button(
                        "CREATE NEW RLS VIEW",
                        icon="add_circle",
                        on_click=lambda: ui.navigate.to('/rls/create-view')
                    ).props('color=positive outline')
    
    def run(self):
        pass
