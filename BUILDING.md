# 🏗️ Guia de Construção - PetCareAI Analytics

Este documento fornece instruções detalhadas para construir e configurar o sistema PetCareAI Analytics localmente ou em produção.

## 📋 Pré-requisitos

### Requisitos do Sistema
- **Python**: 3.8 ou superior
- **Node.js**: 16+ (opcional, para ferramentas de desenvolvimento)
- **Git**: Para controle de versão
- **Conta Supabase**: Para banco de dados em nuvem

### Requisitos de Hardware
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Espaço em Disco**: 2GB livres para instalação completa
- **CPU**: Qualquer processador moderno (suporte a Python)

## 🛠️ Configuração do Ambiente

### 1. Clone do Repositório
```bash
git clone https://github.com/PetCareAi/analytics.git
cd analytics
```

### 2. Ambiente Virtual Python
```bash
# Criar ambiente virtual
python -m venv petcare_env

# Ativar ambiente virtual
# Windows
petcare_env\Scripts\activate
# Linux/Mac
source petcare_env/bin/activate
```

### 3. Instalação de Dependências
```bash
# Instalar dependências principais
pip install -r requirements.txt

# Para desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

## 🔧 Configuração do Banco de Dados

### Configuração do Supabase

1. **Criar Projeto no Supabase**
   - Acesse [supabase.com](https://supabase.com)
   - Crie uma nova organização/projeto
   - Anote a URL e chave anônima do projeto

2. **Configurar Variáveis de Ambiente**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_ANON_KEY=sua_chave_anonima
   ```

3. **Criar Tabelas no Supabase**
   
   Execute os seguintes SQLs no SQL Editor do Supabase:

   ```sql
   -- Tabela de usuários
   CREATE TABLE users_analytics (
     id SERIAL PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     password_hash VARCHAR(255) NOT NULL,
     full_name VARCHAR(255) NOT NULL,
     role VARCHAR(50) DEFAULT 'user',
     preferences JSONB DEFAULT '{}',
     profile_data JSONB DEFAULT '{}',
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW(),
     last_login TIMESTAMP
   );

   -- Tabela de pets
   CREATE TABLE pets_analytics (
     id SERIAL PRIMARY KEY,
     nome VARCHAR(255) NOT NULL,
     tipo_pet VARCHAR(100) NOT NULL,
     raca VARCHAR(255),
     idade DECIMAL(5,2),
     peso DECIMAL(6,2),
     sexo VARCHAR(20),
     genero VARCHAR(20),
     bairro VARCHAR(255),
     regiao VARCHAR(100),
     telefone VARCHAR(50),
     cor_pelagem VARCHAR(100),
     status_vacinacao VARCHAR(100),
     estado_saude VARCHAR(100),
     necessidades_especiais TEXT,
     historico_medico TEXT,
     comportamento VARCHAR(100),
     temperamento VARCHAR(100),
     sociabilidade INTEGER CHECK (sociabilidade BETWEEN 1 AND 5),
     energia INTEGER CHECK (energia BETWEEN 1 AND 5),
     nivel_atividade INTEGER CHECK (nivel_atividade BETWEEN 1 AND 5),
     adaptabilidade INTEGER CHECK (adaptabilidade BETWEEN 1 AND 5),
     adotado BOOLEAN DEFAULT FALSE,
     score_adocao DECIMAL(3,2),
     risco_abandono DECIMAL(3,2),
     observacoes TEXT,
     foto_url VARCHAR(500),
     status VARCHAR(100) DEFAULT 'Disponível',
     castrado BOOLEAN DEFAULT FALSE,
     microchip BOOLEAN DEFAULT FALSE,
     compatibilidade_criancas BOOLEAN DEFAULT TRUE,
     compatibilidade_pets BOOLEAN DEFAULT TRUE,
     custo_mensal DECIMAL(8,2),
     created_by INTEGER REFERENCES users_analytics(id),
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );

   -- Tabela de logs de atividade
   CREATE TABLE activity_logs_analytics (
     id SERIAL PRIMARY KEY,
     user_id INTEGER REFERENCES users_analytics(id),
     action VARCHAR(255) NOT NULL,
     details TEXT,
     session_id VARCHAR(255),
     execution_time DECIMAL(8,3),
     ip_address INET,
     timestamp TIMESTAMP DEFAULT NOW()
   );

   -- Tabela de logs de login
   CREATE TABLE login_logs_analytics (
     id SERIAL PRIMARY KEY,
     user_id INTEGER REFERENCES users_analytics(id),
     success BOOLEAN NOT NULL,
     failure_reason VARCHAR(255),
     ip_address INET,
     user_agent TEXT,
     timestamp TIMESTAMP DEFAULT NOW()
   );

   -- Criar índices para performance
   CREATE INDEX idx_pets_tipo_pet ON pets_analytics(tipo_pet);
   CREATE INDEX idx_pets_bairro ON pets_analytics(bairro);
   CREATE INDEX idx_pets_adotado ON pets_analytics(adotado);
   CREATE INDEX idx_pets_created_at ON pets_analytics(created_at);
   CREATE INDEX idx_activity_logs_user_id ON activity_logs_analytics(user_id);
   CREATE INDEX idx_activity_logs_timestamp ON activity_logs_analytics(timestamp);
   CREATE INDEX idx_login_logs_timestamp ON login_logs_analytics(timestamp);
   ```

## 🚀 Execução do Sistema

### Desenvolvimento Local
```bash
# Ativar ambiente virtual
source petcare_env/bin/activate  # Linux/Mac
# ou
petcare_env\Scripts\activate     # Windows

# Executar aplicação
streamlit run app.py
```

### Configuração para Produção

#### Usando Docker (Recomendado)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build da imagem
docker build -t petcare-analytics .

# Executar container
docker run -p 8501:8501 -e SUPABASE_URL=sua_url -e SUPABASE_ANON_KEY=sua_chave petcare-analytics
```

#### Deploy no Streamlit Cloud
1. Faça fork do repositório
2. Conecte sua conta GitHub ao Streamlit Cloud
3. Configure as secrets no painel do Streamlit:
   ```toml
   [supabase]
   SUPABASE_URL = "sua_url_do_supabase"
   SUPABASE_ANON_KEY = "sua_chave_anonima"
   ```

## 🔍 Verificação da Instalação

### Testes Básicos
```bash
# Testar importações
python -c "import streamlit, pandas, numpy, plotly; print('✅ Todas as dependências instaladas')"

# Verificar conexão com Supabase
python -c "from config.database import get_supabase; client = get_supabase(); print('✅ Conexão Supabase OK' if client else '❌ Erro na conexão')"
```

### Checklist de Verificação
- [ ] Python 3.8+ instalado
- [ ] Todas as dependências instaladas sem erro
- [ ] Arquivo `.env` configurado corretamente
- [ ] Tabelas criadas no Supabase
- [ ] Aplicação inicia sem erros
- [ ] Login funciona (usar admin@petcare.com / admin123)
- [ ] Dashboard carrega dados corretamente

## 🐛 Solução de Problemas Comuns

### Erro de Dependências
```bash
# Limpar cache do pip
pip cache purge

# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Erro de Conexão com Supabase
1. Verifique se as credenciais estão corretas
2. Confirme se as tabelas foram criadas
3. Teste a conexão manualmente:
   ```python
   from supabase import create_client
   client = create_client("SUA_URL", "SUA_CHAVE")
   result = client.table('users_analytics').select('*').limit(1).execute()
   print(result)
   ```

### Problemas de Performance
- Aumente a memória disponível para Python
- Configure cache do Streamlit:
  ```python
  @st.cache_data(ttl=300)  # Cache por 5 minutos
  def load_data():
      # sua função aqui
  ```

## 📚 Recursos Adicionais

### Documentação
- [Documentação do Streamlit](https://docs.streamlit.io)
- [Documentação do Supabase](https://supabase.com/docs)
- [Guia do Pandas](https://pandas.pydata.org/docs/)

### Ferramentas de Desenvolvimento
```bash
# Instalar ferramentas opcionais de desenvolvimento
pip install black flake8 pytest jupyter

# Formatação de código
black app.py

# Linting
flake8 app.py

# Jupyter para análises
jupyter notebook
```

## 🔄 Atualizações

### Atualizar Dependências
```bash
# Verificar dependências desatualizadas
pip list --outdated

# Atualizar todas as dependências
pip install -r requirements.txt --upgrade
```

### Migração de Banco
Para atualizações que requerem mudanças no banco:
1. Faça backup dos dados
2. Execute os scripts de migração
3. Teste a aplicação
4. Restaure backup se necessário

## 📞 Suporte

Para problemas não cobertos neste guia:
- Abra uma issue no GitHub
- Consulte a documentação técnica
- Entre em contato com a equipe de desenvolvimento

---

**Nota**: Este guia assume conhecimento básico de Python e desenvolvimento web. Para iniciantes, recomenda-se começar com um ambiente de desenvolvimento local antes de partir para produção.
