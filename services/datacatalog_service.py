"""
Data Catalog Service for CLS
Manages taxonomies and policy tags in Google Cloud Data Catalog
"""

from google.cloud import datacatalog_v1
from typing import List, Dict, Optional
import re


class DataCatalogService:
    """Service for Data Catalog operations"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.client = datacatalog_v1.PolicyTagManagerClient()
        self.parent = f"projects/{project_id}/locations/{location}"
    
    # ==================== TAXONOMIES ====================
    
    def list_taxonomies(self) -> List[Dict]:
        """List all taxonomies in the project"""
        try:
            request = datacatalog_v1.ListTaxonomiesRequest(parent=self.parent)
            taxonomies = self.client.list_taxonomies(request=request)
            
            result = []
            for taxonomy in taxonomies:
                # Contar tags de forma segura para não quebrar se falhar
                try:
                    tags = self.list_policy_tags(taxonomy.name)
                    tag_count = len(tags)
                except Exception as tag_error:
                    print(f"Warning: Could not count tags for {taxonomy.display_name}: {tag_error}")
                    tag_count = 0
                
                result.append({
                    "name": taxonomy.name,
                    "display_name": taxonomy.display_name,
                    "description": taxonomy.description,
                    "tag_count": tag_count,
                    "activated_policy_types": list(taxonomy.activated_policy_types)
                })
            
            return result
        except Exception as e:
            print(f"Error listing taxonomies: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def create_taxonomy(self, display_name: str, description: str = "") -> Optional[str]:
        """Create a new taxonomy"""
        try:
            taxonomy = datacatalog_v1.Taxonomy(
                display_name=display_name,
                description=description,
                activated_policy_types=[
                    datacatalog_v1.Taxonomy.PolicyType.FINE_GRAINED_ACCESS_CONTROL
                ]
            )
            
            request = datacatalog_v1.CreateTaxonomyRequest(
                parent=self.parent,
                taxonomy=taxonomy
            )
            
            result = self.client.create_taxonomy(request=request)
            return result.name
            
        except Exception as e:
            print(f"Error creating taxonomy: {e}")
            return None
    
    def delete_taxonomy(self, taxonomy_name: str) -> bool:
        """Delete a taxonomy"""
        try:
            request = datacatalog_v1.DeleteTaxonomyRequest(name=taxonomy_name)
            self.client.delete_taxonomy(request=request)
            return True
        except Exception as e:
            print(f"Error deleting taxonomy: {e}")
            return False
    
    def update_taxonomy(self, taxonomy_name: str, display_name: str = None, 
                       description: str = None) -> bool:
        """Update a taxonomy"""
        try:
            request = datacatalog_v1.GetTaxonomyRequest(name=taxonomy_name)
            taxonomy = self.client.get_taxonomy(request=request)
            
            if display_name:
                taxonomy.display_name = display_name
            if description is not None:
                taxonomy.description = description
            
            update_request = datacatalog_v1.UpdateTaxonomyRequest(taxonomy=taxonomy)
            self.client.update_taxonomy(request=update_request)
            return True
            
        except Exception as e:
            print(f"Error updating taxonomy: {e}")
            return False
    
    # ==================== POLICY TAGS ====================
    
    def list_policy_tags(self, taxonomy_name: str) -> List[Dict]:
        """List all policy tags in a taxonomy"""
        try:
            request = datacatalog_v1.ListPolicyTagsRequest(parent=taxonomy_name)
            tags = self.client.list_policy_tags(request=request)
            
            result = []
            for tag in tags:
                # Contar child tags de forma segura
                try:
                    child_tags = list(self.client.list_policy_tags(
                        request=datacatalog_v1.ListPolicyTagsRequest(parent=tag.name)
                    ))
                    child_count = len(child_tags)
                except Exception:
                    child_count = 0
                
                result.append({
                    "name": tag.name,
                    "display_name": tag.display_name,
                    "description": tag.description,
                    "parent_tag": tag.parent_policy_tag if tag.parent_policy_tag else None,
                    "child_count": child_count
                })
            
            return result
        except Exception as e:
            print(f"Error listing policy tags: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def create_policy_tag(self, taxonomy_name: str, display_name: str, 
                         description: str = "", parent_tag: str = None) -> Optional[str]:
        """Create a new policy tag"""
        try:
            policy_tag = datacatalog_v1.PolicyTag(
                display_name=display_name,
                description=description
            )
            
            if parent_tag:
                policy_tag.parent_policy_tag = parent_tag
            
            request = datacatalog_v1.CreatePolicyTagRequest(
                parent=taxonomy_name,
                policy_tag=policy_tag
            )
            
            result = self.client.create_policy_tag(request=request)
            return result.name
            
        except Exception as e:
            print(f"Error creating policy tag: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_policy_tag(self, tag_name: str) -> bool:
        """Delete a policy tag"""
        try:
            request = datacatalog_v1.DeletePolicyTagRequest(name=tag_name)
            self.client.delete_policy_tag(request=request)
            return True
        except Exception as e:
            print(f"Error deleting policy tag: {e}")
            return False
    
    def update_policy_tag(self, tag_name: str, display_name: str = None,
                         description: str = None) -> bool:
        """Update a policy tag"""
        try:
            request = datacatalog_v1.GetPolicyTagRequest(name=tag_name)
            tag = self.client.get_policy_tag(request=request)
            
            if display_name:
                tag.display_name = display_name
            if description is not None:
                tag.description = description
            
            update_request = datacatalog_v1.UpdatePolicyTagRequest(policy_tag=tag)
            self.client.update_policy_tag(request=update_request)
            return True
            
        except Exception as e:
            print(f"Error updating policy tag: {e}")
            return False
    
    # ==================== IAM PERMISSIONS ====================
    
    def get_tag_iam_policy(self, tag_name: str) -> Dict:
        """Get IAM policy for a policy tag"""
        try:
            request = datacatalog_v1.GetIamPolicyRequest(resource=tag_name)
            policy = self.client.get_iam_policy(request=request)
            
            bindings = []
            for binding in policy.bindings:
                bindings.append({
                    "role": binding.role,
                    "members": list(binding.members)
                })
            
            return {
                "bindings": bindings,
                "etag": policy.etag
            }
            
        except Exception as e:
            print(f"Error getting IAM policy: {e}")
            return {"bindings": [], "etag": ""}
    
    def set_tag_iam_policy(self, tag_name: str, members: List[str], 
                          role: str = "roles/datacatalog.categoryFineGrainedReader") -> bool:
        """Set IAM policy for a policy tag"""
        try:
            from google.iam.v1 import policy_pb2
            
            binding = policy_pb2.Binding(
                role=role,
                members=members
            )
            
            policy = policy_pb2.Policy(bindings=[binding])
            
            request = datacatalog_v1.SetIamPolicyRequest(
                resource=tag_name,
                policy=policy
            )
            
            self.client.set_iam_policy(request=request)
            return True
            
        except Exception as e:
            print(f"Error setting IAM policy: {e}")
            return False
