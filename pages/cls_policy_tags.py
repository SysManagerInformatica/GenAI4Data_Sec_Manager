"""
CLS Policy Tags Page
Manage policy tags within taxonomies
"""

from nicegui import ui
import theme
from config import Config
from services.datacatalog_service import DataCatalogService
from services.audit_service import AuditService


class CLSPolicyTags:
    def __init__(self):
        self.datacatalog_service = DataCatalogService(Config.PROJECT_ID, Config.LOCATION)
        self.audit_service = AuditService(Config.PROJECT_ID)
        self.tags_container = None
        self.selected_taxonomy = None
        self.selected_taxonomy_display_name = None
        self.taxonomies = []
        self.taxonomy_map = {}
    
    def run(self):
        with theme.frame('CLS - Manage Policy Tags'):
            ui.label('🏷️ Manage Policy Tags').classes('text-3xl font-bold mb-4')
            ui.label('Create and manage policy tags within taxonomies').classes('text-gray-600 mb-6')
            
            # Get taxonomies
            self.taxonomies = self.datacatalog_service.list_taxonomies()
            
            if not self.taxonomies:
                ui.label('⚠️ No taxonomies found. Please create a taxonomy first.').classes('text-gray-500')
                ui.button('Go to Taxonomies', 
                         on_click=lambda: ui.navigate.to('/clstaxonomies/')).classes('mt-4')
                return
            
            # Create mapping of display_name to full taxonomy
            self.taxonomy_map = {tax['display_name']: tax for tax in self.taxonomies}
            
            # Don't pre-select
            self.selected_taxonomy = None
            
            # Taxonomy selector
            with ui.row().classes('gap-4 mb-4 items-center'):
                ui.label('Select Taxonomy:').classes('font-bold')
                
                # Simple list of display names
                taxonomy_names = [tax['display_name'] for tax in self.taxonomies]
                
                ui.select(
                    label='Choose a taxonomy',
                    options=taxonomy_names,
                    on_change=lambda e: self.on_taxonomy_change_by_display(e.value)
                ).classes('w-64')
                
                ui.button('➕ Create New Tag', 
                         on_click=self.show_create_dialog,
                         icon='add')
            
            # Container for tags list
            self.tags_container = ui.column().classes('gap-4 w-full')
            
            # Show message to select taxonomy
            with self.tags_container:
                ui.label('👆 Please select a taxonomy to view its policy tags').classes('text-gray-500 text-center mt-8')
    
    def on_taxonomy_change_by_display(self, display_name):
        """Handle taxonomy selection change by display name"""
        if display_name and display_name in self.taxonomy_map:
            taxonomy = self.taxonomy_map[display_name]
            self.selected_taxonomy = taxonomy['name']
            self.selected_taxonomy_display_name = display_name
            self.refresh_tags()
    
    def on_taxonomy_change(self, taxonomy_name):
        """Handle taxonomy selection change"""
        if taxonomy_name:
            self.selected_taxonomy = taxonomy_name
            self.refresh_tags()
    
    def refresh_tags(self):
        """Refresh the policy tags list"""
        if not self.selected_taxonomy:
            return
        
        self.tags_container.clear()
        
        with self.tags_container:
            tags = self.datacatalog_service.list_policy_tags(self.selected_taxonomy)
            
            if tags:
                for tag in tags:
                    with ui.card().classes('w-full'):
                        with ui.row().classes('items-center justify-between w-full'):
                            with ui.column():
                                ui.label(tag['display_name']).classes('text-xl font-bold')
                                ui.label(tag['description'] or 'No description').classes('text-sm text-gray-600')
                                if tag['child_count'] > 0:
                                    ui.label(f"👶 {tag['child_count']} child tags").classes('text-sm')
                            
                            with ui.row().classes('gap-2'):
                                ui.button('✏️', 
                                         on_click=lambda t=tag: self.show_edit_dialog(t)).props('flat dense').classes('text-blue-500')
                                ui.button('🗑️', 
                                         on_click=lambda t=tag: self.show_delete_dialog(t)).props('flat dense').classes('text-red-500')
            else:
                ui.label('⚠️ No policy tags found in this taxonomy. Create your first tag!').classes('text-gray-500')
    
    def show_create_dialog(self):
        """Show dialog to create new policy tag"""
        if not self.selected_taxonomy:
            ui.notify('⚠️ Please select a taxonomy first!', type='warning')
            return
            
        with ui.dialog() as dialog, ui.card():
            ui.label('➕ Create New Policy Tag').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input('Tag Name', placeholder='e.g., PII_HIGH').classes('w-full')
            desc_input = ui.textarea('Description', 
                                    placeholder='e.g., High sensitivity personal data').classes('w-full')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def create():
                    if not name_input.value:
                        ui.notify('Please enter a tag name', type='warning')
                        return
                    
                    try:
                        result = self.datacatalog_service.create_policy_tag(
                            self.selected_taxonomy,
                            name_input.value,
                            desc_input.value or ''
                        )
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='CREATE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=name_input.value,
                                status='SUCCESS',
                                taxonomy=self.selected_taxonomy_display_name,
                                details={
                                    'description': desc_input.value or '',
                                    'taxonomy': self.selected_taxonomy_display_name
                                }
                            )
                            
                            ui.notify(f'✅ Policy tag "{name_input.value}" created successfully!', type='positive')
                            dialog.close()
                            self.refresh_tags()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='CREATE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=name_input.value,
                                status='FAILED',
                                taxonomy=self.selected_taxonomy_display_name,
                                error_message='Unknown error creating policy tag'
                            )
                            ui.notify('❌ Error creating policy tag', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='CREATE_POLICY_TAG',
                            resource_type='POLICY_TAG',
                            resource_name=name_input.value,
                            status='FAILED',
                            taxonomy=self.selected_taxonomy_display_name,
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Create', on_click=create).props('color=primary')
        
        dialog.open()
    
    def show_edit_dialog(self, tag):
        """Show dialog to edit policy tag"""
        with ui.dialog() as dialog, ui.card():
            ui.label('✏️ Edit Policy Tag').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input('Tag Name', value=tag['display_name']).classes('w-full')
            desc_input = ui.textarea('Description', value=tag['description']).classes('w-full')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def update():
                    try:
                        result = self.datacatalog_service.update_policy_tag(
                            tag['name'],
                            name_input.value,
                            desc_input.value
                        )
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='UPDATE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=name_input.value,
                                status='SUCCESS',
                                taxonomy=self.selected_taxonomy_display_name,
                                details={
                                    'old_name': tag['display_name'],
                                    'new_name': name_input.value,
                                    'description': desc_input.value,
                                    'taxonomy': self.selected_taxonomy_display_name
                                }
                            )
                            
                            ui.notify('✅ Policy tag updated successfully!', type='positive')
                            dialog.close()
                            self.refresh_tags()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='UPDATE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=tag['display_name'],
                                status='FAILED',
                                taxonomy=self.selected_taxonomy_display_name,
                                error_message='Unknown error updating policy tag'
                            )
                            ui.notify('❌ Error updating policy tag', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='UPDATE_POLICY_TAG',
                            resource_type='POLICY_TAG',
                            resource_name=tag['display_name'],
                            status='FAILED',
                            taxonomy=self.selected_taxonomy_display_name,
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Save', on_click=update).props('color=primary')
        
        dialog.open()
    
    def show_delete_dialog(self, tag):
        """Show dialog to confirm deletion"""
        with ui.dialog() as dialog, ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-2xl font-bold mb-4')
            ui.label(f'Are you sure you want to delete policy tag "{tag["display_name"]}"?')
            ui.label('This action cannot be undone!').classes('text-red-600 font-bold')
            
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                
                def confirm_delete():
                    try:
                        result = self.datacatalog_service.delete_policy_tag(tag['name'])
                        
                        if result:
                            # Log success
                            self.audit_service.log_action(
                                action='DELETE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=tag['display_name'],
                                status='SUCCESS',
                                taxonomy=self.selected_taxonomy_display_name,
                                details={
                                    'child_count': tag.get('child_count', 0),
                                    'taxonomy': self.selected_taxonomy_display_name
                                }
                            )
                            
                            ui.notify('✅ Policy tag deleted successfully!', type='positive')
                            dialog.close()
                            self.refresh_tags()
                        else:
                            # Log failure
                            self.audit_service.log_action(
                                action='DELETE_POLICY_TAG',
                                resource_type='POLICY_TAG',
                                resource_name=tag['display_name'],
                                status='FAILED',
                                taxonomy=self.selected_taxonomy_display_name,
                                error_message='Unknown error deleting policy tag'
                            )
                            ui.notify('❌ Error deleting policy tag', type='negative')
                    
                    except Exception as e:
                        # Log exception
                        self.audit_service.log_action(
                            action='DELETE_POLICY_TAG',
                            resource_type='POLICY_TAG',
                            resource_name=tag['display_name'],
                            status='FAILED',
                            taxonomy=self.selected_taxonomy_display_name,
                            error_message=str(e)
                        )
                        ui.notify(f'❌ Error: {str(e)}', type='negative')
                
                ui.button('Delete', on_click=confirm_delete).props('color=negative')
        
        dialog.open()
