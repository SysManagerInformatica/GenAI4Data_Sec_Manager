"""
Audit Service
Handles audit logging for all security operations
"""

from google.cloud import bigquery
from datetime import datetime
import json
import os


class AuditService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        self.table_id = f"{project_id}.rls_manager.audit_logs"
        
        # Get user email from environment or default
        self.user_email = os.getenv('USER_EMAIL', 'system@genai4datasec.com')
    
    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_name: str,
        status: str = 'SUCCESS',
        taxonomy: str = None,
        details: dict = None,
        error_message: str = None
    ):
        """
        Log an audit event
        
        Args:
            action: Type of action (CREATE_TAXONOMY, DELETE_TAG, etc.)
            resource_type: Type of resource (TAXONOMY, POLICY_TAG, COLUMN, etc.)
            resource_name: Name of the resource
            status: SUCCESS or FAILED
            taxonomy: Related taxonomy (if applicable)
            details: Additional details as dict
            error_message: Error message if status is FAILED
        """
        try:
            # Prepare row
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_email": self.user_email,
                "action": action,
                "resource_type": resource_type,
                "resource_name": resource_name,
                "taxonomy": taxonomy,
                "details": json.dumps(details) if details else None,
                "status": status,
                "error_message": error_message
            }
            
            # Insert row
            errors = self.client.insert_rows_json(self.table_id, [row])
            
            if errors:
                print(f"⚠️ Error logging audit: {errors}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to log audit: {e}")
            return False
    
    def get_recent_logs(self, limit: int = 50, filters: dict = None):
        """
        Get recent audit logs with optional filters
        
        Args:
            limit: Maximum number of logs to return
            filters: Optional filters (date_range, action, user_email)
        
        Returns:
            List of log entries
        """
        try:
            # Build query
            query = f"""
            SELECT 
                timestamp,
                user_email,
                action,
                resource_type,
                resource_name,
                taxonomy,
                details,
                status,
                error_message
            FROM `{self.table_id}`
            WHERE 1=1
            """
            
            # Apply filters
            if filters:
                if filters.get('date_range'):
                    date_range = filters['date_range']
                    if date_range == 'last_hour':
                        query += " AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)"
                    elif date_range == 'today':
                        query += " AND DATE(timestamp) = CURRENT_DATE()"
                    elif date_range == 'last_7_days':
                        query += " AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)"
                    elif date_range == 'last_30_days':
                        query += " AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)"
                
                if filters.get('action') and filters['action'] != 'ALL':
                    query += f" AND action = '{filters['action']}'"
                
                if filters.get('user_email') and filters['user_email'] != 'ALL':
                    query += f" AND user_email = '{filters['user_email']}'"
            
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            # Execute query
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert to list of dicts
            logs = []
            for row in results:
                log_entry = {
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None,
                    'user_email': row.user_email,
                    'action': row.action,
                    'resource_type': row.resource_type,
                    'resource_name': row.resource_name,
                    'taxonomy': row.taxonomy,
                    'details': json.loads(row.details) if row.details else {},
                    'status': row.status,
                    'error_message': row.error_message
                }
                logs.append(log_entry)
            
            return logs
            
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
            return []
    
    def get_statistics(self, date_range: str = 'last_7_days'):
        """
        Get audit statistics
        
        Returns:
            Dict with statistics
        """
        try:
            # Date filter
            date_filter = ""
            if date_range == 'last_hour':
                date_filter = "timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)"
            elif date_range == 'today':
                date_filter = "DATE(timestamp) = CURRENT_DATE()"
            elif date_range == 'last_7_days':
                date_filter = "timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)"
            elif date_range == 'last_30_days':
                date_filter = "timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)"
            
            query = f"""
            SELECT
                COUNT(*) as total_actions,
                COUNTIF(status = 'SUCCESS') as successful_actions,
                COUNTIF(status = 'FAILED') as failed_actions,
                COUNT(DISTINCT user_email) as unique_users,
                COUNT(DISTINCT action) as unique_action_types
            FROM `{self.table_id}`
            WHERE {date_filter}
            """
            
            query_job = self.client.query(query)
            result = list(query_job.result())[0]
            
            return {
                'total_actions': result.total_actions,
                'successful_actions': result.successful_actions,
                'failed_actions': result.failed_actions,
                'unique_users': result.unique_users,
                'unique_action_types': result.unique_action_types,
                'success_rate': round((result.successful_actions / result.total_actions * 100) if result.total_actions > 0 else 0, 1)
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def get_top_actions(self, limit: int = 5, date_range: str = 'last_7_days'):
        """Get most common actions"""
        try:
            date_filter = ""
            if date_range == 'last_7_days':
                date_filter = "WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)"
            
            query = f"""
            SELECT 
                action,
                COUNT(*) as count
            FROM `{self.table_id}`
            {date_filter}
            GROUP BY action
            ORDER BY count DESC
            LIMIT {limit}
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [{'action': row.action, 'count': row.count} for row in results]
            
        except Exception as e:
            print(f"❌ Error getting top actions: {e}")
            return []
    
    def get_active_users(self, limit: int = 5, date_range: str = 'last_7_days'):
        """Get most active users"""
        try:
            date_filter = ""
            if date_range == 'last_7_days':
                date_filter = "WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)"
            
            query = f"""
            SELECT 
                user_email,
                COUNT(*) as action_count
            FROM `{self.table_id}`
            {date_filter}
            GROUP BY user_email
            ORDER BY action_count DESC
            LIMIT {limit}
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [{'user_email': row.user_email, 'action_count': row.action_count} for row in results]
            
        except Exception as e:
            print(f"❌ Error getting active users: {e}")
            return []
