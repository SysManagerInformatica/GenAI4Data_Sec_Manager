"""
RLS Views Service
Manages RLS-protected views in BigQuery

VERSION: 1.0
Date: 14/12/2024
Author: Lucas Carvalhal - Sys Manager
"""

from google.cloud import bigquery
from typing import List, Dict, Optional
import json
from datetime import datetime


class RLSViewsService:
    """Service for managing RLS views"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        self.views_dataset_suffix = "_views"
    
    def get_views_dataset(self, base_dataset: str) -> str:
        """Get or create views dataset"""
        views_dataset = f"{base_dataset}{self.views_dataset_suffix}"
        
        try:
            self.client.get_dataset(views_dataset)
        except Exception:
            # Create dataset if doesn't exist
            dataset = bigquery.Dataset(f"{self.project_id}.{views_dataset}")
            dataset.location = "us-central1"
            dataset.description = f"Protected RLS views from {base_dataset}"
            self.client.create_dataset(dataset)
        
        return views_dataset
    
    def create_rls_view(
        self,
        view_name: str,
        base_dataset: str,
        base_table: str,
        filters: List[Dict],  # [{"field": "diretoria", "operator": "=", "value": "TI"}]
        users: List[str],  # ["user:email@example.com", "group:team@example.com"]
        description: str = ""
    ) -> Optional[str]:
        """
        Create a new RLS-protected view
        
        Args:
            view_name: Name for the view
            base_dataset: Source dataset
            base_table: Source table
            filters: List of filter conditions
            users: List of users/groups to grant access
            description: Optional description
        
        Returns:
            View full name if successful, None otherwise
        """
        try:
            # Get/create views dataset
            views_dataset = self.get_views_dataset(base_dataset)
            view_full_name = f"{self.project_id}.{views_dataset}.{view_name}"
            
            # Build WHERE clause from filters
            where_clauses = []
            for f in filters:
                field = f['field']
                op = f.get('operator', '=')
                value = f['value']
                
                # Handle different value types
                if isinstance(value, str):
                    where_clauses.append(f"{field} {op} '{value}'")
                else:
                    where_clauses.append(f"{field} {op} {value}")
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"
            
            # Create VIEW SQL
            view_sql = f"""
            CREATE OR REPLACE VIEW `{view_full_name}` AS
            SELECT *
            FROM `{self.project_id}.{base_dataset}.{base_table}`
            WHERE {where_clause};
            """
            
            # Create view
            query_job = self.client.query(view_sql)
            query_job.result()
            
            # Apply RLS policy to the VIEW
            policy_name = f"rls_{view_name}"
            
            # Build GRANT TO clause
            grant_to = ", ".join([f'"{u}"' for u in users])
            
            rls_sql = f"""
            CREATE OR REPLACE ROW ACCESS POLICY `{policy_name}`
            ON `{view_full_name}`
            GRANT TO ({grant_to})
            FILTER USING (TRUE);
            """
            
            # Apply RLS
            query_job = self.client.query(rls_sql)
            query_job.result()
            
            # Update view description with metadata
            table_ref = self.client.dataset(views_dataset).table(view_name)
            table = self.client.get_table(table_ref)
            
            metadata = {
                "type": "RLS_VIEW",
                "base_dataset": base_dataset,
                "base_table": base_table,
                "filters": filters,
                "users": users,
                "created_at": datetime.utcnow().isoformat(),
                "description": description
            }
            
            table.description = f"RLS_METADATA:{json.dumps(metadata)}"
            if description:
                table.description = f"{description}\n\n{table.description}"
            
            self.client.update_table(table, ['description'])
            
            # Configure as Authorized View
            self.configure_authorized_view(views_dataset, view_name, base_dataset)
            
            return view_full_name
            
        except Exception as e:
            print(f"Error creating RLS view: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def configure_authorized_view(self, views_dataset: str, view_name: str, base_dataset: str):
        """Configure view as Authorized View on base dataset"""
        try:
            from google.cloud.bigquery import AccessEntry
            
            # Get base dataset
            dataset_ref = self.client.dataset(base_dataset)
            dataset = self.client.get_dataset(dataset_ref)
            
            # Create authorized view entry
            authorized_view = {
                'projectId': self.project_id,
                'datasetId': views_dataset,
                'tableId': view_name
            }
            
            view_entry = AccessEntry(
                role=None,
                entity_type='view',
                entity_id=authorized_view
            )
            
            # Add to access entries
            access_entries = list(dataset.access_entries or [])
            
            # Check if already exists
            exists = any(
                e.entity_type == 'view' and e.entity_id == authorized_view
                for e in access_entries
            )
            
            if not exists:
                access_entries.append(view_entry)
                dataset.access_entries = access_entries
                self.client.update_dataset(dataset, ['access_entries'])
                print(f"✅ Configured {view_name} as Authorized View")
            
        except Exception as e:
            print(f"Warning: Could not configure authorized view: {e}")
            # Not critical, continue anyway
    
    def list_rls_views(self, dataset: str) -> List[Dict]:
        """List all RLS views for a dataset"""
        try:
            views = []
            views_dataset = f"{dataset}{self.views_dataset_suffix}"
            
            # Check if views dataset exists
            try:
                tables = self.client.list_tables(views_dataset)
            except Exception:
                return []  # Dataset doesn't exist yet
            
            for table in tables:
                table_ref = self.client.dataset(views_dataset).table(table.table_id)
                table_obj = self.client.get_table(table_ref)
                
                # Check if it's a view
                if table_obj.table_type != 'VIEW':
                    continue
                
                # Check if it's an RLS view
                if not table_obj.description or 'RLS_METADATA:' not in table_obj.description:
                    continue
                
                # Extract metadata
                try:
                    metadata_str = table_obj.description.split('RLS_METADATA:')[1]
                    metadata = json.loads(metadata_str)
                except:
                    continue
                
                # Get policy info
                policies = self.get_view_policies(views_dataset, table.table_id)
                
                views.append({
                    'view_name': table.table_id,
                    'view_dataset': views_dataset,
                    'base_dataset': metadata.get('base_dataset'),
                    'base_table': metadata.get('base_table'),
                    'filters': metadata.get('filters', []),
                    'users': metadata.get('users', []),
                    'policies': policies,
                    'created_at': metadata.get('created_at'),
                    'description': metadata.get('description', ''),
                    'has_cls': False  # Will be updated by CLS check
                })
            
            return views
            
        except Exception as e:
            print(f"Error listing RLS views: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_view_policies(self, dataset: str, view_name: str) -> List[Dict]:
        """Get RLS policies applied to a view"""
        try:
            table_ref = self.client.dataset(dataset).table(view_name)
            table = self.client.get_table(table_ref)
            
            policies = []
            if hasattr(table, 'row_access_policies') and table.row_access_policies:
                for policy in table.row_access_policies:
                    policies.append({
                        'policy_id': policy.policy_id,
                        'filter': policy.filter_predicate,
                        'grantees': list(policy.grantees) if policy.grantees else []
                    })
            
            return policies
            
        except Exception as e:
            print(f"Error getting policies: {e}")
            return []
    
    def update_rls_view_users(
        self,
        view_dataset: str,
        view_name: str,
        users: List[str]
    ) -> bool:
        """Update users with access to RLS view"""
        try:
            # Get current metadata
            table_ref = self.client.dataset(view_dataset).table(view_name)
            table = self.client.get_table(table_ref)
            
            metadata_str = table.description.split('RLS_METADATA:')[1]
            metadata = json.loads(metadata_str)
            
            # Update users in metadata
            metadata['users'] = users
            metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update description
            desc_parts = table.description.split('RLS_METADATA:')[0]
            table.description = f"{desc_parts}RLS_METADATA:{json.dumps(metadata)}"
            self.client.update_table(table, ['description'])
            
            # Update RLS policy
            view_full_name = f"{self.project_id}.{view_dataset}.{view_name}"
            policy_name = f"rls_{view_name}"
            
            # Drop old policy
            try:
                drop_sql = f"DROP ROW ACCESS POLICY `{policy_name}` ON `{view_full_name}`;"
                self.client.query(drop_sql).result()
            except:
                pass
            
            # Create new policy with updated users
            grant_to = ", ".join([f'"{u}"' for u in users])
            
            rls_sql = f"""
            CREATE OR REPLACE ROW ACCESS POLICY `{policy_name}`
            ON `{view_full_name}`
            GRANT TO ({grant_to})
            FILTER USING (TRUE);
            """
            
            self.client.query(rls_sql).result()
            
            return True
            
        except Exception as e:
            print(f"Error updating users: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_rls_view_filters(
        self,
        view_dataset: str,
        view_name: str,
        filters: List[Dict],
        base_dataset: str,
        base_table: str
    ) -> bool:
        """Update filters for RLS view"""
        try:
            # Get current metadata
            table_ref = self.client.dataset(view_dataset).table(view_name)
            table = self.client.get_table(table_ref)
            
            metadata_str = table.description.split('RLS_METADATA:')[1]
            metadata = json.loads(metadata_str)
            
            # Update filters in metadata
            metadata['filters'] = filters
            metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update description
            desc_parts = table.description.split('RLS_METADATA:')[0]
            table.description = f"{desc_parts}RLS_METADATA:{json.dumps(metadata)}"
            self.client.update_table(table, ['description'])
            
            # Rebuild view with new filters
            where_clauses = []
            for f in filters:
                field = f['field']
                op = f.get('operator', '=')
                value = f['value']
                
                if isinstance(value, str):
                    where_clauses.append(f"{field} {op} '{value}'")
                else:
                    where_clauses.append(f"{field} {op} {value}")
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"
            
            view_full_name = f"{self.project_id}.{view_dataset}.{view_name}"
            
            view_sql = f"""
            CREATE OR REPLACE VIEW `{view_full_name}` AS
            SELECT *
            FROM `{self.project_id}.{base_dataset}.{base_table}`
            WHERE {where_clause};
            """
            
            self.client.query(view_sql).result()
            
            return True
            
        except Exception as e:
            print(f"Error updating filters: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_rls_view(self, view_dataset: str, view_name: str) -> bool:
        """Delete an RLS view"""
        try:
            table_ref = self.client.dataset(view_dataset).table(view_name)
            self.client.delete_table(table_ref)
            return True
            
        except Exception as e:
            print(f"Error deleting view: {e}")
            return False
    
    def get_table_schema(self, dataset: str, table: str) -> List[Dict]:
        """Get schema of a table"""
        try:
            table_ref = self.client.dataset(dataset).table(table)
            table_obj = self.client.get_table(table_ref)
            
            schema = []
            for field in table_obj.schema:
                schema.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description or ''
                })
            
            return schema
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return []
