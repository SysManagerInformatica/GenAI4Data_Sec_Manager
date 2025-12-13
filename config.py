# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# "IMPORTANT: This application is a prototype and should be used for experimental purposes only.
# It is not intended for production use. 
# This software is provided 'as is' without warranty of any kind, express or implied, including but not limited to the warranties 
# of merchantability, fitness for a particular purpose and noninfringement. 
# In no event shall Google or the developers be liable for any claim, damages or other liability, whether in an action of contract, 
# tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software. 
# Google is not responsible for the functionality, reliability, or security of this prototype. 
# Use of this tool is at your own discretion and risk."

"""
Configuration for RLS/CLS Manager
VERSION: 2.0 - Added RLS Views Support
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
