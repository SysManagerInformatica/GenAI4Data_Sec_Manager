"""
Sistema de Traduções Multi-Idiomas
Suporta: Português (pt), English (en), Español (es)

VERSÃO: 2.1 - Completa
Data: 05/12/2024
Autor: Lucas Carvalhal - Sys Manager
"""

from typing import Dict, Any, Optional

# ============================================
# TRANSLATIONS DICTIONARY
# ============================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ==================== PORTUGUÊS ====================
    'pt': {
        # Common
        'app_name': 'GenAI4Data',
        'app_subtitle': 'Gerenciador de Segurança',
        
        # Login
        'login_title': 'GenAI4Data',
        'login_subtitle': 'Sistema de Segurança Integrado',  # ← MODIFICADO
        'login_button': 'Entrar com Google',
        'login_loading': 'CARREGANDO SISTEMA...',  # ← MODIFICADO
        'login_powered': 'Desenvolvido por Sys Manager',
        'login_partner': 'Partner Google Cloud',
        
        # Language Selector  # ← NOVO
        'lang_selector_title': 'Idioma',
        'lang_pt': 'Português',
        'lang_en': 'English',
        'lang_es': 'Español',
        
        # Header
        'header_logout': 'Sair',
        'header_welcome': 'Bem-vindo',
        'header_role': 'Função',
        'header_user_role': 'Sua Função: {role}',  # ← NOVO
        
        # Navigation (Main Sections)
        'nav_home': 'Início',
        'nav_rls': 'Row-Level Security',
        'nav_cls': 'Column-Level Security',
        'nav_iam': 'Gerenciamento IAM',
        'nav_audit': 'Auditoria',
        
        # Navigation - RLS Submenu  # ← NOVO
        'menu_rls_users': 'Criar por Usuários',
        'menu_rls_groups': 'Criar por Grupos',
        'menu_rls_assign_users': 'Atribuir Usuários à Política',
        'menu_rls_assign_values': 'Atribuir Valores ao Grupo',
        
        # Navigation - CLS Submenu  # ← NOVO
        'menu_cls_taxonomies': 'Gerenciar Taxonomias',
        'menu_cls_tags': 'Gerenciar Policy Tags',
        'menu_cls_apply': 'Aplicar Tags em Colunas',
        'menu_cls_iam': 'Permissões de Policy Tags',
        'menu_cls_create_view': 'Criar View Protegida',
        'menu_cls_manage_views': 'Gerenciar Views Protegidas',
        'menu_cls_schema': 'Navegador de Schemas',
        
        # Navigation - IAM Submenu  # ← NOVO
        'menu_iam_dataset': 'Gerenciador IAM de Dataset',
        'menu_iam_project': 'Gerenciador IAM de Projeto',
        'menu_iam_control': 'Controlar Acesso',
        
        # Navigation - Audit Submenu  # ← NOVO
        'menu_audit_logs': 'Visualizar Logs de Auditoria',
        
        # Home
        'home_welcome': 'Bem-vindo de volta,',  # ← MODIFICADO
        'home_subtitle': 'Gerencie políticas RLS, CLS e permissões IAM de forma centralizada',
        'home_quick_start': 'Início Rápido',  # ← NOVO
        
        # Home - Feature Cards
        'home_rls_title': 'Row-Level Security',
        'home_rls_desc': 'Controle o acesso a linhas específicas com base em usuários ou grupos',
        'home_cls_title': 'Column-Level Security',
        'home_cls_desc': 'Proteja colunas sensíveis com policy tags e taxonomias',
        'home_masking_title': 'Data Masking',
        'home_masking_desc': 'Crie views protegidas com mascaramento dinâmico de dados',
        'home_iam_title': 'IAM Policy Control',
        'home_iam_desc': 'Gerencie permissões em datasets, projetos e recursos',
        'home_audit_title': 'Audit & Compliance',
        'home_audit_desc': 'Rastreie todas as operações de segurança e gere relatórios',
        
        # RLS - Create for Users
        'rls_users_title': 'Criar Política RLS para Usuários',
        'rls_users_desc': 'Crie políticas de segurança baseadas em usuários individuais',
        'rls_users_dataset': 'ID do Dataset',
        'rls_users_table': 'Nome da Tabela',
        'rls_users_policy_name': 'Nome da Política',
        'rls_users_filter_column': 'Coluna de Filtro',
        'rls_users_grantees': 'Usuários Autorizados',
        'rls_users_grantees_hint': 'Insira emails separados por vírgula',
        'rls_users_create': 'Criar Política',
        'rls_users_success': 'Política criada com sucesso!',
        'rls_users_error': 'Erro ao criar política: {error}',
        
        # RLS - Create for Groups
        'rls_groups_title': 'Criar Política RLS para Grupos',
        'rls_groups_desc': 'Crie políticas de segurança baseadas em grupos',
        'rls_groups_group_email': 'Email do Grupo',
        'rls_groups_filter_value': 'Valor do Filtro',
        'rls_groups_filter_column': 'Coluna de Filtro',
        
        # CLS - Taxonomies
        'cls_tax_title': 'Gerenciar Taxonomias',
        'cls_tax_desc': 'Crie e organize taxonomias no Data Catalog',
        'cls_tax_create': 'Criar Taxonomia',
        'cls_tax_name': 'Nome',
        'cls_tax_description': 'Descrição',
        'cls_tax_tags_count': 'Tags',
        'cls_tax_edit': 'Editar',
        'cls_tax_delete': 'Deletar',
        'cls_tax_confirm_delete': 'Tem certeza que deseja deletar esta taxonomia?',
        'cls_tax_success_create': 'Taxonomia criada com sucesso!',
        'cls_tax_success_delete': 'Taxonomia deletada com sucesso!',
        
        # CLS - Policy Tags
        'cls_tags_title': 'Gerenciar Policy Tags',
        'cls_tags_desc': 'Crie e organize policy tags hierárquicas',
        'cls_tags_taxonomy': 'Taxonomia',
        'cls_tags_create': 'Criar Tag',
        'cls_tags_parent': 'Tag Pai (Opcional)',
        'cls_tags_hierarchy': 'Hierarquia',
        'cls_tags_no_parent': 'Nenhuma (Tag Raiz)',
        
        # CLS - Apply Tags
        'cls_apply_title': 'Aplicar Tags em Colunas',
        'cls_apply_desc': 'Aplique policy tags em colunas de tabelas',
        'cls_apply_dataset': 'Dataset',
        'cls_apply_table': 'Tabela',
        'cls_apply_column': 'Coluna',
        'cls_apply_tag': 'Policy Tag',
        'cls_apply_current_tag': 'Tag Atual',
        'cls_apply_no_tag': 'Sem tag',
        'cls_apply_button': 'Aplicar Tag',
        'cls_apply_remove': 'Remover Tag',
        'cls_apply_stats': 'Estatísticas',
        'cls_apply_total_columns': 'Total de Colunas',
        'cls_apply_protected': 'Colunas Protegidas',
        'cls_apply_unprotected': 'Colunas Desprotegidas',
        'cls_apply_coverage': 'Cobertura',
        
        # CLS - Schema Browser
        'cls_schema_title': 'Navegador de Schemas',
        'cls_schema_desc': 'Visualize schemas e tags aplicadas',
        'cls_schema_select_dataset': 'Selecione um Dataset',
        'cls_schema_tables': 'Tabelas',
        'cls_schema_columns': 'Colunas',
        'cls_schema_type': 'Tipo',
        'cls_schema_tag': 'Tag',
        
        # IAM
        'iam_dataset_title': 'Gerenciar Permissões de Dataset',
        'iam_project_title': 'Gerenciar Permissões de Projeto',
        'iam_control_title': 'Controle de Acesso',
        'iam_member': 'Membro',
        'iam_role': 'Função',
        'iam_add': 'Adicionar',
        'iam_remove': 'Remover',
        'iam_current_permissions': 'Permissões Atuais',
        
        # Audit
        'audit_title': 'Logs de Auditoria',
        'audit_desc': 'Visualize todas as operações de segurança',
        'audit_user': 'Usuário',
        'audit_operation': 'Operação',
        'audit_resource': 'Recurso',
        'audit_timestamp': 'Data/Hora',
        'audit_status': 'Status',
        'audit_details': 'Detalhes',
        'audit_filter_user': 'Filtrar por Usuário',
        'audit_filter_operation': 'Filtrar por Operação',
        'audit_filter_date': 'Filtrar por Data',
        'audit_export': 'Exportar Relatório',
        
        # Common buttons
        'btn_create': 'Criar',
        'btn_edit': 'Editar',
        'btn_delete': 'Deletar',
        'btn_cancel': 'Cancelar',
        'btn_save': 'Salvar',
        'btn_apply': 'Aplicar',
        'btn_remove': 'Remover',
        'btn_close': 'Fechar',
        'btn_refresh': 'Atualizar',
        'btn_export': 'Exportar',
        'btn_back': 'Voltar',
        
        # Messages
        'msg_success': 'Operação realizada com sucesso!',
        'msg_error': 'Erro: {error}',
        'msg_loading': 'Carregando...',
        'msg_no_data': 'Nenhum dado disponível',
        'msg_confirm': 'Tem certeza?',
        
        # Footer
        'footer_version': 'Versão',
        'footer_powered': 'Desenvolvido por',
        'footer_session': 'Sessão ativa como',
    },
    
    # ==================== ENGLISH ====================
    'en': {
        # Common
        'app_name': 'GenAI4Data',
        'app_subtitle': 'Security Manager',
        
        # Login
        'login_title': 'GenAI4Data',
        'login_subtitle': 'Seamless Security System',
        'login_button': 'Sign in with Google',
        'login_loading': 'LOADING SYSTEM...',
        'login_powered': 'Powered by Sys Manager',
        'login_partner': 'Partner Google Cloud',
        
        # Language Selector  # ← NOVO
        'lang_selector_title': 'Language',
        'lang_pt': 'Português',
        'lang_en': 'English',
        'lang_es': 'Español',
        
        # Header
        'header_logout': 'Logout',
        'header_welcome': 'Welcome',
        'header_role': 'Role',
        'header_user_role': 'Your Role: {role}',  # ← NOVO
        
        # Navigation (Main Sections)
        'nav_home': 'Home',
        'nav_rls': 'Row-Level Security',
        'nav_cls': 'Column-Level Security',
        'nav_iam': 'IAM Management',
        'nav_audit': 'Audit',
        
        # Navigation - RLS Submenu  # ← NOVO
        'menu_rls_users': 'Create for Users',
        'menu_rls_groups': 'Create for Groups',
        'menu_rls_assign_users': 'Assign Users to Policy',
        'menu_rls_assign_values': 'Assign Values to Group',
        
        # Navigation - CLS Submenu  # ← NOVO
        'menu_cls_taxonomies': 'Manage Taxonomies',
        'menu_cls_tags': 'Manage Policy Tags',
        'menu_cls_apply': 'Apply Tags to Columns',
        'menu_cls_iam': 'Policy Tag Permissions',
        'menu_cls_create_view': 'Create Protected View',
        'menu_cls_manage_views': 'Manage Protected Views',
        'menu_cls_schema': 'Schema Browser',
        
        # Navigation - IAM Submenu  # ← NOVO
        'menu_iam_dataset': 'Dataset IAM Manager',
        'menu_iam_project': 'Project IAM Manager',
        'menu_iam_control': 'Control Access',
        
        # Navigation - Audit Submenu  # ← NOVO
        'menu_audit_logs': 'View Audit Logs',
        
        # Home
        'home_welcome': 'Welcome back,',  # ← MODIFICADO
        'home_subtitle': 'Manage RLS policies, CLS tags, and IAM permissions in one place',
        'home_quick_start': 'Quick Start',  # ← NOVO
        
        # Home - Feature Cards
        'home_rls_title': 'Row-Level Security',
        'home_rls_desc': 'Control access to specific rows based on users or groups',
        'home_cls_title': 'Column-Level Security',
        'home_cls_desc': 'Protect sensitive columns with policy tags and taxonomies',
        'home_masking_title': 'Data Masking',
        'home_masking_desc': 'Create protected views with dynamic data masking',
        'home_iam_title': 'IAM Policy Control',
        'home_iam_desc': 'Manage permissions on datasets, projects, and resources',
        'home_audit_title': 'Audit & Compliance',
        'home_audit_desc': 'Track all security operations and generate reports',
        
        # RLS - Create for Users
        'rls_users_title': 'Create RLS Policy for Users',
        'rls_users_desc': 'Create security policies based on individual users',
        'rls_users_dataset': 'Dataset ID',
        'rls_users_table': 'Table Name',
        'rls_users_policy_name': 'Policy Name',
        'rls_users_filter_column': 'Filter Column',
        'rls_users_grantees': 'Authorized Users',
        'rls_users_grantees_hint': 'Enter comma-separated emails',
        'rls_users_create': 'Create Policy',
        'rls_users_success': 'Policy created successfully!',
        'rls_users_error': 'Error creating policy: {error}',
        
        # RLS - Create for Groups
        'rls_groups_title': 'Create RLS Policy for Groups',
        'rls_groups_desc': 'Create security policies based on groups',
        'rls_groups_group_email': 'Group Email',
        'rls_groups_filter_value': 'Filter Value',
        'rls_groups_filter_column': 'Filter Column',
        
        # CLS - Taxonomies
        'cls_tax_title': 'Manage Taxonomies',
        'cls_tax_desc': 'Create and organize taxonomies in Data Catalog',
        'cls_tax_create': 'Create Taxonomy',
        'cls_tax_name': 'Name',
        'cls_tax_description': 'Description',
        'cls_tax_tags_count': 'Tags',
        'cls_tax_edit': 'Edit',
        'cls_tax_delete': 'Delete',
        'cls_tax_confirm_delete': 'Are you sure you want to delete this taxonomy?',
        'cls_tax_success_create': 'Taxonomy created successfully!',
        'cls_tax_success_delete': 'Taxonomy deleted successfully!',
        
        # CLS - Policy Tags
        'cls_tags_title': 'Manage Policy Tags',
        'cls_tags_desc': 'Create and organize hierarchical policy tags',
        'cls_tags_taxonomy': 'Taxonomy',
        'cls_tags_create': 'Create Tag',
        'cls_tags_parent': 'Parent Tag (Optional)',
        'cls_tags_hierarchy': 'Hierarchy',
        'cls_tags_no_parent': 'None (Root Tag)',
        
        # CLS - Apply Tags
        'cls_apply_title': 'Apply Tags to Columns',
        'cls_apply_desc': 'Apply policy tags to table columns',
        'cls_apply_dataset': 'Dataset',
        'cls_apply_table': 'Table',
        'cls_apply_column': 'Column',
        'cls_apply_tag': 'Policy Tag',
        'cls_apply_current_tag': 'Current Tag',
        'cls_apply_no_tag': 'No tag',
        'cls_apply_button': 'Apply Tag',
        'cls_apply_remove': 'Remove Tag',
        'cls_apply_stats': 'Statistics',
        'cls_apply_total_columns': 'Total Columns',
        'cls_apply_protected': 'Protected Columns',
        'cls_apply_unprotected': 'Unprotected Columns',
        'cls_apply_coverage': 'Coverage',
        
        # CLS - Schema Browser
        'cls_schema_title': 'Schema Browser',
        'cls_schema_desc': 'View schemas and applied tags',
        'cls_schema_select_dataset': 'Select a Dataset',
        'cls_schema_tables': 'Tables',
        'cls_schema_columns': 'Columns',
        'cls_schema_type': 'Type',
        'cls_schema_tag': 'Tag',
        
        # IAM
        'iam_dataset_title': 'Manage Dataset Permissions',
        'iam_project_title': 'Manage Project Permissions',
        'iam_control_title': 'Access Control',
        'iam_member': 'Member',
        'iam_role': 'Role',
        'iam_add': 'Add',
        'iam_remove': 'Remove',
        'iam_current_permissions': 'Current Permissions',
        
        # Audit
        'audit_title': 'Audit Logs',
        'audit_desc': 'View all security operations',
        'audit_user': 'User',
        'audit_operation': 'Operation',
        'audit_resource': 'Resource',
        'audit_timestamp': 'Timestamp',
        'audit_status': 'Status',
        'audit_details': 'Details',
        'audit_filter_user': 'Filter by User',
        'audit_filter_operation': 'Filter by Operation',
        'audit_filter_date': 'Filter by Date',
        'audit_export': 'Export Report',
        
        # Common buttons
        'btn_create': 'Create',
        'btn_edit': 'Edit',
        'btn_delete': 'Delete',
        'btn_cancel': 'Cancel',
        'btn_save': 'Save',
        'btn_apply': 'Apply',
        'btn_remove': 'Remove',
        'btn_close': 'Close',
        'btn_refresh': 'Refresh',
        'btn_export': 'Export',
        'btn_back': 'Back',
        
        # Messages
        'msg_success': 'Operation completed successfully!',
        'msg_error': 'Error: {error}',
        'msg_loading': 'Loading...',
        'msg_no_data': 'No data available',
        'msg_confirm': 'Are you sure?',
        
        # Footer
        'footer_version': 'Version',
        'footer_powered': 'Powered by',
        'footer_session': 'Session active as',
    },
    
    # ==================== ESPAÑOL ====================
    'es': {
        # Common
        'app_name': 'GenAI4Data',
        'app_subtitle': 'Gestor de Seguridad',
        
        # Login
        'login_title': 'GenAI4Data',
        'login_subtitle': 'Sistema de Seguridad Integrado',
        'login_button': 'Iniciar sesión con Google',
        'login_loading': 'CARGANDO SISTEMA...',
        'login_powered': 'Desarrollado por Sys Manager',
        'login_partner': 'Partner Google Cloud',
        
        # Language Selector  # ← NOVO
        'lang_selector_title': 'Idioma',
        'lang_pt': 'Português',
        'lang_en': 'English',
        'lang_es': 'Español',
        
        # Header
        'header_logout': 'Cerrar sesión',
        'header_welcome': 'Bienvenido',
        'header_role': 'Rol',
        'header_user_role': 'Su Rol: {role}',  # ← NOVO
        
        # Navigation (Main Sections)
        'nav_home': 'Inicio',
        'nav_rls': 'Seguridad a Nivel de Fila',
        'nav_cls': 'Seguridad a Nivel de Columna',
        'nav_iam': 'Gestión IAM',
        'nav_audit': 'Auditoría',
        
        # Navigation - RLS Submenu  # ← NOVO
        'menu_rls_users': 'Crear por Usuarios',
        'menu_rls_groups': 'Crear por Grupos',
        'menu_rls_assign_users': 'Asignar Usuarios a Política',
        'menu_rls_assign_values': 'Asignar Valores al Grupo',
        
        # Navigation - CLS Submenu  # ← NOVO
        'menu_cls_taxonomies': 'Gestionar Taxonomías',
        'menu_cls_tags': 'Gestionar Etiquetas de Política',
        'menu_cls_apply': 'Aplicar Etiquetas a Columnas',
        'menu_cls_iam': 'Permisos de Etiquetas de Política',
        'menu_cls_create_view': 'Crear Vista Protegida',
        'menu_cls_manage_views': 'Gestionar Vistas Protegidas',
        'menu_cls_schema': 'Navegador de Esquemas',
        
        # Navigation - IAM Submenu  # ← NOVO
        'menu_iam_dataset': 'Gestor IAM de Dataset',
        'menu_iam_project': 'Gestor IAM de Proyecto',
        'menu_iam_control': 'Controlar Acceso',
        
        # Navigation - Audit Submenu  # ← NOVO
        'menu_audit_logs': 'Ver Registros de Auditoría',
        
        # Home
        'home_welcome': 'Bienvenido de nuevo,',  # ← MODIFICADO
        'home_subtitle': 'Gestione políticas RLS, etiquetas CLS y permisos IAM en un solo lugar',
        'home_quick_start': 'Inicio Rápido',  # ← NOVO
        
        # Home - Feature Cards
        'home_rls_title': 'Seguridad a Nivel de Fila',
        'home_rls_desc': 'Controle el acceso a filas específicas según usuarios o grupos',
        'home_cls_title': 'Seguridad a Nivel de Columna',
        'home_cls_desc': 'Proteja columnas sensibles con etiquetas de política y taxonomías',
        'home_masking_title': 'Enmascaramiento de Datos',
        'home_masking_desc': 'Cree vistas protegidas con enmascaramiento dinámico de datos',
        'home_iam_title': 'Control de Políticas IAM',
        'home_iam_desc': 'Gestione permisos en datasets, proyectos y recursos',
        'home_audit_title': 'Auditoría y Cumplimiento',
        'home_audit_desc': 'Rastree todas las operaciones de seguridad y genere informes',
        
        # RLS - Create for Users
        'rls_users_title': 'Crear Política RLS para Usuarios',
        'rls_users_desc': 'Cree políticas de seguridad basadas en usuarios individuales',
        'rls_users_dataset': 'ID del Dataset',
        'rls_users_table': 'Nombre de la Tabla',
        'rls_users_policy_name': 'Nombre de la Política',
        'rls_users_filter_column': 'Columna de Filtro',
        'rls_users_grantees': 'Usuarios Autorizados',
        'rls_users_grantees_hint': 'Ingrese correos separados por comas',
        'rls_users_create': 'Crear Política',
        'rls_users_success': '¡Política creada con éxito!',
        'rls_users_error': 'Error al crear política: {error}',
        
        # RLS - Create for Groups
        'rls_groups_title': 'Crear Política RLS para Grupos',
        'rls_groups_desc': 'Cree políticas de seguridad basadas en grupos',
        'rls_groups_group_email': 'Correo del Grupo',
        'rls_groups_filter_value': 'Valor del Filtro',
        'rls_groups_filter_column': 'Columna de Filtro',
        
        # CLS - Taxonomies
        'cls_tax_title': 'Gestionar Taxonomías',
        'cls_tax_desc': 'Cree y organice taxonomías en Data Catalog',
        'cls_tax_create': 'Crear Taxonomía',
        'cls_tax_name': 'Nombre',
        'cls_tax_description': 'Descripción',
        'cls_tax_tags_count': 'Etiquetas',
        'cls_tax_edit': 'Editar',
        'cls_tax_delete': 'Eliminar',
        'cls_tax_confirm_delete': '¿Está seguro de que desea eliminar esta taxonomía?',
        'cls_tax_success_create': '¡Taxonomía creada con éxito!',
        'cls_tax_success_delete': '¡Taxonomía eliminada con éxito!',
        
        # CLS - Policy Tags
        'cls_tags_title': 'Gestionar Etiquetas de Política',
        'cls_tags_desc': 'Cree y organice etiquetas de política jerárquicas',
        'cls_tags_taxonomy': 'Taxonomía',
        'cls_tags_create': 'Crear Etiqueta',
        'cls_tags_parent': 'Etiqueta Padre (Opcional)',
        'cls_tags_hierarchy': 'Jerarquía',
        'cls_tags_no_parent': 'Ninguna (Etiqueta Raíz)',
        
        # CLS - Apply Tags
        'cls_apply_title': 'Aplicar Etiquetas a Columnas',
        'cls_apply_desc': 'Aplique etiquetas de política a columnas de tablas',
        'cls_apply_dataset': 'Dataset',
        'cls_apply_table': 'Tabla',
        'cls_apply_column': 'Columna',
        'cls_apply_tag': 'Etiqueta de Política',
        'cls_apply_current_tag': 'Etiqueta Actual',
        'cls_apply_no_tag': 'Sin etiqueta',
        'cls_apply_button': 'Aplicar Etiqueta',
        'cls_apply_remove': 'Eliminar Etiqueta',
        'cls_apply_stats': 'Estadísticas',
        'cls_apply_total_columns': 'Total de Columnas',
        'cls_apply_protected': 'Columnas Protegidas',
        'cls_apply_unprotected': 'Columnas Desprotegidas',
        'cls_apply_coverage': 'Cobertura',
        
        # CLS - Schema Browser
        'cls_schema_title': 'Navegador de Esquemas',
        'cls_schema_desc': 'Visualice esquemas y etiquetas aplicadas',
        'cls_schema_select_dataset': 'Seleccione un Dataset',
        'cls_schema_tables': 'Tablas',
        'cls_schema_columns': 'Columnas',
        'cls_schema_type': 'Tipo',
        'cls_schema_tag': 'Etiqueta',
        
        # IAM
        'iam_dataset_title': 'Gestionar Permisos de Dataset',
        'iam_project_title': 'Gestionar Permisos de Proyecto',
        'iam_control_title': 'Control de Acceso',
        'iam_member': 'Miembro',
        'iam_role': 'Rol',
        'iam_add': 'Agregar',
        'iam_remove': 'Eliminar',
        'iam_current_permissions': 'Permisos Actuales',
        
        # Audit
        'audit_title': 'Registros de Auditoría',
        'audit_desc': 'Visualice todas las operaciones de seguridad',
        'audit_user': 'Usuario',
        'audit_operation': 'Operación',
        'audit_resource': 'Recurso',
        'audit_timestamp': 'Fecha/Hora',
        'audit_status': 'Estado',
        'audit_details': 'Detalles',
        'audit_filter_user': 'Filtrar por Usuario',
        'audit_filter_operation': 'Filtrar por Operación',
        'audit_filter_date': 'Filtrar por Fecha',
        'audit_export': 'Exportar Informe',
        
        # Common buttons
        'btn_create': 'Crear',
        'btn_edit': 'Editar',
        'btn_delete': 'Eliminar',
        'btn_cancel': 'Cancelar',
        'btn_save': 'Guardar',
        'btn_apply': 'Aplicar',
        'btn_remove': 'Eliminar',
        'btn_close': 'Cerrar',
        'btn_refresh': 'Actualizar',
        'btn_export': 'Exportar',
        'btn_back': 'Volver',
        
        # Messages
        'msg_success': '¡Operación completada con éxito!',
        'msg_error': 'Error: {error}',
        'msg_loading': 'Cargando...',
        'msg_no_data': 'No hay datos disponibles',
        'msg_confirm': '¿Está seguro?',
        
        # Footer
        'footer_version': 'Versión',
        'footer_powered': 'Desarrollado por',
        'footer_session': 'Sesión activa como',
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Get translated text for a given language and key
    
    Args:
        lang: Language code ('pt', 'en', 'es')
        key: Translation key
        **kwargs: Optional formatting parameters
    
    Returns:
        Translated text (or key if not found)
    
    Example:
        >>> get_text('pt', 'rls_users_error', error='Invalid dataset')
        'Erro ao criar política: Invalid dataset'
    """
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    text = TRANSLATIONS[lang].get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def get_all_keys() -> list:
    """Get all translation keys"""
    return list(TRANSLATIONS['en'].keys())


def validate_translations() -> Dict[str, list]:
    """
    Validate that all languages have the same keys
    
    Returns:
        Dictionary with missing keys per language
    """
    en_keys = set(TRANSLATIONS['en'].keys())
    missing = {}
    
    for lang in ['pt', 'es']:
        lang_keys = set(TRANSLATIONS[lang].keys())
        missing_keys = en_keys - lang_keys
        if missing_keys:
            missing[lang] = list(missing_keys)
    
    return missing


def get_language_stats() -> Dict[str, int]:
    """
    Get statistics about translations
    
    Returns:
        Dictionary with key counts per language
    """
    return {
        lang: len(TRANSLATIONS[lang])
        for lang in SUPPORTED_LANGUAGES
    }


# ============================================
# LANGUAGE CONSTANTS
# ============================================

SUPPORTED_LANGUAGES = ['pt', 'en', 'es']
DEFAULT_LANGUAGE = 'en'

LANGUAGE_NAMES = {
    'pt': 'Português',
    'en': 'English',
    'es': 'Español'
}

LANGUAGE_FLAGS = {
    'pt': '🇧🇷',
    'en': '🇺🇸',
    'es': '🇪🇸'
}


# ============================================
# VALIDATION ON IMPORT
# ============================================

_missing = validate_translations()
if _missing:
    import warnings
    warnings.warn(
        f"Missing translations detected: {_missing}",
        UserWarning
    )
