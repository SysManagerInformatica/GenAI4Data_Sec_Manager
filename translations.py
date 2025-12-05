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
        'home_title': 'Plataforma de Segurança de Dados Empresarial',  # ← NOVO
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
        'rls_users_page_title': 'Criar Política Row Level - Usuários',  # <- NOVO
        'rls_users_subtitle': 'Criar Row Level Security para Usuários',  # <- NOVO
        'rls_users_frame_title': 'Criar',  # <- NOVO
        'rls_users_desc': 'Crie políticas de segurança baseadas em usuários individuais',
        'rls_users_step1_title': 'Selecionar Dataset',  # <- NOVO
        'rls_users_step2_title': 'Selecionar Tabela',  # <- NOVO
        'rls_users_step3_title': 'Selecionar Campo',  # <- NOVO
        'rls_users_step4_title': 'Revisar e Executar',  # <- NOVO
        'rls_users_select_dataset': 'Selecionar Dataset',  # <- NOVO
        'rls_users_select_table': 'Selecionar Tabela',  # <- NOVO
        'rls_users_select_field': 'Selecionar Campo',  # <- NOVO
        'rls_users_review_title': 'A seguinte Política de Row Level Security será criada:',  # <- NOVO
        'rls_users_review_policy_name': 'Nome da Política',  # <- NOVO
        'rls_users_review_project_id': 'ID do Projeto',  # <- NOVO
        'rls_users_review_dataset_id': 'ID do Dataset',  # <- NOVO
        'rls_users_review_table_id': 'ID da Tabela',  # <- NOVO
        'rls_users_review_field_id': 'ID do Campo',  # <- NOVO
        'rls_users_review_code': 'Código',  # <- NOVO
        'rls_users_success_message': 'Política Row Level criada em {table}.{field} com sucesso!',  # <- NOVO
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
        'rls_groups_page_title': 'Criar Política Row Level - Grupos',  # <- NOVO
        'rls_groups_subtitle': 'Criar Row Level Security para Grupos',  # <- NOVO
        'rls_groups_frame_title': 'Criar',  # <- NOVO
        'rls_groups_desc': 'Crie políticas de segurança baseadas em grupos',
        'rls_groups_step4_title': 'Inserir o Grupo',  # <- NOVO
        'rls_groups_enter_group_email': 'Insira o email do grupo',  # <- NOVO
        'rls_groups_review_group_email': 'Email do Grupo',  # <- NOVO
        'rls_groups_success_message': 'Política Row Level criada em {table}.{field} com sucesso!',  # <- NOVO
        'rls_groups_group_email': 'Email do Grupo',
        'rls_groups_filter_value': 'Valor do Filtro',
        'rls_groups_filter_column': 'Coluna de Filtro',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Atribuir Usuários à Política Row Level',
        'rls_assign_users_subtitle': 'Atribuir Usuários à Política Row Level',
        'rls_assign_users_frame_title': 'Atribuir Usuários à Política',
        'rls_assign_users_step1_title': 'Selecionar Política',
        'rls_assign_users_step2_title': 'Gerenciar Atribuições',
        'rls_assign_users_step1_desc': 'Selecione UMA política para gerenciar, ou selecione MÚLTIPLAS para deletar',
        'rls_assign_users_current_assignments': 'Atribuições de Política Atuais',
        'rls_assign_users_select_delete_desc': 'Selecione linhas e clique em DELETAR para remover do banco de dados',
        'rls_assign_users_add_new_title': 'Adicionar Novas Atribuições Usuário-Filtro',
        'rls_assign_users_add_new_desc': 'Adicione usuários e filtros, selecione checkboxes, depois clique em INSERIR',
        'rls_assign_users_add_emails': 'Adicionar Emails de Usuários:',
        'rls_assign_users_add_filters': 'Adicionar Valores de Filtro:',
        'rls_assign_users_user_list_label': 'Email do Usuário (marque para inserir)',
        'rls_assign_users_filter_list_label': 'Valores de Filtro (marque para inserir)',
        
        # Messages - Assign Users
        'msg_error_loading_policies': 'Erro ao carregar políticas existentes: {error}',
        'msg_policy_deleted': 'Política deletada: {username} → {filter_value}',
        'msg_error_deleting_policy': 'Erro ao deletar política: {error}',
        'msg_error_deleting_policy_name': 'Erro ao deletar política \'{policy_name}\': {error}',
        'msg_no_policies_selected_delete': 'Nenhuma política selecionada para deletar.',
        'msg_delete_policies_confirm': 'Deletar {count} política(s)?',
        'msg_and_more': '... e mais {count}',
        'msg_delete_warning_rls': '⚠️ Isto irá deletar a política RLS do BigQuery e todos os filtros associados!',
        'msg_action_cannot_undone': 'Esta ação não pode ser desfeita.',
        'msg_deleted_success': '✅ {count} política(s) deletada(s) com sucesso!',
        'msg_deleted_partial': '⚠️ {success} deletadas, {failed} falharam.',
        'msg_no_policies_selected': 'Nenhuma política selecionada',
        'msg_drop_all_title': '⚠️ REMOVER TODAS AS POLÍTICAS DE ACESSO POR LINHA',
        'msg_critical_warning': '🚨 AVISO CRÍTICO',
        'msg_drop_all_warning1': 'Isto irá remover TODAS as Políticas de Acesso por Linha das tabelas selecionadas!',
        'msg_drop_all_warning2': 'Após esta ação, as tabelas estarão ACESSÍVEIS A TODOS OS USUÁRIOS com permissões de tabela.',
        'msg_affected_tables': 'Tabelas Afetadas:',
        'msg_policies_to_remove': '   Políticas a remover: {count}',
        'msg_show_policy_names': 'Mostrar nomes das políticas',
        'msg_drop_all_alternative': '💡 Alternativa: Se quiser manter controle de acesso, crie uma nova política antes de remover estas.',
        'msg_dropped_success': '✅ Removidas {policies} políticas de {tables} tabela(s)!',
        'msg_dropped_failed': '❌ Falha ao remover políticas de {tables} tabela(s)',
        'msg_no_users_added': 'Nenhum usuário adicionado ainda',
        'msg_no_filters_added': 'Nenhum filtro adicionado ainda',
        'msg_user_removed': 'Usuário {email} removido da lista',
        'msg_filter_removed': 'Filtro \'{filter_value}\' removido da lista',
        'msg_error_fetch_policies': 'Erro ao buscar políticas: {error}',
        'msg_error_unexpected_fetch_policies': 'Erro inesperado ao buscar políticas: {error}',
        'msg_select_at_least_one_user': 'Por favor, selecione pelo menos um usuário para inserir.',
        'msg_select_at_least_one_filter': 'Por favor, selecione pelo menos um filtro para inserir.',
        'msg_inserted_success': 'Inseridos com sucesso {users} usuários × {filters} filtros',
        'msg_error_inserting_data': 'Erro ao inserir dados: {error}',
        'msg_no_rows_selected': 'Nenhuma linha selecionada.',
        'msg_no_policy_selected': 'Nenhuma política selecionada.',
        'msg_user_added': 'Usuário {email} adicionado',
        'msg_user_already_added': 'Usuário já adicionado.',
        'msg_invalid_email': 'Endereço de email inválido.',
        'msg_filter_added': 'Filtro \'{filter_value}\' adicionado',
        'msg_filter_already_added': 'Filtro já adicionado.',
        'msg_invalid_filter': 'Valor de filtro inválido.',
        'msg_no_rows_selected_delete': 'Nenhuma linha selecionada para deletar.',
        
        # Buttons - Assign Users
        'btn_delete_upper': 'DELETAR',
        'btn_cancel_upper': 'CANCELAR',
        'btn_delete_selected': 'DELETAR SELECIONADOS',
        'btn_drop_all_from_table': 'REMOVER TODAS DA TABELA',
        'btn_drop_all_policies': 'REMOVER TODAS AS POLÍTICAS',
        'btn_add_user': 'ADICIONAR USUÁRIO',
        'btn_add_filter': 'ADICIONAR FILTRO',
        'btn_insert_selected': 'INSERIR SELECIONADOS',
        
        # Tooltips - Assign Users
        'tooltip_remove_from_list': 'Remover da lista',
        'tooltip_drop_all': '⚠️ Remove TODAS as políticas das tabelas selecionadas',
        
        # Tabs - Assign Users
        'tab_existing_policies': 'Políticas Existentes',
        'tab_add_new_assignments': 'Adicionar Novas Atribuições',
        
        # Grid Columns - Assign Users
        'col_user_email': 'Email do Usuário',
        'col_filter_value': 'Valor do Filtro',
        'col_policy_name': 'Nome da Política',
        'col_field': 'Campo',
        'col_created_at': 'Criado em',
        
        # Placeholders - Assign Users
        'placeholder_user_email': 'usuario@exemplo.com',
        'placeholder_filter_value': 'Tecnologia da Informação',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Atribuir Usuários à Política Row Level',
        'rls_assign_users_subtitle': 'Atribuir Usuários à Política Row Level',
        'rls_assign_users_frame_title': 'Atribuir Usuários à Política',
        'rls_assign_users_step1_title': 'Selecionar Política',
        'rls_assign_users_step2_title': 'Gerenciar Atribuições',
        'rls_assign_users_step1_desc': 'Selecione UMA política para gerenciar, ou MÚLTIPLAS para deletar',
        
        # RLS Assign - Tabs
        'tab_existing_policies': 'Políticas Existentes',
        'tab_add_new_assignments': 'Adicionar Novas Atribuições',
        
        # RLS Assign - Labels
        'label_current_policy_assignments': 'Atribuições de Política Atuais',
        'label_select_rows_delete': 'Selecione linhas e clique DELETAR para remover do banco de dados',
        'label_add_new_assignments': 'Adicionar Novas Atribuições Usuário-Filtro',
        'label_add_users_filters_instruction': 'Adicione usuários e filtros, marque as checkboxes e clique INSERIR',
        'label_add_user_emails': 'Adicionar Emails de Usuários:',
        'label_user_email_check_insert': 'Email do Usuário (marque para inserir)',
        'label_add_filter_values': 'Adicionar Valores de Filtro:',
        'label_filter_values_check_insert': 'Valores de Filtro (marque para inserir)',
        
        # RLS Assign - Grid Headers
        'grid_header_user_email': 'Email do Usuário',
        'grid_header_filter_value': 'Valor do Filtro',
        'grid_header_policy_name': 'Nome da Política',
        'grid_header_field': 'Campo',
        'grid_header_created_at': 'Criado Em',
        
        # RLS Assign - Placeholders
        'placeholder_user_email': 'usuario@exemplo.com',
        'placeholder_filter_value': 'Tecnologia da Informação',
        
        # RLS Assign - Tooltips
        'tooltip_remove_from_list': 'Remover da lista',
        'tooltip_drop_all': '⚠️ Remove TODAS as políticas das tabelas selecionadas',
        
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
        # Audit Page
        'audit_title': 'Logs de Auditoria',
        'audit_subtitle': 'Rastreie todas as operações e mudanças de segurança',
        'audit_desc': 'Visualize todas as operações de segurança',
        'audit_filters_title': 'Filtros',  # <- NOVO
        'audit_user': 'Usuário',
        'audit_operation': 'Operação',
        'audit_resource': 'Recurso',
        'audit_timestamp': 'Data/Hora',
        'audit_status': 'Status',
        'audit_details': 'Detalhes',
        'audit_filter_user': 'Filtrar por Usuário',
        'audit_filter_operation': 'Filtrar por Operação',
        'audit_filter_date': 'Filtrar por Data',
        'audit_filter_date_range': 'Período',
        'audit_filter_action': 'Ação',
        'audit_export': 'Exportar Relatório',
        'audit_refresh': 'Atualizar',
        
        # Audit - Date Range Options
        'audit_filter_last_hour': 'Última Hora',  # <- NOVO
        'audit_filter_today': 'Hoje',  # <- NOVO
        'audit_filter_last_7_days': 'Últimos 7 Dias',  # <- NOVO
        'audit_filter_last_30_days': 'Últimos 30 Dias',  # <- NOVO
        
        # Audit - Statistics
        'audit_stat_total_actions': 'Total de Ações',  # <- NOVO
        'audit_stat_success_rate': 'Taxa de Sucesso',
        'audit_stat_failed_actions': 'Ações Falhadas',  # <- NOVO
        'audit_stat_active_users': 'Usuários Ativos',
        
        # Audit - Activity Labels
        'audit_recent_activities': 'Atividades Recentes (mostrando {count} logs)',
        'audit_no_logs': 'Nenhum log de auditoria encontrado com os filtros atuais',  # <- MODIFICADO
        'audit_log_user': 'Usuário',  # <- NOVO
        'audit_log_resource': 'Recurso',  # <- NOVO
        'audit_log_taxonomy': 'Taxonomia',  # <- NOVO
        'audit_log_error': 'Erro',  # <- NOVO
        
        # Audit - Action Filter  # <- NOVO
        'audit_action_all': 'Todas',
        
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
        'btn_next': 'Próximo',
        'btn_delete_selected': 'DELETAR SELECIONADOS',  # <- NOVO
        'btn_drop_all_from_table': 'REMOVER TODAS DA TABELA',  # <- NOVO
        'btn_add_user': 'ADICIONAR USUÁRIO',  # <- NOVO
        'btn_add_filter': 'ADICIONAR FILTRO',  # <- NOVO
        'btn_insert_selected': 'INSERIR SELECIONADOS',  # <- NOVO
        'btn_drop_all_policies': 'REMOVER TODAS AS POLÍTICAS',  # <- NOVO
        
        # Messages
        'msg_success': 'Operação realizada com sucesso!',
        'msg_error': 'Erro: {error}',
        'msg_loading': 'Carregando...',
        'msg_no_data': 'Nenhum dado disponível',
        'msg_confirm': 'Tem certeza?',
        'msg_error_fetch_datasets': 'Erro ao buscar datasets: {error}',  # <- NOVO
        'msg_error_fetch_tables': 'Erro ao buscar tabelas: {error}',  # <- NOVO
        'msg_error_fetch_fields': 'Erro ao buscar campos: {error}',  # <- NOVO
        'msg_error_create_policy': 'Erro ao criar política de row-level access: {error}',  # <- NOVO
        'msg_error_unexpected': 'Ocorreu um erro inesperado: {error}',  # <- NOVO
        'msg_select_dataset_first': 'Por favor, selecione um dataset primeiro.',  # <- NOVO
        'msg_select_table_first': 'Por favor, selecione uma tabela primeiro.',  # <- NOVO
        'msg_select_field_first': 'Por favor, selecione um campo primeiro.',  # <- NOVO
        'msg_dataset_not_found': 'Dataset não encontrado: {dataset}',  # <- NOVO
        'msg_table_not_found': 'Tabela não encontrada: {table}',
        # RLS Assign - Messages
        'msg_error_load_policies': 'Erro ao carregar políticas existentes: {error}',
        'msg_error_delete_policy': 'Erro ao deletar política: {error}',
        'msg_error_delete_policy_full': "Erro ao deletar política '{policy}': {error}",
        'msg_error_fetch_policies': 'Erro ao buscar políticas: {error}',
        'msg_error_insert_data': 'Erro ao inserir dados: {error}',
        'msg_no_policies_selected': 'Nenhuma política selecionada.',
        'msg_no_rows_selected': 'Nenhuma linha selecionada.',
        'msg_no_policy_selected': 'Nenhuma política selecionada.',
        'msg_no_rows_selected_delete': 'Nenhuma linha selecionada para deletar.',
        'msg_no_users_added': 'Nenhum usuário adicionado ainda',
        'msg_no_filters_added': 'Nenhum filtro adicionado ainda',
        'msg_select_at_least_one_user': 'Por favor, selecione pelo menos um usuário para inserir.',
        'msg_select_at_least_one_filter': 'Por favor, selecione pelo menos um filtro para inserir.',
        'msg_user_already_added': 'Usuário já adicionado.',
        'msg_filter_already_added': 'Filtro já adicionado.',
        'msg_invalid_email': 'Endereço de email inválido.',
        'msg_invalid_filter': 'Valor de filtro inválido.',
        'msg_policy_deleted': 'Política deletada: {username} → {filter}',
        'msg_user_removed': 'Usuário {email} removido da lista',
        'msg_filter_removed': "Filtro '{filter}' removido da lista",
        'msg_user_added': 'Usuário {email} adicionado',
        'msg_filter_added': "Filtro '{filter}' adicionado",
        'msg_insert_success': '{users} usuários × {filters} filtros inseridos com sucesso',
        'msg_delete_success': '✅ {count} política(s) deletada(s) com sucesso!',
        'msg_delete_partial': '⚠️ {success} deletada(s), {failed} falharam.',
        'msg_drop_all_success': '✅ {policies} políticas removidas de {tables} tabela(s)!',
        'msg_drop_all_failed': '❌ Falha ao remover políticas de {tables} tabela(s)',
        'msg_delete_confirm_title': 'Deletar {count} política(s)?',
        'msg_and_more': '... e mais {count}',
        'msg_delete_warning': '⚠️ Isto irá deletar a política RLS do BigQuery e todos os filtros associados!',
        'msg_action_cannot_undone': 'Esta ação não pode ser desfeita.',
        'msg_drop_all_title': '⚠️ REMOVER TODAS AS POLÍTICAS ROW ACCESS',
        'msg_critical_warning': '🚨 AVISO CRÍTICO',
        'msg_drop_all_warning1': 'Isto irá remover TODAS as Políticas Row Access das tabelas selecionadas!',
        'msg_drop_all_warning2': 'Após esta ação, as tabelas estarão ACESSÍVEIS A TODOS OS USUÁRIOS com permissões de tabela.',
        'msg_affected_tables': 'Tabelas Afetadas:',
        'msg_policies_to_remove': 'Políticas a remover: {count}',
        'msg_show_policy_names': 'Mostrar nomes das políticas',
        'msg_alternative_hint': '💡 Alternativa: Se você deseja manter o controle de acesso, crie uma nova política antes de remover estas.',
        
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
        'home_title': 'Enterprise Data Security Platform',  # ← NOVO
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
        'rls_users_page_title': 'Create Row Level Policy - Users',  # <- NOVO
        'rls_users_subtitle': 'Create Row Level Security for Users',  # <- NOVO
        'rls_users_frame_title': 'Create',  # <- NOVO
        'rls_users_desc': 'Create security policies based on individual users',
        'rls_users_step1_title': 'Select Dataset',  # <- NOVO
        'rls_users_step2_title': 'Select Table',  # <- NOVO
        'rls_users_step3_title': 'Select Field',  # <- NOVO
        'rls_users_step4_title': 'Review and Run',  # <- NOVO
        'rls_users_select_dataset': 'Select Dataset',  # <- NOVO
        'rls_users_select_table': 'Select Table',  # <- NOVO
        'rls_users_select_field': 'Select Field',  # <- NOVO
        'rls_users_review_title': 'The following Row Level Security Policy will be created:',  # <- NOVO
        'rls_users_review_policy_name': 'Policy Name',  # <- NOVO
        'rls_users_review_project_id': 'Project ID',  # <- NOVO
        'rls_users_review_dataset_id': 'Dataset ID',  # <- NOVO
        'rls_users_review_table_id': 'Table ID',  # <- NOVO
        'rls_users_review_field_id': 'Field ID',  # <- NOVO
        'rls_users_review_code': 'Code',  # <- NOVO
        'rls_users_success_message': 'Row Level Policy created on {table}.{field} successfully!',  # <- NOVO
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
        'rls_groups_page_title': 'Create Row Level Policy - Groups',  # <- NOVO
        'rls_groups_subtitle': 'Create Row Level Security for Groups',  # <- NOVO
        'rls_groups_frame_title': 'Create',  # <- NOVO
        'rls_groups_desc': 'Create security policies based on groups',
        'rls_groups_step4_title': 'Enter the Group',  # <- NOVO
        'rls_groups_enter_group_email': 'Enter the group email',  # <- NOVO
        'rls_groups_review_group_email': 'Group Email',  # <- NOVO
        'rls_groups_success_message': 'Row Level Policy created on {table}.{field} successfully!',  # <- NOVO
        'rls_groups_group_email': 'Group Email',
        'rls_groups_filter_value': 'Filter Value',
        'rls_groups_filter_column': 'Filter Column',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Assign Users to Row Level Policy',
        'rls_assign_users_subtitle': 'Assign Users to Row Level Policy',
        'rls_assign_users_frame_title': 'Assign Users to Policy',
        'rls_assign_users_step1_title': 'Select Policy',
        'rls_assign_users_step2_title': 'Manage Assignments',
        'rls_assign_users_step1_desc': 'Select ONE policy to manage, or select MULTIPLE to delete',
        'rls_assign_users_current_assignments': 'Current Policy Assignments',
        'rls_assign_users_select_delete_desc': 'Select rows and click DELETE to remove from database',
        'rls_assign_users_add_new_title': 'Add New User-Filter Assignments',
        'rls_assign_users_add_new_desc': 'Add users and filters, select checkboxes, then click INSERT',
        'rls_assign_users_add_emails': 'Add User Emails:',
        'rls_assign_users_add_filters': 'Add Filter Values:',
        'rls_assign_users_user_list_label': 'User Email (check to insert)',
        'rls_assign_users_filter_list_label': 'Filter Values (check to insert)',
        
        # Messages - Assign Users
        'msg_error_loading_policies': 'Error loading existing policies: {error}',
        'msg_policy_deleted': 'Policy deleted: {username} → {filter_value}',
        'msg_error_deleting_policy': 'Error deleting policy: {error}',
        'msg_error_deleting_policy_name': 'Error deleting policy \'{policy_name}\': {error}',
        'msg_no_policies_selected_delete': 'No policies selected to delete.',
        'msg_delete_policies_confirm': 'Delete {count} policy(ies)?',
        'msg_and_more': '... and {count} more',
        'msg_delete_warning_rls': '⚠️ This will delete the RLS policy from BigQuery and all associated filters!',
        'msg_action_cannot_undone': 'This action cannot be undone.',
        'msg_deleted_success': '✅ Successfully deleted {count} policy(ies)!',
        'msg_deleted_partial': '⚠️ Deleted {success}, {failed} failed.',
        'msg_no_policies_selected': 'No policies selected',
        'msg_drop_all_title': '⚠️ DROP ALL ROW ACCESS POLICIES',
        'msg_critical_warning': '🚨 CRITICAL WARNING',
        'msg_drop_all_warning1': 'This will remove ALL Row Access Policies from the selected tables!',
        'msg_drop_all_warning2': 'After this action, tables will be ACCESSIBLE TO ALL USERS with table permissions.',
        'msg_affected_tables': 'Affected Tables:',
        'msg_policies_to_remove': '   Policies to remove: {count}',
        'msg_show_policy_names': 'Show policy names',
        'msg_drop_all_alternative': '💡 Alternative: If you want to keep access control, create a new policy before dropping these.',
        'msg_dropped_success': '✅ Dropped {policies} policies from {tables} table(s)!',
        'msg_dropped_failed': '❌ Failed to drop policies from {tables} table(s)',
        'msg_no_users_added': 'No users added yet',
        'msg_no_filters_added': 'No filters added yet',
        'msg_user_removed': 'User {email} removed from list',
        'msg_filter_removed': 'Filter \'{filter_value}\' removed from list',
        'msg_error_fetch_policies': 'Error fetching policies: {error}',
        'msg_error_unexpected_fetch_policies': 'Unexpected error fetching policies: {error}',
        'msg_select_at_least_one_user': 'Please select at least one user to insert.',
        'msg_select_at_least_one_filter': 'Please select at least one filter to insert.',
        'msg_inserted_success': 'Successfully inserted {users} users × {filters} filters',
        'msg_error_inserting_data': 'Error inserting data: {error}',
        'msg_no_rows_selected': 'No rows selected.',
        'msg_no_policy_selected': 'No policy selected.',
        'msg_user_added': 'User {email} added',
        'msg_user_already_added': 'User already added.',
        'msg_invalid_email': 'Invalid email address.',
        'msg_filter_added': 'Filter \'{filter_value}\' added',
        'msg_filter_already_added': 'Filter already added.',
        'msg_invalid_filter': 'Invalid filter value.',
        'msg_no_rows_selected_delete': 'No rows selected to delete.',
        
        # Buttons - Assign Users
        'btn_delete_upper': 'DELETE',
        'btn_cancel_upper': 'CANCEL',
        'btn_delete_selected': 'DELETE SELECTED',
        'btn_drop_all_from_table': 'DROP ALL FROM TABLE',
        'btn_drop_all_policies': 'DROP ALL POLICIES',
        'btn_add_user': 'ADD USER',
        'btn_add_filter': 'ADD FILTER',
        'btn_insert_selected': 'INSERT SELECTED',
        
        # Tooltips - Assign Users
        'tooltip_remove_from_list': 'Remove from list',
        'tooltip_drop_all': '⚠️ Removes ALL policies from selected tables',
        
        # Tabs - Assign Users
        'tab_existing_policies': 'Existing Policies',
        'tab_add_new_assignments': 'Add New Assignments',
        
        # Grid Columns - Assign Users
        'col_user_email': 'User Email',
        'col_filter_value': 'Filter Value',
        'col_policy_name': 'Policy Name',
        'col_field': 'Field',
        'col_created_at': 'Created At',
        
        # Placeholders - Assign Users
        'placeholder_user_email': 'user@example.com',
        'placeholder_filter_value': 'Information Technology',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Assign Users to Row Level Policy',
        'rls_assign_users_subtitle': 'Assign Users to Row Level Policy',
        'rls_assign_users_frame_title': 'Assign Users to Policy',
        'rls_assign_users_step1_title': 'Select Policy',
        'rls_assign_users_step2_title': 'Manage Assignments',
        'rls_assign_users_step1_desc': 'Select ONE policy to manage, or MULTIPLE to delete',
        
        # RLS Assign - Tabs
        'tab_existing_policies': 'Existing Policies',
        'tab_add_new_assignments': 'Add New Assignments',
        
        # RLS Assign - Labels
        'label_current_policy_assignments': 'Current Policy Assignments',
        'label_select_rows_delete': 'Select rows and click DELETE to remove from database',
        'label_add_new_assignments': 'Add New User-Filter Assignments',
        'label_add_users_filters_instruction': 'Add users and filters, check boxes, then click INSERT',
        'label_add_user_emails': 'Add User Emails:',
        'label_user_email_check_insert': 'User Email (check to insert)',
        'label_add_filter_values': 'Add Filter Values:',
        'label_filter_values_check_insert': 'Filter Values (check to insert)',
        
        # RLS Assign - Grid Headers
        'grid_header_user_email': 'User Email',
        'grid_header_filter_value': 'Filter Value',
        'grid_header_policy_name': 'Policy Name',
        'grid_header_field': 'Field',
        'grid_header_created_at': 'Created At',
        
        # RLS Assign - Placeholders
        'placeholder_user_email': 'user@example.com',
        'placeholder_filter_value': 'Information Technology',
        
        # RLS Assign - Tooltips
        'tooltip_remove_from_list': 'Remove from list',
        'tooltip_drop_all': '⚠️ Removes ALL policies from selected tables',
        
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
        
        # Audit Page
        'audit_title': 'Audit Logs',
        'audit_subtitle': 'Track all security operations and changes',
        'audit_desc': 'View all security operations',
        'audit_filters_title': 'Filters',  # <- NOVO
        'audit_user': 'User',
        'audit_operation': 'Operation',
        'audit_resource': 'Resource',
        'audit_timestamp': 'Timestamp',
        'audit_status': 'Status',
        'audit_details': 'Details',
        'audit_filter_user': 'Filter by User',
        'audit_filter_operation': 'Filter by Operation',
        'audit_filter_date': 'Filter by Date',
        'audit_filter_date_range': 'Date Range',
        'audit_filter_action': 'Action',
        'audit_export': 'Export Report',
        'audit_refresh': 'Refresh',
        
        # Audit - Date Range Options
        'audit_filter_last_hour': 'Last Hour',  # <- NOVO
        'audit_filter_today': 'Today',  # <- NOVO
        'audit_filter_last_7_days': 'Last 7 Days',  # <- NOVO
        'audit_filter_last_30_days': 'Last 30 Days',  # <- NOVO
        
        # Audit - Statistics
        'audit_stat_total_actions': 'Total Actions',  # <- NOVO
        'audit_stat_success_rate': 'Success Rate',
        'audit_stat_failed_actions': 'Failed Actions',  # <- NOVO
        'audit_stat_active_users': 'Active Users',
        
        # Audit - Activity Labels
        'audit_recent_activities': 'Recent Activities (showing {count} logs)',
        'audit_no_logs': 'No audit logs found with current filters',  # <- MODIFICADO
        'audit_log_user': 'User',  # <- NOVO
        'audit_log_resource': 'Resource',  # <- NOVO
        'audit_log_taxonomy': 'Taxonomy',  # <- NOVO
        'audit_log_error': 'Error',  # <- NOVO
        
        # Audit - Action Filter  # <- NOVO
        'audit_action_all': 'All',
        
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
        'btn_next': 'Next',
        'btn_delete_selected': 'DELETE SELECTED',  # <- NOVO
        'btn_drop_all_from_table': 'DROP ALL FROM TABLE',  # <- NOVO
        'btn_add_user': 'ADD USER',  # <- NOVO
        'btn_add_filter': 'ADD FILTER',  # <- NOVO
        'btn_insert_selected': 'INSERT SELECTED',  # <- NOVO
        'btn_drop_all_policies': 'DROP ALL POLICIES',  # <- NOVO
        
        # Messages
        'msg_success': 'Operation completed successfully!',
        'msg_error': 'Error: {error}',
        'msg_loading': 'Loading...',
        'msg_no_data': 'No data available',
        'msg_confirm': 'Are you sure?',
        'msg_error_fetch_datasets': 'Error fetching datasets: {error}',  # <- NOVO
        'msg_error_fetch_tables': 'Error fetching tables: {error}',  # <- NOVO
        'msg_error_fetch_fields': 'Error fetching fields: {error}',  # <- NOVO
        'msg_error_create_policy': 'Error creating row-level access policy: {error}',  # <- NOVO
        'msg_error_unexpected': 'An unexpected error occurred: {error}',  # <- NOVO
        'msg_select_dataset_first': 'Please select a dataset first.',  # <- NOVO
        'msg_select_table_first': 'Please select a table first.',  # <- NOVO
        'msg_select_field_first': 'Please select a field first.',  # <- NOVO
        'msg_dataset_not_found': 'Dataset not found: {dataset}',  # <- NOVO
        'msg_table_not_found': 'Table not found: {table}',
        # RLS Assign - Messages
        'msg_error_load_policies': 'Error loading existing policies: {error}',
        'msg_error_delete_policy': 'Error deleting policy: {error}',
        'msg_error_delete_policy_full': "Error deleting policy '{policy}': {error}",
        'msg_error_fetch_policies': 'Error fetching policies: {error}',
        'msg_error_insert_data': 'Error inserting data: {error}',
        'msg_no_policies_selected': 'No policies selected.',
        'msg_no_rows_selected': 'No rows selected.',
        'msg_no_policy_selected': 'No policy selected.',
        'msg_no_rows_selected_delete': 'No rows selected to delete.',
        'msg_no_users_added': 'No users added yet',
        'msg_no_filters_added': 'No filters added yet',
        'msg_select_at_least_one_user': 'Please select at least one user to insert.',
        'msg_select_at_least_one_filter': 'Please select at least one filter to insert.',
        'msg_user_already_added': 'User already added.',
        'msg_filter_already_added': 'Filter already added.',
        'msg_invalid_email': 'Invalid email address.',
        'msg_invalid_filter': 'Invalid filter value.',
        'msg_policy_deleted': 'Policy deleted: {username} → {filter}',
        'msg_user_removed': 'User {email} removed from list',
        'msg_filter_removed': "Filter '{filter}' removed from list",
        'msg_user_added': 'User {email} added',
        'msg_filter_added': "Filter '{filter}' added",
        'msg_insert_success': '{users} users × {filters} filters inserted successfully',
        'msg_delete_success': '✅ {count} policy(ies) deleted successfully!',
        'msg_delete_partial': '⚠️ {success} deleted, {failed} failed.',
        'msg_drop_all_success': '✅ {policies} policies removed from {tables} table(s)!',
        'msg_drop_all_failed': '❌ Failed to remove policies from {tables} table(s)',
        'msg_delete_confirm_title': 'Delete {count} policy(ies)?',
        'msg_and_more': '... and {count} more',
        'msg_delete_warning': '⚠️ This will delete the RLS policy from BigQuery and all associated filters!',
        'msg_action_cannot_undone': 'This action cannot be undone.',
        'msg_drop_all_title': '⚠️ DROP ALL ROW ACCESS POLICIES',
        'msg_critical_warning': '🚨 CRITICAL WARNING',
        'msg_drop_all_warning1': 'This will remove ALL Row Access Policies from selected tables!',
        'msg_drop_all_warning2': 'After this action, tables will be ACCESSIBLE TO ALL USERS with table permissions.',
        'msg_affected_tables': 'Affected Tables:',
        'msg_policies_to_remove': 'Policies to remove: {count}',
        'msg_show_policy_names': 'Show policy names',
        'msg_alternative_hint': '💡 Alternative: If you want to keep access control, create a new policy before dropping these.',
        
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
        'home_title': 'Plataforma de Seguridad de Datos Empresarial',  # ← NOVO
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
        'rls_users_page_title': 'Crear Política Row Level - Usuarios',  # <- NOVO
        'rls_users_subtitle': 'Crear Row Level Security para Usuarios',  # <- NOVO
        'rls_users_frame_title': 'Crear',  # <- NOVO
        'rls_users_desc': 'Cree políticas de seguridad basadas en usuarios individuales',
        'rls_users_step1_title': 'Seleccionar Dataset',  # <- NOVO
        'rls_users_step2_title': 'Seleccionar Tabla',  # <- NOVO
        'rls_users_step3_title': 'Seleccionar Campo',  # <- NOVO
        'rls_users_step4_title': 'Revisar y Ejecutar',  # <- NOVO
        'rls_users_select_dataset': 'Seleccionar Dataset',  # <- NOVO
        'rls_users_select_table': 'Seleccionar Tabla',  # <- NOVO
        'rls_users_select_field': 'Seleccionar Campo',  # <- NOVO
        'rls_users_review_title': 'Se creará la siguiente Política de Row Level Security:',  # <- NOVO
        'rls_users_review_policy_name': 'Nombre de la Política',  # <- NOVO
        'rls_users_review_project_id': 'ID del Proyecto',  # <- NOVO
        'rls_users_review_dataset_id': 'ID del Dataset',  # <- NOVO
        'rls_users_review_table_id': 'ID de la Tabla',  # <- NOVO
        'rls_users_review_field_id': 'ID del Campo',  # <- NOVO
        'rls_users_review_code': 'Código',  # <- NOVO
        'rls_users_success_message': '¡Política Row Level creada en {table}.{field} con éxito!',  # <- NOVO
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
        'rls_groups_page_title': 'Crear Política Row Level - Grupos',  # <- NOVO
        'rls_groups_subtitle': 'Crear Row Level Security para Grupos',  # <- NOVO
        'rls_groups_frame_title': 'Crear',  # <- NOVO
        'rls_groups_desc': 'Cree políticas de seguridad basadas en grupos',
        'rls_groups_step4_title': 'Ingresar el Grupo',  # <- NOVO
        'rls_groups_enter_group_email': 'Ingrese el correo del grupo',  # <- NOVO
        'rls_groups_review_group_email': 'Correo del Grupo',  # <- NOVO
        'rls_groups_success_message': '¡Política Row Level creada en {table}.{field} con éxito!',  # <- NOVO
        'rls_groups_group_email': 'Correo del Grupo',
        'rls_groups_filter_value': 'Valor del Filtro',
        'rls_groups_filter_column': 'Columna de Filtro',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Asignar Usuarios a Política Row Level',
        'rls_assign_users_subtitle': 'Asignar Usuarios a Política Row Level',
        'rls_assign_users_frame_title': 'Asignar Usuarios a Política',
        'rls_assign_users_step1_title': 'Seleccionar Política',
        'rls_assign_users_step2_title': 'Gestionar Asignaciones',
        'rls_assign_users_step1_desc': 'Seleccione UNA política para gestionar, o seleccione MÚLTIPLES para eliminar',
        'rls_assign_users_current_assignments': 'Asignaciones de Política Actuales',
        'rls_assign_users_select_delete_desc': 'Seleccione filas y haga clic en ELIMINAR para remover de la base de datos',
        'rls_assign_users_add_new_title': 'Agregar Nuevas Asignaciones Usuario-Filtro',
        'rls_assign_users_add_new_desc': 'Agregue usuarios y filtros, seleccione checkboxes, luego haga clic en INSERTAR',
        'rls_assign_users_add_emails': 'Agregar Correos de Usuarios:',
        'rls_assign_users_add_filters': 'Agregar Valores de Filtro:',
        'rls_assign_users_user_list_label': 'Correo del Usuario (marque para insertar)',
        'rls_assign_users_filter_list_label': 'Valores de Filtro (marque para insertar)',
        
        # Messages - Assign Users
        'msg_error_loading_policies': 'Error al cargar políticas existentes: {error}',
        'msg_policy_deleted': 'Política eliminada: {username} → {filter_value}',
        'msg_error_deleting_policy': 'Error al eliminar política: {error}',
        'msg_error_deleting_policy_name': 'Error al eliminar política \'{policy_name}\': {error}',
        'msg_no_policies_selected_delete': 'No se seleccionaron políticas para eliminar.',
        'msg_delete_policies_confirm': '¿Eliminar {count} política(s)?',
        'msg_and_more': '... y {count} más',
        'msg_delete_warning_rls': '⚠️ ¡Esto eliminará la política RLS de BigQuery y todos los filtros asociados!',
        'msg_action_cannot_undone': 'Esta acción no se puede deshacer.',
        'msg_deleted_success': '✅ ¡{count} política(s) eliminada(s) con éxito!',
        'msg_deleted_partial': '⚠️ {success} eliminadas, {failed} fallaron.',
        'msg_no_policies_selected': 'No se seleccionaron políticas',
        'msg_drop_all_title': '⚠️ ELIMINAR TODAS LAS POLÍTICAS DE ACCESO POR FILA',
        'msg_critical_warning': '🚨 ADVERTENCIA CRÍTICA',
        'msg_drop_all_warning1': '¡Esto eliminará TODAS las Políticas de Acceso por Fila de las tablas seleccionadas!',
        'msg_drop_all_warning2': 'Después de esta acción, las tablas estarán ACCESIBLES A TODOS LOS USUARIOS con permisos de tabla.',
        'msg_affected_tables': 'Tablas Afectadas:',
        'msg_policies_to_remove': '   Políticas a eliminar: {count}',
        'msg_show_policy_names': 'Mostrar nombres de políticas',
        'msg_drop_all_alternative': '💡 Alternativa: Si desea mantener el control de acceso, cree una nueva política antes de eliminar estas.',
        'msg_dropped_success': '✅ ¡Eliminadas {policies} políticas de {tables} tabla(s)!',
        'msg_dropped_failed': '❌ Falló al eliminar políticas de {tables} tabla(s)',
        'msg_no_users_added': 'No se agregaron usuarios aún',
        'msg_no_filters_added': 'No se agregaron filtros aún',
        'msg_user_removed': 'Usuario {email} eliminado de la lista',
        'msg_filter_removed': 'Filtro \'{filter_value}\' eliminado de la lista',
        'msg_error_fetch_policies': 'Error al obtener políticas: {error}',
        'msg_error_unexpected_fetch_policies': 'Error inesperado al obtener políticas: {error}',
        'msg_select_at_least_one_user': 'Por favor, seleccione al menos un usuario para insertar.',
        'msg_select_at_least_one_filter': 'Por favor, seleccione al menos un filtro para insertar.',
        'msg_inserted_success': 'Insertados con éxito {users} usuarios × {filters} filtros',
        'msg_error_inserting_data': 'Error al insertar datos: {error}',
        'msg_no_rows_selected': 'No se seleccionaron filas.',
        'msg_no_policy_selected': 'No se seleccionó política.',
        'msg_user_added': 'Usuario {email} agregado',
        'msg_user_already_added': 'Usuario ya agregado.',
        'msg_invalid_email': 'Dirección de correo inválida.',
        'msg_filter_added': 'Filtro \'{filter_value}\' agregado',
        'msg_filter_already_added': 'Filtro ya agregado.',
        'msg_invalid_filter': 'Valor de filtro inválido.',
        'msg_no_rows_selected_delete': 'No se seleccionaron filas para eliminar.',
        
        # Buttons - Assign Users
        'btn_delete_upper': 'ELIMINAR',
        'btn_cancel_upper': 'CANCELAR',
        'btn_delete_selected': 'ELIMINAR SELECCIONADOS',
        'btn_drop_all_from_table': 'ELIMINAR TODAS DE LA TABLA',
        'btn_drop_all_policies': 'ELIMINAR TODAS LAS POLÍTICAS',
        'btn_add_user': 'AGREGAR USUARIO',
        'btn_add_filter': 'AGREGAR FILTRO',
        'btn_insert_selected': 'INSERTAR SELECCIONADOS',
        
        # Tooltips - Assign Users
        'tooltip_remove_from_list': 'Eliminar de la lista',
        'tooltip_drop_all': '⚠️ Elimina TODAS las políticas de las tablas seleccionadas',
        
        # Tabs - Assign Users
        'tab_existing_policies': 'Políticas Existentes',
        'tab_add_new_assignments': 'Agregar Nuevas Asignaciones',
        
        # Grid Columns - Assign Users
        'col_user_email': 'Correo del Usuario',
        'col_filter_value': 'Valor del Filtro',
        'col_policy_name': 'Nombre de la Política',
        'col_field': 'Campo',
        'col_created_at': 'Creado en',
        
        # Placeholders - Assign Users
        'placeholder_user_email': 'usuario@ejemplo.com',
        'placeholder_filter_value': 'Tecnología de la Información',
        
        # RLS - Assign Users to Policy
        'rls_assign_users_page_title': 'Asignar Usuarios a la Política Row Level',
        'rls_assign_users_subtitle': 'Asignar Usuarios a la Política Row Level',
        'rls_assign_users_frame_title': 'Asignar Usuarios a la Política',
        'rls_assign_users_step1_title': 'Seleccionar Política',
        'rls_assign_users_step2_title': 'Gestionar Asignaciones',
        'rls_assign_users_step1_desc': 'Seleccione UNA política para gestionar, o MÚLTIPLES para eliminar',
        
        # RLS Assign - Tabs
        'tab_existing_policies': 'Políticas Existentes',
        'tab_add_new_assignments': 'Agregar Nuevas Asignaciones',
        
        # RLS Assign - Labels
        'label_current_policy_assignments': 'Asignaciones de Política Actuales',
        'label_select_rows_delete': 'Seleccione filas y haga clic en ELIMINAR para remover de la base de datos',
        'label_add_new_assignments': 'Agregar Nuevas Asignaciones Usuario-Filtro',
        'label_add_users_filters_instruction': 'Agregue usuarios y filtros, marque las casillas y haga clic en INSERTAR',
        'label_add_user_emails': 'Agregar Correos de Usuarios:',
        'label_user_email_check_insert': 'Correo del Usuario (marque para insertar)',
        'label_add_filter_values': 'Agregar Valores de Filtro:',
        'label_filter_values_check_insert': 'Valores de Filtro (marque para insertar)',
        
        # RLS Assign - Grid Headers
        'grid_header_user_email': 'Correo del Usuario',
        'grid_header_filter_value': 'Valor del Filtro',
        'grid_header_policy_name': 'Nombre de la Política',
        'grid_header_field': 'Campo',
        'grid_header_created_at': 'Creado En',
        
        # RLS Assign - Placeholders
        'placeholder_user_email': 'usuario@ejemplo.com',
        'placeholder_filter_value': 'Tecnología de la Información',
        
        # RLS Assign - Tooltips
        'tooltip_remove_from_list': 'Remover de la lista',
        'tooltip_drop_all': '⚠️ Elimina TODAS las políticas de las tablas seleccionadas',
        
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
        
        # Audit Page
        'audit_title': 'Registros de Auditoría',
        'audit_subtitle': 'Rastree todas las operaciones y cambios de seguridad',
        'audit_desc': 'Visualice todas las operaciones de seguridad',
        'audit_filters_title': 'Filtros',  # <- NOVO
        'audit_user': 'Usuario',
        'audit_operation': 'Operación',
        'audit_resource': 'Recurso',
        'audit_timestamp': 'Fecha/Hora',
        'audit_status': 'Estado',
        'audit_details': 'Detalles',
        'audit_filter_user': 'Filtrar por Usuario',
        'audit_filter_operation': 'Filtrar por Operación',
        'audit_filter_date': 'Filtrar por Fecha',
        'audit_filter_date_range': 'Período',
        'audit_filter_action': 'Acción',
        'audit_export': 'Exportar Informe',
        'audit_refresh': 'Actualizar',
        
        # Audit - Date Range Options
        'audit_filter_last_hour': 'Última Hora',  # <- NOVO
        'audit_filter_today': 'Hoy',  # <- NOVO
        'audit_filter_last_7_days': 'Últimos 7 Días',  # <- NOVO
        'audit_filter_last_30_days': 'Últimos 30 Días',  # <- NOVO
        
        # Audit - Statistics
        'audit_stat_total_actions': 'Total de Acciones',  # <- NOVO
        'audit_stat_success_rate': 'Tasa de Éxito',
        'audit_stat_failed_actions': 'Acciones Fallidas',  # <- NOVO
        'audit_stat_active_users': 'Usuarios Activos',
        
        # Audit - Activity Labels
        'audit_recent_activities': 'Actividades Recientes (mostrando {count} registros)',
        'audit_no_logs': 'No se encontraron registros de auditoría con los filtros actuales',  # <- MODIFICADO
        'audit_log_user': 'Usuario',  # <- NOVO
        'audit_log_resource': 'Recurso',  # <- NOVO
        'audit_log_taxonomy': 'Taxonomía',  # <- NOVO
        'audit_log_error': 'Error',  # <- NOVO
        
        # Audit - Action Filter  # <- NOVO
        'audit_action_all': 'Todas',
        
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
        'btn_next': 'Siguiente',
        'btn_delete_selected': 'ELIMINAR SELECCIONADOS',  # <- NOVO
        'btn_drop_all_from_table': 'ELIMINAR TODAS DE LA TABLA',  # <- NOVO
        'btn_add_user': 'AGREGAR USUARIO',  # <- NOVO
        'btn_add_filter': 'AGREGAR FILTRO',  # <- NOVO
        'btn_insert_selected': 'INSERTAR SELECCIONADOS',  # <- NOVO
        'btn_drop_all_policies': 'ELIMINAR TODAS LAS POLÍTICAS',  # <- NOVO
        
        # Messages
        'msg_success': '¡Operación completada con éxito!',
        'msg_error': 'Error: {error}',
        'msg_loading': 'Cargando...',
        'msg_no_data': 'No hay datos disponibles',
        'msg_confirm': '¿Está seguro?',
        'msg_error_fetch_datasets': 'Error al obtener datasets: {error}',  # <- NOVO
        'msg_error_fetch_tables': 'Error al obtener tablas: {error}',  # <- NOVO
        'msg_error_fetch_fields': 'Error al obtener campos: {error}',  # <- NOVO
        'msg_error_create_policy': 'Error al crear política de row-level access: {error}',  # <- NOVO
        'msg_error_unexpected': 'Ocurrió un error inesperado: {error}',  # <- NOVO
        'msg_select_dataset_first': 'Por favor, seleccione un dataset primero.',  # <- NOVO
        'msg_select_table_first': 'Por favor, seleccione una tabla primero.',  # <- NOVO
        'msg_select_field_first': 'Por favor, seleccione un campo primero.',  # <- NOVO
        'msg_dataset_not_found': 'Dataset no encontrado: {dataset}',  # <- NOVO
        'msg_table_not_found': 'Tabla no encontrada: {table}',
        # RLS Assign - Messages
        'msg_error_load_policies': 'Error al cargar políticas existentes: {error}',
        'msg_error_delete_policy': 'Error al eliminar política: {error}',
        'msg_error_delete_policy_full': "Error al eliminar política '{policy}': {error}",
        'msg_error_fetch_policies': 'Error al obtener políticas: {error}',
        'msg_error_insert_data': 'Error al insertar datos: {error}',
        'msg_no_policies_selected': 'No hay políticas seleccionadas.',
        'msg_no_rows_selected': 'No hay filas seleccionadas.',
        'msg_no_policy_selected': 'No hay política seleccionada.',
        'msg_no_rows_selected_delete': 'No hay filas seleccionadas para eliminar.',
        'msg_no_users_added': 'No se han agregado usuarios aún',
        'msg_no_filters_added': 'No se han agregado filtros aún',
        'msg_select_at_least_one_user': 'Por favor, seleccione al menos un usuario para insertar.',
        'msg_select_at_least_one_filter': 'Por favor, seleccione al menos un filtro para insertar.',
        'msg_user_already_added': 'Usuario ya agregado.',
        'msg_filter_already_added': 'Filtro ya agregado.',
        'msg_invalid_email': 'Dirección de correo inválida.',
        'msg_invalid_filter': 'Valor de filtro inválido.',
        'msg_policy_deleted': 'Política eliminada: {username} → {filter}',
        'msg_user_removed': 'Usuario {email} eliminado de la lista',
        'msg_filter_removed': "Filtro '{filter}' eliminado de la lista",
        'msg_user_added': 'Usuario {email} agregado',
        'msg_filter_added': "Filtro '{filter}' agregado",
        'msg_insert_success': '{users} usuarios × {filters} filtros insertados con éxito',
        'msg_delete_success': '✅ ¡{count} política(s) eliminada(s) con éxito!',
        'msg_delete_partial': '⚠️ {success} eliminada(s), {failed} fallaron.',
        'msg_drop_all_success': '✅ ¡{policies} políticas eliminadas de {tables} tabla(s)!',
        'msg_drop_all_failed': '❌ Error al eliminar políticas de {tables} tabla(s)',
        'msg_delete_confirm_title': '¿Eliminar {count} política(s)?',
        'msg_and_more': '... y {count} más',
        'msg_delete_warning': '⚠️ ¡Esto eliminará la política RLS de BigQuery y todos los filtros asociados!',
        'msg_action_cannot_undone': 'Esta acción no se puede deshacer.',
        'msg_drop_all_title': '⚠️ ELIMINAR TODAS LAS POLÍTICAS ROW ACCESS',
        'msg_critical_warning': '🚨 ADVERTENCIA CRÍTICA',
        'msg_drop_all_warning1': '¡Esto eliminará TODAS las Políticas Row Access de las tablas seleccionadas!',
        'msg_drop_all_warning2': 'Después de esta acción, las tablas estarán ACCESIBLES PARA TODOS LOS USUARIOS con permisos de tabla.',
        'msg_affected_tables': 'Tablas Afectadas:',
        'msg_policies_to_remove': 'Políticas a eliminar: {count}',
        'msg_show_policy_names': 'Mostrar nombres de las políticas',
        'msg_alternative_hint': '💡 Alternativa: Si desea mantener el control de acceso, cree una nueva política antes de eliminar estas.',
        
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
