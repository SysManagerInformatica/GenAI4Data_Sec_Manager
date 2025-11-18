"""
BigQuery CLS Service
Manages BigQuery operations and policy tag application
"""

from google.cloud import bigquery
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryCLSService:
    """Service for BigQuery CLS operations"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        logger.info(f"BigQueryCLSService initialized for project: {project_id}")
    
    # ==================== DATASETS ====================
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets in the project"""
        try:
            datasets = list(self.client.list_datasets())
            
            result = []
            for dataset in datasets:
                dataset_ref = self.client.get_dataset(dataset.reference)
                tables = list(self.client.list_tables(dataset.reference))
                
                result.append({
                    "dataset_id": dataset.dataset_id,
                    "project": dataset.project,
                    "full_id": f"{dataset.project}.{dataset.dataset_id}",
                    "location": dataset_ref.location,
                    "description": dataset_ref.description or "",
                    "table_count": len(tables)
                })
            
            return result
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []
    
    # ==================== TABLES ====================
    
    def list_tables(self, dataset_id: str) -> List[Dict]:
        """List all tables in a dataset"""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            tables = list(self.client.list_tables(dataset_ref))
            
            result = []
            for table in tables:
                table_ref = self.client.get_table(table.reference)
                
                result.append({
                    "table_id": table.table_id,
                    "dataset_id": dataset_id,
                    "full_id": f"{self.project_id}.{dataset_id}.{table.table_id}",
                    "table_type": table.table_type,
                    "num_rows": table_ref.num_rows,
                    "description": table_ref.description or ""
                })
            
            return result
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    # ==================== SCHEMA & COLUMNS ====================
    
    def get_table_schema(self, dataset_id: str, table_id: str) -> List[Dict]:
        """Get complete schema of a table"""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            result = []
            for field in table.schema:
                policy_tags = []
                if hasattr(field, 'policy_tags') and field.policy_tags:
                    policy_tags = field.policy_tags.names if hasattr(field.policy_tags, 'names') else []
                
                result.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or "",
                    "policy_tags": policy_tags
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return []
    
    def get_columns_with_tags(self, dataset_id: str, table_id: str) -> Dict[str, List[str]]:
        """Return dictionary of columns and their policy tags"""
        try:
            schema = self.get_table_schema(dataset_id, table_id)
            
            result = {}
            for column in schema:
                if column['policy_tags']:
                    result[column['name']] = column['policy_tags']
            
            return result
        except Exception as e:
            logger.error(f"Error getting columns with tags: {e}")
            return {}
    
    # ==================== APPLY TAGS ====================
    
    def apply_tag_to_column(self, dataset_id: str, table_id: str, 
                           column_name: str, tag_name: str) -> bool:
        """Apply a policy tag to a column"""
        try:
            logger.info("="*60)
            logger.info("APPLYING TAG")
            logger.info(f"Dataset: {dataset_id}")
            logger.info(f"Table: {table_id}")
            logger.info(f"Column: {column_name}")
            logger.info(f"Tag: {tag_name}")
            logger.info("="*60)
            
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            # Build new schema
            new_schema = []
            for field in table.schema:
                if field.name == column_name:
                    # Apply tag to target column
                    new_field = bigquery.SchemaField(
                        name=field.name,
                        field_type=field.field_type,
                        mode=field.mode,
                        description=field.description,
                        policy_tags=bigquery.PolicyTagList(names=[tag_name])
                    )
                    new_schema.append(new_field)
                    logger.info(f"✅ Applied tag to column: {column_name}")
                else:
                    # Keep other fields as-is
                    new_schema.append(field)
            
            # Update table
            table.schema = new_schema
            self.client.update_table(table, ["schema"])
            
            logger.info(f"✅ SUCCESS: Tag applied to {dataset_id}.{table_id}.{column_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERROR applying tag: {str(e)}", exc_info=True)
            return False
    
    def remove_tag_from_column(self, dataset_id: str, table_id: str, 
                               column_name: str) -> bool:
        """Remove policy tags from a column"""
        try:
            logger.info("="*60)
            logger.info("REMOVING TAG - START")
            logger.info(f"Dataset: {dataset_id}")
            logger.info(f"Table: {table_id}")
            logger.info(f"Column: {column_name}")
            logger.info("="*60)
            
            # Get current table
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            # Check current tags
            logger.info("Current schema fields:")
            for field in table.schema:
                if field.name == column_name:
                    has_tags = hasattr(field, 'policy_tags') and field.policy_tags
                    if has_tags:
                        logger.info(f"  - {field.name}: HAS TAGS = {field.policy_tags.names}")
                    else:
                        logger.info(f"  - {field.name}: NO TAGS")
            
            # Build new schema WITHOUT tags on target column
            new_schema = []
            found_target = False
            
            for field in table.schema:
                if field.name == column_name:
                    found_target = True
                    # Create new field with EMPTY PolicyTagList to remove tags
                    new_field = bigquery.SchemaField(
                        name=field.name,
                        field_type=field.field_type,
                        mode=field.mode,
                        description=field.description,
                        policy_tags=bigquery.PolicyTagList(names=[])  # EMPTY list = REMOVE tags
                    )
                    new_schema.append(new_field)
                    logger.info(f"  ✅ Rebuilt column {column_name} with EMPTY PolicyTagList")
                else:
                    # Keep other fields unchanged
                    new_schema.append(field)
            
            if not found_target:
                logger.error(f"  ❌ Column {column_name} not found in schema!")
                return False
            
            # Update table with new schema
            logger.info("Updating table schema...")
            table.schema = new_schema
            updated_table = self.client.update_table(table, ["schema"])
            logger.info("  ✅ Schema updated in BigQuery")
            
            # VERIFY the tag was actually removed
            logger.info("Verifying tag removal...")
            verification_table = self.client.get_table(table_ref)
            
            for field in verification_table.schema:
                if field.name == column_name:
                    has_tags = hasattr(field, 'policy_tags') and field.policy_tags
                    if has_tags:
                        logger.error(f"  ❌ VERIFICATION FAILED: Tags still present!")
                        logger.error(f"     Remaining tags: {field.policy_tags.names}")
                        return False
                    else:
                        logger.info(f"  ✅ VERIFICATION PASSED: No tags found")
                        logger.info(f"✅ SUCCESS: Tag removed from {dataset_id}.{table_id}.{column_name}")
                        logger.info("="*60)
                        return True
            
            logger.error(f"  ❌ Column not found in verification")
            return False
            
        except Exception as e:
            logger.error(f"❌ ERROR removing tag: {str(e)}", exc_info=True)
            return False
    
    # ==================== STATISTICS ====================
    
    def get_tagged_columns_count(self, dataset_id: str, table_id: str) -> Dict[str, int]:
        """Return statistics of tagged columns"""
        try:
            schema = self.get_table_schema(dataset_id, table_id)
            
            total_columns = len(schema)
            tagged_columns = sum(1 for col in schema if col['policy_tags'])
            
            return {
                "total_columns": total_columns,
                "tagged_columns": tagged_columns,
                "untagged_columns": total_columns - tagged_columns,
                "percentage_tagged": round((tagged_columns / total_columns * 100), 2) if total_columns > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_columns": 0,
                "tagged_columns": 0,
                "untagged_columns": 0,
                "percentage_tagged": 0
            }
