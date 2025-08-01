# 🔧 Guia de Troubleshooting - PetCare Analytics

## 🚨 Problemas Comuns e Soluções

### 1. 🔗 Problemas de Conexão com Supabase

#### Erro: "Não foi possível conectar ao Supabase"

**Sintomas:**
- Mensagem de erro na interface
- Dados não carregam
- Login não funciona

**Soluções:**

1. **Verificar variáveis de ambiente:**
   ```bash
   # Verificar se as variáveis estão definidas
   echo $SUPABASE_URL
   echo $SUPABASE_ANON_KEY
   ```

2. **Verificar arquivo .env:**
   ```env
   SUPABASE_URL=https://jthzocdiryhuytnmtekj.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Verificar conexão de rede:**
   ```bash
   # Testar conectividade
   ping jthzocdiryhuytnmtekj.supabase.co
   curl -I https://jthzocdiryhuytnmtekj.supabase.co
   ```

#### Erro: "Authentication failed"

**Sintomas:**
- Login falha constantemente
- Erro 401 nas requisições

**Soluções:**

1. **Verificar credenciais no Supabase:**
   - Acessar dashboard do Supabase
   - Ir em Settings > API
   - Verificar se as chaves estão corretas

2. **Regenerar chaves de API se necessário**

3. **Verificar configuração RLS (Row Level Security)**

### 2. 📦 Problemas de Dependências

#### Erro: ModuleNotFoundError

**Sintomas:**
- `ModuleNotFoundError: No module named 'xxx'`
- Aplicação não inicia

**Soluções:**

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verificar versão do Python:**
   ```bash
   python --version  # Deve ser 3.8+
   ```

3. **Criar ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

#### Erro: Conflito de versões

**Sintomas:**
- Warnings sobre versões incompatíveis
- Comportamento inesperado

**Soluções:**

1. **Atualizar pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Reinstalar dependências:**
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

### 3. 🗄️ Problemas de Banco de Dados

#### Erro: Tabelas não encontradas

**Sintomas:**
- Erro: "relation does not exist"
- Dados não carregam

**Soluções:**

1. **Verificar se as tabelas existem no Supabase:**
   - Acessar Supabase Dashboard
   - Ir na aba Table Editor
   - Verificar tabelas: `pets_analytics`, `users_analytics`, etc.

2. **Executar scripts de criação das tabelas (se necessário)**

3. **Verificar permissões RLS**

#### Erro: Permission denied

**Sintomas:**
- Erro 403 nas operações
- "Permission denied for table"

**Soluções:**

1. **Configurar RLS policies no Supabase:**
   ```sql
   -- Exemplo de policy básica
   CREATE POLICY "Allow all operations for authenticated users" 
   ON pets_analytics 
   FOR ALL 
   TO authenticated 
   USING (true);
   ```

2. **Verificar se o usuário está autenticado**

### 4. 🖥️ Problemas de Interface

#### Erro: Página em branco

**Sintomas:**
- Streamlit carrega mas não mostra conteúdo
- Erro no console do navegador

**Soluções:**

1. **Verificar logs do Streamlit:**
   ```bash
   streamlit run app.py --logger.level=debug
   ```

2. **Limpar cache:**
   ```python
   # No código, ou pelo menu do Streamlit
   st.cache_data.clear()
   ```

3. **Verificar portas:**
   ```bash
   # Verificar se a porta 8501 está livre
   netstat -an | grep 8501
   ```

#### Erro: Componentes não renderizam

**Sintomas:**
- Gráficos não aparecem
- Elementos de interface quebrados

**Soluções:**

1. **Verificar versões das bibliotecas de visualização:**
   ```bash
   pip list | grep plotly
   pip list | grep streamlit
   ```

2. **Atualizar navegador**

3. **Testar em modo incógnito**

### 5. 🔐 Problemas de Autenticação

#### Erro: Login não funciona

**Sintomas:**
- Credenciais corretas mas login falha
- Redirecionamento não funciona

**Soluções:**

1. **Verificar hash das senhas:**
   ```python
   import hashlib
   password = "sua_senha"
   hash_result = hashlib.sha256(password.encode()).hexdigest()
   print(hash_result)
   ```

2. **Verificar sessão do Streamlit:**
   ```python
   # Limpar session_state
   for key in st.session_state.keys():
       del st.session_state[key]
   ```

#### Erro: Sessão expira rapidamente

**Sintomas:**
- Usuário é deslogado constantemente
- Perda de dados da sessão

**Soluções:**

1. **Verificar configurações de sessão no Streamlit:**
   ```toml
   # .streamlit/config.toml
   [server]
   maxUploadSize = 200
   maxMessageSize = 200
   enableCORS = false
   
   [browser]
   gatherUsageStats = false
   ```

### 6. 📊 Problemas de Performance

#### Sintoma: Aplicação lenta

**Soluções:**

1. **Otimizar consultas ao banco:**
   ```python
   # Usar cache para consultas frequentes
   @st.cache_data(ttl=300)  # 5 minutos
   def load_pets_data():
       return supabase.table('pets_analytics').select('*').execute()
   ```

2. **Implementar paginação:**
   ```python
   # Limitar resultados
   result = supabase.table('pets_analytics')\
       .select('*')\
       .range(start, end)\
       .execute()
   ```

#### Sintoma: Uso excessivo de memória

**Soluções:**

1. **Otimizar DataFrames:**
   ```python
   # Usar tipos de dados mais eficientes
   df['id'] = df['id'].astype('int32')
   df['categoria'] = df['categoria'].astype('category')
   ```

2. **Limpar dados não utilizados:**
   ```python
   del df_temp  # Remover DataFrames temporários
   import gc
   gc.collect()  # Forçar garbage collection
   ```

### 7. 🔄 Problemas de Deploy

#### Erro: Deploy falha no Streamlit Cloud

**Sintomas:**
- Build falha
- Aplicação não inicia no cloud

**Soluções:**

1. **Verificar secrets no Streamlit Cloud:**
   ```toml
   # secrets.toml no Streamlit Cloud
   [supabase]
   SUPABASE_URL = "https://..."
   SUPABASE_ANON_KEY = "eyJ..."
   ```

2. **Verificar requirements.txt:**
   - Garantir que todas as dependências estão listadas
   - Usar versões específicas quando necessário

3. **Verificar arquivos de configuração:**
   ```
   .streamlit/
   ├── config.toml
   └── secrets.toml
   ```

## 🛠️ Ferramentas de Diagnóstico

### Script de Verificação de Sistema

```python
import streamlit as st
import sys
import pandas as pd
import plotly
import os

def check_system():
    st.write("## 🔍 Diagnóstico do Sistema")
    
    # Verificar Python
    st.write(f"**Python:** {sys.version}")
    
    # Verificar bibliotecas principais
    st.write(f"**Streamlit:** {st.__version__}")
    st.write(f"**Pandas:** {pd.__version__}")
    st.write(f"**Plotly:** {plotly.__version__}")
    
    # Verificar variáveis de ambiente
    supabase_url = os.getenv("SUPABASE_URL")
    st.write(f"**Supabase URL configurada:** {'✅' if supabase_url else '❌'}")
    
    # Testar conexão
    try:
        from config.database import get_supabase
        supabase = get_supabase()
        if supabase:
            result = supabase.table('users_analytics').select('id').limit(1).execute()
            st.write("**Conexão Supabase:** ✅")
        else:
            st.write("**Conexão Supabase:** ❌")
    except Exception as e:
        st.write(f"**Conexão Supabase:** ❌ - {str(e)}")
```

### Logs de Debug

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('petcare_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usar nos pontos críticos
logger.debug("Iniciando conexão com Supabase")
logger.error("Erro na autenticação: %s", str(e))
```

## 📞 Suporte

### Informações para Reportar Bugs

Ao reportar um problema, inclua:

1. **Versão do Python:** `python --version`
2. **Versão do Streamlit:** `streamlit --version`
3. **Sistema Operacional**
4. **Mensagem de erro completa**
5. **Passos para reproduzir**
6. **Logs relevantes**

### Contatos

- **Email:** admin@petcare.com
- **GitHub Issues:** [Criar issue no repositório]
- **Documentação:** [Link para docs]

## 🔄 Procedimentos de Recuperação

### Reset Completo da Aplicação

```bash
# 1. Parar aplicação
pkill -f streamlit

# 2. Limpar cache Python
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete

# 3. Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 4. Limpar cache Streamlit
rm -rf ~/.streamlit/

# 5. Reiniciar aplicação
streamlit run app.py
```

### Backup de Emergência

```python
def emergency_backup():
    """Criar backup de emergência dos dados"""
    try:
        # Exportar dados críticos
        users_data = supabase.table('users_analytics').select('*').execute()
        pets_data = supabase.table('pets_analytics').select('*').execute()
        
        # Salvar em arquivos
        with open('emergency_backup_users.json', 'w') as f:
            json.dump(users_data.data, f)
            
        with open('emergency_backup_pets.json', 'w') as f:
            json.dump(pets_data.data, f)
            
        return True
    except Exception as e:
        logger.error(f"Falha no backup de emergência: {e}")
        return False
```
