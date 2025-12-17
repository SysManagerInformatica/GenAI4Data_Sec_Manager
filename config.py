"""
================================================================================
  GenAI4Data Security Manager
  Module: Global Configuration Settings
================================================================================
  Version:      2.0.0
  Release Date: 2024-12-15
  Author:       Lucas Carvalhal - Sys Manager
  Company:      Sys Manager Informática
  
  Description:
  Central configuration management for RLS/CLS Security Manager including
  Google Cloud project settings, dataset names, table references, and
  RLS views architecture configuration.
================================================================================
"""

import os

class Config:
    # Google Cloud Project Configuration
    PROJECT_ID = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')
    LOCATION = 'us-central1'
    
    # RLS Manager Configuration
    RLS_MANAGER_DATASET = 'rls_manager'
    POLICY_TABLE = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.policies'
    FILTER_TABLE = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.policies_filters'
    
    # Application Configuration
    APP_TITLE = 'GenAI4Data - Security Manager'
    APP_VERSION = '2.0.0'
    
    # Additional tables
    USERS_TABLE = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.users'
    AUDIT_LOGS_TABLE = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.audit_logs'
    
    # ==================== NEW: RLS Views Architecture ====================
    # Views são criadas em datasets separados com sufixo "_views"
    # Exemplo: demo_rls_cls → demo_rls_cls_views
    RLS_VIEWS_REGISTRY = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.rls_views_registry'
    VIEWS_DATASET_SUFFIX = '_views'
    
    # View Types
    VIEW_TYPE_RLS = 'RLS_VIEW'  # View com RLS aplicado
    VIEW_TYPE_CLS = 'CLS_VIEW'  # View com CLS/masking
    VIEW_TYPE_HYBRID = 'HYBRID_VIEW'  # View com RLS + CLS
