"""
RLS Views Service
Manages RLS-protected views in BigQuery

VERSION: 2.0 - FIXED for NEW RLS format (policies_filters table)
Date: 15/12/2024
Author: Lucas Carvalhal - Sys Manager
"""

from google.cloud import bigquery
from typing import List, Dict, Optional
import json
import re
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
    
    def detect_rls_view(self, table_obj) -> bool:
        """
        ✅ FIXED: Detect if view is RLS using NEW format
        
        Checks if view uses policies_filters table pattern
        """
        view_query = table_obj.view_query or ''
        
        # Check for RLS pattern: vw_ prefix + policies_filters + SESSION_USER()
        if (table_obj.table_id.startswith('vw_') and 
            'policies_filters' in view_query.lower() and 
            'session_user()' in view_query.lower()):
            return True
        
        # Also support old format (RLS_METADATA in description)
        if table_obj.description and 'RLS_METADATA:' in table_obj.description:
            return True
        
        return False
    
    def get_rls_users_from_policies_table(self, view_name: str) -> List[str]:
        """
        ✅ FIXED: Get RLS users from policies_filters table
        
        This is the NEW format where users are stored in BigQuery table
        """
        try:
            # Extract policy name from view name
            # vw_tb_headcount_executivo_diretoria_callous -> tb_headcount_executivo_diretoria_callous
            policy_base = view_name.replace('vw_', '')
            
            query = f"""
            SELECT DISTINCT username
            FROM `{self.project_id}.rls_manager.policies_filters`
            WHERE policy_name LIKE '%{policy_base}%'
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            users = [row.username for row in results if row.username]
            print(f"[DEBUG] Found {len(users)} RLS users for {view_name}: {users}")
            
            return users
        except Exception as e:
            print(f"[ERROR] get_rls_users_from_policies_table: {e}")
            return []
    
    def extract_source_table_from_query(self, view_query: str) -> tuple:
        """
        Extract base dataset and table from view query
        
        Returns: (dataset, table) or (None, None)
        """
        try:
            # Pattern: FROM `project.dataset.table`
            pattern = r'FROM\s+`[^`]*\.([^`\.]+)\.([^`\.]+)`'
            match = re.search(pattern, view_query, re.IGNORECASE)
            
            if match:
                dataset = match.group(1)
                table = match.group(2)
                return (dataset, table)
            
            return (None, None)
        except Exception as e:
            print(f"[ERROR] extract_source_table_from_query: {e}")
            return (None, None)
    
    def extract_filters_from_query(self, view_query: str) -> List[Dict]:
        """
        ✅ Extract filter conditions from view SQL
        
        This extracts RLS filters from the WHERE clause
        Note: This is a simplified parser, may not catch all complex cases
        """
        try:
            filters = []
            
            # Find WHERE clause
            where_match = re.search(r'\bWHERE\b', view_query, re.IGNORECASE)
            if not where_match:
                return filters
            
            where_clause = view_query[where_match.end():].strip()
            
            # Extract username/policy filter (this is for RLS metadata)
            # Example: usuario IN (SELECT username FROM policies_filters WHERE policy_name = 'xxx')
            
            # Try to find field used for RLS filtering
            field_match = re.search(r'(\w+)\s+IN\s*\(', where_clause, re.IGNORECASE)
            if field_match:
                field = field_match.group(1)
                filters.append({
                    'field': field,
                    'operator': 'IN',
                    'value': '(RLS policy filter)'
                })
            
            return filters
        except Exception as e:
            print(f"[ERROR] extract_filters_from_query: {e}")
            return []
    
    def list_rls_views(self, dataset: str) -> List[Dict]:
        """
        ✅ FIXED: List all RLS views for a dataset
        
        Now supports BOTH formats:
        - NEW format: Uses policies_filters table
        - OLD format: Uses RLS_METADATA in description
        """
        try:
            views = []
            
            # Search in both base dataset and views dataset
            datasets_to_search = [dataset]
            views_dataset = f"{dataset}{self.views_dataset_suffix}"
            
            try:
                self.client.get_dataset(views_dataset)
                datasets_to_search.append(views_dataset)
                print(f"[DEBUG] Found views dataset: {views_dataset}")
            except Exception:
                print(f"[DEBUG] No views dataset found for {dataset}")
            
            for ds in datasets_to_search:
                print(f"[DEBUG] Searching RLS views in: {ds}")
                
                try:
                    tables = list(self.client.list_tables(ds))
                except Exception as e:
                    print(f"[DEBUG] Cannot list tables in {ds}: {e}")
                    continue
                
                for table in tables:
                    table_ref = self.client.dataset(ds).table(table.table_id)
                    table_obj = self.client.get_table(table_ref)
                    
                    # Check if it's a view
                    if table_obj.table_type != 'VIEW':
                        continue
                    
                    # ✅ CRITICAL: Detect RLS view using NEW method
                    if not self.detect_rls_view(table_obj):
                        continue
                    
                    print(f"[DEBUG] 🔐 Found RLS view: {table.table_id}")
                    
                    # Extract source table from query
                    base_dataset, base_table = self.extract_source_table_from_query(table_obj.view_query)
                    
                    # ✅ Get users from policies_filters table (NEW format)
                    users = self.get_rls_users_from_policies_table(table.table_id)
                    
                    # Convert users to format expected by UI: ["user:email@example.com"]
                    users_formatted = [f"user:{u}" for u in users]
                    
                    # Extract filters from query
                    filters = self.extract_filters_from_query(table_obj.view_query)
                    
                    # Check for OLD format metadata
                    old_format_data = None
                    if table_obj.description and 'RLS_METADATA:' in table_obj.description:
                        try:
                            metadata_str = table_obj.description.split('RLS_METADATA:')[1]
                            old_format_data = json.loads(metadata_str)
                            
                            # Use old format data if available
                            if not users_formatted and old_format_data.get('users'):
                                users_formatted = old_format_data['users']
                            
                            if not filters and old_format_data.get('filters'):
                                filters = old_format_data['filters']
                            
                            if not base_dataset and old_format_data.get('base_dataset'):
                                base_dataset = old_format_data['base_dataset']
                            
                            if not base_table and old_format_data.get('base_table'):
                                base_table = old_format_data['base_table']
                        except Exception as e:
                            print(f"[DEBUG] Could not parse old format metadata: {e}")
                    
                    # Check if view has CLS (COLUMN_PROTECTION in description)
                    has_cls = bool(table_obj.description and 'COLUMN_PROTECTION:' in table_obj.description)
                    
                    # Determine view type
                    if has_cls:
                        view_type = 'HYBRID'  # RLS + CLS
                    else:
                        view_type = 'RLS'
                    
                    views.append({
                        'view_name': table.table_id,
                        'view_dataset': ds,
                        'base_dataset': base_dataset or dataset,
                        'base_table': base_table or 'Unknown',
                        'filters': filters,
                        'users': users_formatted,
                        'created_at': table_obj.created.strftime('%Y-%m-%d %H:%M') if table_obj.created else 'Unknown',
                        'modified_at': table_obj.modified.strftime('%Y-%m-%d %H:%M') if table_obj.modified else 'Unknown',
                        'description': table_obj.description or '',
                        'has_cls': has_cls,
                        'view_type': view_type
                    })
                    
                    print(f"[DEBUG] Added {view_type} view: {table.table_id} ({len(users_formatted)} users)")
            
            print(f"[DEBUG] ===== TOTAL RLS VIEWS FOUND: {len(views)} =====")
            return views
            
        except Exception as e:
            print(f"[ERROR] list_rls_views: {e}")
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
        """
        ✅ Update users with access to RLS view
        
        For NEW format views, this updates the policies_filters table
        """
        try:
            print(f"[DEBUG] update_rls_view_users: {view_name}, users: {users}")
            
            # Extract policy name from view name
            policy_base = view_name.replace('vw_', '')
            
            # Get existing users from policies_filters
            existing_users_query = f"""
            SELECT DISTINCT username, policy_name
            FROM `{self.project_id}.rls_manager.policies_filters`
            WHERE policy_name LIKE '%{policy_base}%'
            """
            
            existing_users = {}
            try:
                results = self.client.query(existing_users_query).result()
                for row in results:
                    existing_users[row.username] = row.policy_name
                print(f"[DEBUG] Found {len(existing_users)} existing users")
            except Exception as e:
                print(f"[DEBUG] No existing users found: {e}")
            
            # Parse users from format "user:email@example.com" to "email@example.com"
            new_users = []
            for u in users:
                if u.startswith('user:'):
                    new_users.append(u.replace('user:', ''))
                elif u.startswith('group:'):
                    # Groups not supported in NEW format yet
                    print(f"[WARNING] Groups not yet supported: {u}")
                else:
                    new_users.append(u)
            
            # Determine which policy_name to use
            if existing_users:
                # Use existing policy_name
                policy_name = list(existing_users.values())[0]
            else:
                # Create new policy_name
                policy_name = policy_base
            
            print(f"[DEBUG] Using policy_name: {policy_name}")
            
            # Delete old entries for this policy
            delete_query = f"""
            DELETE FROM `{self.project_id}.rls_manager.policies_filters`
            WHERE policy_name = '{policy_name}'
            """
            
            try:
                self.client.query(delete_query).result()
                print(f"[DEBUG] Deleted old entries")
            except Exception as e:
                print(f"[DEBUG] Could not delete old entries: {e}")
            
            # Insert new entries
            if new_users:
                for user in new_users:
                    insert_query = f"""
                    INSERT INTO `{self.project_id}.rls_manager.policies_filters`
                    (policy_name, username, filter_type, filter_value, created_at)
                    VALUES ('{policy_name}', '{user}', 'USER', '', CURRENT_TIMESTAMP())
                    """
                    
                    try:
                        self.client.query(insert_query).result()
                        print(f"[DEBUG] Inserted user: {user}")
                    except Exception as e:
                        print(f"[ERROR] Could not insert user {user}: {e}")
            
            # Also update OLD format metadata if present
            try:
                table_ref = self.client.dataset(view_dataset).table(view_name)
                table = self.client.get_table(table_ref)
                
                if table.description and 'RLS_METADATA:' in table.description:
                    metadata_str = table.description.split('RLS_METADATA:')[1]
                    metadata = json.loads(metadata_str)
                    
                    metadata['users'] = users
                    metadata['updated_at'] = datetime.utcnow().isoformat()
                    
                    desc_parts = table.description.split('RLS_METADATA:')[0]
                    table.description = f"{desc_parts}RLS_METADATA:{json.dumps(metadata)}"
                    self.client.update_table(table, ['description'])
                    print(f"[DEBUG] Updated OLD format metadata")
            except Exception as e:
                print(f"[DEBUG] No OLD format metadata to update: {e}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] update_rls_view_users: {e}")
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
        """
        ✅ Update filters for RLS view
        
        WARNING: For NEW format views with policies_filters, 
        this will preserve the RLS WHERE clause!
        """
        try:
            print(f"[DEBUG] update_rls_view_filters: {view_name}")
            
            # Get current view to preserve RLS WHERE clause
            table_ref = self.client.dataset(view_dataset).table(view_name)
            table = self.client.get_table(table_ref)
            
            # Check if this is a NEW format RLS view
            is_new_format = self.detect_rls_view(table)
            
            # Extract current WHERE clause if RLS
            current_where = None
            if is_new_format and table.view_query:
                where_match = re.search(r'\bWHERE\b', table.view_query, re.IGNORECASE)
                if where_match:
                    current_where = table.view_query[where_match.end():].strip()
                    if current_where.endswith(';'):
                        current_where = current_where[:-1].strip()
            
            # Build new WHERE clause from filters
            where_clauses = []
            for f in filters:
                field = f['field']
                op = f.get('operator', '=')
                value = f['value']
                
                if isinstance(value, str) and not value.startswith('('):
                    where_clauses.append(f"{field} {op} '{value}'")
                else:
                    where_clauses.append(f"{field} {op} {value}")
            
            # Combine with RLS WHERE if needed
            if current_where and is_new_format:
                # Keep existing RLS WHERE clause
                final_where = current_where
                print(f"[DEBUG] Preserving RLS WHERE clause")
            elif where_clauses:
                final_where = " AND ".join(where_clauses)
            else:
                final_where = "TRUE"
            
            # Rebuild view
            view_full_name = f"{self.project_id}.{view_dataset}.{view_name}"
            
            view_sql = f"""
            CREATE OR REPLACE VIEW `{view_full_name}` AS
            SELECT *
            FROM `{self.project_id}.{base_dataset}.{base_table}`
            WHERE {final_where};
            """
            
            print(f"[DEBUG] Updating view SQL")
            self.client.query(view_sql).result()
            
            # Update OLD format metadata if present
            try:
                table_ref = self.client.dataset(view_dataset).table(view_name)
                table = self.client.get_table(table_ref)
                
                if table.description and 'RLS_METADATA:' in table.description:
                    metadata_str = table.description.split('RLS_METADATA:')[1]
                    metadata = json.loads(metadata_str)
                    
                    metadata['filters'] = filters
                    metadata['updated_at'] = datetime.utcnow().isoformat()
                    
                    desc_parts = table.description.split('RLS_METADATA:')[0]
                    table.description = f"{desc_parts}RLS_METADATA:{json.dumps(metadata)}"
                    self.client.update_table(table, ['description'])
            except Exception as e:
                print(f"[DEBUG] No OLD format metadata to update: {e}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] update_rls_view_filters: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_rls_view(self, view_dataset: str, view_name: str) -> bool:
        """Delete an RLS view"""
        try:
            table_ref = self.client.dataset(view_dataset).table(view_name)
            self.client.delete_table(table_ref)
            
            # Also delete entries from policies_filters table
            policy_base = view_name.replace('vw_', '')
            
            delete_query = f"""
            DELETE FROM `{self.project_id}.rls_manager.policies_filters`
            WHERE policy_name LIKE '%{policy_base}%'
            """
            
            try:
                self.client.query(delete_query).result()
                print(f"[DEBUG] Deleted policies_filters entries")
            except Exception as e:
                print(f"[DEBUG] Could not delete policies_filters entries: {e}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] delete_rls_view: {e}")
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
    
    # ==================== CREATE METHOD (keep for backward compatibility) ====================
    
    def create_rls_view(
        self,
        view_name: str,
        base_dataset: str,
        base_table: str,
        filters: List[Dict],
        users: List[str],
        description: str = ""
    ) -> Optional[str]:
        """
        Create a new RLS-protected view (OLD format with RLS_METADATA)
        
        NOTE: This creates OLD format views. 
        For NEW format, use the RLS creation flow in create_rls_users.py
        """
        try:
            views_dataset = self.get_views_dataset(base_dataset)
            view_full_name = f"{self.project_id}.{views_dataset}.{view_name}"
            
            # Build WHERE clause
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
            
            # Create VIEW
            view_sql = f"""
            CREATE OR REPLACE VIEW `{view_full_name}` AS
            SELECT *
            FROM `{self.project_id}.{base_dataset}.{base_table}`
            WHERE {where_clause};
            """
            
            self.client.query(view_sql).result()
            
            # Update description with metadata (OLD format)
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
            
            dataset_ref = self.client.dataset(base_dataset)
            dataset = self.client.get_dataset(dataset_ref)
            
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
            
            access_entries = list(dataset.access_entries or [])
            
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
