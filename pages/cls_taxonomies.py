"""
CLS Taxonomies Page
Manage Data Catalog taxonomies
"""

from nicegui import ui
import theme
from config import Config
from services.datacatalog_service import DataCatalogService
from services.audit_service import AuditService


class CLSTaxonomies:
    def __init__(self):
        self.datacatalog_service = DataCatalogService(Config.PROJECT_ID, Config.LOCATION)
        self.audit_service = AuditService(Config.PROJECT_ID)
        self.taxonomies_container = None
    
    def run(self):
        with theme.frame('CLS - Manage Taxonomies'):
            ui.label('📁 Manage Taxonomies').classes('text-3xl font-bold mb-4')
            ui.label('Create and manage Data Catalog taxonomies for column-level security').classes('text-gray-600 mb-6')
            
            # Create button
            ui.button('➕ Create New Taxonomy', 
                     on_click=self.show_create_dialog,
                     icon='add').classes('mb-4')
            
            # Container for taxonomies list
            self.taxonomies_container = ui.column().classes('gap-4 w-full')
            self.refresh_taxonomies()
    
    def refresh_taxonomies(self):
        """Refresh the taxonomies list"""
        self.taxonomies_container.clear()
        
        with self.taxonomies_container:
            taxonomies = self.datacatalog_service.list_taxonomies()
            
            if taxonomies:
                for tax in taxonomies:
                    with ui.card().classes('w-full'):
                        with ui.row().classes('items-center justify-between w-full'):
                            with ui.column():
                                ui.label(tax['display_name']).classes('text-xl font-bold')
                                ui.label(tax['description'] or 'No description').classes('text-sm text-gray-600')
                                ui.label(f"🏷️ {tax['tag_count']} policy tags").classes('text-sm')
                            
                            with ui.row().classes('gap-2'):
                                ui.button('✏️', 
                                         on_click=lambda t=tax: self.show_edit_dialog(t)).props('flat dense').classes('text-blue-500')
                                ui.button('🗑️', 
                                         on_click=lambda t=tax: self.show_delete_dialog(t)).props('flat dense').classes('text-red-500')
            else:
                ui.label('⚠️ No taxonomies found. Create your first taxonomy!').classes('text-gray-500')
    
    def show_create_dialog(self):
        """Show dialog to create new taxonomy"""
        with ui.dialog() as dialog, ui.card():
            ui.label('➕ Create New Taxonomy').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input('Taxonomy Name', placeholder='e.g., PII').classes('w-full')
            desc_input = ui.textarea('Description', 
                                    placeholder='e.g., Personally Identifiable Information').classes('w-full')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def create():
                    if not name_input.value:
                        ui.notify('Please enter a taxonomy name', type='warning')
                        return
                    
                    try:
                        result = self.datacatalog_service.create_taxonomy(
                            name_input.value,
                            desc_input.value or ''
                        )
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='CREATE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=name_input.value,
                                status='SUCCESS',
                                details={
                                    'description': desc_input.value or '',
                                    'display_name': name_input.value
                                }
                            )
                            
                            ui.notify(f'✅ Taxonomy "{name_input.value}" created successfully!', type='positive')
                            dialog.close()
                            self.refresh_taxonomies()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='CREATE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=name_input.value,
                                status='FAILED',
                                error_message='Unknown error creating taxonomy'
                            )
                            ui.notify('❌ Error creating taxonomy', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='CREATE_TAXONOMY',
                            resource_type='TAXONOMY',
                            resource_name=name_input.value,
                            status='FAILED',
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Create', on_click=create).props('color=primary')
        
        dialog.open()
    
    def show_edit_dialog(self, taxonomy):
        """Show dialog to edit taxonomy"""
        with ui.dialog() as dialog, ui.card():
            ui.label('✏️ Edit Taxonomy').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input('Taxonomy Name', value=taxonomy['display_name']).classes('w-full')
            desc_input = ui.textarea('Description', value=taxonomy['description']).classes('w-full')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def update():
                    try:
                        result = self.datacatalog_service.update_taxonomy(
                            taxonomy['name'],
                            name_input.value,
                            desc_input.value
                        )
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='UPDATE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=name_input.value,
                                status='SUCCESS',
                                taxonomy=taxonomy['display_name'],
                                details={
                                    'old_name': taxonomy['display_name'],
                                    'new_name': name_input.value,
                                    'description': desc_input.value
                                }
                            )
                            
                            ui.notify('✅ Taxonomy updated successfully!', type='positive')
                            dialog.close()
                            self.refresh_taxonomies()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='UPDATE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=taxonomy['display_name'],
                                status='FAILED',
                                error_message='Unknown error updating taxonomy'
                            )
                            ui.notify('❌ Error updating taxonomy', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='UPDATE_TAXONOMY',
                            resource_type='TAXONOMY',
                            resource_name=taxonomy['display_name'],
                            status='FAILED',
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Save', on_click=update).props('color=primary')
        
        dialog.open()
    
    def show_delete_dialog(self, taxonomy):
        """Show dialog to confirm deletion"""
        with ui.dialog() as dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-2xl font-bold mb-4')
            ui.label(f'Are you sure you want to delete taxonomy "{taxonomy["display_name"]}"?')
            ui.label('This action cannot be undone!').classes('text-red-600 font-bold')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def confirm_delete():
                    try:
                        result = self.datacatalog_service.delete_taxonomy(taxonomy['name'])
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='DELETE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=taxonomy['display_name'],
                                status='SUCCESS',
                                details={
                                    'tag_count': taxonomy.get('tag_count', 0)
                                }
                            )
                            
                            ui.notify('✅ Taxonomy deleted successfully!', type='positive')
                            dialog.close()
                            self.refresh_taxonomies()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='DELETE_TAXONOMY',
                                resource_type='TAXONOMY',
                                resource_name=taxonomy['display_name'],
                                status='FAILED',
                                error_message='Unknown error deleting taxonomy'
                            )
                            ui.notify('❌ Error deleting taxonomy', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='DELETE_TAXONOMY',
                            resource_type='TAXONOMY',
                            resource_name=taxonomy['display_name'],
                            status='FAILED',
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Delete', on_click=confirm_delete).props('color=negative')
        
        dialog.open()
