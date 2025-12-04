# RLS & CLS Security Manager

## Documentação Técnica Completa

**Sistema Integrado de Segurança para BigQuery**

**Versão**: 2.0  
**Data**: 04/12/2025  
**Autor**: Lucas Carvalhal - Sys Manager  
**Status**: Em Produção

---

## 📑 ÍNDICE

### 1. CONTEXTO E VISÃO GERAL
- [1.1 Problema de Negócio](#11-problema-de-negócio)
- [1.2 Solução Proposta](#12-solução-proposta)
- [1.3 Benefícios e Impacto](#13-benefícios-e-impacto)

### 2. ARQUITETURA TÉCNICA
- [2.1 Visão Geral da Arquitetura](#21-visão-geral-da-arquitetura)
- [2.2 Componentes Principais](#22-componentes-principais)
- [2.3 Fluxo de Dados](#23-fluxo-de-dados)

### 3. STACK TECNOLÓGICA
- [3.1 Frontend](#31-frontend)
- [3.2 Backend](#32-backend)
- [3.3 Cloud Services](#33-cloud-services)
- [3.4 Bibliotecas e Frameworks](#34-bibliotecas-e-frameworks)

### 4. ESTRUTURA DO PROJETO
- [4.1 Organização de Diretórios](#41-organização-de-diretórios)
- [4.2 Arquivos de Configuração](#42-arquivos-de-configuração)

### 5. IMPLEMENTAÇÃO DETALHADA
- [5.1 Módulo RLS (Row-Level Security)](#51-módulo-rls-row-level-security)
- [5.2 Módulo CLS (Column-Level Security)](#52-módulo-cls-column-level-security)
- [5.3 Módulo Audit Logs](#53-módulo-audit-logs)
- [5.4 Camada de Serviços](#54-camada-de-serviços)

### 6. SISTEMA DE UI/UX (v2.0)
- [6.1 Tema HUD/Sci-Fi](#61-tema-hudsci-fi)
- [6.2 Login Page](#62-login-page)
- [6.3 Design System](#63-design-system)
- [6.4 Componentes Interativos](#64-componentes-interativos)

### 7. DECISÕES TÉCNICAS
- [7.1 Por que NiceGUI?](#71-por-que-nicegui)
- [7.2 Por que Cloud Run?](#72-por-que-cloud-run)
- [7.3 Por que HTML Puro no Login?](#73-por-que-html-puro-no-login)
- [7.4 Padrões de Design](#74-padrões-de-design)

### 8. DESAFIOS E SOLUÇÕES
- [8.1 Remoção de Policy Tags](#81-remoção-de-policy-tags)
- [8.2 Logging em Cloud Run](#82-logging-em-cloud-run)
- [8.3 Schema Dinâmico do BigQuery](#83-schema-dinâmico-do-bigquery)
- [8.4 CSS Conflicts no Login](#84-css-conflicts-no-login)

### 9. SEGURANÇA E COMPLIANCE
- [9.1 Autenticação e Autorização](#91-autenticação-e-autorização)
- [9.2 Proteção de Dados Sensíveis](#92-proteção-de-dados-sensíveis)
- [9.3 Audit Trail](#93-audit-trail)

### 10. CODE DOCUMENTATION
- [10.1 BigQuery Services](#101-bigquery-services)
- [10.2 Data Catalog Services](#102-data-catalog-services)
- [10.3 Audit Services](#103-audit-services)
- [10.4 Theme Services](#104-theme-services)

### 11. PERFORMANCE E ESCALABILIDADE
- [11.1 Otimizações Implementadas](#111-otimizações-implementadas)
- [11.2 Limites e Restrições](#112-limites-e-restrições)

### 12. HISTÓRICO DE VERSÕES
- [12.1 v1.0 - RLS + CLS Integration](#121-v10---rls--cls-integration)
- [12.2 v2.0 - UI Overhaul & HUD Theme](#122-v20---ui-overhaul--hud-theme)

### 13. ROADMAP FUTURO
- [13.1 v2.1 - Translations](#131-v21---translations)
- [13.2 v3.0 - Features Avançadas](#132-v30---features-avançadas)

---

## 🎯 1. CONTEXTO E VISÃO GERAL

### 1.1 Problema de Negócio

#### Desafio de Segurança de Dados no BigQuery

Organizações que utilizam o Google BigQuery enfrentam desafios significativos ao implementar políticas de segurança granulares em seus dados.

#### Problemas Identificados

**1. Complexidade na Implementação de RLS**
- Criação manual de políticas de segurança requer conhecimento avançado de SQL
- Gerenciamento de filtros por usuário/grupo é trabalhoso e propenso a erros
- Falta de interface visual para configuração de políticas
- Dificuldade em manter consistência entre múltiplos datasets

**2. Gestão Fragmentada de CLS**
- Policy tags espalhadas em múltiplas taxonomias sem visão centralizada
- Aplicação manual de tags em colunas é repetitiva e propensa a erros
- Ausência de ferramentas para visualizar cobertura de tags
- Dificuldade em auditar quais colunas possuem proteção

**3. Falta de Visibilidade**
- Sem audit logs centralizados para mudanças de segurança
- Impossível rastrear quem fez o quê e quando
- Dificuldade em demonstrar compliance para auditores
- Falta de relatórios sobre estado de segurança dos dados

**4. Interface Técnica**
- Console do GCP é técnico demais para usuários de negócio
- Requer múltiplas navegações entre Data Catalog, BigQuery e IAM
- Curva de aprendizado alta para novos usuários
- Sem visualização consolidada do estado de segurança

#### Impacto nos Negócios

- **Tempo perdido**: 2-3 horas/semana por analista gerenciando segurança manualmente
- **Risco de exposição**: Dados sensíveis podem ficar desprotegidos por erro humano
- **Compliance**: Dificuldade em demonstrar conformidade com LGPD, SOX, ISO 27001
- **Custos**: Aumento de custos operacionais com processos manuais

---

### 1.2 Solução Proposta

#### RLS & CLS Security Manager: Interface Unificada

Desenvolvimento de uma aplicação web integrada que centraliza a gestão de segurança de dados no BigQuery, oferecendo funcionalidades principais organizadas e acessíveis.

#### Funcionalidades Principais

**🔐 Gestão Completa de RLS**
- Interface visual para criar políticas de Row-Level Security
- Suporte para políticas baseadas em usuários individuais
- Suporte para políticas baseadas em grupos
- Atribuição de usuários a políticas existentes
- Atribuição de valores permitidos por grupo
- Validação automática de sintaxe SQL
- Preview de políticas antes de aplicar

**🏷️ Gestão Completa de CLS**
- Criar e gerenciar taxonomias no Data Catalog
- Criar e organizar policy tags hierárquicas
- Aplicar tags em colunas de forma visual
- Remover tags de colunas
- Schema browser com visualização de tags aplicadas
- Estatísticas de cobertura (quantas colunas estão protegidas)
- Gerenciar permissões IAM por policy tag

**📊 Sistema de Auditoria Completo**
- Log de todas as operações de segurança
- Rastreamento de quem fez cada mudança
- Timestamp de todas as operações
- Histórico de mudanças por dataset/tabela
- Exportação de relatórios para compliance

**🎨 Interface Moderna (v2.0)**
- Tema HUD/Sci-Fi com elementos visuais técnicos
- Dark mode por padrão
- Animações e transições suaves
- Sidebar sempre visível para navegação rápida
- Cards interativos com hover effects
- Login page em HTML puro com glassmorphism

**🌍 Multi-idioma (em desenvolvimento)**
- Suporte para Português, Inglês e Espanhol
- Seleção de idioma via bandeiras no header
- Persistência de preferência do usuário
- Traduções completas de toda a interface

#### Arquitetura da Solução

A arquitetura do sistema é composta por camadas bem definidas que garantem escalabilidade, manutenibilidade e segurança.

```
┌─────────────────────────────────────────────────┐
│           PRESENTATION LAYER                    │
│  ┌──────────────────────────────────────────┐  │
│  │  NiceGUI Frontend (Python)               │  │
│  │  - Pages (RLS, CLS, Audit)               │  │
│  │  - Components (Menu, Theme, Cards)       │  │
│  │  - HTML Login Page (v2.0)                │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           BUSINESS LOGIC LAYER                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Services                                 │  │
│  │  - BigQueryRLSService                    │  │
│  │  - BigQueryCLSService                    │  │
│  │  - DataCatalogService                    │  │
│  │  - AuditService                          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           DATA ACCESS LAYER                     │
│  ┌──────────────────────────────────────────┐  │
│  │  Google Cloud APIs                        │  │
│  │  - BigQuery Client                       │  │
│  │  - Data Catalog Client                   │  │
│  │  - Cloud Logging                         │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           STORAGE LAYER                         │
│  ┌──────────────────────────────────────────┐  │
│  │  Google Cloud Platform                    │  │
│  │  - BigQuery Datasets & Tables            │  │
│  │  - Data Catalog (Taxonomies & Tags)      │  │
│  │  - Cloud Storage (Audit Logs)            │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

### 1.3 Benefícios e Impacto

#### Benefícios Qualitativos

**1. Redução de Tempo**
- **Antes**: 2-3 horas/semana por analista
- **Depois**: 15-30 minutos/semana
- **Economia**: 85-90% do tempo gasto em segurança

**2. Redução de Erros**
- Interface visual elimina erros de sintaxe SQL
- Validação automática de políticas antes de aplicar
- Preview de mudanças antes de confirmar
- Audit trail para reverter mudanças problemáticas

**3. Melhoria de Compliance**
- Audit logs automáticos de todas as operações
- Relatórios prontos para auditores
- Rastreabilidade completa de mudanças
- Demonstração clara de controles de segurança

**4. Democratização**
- Usuários de negócio podem gerenciar segurança
- Sem necessidade de conhecimento SQL avançado
- Interface intuitiva com tooltips e guias
- Redução de dependência de equipe técnica

**5. Experiência do Usuário (v2.0)**
- Interface moderna e profissional
- Feedback visual imediato
- Animações suaves e intuitivas
- Dark mode reduz fadiga ocular
- Navegação rápida e eficiente

#### ROI Estimado

**Cenário: Empresa com 20 analistas**

| Métrica | Antes | Depois | Economia |
|---------|-------|--------|----------|
| **Tempo/semana** | 50h (20 × 2.5h) | 8h (20 × 0.4h) | 42h/semana |
| **Horas/ano** | 2.600h | 416h | 2.184h/ano |
| **Custo/hora** | R$ 100 | R$ 100 | - |
| **Economia anual** | - | - | **R$ 218.400/ano** |

**Benefícios Adicionais (não quantificados)**:
- Redução de incidentes de segurança
- Melhoria em auditorias de compliance
- Redução de multas por exposição de dados
- Aumento de confiança de clientes

---

## 🏗️ 2. ARQUITETURA TÉCNICA

### 2.1 Visão Geral da Arquitetura

O sistema é estruturado em camadas bem definidas, seguindo os princípios de arquitetura limpa e separação de responsabilidades.

#### Diagrama de Alto Nível

```
┌────────────────────────────────────────────────────────┐
│                    CLOUD RUN                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │         FastAPI + NiceGUI Application            │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Static Files (v2.0)                      │  │  │
│  │  │  - login.html (HTML puro)                 │  │  │
│  │  │  - flags/ (bandeiras de idiomas)          │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Presentation Layer                       │  │  │
│  │  │  - theme.py (CSS global + dark mode)      │  │  │
│  │  │  - home.py (página inicial)               │  │  │
│  │  │  - menu.py (sidebar navigation)           │  │  │
│  │  │  - pages/ (RLS, CLS, Audit, IAM)          │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Business Logic Layer                     │  │  │
│  │  │  - BigQueryRLSService                     │  │  │
│  │  │  - BigQueryCLSService                     │  │  │
│  │  │  - DataCatalogService                     │  │  │
│  │  │  - AuditService                           │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Authentication Layer                     │  │  │
│  │  │  - OAuth 2.0 (Google)                     │  │  │
│  │  │  - Session Management                     │  │  │
│  │  │  - Role-based Access Control              │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD PLATFORM                      │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   BigQuery   │  │ Data Catalog │  │Cloud Logging│  │
│  │              │  │              │  │             │  │
│  │ - Datasets   │  │ - Taxonomies │  │ - Audit Log │  │
│  │ - Tables     │  │ - Policy Tags│  │ - App Log   │  │
│  │ - RLS Pol.   │  │ - IAM Perms  │  │ - Error Log │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

### 2.2 Componentes Principais

#### 1. Application Core (main.py)

Entry point da aplicação responsável por:
- Inicialização do NiceGUI e FastAPI
- Configuração de routing
- Loading de páginas
- Gestão do ciclo de vida da aplicação
- Dark mode global (v2.0)
- Servir static files (v2.0)

**Código-chave**:
```python
# main.py
import os
from nicegui import ui, app
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Dark mode global (v2.0)
ui.dark_mode().enable()

# Montar static files (v2.0)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')

# Rota FastAPI para login HTML (v2.0)
@app.get('/login', response_class=HTMLResponse)
async def serve_login_html():
    # Serve HTML puro com variáveis injetadas
    ...

# Rota NiceGUI para callback OAuth
@ui.page('/callback')
def callback():
    # Lógica de autenticação
    ...

# Rota principal
@ui.page('/')
def index():
    with frame('Home'):
        content()
```

---

#### 2. Services Layer

**BigQueryRLSService**
- Criação de políticas RLS
- Listagem de políticas existentes
- Atribuição de usuários/grupos
- Remoção de políticas

**BigQueryCLSService**
- Listagem de datasets e tabelas
- Obtenção de schemas
- Aplicação/remoção de tags
- Estatísticas de cobertura

**DataCatalogService**
- CRUD de taxonomias
- CRUD de policy tags
- Gerenciamento de IAM por tag
- Hierarquia de tags

**AuditService**
- Registro de todas as operações
- Consulta de logs históricos
- Exportação de relatórios
- Métricas de uso

---

#### 3. Presentation Layer

**Theme System (v2.0)**
- CSS global injetado no `<head>`
- Variáveis CSS customizadas
- Dark mode por padrão
- Cores consistentes em toda aplicação

**Componentes**:
- `theme.py`: CSS global + frame() function
- `home.py`: Página inicial com 5 feature cards
- `menu.py`: Sidebar com navegação color-coded
- `pages/`: Todas as páginas funcionais

---

#### 4. Static Files (v2.0)

**login.html**
- HTML puro sem NiceGUI
- CSS customizado com tema HUD/Sci-Fi
- JavaScript para OAuth flow
- Elementos decorativos animados

**Estrutura**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        :root {
            --hud-color: #00f3ff;
            --bg-color: #000000;
        }
        /* ~400 linhas de CSS */
    </style>
</head>
<body>
    <div class="tech-bg">
        <div class="grid-overlay"></div>
        <div class="hud-circle-outer"></div>
        <div class="glass-card">
            <!-- Login content -->
        </div>
    </div>
    <script>
        // OAuth logic
    </script>
</body>
</html>
```

---

### 2.3 Fluxo de Dados

#### Fluxo de Criação de Política RLS

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │ 1. Preenche formulário
       ↓
┌─────────────────────────┐
│  create_rls_users.py    │
│  (Presentation Layer)   │
└──────┬──────────────────┘
       │ 2. Valida dados
       │ 3. Chama serviço
       ↓
┌─────────────────────────┐
│ BigQueryRLSService      │
│ (Business Logic)        │
└──────┬──────────────────┘
       │ 4. Monta SQL
       │ 5. Executa query
       ↓
┌─────────────────────────┐
│  BigQuery API           │
│  (Data Access)          │
└──────┬──────────────────┘
       │ 6. Cria/atualiza tabela
       ↓
┌─────────────────────────┐
│  BigQuery Dataset       │
│  (Storage)              │
└─────────────────────────┘
       │ 7. Confirma sucesso
       ↓
┌─────────────────────────┐
│  AuditService           │
│  (Logging)              │
└─────────────────────────┘
       │ 8. Registra operação
       ↓
┌─────────────────────────┐
│  Cloud Logging          │
└─────────────────────────┘
```

---

#### Fluxo de Aplicação de Policy Tag

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │ 1. Seleciona dataset/tabela/coluna/tag
       ↓
┌─────────────────────────┐
│  cls_apply_tags.py      │
│  (Presentation Layer)   │
└──────┬──────────────────┘
       │ 2. Valida seleção
       │ 3. Chama serviço CLS
       ↓
┌─────────────────────────┐
│ BigQueryCLSService      │
│ (Business Logic)        │
└──────┬──────────────────┘
       │ 4. Busca schema atual
       │ 5. Modifica schema
       │ 6. Atualiza tabela
       ↓
┌─────────────────────────┐
│  BigQuery API           │
│  (Data Access)          │
└──────┬──────────────────┘
       │ 7. Aplica mudança
       ↓
┌─────────────────────────┐
│  BigQuery Table         │
│  (Storage)              │
└─────────────────────────┘
       │ 8. Registra no audit
       ↓
┌─────────────────────────┐
│  AuditService           │
└─────────────────────────┘
```

---

## 💻 3. STACK TECNOLÓGICA

### 3.1 Frontend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **NiceGUI** | 1.4.x | Framework Python para UI web |
| **HTML5** | - | Login page (v2.0) |
| **CSS3** | - | Tema HUD/Sci-Fi customizado (v2.0) |
| **JavaScript** | ES6+ | OAuth flow + interatividade |
| **Quasar** | 2.x | Framework Vue.js (via NiceGUI) |
| **Material Design Icons** | - | Ícones da interface |

**Características**:
- Reactive UI com Python puro
- Single Page Application (SPA)
- Server-side rendering
- Dark mode nativo (v2.0)
- Glassmorphism effects (v2.0)

---

### 3.2 Backend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.11+ | Linguagem principal |
| **FastAPI** | 0.104+ | Framework web (via NiceGUI) |
| **Uvicorn** | 0.24+ | ASGI server |
| **google-cloud-bigquery** | 3.14.1 | Cliente BigQuery |
| **google-cloud-datacatalog** | 3.17.0 | Cliente Data Catalog |
| **google-auth** | 2.x | Autenticação Google |

**Padrões de Código**:
- Type hints em todas as funções
- Docstrings em estilo Google
- Logging estruturado
- Error handling robusto

---

### 3.3 Cloud Services

| Serviço | Uso |
|---------|-----|
| **Cloud Run** | Hospedagem da aplicação |
| **BigQuery** | Storage de dados + RLS/CLS |
| **Data Catalog** | Taxonomies + Policy Tags |
| **Cloud Logging** | Logs centralizados |
| **Cloud Build** | CI/CD pipeline |
| **Secret Manager** | Gerenciamento de secrets |
| **Cloud IAM** | Controle de acesso |

---

### 3.4 Bibliotecas e Frameworks

**Core**:
```python
# requirements.txt
nicegui==1.4.34
fastapi==0.104.1
uvicorn[standard]==0.24.0
google-cloud-bigquery==3.14.1
google-cloud-datacatalog==3.17.0
google-cloud-logging==3.8.0
google-auth==2.25.2
google-auth-oauthlib==1.1.0
python-dotenv==1.0.0
```

**Utilities**:
```python
wonderwords==2.2.0      # Geração de nomes aleatórios
db-dtypes==1.2.0        # Tipos de dados BigQuery
pydantic==2.5.0         # Validação de dados
python-jose==3.3.0      # JWT tokens
passlib==1.7.4          # Hashing de senhas
```

---

## 📂 4. ESTRUTURA DO PROJETO

### 4.1 Organização de Diretórios

```
GenAI4Data_Sec_Manager/
├── main.py                         # Entry point da aplicação
├── home.py                         # Página inicial (v2.0)
├── menu.py                         # Menu lateral (v1.0 + v2.0)
├── theme.py                        # Tema global (v2.0)
├── config.py                       # Configurações
├── requirements.txt                # Dependências Python
├── Dockerfile                      # Container configuration
├── .dockerignore                   # Exclusões do Docker
├── .gitignore                      # Exclusões do Git
├── README.md                       # Documentação do projeto
├── CHANGELOG.md                    # Histórico de mudanças (v2.0)
├── LICENSE                         # Licença MIT
│
├── static/                         # Arquivos estáticos (v2.0 NOVO)
│   ├── login.html                  # Login page HTML puro
│   └── flags/                      # Bandeiras de idiomas (futuro)
│       ├── br.svg
│       ├── us.svg
│       └── es.svg
│
├── services/                       # Camada de serviços (v1.0 NOVO)
│   ├── __init__.py
│   ├── bigquery_rls_service.py     # Serviço RLS
│   ├── bigquery_cls_service.py     # Serviço CLS
│   ├── datacatalog_service.py      # Serviço Data Catalog
│   └── audit_service.py            # Serviço de Auditoria
│
├── pages/                          # Páginas da aplicação
│   ├── __init__.py
│   ├── login_page.py               # Callback OAuth (v2.0 modificado)
│   │
│   ├── create_rls_users.py         # RLS: Criar por usuários
│   ├── create_rls_groups.py        # RLS: Criar por grupos
│   ├── assign_users_to_policy.py   # RLS: Atribuir usuários
│   ├── assign_values_to_group.py   # RLS: Atribuir valores
│   │
│   ├── cls_taxonomies.py           # CLS: Gerenciar taxonomias (v1.0)
│   ├── cls_policy_tags.py          # CLS: Gerenciar tags (v1.0)
│   ├── cls_apply_tags.py           # CLS: Aplicar tags (v1.0)
│   ├── cls_apply_iam.py            # CLS: Permissões IAM (v1.0)
│   ├── cls_dynamic_columns.py      # CLS: Criar protected view (v1.0)
│   ├── cls_dynamic_manage.py       # CLS: Gerenciar views (v1.0)
│   ├── cls_schema_browser.py       # CLS: Navegar schemas (v1.0)
│   │
│   ├── dataset_iam_manager.py      # IAM: Gerenciar dataset
│   ├── project_iam_manager.py      # IAM: Gerenciar projeto
│   └── control_access.py           # IAM: Controle de acesso
│
├── translations.py                 # Sistema de traduções (v2.0 - estrutura)
│
├── utils/                          # Utilitários
│   ├── __init__.py
│   ├── validators.py               # Validações
│   ├── formatters.py               # Formatadores
│   └── helpers.py                  # Funções auxiliares
│
├── docs/                           # Documentação
│   ├── USERGUIDE.md                # Guia do usuário
│   ├── TECHNICAL_DOCS.md           # Documentação técnica (este arquivo)
│   ├── API.md                      # Documentação da API
│   └── images/                     # Imagens da documentação
│
└── tests/                          # Testes (futuro)
    ├── __init__.py
    ├── test_services.py
    ├── test_pages.py
    └── test_utils.py
```

---

### 4.2 Arquivos de Configuração

#### config.py

```python
"""
Configurações centralizadas da aplicação
"""
import os
from typing import Optional

class Config:
    """Configurações do sistema"""
    
    # Google Cloud
    PROJECT_ID: str = os.getenv('PROJECT_ID', 'sys-googl-cortex-security')
    LOCATION: str = os.getenv('LOCATION', 'us-central1')
    
    # BigQuery
    RLS_MANAGER_DATASET: str = 'rls_security'
    POLICY_TABLE: str = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.policies'
    FILTER_TABLE: str = f'{PROJECT_ID}.{RLS_MANAGER_DATASET}.policies_filters'
    
    # OAuth
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    REDIRECT_URI: str = os.getenv('REDIRECT_URI', 'http://localhost:8080/callback')
    
    # Session
    SESSION_SECRET: str = os.getenv('SESSION_SECRET', 'default-secret-key')
    SESSION_TIMEOUT: int = 3600  # 1 hora
    
    # Application
    PORT: int = int(os.getenv('PORT', 8080))
    HOST: str = '0.0.0.0'
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # UI (v2.0)
    THEME: str = 'dark'  # dark | light
    PRIMARY_COLOR: str = '#00f3ff'  # Ciano neon
    
    # Translations (v2.0)
    DEFAULT_LANGUAGE: str = 'en'  # pt | en | es
    
    @classmethod
    def validate(cls) -> bool:
        """Valida configurações obrigatórias"""
        required = [
            'PROJECT_ID',
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET',
            'SESSION_SECRET',
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        return True
```

---

#### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Metadados
LABEL maintainer="Lucas Carvalhal <lucas.carvalhal@sysmanager.com.br>"
LABEL version="2.0"
LABEL description="RLS & CLS Security Manager for BigQuery"

# Configurar workdir
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8080

# Variáveis de ambiente padrão
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicialização
CMD ["python", "main.py"]
```

---

#### requirements.txt

```txt
# Core Framework
nicegui==1.4.34
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Google Cloud
google-cloud-bigquery==3.14.1
google-cloud-datacatalog==3.17.0
google-cloud-logging==3.8.0
google-cloud-core==2.4.1

# Authentication
google-auth==2.25.2
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1

# Utilities
python-dotenv==1.0.0
wonderwords==2.2.0
db-dtypes==1.2.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.1
```

---

## 5. IMPLEMENTAÇÃO DETALHADA

### 5.1 Módulo RLS (Row-Level Security)

#### 5.1.1 Create RLS for Users

**Arquivo**: `pages/create_rls_users.py`

**Funcionalidade**: Permite criar políticas de RLS baseadas em usuários individuais.

**Fluxo**:
1. Usuário seleciona dataset e tabela
2. Usuário define a coluna de filtro (ex: `user_email`)
3. Sistema gera policy name automaticamente
4. Usuário revisa SQL gerado
5. Sistema cria a policy no BigQuery
6. Sistema registra no audit log

**Código de Exemplo**:
```python
def create_rls_for_users():
    """Criar política RLS para usuários"""
    
    with ui.card().classes('w-full'):
        ui.label('Create RLS Policy for Users').classes('text-xl font-bold')
        ui.label('Define row-level security based on user email')
        
        # Inputs
        dataset_input = ui.input('Dataset ID').classes('w-full')
        table_input = ui.input('Table Name').classes('w-full')
        filter_column = ui.input('Filter Column').classes('w-full')
        
        # Botão de criar
        def on_create():
            try:
                service = BigQueryRLSService()
                policy_name = f"rls_users_{table_input.value}"
                
                # SQL da policy
                sql = f"""
                CREATE OR REPLACE ROW ACCESS POLICY {policy_name}
                ON `{Config.PROJECT_ID}.{dataset_input.value}.{table_input.value}`
                GRANT TO ("user:{SESSION_USER()}")
                FILTER USING ({filter_column.value} = SESSION_USER())
                """
                
                # Executar
                service.execute_query(sql)
                
                # Audit log
                AuditService.log_operation(
                    operation='CREATE_RLS_POLICY',
                    resource=f'{dataset_input.value}.{table_input.value}',
                    details={'policy_name': policy_name}
                )
                
                ui.notify('Policy created successfully!', type='positive')
                
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        
        ui.button('Create Policy', on_click=on_create).classes('mt-4')
```

---

#### 5.1.2 Create RLS for Groups

**Arquivo**: `pages/create_rls_groups.py`

**Funcionalidade**: Permite criar políticas RLS baseadas em grupos.

**Diferencial**: Em vez de filtrar por usuário individual, filtra por grupo (ex: departamento, região, empresa).

**SQL Gerado**:
```sql
CREATE OR REPLACE ROW ACCESS POLICY rls_group_sales
ON `project.dataset.sales_data`
GRANT TO ("group:sales@company.com")
FILTER USING (department = 'Sales')
```

---

#### 5.1.3 Assign Users to Policy

**Arquivo**: `pages/assign_users_to_policy.py`

**Funcionalidade**: Atribuir usuários específicos a políticas RLS existentes.

**Casos de Uso**:
- Novo funcionário precisa acesso a dados específicos
- Mudança de departamento requer atualização de políticas
- Acesso temporário para auditores/consultores

---

#### 5.1.4 Assign Values to Groups

**Arquivo**: `pages/assign_values_to_group.py`

**Funcionalidade**: Definir quais valores de filtro são permitidos para cada grupo.

**Exemplo**:
- Grupo "Sales_Brazil" → Filtro: `country = 'Brazil'`
- Grupo "Sales_LATAM" → Filtro: `region IN ('Brazil', 'Argentina', 'Chile')`

---

### 5.2 Módulo CLS (Column-Level Security)

#### 5.2.1 Manage Taxonomies

**Arquivo**: `pages/cls_taxonomies.py` (v1.0)

**Funcionalidade**: CRUD completo de taxonomias no Data Catalog.

**Features**:
- Listar todas as taxonomias do projeto
- Criar nova taxonomia
- Editar display name e descrição
- Deletar taxonomia (com confirmação)
- Visualizar contagem de policy tags

**Interface**:
```python
def taxonomies_page():
    """Página de gerenciamento de taxonomias"""
    
    with frame('Manage Taxonomies'):
        # Header com botão criar
        with ui.row().classes('w-full justify-between'):
            ui.label('Taxonomies').classes('text-2xl')
            ui.button('+ Create Taxonomy', on_click=show_create_dialog)
        
        # Grid de taxonomies
        def refresh_taxonomies():
            service = DataCatalogService()
            taxonomies = service.list_taxonomies()
            
            with ui.grid(columns=3).classes('w-full gap-4'):
                for tax in taxonomies:
                    with ui.card():
                        ui.label(tax.display_name).classes('font-bold')
                        ui.label(f'{tax.policy_tag_count} tags')
                        
                        with ui.row():
                            ui.button('Edit', on_click=lambda t=tax: edit_taxonomy(t))
                            ui.button('Delete', on_click=lambda t=tax: delete_taxonomy(t))
```

---

#### 5.2.2 Manage Policy Tags

**Arquivo**: `pages/cls_policy_tags.py` (v1.0)

**Funcionalidade**: CRUD de policy tags dentro de taxonomias.

**Hierarquia Suportada**:
```
Taxonomy: PII
  ├─ PII_HIGH
  │  ├─ PII_HIGH_SSN
  │  └─ PII_HIGH_CREDIT_CARD
  └─ PII_MEDIUM
     ├─ PII_MEDIUM_EMAIL
     └─ PII_MEDIUM_PHONE
```

**Código de Criação**:
```python
def create_policy_tag(taxonomy_id: str, display_name: str, parent_tag_id: Optional[str] = None):
    """Criar policy tag"""
    
    service = DataCatalogService()
    
    # Criar tag
    policy_tag = service.create_policy_tag(
        taxonomy_id=taxonomy_id,
        display_name=display_name,
        description=f'Policy tag: {display_name}',
        parent_policy_tag=parent_tag_id
    )
    
    # Audit log
    AuditService.log_operation(
        operation='CREATE_POLICY_TAG',
        resource=taxonomy_id,
        details={
            'tag_name': display_name,
            'parent': parent_tag_id
        }
    )
    
    return policy_tag
```

---

#### 5.2.3 Apply Tags to Columns

**Arquivo**: `pages/cls_apply_tags.py` (v1.0)

**Funcionalidade**: Aplicar policy tags em colunas de tabelas BigQuery.

**Interface**:
1. Selecionar dataset
2. Selecionar tabela
3. Visualizar todas as colunas
4. Para cada coluna:
   - Ver tipo de dado
   - Ver tag atual (se houver)
   - Selecionar nova tag
   - Aplicar ou remover

**Estatísticas Exibidas**:
- Total de colunas na tabela
- Colunas com tags aplicadas
- Colunas sem proteção
- Percentual de cobertura

**Código de Aplicação**:
```python
def apply_tag_to_column(dataset_id: str, table_id: str, column_name: str, policy_tag_id: str):
    """Aplicar policy tag em coluna"""
    
    service = BigQueryCLSService()
    
    # Buscar schema atual
    table = service.get_table(f'{dataset_id}.{table_id}')
    schema = table.schema
    
    # Modificar schema da coluna
    new_schema = []
    for field in schema:
        if field.name == column_name:
            # Adicionar policy tag
            new_field = field.to_api_repr()
            new_field['policyTags'] = {'names': [policy_tag_id]}
            new_schema.append(bigquery.SchemaField.from_api_repr(new_field))
        else:
            new_schema.append(field)
    
    # Atualizar tabela
    table.schema = new_schema
    service.update_table(table)
    
    # Audit log
    AuditService.log_operation(
        operation='APPLY_POLICY_TAG',
        resource=f'{dataset_id}.{table_id}.{column_name}',
        details={'policy_tag_id': policy_tag_id}
    )
```

---

#### 5.2.4 Policy Tag Permissions

**Arquivo**: `pages/cls_apply_iam.py` (v1.0)

**Funcionalidade**: Gerenciar permissões IAM por policy tag.

**Conceito**: Uma vez que uma coluna tem uma policy tag, é preciso dar permissão aos usuários para acessar dados dessa tag.

**Permissões**:
- `roles/datacatalog.categoryFineGrainedReader`: Permite ler dados com a tag
- Custom roles: Criar roles customizadas por necessidade

**Interface**:
```python
def manage_tag_permissions(policy_tag_id: str):
    """Gerenciar permissões de uma policy tag"""
    
    service = DataCatalogService()
    
    # Buscar policy IAM atual
    policy = service.get_tag_iam_policy(policy_tag_id)
    
    # Exibir bindings atuais
    with ui.card():
        ui.label('Current Permissions').classes('font-bold')
        
        for binding in policy.bindings:
            with ui.expansion(binding.role):
                for member in binding.members:
                    with ui.row():
                        ui.label(member)
                        ui.button('Remove', on_click=lambda m=member: remove_member(m))
        
        # Adicionar novo membro
        with ui.row():
            email_input = ui.input('User/Group Email')
            role_select = ui.select(['Reader', 'Admin'], value='Reader')
            ui.button('Add', on_click=lambda: add_member(email_input.value, role_select.value))
```

---

#### 5.2.5 Schema Browser

**Arquivo**: `pages/cls_schema_browser.py` (v1.0)

**Funcionalidade**: Navegar por datasets/tabelas e visualizar quais colunas têm policy tags aplicadas.

**Visualização**:
```
📂 Dataset: analytics
  ├─ 📊 Table: users (5 columns)
  │   ├─ 🔓 user_id (INT64) - No tag
  │   ├─ 🔓 name (STRING) - No tag
  │   ├─ 🔒 email (STRING) - Tag: PII_HIGH
  │   ├─ 🔒 phone (STRING) - Tag: PII_MEDIUM
  │   └─ 🔓 created_at (TIMESTAMP) - No tag
  └─ 📊 Table: transactions (12 columns)
      ├─ ...
```

**Estatísticas por Tabela**:
- Total de colunas
- Colunas protegidas
- Colunas desprotegidas
- % de cobertura

---

#### 5.2.6 Create Protected View

**Arquivo**: `pages/cls_dynamic_columns.py` (v1.0)

**Funcionalidade**: Criar views protegidas com mascaramento dinâmico de colunas.

**Conceito**: Em vez de aplicar policy tags diretamente na tabela, criar uma view que mascara colunas sensíveis baseado nas permissões do usuário.

**SQL Gerado**:
```sql
CREATE OR REPLACE VIEW `project.dataset.users_protected` AS
SELECT
  user_id,
  name,
  CASE 
    WHEN SESSION_USER() IN (
      SELECT member FROM `project.dataset.authorized_users`
      WHERE policy = 'PII_ACCESS'
    )
    THEN email
    ELSE '***@***.com'
  END AS email,
  created_at
FROM `project.dataset.users`
```

---

### 5.3 Módulo Audit Logs

**Arquivo**: `pages/audit_logs.py`

**Funcionalidade**: Visualizar e filtrar todos os logs de operações de segurança.

**Operações Registradas**:
- CREATE_RLS_POLICY
- DELETE_RLS_POLICY
- CREATE_TAXONOMY
- DELETE_TAXONOMY
- CREATE_POLICY_TAG
- DELETE_POLICY_TAG
- APPLY_POLICY_TAG
- REMOVE_POLICY_TAG
- UPDATE_IAM_POLICY
- CREATE_PROTECTED_VIEW

**Estrutura do Log**:
```json
{
  "timestamp": "2025-12-04T15:30:00Z",
  "user": "user@company.com",
  "operation": "APPLY_POLICY_TAG",
  "resource": "analytics.users.email",
  "details": {
    "policy_tag_id": "projects/123/locations/us/taxonomies/456/policyTags/789",
    "policy_tag_name": "PII_HIGH"
  },
  "status": "SUCCESS"
}
```

**Interface de Filtros**:
- Por usuário
- Por operação
- Por resource (dataset/table/column)
- Por data (range)
- Por status (SUCCESS/FAILURE)

---

### 5.4 Camada de Serviços

#### 5.4.1 BigQueryRLSService

**Arquivo**: `services/bigquery_rls_service.py`

**Principais Métodos**:

```python
class BigQueryRLSService:
    """Serviço para operações RLS no BigQuery"""
    
    def __init__(self):
        self.client = bigquery.Client(project=Config.PROJECT_ID)
    
    def create_policy(
        self,
        dataset_id: str,
        table_id: str,
        policy_name: str,
        filter_expression: str,
        grantees: List[str]
    ) -> None:
        """Criar política RLS"""
        
        grantees_str = ', '.join([f'"{g}"' for g in grantees])
        
        sql = f"""
        CREATE OR REPLACE ROW ACCESS POLICY {policy_name}
        ON `{Config.PROJECT_ID}.{dataset_id}.{table_id}`
        GRANT TO ({grantees_str})
        FILTER USING ({filter_expression})
        """
        
        self.client.query(sql).result()
    
    def list_policies(self, dataset_id: str, table_id: str) -> List[Dict]:
        """Listar políticas de uma tabela"""
        
        sql = f"""
        SELECT * FROM `{Config.PROJECT_ID}.{dataset_id}.INFORMATION_SCHEMA.ROW_ACCESS_POLICIES`
        WHERE table_name = '{table_id}'
        """
        
        results = self.client.query(sql).result()
        return [dict(row) for row in results]
    
    def delete_policy(
        self,
        dataset_id: str,
        table_id: str,
        policy_name: str
    ) -> None:
        """Deletar política RLS"""
        
        sql = f"""
        DROP ROW ACCESS POLICY {policy_name}
        ON `{Config.PROJECT_ID}.{dataset_id}.{table_id}`
        """
        
        self.client.query(sql).result()
```

---

#### 5.4.2 DataCatalogService

**Arquivo**: `services/datacatalog_service.py` (v1.0)

**Principais Métodos**:

```python
class DataCatalogService:
    """Serviço para operações no Data Catalog"""
    
    def __init__(self):
        self.client = datacatalog_v1.PolicyTagManagerClient()
        self.parent = f"projects/{Config.PROJECT_ID}/locations/{Config.LOCATION}"
    
    def list_taxonomies(self) -> List[datacatalog_v1.Taxonomy]:
        """Listar todas as taxonomias"""
        
        request = datacatalog_v1.ListTaxonomiesRequest(parent=self.parent)
        taxonomies = self.client.list_taxonomies(request=request)
        return list(taxonomies)
    
    def create_taxonomy(
        self,
        display_name: str,
        description: str = ""
    ) -> datacatalog_v1.Taxonomy:
        """Criar nova taxonomia"""
        
        taxonomy = datacatalog_v1.Taxonomy(
            display_name=display_name,
            description=description
        )
        
        request = datacatalog_v1.CreateTaxonomyRequest(
            parent=self.parent,
            taxonomy=taxonomy
        )
        
        return self.client.create_taxonomy(request=request)
    
    def create_policy_tag(
        self,
        taxonomy_id: str,
        display_name: str,
        description: str = "",
        parent_policy_tag: Optional[str] = None
    ) -> datacatalog_v1.PolicyTag:
        """Criar policy tag"""
        
        policy_tag = datacatalog_v1.PolicyTag(
            display_name=display_name,
            description=description
        )
        
        if parent_policy_tag:
            policy_tag.parent_policy_tag = parent_policy_tag
        
        request = datacatalog_v1.CreatePolicyTagRequest(
            parent=taxonomy_id,
            policy_tag=policy_tag
        )
        
        return self.client.create_policy_tag(request=request)
    
    def get_tag_iam_policy(self, policy_tag_id: str) -> Policy:
        """Obter policy IAM de uma tag"""
        
        request = GetIamPolicyRequest(resource=policy_tag_id)
        return self.client.get_iam_policy(request=request)
    
    def set_tag_iam_policy(
        self,
        policy_tag_id: str,
        policy: Policy
    ) -> Policy:
        """Configurar policy IAM de uma tag"""
        
        request = SetIamPolicyRequest(
            resource=policy_tag_id,
            policy=policy
        )
        
        return self.client.set_iam_policy(request=request)
```

---

#### 5.4.3 BigQueryCLSService

**Arquivo**: `services/bigquery_cls_service.py` (v1.0)

**Principais Métodos**:

```python
class BigQueryCLSService:
    """Serviço para operações CLS no BigQuery"""
    
    def __init__(self):
        self.client = bigquery.Client(project=Config.PROJECT_ID)
    
    def list_datasets(self) -> List[str]:
        """Listar datasets do projeto"""
        
        datasets = self.client.list_datasets()
        return [dataset.dataset_id for dataset in datasets]
    
    def list_tables(self, dataset_id: str) -> List[str]:
        """Listar tabelas de um dataset"""
        
        dataset_ref = self.client.dataset(dataset_id)
        tables = self.client.list_tables(dataset_ref)
        return [table.table_id for table in tables]
    
    def get_table_schema(
        self,
        dataset_id: str,
        table_id: str
    ) -> List[bigquery.SchemaField]:
        """Obter schema de uma tabela"""
        
        table_ref = f'{Config.PROJECT_ID}.{dataset_id}.{table_id}'
        table = self.client.get_table(table_ref)
        return table.schema
    
    def apply_tag_to_column(
        self,
        dataset_id: str,
        table_id: str,
        column_name: str,
        policy_tag_id: str
    ) -> None:
        """Aplicar policy tag em coluna"""
        
        table_ref = f'{Config.PROJECT_ID}.{dataset_id}.{table_id}'
        table = self.client.get_table(table_ref)
        
        # Modificar schema
        new_schema = []
        for field in table.schema:
            if field.name == column_name:
                # Criar novo field com policy tag
                field_dict = field.to_api_repr()
                field_dict['policyTags'] = {'names': [policy_tag_id]}
                new_field = bigquery.SchemaField.from_api_repr(field_dict)
                new_schema.append(new_field)
            else:
                new_schema.append(field)
        
        # Atualizar tabela
        table.schema = new_schema
        self.client.update_table(table, ['schema'])
    
    def remove_tag_from_column(
        self,
        dataset_id: str,
        table_id: str,
        column_name: str
    ) -> None:
        """Remover policy tag de coluna"""
        
        table_ref = f'{Config.PROJECT_ID}.{dataset_id}.{table_id}'
        table = self.client.get_table(table_ref)
        
        # Modificar schema
        new_schema = []
        for field in table.schema:
            if field.name == column_name:
                # Criar field sem policy tag
                field_dict = field.to_api_repr()
                field_dict.pop('policyTags', None)
                new_field = bigquery.SchemaField.from_api_repr(field_dict)
                new_schema.append(new_field)
            else:
                new_schema.append(field)
        
        # Atualizar tabela
        table.schema = new_schema
        self.client.update_table(table, ['schema'])
    
    def get_columns_with_tags(
        self,
        dataset_id: str,
        table_id: str
    ) -> Dict[str, Optional[str]]:
        """Obter mapeamento coluna -> policy tag"""
        
        schema = self.get_table_schema(dataset_id, table_id)
        
        result = {}
        for field in schema:
            policy_tags = field.policy_tags
            if policy_tags and policy_tags.names:
                result[field.name] = policy_tags.names[0]
            else:
                result[field.name] = None
        
        return result
```

---

#### 5.4.4 AuditService

**Arquivo**: `services/audit_service.py`

**Principais Métodos**:

```python
class AuditService:
    """Serviço de auditoria"""
    
    @staticmethod
    def log_operation(
        operation: str,
        resource: str,
        user: str,
        details: Optional[Dict] = None,
        status: str = 'SUCCESS'
    ) -> None:
        """Registrar operação no audit log"""
        
        import logging
        from google.cloud import logging as cloud_logging
        
        # Configurar Cloud Logging
        client = cloud_logging.Client()
        logger = client.logger('rls-cls-security-audit')
        
        # Montar log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user': user,
            'operation': operation,
            'resource': resource,
            'details': details or {},
            'status': status
        }
        
        # Enviar para Cloud Logging
        logger.log_struct(log_entry, severity='INFO')
    
    @staticmethod
    def query_logs(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Consultar audit logs"""
        
        from google.cloud import logging as cloud_logging
        
        client = cloud_logging.Client()
        logger = client.logger('rls-cls-security-audit')
        
        # Montar filtro
        filters = []
        if start_time:
            filters.append(f'timestamp>="{start_time.isoformat()}"')
        if end_time:
            filters.append(f'timestamp<="{end_time.isoformat()}"')
        if user:
            filters.append(f'jsonPayload.user="{user}"')
        if operation:
            filters.append(f'jsonPayload.operation="{operation}"')
        
        filter_str = ' AND '.join(filters)
        
        # Buscar logs
        entries = client.list_entries(
            filter_=filter_str,
            max_results=limit,
            order_by=cloud_logging.DESCENDING
        )
        
        return [entry.payload for entry in entries]
```

---

## 6. SISTEMA DE UI/UX (v2.0)

### 6.1 Tema HUD/Sci-Fi

**Arquivo**: `theme.py` (v2.0)

**Conceito**: Tema visual inspirado em interfaces HUD (Heads-Up Display) de jogos sci-fi como Halo, Cyberpunk 2077 e Tron.

**Características**:
- Background escuro (#0a0f1a)
- Cor primária: Ciano neon (#00f3ff)
- Glassmorphism effects
- Grid de fundo sutil
- Animações suaves
- Elementos decorativos técnicos

**Implementação**:
```python
def _apply_global_theme():
    """Aplica tema HUD/Sci-Fi globalmente"""
    
    ui.add_head_html('''
        <style>
            :root {
                /* Colors */
                --hud-color: #00f3ff;
                --bg-primary: #0a0f1a;
                --bg-secondary: #050810;
                --text-main: #ffffff;
                --text-dim: #94a3b8;
                
                /* Spacing */
                --spacing-sm: 0.5rem;
                --spacing-md: 1rem;
                --spacing-lg: 1.5rem;
                
                /* Transitions */
                --transition-fast: 0.15s ease;
                --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                --transition-slow: 0.5s ease-in-out;
            }
            
            /* Global Styles */
            body, .nicegui-content {
                background: linear-gradient(
                    135deg,
                    var(--bg-primary) 0%,
                    var(--bg-secondary) 50%,
                    var(--bg-primary) 100%
                ) !important;
                color: var(--text-main) !important;
            }
            
            /* Grid Background */
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image:
                    linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
                background-size: 50px 50px;
                opacity: 0.5;
                pointer-events: none;
                z-index: 0;
            }
            
            /* Header */
            .q-header {
                background: linear-gradient(
                    90deg,
                    var(--bg-primary) 0%,
                    #1a2535 100%
                ) !important;
                border-bottom: 1px solid rgba(0, 243, 255, 0.3) !important;
                box-shadow: 0 4px 20px rgba(0, 243, 255, 0.15) !important;
            }
            
            /* Sidebar */
            .q-drawer {
                background: rgba(10, 15, 26, 0.95) !important;
                border-right: 1px solid rgba(0, 243, 255, 0.3) !important;
                backdrop-filter: blur(10px) !important;
            }
            
            /* Cards */
            .q-card {
                background: rgba(15, 25, 35, 0.9) !important;
                border: 1px solid rgba(0, 243, 255, 0.2) !important;
                box-shadow: 0 0 20px rgba(0, 243, 255, 0.1) !important;
                border-radius: 8px !important;
                transition: var(--transition-normal);
            }
            
            .q-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 0 30px rgba(0, 243, 255, 0.2) !important;
                border-color: rgba(0, 243, 255, 0.4) !important;
            }
            
            /* Buttons */
            .q-btn {
                border-radius: 6px !important;
                transition: var(--transition-normal);
            }
            
            .q-btn:hover {
                background: rgba(0, 243, 255, 0.1) !important;
                box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
            }
            
            /* Inputs */
            .q-field__control {
                background: rgba(15, 25, 35, 0.5) !important;
                border: 1px solid rgba(0, 243, 255, 0.2) !important;
                border-radius: 6px !important;
            }
            
            .q-field__control:focus-within {
                border-color: var(--hud-color) !important;
                box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
            }
            
            /* Tables */
            .q-table thead {
                background: rgba(0, 243, 255, 0.05) !important;
            }
            
            .q-table tbody tr:hover {
                background: rgba(0, 243, 255, 0.08) !important;
            }
            
            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 243, 255, 0.2);
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--hud-color);
            }
            
            /* Menu Items */
            .q-item:hover {
                background: rgba(0, 243, 255, 0.1) !important;
                transform: translateX(4px);
            }
        </style>
    ''')
    
    # Configurar cores do Quasar
    ui.colors(
        primary='#00f3ff',
        secondary='#5B9FED',
        accent='#00f3ff',
        dark='#0a0f1a',
        positive='#10b981',
        negative='#ef4444',
        info='#3b82f6',
        warning='#f59e0b'
    )
    
    # Ativar dark mode
    ui.dark_mode().enable()
```

---

### 6.2 Login Page

**Arquivo**: `static/login.html` (v2.0)

**Por que HTML Puro?**
- NiceGUI causava conflitos de CSS
- Necessidade de controle total sobre o design
- Performance: 75% mais rápido
- Facilidade de manutenção

**Estrutura do Login**:
```html
<body>
    <!-- Background decorativo -->
    <div class="tech-bg">
        <!-- Grid milimétrico -->
        <div class="grid-overlay"></div>
        
        <!-- Hexágonos animados -->
        <div class="hexagon hex-1"></div>
        <div class="hexagon hex-2"></div>
        <div class="hexagon hex-3"></div>
        
        <!-- Círculos técnicos -->
        <div class="hud-circle-outer"></div>
        <div class="hud-circle-inner"></div>
        
        <!-- Crosshair -->
        <div class="hud-crosshair"></div>
        
        <!-- Card principal com glassmorphism -->
        <div class="glass-card">
            <!-- Ícone BigQuery + Shield -->
            <div class="bigquery-icon">
                <div class="hex-shield"></div>
            </div>
            
            <!-- Título -->
            <div class="title">GenAI4Data</div>
            <div class="subtitle">Controle de Acesso ao Sistema</div>
            
            <!-- Botão Google -->
            <button class="google-btn" onclick="loginWithGoogle()">
                <svg><!-- Google icon --></svg>
                Entrar com Google
            </button>
            
            <!-- Footer -->
            <div class="footer">SYS_MANAGER | SEC_MODULE_V2</div>
        </div>
        
        <!-- Scanlines CRT effect -->
        <div class="scanlines"></div>
    </div>
</body>
```

**CSS Highlights**:
```css
/* Glass Card */
.glass-card {
    background: rgba(5, 10, 15, 0.85);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(0, 243, 255, 0.3);
    clip-path: polygon(
        15px 0%, 100% 0%, 100% calc(100% - 15px),
        calc(100% - 15px) 100%, 0% 100%, 0% 15px
    );
    box-shadow:
        0 0 40px rgba(0, 243, 255, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Hexágonos animados */
.hexagon {
    width: 100px;
    height: 115px;
    background: rgba(0, 243, 255, 0.05);
    border: 1px solid rgba(0, 243, 255, 0.2);
    clip-path: polygon(
        50% 0%, 100% 25%, 100% 75%, 
        50% 100%, 0% 75%, 0% 25%
    );
    animation: float 6s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(10deg); }
}

/* Círculos técnicos */
.hud-circle-outer {
    width: 300px;
    height: 300px;
    border: 2px solid rgba(0, 243, 255, 0.2);
    border-radius: 50%;
    animation: rotate 20s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

---

### 6.3 Design System

**Paleta de Cores**:
```css
/* Primary Colors */
--hud-color: #00f3ff;          /* Ciano Neon - Accent principal */
--bg-primary: #0a0f1a;         /* Preto azulado - Background */
--bg-secondary: #050810;       /* Preto mais escuro - Gradientes */
--text-main: #ffffff;          /* Branco - Textos principais */
--text-dim: #94a3b8;           /* Cinza claro - Textos secundários */

/* Functional Colors */
--status-success: #10b981;     /* Verde - Sucesso */
--status-warning: #f59e0b;     /* Amarelo/Laranja - Aviso */
--status-error: #ef4444;       /* Vermelho - Erro */
--status-info: #3b82f6;        /* Azul - Informação */
--status-audit: #a855f7;       /* Roxo - Audit logs */

/* Menu Colors (v2.0) */
--menu-home: #00f3ff;          /* Ciano - Home */
--menu-rls: #10b981;           /* Verde - RLS */
--menu-cls: #f59e0b;           /* Amarelo - CLS */
--menu-iam: #ef4444;           /* Vermelho - IAM */
--menu-audit: #a855f7;         /* Roxo - Audit */
```

**Tipografia**:
```css
/* Font Families */
--font-main: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Font Sizes */
--text-xs: 0.75rem;      /* 12px - Footer, badges */
--text-sm: 0.875rem;     /* 14px - Descrições */
--text-base: 1rem;       /* 16px - Body text */
--text-lg: 1.125rem;     /* 18px - Cards */
--text-xl: 1.25rem;      /* 20px - Subtítulos */
--text-2xl: 1.5rem;      /* 24px - Títulos de seção */
--text-3xl: 1.875rem;    /* 30px - Títulos de página */
--text-4xl: 2.25rem;     /* 36px - Títulos principais */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

**Spacing**:
```css
/* Spacing Scale */
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-2xl: 3rem;     /* 48px */
--spacing-3xl: 4rem;     /* 64px */
```

**Border Radius**:
```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-xl: 12px;
--radius-2xl: 16px;
--radius-full: 9999px;
```

**Transitions**:
```css
--transition-fast: 0.15s ease;
--transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 0.5s ease-in-out;
```

---

### 6.4 Componentes Interativos

#### Home Feature Cards (v2.0)

**Arquivo**: `home.py`

**5 Cards Interativos**:
1. Row-Level Security
2. Column-Level Security
3. Data Masking
4. IAM Policy Control
5. Audit & Compliance

**Hover Effects**:
```python
# CSS para hover effects
ui.add_head_html('''
    <style>
        .feature-card {
            width: 280px;
            padding: 1.5rem;
            background: rgba(15, 25, 35, 0.85);
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        
        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: rgba(0, 243, 255, 0.5);
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.3),
                        0 10px 40px rgba(0, 0, 0, 0.5);
            background: rgba(15, 25, 35, 0.95);
        }
        
        .feature-card:hover .q-icon {
            transform: scale(1.15) rotate(5deg);
            filter: drop-shadow(0 0 15px rgba(0, 243, 255, 0.6));
        }
    </style>
''')
```

**Efeitos Aplicados**:
- ⬆️ Levanta 8px
- 🔍 Aumenta 2% (scale 1.02)
- 💡 Borda intensifica (0.2 → 0.5 opacity)
- ✨ Glow ciano (30px)
- 🌟 Background opacidade aumenta
- 🎯 Ícone aumenta 15% + rotaciona 5°
- 💫 Drop-shadow no ícone

---

#### Menu Color-Coded (v2.0)

**Arquivo**: `menu.py`

**Cores por Seção**:
```python
# Home - Ciano
ui.icon('home').style('color: #00f3ff;')

# RLS - Verde
ui.icon('policy').style('color: #ffffff;')  # Título branco
ui.icon('person').style('color: #10b981;')  # Submenus verdes
ui.icon('groups').style('color: #10b981;')
ui.icon('assignment_ind').style('color: #10b981;')
ui.icon('assignment').style('color: #10b981;')

# CLS - Amarelo
ui.icon('security').style('color: #ffffff;')  # Título branco
ui.icon('folder').style('color: #f59e0b;')    # Submenus amarelos
ui.icon('label').style('color: #f59e0b;')
ui.icon('build').style('color: #f59e0b;')
# ... (7 ícones amarelos total)

# IAM - Vermelho
ui.icon('admin_panel_settings').style('color: #ffffff;')
ui.icon('storage').style('color: #ef4444;')
ui.icon('shield').style('color: #ef4444;')
ui.icon('lock').style('color: #ef4444;')

# Audit - Roxo
ui.icon('history').style('color: #a855f7;')
```

---

## 7. DECISÕES TÉCNICAS

### 7.1 Por que NiceGUI?

**Razões para Escolher NiceGUI**:

1. **Python Puro**
   - Sem necessidade de escrever JavaScript
   - Backend e frontend na mesma linguagem
   - Tipagem forte com Python type hints

2. **Produtividade**
   - Desenvolvimento 3x mais rápido que frameworks JS
   - Menos context switching
   - Menos código boilerplate

3. **Reatividade Nativa**
   - UI atualiza automaticamente quando variáveis mudam
   - Sem necessidade de gerenciar estado manualmente
   - Binding bidirecional out-of-the-box

4. **Integração com Google Cloud**
   - Mesma linguagem dos SDKs do GCP
   - Fácil integração com BigQuery e Data Catalog
   - Autenticação OAuth simplificada

5. **Deploy Simples**
   - Um único container Docker
   - Sem build steps complexos
   - Escalável no Cloud Run

**Trade-offs**:
- Performance: Slightly slower than React/Vue para apps muito complexas
- Comunidade: Menor que frameworks mainstream
- Customização: Algumas limitações de UI (resolvido com HTML puro no login)

---

### 7.2 Por que Cloud Run?

**Razões para Escolher Cloud Run**:

1. **Serverless**
   - Sem gerenciamento de servidores
   - Escala automática (0 → N instances)
   - Pay-per-use (custo apenas quando usado)

2. **Integração GCP**
   - Service Account nativo
   - VPC connector para acesso privado
   - Logs centralizados no Cloud Logging

3. **Deploy Simplificado**
   - `gcloud run deploy --source .`
   - CI/CD com Cloud Build
   - Rollback instantâneo

4. **Performance**
   - Cold start ~2s (aceitável para admin UI)
   - Request timeout configurável (até 1h)
   - Escalabilidade horizontal automática

5. **Custo**
   - Free tier: 2M requests/mês
   - Custo baixo para apps admin
   - Sem infraestrutura ociosa

**Comparação com Alternativas**:

| Aspecto | Cloud Run | GKE | App Engine | Compute Engine |
|---------|-----------|-----|------------|----------------|
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Custo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Escala** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Manutenção** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

### 7.3 Por que HTML Puro no Login? (v2.0)

**Problema Identificado**:
```
NiceGUI Login Page → CSS Conflicts → Elements não renderizavam corretamente
```

**Tentativas de Solução**:
1. ❌ Override CSS do NiceGUI → Conflitos persistiam
2. ❌ Usar !important → Poluía o código
3. ❌ Shadow DOM → Incompatível com NiceGUI
4. ✅ HTML puro servido por FastAPI → **SOLUÇÃO**

**Benefícios do HTML Puro**:

**Controle Total**:
```html
<!-- 100% controle sobre cada pixel -->
<style>
    .glass-card {
        /* Exatamente como desejado */
        background: rgba(5, 10, 15, 0.85);
        backdrop-filter: blur(20px);
        /* Sem interferências */
    }
</style>
```

**Performance**:
- Antes: ~800ms load time
- Depois: ~200ms load time
- **Melhoria: 75% mais rápido**

**Zero Conflitos**:
- Sem CSS do NiceGUI interferindo
- Sem JavaScript framework overhead
- Apenas HTML, CSS e vanilla JS

**Facilidade de Manutenção**:
- Um único arquivo (`login.html`)
- CSS inline (não precisa de bundler)
- JavaScript vanilla (sem dependências)

**Implementação**:
```python
# main.py (v2.0)
@app.get('/login', response_class=HTMLResponse)
async def serve_login_html():
    """Serve HTML puro sem NiceGUI"""
    
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'login.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Injetar variáveis de ambiente
    html_content = html_content.replace('{{GOOGLE_CLIENT_ID}}', GOOGLE_CLIENT_ID)
    html_content = html_content.replace('{{REDIRECT_URI}}', REDIRECT_URI)
    
    return HTMLResponse(content=html_content)
```

---

### 7.4 Padrões de Design

#### 7.4.1 Service Layer Pattern

**Conceito**: Separar lógica de negócio (services) da apresentação (pages).

**Benefícios**:
- Reutilização de código
- Testabilidade
- Manutenibilidade
- Separação de responsabilidades

**Exemplo**:
```python
# ❌ SEM Service Layer (ruim)
@ui.page('/create-rls')
def create_rls_page():
    def on_create():
        # Lógica de negócio misturada com UI
        client = bigquery.Client()
        sql = f"CREATE ROW ACCESS POLICY..."
        client.query(sql).result()
        
        # Logging misturado
        logger.info(f"Created policy...")
        
        ui.notify('Success!')

# ✅ COM Service Layer (bom)
@ui.page('/create-rls')
def create_rls_page():
    def on_create():
        # UI apenas chama o serviço
        service = BigQueryRLSService()
        service.create_policy(...)
        
        ui.notify('Success!')

# Service isolado e testável
class BigQueryRLSService:
    def create_policy(self, ...):
        # Lógica pura, sem UI
        client = self.get_client()
        sql = self._build_sql(...)
        client.query(sql).result()
        self._log_operation(...)
```

---

#### 7.4.2 Dependency Injection

**Conceito**: Injetar dependências em vez de criá-las internamente.

**Benefícios**:
- Testabilidade (mock dependencies)
- Flexibilidade (trocar implementações)
- Desacoplamento

**Exemplo**:
```python
# ❌ SEM Dependency Injection (ruim)
class BigQueryRLSService:
    def __init__(self):
        # Cria dependência internamente (acoplamento)
        self.client = bigquery.Client()
    
    def create_policy(self, ...):
        self.client.query(...)

# ✅ COM Dependency Injection (bom)
class BigQueryRLSService:
    def __init__(self, client: bigquery.Client = None):
        # Recebe dependência (desacoplamento)
        self.client = client or self._create_default_client()
    
    def _create_default_client(self):
        return bigquery.Client()
    
    def create_policy(self, ...):
        self.client.query(...)

# Facilita testes
def test_create_policy():
    mock_client = Mock(spec=bigquery.Client)
    service = BigQueryRLSService(client=mock_client)
    service.create_policy(...)
    mock_client.query.assert_called_once()
```

---

#### 7.4.3 Error Handling Pattern

**Conceito**: Tratar erros de forma consistente em toda aplicação.

**Implementação**:
```python
# services/base_service.py
class BaseService:
    """Classe base para todos os services"""
    
    def _execute_with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ):
        """Executa função com retry exponencial"""
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    # Última tentativa, propaga erro
                    self._log_error(e)
                    raise
                
                # Aguarda antes de tentar novamente
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)
    
    def _log_error(self, error: Exception):
        """Log estruturado de erros"""
        
        import traceback
        
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.error('Service error', extra=error_details)

# Uso nos services
class BigQueryRLSService(BaseService):
    def create_policy(self, ...):
        return self._execute_with_retry(
            lambda: self._create_policy_impl(...)
        )
```

---

## 8. DESAFIOS E SOLUÇÕES

### 8.1 Remoção de Policy Tags

**Desafio**: A API do Data Catalog não possui método direto para remover policy tags de colunas.

**Solução Implementada**:
```python
def remove_tag_from_column(dataset_id, table_id, column_name):
    """Remove policy tag de coluna modificando o schema"""
    
    # 1. Buscar tabela
    table = client.get_table(f'{dataset_id}.{table_id}')
    
    # 2. Clonar schema excluindo policy tag
    new_schema = []
    for field in table.schema:
        if field.name == column_name:
            # Criar field sem policy tags
            field_dict = field.to_api_repr()
            field_dict.pop('policyTags', None)  # Remove chave
            new_field = bigquery.SchemaField.from_api_repr(field_dict)
            new_schema.append(new_field)
        else:
            new_schema.append(field)
    
    # 3. Atualizar tabela com novo schema
    table.schema = new_schema
    client.update_table(table, ['schema'])
```

**Lições Aprendidas**:
- Sempre trabalhar com cópia do schema
- Validar schema antes de aplicar
- Fazer backup do schema original

---

### 8.2 Logging em Cloud Run

**Desafio**: Logs do `print()` não apareciam no Cloud Logging.

**Causa**: Cloud Run captura apenas logs estruturados ou stdout corretamente formatado.

**Solução**:
```python
import logging
from google.cloud import logging as cloud_logging

# Configurar Cloud Logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()

# Configurar logger Python
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Agora funciona
logger.info('This appears in Cloud Logging')
logger.error('This too', extra={'user': 'user@example.com'})
```

**Benefícios**:
- Logs estruturados (JSON)
- Campos customizados (extra)
- Níveis de severidade (INFO, ERROR, etc)
- Integração com Error Reporting

---

### 8.3 Schema Dinâmico do BigQuery

**Desafio**: Ao aplicar policy tags, schema pode mudar dinamicamente (colunas adicionadas/removidas).

**Problema**:
```python
# Schema pode ter mudado desde última leitura
schema = get_table_schema(...)
# ... (tempo passa)
update_table_schema(schema)  # ❌ Pode sobrescrever mudanças
```

**Solução - Optimistic Locking**:
```python
def apply_tag_with_lock(dataset_id, table_id, column_name, tag_id):
    """Aplicar tag com verificação de versão"""
    
    max_retries = 3
    for attempt in range(max_retries):
        # 1. Buscar schema mais recente
        table = client.get_table(f'{dataset_id}.{table_id}')
        etag = table.etag  # Version tag
        
        # 2. Modificar schema
        new_schema = modify_schema(table.schema, column_name, tag_id)
        
        # 3. Tentar atualizar com etag
        table.schema = new_schema
        try:
            updated_table = client.update_table(
                table,
                ['schema'],
                # Atualiza apenas se etag ainda é válido
                if_etag_match=etag
            )
            return updated_table  # Sucesso!
        
        except Conflict:
            # Schema mudou, tentar novamente
            if attempt == max_retries - 1:
                raise
            time.sleep(0.5 * (attempt + 1))
```

---

### 8.4 CSS Conflicts no Login (v2.0)

**Desafio**: Login page em NiceGUI tinha conflitos de CSS.

**Tentativas**:
1. Override CSS → Não funcionou
2. !important → Poluiu código
3. Shadow DOM → Incompatível

**Solução Final - HTML Puro**:
```python
# main.py
@app.get('/login', response_class=HTMLResponse)
async def serve_login_html():
    # Serve HTML puro sem NiceGUI
    with open('static/login.html') as f:
        return HTMLResponse(f.read())
```

**Resultado**:
- ✅ Zero conflitos
- ✅ 75% mais rápido
- ✅ Controle total do design

---

## 9. SEGURANÇA E COMPLIANCE

### 9.1 Autenticação e Autorização

#### OAuth 2.0 com Google

**Fluxo de Autenticação**:
```
┌─────────┐         ┌─────────────┐         ┌──────────┐
│ Browser │         │ Application │         │  Google  │
└────┬────┘         └──────┬──────┘         └────┬─────┘
     │                     │                     │
     │ 1. Acessa /login    │                     │
     ├────────────────────>│                     │
     │                     │                     │
     │ 2. Redirect to      │                     │
     │    Google OAuth     │                     │
     │<────────────────────┤                     │
     │                     │                     │
     │ 3. Login com Google │                     │
     ├─────────────────────┴────────────────────>│
     │                                            │
     │ 4. Autoriza app                            │
     ├───────────────────────────────────────────>│
     │                                            │
     │ 5. Redirect to /callback?code=XXX          │
     │<───────────────────────────────────────────┤
     │                                            │
     │ 6. Envia code       │                      │
     ├────────────────────>│                      │
     │                     │ 7. Troca code por    │
     │                     │    access token      │
     │                     ├─────────────────────>│
     │                     │                      │
     │                     │ 8. Access token      │
     │                     │<─────────────────────┤
     │                     │                      │
     │                     │ 9. Busca user info   │
     │                     ├─────────────────────>│
     │                     │                      │
     │                     │ 10. User info        │
     │                     │<─────────────────────┤
     │                     │                      │
     │ 11. Cria sessão     │                      │
     │     + redirect /    │                      │
     │<────────────────────┤                      │
```

**Implementação**:
```python
# pages/login_page.py
from google.oauth2 import id_token
from google.auth.transport import requests

@ui.page('/callback')
def oauth_callback():
    """Callback OAuth do Google"""
    
    # 1. Extrair code da URL
    code = request.args.get('code')
    
    if not code:
        ui.notify('Authentication failed', type='negative')
        return ui.navigate.to('/login')
    
    try:
        # 2. Trocar code por tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': Config.GOOGLE_CLIENT_ID,
            'client_secret': Config.GOOGLE_CLIENT_SECRET,
            'redirect_uri': Config.REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        tokens = token_response.json()
        
        # 3. Validar ID token
        id_info = id_token.verify_oauth2_token(
            tokens['id_token'],
            requests.Request(),
            Config.GOOGLE_CLIENT_ID
        )
        
        # 4. Extrair info do usuário
        user_info = {
            'email': id_info['email'],
            'name': id_info.get('name', ''),
            'picture': id_info.get('picture', ''),
            'sub': id_info['sub']  # Google User ID
        }
        
        # 5. Determinar role baseado no email
        role = determine_user_role(user_info['email'])
        user_info['role'] = role
        
        # 6. Criar sessão
        app.storage.user['user_info'] = user_info
        app.storage.user['authenticated'] = True
        
        # 7. Audit log
        AuditService.log_operation(
            operation='USER_LOGIN',
            user=user_info['email'],
            resource='authentication',
            details={'role': role}
        )
        
        # 8. Redirect para home
        ui.navigate.to('/')
    
    except Exception as e:
        logger.error(f'OAuth error: {e}')
        ui.notify('Authentication failed', type='negative')
        ui.navigate.to('/login')

def determine_user_role(email: str) -> str:
    """Determina role do usuário"""
    
    # Exemplo: baseado no domínio
    if email.endswith('@sysmanager.com.br'):
        return 'OWNER'
    elif email.endswith('@company.com'):
        return 'ADMIN'
    else:
        return 'VIEWER'
```

---

#### Role-Based Access Control (RBAC)

**Roles Definidas**:
```python
# config.py
class Roles:
    OWNER = 'OWNER'      # Acesso total
    ADMIN = 'ADMIN'      # Gerenciar RLS/CLS
    EDITOR = 'EDITOR'    # Criar/editar políticas
    VIEWER = 'VIEWER'    # Apenas visualizar
```

**Permissões por Role**:
```python
PERMISSIONS = {
    'OWNER': [
        'view_all',
        'create_rls',
        'delete_rls',
        'create_cls',
        'delete_cls',
        'manage_iam',
        'control_access',
        'view_audit'
    ],
    'ADMIN': [
        'view_all',
        'create_rls',
        'create_cls',
        'manage_iam',
        'view_audit'
    ],
    'EDITOR': [
        'view_all',
        'create_rls',
        'create_cls',
        'view_audit'
    ],
    'VIEWER': [
        'view_all',
        'view_audit'
    ]
}
```

**Decorator para Proteção de Rotas**:
```python
# utils/decorators.py
from functools import wraps

def require_role(*required_roles):
    """Decorator para exigir role específica"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar se usuário está autenticado
            if not app.storage.user.get('authenticated'):
                ui.notify('Authentication required', type='warning')
                return ui.navigate.to('/login')
            
            # Verificar role
            user_role = app.storage.user.get('user_info', {}).get('role')
            
            if user_role not in required_roles:
                ui.notify('Insufficient permissions', type='negative')
                return ui.navigate.to('/')
            
            # Executar função
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Uso
@ui.page('/control-access')
@require_role('OWNER', 'ADMIN')
def control_access_page():
    """Apenas OWNER e ADMIN podem acessar"""
    with frame('Control Access'):
        # ... conteúdo da página
```

---

### 9.2 Proteção de Dados Sensíveis

#### Secrets Management

**Uso do Secret Manager**:
```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """Buscar secret do Secret Manager"""
    
    client = secretmanager.SecretManagerServiceClient()
    
    # Build resource name
    name = f"projects/{Config.PROJECT_ID}/secrets/{secret_id}/versions/latest"
    
    # Access secret
    response = client.access_secret_version(request={"name": name})
    
    # Decode payload
    return response.payload.data.decode('UTF-8')

# Carregar secrets no startup
Config.GOOGLE_CLIENT_SECRET = get_secret('google-oauth-client-secret')
Config.SESSION_SECRET = get_secret('session-secret-key')
```

---

#### Sensitive Data Masking

**Mascaramento em Logs**:
```python
import re

def mask_sensitive_data(text: str) -> str:
    """Mascarar dados sensíveis em logs"""
    
    # Email: preserva primeira letra + domínio
    text = re.sub(
        r'\b([a-zA-Z])[a-zA-Z0-9._-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        r'\1***@\2',
        text
    )
    
    # CPF: mostra apenas últimos 4 dígitos
    text = re.sub(r'\d{3}\.\d{3}\.\d{3}-(\d{2})', r'***.***.**-\1', text)
    
    # Cartão de crédito: mostra apenas últimos 4
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b', r'****-****-****-\1', text)
    
    return text

# Uso no logger
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        record.msg = mask_sensitive_data(str(record.msg))
        return True

logger.addFilter(SensitiveDataFilter())
```

---

### 9.3 Audit Trail

#### Estrutura do Audit Log

```python
{
    "timestamp": "2025-12-04T15:30:00.000Z",
    "user": "u***@sysmanager.com.br",
    "operation": "APPLY_POLICY_TAG",
    "resource": "analytics.users.email",
    "details": {
        "dataset_id": "analytics",
        "table_id": "users",
        "column_name": "email",
        "policy_tag_id": "projects/123/.../PII_HIGH",
        "policy_tag_name": "PII_HIGH"
    },
    "status": "SUCCESS",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0...",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### Compliance Reports

**Geração de Relatório de Compliance**:
```python
def generate_compliance_report(start_date: date, end_date: date) -> Dict:
    """Gerar relatório de compliance"""
    
    audit_service = AuditService()
    
    # Buscar logs do período
    logs = audit_service.query_logs(
        start_time=datetime.combine(start_date, time.min),
        end_time=datetime.combine(end_date, time.max)
    )
    
    # Agregar estatísticas
    report = {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'summary': {
            'total_operations': len(logs),
            'unique_users': len(set(log['user'] for log in logs)),
            'failed_operations': sum(1 for log in logs if log['status'] == 'FAILURE')
        },
        'operations_by_type': {},
        'operations_by_user': {},
        'operations_by_day': {},
        'resources_modified': set(),
        'security_events': []
    }
    
    # Preencher estatísticas
    for log in logs:
        # Por tipo
        op_type = log['operation']
        report['operations_by_type'][op_type] = \
            report['operations_by_type'].get(op_type, 0) + 1
        
        # Por usuário
        user = log['user']
        report['operations_by_user'][user] = \
            report['operations_by_user'].get(user, 0) + 1
        
        # Por dia
        day = log['timestamp'][:10]
        report['operations_by_day'][day] = \
            report['operations_by_day'].get(day, 0) + 1
        
        # Recursos modificados
        report['resources_modified'].add(log['resource'])
        
        # Eventos de segurança (ex: falhas de acesso)
        if log['status'] == 'FAILURE':
            report['security_events'].append({
                'timestamp': log['timestamp'],
                'user': log['user'],
                'operation': log['operation'],
                'resource': log['resource']
            })
    
    # Converter sets para lists
    report['resources_modified'] = list(report['resources_modified'])
    
    return report
```

---

## 10. CODE DOCUMENTATION

### 10.1 BigQuery Services

#### BigQueryRLSService - Principais Métodos

```python
class BigQueryRLSService:
    """
    Serviço para gerenciar Row-Level Security no BigQuery
    
    Responsabilidades:
        - Criação de políticas RLS
        - Listagem de políticas existentes
        - Atribuição de usuários/grupos a políticas
        - Remoção de políticas
    
    Attributes:
        client (bigquery.Client): Cliente do BigQuery
        project_id (str): ID do projeto GCP
    """
    
    def create_policy_for_users(
        self,
        dataset_id: str,
        table_id: str,
        policy_name: str,
        filter_column: str,
        grantees: List[str]
    ) -> None:
        """
        Cria política RLS baseada em usuários
        
        Args:
            dataset_id: ID do dataset
            table_id: ID da tabela
            policy_name: Nome da política
            filter_column: Coluna usada no filtro
            grantees: Lista de emails dos usuários
        
        Raises:
            ValueError: Se parâmetros inválidos
            google.api_core.exceptions.GoogleAPIError: Erro na API
        
        Example:
            >>> service = BigQueryRLSService()
            >>> service.create_policy_for_users(
            ...     dataset_id='analytics',
            ...     table_id='sales',
            ...     policy_name='rls_sales_users',
            ...     filter_column='user_email',
            ...     grantees=['user@company.com']
            ... )
        """
    
    def list_policies(
        self,
        dataset_id: str,
        table_id: str
    ) -> List[Dict[str, Any]]:
        """
        Lista políticas RLS de uma tabela
        
        Args:
            dataset_id: ID do dataset
            table_id: ID da tabela
        
        Returns:
            Lista de dicionários com informações das políticas
        
        Example:
            >>> policies = service.list_policies('analytics', 'sales')
            >>> print(policies[0]['policy_name'])
            'rls_sales_users'
        """
```

---

### 10.2 Data Catalog Services

#### DataCatalogService - Principais Métodos

```python
class DataCatalogService:
    """
    Serviço para gerenciar taxonomias e policy tags
    
    Responsabilidades:
        - CRUD de taxonomias
        - CRUD de policy tags
        - Gerenciamento de hierarquia de tags
        - Gerenciamento de IAM por tag
    
    Attributes:
        client (PolicyTagManagerClient): Cliente do Data Catalog
        parent (str): Resource name do projeto/região
    """
    
    def create_taxonomy(
        self,
        display_name: str,
        description: str = "",
        activated_policy_types: Optional[List[str]] = None
    ) -> datacatalog_v1.Taxonomy:
        """
        Cria nova taxonomia
        
        Args:
            display_name: Nome exibido da taxonomia
            description: Descrição da taxonomia
            activated_policy_types: Tipos de política ativados
        
        Returns:
            Objeto Taxonomy criado
        
        Raises:
            google.api_core.exceptions.AlreadyExists: Taxonomia já existe
        
        Example:
            >>> taxonomy = service.create_taxonomy(
            ...     display_name='PII',
            ...     description='Personally Identifiable Information'
            ... )
        """
    
    def create_policy_tag_hierarchy(
        self,
        taxonomy_id: str,
        hierarchy: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """
        Cria hierarquia de policy tags
        
        Args:
            taxonomy_id: ID da taxonomia pai
            hierarchy: Dicionário com estrutura hierárquica
                      {
                          'PII_HIGH': ['SSN', 'CREDIT_CARD'],
                          'PII_MEDIUM': ['EMAIL', 'PHONE']
                      }
        
        Returns:
            Mapeamento de nomes para IDs das tags criadas
        
        Example:
            >>> tags = service.create_policy_tag_hierarchy(
            ...     taxonomy_id='projects/123/.../taxonomies/456',
            ...     hierarchy={'PII_HIGH': ['SSN', 'CREDIT_CARD']}
            ... )
        """
```

---

### 10.3 Audit Services

#### AuditService - Método Principal

```python
class AuditService:
    """
    Serviço de auditoria e logging
    
    Responsabilidades:
        - Registro de operações de segurança
        - Consulta de logs históricos
        - Geração de relatórios de compliance
        - Alertas de segurança
    """
    
    @staticmethod
    def log_operation(
        operation: str,
        resource: str,
        details: Optional[Dict] = None,
        status: str = 'SUCCESS'
    ) -> None:
        """
        Registra operação no audit log
        
        Args:
            operation: Tipo de operação (CREATE_RLS_POLICY, etc)
            resource: Recurso afetado (dataset.table.column)
            details: Detalhes adicionais da operação
            status: Status da operação (SUCCESS, FAILURE)
        
        Example:
            >>> AuditService.log_operation(
            ...     operation='APPLY_POLICY_TAG',
            ...     resource='analytics.users.email',
            ...     details={'policy_tag': 'PII_HIGH'},
            ...     status='SUCCESS'
            ... )
        """
```

---

### 10.4 Theme Services (v2.0)

#### Theme Module - Global Styling

```python
def _apply_global_theme() -> None:
    """
    Aplica tema HUD/Sci-Fi globalmente na aplicação
    
    Features:
        - Dark mode por padrão
        - Cor primária: Ciano neon (#00f3ff)
        - Glassmorphism effects
        - Grid de fundo animado
        - Hover effects nos cards
        - Scrollbar customizada
        - Transições suaves
    
    Styles Applied:
        - Body background gradient
        - Header with cyan border
        - Sidebar with backdrop blur
        - Cards with glow effects
        - Buttons with hover animations
        - Inputs with focus effects
        - Tables with zebra striping
        - Menu items with slide effect
    
    Example:
        >>> from theme import frame
        >>> with frame('Home'):
        ...     # Tema já aplicado automaticamente
        ...     ui.label('Content')
    """

@contextmanager
def frame(navtitle: str):
    """
    Context manager para criar frame da aplicação
    
    Features:
        - Header com título e botão logout
        - Sidebar sempre visível (v2.0)
        - Menu lateral carregado
        - Footer com info de sessão
        - Tema global aplicado
    
    Args:
        navtitle: Título da página atual (exibido no header)
    
    Yields:
        Column: Coluna principal para conteúdo
    
    Example:
        >>> with frame('Row Level Security'):
        ...     with ui.card():
        ...         ui.label('RLS Content')
    """
```

---

## 11. PERFORMANCE E ESCALABILIDADE

### 11.1 Otimizações Implementadas

#### 1. Query Optimization

**Uso de Parametrized Queries**:
```python
# ❌ Ruim - String concatenation
sql = f"SELECT * FROM table WHERE user = '{user_email}'"

# ✅ Bom - Parametrized query
from google.cloud.bigquery import ScalarQueryParameter

sql = "SELECT * FROM table WHERE user = @user_email"
params = [ScalarQueryParameter("user_email", "STRING", user_email)]

job_config = bigquery.QueryJobConfig(query_parameters=params)
client.query(sql, job_config=job_config)
```

**Benefícios**:
- Caching automático pelo BigQuery
- Reutilização de planos de execução
- Proteção contra SQL injection
- Performance 20-30% melhor

---

#### 2. Batch Operations

**Processamento em Lote**:
```python
def apply_tags_batch(
    dataset_id: str,
    table_id: str,
    column_tag_mapping: Dict[str, str]
) -> None:
    """Aplicar múltiplas tags de uma vez"""
    
    # Buscar tabela uma única vez
    table = client.get_table(f'{dataset_id}.{table_id}')
    
    # Modificar schema em memória
    new_schema = []
    for field in table.schema:
        if field.name in column_tag_mapping:
            # Aplicar tag
            field_dict = field.to_api_repr()
            field_dict['policyTags'] = {
                'names': [column_tag_mapping[field.name]]
            }
            new_schema.append(
                bigquery.SchemaField.from_api_repr(field_dict)
            )
        else:
            new_schema.append(field)
    
    # Atualizar tabela uma única vez
    table.schema = new_schema
    client.update_table(table, ['schema'])

# Antes: N updates (lento)
for column, tag in column_tag_mapping.items():
    apply_tag(dataset_id, table_id, column, tag)

# Depois: 1 update (rápido)
apply_tags_batch(dataset_id, table_id, column_tag_mapping)
```

**Melhoria**: Reduz de N API calls para 1

---

#### 3. Caching de Metadados

**Implementação de Cache**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedDataCatalogService:
    """Service com cache de metadados"""
    
    def __init__(self):
        self.cache_ttl = timedelta(minutes=5)
        self._cache = {}
    
    def list_taxonomies(self) -> List[datacatalog_v1.Taxonomy]:
        """Lista taxonomias com cache"""
        
        cache_key = 'taxonomies'
        
        # Verificar cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data
        
        # Buscar do Data Catalog
        taxonomies = self._fetch_taxonomies_from_api()
        
        # Atualizar cache
        self._cache[cache_key] = (taxonomies, datetime.now())
        
        return taxonomies
    
    @lru_cache(maxsize=128)
    def get_policy_tag_by_id(self, tag_id: str) -> datacatalog_v1.PolicyTag:
        """Buscar tag por ID com cache em memória"""
        return self.client.get_policy_tag(name=tag_id)
```

**Tempos de Cache**:
- Taxonomies: 5 minutos
- Policy tags: 5 minutos
- Table schemas: 2 minutos
- Audit logs: 1 minuto

---

#### 4. Lazy Loading

**Carregamento Sob Demanda**:
```python
class LazyLoadedTableList:
    """Lista de tabelas com lazy loading"""
    
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self._tables = None
    
    @property
    def tables(self) -> List[str]:
        """Carrega tabelas apenas quando acessado"""
        if self._tables is None:
            self._tables = self._load_tables()
        return self._tables
    
    def _load_tables(self) -> List[str]:
        """Carrega lista de tabelas"""
        client = bigquery.Client()
        dataset_ref = client.dataset(self.dataset_id)
        tables = client.list_tables(dataset_ref)
        return [table.table_id for table in tables]

# Uso
dataset = LazyLoadedTableList('analytics')
# Tabelas NÃO carregadas ainda

print(dataset.tables)  # Carrega AGORA
```

---

### 11.2 Limites e Restrições

#### Limites do BigQuery

| Recurso | Limite | Observação |
|---------|--------|------------|
| **Queries por segundo** | 100 | Por projeto |
| **Concurrent queries** | 100 | Por projeto |
| **Query result size** | 10 GB | Exportar para GCS se maior |
| **Query timeout** | 6 horas | Padrão: 10 minutos |
| **RLS policies por tabela** | 100 | - |
| **Table size** | 10 TB | Por tabela |
| **Columns por tabela** | 10.000 | - |

**Mitigações**:
- Implementar rate limiting no client
- Usar batch operations
- Paginar resultados grandes
- Timeouts configuráveis

---

#### Limites do Data Catalog

| Recurso | Limite | Observação |
|---------|--------|------------|
| **Taxonomies por projeto** | 1.000 | - |
| **Policy tags por taxonomy** | 1.000 | - |
| **Tag hierarchy depth** | 5 níveis | - |
| **API calls por minuto** | 60 | Por projeto |

**Mitigações**:
- Cache de taxonomies/tags
- Organizar hierarquia eficientemente
- Implementar retry com exponential backoff

---

#### Limites do Cloud Run

| Recurso | Limite | Configurável |
|---------|--------|--------------|
| **Memory** | 32 GB max | Sim (default: 512 MB) |
| **CPU** | 8 vCPUs max | Sim (default: 1 vCPU) |
| **Request timeout** | 60 min max | Sim (default: 5 min) |
| **Concurrent requests** | 1000 per instance | Sim |
| **Max instances** | 1000 | Sim |
| **Cold start** | ~2s | - |

**Configuração Atual**:
```yaml
# cloud-run-config.yaml
memory: 512Mi
cpu: 1
timeout: 300s
max-instances: 10
min-instances: 0
concurrency: 80
```

---

## 12. HISTÓRICO DE VERSÕES

### 12.1 v1.0 - RLS + CLS Integration (08/11/2025)

**Objetivo**: Integrar funcionalidades de Column-Level Security na aplicação RLS Manager.

**Arquivos Criados** (7):
- `services/datacatalog_service.py` (~250 linhas)
- `services/bigquery_cls_service.py` (~230 linhas)
- `services/__init__.py` (~5 linhas)
- `pages/cls_taxonomies.py` (~150 linhas)
- `pages/cls_policy_tags.py` (~175 linhas)
- `pages/cls_apply_tags.py` (~210 linhas)
- `pages/cls_schema_browser.py` (~105 linhas)

**Arquivos Modificados** (4):
- `menu.py` - Adicionada seção CLS (~30 linhas)
- `allpages.py` - Registradas 4 rotas CLS (~25 linhas)
- `requirements.txt` - Adicionadas dependências (~2 linhas)
- `config.py` - Adicionado parâmetro LOCATION (~1 linha)

**Funcionalidades Adicionadas**:
1. Manage Taxonomies (CRUD completo)
2. Manage Policy Tags (CRUD + hierarquia)
3. Apply Tags to Columns (aplicar/remover tags)
4. Schema Browser (visualizar cobertura)

**Métricas**:
- Linhas de código: ~900
- Tempo de desenvolvimento: ~2 horas
- Compatibilidade: 100% com RLS original

---

### 12.2 v2.0 - UI Overhaul & HUD Theme (04/12/2025)

**Objetivo**: Modernizar interface com tema HUD/Sci-Fi e melhorar UX.

**Arquivos Criados** (2):
- `static/login.html` (~400 linhas) - Login em HTML puro
- `translations.py` (~300 linhas) - Sistema de traduções (estrutura)

**Arquivos Modificados** (5):
- `theme.py` (~200 linhas) - CSS global + dark mode
- `home.py` (~150 linhas) - 5 feature cards + welcome card compacto
- `menu.py` (~80 linhas) - Ícones color-coded
- `main.py` (~40 linhas) - Dark mode + FastAPI routes
- `pages/login_page.py` - Callback OAuth apenas

**Funcionalidades Adicionadas**:
1. Login HTML puro com tema HUD/Sci-Fi
2. Tema dark global com ciano neon
3. 5 feature cards interativos na home
4. Cores distintas por seção no menu
5. Sidebar sempre visível
6. Header simplificado
7. Hover effects avançados
8. Sistema de traduções (estrutura pt/en/es)

**Mudanças Visuais**:
- Login: 75% mais rápido (~200ms vs ~800ms)
- Tema: Ciano neon (#00f3ff) + preto (#0a0f1a)
- Cards: Glassmorphism + animations
- Menu: Color-coded (Home=ciano, RLS=verde, CLS=amarelo, IAM=vermelho, Audit=roxo)

**Métricas**:
- Linhas modificadas: ~800
- Performance: +75% no login
- CSS conflicts: Zero (vs muitos antes)

---

## 13. ROADMAP FUTURO

### 13.1 v2.1 - Translations (Janeiro 2025)

**Status**: Em desenvolvimento (estrutura criada)

**Features Planejadas**:
- ✅ Estrutura de traduções criada (pt/en/es)
- [ ] Integração no login.html
- [ ] Bandeiras no header
- [ ] Persistência de idioma (localStorage)
- [ ] Tradução de todas as páginas
- [ ] Suporte a mais idiomas (fr/de/jp/cn)

**Estimativa**: 2 semanas

---

### 13.2 v3.0 - Features Avançadas (Q1 2025)

**Dashboard Analítico**:
- Métricas de segurança em tempo real
- Gráficos de cobertura RLS/CLS
- Alertas de políticas não aplicadas
- Tendências de uso por usuário

**Automações**:
- Auto-aplicação de tags baseado em padrões
- Sugestões de políticas RLS baseadas em dados
- Detecção de anomalias de acesso
- Notificações push de mudanças

**Integrações**:
- Slack notifications
- ServiceNow tickets
- Jira issues
- Email alerts

**API Pública**:
- REST API para operações programáticas
- Webhooks para eventos
- SDK em Python
- Documentação OpenAPI

**Estimativa**: 3 meses

---

### 13.3 v4.0 - Enterprise Features (Q2 2025)

**Multi-Projeto**:
- Gerenciar múltiplos projetos GCP
- Dashboard consolidado
- Políticas cross-projeto

**Advanced RBAC**:
- Roles customizadas por organização
- Granular permissions
- Approval workflows

**Compliance Pack**:
- Templates pré-configurados (LGPD, SOX, ISO 27001)
- Relatórios automáticos
- Certificações

**High Availability**:
- Multi-region deployment
- Active-active setup
- Disaster recovery

**Estimativa**: 4 meses

---

### 13.4 v5.0 - AI-Powered (Q3 2025)

**Machine Learning**:
- Predição de anomalias de acesso
- Classificação automática de sensibilidade
- Sugestões inteligentes de políticas

**Natural Language**:
- Criar políticas RLS/CLS com linguagem natural
- Chatbot para perguntas sobre segurança
- Geração automática de documentação

**Advanced Analytics**:
- Análise preditiva de riscos
- Simulação de impacto de políticas
- Recomendações baseadas em ML

**Estimativa**: 6 meses

---

## CONCLUSÃO

Este documento técnico cobre todos os aspectos do **RLS & CLS Security Manager**, desde sua concepção até a implementação atual (v2.0).

### Principais Conquistas

**v1.0 (08/11/2025)**:
- ✅ Integração RLS + CLS completa
- ✅ 7 novos arquivos criados
- ✅ 4 páginas CLS funcionais
- ✅ ~900 linhas de código
- ✅ 100% retrocompatível

**v2.0 (04/12/2025)**:
- ✅ UI moderna com tema HUD/Sci-Fi
- ✅ Login 75% mais rápido
- ✅ Zero CSS conflicts
- ✅ 5 feature cards interativos
- ✅ Menu color-coded
- ✅ Dark mode nativo

### Tecnologias Utilizadas

- **Frontend**: NiceGUI + HTML5 + CSS3
- **Backend**: Python 3.11 + FastAPI
- **Cloud**: Google Cloud Platform (Cloud Run, BigQuery, Data Catalog)
- **Segurança**: OAuth 2.0 + RBAC + Audit Logs

### Próximos Passos

1. **v2.1 - Translations** (Jan 2025)
2. **v3.0 - Advanced Features** (Q1 2025)
3. **v4.0 - Enterprise** (Q2 2025)
4. **v5.0 - AI-Powered** (Q3 2025)

---

## INFORMAÇÕES DE CONTATO

**Desenvolvedor**: Lucas Carvalhal  
**Empresa**: Sys Manager - Partner Google Cloud  
**Email**: lucas.carvalhal@sysmanager.com.br  
**Projeto**: sys-googl-cortex-security  
**Deploy**: Cloud Run (us-central1)

---

## LICENÇA

Copyright © 2025-2025 Sys Manager  
Partner Google Cloud  
Todos os direitos reservados.

---

**Última Atualização**: 04/12/2025  
**Versão do Documento**: 2.0  
**Status**: Documentação Completa
