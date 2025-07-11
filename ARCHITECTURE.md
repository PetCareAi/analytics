# Arquitetura - PetCareAI Analytics

## 🏗️ Visão Geral da Arquitetura

O PetCareAI Analytics é construído com uma arquitetura moderna e escalável, combinando frontend interativo com backend robusto e inteligência artificial avançada.

## 📋 Stack Tecnológico

### Frontend
- **Streamlit** 1.31.1 - Framework principal para interface web
- **Plotly** 5.18+ - Visualizações interativas e gráficos
- **HTML/CSS/JavaScript** - Customizações e componentes avançados

### Backend & Data Processing
- **Python** 3.8+ - Linguagem principal
- **Pandas** 2.2+ - Manipulação de dados
- **NumPy** 1.24+ - Computação numérica
- **Scikit-learn** 1.4+ - Machine Learning

### Banco de Dados
- **Supabase** - PostgreSQL gerenciado
  - Real-time subscriptions
  - Row Level Security (RLS)
  - API REST automática
  - Dashboard administrativo

### Machine Learning & IA
- **Scikit-learn** - Algoritmos clássicos de ML
- **Statsmodels** - Análises estatísticas
- **NLTK/TextBlob** - Processamento de linguagem natural
- **NetworkX** - Análise de grafos e redes

### Visualização & Analytics
- **Plotly** - Gráficos interativos
- **Matplotlib/Seaborn** - Visualizações estáticas
- **Altair** - Grammar of graphics
- **Pydeck** - Mapas 3D

## 🏛️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                   │
├─────────────────────────────────────────────────────────────┤
│  Streamlit Frontend                                         │
│  ├── Dashboards Interativos                               │
│  ├── Formulários de Gestão                                │
│  ├── Visualizações Avançadas                              │
│  └── Sistema de Autenticação                              │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                     │
├─────────────────────────────────────────────────────────────┤
│  Controllers & Business Logic                               │
│  ├── Pet Management System                                 │
│  ├── User Management                                       │
│  ├── Analytics Engine                                      │
│  ├── ML Pipeline                                          │
│  └── Export/Import System                                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                         │
├─────────────────────────────────────────────────────────────┤
│  Data Access Layer                                         │
│  ├── Supabase Client                                      │
│  ├── Data Validation                                       │
│  ├── Caching System                                       │
│  └── File Storage                                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE PERSISTÊNCIA                  │
├─────────────────────────────────────────────────────────────┤
│  Supabase (PostgreSQL)                                     │
│  ├── pets_analytics                                       │
│  ├── users_analytics                                      │
│  ├── activity_logs_analytics                              │
│  ├── login_logs_analytics                                 │
│  └── system_config                                        │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Modelo de Dados

### Tabelas Principais

#### pets_analytics
```sql
CREATE TABLE pets_analytics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nome TEXT NOT NULL,
    tipo_pet TEXT NOT NULL,
    raca TEXT,
    idade NUMERIC,
    peso NUMERIC,
    sexo TEXT,
    genero TEXT, -- compatibilidade
    bairro TEXT,
    regiao TEXT,
    telefone TEXT,
    comportamento TEXT,
    sociabilidade INTEGER CHECK (sociabilidade >= 1 AND sociabilidade <= 5),
    energia INTEGER CHECK (energia >= 1 AND energia <= 5),
    nivel_atividade INTEGER CHECK (nivel_atividade >= 1 AND nivel_atividade <= 5),
    adaptabilidade INTEGER CHECK (adaptabilidade >= 1 AND adaptabilidade <= 5),
    score_adocao NUMERIC CHECK (score_adocao >= 0 AND score_adocao <= 5),
    risco_abandono NUMERIC CHECK (risco_abandono >= 0 AND risco_abandono <= 1),
    adotado BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'Disponível',
    castrado BOOLEAN DEFAULT FALSE,
    microchip BOOLEAN DEFAULT FALSE,
    status_vacinacao TEXT,
    estado_saude TEXT,
    necessidades_especiais TEXT,
    historico_medico TEXT,
    cor_pelagem TEXT,
    custo_mensal NUMERIC,
    compatibilidade_criancas BOOLEAN,
    compatibilidade_pets BOOLEAN,
    foto_url TEXT,
    observacoes TEXT,
    cluster_comportamental INTEGER,
    created_by BIGINT REFERENCES users_analytics(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### users_analytics
```sql
CREATE TABLE users_analytics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user', 'guest')),
    preferences JSONB DEFAULT '{}',
    profile_data JSONB DEFAULT '{}',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### activity_logs_analytics
```sql
CREATE TABLE activity_logs_analytics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT REFERENCES users_analytics(id),
    action TEXT NOT NULL,
    details TEXT,
    session_id TEXT,
    execution_time NUMERIC,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

#### login_logs_analytics
```sql
CREATE TABLE login_logs_analytics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT REFERENCES users_analytics(id),
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

### Relacionamentos
```
users_analytics (1) → (N) pets_analytics
users_analytics (1) → (N) activity_logs_analytics  
users_analytics (1) → (N) login_logs_analytics
```

## 🔧 Componentes Principais

### 1. Sistema de Autenticação
- **Localização**: `app.py` (funções auth_*)
- **Responsabilidades**:
  - Login/logout seguro
  - Gestão de sessões
  - Controle de acesso baseado em roles
  - Sistema de logins salvos com criptografia

### 2. Motor de Analytics
- **Localização**: `app.py` (classe PetMLAnalyzer)
- **Responsabilidades**:
  - Clustering comportamental
  - Análises preditivas
  - Detecção de anomalias
  - Séries temporais

### 3. Sistema de Gestão de Pets
- **Localização**: `app.py` (funções pet_*)
- **Responsabilidades**:
  - CRUD completo de pets
  - Validação de dados
  - Cálculo automático de scores
  - Upload de imagens

### 4. Dashboard Engine
- **Localização**: `app.py` (display_dashboard)
- **Responsabilidades**:
  - Métricas em tempo real
  - Visualizações interativas
  - Filtros dinâmicos
  - Insights automatizados

### 5. Sistema de Exportação/Importação
- **Localização**: `app.py` (exportar_importar_dados)
- **Responsabilidades**:
  - Múltiplos formatos de export
  - Validação de importação
  - Mapeamento de colunas
  - Processamento em lotes

## 🔄 Fluxo de Dados

### 1. Fluxo de Autenticação
```
Login Form → authenticate_user() → Supabase Auth → Session State → Dashboard
```

### 2. Fluxo de Adição de Pet
```
Formulário → Validação → calculate_scores() → Supabase Insert → Log Activity
```

### 3. Fluxo de Analytics
```
Data Loading → PetMLAnalyzer → Processing → Visualization → Cache
```

### 4. Fluxo de Exportação
```
Data Selection → Format Choice → Processing → Download
```

## 🛡️ Segurança

### Autenticação e Autorização
- Hash SHA-256 para senhas
- Session-based authentication
- Role-based access control (RBAC)
- Row Level Security (RLS) no Supabase

### Proteção de Dados
- Validação rigorosa de entrada
- Sanitização de dados
- Prevenção de SQL Injection via ORM
- Logs de auditoria completos

### Comunicação
- HTTPS obrigatório em produção
- API keys protegidas
- Rate limiting implementado
- CORS configurado adequadamente

## 📈 Performance e Escalabilidade

### Otimizações Implementadas
- **Caching**: Session state para dados frequentes
- **Lazy Loading**: Carregamento sob demanda
- **Pagination**: Limitação de registros por página
- **Indexação**: Índices otimizados no Supabase

### Monitoramento
- Logs de performance
- Métricas de uso
- Health checks automáticos
- Alertas proativos

### Escalabilidade Horizontal
- Supabase gerencia scaling automático
- Stateless application design
- Load balancing via cloud providers
- CDN para assets estáticos

## 🔮 Machine Learning Pipeline

### 1. Data Preprocessing
```python
class PetMLAnalyzer:
    def preprocess_data(self):
        # Limpeza de dados
        # Encoding categórico
        # Normalização numérica
        # Feature engineering
```

### 2. Model Training
```python
def advanced_clustering(self):
    # KMeans, DBSCAN, Agglomerative
    # Validação com Silhouette Score
    # PCA para visualização
```

### 3. Prediction Pipeline
```python
def predictive_modeling(self):
    # Train/Test Split
    # Multiple algorithms
    # Cross-validation
    # Feature importance
```

### 4. Anomaly Detection
```python
def anomaly_detection(self):
    # Isolation Forest
    # One-Class SVM
    # Local Outlier Factor
```

## 🚀 Deploy e DevOps

### Ambientes
- **Development**: Local com SQLite
- **Staging**: Streamlit Cloud + Supabase
- **Production**: Cloud provider + Supabase

### CI/CD Pipeline (Recomendado)
```yaml
1. Code Push → GitHub
2. Tests → GitHub Actions
3. Build → Docker Image
4. Deploy → Cloud Platform
5. Health Check → Monitoring
```

### Monitoramento
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Log aggregation (ELK Stack)
- Uptime monitoring

## 📦 Estrutura de Arquivos

```
petcare-analytics/
├── app.py                 # Aplicação principal
├── config/
│   └── database.py       # Configuração Supabase
├── data/                 # Dados temporários
├── models/               # Modelos ML salvos
├── assets/               # Assets estáticos
├── exports/              # Arquivos exportados
├── requirements.txt      # Dependências
├── .env                 # Variáveis ambiente
├── .gitignore           # Git ignore
└── README.md            # Documentação

docs/
├── architecture.md      # Este arquivo
├── api.md              # Documentação API
├── deployment.md       # Guia deploy
└── user-guide.md       # Manual usuário
```

## 🔄 Padrões de Desenvolvimento

### Padrões Arquiteturais
- **MVC Pattern**: Model-View-Controller
- **Repository Pattern**: Abstração do acesso a dados
- **Factory Pattern**: Criação de objetos complexos
- **Observer Pattern**: Sistema de eventos

### Padrões de Código
- **PEP 8**: Style guide Python
- **Type Hints**: Tipagem estática
- **Docstrings**: Documentação de funções
- **Error Handling**: Tratamento robusto de erros

---

*Esta documentação é mantida atualizada com cada release. Para detalhes técnicos específicos, consulte o código fonte ou a documentação da API.*
