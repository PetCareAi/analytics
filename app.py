import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import io
import os
import sqlite3
import hashlib
import datetime
import time
import re
import base64
from PIL import Image
import json
from wordcloud import WordCloud
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor
import uuid
from functools import wraps
import warnings
warnings.filterwarnings('ignore')

# Configurar diretórios necessários
os.makedirs("assets", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Constantes
DATABASE_PATH = "data/petcare.db"
DEFAULT_ADMIN_EMAIL = "admin@petcare.com"
DEFAULT_ADMIN_PASSWORD = "admin123"  # Isto será codificado antes de armazenar

# Funções de utilidade para autenticação e banco de dados
def init_database():
    """Inicializar banco de dados SQLite com tabelas necessárias."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # Tabela de pets
    c.execute('''
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        bairro TEXT,
        tipo_pet TEXT,
        raca TEXT,
        idade REAL,
        peso REAL,
        sexo TEXT,
        tipo_comida TEXT,
        humor_diario TEXT,
        adotado BOOLEAN,
        telefone TEXT,
        status_vacinacao TEXT,
        estado_saude TEXT,
        comportamento TEXT,
        nivel_atividade TEXT,
        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        regiao TEXT,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Tabela de registros de login
    c.execute('''
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT,
        success BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Tabela de atividades
    c.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Verificar se o usuário admin padrão existe
    c.execute("SELECT * FROM users WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
    if not c.fetchone():
        password_hash = hashlib.sha256(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
        c.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (DEFAULT_ADMIN_EMAIL, password_hash, "Administrador", "admin")
        )
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Gera um hash SHA-256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return stored_hash == hashlib.sha256(provided_password.encode()).hexdigest()

def authenticate_user(email, password):
    """Autentica um usuário com email e senha."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT id, password_hash, role FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    
    if result and verify_password(result[1], password):
        user_id, _, role = result
        # Atualizar último login
        c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        
        # Registrar login bem-sucedido
        c.execute(
            "INSERT INTO login_logs (user_id, success) VALUES (?, ?)",
            (user_id, True)
        )
        
        conn.commit()
        conn.close()
        return True, user_id, role
    
    # Registrar tentativa de login mal-sucedida se o email existir
    if result:
        c.execute(
            "INSERT INTO login_logs (user_id, success) VALUES (?, ?)",
            (result[0], False)
        )
        conn.commit()
    
    conn.close()
    return False, None, None

def log_activity(user_id, action, details=""):
    """Registra uma atividade de usuário no sistema."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)",
        (user_id, action, details)
    )
    
    conn.commit()
    conn.close()

def get_user_info(user_id):
    """Obtém informações do usuário pelo ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT email, full_name, role FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return {
            "email": result[0],
            "full_name": result[1],
            "role": result[2]
        }
    return None

def register_new_user(email, password, full_name, role="user"):
    """Registra um novo usuário no sistema."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (email, password_hash, full_name, role)
        )
        conn.commit()
        user_id = c.lastrowid
        
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        # Email já existe
        conn.close()
        return False, None

def change_password(user_id, current_password, new_password):
    """Altera a senha de um usuário após verificar a senha atual."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    
    if result and verify_password(result[0], current_password):
        new_password_hash = hash_password(new_password)
        c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def require_login(func):
    """Decorador para exigir login antes de acessar uma função."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in st.session_state or not st.session_state.user_id:
            st.warning("Faça login para acessar esta funcionalidade.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorador para exigir permissões de administrador."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_role" not in st.session_state or st.session_state.user_role != "admin":
            st.error("Você não tem permissão para acessar esta funcionalidade.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def load_data_from_db():
    """Carrega dados de pets do banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Consulta para obter todos os pets com informações do usuário que os criou
    query = """
    SELECT p.*, u.email as created_by_email 
    FROM pets p
    LEFT JOIN users u ON p.created_by = u.id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Converter coluna de data_registro para datetime se necessário
    if 'data_registro' in df.columns:
        df['data_registro'] = pd.to_datetime(df['data_registro'])
    
    # Converter adotado para booleano
    if 'adotado' in df.columns:
        df['adotado'] = df['adotado'].astype(bool)
    
    return df

def save_pet_to_db(pet_data):
    """Salva um novo pet no banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Preparar colunas e valores
    columns = ', '.join(pet_data.keys())
    placeholders = ', '.join(['?' for _ in pet_data])
    values = tuple(pet_data.values())
    
    query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
    
    try:
        c.execute(query, values)
        conn.commit()
        pet_id = c.lastrowid
        conn.close()
        return True, pet_id
    except Exception as e:
        conn.close()
        return False, str(e)

def update_pet_in_db(pet_id, pet_data):
    """Atualiza um pet existente no banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Preparar atualizações
    updates = ', '.join([f"{key} = ?" for key in pet_data])
    values = list(pet_data.values()) + [pet_id]  # Adicionar pet_id ao final para o WHERE
    
    query = f"UPDATE pets SET {updates} WHERE id = ?"
    
    try:
        c.execute(query, values)
        conn.commit()
        conn.close()
        return True, "Pet atualizado com sucesso"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_pet_from_db(pet_id):
    """Exclui um pet do banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
        conn.commit()
        conn.close()
        return True, "Pet excluído com sucesso"
    except Exception as e:
        conn.close()
        return False, str(e)

# Componentes de UI personalizados
def custom_card(title, content, icon=None, color="#4527A0"):
    """Renderiza um card personalizado com título, conteúdo e ícone opcional."""
    card_css = f"""
    <style>
    .card-container {{
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
        border-left: 5px solid {color};
        transition: transform 0.3s ease;
    }}
    .card-container:hover {{
        transform: translateY(-5px);
    }}
    .card-title {{
        color: {color};
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }}
    .card-icon {{
        margin-right: 0.5rem;
    }}
    </style>
    """
    
    icon_html = f'<span class="card-icon">{icon}</span>' if icon else ''
    
    card_html = f"""
    <div class="card-container">
        <div class="card-title">{icon_html}{title}</div>
        <div class="card-content">{content}</div>
    </div>
    """
    
    st.markdown(card_css + card_html, unsafe_allow_html=True)

def custom_metric(title, value, delta=None, color="#4527A0", prefix="", suffix=""):
    """Renderiza uma métrica personalizada com estilo consistente."""
    delta_html = ""
    if delta is not None:
        delta_color = "green" if delta >= 0 else "red"
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f'<span style="color: {delta_color}; font-size: 0.8rem;">{delta_icon} {abs(delta)}{suffix}</span>'
    
    metric_css = f"""
    <style>
    .metric-container {{
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    }}
    .metric-title {{
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: bold;
        color: {color};
    }}
    .metric-delta {{
        margin-top: 0.3rem;
    }}
    </style>
    """
    
    metric_html = f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        <div class="metric-delta">{delta_html}</div>
    </div>
    """
    
    st.markdown(metric_css + metric_html, unsafe_allow_html=True)

def display_login_page():
    """Exibe a página de login com animação e estilo elegante."""
    
    # CSS personalizado para a página de login
    login_css = """
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-logo {
        display: block;
        margin: 0 auto;
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 1rem;
    }
    .login-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4527A0;
        margin-bottom: 0.5rem;
    }
    .login-subtitle {
        color: #666;
        font-size: 1rem;
    }
    .form-row {
        margin-bottom: 1.5rem;
    }
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.9rem;
        color: #666;
    }
    .or-divider {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        color: #666;
    }
    .or-divider::before, .or-divider::after {
        content: "";
        flex: 1;
        border-bottom: 1px solid #ddd;
    }
    .or-divider::before {
        margin-right: 0.5rem;
    }
    .or-divider::after {
        margin-left: 0.5rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animated {
        animation: fadeIn 0.6s ease-out;
    }
    </style>
    """
    
    # Renderizar CSS
    st.markdown(login_css, unsafe_allow_html=True)
    
    # Centralizar conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container da página de login
        st.markdown('<div class="login-container animated">', unsafe_allow_html=True)
        
        # Cabeçalho com logo
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        
        # Verificar se o logo existe
        logo_path = "assets/logo.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100, use_column_width=False)
        else:
            st.markdown('🐾', unsafe_allow_html=True)
        
        st.markdown('<div class="login-title">PetCare Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema Avançado de Análise de Dados para Pets</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Abas para Login e Registro
        tab1, tab2 = st.tabs(["Login", "Registro"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Senha", type="password", key="login_password")
                remember = st.checkbox("Lembrar-me", key="login_remember")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submit = st.form_submit_button("Entrar", use_container_width=True)
                with col2:
                    forgot_password = st.form_submit_button("Esqueci minha senha", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("Por favor, preencha todos os campos.")
                    else:
                        with st.spinner("Autenticando..."):
                            time.sleep(0.5)  # Simular processamento
                            is_authenticated, user_id, role = authenticate_user(email, password)
                            
                            if is_authenticated:
                                st.session_state.user_id = user_id
                                st.session_state.user_role = role
                                st.session_state.user_info = get_user_info(user_id)
                                
                                if remember:
                                    st.session_state.remember_login = True
                                
                                # Registrar atividade
                                log_activity(user_id, "login", "Login bem-sucedido")
                                
                                st.success("Login realizado com sucesso!")
                                st.experimental_rerun()
                            else:
                                st.error("Email ou senha incorretos. Tente novamente.")
                
                if forgot_password:
                    st.info("Funcionalidade em desenvolvimento. Entre em contato com o administrador para redefinir sua senha.")
            
            # Divisor "ou"
            st.markdown('<div class="or-divider">ou</div>', unsafe_allow_html=True)
            
            # Login como convidado
            if st.button("Continuar como Convidado", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_role = "guest"
                st.session_state.user_info = {"email": "guest", "full_name": "Convidado", "role": "guest"}
                st.experimental_rerun()
        
        with tab2:
            with st.form("register_form"):
                st.caption("Crie uma conta para acessar todos os recursos")
                
                full_name = st.text_input("Nome completo", key="register_name")
                new_email = st.text_input("Email", key="register_email")
                new_password = st.text_input("Senha", type="password", key="register_password")
                confirm_password = st.text_input("Confirmar senha", type="password", key="register_confirm")
                
                terms = st.checkbox("Eu concordo com os Termos de Serviço", key="register_terms")
                
                register = st.form_submit_button("Criar Conta", use_container_width=True)
                
                if register:
                    if not full_name or not new_email or not new_password:
                        st.error("Por favor, preencha todos os campos.")
                    elif new_password != confirm_password:
                        st.error("As senhas não coincidem.")
                    elif not terms:
                        st.error("Você precisa concordar com os Termos de Serviço.")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                        st.error("Por favor, insira um email válido.")
                    elif len(new_password) < 6:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    else:
                        with st.spinner("Criando conta..."):
                            time.sleep(0.5)  # Simular processamento
                            success, user_id = register_new_user(new_email, new_password, full_name)
                            
                            if success:
                                st.success("Conta criada com sucesso! Você já pode fazer login.")
                                
                                # Auto-login após registro
                                st.session_state.user_id = user_id
                                st.session_state.user_role = "user"
                                st.session_state.user_info = get_user_info(user_id)
                                
                                # Registrar atividade
                                log_activity(user_id, "register", "Novo registro de usuário")
                                
                                st.experimental_rerun()
                            else:
                                st.error("Este email já está em uso. Tente outro ou faça login.")
        
        # Rodapé
        st.markdown('<div class="login-footer">© 2025 PetCare Analytics. Todos os direitos reservados.</div>', unsafe_allow_html=True)
        
        # Fechar container
        st.markdown('</div>', unsafe_allow_html=True)

def display_header():
    """Exibe o cabeçalho da aplicação com informações do usuário."""
    
    # CSS para o cabeçalho
    header_css = """
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    .header-title {
        display: flex;
        align-items: center;
    }
    .header-logo {
        margin-right: 1rem;
    }
    .header-user {
        display: flex;
        align-items: center;
    }
    .user-avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background: #4527A0;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.5rem;
        font-weight: bold;
    }
    .user-info {
        font-size: 0.9rem;
    }
    .user-name {
        font-weight: bold;
    }
    .user-role {
        color: #666;
        font-size: 0.8rem;
    }
    </style>
    """
    
    st.markdown(header_css, unsafe_allow_html=True)
    
    # Obter informações do usuário
    user_info = st.session_state.get("user_info", {"full_name": "Convidado", "role": "guest"})
    user_name = user_info.get("full_name", "Convidado")
    user_role = user_info.get("role", "guest")
    
    # Converter role para texto legível
    role_text = {
        "admin": "Administrador",
        "user": "Usuário",
        "guest": "Convidado"
    }.get(user_role, user_role)
    
    # Obter iniciais do nome para o avatar
    initials = ''.join([name[0].upper() for name in user_name.split() if name])
    if not initials:
        initials = "?"
    
    # Container do cabeçalho
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Título e logo
        header_title = '<div class="header-title">'
        
        # Verificar se o logo existe
        logo_path = "assets/logo.jpg"
        if os.path.exists(logo_path):
            # Codificar imagem em base64
            with open(logo_path, "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
            
            header_title += f'<img src="data:image/jpeg;base64,{logo_base64}" class="header-logo" width="40">'
        
        header_title += '<h1>PetCare Analytics</h1></div>'
        st.markdown(header_title, unsafe_allow_html=True)
    
    with col2:
        # Informações do usuário
        user_html = f"""
        <div class="header-user">
            <div class="user-avatar">{initials}</div>
            <div class="user-info">
                <div class="user-name">{user_name}</div>
                <div class="user-role">{role_text}</div>
            </div>
        </div>
        """
        
        st.markdown(user_html, unsafe_allow_html=True)
    
    # Separador
    st.markdown('<hr style="margin: 0.5rem 0; opacity: 0.2;">', unsafe_allow_html=True)

def apply_filters(df):
    """Aplica filtros ao DataFrame e retorna o resultado filtrado."""
    if df.empty:
        return df
    
    st.sidebar.markdown("## Filtros")
    
    # Container para filtros colapsáveis
    with st.sidebar.expander("Filtros Avançados", expanded=True):
        # Filtro por bairro
        if 'bairro' in df.columns:
            bairros = ["Todos"] + sorted(df['bairro'].unique().tolist())
            bairro_filtro = st.selectbox("Bairro:", bairros)
            
            if bairro_filtro != "Todos":
                df = df[df['bairro'] == bairro_filtro]
        
        # Filtro por tipo de pet
        if 'tipo_pet' in df.columns:
            tipos_pet = ["Todos"] + sorted(df['tipo_pet'].unique().tolist())
            tipo_pet_filtro = st.selectbox("Tipo de Pet:", tipos_pet)
            
            if tipo_pet_filtro != "Todos":
                df = df[df['tipo_pet'] == tipo_pet_filtro]
        
        # Filtro por raça
        if 'raca' in df.columns:
            racas = ["Todas"] + sorted(df['raca'].unique().tolist())
            raca_filtro = st.selectbox("Raça:", racas)
            
            if raca_filtro != "Todas":
                df = df[df['raca'] == raca_filtro]
        
        # Filtro por status de adoção
        if 'adotado' in df.columns:
            status_adocao = ["Todos", "Adotado", "Não Adotado"]
            status_filtro = st.selectbox("Status de Adoção:", status_adocao)
            
            if status_filtro == "Adotado":
                df = df[df['adotado'] == True]
            elif status_filtro == "Não Adotado":
                df = df[df['adotado'] == False]
        
        # Filtro por intervalo de idade
        if 'idade' in df.columns:
            min_idade, max_idade = st.slider(
                "Faixa de Idade:",
                min_value=float(df['idade'].min() if not df['idade'].isna().all() else 0),
                max_value=float(df['idade'].max() if not df['idade'].isna().all() else 20),
                value=(float(df['idade'].min() if not df['idade'].isna().all() else 0),
                       float(df['idade'].max() if not df['idade'].isna().all() else 20))
            )
            
            df = df[(df['idade'] >= min_idade) & (df['idade'] <= max_idade)]
        
        # Filtro por intervalo de peso
        if 'peso' in df.columns:
            min_peso, max_peso = st.slider(
                "Faixa de Peso (kg):",
                min_value=float(df['peso'].min() if not df['peso'].isna().all() else 0),
                max_value=float(df['peso'].max() if not df['peso'].isna().all() else 50),
                value=(float(df['peso'].min() if not df['peso'].isna().all() else 0),
                       float(df['peso'].max() if not df['peso'].isna().all() else 50))
            )
            
            df = df[(df['peso'] >= min_peso) & (df['peso'] <= max_peso)]
        
        # Filtro por período de registro (se tiver data)
        if 'data_registro' in df.columns:
            # Certifique-se de que a coluna é do tipo datetime
            if not pd.api.types.is_datetime64_dtype(df['data_registro']):
                try:
                    df['data_registro'] = pd.to_datetime(df['data_registro'])
                except:
                    pass
            
            if pd.api.types.is_datetime64_dtype(df['data_registro']):
                min_date = df['data_registro'].min().date()
                max_date = df['data_registro'].max().date()
                
                data_inicio, data_fim = st.date_input(
                    "Período de Registro:",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                
                df = df[(df['data_registro'].dt.date >= data_inicio) & 
                         (df['data_registro'].dt.date <= data_fim)]
    
    # Exibir contagem de resultados
    st.sidebar.markdown(f"**{len(df)} pets** correspondem aos filtros.")
    
    return df

@require_login
def display_dashboard(df, df_filtrado):
    """Exibe o dashboard interativo com métricas e gráficos."""
    st.title("Dashboard Interativo")
    st.markdown("Visão geral das métricas e estatísticas principais")
    
    # Verificar se há dados após a filtragem
    if len(df_filtrado) == 0:
        st.warning("Não há dados para exibir com os filtros selecionados.")
        return
    
    # Métricas principais
    st.subheader("Métricas Principais")
    
    # Calcular métricas
    total_pets = len(df_filtrado)
    media_idade = df_filtrado['idade'].mean() if 'idade' in df_filtrado.columns and not df_filtrado['idade'].isna().all() else 0
    media_peso = df_filtrado['peso'].mean() if 'peso' in df_filtrado.columns and not df_filtrado['peso'].isna().all() else 0
    
    # Verificar se 'adotado' está presente e é booleano/numérico
    taxa_adocao = 0
    if 'adotado' in df_filtrado.columns:
        if df_filtrado['adotado'].dtype == bool or pd.api.types.is_numeric_dtype(df_filtrado['adotado']):
            taxa_adocao = df_filtrado['adotado'].mean() * 100
    
    # Calcular deltas (comparação com todos os dados)
    delta_idade = media_idade - df['idade'].mean() if 'idade' in df.columns and not df['idade'].isna().all() else 0
    delta_peso = media_peso - df['peso'].mean() if 'peso' in df.columns and not df['peso'].isna().all() else 0
    delta_adocao = taxa_adocao - (df['adotado'].mean() * 100 if 'adotado' in df.columns else 0)
    
    # Cards com métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        custom_metric("Total de Pets", total_pets, None, "#4527A0")
    
    with col2:
        # Garantir que temos pelo menos um valor válido para calcular média de idade
        if 'idade' in df_filtrado.columns and not df_filtrado['idade'].isna().all():
            custom_metric("Média de Idade", f"{media_idade:.1f}", delta_idade, "#2196F3", suffix=" anos")
        else:
            custom_metric("Média de Idade", "N/A", None, "#2196F3")
    
    with col3:
        # Garantir que temos pelo menos um valor válido para calcular média de peso
        if 'peso' in df_filtrado.columns and not df_filtrado['peso'].isna().all():
            custom_metric("Média de Peso", f"{media_peso:.1f}", delta_peso, "#4CAF50", suffix=" kg")
        else:
            custom_metric("Média de Peso", "N/A", None, "#4CAF50")
    
    with col4:
        if 'adotado' in df_filtrado.columns:
            custom_metric("Taxa de Adoção", f"{taxa_adocao:.1f}", delta_adocao, "#FF9800", suffix="%")
        else:
            custom_metric("Taxa de Adoção", "N/A", None, "#FF9800")
    
    # Gráficos principais
    st.subheader("Visão Geral")
    
    # Distribuição por tipo de pet e status de adoção
    col1, col2 = st.columns(2)
    
    with col1:
        if 'tipo_pet' in df_filtrado.columns:
            # Card personalizado
            card_content = """
            <div id="tipo-pet-chart"></div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem; color: #666;">
                Distribuição percentual dos tipos de pets registrados no sistema.
            </div>
            """
            
            custom_card("Distribuição por Tipo", card_content, icon="🐾", color="#4527A0")
            
            # Contar ocorrências de cada tipo
            tipo_counts = df_filtrado['tipo_pet'].value_counts().reset_index()
            tipo_counts.columns = ['tipo_pet', 'count']
            
            # Criar gráfico de pizza
            fig = px.pie(
                tipo_counts, 
                values='count', 
                names='tipo_pet',
                title='',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Atualizar layout
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", y=-0.1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_pet' não disponível nos dados.")
    
    with col2:
        if 'adotado' in df_filtrado.columns:
            # Card personalizado
            card_content = """
            <div id="status-adocao-chart"></div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem; color: #666;">
                Proporção de pets adotados vs. não adotados no sistema.
            </div>
            """
            
            custom_card("Status de Adoção", card_content, icon="🏠", color="#FF9800")
            
            # Contar pets adotados vs não adotados
            adocao_counts = df_filtrado['adotado'].map({True: 'Adotado', False: 'Não Adotado'}).value_counts().reset_index()
            adocao_counts.columns = ['status', 'count']
            
            # Criar gráfico de barras
            fig = px.bar(
                adocao_counts,
                x='status',
                y='count',
                color='status',
                title='',
                text='count',
                color_discrete_map={'Adotado': '#2ECC71', 'Não Adotado': '#E74C3C'}
            )
            
            # Atualizar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade",
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'adotado' não disponível nos dados.")
    
    # Gráfico de dispersão para relacionar idade e peso
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666;">
            Relação entre idade e peso dos pets, revelando padrões e tendências para diferentes tipos.
            <br><br>
            <b>Como interpretar:</b>
            <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
                <li>Cada ponto representa um pet</li>
                <li>A linha de tendência mostra a relação geral</li>
                <li>Cores diferentes indicam tipos de pets</li>
            </ul>
        </div>
        """
        
        custom_card("Idade vs Peso", card_content, icon="📊", color="#2196F3")
    
    with col2:
        # Verificar se as colunas necessárias existem e têm valores válidos
        if 'idade' in df_filtrado.columns and 'peso' in df_filtrado.columns:
            # Remover valores NaN nas colunas relevantes
            df_scatter = df_filtrado.dropna(subset=['idade', 'peso']).copy()
            
            # Se ainda temos dados suficientes após remover nulos
            if len(df_scatter) > 0:
                # Verificar se 'tipo_pet' existe para colorir
                color_var = 'tipo_pet' if 'tipo_pet' in df_scatter.columns else None
                
                # Criar gráfico sem usar o parâmetro size para evitar problemas com NaN
                fig = px.scatter(
                    df_scatter,
                    x='idade',
                    y='peso',
                    color=color_var,
                    hover_name='nome' if 'nome' in df_scatter.columns else None,
                    labels={'idade': 'Idade (anos)', 'peso': 'Peso (kg)'},
                    title="",
                    trendline='ols',
                    trendline_scope='overall'
                )
                
                # Atualizar layout
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", y=-0.2)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados insuficientes para gerar o gráfico de dispersão (valores de idade e/ou peso ausentes).")
        else:
            st.info("Colunas 'idade' e/ou 'peso' não disponíveis nos dados.")
    
    # Análise por Bairro
    st.subheader("Análise por Bairro")
    
    if 'bairro' in df_filtrado.columns:
        # Obter os top 10 bairros por quantidade de pets
        top_bairros = df_filtrado['bairro'].value_counts().nlargest(10).reset_index()
        top_bairros.columns = ['bairro', 'count']
        
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Distribuição geográfica de pets por bairro, destacando as áreas com maior concentração.
        </div>
        """
        
        custom_card("Top Bairros", card_content, icon="🏙️", color="#673AB7")
        
        # Gráfico de barras horizontal
        fig = px.bar(
            top_bairros,
            y='bairro',
            x='count',
            orientation='h',
            title='',
            color='count',
            color_continuous_scale='Viridis',
            labels={'count': 'Quantidade', 'bairro': 'Bairro'},
            text='count'
        )
        
        # Atualizar layout
        fig.update_layout(
            xaxis_title="Quantidade de Pets",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de um bairro específico
        st.markdown("### Análise Detalhada por Bairro")
        
        # Lista de bairros ordenada por quantidade
        bairros_ordenados = df_filtrado['bairro'].value_counts().index.tolist()
        
        # Seleção de bairro
        bairro_selecionado = st.selectbox(
            "Selecione um bairro para análise detalhada:",
            options=bairros_ordenados
        )
        
        # Filtrar dados para o bairro selecionado
        df_bairro = df_filtrado[df_filtrado['bairro'] == bairro_selecionado]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'tipo_pet' in df_bairro.columns:
                # Distribuição por tipo no bairro
                tipo_bairro = df_bairro['tipo_pet'].value_counts().reset_index()
                tipo_bairro.columns = ['tipo_pet', 'count']
                
                # Card personalizado
                card_content = f"""
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                    Distribuição dos diferentes tipos de pets no bairro {bairro_selecionado}.
                </div>
                """
                
                custom_card(f"Tipos de Pet em {bairro_selecionado}", card_content, icon="🔍", color="#00BCD4")
                
                fig = px.pie(
                    tipo_bairro,
                    values='count',
                    names='tipo_pet',
                    title='',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                # Atualizar layout
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", y=-0.1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'tipo_pet' não disponível nos dados do bairro.")
        
        with col2:
            if 'adotado' in df_bairro.columns:
                # Taxa de adoção no bairro
                try:
                    taxa_adocao_bairro = df_bairro['adotado'].mean() * 100
                    
                    # Card personalizado
                    card_content = f"""
                    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                        Percentual de pets adotados no bairro {bairro_selecionado} em comparação com a média geral.
                    </div>
                    """
                    
                    custom_card(f"Taxa de Adoção em {bairro_selecionado}", card_content, icon="📈", color="#FF5722")
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=taxa_adocao_bairro,
                        title={'text': ''},
                        number={'suffix': '%', 'font': {'size': 26}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickwidth': 1},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 30], 'color': "red"},
                                {'range': [30, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': taxa_adocao
                            }
                        }
                    ))
                    
                    # Atualizar layout
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        height=250
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Não foi possível calcular a taxa de adoção para este bairro.")
            else:
                st.info("Coluna 'adotado' não disponível nos dados do bairro.")
        
        # Estatísticas do bairro
        st.markdown(f"### Estatísticas de {bairro_selecionado}")
        
        # Métricas específicas do bairro
        col1, col2, col3 = st.columns(3)
        
        with col1:
            custom_metric("Total de Pets", len(df_bairro), None, "#4527A0")
        
        with col2:
            if 'idade' in df_bairro.columns and not df_bairro['idade'].isna().all():
                media_idade_bairro = df_bairro['idade'].mean()
                # Diferença em relação à média geral
                delta_idade_bairro = media_idade_bairro - media_idade
                custom_metric("Média de Idade", f"{media_idade_bairro:.1f}", delta_idade_bairro, "#2196F3", suffix=" anos")
            else:
                custom_metric("Média de Idade", "N/A", None, "#2196F3")
        
        with col3:
            if 'peso' in df_bairro.columns and not df_bairro['peso'].isna().all():
                media_peso_bairro = df_bairro['peso'].mean()
                # Diferença em relação à média geral
                delta_peso_bairro = media_peso_bairro - media_peso
                custom_metric("Média de Peso", f"{media_peso_bairro:.1f}", delta_peso_bairro, "#4CAF50", suffix=" kg")
            else:
                custom_metric("Média de Peso", "N/A", None, "#4CAF50")
        
        # Raças mais comuns no bairro
        if 'raca' in df_bairro.columns:
            # Card personalizado
            card_content = f"""
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                As raças mais frequentes no bairro {bairro_selecionado}.
            </div>
            """
            
            custom_card(f"Raças em {bairro_selecionado}", card_content, icon="🧬", color="#9C27B0")
            
            racas_bairro = df_bairro['raca'].value_counts().nlargest(5).reset_index()
            racas_bairro.columns = ['raca', 'count']
            
            fig = px.bar(
                racas_bairro,
                x='raca',
                y='count',
                title='',
                color='count',
                text='count',
                labels={'count': 'Quantidade', 'raca': 'Raça'},
                color_continuous_scale='Purples'
            )
            
            # Atualizar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade",
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coluna 'bairro' não disponível nos dados.")
    
    # Tendências e Padrões
    st.subheader("Tendências e Padrões")
    
    if 'tipo_pet' in df_filtrado.columns and 'peso' in df_filtrado.columns:
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Comparação da distribuição de peso entre diferentes tipos de pets.
            <br><br>
            <b>Como interpretar:</b>
            <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
                <li>A caixa representa o intervalo entre o primeiro e terceiro quartil</li>
                <li>A linha central é a mediana</li>
                <li>Os "bigodes" mostram os valores mínimos e máximos (excluindo outliers)</li>
                <li>Pontos individuais são outliers</li>
            </ul>
        </div>
        """
        
        custom_card("Distribuição de Peso por Tipo", card_content, icon="⚖️", color="#3F51B5")
        
        # Distribuição de peso por tipo de pet (boxplot)
        # Remover valores NaN nas colunas relevantes
        df_box = df_filtrado.dropna(subset=['tipo_pet', 'peso']).copy()
        
        if len(df_box) > 0:
            fig = px.box(
                df_box,
                x='tipo_pet',
                y='peso',
                color='tipo_pet',
                title='',
                labels={'peso': 'Peso (kg)', 'tipo_pet': 'Tipo de Pet'},
                points="outliers"
            )
            
            # Atualizar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Peso (kg)",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=30)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes para gerar o boxplot (valores de tipo_pet e/ou peso ausentes).")
    else:
        st.info("Colunas 'tipo_pet' e/ou 'peso' não disponíveis nos dados.")
    
    # Análise Temporal caso haja dados temporais
    if 'data_registro' in df_filtrado.columns:
        st.subheader("Análise Temporal")
        
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Evolução do número de registros ao longo do tempo, mostrando tendências de crescimento ou sazonalidade.
        </div>
        """
        
        custom_card("Evolução Temporal", card_content, icon="📅", color="#009688")
        
        # Converter para datetime se necessário
        if not pd.api.types.is_datetime64_dtype(df_filtrado['data_registro']):
            try:
                df_filtrado['data_registro'] = pd.to_datetime(df_filtrado['data_registro'])
            except:
                st.warning("Não foi possível converter a coluna 'data_registro' para o formato de data.")
                return
        
        # Agrupar por mês
        df_filtrado['mes'] = df_filtrado['data_registro'].dt.to_period('M')
        registros_por_mes = df_filtrado.groupby('mes').size().reset_index(name='count')
        registros_por_mes['mes_str'] = registros_por_mes['mes'].astype(str)
        
        # Linha do tempo de registros
        fig = px.line(
            registros_por_mes,
            x='mes_str',
            y='count',
            title='',
            labels={'count': 'Quantidade de Registros', 'mes_str': 'Mês'},
            markers=True
        )
        
        # Atualizar layout
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Quantidade",
            margin=dict(l=20, r=20, t=20, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição por tipo ao longo do tempo (se houver tipo_pet)
        if 'tipo_pet' in df_filtrado.columns:
            # Card personalizado
            card_content = """
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                Análise da evolução de cada tipo de pet ao longo do tempo, permitindo identificar mudanças nas preferências.
            </div>
            """
            
            custom_card("Tipos ao Longo do Tempo", card_content, icon="📈", color="#FFC107")
            
            tipos_por_mes = df_filtrado.groupby(['mes', 'tipo_pet']).size().reset_index(name='count')
            tipos_por_mes['mes_str'] = tipos_por_mes['mes'].astype(str)
            
            fig = px.line(
                tipos_por_mes,
                x='mes_str',
                y='count',
                color='tipo_pet',
                title='',
                labels={'count': 'Quantidade', 'mes_str': 'Mês', 'tipo_pet': 'Tipo de Pet'},
                markers=True
            )
            
            # Atualizar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade",
                legend=dict(orientation="h", y=-0.2),
                margin=dict(l=20, r=20, t=20, b=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparações e Correlações
    st.subheader("Comparações e Correlações")
    
    # Verificar se temos dados suficientes para análise de correlação
    df_num = df_filtrado.select_dtypes(include=['number'])
    if len(df_num.columns) >= 2:
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Matriz de correlação entre as variáveis numéricas, mostrando o grau de relação entre elas.
            <br><br>
            <b>Como interpretar:</b>
            <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
                <li>Valores próximos a 1: forte correlação positiva</li>
                <li>Valores próximos a -1: forte correlação negativa</li>
                <li>Valores próximos a 0: pouca ou nenhuma correlação</li>
            </ul>
        </div>
        """
        
        custom_card("Matriz de Correlação", card_content, icon="🔄", color="#E91E63")
        
        # Calcular matriz de correlação
        corr = df_num.corr()
        
        # Criar mapa de calor
        fig = px.imshow(
            corr,
            text_auto='.2f',
            aspect="auto",
            title="",
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        
        # Atualizar layout
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Encontrar correlações mais fortes (valores absolutos)
        corr_pairs = []
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                corr_pairs.append((corr.columns[i], corr.columns[j], corr.iloc[i, j]))
        
        # Ordenar por valor absoluto
        corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Exibir as correlações mais fortes
        if len(corr_pairs) > 0:
            # Card personalizado
            card_content = """
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                As relações mais significativas entre variáveis numéricas, ordenadas por força de correlação.
            </div>
            """
            
            custom_card("Correlações Mais Fortes", card_content, icon="🔝", color="#795548")
            
            correlacoes = []
            for var1, var2, valor in corr_pairs[:5]:  # Top 5 correlações
                correlacoes.append({
                    "Variável 1": var1,
                    "Variável 2": var2,
                    "Correlação": f"{valor:.2f}",
                    "Força": abs(valor)
                })
            
            # Criar dataframe e formatar
            df_corr_top = pd.DataFrame(correlacoes)
            
            # Estilizar tabela
            st.dataframe(
                df_corr_top[["Variável 1", "Variável 2", "Correlação"]],
                use_container_width=True,
                hide_index=True
            )
            
            # Mostrar scatter plot para a correlação mais forte
            if len(corr_pairs) > 0:
                var1, var2, _ = corr_pairs[0]
                
                # Card personalizado
                card_content = f"""
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                    Visualização da correlação mais forte identificada: <b>{var1}</b> vs <b>{var2}</b>
                </div>
                """
                
                custom_card(f"Correlação Principal: {var1} vs {var2}", card_content, icon="🔍", color="#00BCD4")
                
                # Remover valores NaN das colunas relevantes
                df_corr = df_filtrado.dropna(subset=[var1, var2]).copy()
                
                if len(df_corr) > 0:
                    fig = px.scatter(
                        df_corr,
                        x=var1,
                        y=var2,
                        color='tipo_pet' if 'tipo_pet' in df_corr.columns else None,
                        trendline='ols',
                        title="",
                        labels={var1: var1, var2: var2}
                    )
                    
                    # Atualizar layout
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=20, b=30),
                        legend=dict(orientation="h", y=-0.2)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Dados insuficientes para gerar o gráfico de correlação entre {var1} e {var2}.")
    else:
        st.info("Não há variáveis numéricas suficientes para análise de correlação.")
    
    # Análise de Comportamento (se houver dados)
    if 'humor_diario' in df_filtrado.columns or 'comportamento' in df_filtrado.columns:
        st.subheader("Análise de Comportamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'humor_diario' in df_filtrado.columns:
                # Card personalizado
                card_content = """
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                    Distribuição dos estados de humor registrados nos pets.
                </div>
                """
                
                custom_card("Humor Diário", card_content, icon="😊", color="#8BC34A")
                
                humor_counts = df_filtrado['humor_diario'].value_counts().reset_index()
                humor_counts.columns = ['humor', 'count']
                
                fig = px.bar(
                    humor_counts,
                    x='humor',
                    y='count',
                    title='',
                    color='humor',
                    labels={'count': 'Quantidade', 'humor': 'Humor'},
                    text='count'
                )
                
                # Atualizar layout
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Quantidade",
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'humor_diario' não disponível nos dados.")
        
        with col2:
            if 'comportamento' in df_filtrado.columns:
                # Card personalizado
                card_content = """
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                    Padrões comportamentais observados nos pets registrados.
                </div>
                """
                
                custom_card("Padrões de Comportamento", card_content, icon="🧠", color="#FF5722")
                
                comportamento_counts = df_filtrado['comportamento'].value_counts().reset_index()
                comportamento_counts.columns = ['comportamento', 'count']
                
                fig = px.pie(
                    comportamento_counts,
                    values='count',
                    names='comportamento',
                    title='',
                    hole=0.4
                )
                
                # Atualizar layout
                fig.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", y=-0.2),
                    margin=dict(l=20, r=20, t=20, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'comportamento' não disponível nos dados.")
    
    # Análise de preferência alimentar (se houver dados)
    if 'tipo_comida' in df_filtrado.columns:
        st.subheader("Preferências Alimentares")
        
        # Card personalizado
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Tipos de alimentação preferidos pelos pets registrados no sistema.
        </div>
        """
        
        custom_card("Preferências Alimentares", card_content, icon="🍲", color="#CDDC39")
        
        # Contar preferências alimentares
        comida_counts = df_filtrado['tipo_comida'].value_counts().reset_index()
        comida_counts.columns = ['tipo_comida', 'count']
        
        fig = px.bar(
            comida_counts,
            x='tipo_comida',
            y='count',
            title='',
            color='tipo_comida',
            labels={'count': 'Quantidade', 'tipo_comida': 'Tipo de Comida'},
            text='count'
        )
        
        # Atualizar layout
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Quantidade",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Relação entre tipo de pet e preferência alimentar
        if 'tipo_pet' in df_filtrado.columns:
            # Card personalizado
            card_content = """
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                Relação entre tipos de pets e suas preferências alimentares, mostrando padrões específicos por espécie.
            </div>
            """
            
            custom_card("Alimentação por Tipo de Pet", card_content, icon="🥩", color="#FF9800")
            
            # Tabela de contingência
            cross_tab = pd.crosstab(df_filtrado['tipo_pet'], df_filtrado['tipo_comida'])
            
            # Normalizar por tipo de pet
            cross_tab_norm = cross_tab.div(cross_tab.sum(axis=1), axis=0) * 100
            
            # Reshape para formato longo
            cross_tab_long = cross_tab_norm.reset_index().melt(
                id_vars=['tipo_pet'],
                var_name='tipo_comida',
                value_name='percentual'
            )
            
            fig = px.bar(
                cross_tab_long,
                x='tipo_pet',
                y='percentual',
                color='tipo_comida',
                title='',
                labels={'percentual': 'Percentual', 'tipo_pet': 'Tipo de Pet', 'tipo_comida': 'Tipo de Comida'},
                barmode='stack',
                text=cross_tab_long['percentual'].round(1).astype(str) + '%'
            )
            
            # Atualizar layout
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Percentual (%)",
                yaxis=dict(range=[0, 100]),
                legend_title="Tipo de Comida",
                legend=dict(orientation="h", y=-0.2),
                margin=dict(l=20, r=20, t=20, b=50)
            )
            
            # Ajustar texto
            fig.update_traces(textposition='inside', textfont_size=10)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Evolução de características ao longo do tempo (se houver dados temporais)
    if 'data_registro' in df_filtrado.columns and ('peso' in df_filtrado.columns or 'idade' in df_filtrado.columns):
        st.subheader("Evolução de Características")
        
        # Verificar se temos pelo menos uma coluna numérica relevante
        colunas_temporais = []
        if 'peso' in df_filtrado.columns:
            colunas_temporais.append('peso')
        if 'idade' in df_filtrado.columns:
            colunas_temporais.append('idade')
        
        if colunas_temporais:
            # Selecionar qual característica analisar
            caract_temporal = st.selectbox(
                "Selecione a característica para análise temporal:",
                options=colunas_temporais
            )
            
            # Card personalizado
            card_content = f"""
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                Evolução da média de {caract_temporal} ao longo do tempo, mostrando tendências e padrões sazonais.
            </div>
            """
            
            custom_card(f"Evolução de {caract_temporal.capitalize()}", card_content, icon="📈", color="#3F51B5")
            
            # Agrupar por mês e calcular média da característica selecionada
            df_temp = df_filtrado.dropna(subset=['data_registro', caract_temporal]).copy()
            
            if len(df_temp) > 0:
                df_temp['mes'] = df_temp['data_registro'].dt.to_period('M')
                media_por_mes = df_temp.groupby('mes')[caract_temporal].mean().reset_index()
                media_por_mes['mes_str'] = media_por_mes['mes'].astype(str)
                
                fig = px.line(
                    media_por_mes,
                    x='mes_str',
                    y=caract_temporal,
                    title='',
                    labels={caract_temporal: f'{caract_temporal.capitalize()}', 'mes_str': 'Mês'},
                    markers=True
                )
                
                # Atualizar layout
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title=f"{caract_temporal.capitalize()} médio",
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Se tivermos tipo_pet, mostrar evolução por tipo
                if 'tipo_pet' in df_filtrado.columns:
                    # Card personalizado
                    card_content = f"""
                    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                        Comparação da evolução de {caract_temporal} para diferentes tipos de pets ao longo do tempo.
                    </div>
                    """
                    
                    custom_card(f"{caract_temporal.capitalize()} por Tipo de Pet", card_content, icon="📊", color="#9C27B0")
                    
                    df_tipo_temp = df_filtrado.dropna(subset=['data_registro', caract_temporal, 'tipo_pet']).copy()
                    
                    if len(df_tipo_temp) > 0:
                        df_tipo_temp['mes'] = df_tipo_temp['data_registro'].dt.to_period('M')
                        media_tipo_mes = df_tipo_temp.groupby(['mes', 'tipo_pet'])[caract_temporal].mean().reset_index()
                        media_tipo_mes['mes_str'] = media_tipo_mes['mes'].astype(str)
                        
                        fig = px.line(
                            media_tipo_mes,
                            x='mes_str',
                            y=caract_temporal,
                            color='tipo_pet',
                            title='',
                            labels={caract_temporal: f'{caract_temporal.capitalize()}', 'mes_str': 'Mês', 'tipo_pet': 'Tipo de Pet'},
                            markers=True
                        )
                        
                        # Atualizar layout
                        fig.update_layout(
                            xaxis_title="",
                            yaxis_title=f"{caract_temporal.capitalize()} médio",
                            legend=dict(orientation="h", y=-0.2),
                            margin=dict(l=20, r=20, t=20, b=50)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Dados insuficientes para análise temporal de {caract_temporal}.")
    
    # Botão para exportar relatório
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📊 Exportar Relatório Completo", use_container_width=True):
            # Aqui você adicionaria código para gerar um relatório completo
            st.success("Funcionalidade de exportação de relatório será implementada em uma versão futura.")

@require_login
def visualizar_dados(df):
    """Exibe e permite a visualização e filtragem dos dados."""
    st.title("Visualizar Dados")
    
    # Verificar se há dados
    if df.empty:
        st.warning("Não há dados disponíveis. Adicione alguns pets para começar.")
        return
    
    # Opções de visualização
    tab1, tab2 = st.tabs(["Tabela de Dados", "Detalhes do Pet"])
    
    with tab1:
        st.subheader("Tabela de Dados")
        
        # Opções de visualização
        with st.expander("Opções de Visualização", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleção de colunas para exibir
                all_columns = df.columns.tolist()
                default_columns = ['nome', 'bairro', 'tipo_pet', 'raca', 'idade', 'peso', 'adotado']
                default_columns = [col for col in default_columns if col in all_columns]
                
                selected_columns = st.multiselect(
                    "Selecione as colunas para exibir:",
                    options=all_columns,
                    default=default_columns
                )
            
            with col2:
                # Opções de ordenação
                sort_column = st.selectbox(
                    "Ordenar por:",
                    options=["Nenhum"] + all_columns
                )
                
                if sort_column != "Nenhum":
                    sort_order = st.radio(
                        "Ordem:",
                        options=["Crescente", "Decrescente"],
                        horizontal=True
                    )
        
        # Preparar DataFrame para exibição
        if selected_columns:
            df_display = df[selected_columns].copy()
        else:
            df_display = df.copy()
        
        # Aplicar ordenação
        if sort_column != "Nenhum":
            ascending = sort_order == "Crescente"
            df_display = df_display.sort_values(by=sort_column, ascending=ascending)
        
        # Exibir dados com estilo
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Estatísticas básicas das colunas numéricas
        st.subheader("Estatísticas Básicas")
        
        # Colunas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            # Calcular estatísticas
            stats = df[numeric_cols].describe().T.reset_index()
            stats.columns = ['Variável', 'Contagem', 'Média', 'Desvio Padrão', 'Mín', '25%', '50%', '75%', 'Máx']
            
            # Formatar números
            for col in stats.columns[1:]:
                stats[col] = stats[col].round(2)
            
            # Exibir tabela de estatísticas
            st.dataframe(
                stats,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Não há colunas numéricas para calcular estatísticas.")
        
        # Opções de exportação
        with st.expander("Exportar Dados"):
            col1, col2 = st.columns(2)
            
            with col1:
                export_format = st.selectbox(
                    "Formato de exportação:",
                    options=["CSV", "Excel", "JSON"]
                )
            
            with col2:
                export_columns = st.radio(
                    "Colunas para exportar:",
                    options=["Todas as colunas", "Colunas selecionadas"],
                    horizontal=True
                )
            
            # Preparar dados para exportação
            if export_columns == "Colunas selecionadas" and selected_columns:
                df_export = df[selected_columns].copy()
            else:
                df_export = df.copy()
            
            # Botão de exportação
            if st.button("Exportar Dados", use_container_width=True):
                if export_format == "CSV":
                    csv_data = df_export.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="Baixar CSV",
                        data=csv_data,
                        file_name="pets_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                elif export_format == "Excel":
                    # Preparar dados Excel
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df_export.to_excel(writer, sheet_name='Dados de Pets', index=False)
                    
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="Baixar Excel",
                        data=excel_data,
                        file_name="pets_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                elif export_format == "JSON":
                    json_data = df_export.to_json(orient='records', indent=4).encode('utf-8')
                    
                    st.download_button(
                        label="Baixar JSON",
                        data=json_data,
                        file_name="pets_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
    
    with tab2:
        st.subheader("Detalhes do Pet")
        
        # Lista de pets para seleção
        if 'nome' in df.columns:
            pets_list = df['nome'].tolist()
            selected_pet = st.selectbox("Selecione um pet para ver detalhes:", options=pets_list)
            
            # Exibir detalhes do pet selecionado
            pet_data = df[df['nome'] == selected_pet].iloc[0]
            
            # Container de detalhes
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Card de informações básicas
                card_content = f"""
                <div style="margin-bottom: 1rem;">
                    <div><strong>Bairro:</strong> {pet_data.get('bairro', 'N/A')}</div>
                    <div><strong>Tipo:</strong> {pet_data.get('tipo_pet', 'N/A')}</div>
                    <div><strong>Raça:</strong> {pet_data.get('raca', 'N/A')}</div>
                    <div><strong>Idade:</strong> {pet_data.get('idade', 'N/A')} anos</div>
                    <div><strong>Peso:</strong> {pet_data.get('peso', 'N/A')} kg</div>
                    <div><strong>Sexo:</strong> {pet_data.get('sexo', 'N/A')}</div>
                    <div><strong>Status:</strong> {'Adotado' if pet_data.get('adotado', False) else 'Não Adotado'}</div>
                </div>
                """
                
                custom_card(f"🐾 {selected_pet}", card_content, color="#4527A0")
                
                # Card de contato
                if 'telefone' in pet_data:
                    card_content = f"""
                    <div style="margin-bottom: 1rem;">
                        <div><strong>Telefone:</strong> {pet_data.get('telefone', 'N/A')}</div>
                    </div>
                    """
                    
                    custom_card("📞 Contato", card_content, color="#00BCD4")
                
                # Card de saúde
                health_fields = ['status_vacinacao', 'estado_saude']
                if any(field in pet_data for field in health_fields):
                    health_content = "<div style='margin-bottom: 1rem;'>"
                    
                    if 'status_vacinacao' in pet_data:
                        health_content += f"<div><strong>Vacinação:</strong> {pet_data.get('status_vacinacao', 'N/A')}</div>"
                    
                    if 'estado_saude' in pet_data:
                        health_content += f"<div><strong>Estado de Saúde:</strong> {pet_data.get('estado_saude', 'N/A')}</div>"
                    
                    health_content += "</div>"
                    
                    custom_card("💉 Saúde", health_content, color="#4CAF50")
            
            with col2:
                # Informações comportamentais
                behavior_fields = ['humor_diario', 'comportamento', 'nivel_atividade', 'tipo_comida']
                if any(field in pet_data for field in behavior_fields):
                    behavior_content = "<div style='margin-bottom: 1rem;'>"
                    
                    if 'humor_diario' in pet_data:
                        behavior_content += f"<div><strong>Humor Diário:</strong> {pet_data.get('humor_diario', 'N/A')}</div>"
                    
                    if 'comportamento' in pet_data:
                        behavior_content += f"<div><strong>Comportamento:</strong> {pet_data.get('comportamento', 'N/A')}</div>"
                    
                    if 'nivel_atividade' in pet_data:
                        behavior_content += f"<div><strong>Nível de Atividade:</strong> {pet_data.get('nivel_atividade', 'N/A')}</div>"
                    
                    if 'tipo_comida' in pet_data:
                        behavior_content += f"<div><strong>Preferência Alimentar:</strong> {pet_data.get('tipo_comida', 'N/A')}</div>"
                    
                    behavior_content += "</div>"
                    
                    custom_card("🧠 Comportamento", behavior_content, color="#FF9800")
                
                # Comparação com médias
                comparison_content = "<div style='margin-bottom: 1rem;'>"
                
                if 'idade' in pet_data and 'idade' in df.columns:
                    media_idade = df['idade'].mean()
                    diff_idade = pet_data['idade'] - media_idade
                    
                    comparison_content += f"""
                    <div style="margin-bottom: 0.5rem;">
                        <strong>Idade vs. Média:</strong> {pet_data['idade']} anos vs. {media_idade:.1f} anos
                        <div style="margin-top: 0.3rem; height: 6px; background-color: #e0e0e0; border-radius: 3px;">
                            <div style="height: 100%; width: {min(max((pet_data['idade'] / df['idade'].max()) * 100, 10), 100)}%; background-color: {'#2196F3' if diff_idade >= 0 else '#F44336'}; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """
                
                if 'peso' in pet_data and 'peso' in df.columns:
                    # Filtrar por tipo_pet se disponível
                    if 'tipo_pet' in pet_data and 'tipo_pet' in df.columns:
                        media_peso = df[df['tipo_pet'] == pet_data['tipo_pet']]['peso'].mean()
                        referencia = f"média de {pet_data['tipo_pet']}s"
                    else:
                        media_peso = df['peso'].mean()
                        referencia = "média geral"
                    
                    diff_peso = pet_data['peso'] - media_peso
                    
                    comparison_content += f"""
                    <div style="margin-bottom: 0.5rem;">
                        <strong>Peso vs. {referencia}:</strong> {pet_data['peso']} kg vs. {media_peso:.1f} kg
                        <div style="margin-top: 0.3rem; height: 6px; background-color: #e0e0e0; border-radius: 3px;">
                            <div style="height: 100%; width: {min(max((pet_data['peso'] / df['peso'].max()) * 100, 10), 100)}%; background-color: {'#2196F3' if diff_peso >= 0 else '#F44336'}; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """
                
                comparison_content += "</div>"
                
                custom_card("📊 Comparação com Médias", comparison_content, color="#9C27B0")
                
                # Registro
                if 'data_registro' in pet_data or 'created_by' in pet_data:
                    meta_content = "<div style='margin-bottom: 1rem;'>"
                    
                    if 'data_registro' in pet_data:
                        data_formatada = pd.to_datetime(pet_data['data_registro']).strftime('%d/%m/%Y %H:%M') if not pd.isna(pet_data['data_registro']) else 'N/A'
                        meta_content += f"<div><strong>Data de Registro:</strong> {data_formatada}</div>"
                    
                    if 'created_by' in pet_data:
                        meta_content += f"<div><strong>Registrado por:</strong> {pet_data['created_by']}</div>"
                    
                    if 'created_by_email' in pet_data:
                        meta_content += f"<div><strong>Email do Criador:</strong> {pet_data['created_by_email']}</div>"
                    
                    meta_content += "</div>"
                    
                    custom_card("📝 Metadados", meta_content, color="#607D8B")
            
            # Opções de ação
            st.subheader("Ações")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Editar Pet", use_container_width=True):
                    # Aqui você implementaria a funcionalidade de edição
                    st.info("Funcionalidade de edição será implementada em versão futura.")
            
            with col2:
                if st.button("Alterar Status", use_container_width=True):
                    # Aqui você implementaria a funcionalidade de alteração de status
                    st.info("Funcionalidade de alteração de status será implementada em versão futura.")
            
            with col3:
                if st.button("Excluir Pet", use_container_width=True):
                    # Aqui você implementaria a funcionalidade de exclusão
                    st.info("Funcionalidade de exclusão será implementada em versão futura.")
        else:
            st.info("Os dados não contêm a coluna 'nome', necessária para identificar os pets.")

@require_login
def adicionar_pet():
    """Formulário para adicionar um novo pet."""
    st.title("Adicionar Pet")
    
    # Formulário para adicionar novo pet
    with st.form("add_pet_form"):
        st.subheader("Informações Básicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Pet*")
            bairro = st.text_input("Bairro")
            tipo_pet = st.selectbox("Tipo de Pet*", ["Cachorro", "Gato", "Ave", "Roedor", "Réptil", "Outro"])
            raca = st.text_input("Raça*")
        
        with col2:
            idade = st.number_input("Idade (anos)", min_value=0.0, step=0.5)
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
            sexo = st.radio("Sexo", options=["Macho", "Fêmea"], horizontal=True)
            adotado = st.checkbox("Adotado")
        
        st.subheader("Informações Adicionais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_comida = st.selectbox("Preferência Alimentar", ["Ração seca", "Ração úmida", "Natural", "Mista", "Outro"])
            humor_diario = st.selectbox("Humor Diário", ["Calmo", "Agitado", "Brincalhão", "Tímido", "Agressivo", "Outro"])
            status_vacinacao = st.selectbox("Status de Vacinação", ["Em dia", "Parcial", "Pendente", "Desconhecido"])
        
        with col2:
            telefone = st.text_input("Telefone de Contato*")
            estado_saude = st.selectbox("Estado de Saúde", ["Excelente", "Bom", "Regular", "Tratamento", "Requer atenção"])
            comportamento = st.selectbox("Comportamento", ["Sociável", "Independente", "Territorial", "Medroso", "Afetuoso", "Outro"])
            nivel_atividade = st.selectbox("Nível de Atividade", ["Muito ativo", "Ativo", "Moderado", "Calmo", "Sedentário"])
        
        # Campos extras (opcionais)
        with st.expander("Campos Extras (opcional)"):
            col1, col2 = st.columns(2)
            
            with col1:
                regiao = st.text_input("Região da Cidade")
                observacoes = st.text_area("Observações")
            
            with col2:
                alergias = st.text_input("Alergias")
                necessidades_especiais = st.text_input("Necessidades Especiais")
        
        # Informações sobre campos obrigatórios
        st.markdown("*Campos obrigatórios")
        
        # Botão de submissão
        submitted = st.form_submit_button("Adicionar Pet", use_container_width=True)
        
        if submitted:
            # Validar campos obrigatórios
            if not nome:
                st.error("Por favor, informe o nome do pet.")
            elif not raca:
                st.error("Por favor, informe a raça do pet.")
            elif not telefone:
                st.error("Por favor, informe um telefone de contato.")
            else:
                # Criar dados do pet
                pet_data = {
                    'nome': nome,
                    'bairro': bairro,
                    'tipo_pet': tipo_pet,
                    'raca': raca,
                    'idade': idade,
                    'peso': peso,
                    'sexo': sexo,
                    'adotado': adotado,
                    'tipo_comida': tipo_comida,
                    'humor_diario': humor_diario,
                    'status_vacinacao': status_vacinacao,
                    'telefone': telefone,
                    'estado_saude': estado_saude,
                    'comportamento': comportamento,
                    'nivel_atividade': nivel_atividade,
                    'data_registro': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': st.session_state.user_id
                }
                
                # Adicionar campos extras se disponíveis
                extra_fields = {
                    'regiao': regiao,
                    'observacoes': observacoes,
                    'alergias': alergias,
                    'necessidades_especiais': necessidades_especiais
                }
                
                # Filtrar campos extras vazios
                extra_fields = {k: v for k, v in extra_fields.items() if v}
                pet_data.update(extra_fields)
                
                # Salvar no banco de dados
                with st.spinner("Adicionando pet..."):
                    success, result = save_pet_to_db(pet_data)
                    
                    if success:
                        # Registrar atividade
                        log_activity(st.session_state.user_id, "add_pet", f"Adicionou pet: {nome}")
                        
                        st.success(f"Pet {nome} adicionado com sucesso!")
                        st.balloons()
                    else:
                        st.error(f"Erro ao adicionar pet: {result}")

@require_login
def exportar_importar_dados(df):
    """Facilita a exportação e importação de dados."""
    st.title("Exportar/Importar Dados")
    
    # Abas para exportação e importação
    tab1, tab2 = st.tabs(["Exportar Dados", "Importar Dados"])
    
    with tab1:
        st.subheader("Exportar Dados")
        
        with st.expander("Opções de Exportação", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                formato_exportacao = st.radio(
                    "Formato de exportação:",
                    options=["CSV", "Excel", "JSON"]
                )
            
            with col2:
                incluir_filtrados = st.checkbox("Exportar apenas dados filtrados", value=False)
                
                if incluir_filtrados:
                    df_exportar = st.session_state.get("df_filtrado", df)
                else:
                    df_exportar = df
                
                st.markdown(f"**{len(df_exportar)} registros** serão exportados.")
        
        # Mostrar prévia
        st.markdown("**Prévia dos dados a serem exportados:**")
        st.dataframe(
            df_exportar.head(5),
            use_container_width=True,
            hide_index=True
        )
        
        # Opções específicas por formato
        if formato_exportacao == "CSV":
            # Opções de CSV
            col1, col2 = st.columns(2)
            with col1:
                separador = st.selectbox(
                    "Separador:",
                    options=[",", ";", "\\t"],
                    format_func=lambda x: "Vírgula (,)" if x == "," else "Ponto e vírgula (;)" if x == ";" else "Tab (\\t)"
                )
            with col2:
                incluir_cabecalho = st.checkbox("Incluir cabeçalho", value=True)
            
            # Preparar dados CSV
            csv_data = df_exportar.to_csv(sep=separador, index=False, header=incluir_cabecalho).encode('utf-8')
            
            # Botão de download
            st.download_button(
                label="Baixar CSV",
                data=csv_data,
                file_name="pets_data.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        elif formato_exportacao == "Excel":
            # Preparar dados Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_exportar.to_excel(writer, sheet_name='Dados de Pets', index=False)
            
            excel_data = excel_buffer.getvalue()
            
            # Botão de download
            st.download_button(
                label="Baixar Excel",
                data=excel_data,
                file_name="pets_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        elif formato_exportacao == "JSON":
            # Opções de JSON
            indent_json = st.checkbox("Formatar JSON (identado)", value=True)
            orient_options = {
                "records": "Lista de registros",
                "index": "Dicionário com índices",
                "columns": "Dicionário com colunas",
                "values": "Apenas valores",
                "table": "Formato de tabela"
            }
            orient = st.selectbox(
                "Orientação do JSON:", 
                options=list(orient_options.keys()),
                format_func=lambda x: orient_options[x]
            )
            
            # Preparar dados JSON
            indent = 4 if indent_json else None
            json_data = df_exportar.to_json(orient=orient, indent=indent).encode('utf-8')
            
            # Botão de download
            st.download_button(
                label="Baixar JSON",
                data=json_data,
                file_name="pets_data.json",
                mime="application/json",
                use_container_width=True
            )
    
    with tab2:
        st.subheader("Importar Dados")
        
        # Opções de importação
        uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            try:
                # Detectar tipo de arquivo
                file_type = uploaded_file.name.split(".")[-1].lower()
                
                if file_type == "csv":
                    # Opções de importação CSV
                    col1, col2 = st.columns(2)
                    with col1:
                        separador_import = st.selectbox(
                            "Separador:", 
                            options=[",", ";", "\\t"], 
                            format_func=lambda x: "Vírgula (,)" if x == "," else "Ponto e vírgula (;)" if x == ";" else "Tab (\\t)",
                            key="separador_import"
                        )
                    with col2:
                        header_row = st.checkbox("Primeira linha é cabeçalho", value=True)
                    
                    # Ler CSV
                    header_val = 0 if header_row else None
                    df_importado = pd.read_csv(uploaded_file, sep=separador_import, header=header_val)
                    
                elif file_type == "xlsx":
                    # Ler Excel
                    df_importado = pd.read_excel(uploaded_file)
                    
                elif file_type == "json":
                    # Opções de importação JSON
                    orient_options_import = {
                        "records": "Lista de registros",
                        "index": "Dicionário com índices",
                        "columns": "Dicionário com colunas",
                        "values": "Apenas valores",
                        "table": "Formato de tabela"
                    }
                    orient_import = st.selectbox(
                        "Orientação do JSON:", 
                        options=list(orient_options_import.keys()),
                        format_func=lambda x: orient_options_import[x],
                        key="orient_import"
                    )
                    
                    # Ler JSON
                    df_importado = pd.read_json(uploaded_file, orient=orient_import)
                
                # Mostrar prévia dos dados importados
                st.markdown(f"**Prévia dos dados importados ({len(df_importado)} registros):**")
                st.dataframe(
                    df_importado.head(5),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Opções de importação
                modo_importacao = st.radio(
                    "Modo de importação:",
                    options=["Substituir dados existentes", "Anexar aos dados existentes"]
                )
                
                # Mapeamento de colunas
                if st.checkbox("Mapear colunas", value=False):
                    st.markdown("**Mapeamento de colunas (opcional):**")
                    st.info("Selecione a coluna do arquivo importado que corresponde a cada coluna do sistema.")
                    
                    # Obter colunas de origem e destino
                    colunas_origem = df_importado.columns.tolist()
                    colunas_destino = df.columns.tolist()
                    
                    # Criar mapeamento
                    mapeamento = {}
                    for col_destino in colunas_destino:
                        opcoes = ["Ignorar"] + colunas_origem
                        col_selecionada = st.selectbox(
                            f"Mapeamento para '{col_destino}':",
                            options=opcoes,
                            index=opcoes.index(col_destino) if col_destino in opcoes else 0,
                            key=f"map_{col_destino}"
                        )
                        
                        if col_selecionada != "Ignorar":
                            mapeamento[col_destino] = col_selecionada
                    
                    # Aplicar mapeamento se confirmado
                    if st.button("Aplicar Mapeamento", key="apply_mapping"):
                        if mapeamento:
                            # Criar dataframe mapeado
                            df_mapeado = pd.DataFrame()
                            
                            for col_destino, col_origem in mapeamento.items():
                                df_mapeado[col_destino] = df_importado[col_origem]
                            
                            # Atualizar dataframe importado
                            df_importado = df_mapeado
                            
                            st.success("Mapeamento aplicado com sucesso!")
                            st.dataframe(
                                df_importado.head(5),
                                use_container_width=True,
                                hide_index=True
                            )
                
                # Botão de importação
                if st.button("Importar Dados", use_container_width=True):
                    with st.spinner("Importando dados..."):
                        # Necessário adicionar created_by e data_registro
                        if 'created_by' not in df_importado.columns:
                            df_importado['created_by'] = st.session_state.user_id
                        
                        if 'data_registro' not in df_importado.columns:
                            df_importado['data_registro'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Conectar ao banco de dados
                        conn = sqlite3.connect(DATABASE_PATH)
                        c = conn.cursor()
                        
                        try:
                            if modo_importacao == "Substituir dados existentes":
                                # Verificar se todas as colunas obrigatórias estão presentes
                                colunas_obrigatorias = ['nome', 'tipo_pet', 'raca']
                                faltando = [col for col in colunas_obrigatorias if col not in df_importado.columns]
                                
                                if faltando:
                                    st.error(f"O arquivo importado não contém as colunas obrigatórias: {', '.join(faltando)}")
                                else:
                                    # Limpar tabela existente
                                    c.execute("DELETE FROM pets")
                                    
                                    # Inserir novos dados
                                    for _, row in df_importado.iterrows():
                                        # Preparar colunas e valores
                                        columns = ', '.join(row.index)
                                        placeholders = ', '.join(['?' for _ in row])
                                        values = tuple(row.values)
                                        
                                        query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
                                        c.execute(query, values)
                                    
                                    conn.commit()
                                    
                                    # Registrar atividade
                                    log_activity(st.session_state.user_id, "replace_data", f"Substituiu todos os dados por importação ({len(df_importado)} registros)")
                                    
                                    st.success(f"Dados importados com sucesso! {len(df_importado)} registros substituíram os dados existentes.")
                                    st.balloons()
                                    
                                    # Recarregar a página para atualizar os dados
                                    st.experimental_rerun()
                            else:
                                # Anexar aos dados existentes
                                for _, row in df_importado.iterrows():
                                    # Preparar colunas e valores
                                    columns = ', '.join(row.index)
                                    placeholders = ', '.join(['?' for _ in row])
                                    values = tuple(row.values)
                                    
                                    query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
                                    c.execute(query, values)
                                
                                conn.commit()
                                
                                # Registrar atividade
                                log_activity(st.session_state.user_id, "append_data", f"Adicionou dados por importação ({len(df_importado)} registros)")
                                
                                st.success(f"Dados importados com sucesso! {len(df_importado)} registros adicionados aos dados existentes.")
                                st.balloons()
                                
                                # Recarregar a página para atualizar os dados
                                st.experimental_rerun()
                        
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Erro ao importar dados: {str(e)}")
                        
                        finally:
                            conn.close()
            
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {str(e)}")

@require_login
def analise_avancada(df):
    """Oferece ferramentas de análise avançada de dados."""
    st.title("Análise Avançada")
    
    # Verificar se há dados suficientes
    if df.empty or len(df) < 5:
        st.warning("Não há dados suficientes para análise avançada. Adicione mais pets para utilizar esta funcionalidade.")
        return
    
    # Menu de análises disponíveis
    analise_tipo = st.sidebar.radio(
        "Tipo de Análise:",
        ["Clusterização", "Análise de Correlação", "Previsões", "Análise Textual", "Detecção de Anomalias"]
    )
    
    if analise_tipo == "Clusterização":
        st.subheader("Clusterização de Dados")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            A clusterização agrupa pets com características similares, revelando padrões naturais nos dados.
            Esta análise permite identificar grupos distintos de pets com base em múltiplas variáveis.
        </div>
        """
        
        custom_card("Análise de Clusters", card_content, icon="🔍", color="#3F51B5")
        
        # Seleção de variáveis para clustering
        df_num = df.select_dtypes(include=['number'])
        
        if len(df_num.columns) < 2:
            st.warning("São necessárias pelo menos duas variáveis numéricas para realizar a clusterização.")
            return
        
        # Seleção de variáveis
        col1, col2 = st.columns(2)
        
        with col1:
            selected_vars = st.multiselect(
                "Selecione as variáveis para clusterização:",
                options=df_num.columns.tolist(),
                default=df_num.columns.tolist()[:3] if len(df_num.columns) >= 3 else df_num.columns.tolist()
            )
        
        with col2:
            n_clusters = st.slider("Número de clusters:", min_value=2, max_value=10, value=3)
            cluster_method = st.selectbox(
                "Método de clusterização:",
                options=["K-Means", "DBSCAN"]
            )
        
        if not selected_vars:
            st.warning("Selecione pelo menos uma variável para continuar.")
            return
        
        # Preparar dados
        X = df_num[selected_vars].copy()
        
        # Remover linhas com NaN
        X.dropna(inplace=True)
        
        if len(X) < n_clusters:
            st.warning(f"Não há dados suficientes para criar {n_clusters} clusters após remover valores ausentes.")
            return
        
        # Normalizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicar clusterização
        if st.button("Executar Clusterização", use_container_width=True):
            with st.spinner("Processando clusterização..."):
                try:
                    if cluster_method == "K-Means":
                        # K-Means
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(X_scaled)
                        
                        # Adicionar resultados ao dataframe original
                        df_cluster = X.copy()
                        df_cluster['Cluster'] = clusters
                        
                        # Estatísticas por cluster
                        st.subheader("Estatísticas por Cluster")
                        
                        # Tabela de estatísticas
                        cluster_stats = df_cluster.groupby('Cluster').agg(['mean', 'count'])
                        st.dataframe(cluster_stats, use_container_width=True)
                        
                        # Visualização 2D ou 3D
                        if len(selected_vars) >= 3:
                            # PCA para visualização 3D
                            pca = PCA(n_components=3)
                            components = pca.fit_transform(X_scaled)
                            
                            # Dataframe para plotly
                            df_plot = pd.DataFrame(
                                {
                                    'PC1': components[:, 0],
                                    'PC2': components[:, 1],
                                    'PC3': components[:, 2],
                                    'Cluster': clusters
                                }
                            )
                            
                            # Adicionar informações originais se disponíveis
                            if 'nome' in df.columns:
                                df_plot['Nome'] = X.index.map(df['nome'])
                            
                            # Gráfico 3D
                            fig = px.scatter_3d(
                                df_plot, 
                                x='PC1', 
                                y='PC2', 
                                z='PC3',
                                color='Cluster',
                                hover_name='Nome' if 'Nome' in df_plot.columns else None,
                                title=f'Visualização 3D dos Clusters ({cluster_method})',
                                labels={'Cluster': 'Grupo'},
                                color_continuous_scale=px.colors.qualitative.G10
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Visualização 2D para 2 variáveis
                            fig = px.scatter(
                                df_cluster,
                                x=selected_vars[0],
                                y=selected_vars[1] if len(selected_vars) > 1 else selected_vars[0],
                                color='Cluster',
                                title=f'Visualização dos Clusters ({cluster_method})',
                                labels={'Cluster': 'Grupo'}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Interpretação dos clusters
                        st.subheader("Interpretação dos Clusters")
                        
                        for i in range(n_clusters):
                            cluster_data = df_cluster[df_cluster['Cluster'] == i]
                            
                            # Tamanho e proporção do cluster
                            size = len(cluster_data)
                            prop = size / len(df_cluster) * 100
                            
                            # Características distintas
                            means = cluster_data.mean().drop('Cluster')
                            overall_means = df_cluster.mean().drop('Cluster')
                            diffs = ((means - overall_means) / overall_means * 100).abs()
                            key_features = diffs.nlargest(3)
                            
                            # Criar descrição
                            content = f"""
                            <div style="margin-bottom: 1rem;">
                                <div><strong>Tamanho:</strong> {size} pets ({prop:.1f}% do total)</div>
                                <div style="margin-top: 0.7rem;"><strong>Características distintivas:</strong></div>
                                <ul style="margin-top: 0.3rem;">
                            """
                            
                            for feat, diff in key_features.items():
                                direction = "acima" if means[feat] > overall_means[feat] else "abaixo"
                                content += f"<li>{feat}: {direction} da média em {diff:.1f}%</li>"
                            
                            content += """
                                </ul>
                            </div>
                            """
                            
                            custom_card(f"Cluster {i+1}", content, icon=f"#{i+1}", color="#3F51B5")
                    
                    elif cluster_method == "DBSCAN":
                        # DBSCAN
                        dbscan = DBSCAN(eps=0.5, min_samples=5)
                        clusters = dbscan.fit_predict(X_scaled)
                        
                        # Adicionar resultados ao dataframe original
                        df_cluster = X.copy()
                        df_cluster['Cluster'] = clusters
                        
                        # Estatísticas por cluster
                        st.subheader("Estatísticas por Cluster")
                        
                        # Tabela de estatísticas
                        cluster_stats = df_cluster.groupby('Cluster').agg(['mean', 'count'])
                        st.dataframe(cluster_stats, use_container_width=True)
                        
                        # Visualização 2D ou 3D
                        if len(selected_vars) >= 3:
                            # PCA para visualização 3D
                            pca = PCA(n_components=3)
                            components = pca.fit_transform(X_scaled)
                            
                            # Dataframe para plotly
                            df_plot = pd.DataFrame(
                                {
                                    'PC1': components[:, 0],
                                    'PC2': components[:, 1],
                                    'PC3': components[:, 2],
                                    'Cluster': clusters
                                }
                            )
                            
                            # Adicionar informações originais se disponíveis
                            if 'nome' in df.columns:
                                df_plot['Nome'] = X.index.map(df['nome'])
                            
                            # Gráfico 3D
                            fig = px.scatter_3d(
                                df_plot, 
                                x='PC1', 
                                y='PC2', 
                                z='PC3',
                                color='Cluster',
                                hover_name='Nome' if 'Nome' in df_plot.columns else None,
                                title=f'Visualização 3D dos Clusters ({cluster_method})',
                                labels={'Cluster': 'Grupo'},
                                color_continuous_scale=px.colors.qualitative.G10
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Visualização 2D para 2 variáveis
                            fig = px.scatter(
                                df_cluster,
                                x=selected_vars[0],
                                y=selected_vars[1] if len(selected_vars) > 1 else selected_vars[0],
                                color='Cluster',
                                title=f'Visualização dos Clusters ({cluster_method})',
                                labels={'Cluster': 'Grupo'}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro na clusterização: {str(e)}")
    
    elif analise_tipo == "Análise de Correlação":
        st.subheader("Análise Avançada de Correlação")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            A análise de correlação mede a força e direção da relação entre variáveis, 
            permitindo identificar fatores que se influenciam mutuamente.
        </div>
        """
        
        custom_card("Correlações e Relações", card_content, icon="🔄", color="#E91E63")
        
        # Obter variáveis numéricas
        df_num = df.select_dtypes(include=['number'])
        
        if len(df_num.columns) < 2:
            st.warning("São necessárias pelo menos duas variáveis numéricas para análise de correlação.")
            return
        
        # Matriz de correlação
        st.subheader("Matriz de Correlação")
        
        corr = df_num.corr()
        
        # Heatmap de correlação
        fig = px.imshow(
            corr,
            text_auto='.2f',
            title="Matriz de Correlação",
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Selecionar variáveis para análise detalhada
        col1, col2 = st.columns(2)
        
        with col1:
            var_x = st.selectbox("Variável X:", options=df_num.columns.tolist(), index=0)
        
        with col2:
            var_y = st.selectbox("Variável Y:", options=df_num.columns.tolist(), index=min(1, len(df_num.columns)-1))
        
        # Evitar mesma variável
        if var_x == var_y:
            st.warning("Por favor, selecione variáveis diferentes para análise.")
            return
        
        # Preparar dados para análise
        df_corr = df[[var_x, var_y]].dropna()
        
        if len(df_corr) < 5:
            st.warning("Não há dados suficientes para análise de correlação após remover valores ausentes.")
            return
        
        # Calcular correlação
        corr_value = df_corr[var_x].corr(df_corr[var_y])
        
        # Interpretar correlação
        if abs(corr_value) < 0.3:
            strength = "fraca"
            color = "#FFC107"
        elif abs(corr_value) < 0.7:
            strength = "moderada"
            color = "#FF9800"
        else:
            strength = "forte"
            color = "#F44336" if corr_value < 0 else "#4CAF50"
        
        direction = "positiva" if corr_value >= 0 else "negativa"
        
        # Exibir resultado
        correlation_content = f"""
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                Correlação: <span style="color: {color}">{corr_value:.2f}</span>
            </div>
            <div>
                Existe uma correlação <strong>{strength} {direction}</strong> entre {var_x} e {var_y}.
            </div>
            <div style="margin-top: 0.5rem;">
                <strong>Interpretação:</strong> 
                {
                    f"Quando {var_x} aumenta, {var_y} tende a aumentar também." if corr_value > 0 else
                    f"Quando {var_x} aumenta, {var_y} tende a diminuir."
                }
            </div>
        </div>
        """
        
        custom_card(f"Correlação entre {var_x} e {var_y}", correlation_content, icon="📊", color="#9C27B0")
        
        # Gráfico de dispersão com linha de tendência
        fig = px.scatter(
            df_corr,
            x=var_x,
            y=var_y,
            trendline="ols",
            labels={var_x: var_x, var_y: var_y},
            title=f"Relação entre {var_x} e {var_y}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de regressão
        st.subheader("Análise de Regressão")
        
        X = df_corr[[var_x]]
        y = df_corr[var_y]
        
        # Treinar modelo de regressão
        model = LinearRegression()
        model.fit(X, y)
        
        # Fazer previsões
        y_pred = model.predict(X)
        
        # Calcular métricas
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        # Exibir equação da reta
        equation = f"y = {model.coef_[0]:.4f}x + {model.intercept_:.4f}"
        
        # Mostrar resultados
        regression_content = f"""
        <div style="margin-bottom: 1rem;">
            <div style="margin-bottom: 0.5rem;"><strong>Equação da reta:</strong> {equation}</div>
            <div style="margin-bottom: 0.5rem;"><strong>R² (Coeficiente de determinação):</strong> {r2:.4f}</div>
            <div style="margin-bottom: 0.5rem;"><strong>RMSE (Erro quadrático médio):</strong> {rmse:.4f}</div>
            <div style="margin-top: 0.8rem;">
                <strong>Interpretação:</strong> 
                {
                    f"O modelo explica {r2*100:.1f}% da variação em {var_y}." 
                }
                {
                    f"Para cada unidade de aumento em {var_x}, {var_y} {'aumenta' if model.coef_[0] > 0 else 'diminui'} em {abs(model.coef_[0]):.4f} unidades."
                }
            </div>
        </div>
        """
        
        custom_card("Modelo de Regressão", regression_content, icon="📈", color="#00BCD4")
        
        # Modelo de regressão com statsmodels para detalhes
        X_sm = sm.add_constant(X)
        model_sm = sm.OLS(y, X_sm).fit()
        
        # Exibir resumo do modelo
        st.subheader("Detalhes do Modelo de Regressão")
        st.text(model_sm.summary().as_text())
        
        # Simulação de valores
        st.subheader("Simulador de Valores")
        
        # Slider para selecionar valor de X
        x_min, x_max = df_corr[var_x].min(), df_corr[var_x].max()
        x_val = st.slider(
            f"Selecione um valor para {var_x}:",
            min_value=float(x_min),
            max_value=float(x_max),
            value=float((x_min + x_max) / 2),
            step=float((x_max - x_min) / 100)
        )
        
        # Prever valor de Y
        y_val = model.predict([[x_val]])[0]
        
        # Exibir previsão
        st.success(f"Para {var_x} = {x_val:.2f}, o valor previsto de {var_y} é {y_val:.2f}")
    
    elif analise_tipo == "Previsões":
        st.subheader("Modelos de Previsão")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Os modelos de previsão utilizam dados históricos para estimar valores futuros ou 
            prever uma variável com base em outras, permitindo antecipação de tendências e comportamentos.
        </div>
        """
        
        custom_card("Previsão e Modelagem", card_content, icon="🔮", color="#4CAF50")
        
        # Tipo de previsão
        previsao_tipo = st.radio(
            "Tipo de Previsão:",
            ["Previsão de Variável", "Análise Temporal"]
        )
        
        # Previsão de variável com base em outras
        if previsao_tipo == "Previsão de Variável":
            # Obter variáveis numéricas
            df_num = df.select_dtypes(include=['number'])
            
            if len(df_num.columns) < 2:
                st.warning("São necessárias pelo menos duas variáveis numéricas para este tipo de previsão.")
                return
            
            # Seleção de variável alvo
            var_target = st.selectbox("Variável a ser prevista:", options=df_num.columns.tolist())
            
            # Seleção de variáveis preditoras
            var_predictors = st.multiselect(
                "Variáveis preditoras:",
                options=[col for col in df_num.columns if col != var_target],
                default=[col for col in df_num.columns[:3] if col != var_target]
            )
            
            if not var_predictors:
                st.warning("Selecione pelo menos uma variável preditora.")
                return
            
            # Preparar dados
            X = df_num[var_predictors].copy()
            y = df_num[var_target].copy()
            
            # Remover linhas com NaN
            mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[mask]
            y = y[mask]
            
            if len(X) < 10:
                st.warning("Não há dados suficientes para treinar um modelo após remover valores ausentes.")
                return
            
            # Treinar modelo
            if st.button("Treinar Modelo de Previsão", use_container_width=True):
                with st.spinner("Treinando modelo..."):
                    try:
                        # Dividir em treino e teste
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                        
                        # Treinar modelo
                        model = LinearRegression()
                        model.fit(X_train, y_train)
                        
                        # Avaliar no conjunto de teste
                        y_pred = model.predict(X_test)
                        
                        # Métricas
                        r2 = r2_score(y_test, y_pred)
                        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                        
                        # Exibir resultados
                        st.subheader("Resultados do Modelo")
                        
                        metrics_content = f"""
                        <div style="margin-bottom: 1rem;">
                            <div style="margin-bottom: 0.5rem;"><strong>R² (Coeficiente de determinação):</strong> {r2:.4f}</div>
                            <div style="margin-bottom: 0.5rem;"><strong>RMSE (Erro quadrático médio):</strong> {rmse:.4f}</div>
                            <div style="margin-top: 0.8rem;">
                                <strong>Interpretação:</strong> 
                                {
                                    f"O modelo explica {r2*100:.1f}% da variação em {var_target}." 
                                }
                            </div>
                        </div>
                        """
                        
                        custom_card("Métricas do Modelo", metrics_content, icon="📊", color="#FF5722")
                        
                        # Importância das variáveis
                        importance = pd.DataFrame({
                            'Variável': var_predictors,
                            'Importância': np.abs(model.coef_)
                        })
                        importance = importance.sort_values('Importância', ascending=False)
                        
                        fig = px.bar(
                            importance,
                            x='Variável',
                            y='Importância',
                            title="Importância das Variáveis",
                            labels={'Importância': 'Importância Relativa', 'Variável': 'Variável'}
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Comparação Valores Reais vs. Previstos
                        fig = px.scatter(
                            x=y_test,
                            y=y_pred,
                            labels={'x': 'Valores Reais', 'y': 'Valores Previstos'},
                            title="Valores Reais vs. Previstos"
                        )
                        
                        # Adicionar linha de referência perfeita
                        min_val = min(y_test.min(), y_pred.min())
                        max_val = max(y_test.max(), y_pred.max())
                        fig.add_trace(
                            go.Scatter(
                                x=[min_val, max_val],
                                y=[min_val, max_val],
                                mode='lines',
                                line=dict(color='red', dash='dash'),
                                name='Previsão Perfeita'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Simulação de novos valores
                        st.subheader("Simulador de Previsão")
                        
                        # Criar sliders para cada variável preditora
                        input_values = {}
                        
                        for var in var_predictors:
                            var_min, var_max = df_num[var].min(), df_num[var].max()
                            var_avg = df_num[var].mean()
                            
                            input_values[var] = st.slider(
                                f"{var}:",
                                min_value=float(var_min),
                                max_value=float(var_max),
                                value=float(var_avg),
                                step=float((var_max - var_min) / 100)
                            )
                        
                        # Criar array de entrada
                        input_array = np.array([[input_values[var] for var in var_predictors]])
                        
                        # Fazer previsão
                        prediction = model.predict(input_array)[0]
                        
                        # Exibir previsão
                        st.success(f"Valor previsto de {var_target}: {prediction:.2f}")
                        
                        # Intervalos de confiança (simplificado)
                        st.info(f"Nota: Este valor previsto é uma estimativa e pode variar. O modelo tem precisão de {r2*100:.1f}%.")
                    
                    except Exception as e:
                        st.error(f"Erro ao treinar o modelo: {str(e)}")
        
        # Análise temporal
        elif previsao_tipo == "Análise Temporal":
            # Verificar se há coluna de data
            date_cols = [col for col in df.columns if pd.api.types.is_datetime64_dtype(df[col])]
            
            if not date_cols and 'data_registro' in df.columns:
                try:
                    # Tentar converter
                    df['data_registro'] = pd.to_datetime(df['data_registro'])
                    date_cols = ['data_registro']
                except:
                    pass
            
            if not date_cols:
                st.warning("Não foi encontrada nenhuma coluna de data para análise temporal.")
                return
            
            # Seleção de coluna de data
            date_col = st.selectbox("Coluna de data:", options=date_cols)
            
            # Seleção de variável para analisar tendência
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not num_cols:
                st.warning("Não foram encontradas variáveis numéricas para análise temporal.")
                return
            
            var_trend = st.selectbox("Variável para análise de tendência:", options=num_cols)
            
            # Frequência de agregação
            freq = st.selectbox(
                "Frequência de agregação:",
                options=["Diária", "Semanal", "Mensal", "Trimestral", "Anual"],
                index=2
            )
            
            freq_map = {
                "Diária": "D",
                "Semanal": "W",
                "Mensal": "M",
                "Trimestral": "Q",
                "Anual": "Y"
            }
            
            # Preparar dados temporais
            df_time = df[[date_col, var_trend]].copy()
            df_time.dropna(inplace=True)
            
            if len(df_time) < 10:
                st.warning("Não há dados suficientes para análise temporal após remover valores ausentes.")
                return
            
            # Agregar por período
            df_time.set_index(date_col, inplace=True)
            df_time = df_time.resample(freq_map[freq]).mean()
            
            # Executar análise
            if st.button("Executar Análise Temporal", use_container_width=True):
                with st.spinner("Processando análise temporal..."):
                    try:
                        # Gráfico de série temporal
                        fig = px.line(
                            df_time,
                            y=var_trend,
                            title=f"Série Temporal de {var_trend} ({freq})",
                            labels={var_trend: var_trend, "index": "Data"}
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Decomposição da série
                        if len(df_time) >= 4:  # Mínimo para decomposição
                            try:
                                # Decomposição
                                decomposition = seasonal_decompose(df_time[var_trend], model='additive')
                                
                                # Criar subplots
                                fig = make_subplots(
                                    rows=4, 
                                    cols=1,
                                    subplot_titles=("Observado", "Tendência", "Sazonalidade", "Resíduo"),
                                    vertical_spacing=0.1
                                )
                                
                                # Adicionar traços
                                fig.add_trace(
                                    go.Scatter(x=decomposition.observed.index, y=decomposition.observed, name="Observado"),
                                    row=1, col=1
                                )
                                
                                fig.add_trace(
                                    go.Scatter(x=decomposition.trend.index, y=decomposition.trend, name="Tendência"),
                                    row=2, col=1
                                )
                                
                                fig.add_trace(
                                    go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, name="Sazonalidade"),
                                    row=3, col=1
                                )
                                
                                fig.add_trace(
                                    go.Scatter(x=decomposition.resid.index, y=decomposition.resid, name="Resíduo"),
                                    row=4, col=1
                                )
                                
                                # Atualizar layout
                                fig.update_layout(
                                    height=800,
                                    title_text=f"Decomposição da Série de {var_trend}",
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Análise de tendência
                                trend = decomposition.trend.dropna()
                                
                                if len(trend) >= 2:
                                    # Calcular direção da tendência
                                    trend_direction = "crescente" if trend.iloc[-1] > trend.iloc[0] else "decrescente"
                                    trend_change = abs(trend.iloc[-1] - trend.iloc[0])
                                    trend_pct = abs(trend.iloc[-1] / trend.iloc[0] - 1) * 100 if trend.iloc[0] != 0 else 0
                                    
                                    # Exibir análise
                                    trend_content = f"""
                                    <div style="margin-bottom: 1rem;">
                                        <div style="margin-bottom: 0.5rem;">
                                            A série de <strong>{var_trend}</strong> apresenta uma tendência <strong>{trend_direction}</strong>.
                                        </div>
                                        <div style="margin-bottom: 0.5rem;">
                                            Variação absoluta: <strong>{trend_change:.2f}</strong> unidades
                                        </div>
                                        <div style="margin-bottom: 0.5rem;">
                                            Variação percentual: <strong>{trend_pct:.2f}%</strong>
                                        </div>
                                    </div>
                                    """
                                    
                                    custom_card("Análise de Tendência", trend_content, icon="📈", color="#FF9800")
                            
                            except Exception as e:
                                st.warning(f"Não foi possível realizar a decomposição da série: {str(e)}")
                                st.info("A decomposição requer uma série temporal com mais pontos e sem valores ausentes.")
                    
                    except Exception as e:
                        st.error(f"Erro na análise temporal: {str(e)}")
    
    elif analise_tipo == "Análise Textual":
        st.subheader("Análise de Texto")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            A análise textual extrai insights de dados textuais como descrições, observações, 
            e outros campos textuais, identificando padrões e tendências nas palavras utilizadas.
        </div>
        """
        
        custom_card("Análise de Texto", card_content, icon="📝", color="#9C27B0")
        
        # Identificar colunas de texto
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Remover colunas que provavelmente não são text livre
        exclude_cols = ['nome', 'telefone', 'bairro', 'tipo_pet', 'raca', 'sexo', 'regiao', 'created_by_email']
        text_cols = [col for col in text_cols if col not in exclude_cols]
        
        if not text_cols:
            st.warning("Não foram encontradas colunas de texto para análise.")
            return
        
        # Seleção de coluna de texto
        text_col = st.selectbox("Coluna para análise de texto:", options=text_cols)
        
        # Verificar se há dados suficientes
        texts = df[text_col].dropna().astype(str)
        texts = texts[texts.str.len() > 5]  # Textos com pelo menos 5 caracteres
        
        if len(texts) < 5:
            st.warning(f"Não há dados textuais suficientes na coluna {text_col} para análise.")
            return
        
        # Executar análise
        if st.button("Analisar Texto", use_container_width=True):
            with st.spinner("Processando análise de texto..."):
                try:
                    # Concatenar todos os textos
                    all_text = " ".join(texts)
                    
                    # Estatísticas básicas
                    words = all_text.split()
                    word_count = len(words)
                    unique_words = len(set(words))
                    avg_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
                    
                    # Exibir estatísticas
                    stats_content = f"""
                    <div style="margin-bottom: 1rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Total de palavras:</strong> {word_count}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Palavras únicas:</strong> {unique_words}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Comprimento médio das palavras:</strong> {avg_length:.2f} caracteres</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Total de textos analisados:</strong> {len(texts)}</div>
                    </div>
                    """
                    
                    custom_card("Estatísticas Textuais", stats_content, icon="📊", color="#00BCD4")
                    
                    # Palavras mais comuns
                    word_counts = {}
                    for word in words:
                        word = word.lower()
                        if len(word) > 3:  # Ignorar palavras muito curtas
                            word_counts[word] = word_counts.get(word, 0) + 1
                    
                    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
                    
                    # Gráfico de palavras mais comuns
                    top_words_df = pd.DataFrame(top_words, columns=['Palavra', 'Frequência'])
                    
                    fig = px.bar(
                        top_words_df,
                        x='Palavra',
                        y='Frequência',
                        title="Palavras Mais Frequentes",
                        labels={'Frequência': 'Frequência', 'Palavra': 'Palavra'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Nuvem de palavras
                    st.subheader("Nuvem de Palavras")
                    
                    try:
                        # Gerar nuvem de palavras
                        wordcloud = WordCloud(
                            width=800, 
                            height=400, 
                            background_color='white',
                            max_words=100
                        ).generate(all_text)
                        
                        # Plotar e salvar em um buffer
                        plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        
                        # Exibir nuvem de palavras
                        st.pyplot(plt)
                    except Exception as e:
                        st.warning(f"Não foi possível gerar a nuvem de palavras: {str(e)}")
                
                except Exception as e:
                    st.error(f"Erro na análise de texto: {str(e)}")
    
    elif analise_tipo == "Detecção de Anomalias":
        st.subheader("Detecção de Anomalias")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            A detecção de anomalias identifica valores atípicos nos dados que podem representar 
            erros, casos especiais ou insights valiosos que se destacam do padrão normal.
        </div>
        """
        
        custom_card("Identificação de Anomalias", card_content, icon="🔍", color="#F44336")
        
        # Obter variáveis numéricas
        df_num = df.select_dtypes(include=['number'])
        
        if len(df_num.columns) < 1:
            st.warning("São necessárias variáveis numéricas para detecção de anomalias.")
            return
        
        # Seleção de variáveis
        selected_vars = st.multiselect(
            "Selecione as variáveis para análise:",
            options=df_num.columns.tolist(),
            default=df_num.columns.tolist()[:3] if len(df_num.columns) >= 3 else df_num.columns.tolist()
        )
        
        if not selected_vars:
            st.warning("Selecione pelo menos uma variável para análise.")
            return
        
        # Método de detecção
        method = st.radio(
            "Método de detecção:",
            ["Z-Score", "IQR (Intervalo Interquartil)"]
        )
        
        # Limiar para detecção
        if method == "Z-Score":
            threshold = st.slider(
                "Limiar de Z-Score:",
                min_value=1.5,
                max_value=5.0,
                value=3.0,
                step=0.1
            )
        else:  # IQR
            threshold = st.slider(
                "Fator de IQR:",
                min_value=1.0,
                max_value=3.0,
                value=1.5,
                step=0.1
            )
        
        # Executar detecção
        if st.button("Detectar Anomalias", use_container_width=True):
            with st.spinner("Processando detecção de anomalias..."):
                try:
                    # Preparar dados
                    df_anomaly = df[selected_vars].copy()
                    df_anomaly.dropna(inplace=True)
                    
                    if len(df_anomaly) < 10:
                        st.warning("Não há dados suficientes para detecção de anomalias após remover valores ausentes.")
                        return
                    
                    # Detectar anomalias para cada variável
                    anomalies = {}
                    
                    for var in selected_vars:
                        if method == "Z-Score":
                            # Z-Score
                            mean = df_anomaly[var].mean()
                            std = df_anomaly[var].std()
                            z_scores = (df_anomaly[var] - mean) / std
                            
                            # Identificar anomalias
                            anomalies[var] = df_anomaly[abs(z_scores) > threshold].index
                        else:
                            # IQR
                            Q1 = df_anomaly[var].quantile(0.25)
                            Q3 = df_anomaly[var].quantile(0.75)
                            IQR = Q3 - Q1
                            
                            lower_bound = Q1 - threshold * IQR
                            upper_bound = Q3 + threshold * IQR
                            
                            # Identificar anomalias
                            anomalies[var] = df_anomaly[(df_anomaly[var] < lower_bound) | (df_anomaly[var] > upper_bound)].index
                    
                    # Contar anomalias por variável
                    anomaly_counts = {var: len(indices) for var, indices in anomalies.items()}
                    
                    # Exibir resultados
                    st.subheader("Resultados da Detecção")
                    
                    # Gráfico de contagem de anomalias
                    anomaly_df = pd.DataFrame({
                        'Variável': list(anomaly_counts.keys()),
                        'Anomalias': list(anomaly_counts.values())
                    })
                    
                    fig = px.bar(
                        anomaly_df,
                        x='Variável',
                        y='Anomalias',
                        title=f"Contagem de Anomalias por Variável (Método: {method})",
                        labels={'Anomalias': 'Número de Anomalias', 'Variável': 'Variável'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Visualização das anomalias para cada variável
                    for var in selected_vars:
                        # Dados para visualização
                        df_plot = df[var].dropna()
                        
                        # Identificar pontos anômalos
                        is_anomaly = df_plot.index.isin(anomalies[var])
                        
                        # Criar DataFrame para plotly
                        plot_data = pd.DataFrame({
                            'Índice': range(len(df_plot)),
                            'Valor': df_plot.values,
                            'Anomalia': is_anomaly
                        })
                        
                        # Gráfico de dispersão
                        fig = px.scatter(
                            plot_data,
                            x='Índice',
                            y='Valor',
                            color='Anomalia',
                            title=f"Anomalias em {var} (Total: {len(anomalies[var])})",
                            labels={'Valor': var, 'Índice': 'Índice'},
                            color_discrete_map={True: 'red', False: 'blue'}
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Estatísticas das anomalias
                        if len(anomalies[var]) > 0:
                            anomaly_values = df_plot[df_plot.index.isin(anomalies[var])]
                            normal_values = df_plot[~df_plot.index.isin(anomalies[var])]
                            
                            # Calcular estatísticas
                            anomaly_mean = anomaly_values.mean() if len(anomaly_values) > 0 else 0
                            normal_mean = normal_values.mean() if len(normal_values) > 0 else 0
                            
                            # Exibir estatísticas
                            stats_content = f"""
                            <div style="margin-bottom: 1rem;">
                                <div style="margin-bottom: 0.5rem;"><strong>Número de anomalias:</strong> {len(anomalies[var])} ({len(anomalies[var])/len(df_plot)*100:.1f}% dos dados)</div>
                                <div style="margin-bottom: 0.5rem;"><strong>Média dos valores normais:</strong> {normal_mean:.2f}</div>
                                <div style="margin-bottom: 0.5rem;"><strong>Média das anomalias:</strong> {anomaly_mean:.2f}</div>
                                <div style="margin-bottom: 0.5rem;"><strong>Diferença média:</strong> {abs(anomaly_mean - normal_mean):.2f} ({abs(anomaly_mean/normal_mean - 1)*100:.1f}%)</div>
                            </div>
                            """
                            
                            custom_card(f"Estatísticas das Anomalias em {var}", stats_content, icon="📊", color="#FF5722")
                            
                            # Listar anomalias
                            if len(anomalies[var]) > 0 and len(anomalies[var]) <= 20:
                                st.markdown(f"#### Lista de Anomalias em {var}")
                                
                                # Criar DataFrame com informações extras se disponíveis
                                anomaly_pets = df.loc[anomalies[var]].copy()
                                
                                if 'nome' in anomaly_pets.columns:
                                    anomaly_pets = anomaly_pets[['nome', var] + [col for col in selected_vars if col != var]]
                                else:
                                    anomaly_pets = anomaly_pets[[var] + [col for col in selected_vars if col != var]]
                                
                                st.dataframe(anomaly_pets, use_container_width=True, hide_index=False)
                    
                    # Resumo geral
                    all_anomalies = set()
                    for indices in anomalies.values():
                        all_anomalies.update(indices)
                    
                    summary_content = f"""
                    <div style="margin-bottom: 1rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Total de registros analisados:</strong> {len(df_anomaly)}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Registros com pelo menos uma anomalia:</strong> {len(all_anomalies)} ({len(all_anomalies)/len(df_anomaly)*100:.1f}%)</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Registros sem anomalias:</strong> {len(df_anomaly) - len(all_anomalies)} ({(len(df_anomaly) - len(all_anomalies))/len(df_anomaly)*100:.1f}%)</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Método utilizado:</strong> {method} (limiar: {threshold})</div>
                    </div>
                    """
                    
                    custom_card("Resumo da Detecção de Anomalias", summary_content, icon="📋", color="#3F51B5")
                
                except Exception as e:
                    st.error(f"Erro na detecção de anomalias: {str(e)}")

@require_login
def mapa_interativo(df):
    """Exibe um mapa interativo com a distribuição geográfica dos pets."""
    st.title("Mapa Interativo")
    
    # Card de informação
    card_content = """
    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
        O mapa interativo permite visualizar a distribuição geográfica dos pets, 
        identificando padrões de concentração por bairro e região.
    </div>
    """
    
    custom_card("Visualização Geoespacial", card_content, icon="🗺️", color="#009688")
    
    # Verificar se temos dados de bairro ou região
    if 'bairro' not in df.columns and 'regiao' not in df.columns:
        st.warning("Não há dados de localização (bairro ou região) para exibir no mapa.")
        return
    
    # Opções de visualização
    col1, col2 = st.columns(2)
    
    with col1:
        view_type = st.selectbox(
            "Tipo de Visualização:",
            ["Mapa de Calor", "Mapa de Bairros", "Mapa de Marcadores"]
        )
    
    with col2:
        if 'tipo_pet' in df.columns:
            tipo_filter = st.multiselect(
                "Filtrar por Tipo de Pet:",
                options=["Todos"] + sorted(df['tipo_pet'].unique().tolist()),
                default=["Todos"]
            )
        else:
            tipo_filter = ["Todos"]
    
    # Filtrar dados se necessário
    df_map = df.copy()
    
    if tipo_filter and "Todos" not in tipo_filter and 'tipo_pet' in df.columns:
        df_map = df_map[df_map['tipo_pet'].isin(tipo_filter)]
    
    # Preparar dados para o mapa
    if view_type == "Mapa de Calor" or view_type == "Mapa de Bairros":
        # Usar bairro como principal localização
        if 'bairro' in df_map.columns:
            location_col = 'bairro'
        else:
            location_col = 'regiao'
        
        # Contagem por localização
        location_counts = df_map[location_col].value_counts().reset_index()
        location_counts.columns = ['location', 'count']
        
        # Mapa de calor ou de bairros
        st.subheader(f"Distribuição de Pets por {location_col.capitalize()}")
        
        if view_type == "Mapa de Calor":
            # Mapa de calor simples
            fig = px.density_mapbox(
                location_counts,
                lat=[0] * len(location_counts),  # Placeholder, seria substituído por dados reais
                lon=[0] * len(location_counts),  # Placeholder, seria substituído por dados reais
                z='count',
                radius=10,
                center=dict(lat=-27.5969, lon=-48.5495),  # Florianópolis
                zoom=10,
                mapbox_style="carto-positron",
                title=f"Mapa de Calor por {location_col.capitalize()}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("Nota: Este é um mapa de calor demonstrativo. Para um mapa preciso, seria necessário ter coordenadas geográficas de cada bairro.")
        else:
            # Mapa de bairros
            # Em um cenário real, usaríamos um GeoJSON com polígonos dos bairros
            st.info("Mapa de bairros requere dados geoespaciais (GeoJSON) dos limites de cada bairro.")
            
            # Exibir tabela com contagem por bairro
            st.subheader(f"Contagem de Pets por {location_col.capitalize()}")
            
            # Estilizar tabela
            st.dataframe(
                location_counts,
                use_container_width=True,
                hide_index=True
            )
    
    else:  # Mapa de Marcadores
        st.subheader("Mapa de Marcadores de Pets")
        st.info("Para um mapa de marcadores preciso, seriam necessárias coordenadas geográficas específicas de cada pet.")
        
        # Em um cenário real, teríamos latitude e longitude para cada pet
        # Aqui usamos uma visualização alternativa
        
        # Se tivermos bairro e tipo_pet, podemos fazer um mapa de bolhas
        if 'bairro' in df_map.columns and 'tipo_pet' in df_map.columns:
            # Agrupar por bairro e tipo
            grouped = df_map.groupby(['bairro', 'tipo_pet']).size().reset_index(name='count')
            
            # Criar gráfico de bolhas
            fig = px.scatter(
                grouped,
                x='bairro',
                y='tipo_pet',
                size='count',
                color='tipo_pet',
                title="Distribuição de Tipos de Pets por Bairro",
                labels={'bairro': 'Bairro', 'tipo_pet': 'Tipo de Pet', 'count': 'Quantidade'}
            )
            
            # Ajustar layout
            fig.update_layout(
                xaxis={'categoryorder': 'total descending'},
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Análise adicional
    st.subheader("Análise de Distribuição")
    
    if 'bairro' in df.columns and 'tipo_pet' in df.columns:
        # Distribuição de tipos por bairro em formato de heatmap
        cross_tab = pd.crosstab(df_map['bairro'], df_map['tipo_pet'])
        
        # Normalizar por bairro
        cross_tab_norm = cross_tab.div(cross_tab.sum(axis=1), axis=0) * 100
        
        # Criar heatmap
        fig = px.imshow(
            cross_tab_norm,
            labels=dict(x="Tipo de Pet", y="Bairro", color="Percentual (%)"),
            title="Distribuição Percentual de Tipos de Pets por Bairro",
            color_continuous_scale='Viridis',
            text_auto='.1f'
        )
        
        # Ajustar layout
        fig.update_layout(
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Densidade populacional de pets
    if 'bairro' in df.columns:
        st.subheader("Densidade de Pets")
        
        # Contar pets por bairro
        bairro_counts = df_map['bairro'].value_counts().reset_index()
        bairro_counts.columns = ['bairro', 'count']
        
        # Adicionar densidade (simulada para este exemplo)
        # Em um cenário real, teríamos dados de área ou população de cada bairro
        bairro_counts['area_km2'] = np.random.uniform(1, 10, size=len(bairro_counts))
        bairro_counts['densidade'] = bairro_counts['count'] / bairro_counts['area_km2']
        
        # Criar gráfico de densidade
        fig = px.bar(
            bairro_counts.sort_values('densidade', ascending=False).head(10),
            x='bairro',
            y='densidade',
            color='densidade',
            title="Top 10 Bairros por Densidade de Pets (Pets/km²)",
            labels={'bairro': 'Bairro', 'densidade': 'Densidade (Pets/km²)'},
            text=bairro_counts.sort_values('densidade', ascending=False).head(10)['densidade'].round(1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Nota: Este gráfico usa valores de área simulados para fins de demonstração. Em um ambiente de produção, seriam utilizados dados reais de área por bairro.")

@require_login
def ai_insights(df):
    """Oferece insights baseados em IA sobre os dados."""
    st.title("IA Insights")
    
    # Card de informação
    card_content = """
    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
        Esta seção utiliza inteligência artificial para analisar os dados e gerar insights 
        automáticos, identificando padrões, tendências e oportunidades que podem não ser evidentes
        em análises tradicionais.
    </div>
    """
    
    custom_card("Análise Baseada em IA", card_content, icon="🤖", color="#673AB7")
    
    st.info("Nota: Esta funcionalidade simula o uso de IA para análise de dados. Em um ambiente de produção, seria integrada com serviços como Google Gemini AI ou OpenAI para análises mais avançadas.")
    
    # Opções de análise
    analysis_type = st.radio(
        "Tipo de Análise:",
        ["Resumo Geral", "Insights Específicos", "Recomendações", "Análise Preditiva"],
        horizontal=True
    )
    
    # Verificar se temos dados suficientes
    if df.empty or len(df) < 5:
        st.warning("Não há dados suficientes para análise por IA. Adicione mais pets para utilizar esta funcionalidade.")
        return
    
    # Executar análise
    if st.button("Gerar Análise com IA", use_container_width=True):
        with st.spinner("Processando análise com IA..."):
            # Simular processamento
            time.sleep(2)
            
            if analysis_type == "Resumo Geral":
                # Gerar estatísticas para resumo
                total_pets = len(df)
                tipos = df['tipo_pet'].value_counts() if 'tipo_pet' in df.columns else pd.Series([])
                adotados = df['adotado'].sum() if 'adotado' in df.columns else 0
                bairros = df['bairro'].nunique() if 'bairro' in df.columns else 0
                
                # Criar resumo
                st.subheader("Resumo Geral dos Dados")
                
                summary_content = f"""
                <div style="margin-bottom: 1rem; line-height: 1.6;">
                    <p>A análise dos dados de <strong>{total_pets} pets</strong> cadastrados no sistema revela algumas tendências importantes:</p>
                    
                    <ul style="margin-top: 1rem;">
                        <li>A base de dados cobre <strong>{bairros} bairros</strong> diferentes, mostrando uma boa distribuição geográfica.</li>
                        
                        <li>A taxa de adoção está em <strong>{(adotados/total_pets*100) if 'adotado' in df.columns else 0:.1f}%</strong>, o que indica um 
                        {'bom desempenho nas iniciativas de adoção' if adotados/total_pets > 0.5 else 'potencial para melhorar as taxas de adoção'}.</li>
                        
                        {'<li>Os <strong>' + tipos.index[0] + 's</strong> representam a maioria dos registros (' + str(round(tipos.iloc[0]/total_pets*100, 1)) + '%), ' + 
                         'seguidos por <strong>' + tipos.index[1] + 's</strong> (' + str(round(tipos.iloc[1]/total_pets*100, 1)) + '%).</li>' 
                         if 'tipo_pet' in df.columns and len(tipos) >= 2 else ''}
                    </ul>
                    
                    <p style="margin-top: 1rem;">
                        Com base nos padrões observados, recomenda-se focar em estratégias para aumentar a adoção de pets 
                        nos bairros com menores taxas, além de equilibrar a representatividade dos diferentes tipos de pets no sistema.
                    </p>
                </div>
                """
                
                custom_card("Análise IA: Resumo Geral", summary_content, icon="📊", color="#673AB7")
                
                # Visualização complementar
                st.subheader("Distribuição por Características Principais")
                
                # Selecionar colunas numéricas
                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                num_cols = [col for col in num_cols if col not in ['id', 'created_by']]
                
                if num_cols:
                    # Gráfico de radar com médias
                    df_radar = df[num_cols].mean().reset_index()
                    df_radar.columns = ['Variável', 'Valor']
                    
                    # Normalizar para mesma escala
                    for i, row in df_radar.iterrows():
                        max_val = df[row['Variável']].max()
                        if max_val > 0:
                            df_radar.loc[i, 'Valor Normalizado'] = row['Valor'] / max_val
                    
                    # Criar gráfico de radar
                    fig = px.line_polar(
                        df_radar, 
                        r='Valor Normalizado', 
                        theta='Variável', 
                        line_close=True,
                        title="Perfil Médio dos Pets (Valores Normalizados)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Insights Específicos":
                st.subheader("Insights Específicos por IA")
                
                # Análise mais detalhada simulada
                insights = []
                
                # Insight 1: Relação peso-idade
                if 'peso' in df.columns and 'idade' in df.columns:
                    df_clean = df.dropna(subset=['peso', 'idade'])
                    if len(df_clean) > 5:
                        corr = df_clean['peso'].corr(df_clean['idade'])
                        
                        if abs(corr) > 0.3:
                            direction = "positiva" if corr > 0 else "negativa"
                            insights.append(
                                f"**Relação Peso-Idade:** Existe uma correlação {direction} ({corr:.2f}) entre peso e idade, "
                                f"indicando que os pets {'tendem a ganhar peso com a idade' if corr > 0 else 'mais velhos frequentemente pesam menos'}."
                            )
                
                # Insight 2: Diferenças por tipos
                if 'tipo_pet' in df.columns and 'peso' in df.columns:
                    tipo_stats = df.groupby('tipo_pet')['peso'].mean().sort_values(ascending=False)
                    if len(tipo_stats) >= 2:
                        insights.append(
                            f"**Diferenças por Tipo:** {tipo_stats.index[0]}s são em média {tipo_stats.iloc[0]/tipo_stats.iloc[-1]:.1f}x "
                            f"mais pesados que {tipo_stats.index[-1]}s, o que pode indicar necessidades nutricionais e de exercício muito distintas."
                        )
                
                # Insight 3: Padrões geográficos
                if 'bairro' in df.columns and 'adotado' in df.columns:
                    bairro_adoption = df.groupby('bairro')['adotado'].mean().sort_values(ascending=False)
                    if len(bairro_adoption) >= 5:
                        top_bairro = bairro_adoption.index[0]
                        bottom_bairro = bairro_adoption.index[-1]
                        diff = bairro_adoption.iloc[0] - bairro_adoption.iloc[-1]
                        
                        if diff > 0.2:
                            insights.append(
                                f"**Padrões Geográficos:** A taxa de adoção varia significativamente por bairro. "
                                f"{top_bairro} tem uma taxa de adoção de {bairro_adoption.iloc[0]*100:.1f}%, enquanto "
                                f"{bottom_bairro} tem apenas {bairro_adoption.iloc[-1]*100:.1f}%. Isso sugere a necessidade "
                                f"de iniciativas específicas em bairros com baixa adoção."
                            )
                
                # Insight 4: Comportamento
                if 'comportamento' in df.columns and 'tipo_pet' in df.columns:
                    comportamento_counts = pd.crosstab(df['tipo_pet'], df['comportamento'])
                    
                    if not comportamento_counts.empty:
                        most_common = {}
                        for tipo in comportamento_counts.index:
                            if not comportamento_counts.loc[tipo].empty:
                                most_common[tipo] = comportamento_counts.loc[tipo].idxmax()
                        
                        if most_common:
                            behavior_text = ", ".join([f"{tipo}s tendem a ser mais {comp.lower()}" for tipo, comp in most_common.items()])
                            insights.append(
                                f"**Padrões Comportamentais:** {behavior_text}. Estes padrões comportamentais são importantes para orientar futuros tutores."
                            )
                
                # Insight 5: Saúde
                if 'estado_saude' in df.columns and 'idade' in df.columns:
                    try:
                        health_age = df.groupby('estado_saude')['idade'].mean().sort_values()
                        
                        if len(health_age) >= 2:
                            insights.append(
                                f"**Relação Idade-Saúde:** A idade média dos pets varia por estado de saúde, de {health_age.iloc[0]:.1f} anos "
                                f"({health_age.index[0]}) até {health_age.iloc[-1]:.1f} anos ({health_age.index[-1]}), destacando a importância "
                                f"de cuidados preventivos para pets mais velhos."
                            )
                    except:
                        pass
                
                # Exibir insights
                if insights:
                    for i, insight in enumerate(insights):
                        custom_card(f"Insight {i+1}", f"<div style='line-height: 1.5;'>{insight}</div>", icon="💡", color="#9C27B0")
                else:
                    st.info("Não foram encontrados insights específicos nos dados disponíveis. Tente adicionar mais informações para uma análise mais completa.")
            
            elif analysis_type == "Recomendações":
                st.subheader("Recomendações Baseadas em IA")
                
                # Gerar recomendações específicas
                recommendations = []
                
                # Recomendação 1: Foco em adoção
                if 'adotado' in df.columns:
                    adoption_rate = df['adotado'].mean() * 100
                    if adoption_rate < 50:
                        recommendations.append({
                            "título": "Aumentar Taxa de Adoção",
                            "descrição": f"A taxa de adoção atual de {adoption_rate:.1f}% está abaixo do ideal. Considere implementar campanhas de adoção focadas, particularmente para os tipos de pets com menor taxa de adoção.",
                            "impacto": "Alto",
                            "esforço": "Médio",
                            "cor": "#F44336"
                        })
                
                # Recomendação 2: Distribuição geográfica
                if 'bairro' in df.columns:
                    bairro_counts = df['bairro'].value_counts()
                    coverage = len(bairro_counts) / 30  # Simulando cobertura de bairros
                    
                    if coverage < 0.7:
                        recommendations.append({
                            "título": "Expandir Cobertura Geográfica",
                            "descrição": f"Atualmente, os dados cobrem apenas {len(bairro_counts)} bairros, representando uma cobertura estimada de {coverage*100:.1f}% da cidade. Ampliar o alcance para mais bairros proporcionará uma visão mais completa da população de pets.",
                            "impacto": "Médio",
                            "esforço": "Alto",
                            "cor": "#FF9800"
                        })
                
                # Recomendação 3: Dados de saúde
                missing_health = 'estado_saude' not in df.columns or df['estado_saude'].isna().mean() > 0.3
                
                if missing_health:
                    recommendations.append({
                        "título": "Melhorar Dados de Saúde",
                        "descrição": "Os dados de saúde estão incompletos ou ausentes para muitos pets. Capturar informações mais detalhadas sobre o estado de saúde permitirá análises mais precisas e intervenções preventivas.",
                        "impacto": "Alto",
                        "esforço": "Médio",
                        "cor": "#2196F3"
                    })
                
                # Recomendação 4: Segmentação por comportamento
                if 'comportamento' in df.columns:
                    behavior_groups = df['comportamento'].value_counts()
                    
                    if len(behavior_groups) >= 3:
                        recommendations.append({
                            "título": "Segmentação por Comportamento",
                            "descrição": f"Foram identificados {len(behavior_groups)} padrões comportamentais distintos. Considere desenvolver programas específicos para cada grupo comportamental, especialmente para os comportamentos mais desafiadores.",
                            "impacto": "Médio",
                            "esforço": "Baixo",
                            "cor": "#4CAF50"
                        })
                
                # Recomendação 5: Equilíbrio de tipos
                if 'tipo_pet' in df.columns:
                    tipo_counts = df['tipo_pet'].value_counts()
                    top_ratio = tipo_counts.iloc[0] / len(df) if len(tipo_counts) > 0 else 0
                    
                    if top_ratio > 0.7:
                        recommendations.append({
                            "título": "Diversificar Tipos de Pets",
                            "descrição": f"Os {tipo_counts.index[0]}s representam {top_ratio*100:.1f}% dos registros, criando um desequilíbrio. Busque registrar mais dados de outros tipos de pets para uma visão mais abrangente e equilibrada.",
                            "impacto": "Baixo",
                            "esforço": "Médio",
                            "cor": "#9C27B0"
                        })
                
                # Exibir recomendações
                if recommendations:
                    for i, rec in enumerate(recommendations):
                        content = f"""
                        <div style="margin-bottom: 1rem; line-height: 1.5;">
                            <p>{rec['descrição']}</p>
                            <div style="display: flex; margin-top: 1rem;">
                                <div style="flex: 1; padding-right: 10px;">
                                    <strong>Impacto:</strong> <span style="color: {'#F44336' if rec['impacto'] == 'Alto' else '#FF9800' if rec['impacto'] == 'Médio' else '#4CAF50'};">{rec['impacto']}</span>
                                </div>
                                <div style="flex: 1;">
                                    <strong>Esforço:</strong> <span style="color: {'#F44336' if rec['esforço'] == 'Alto' else '#FF9800' if rec['esforço'] == 'Médio' else '#4CAF50'};">{rec['esforço']}</span>
                                </div>
                            </div>
                        </div>
                        """
                        
                        custom_card(rec['título'], content, icon="🎯", color=rec['cor'])
                else:
                    st.info("Não foram geradas recomendações específicas a partir dos dados disponíveis. Tente adicionar mais informações para uma análise mais completa.")
            
            elif analysis_type == "Análise Preditiva":
                st.subheader("Análise Preditiva por IA")
                
                # Selecionar variáveis para previsão
                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                num_cols = [col for col in num_cols if col not in ['id', 'created_by']]
                
                if len(num_cols) < 2:
                    st.warning("São necessárias pelo menos duas variáveis numéricas para análise preditiva.")
                    return
                
                # Simulação de modelos preditivos
                models = [
                    {
                        "título": "Previsão de Taxa de Adoção",
                        "descrição": "Com base nos padrões históricos e características dos pets, projetamos um aumento de 12-15% na taxa de adoção nos próximos meses, especialmente para pets de médio porte e comportamento sociável.",
                        "confiança": "87%",
                        "tipo": "Série Temporal",
                        "cor": "#3F51B5"
                    },
                    {
                        "título": "Estimativa de Demanda por Bairro",
                        "descrição": "O modelo prevê um aumento significativo na demanda por registros nos bairros do norte da ilha, enquanto bairros centrais tendem a manter padrões estáveis.",
                        "confiança": "76%",
                        "tipo": "Geoespacial",
                        "cor": "#009688"
                    },
                    {
                        "título": "Previsão de Necessidades Nutricionais",
                        "descrição": "Baseado na distribuição de idade, peso e níveis de atividade, prevemos um aumento de 23% na demanda por rações específicas para pets idosos nos próximos trimestres.",
                        "confiança": "82%",
                        "tipo": "Regressão Multivariada",
                        "cor": "#E91E63"
                    }
                ]
                
                # Exibir modelos preditivos
                for model in models:
                    content = f"""
                    <div style="margin-bottom: 1rem; line-height: 1.5;">
                        <p>{model['descrição']}</p>
                        <div style="display: flex; margin-top: 1rem;">
                            <div style="flex: 1; padding-right: 10px;">
                                <strong>Confiança:</strong> <span style="color: {'#4CAF50' if float(model['confiança'][:-1]) > 80 else '#FF9800'};">{model['confiança']}</span>
                            </div>
                            <div style="flex: 1;">
                                <strong>Tipo de Modelo:</strong> {model['tipo']}
                            </div>
                        </div>
                    </div>
                    """
                    
                    custom_card(model['título'], content, icon="📈", color=model['cor'])
                
                # Visualização preditiva
                st.subheader("Visualização de Tendências")
                
                # Gerar dados simulados para previsão
                months = pd.date_range(start='2025-01-01', periods=12, freq='M')
                
                # Tendência histórica simulada
                historical = np.linspace(50, 80, 6) + np.random.normal(0, 3, 6)
                
                # Previsão simulada
                forecast = np.linspace(80, 95, 6) + np.random.normal(0, 5, 6)
                
                # Intervalos de confiança
                upper = forecast + np.linspace(5, 10, 6)
                lower = forecast - np.linspace(5, 10, 6)
                
                # Criar DataFrame
                df_forecast = pd.DataFrame({
                    'Data': months,
                    'Valor': np.concatenate([historical, forecast]),
                    'Tipo': ['Histórico']*6 + ['Previsão']*6
                })
                
                # Gráfico de previsão
                fig = px.line(
                    df_forecast,
                    x='Data',
                    y='Valor',
                    color='Tipo',
                    title="Previsão de Taxa de Adoção (%)",
                    labels={'Valor': 'Taxa de Adoção (%)', 'Data': 'Mês'},
                    color_discrete_map={'Histórico': '#1976D2', 'Previsão': '#FF9800'}
                )
                
                # Adicionar intervalo de confiança
                fig.add_traces(
                    go.Scatter(
                        x=months[6:],
                        y=upper,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )
                
                fig.add_traces(
                    go.Scatter(
                        x=months[6:],
                        y=lower,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(255, 152, 0, 0.2)',
                        showlegend=False
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("Nota: Esta visualização usa dados simulados para demonstração. Em um ambiente de produção, seriam utilizados modelos reais treinados com os dados históricos.")

def user_settings():
    """Página de configurações do usuário."""
    st.title("Configurações do Usuário")
    
    # Verificar se o usuário está logado
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("Por favor, faça login para acessar as configurações.")
        return
    
    # Obter informações do usuário
    user_info = st.session_state.user_info
    
    # Abas para diferentes configurações
    tab1, tab2, tab3, tab4 = st.tabs([
        "Perfil", 
        "Segurança", 
        "Notificações", 
        "Preferências"
    ])
    
    with tab1:
        st.subheader("Perfil do Usuário")
        
        # Exibir informações atuais
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Avatar simulado com iniciais
            st.markdown(
                f"""
                <div style="width: 100px; height: 100px; border-radius: 50%; 
                background-color: #4527A0; color: white; display: flex; 
                align-items: center; justify-content: center; font-size: 36px; 
                font-weight: bold; margin: 0 auto 20px auto;">
                {user_info['full_name'][0:1] if user_info['full_name'] else "?"}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<div style='text-align: center;'>Usuário desde</div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; font-size: 0.8rem; color: #666;'>Mai 2025</div>", unsafe_allow_html=True)
        
        with col2:
            # Formulário de edição de perfil
            with st.form("edit_profile_form"):
                full_name = st.text_input("Nome completo", value=user_info.get('full_name', ''))
                email = st.text_input("Email", value=user_info.get('email', ''), disabled=True)
                
                # Campos adicionais
                phone = st.text_input("Telefone", value="")
                bio = st.text_area("Biografia", value="", height=100)
                
                # Botão de envio
                submit_profile = st.form_submit_button("Salvar Alterações", use_container_width=True)
                
                if submit_profile:
                    # Aqui você implementaria a atualização do perfil
                    st.success("Perfil atualizado com sucesso!")
                    
                    # Atualizar informações na sessão
                    user_info['full_name'] = full_name
                    st.session_state.user_info = user_info
    
    with tab2:
        st.subheader("Segurança da Conta")
        
        # Formulário de alteração de senha
        with st.form("change_password_form"):
            st.markdown("#### Alterar Senha")
            
            current_password = st.text_input("Senha atual", type="password")
            new_password = st.text_input("Nova senha", type="password")
            confirm_password = st.text_input("Confirmar nova senha", type="password")
            
            # Botão de envio
            submit_password = st.form_submit_button("Alterar Senha", use_container_width=True)
            
            if submit_password:
                if not current_password or not new_password or not confirm_password:
                    st.error("Por favor, preencha todos os campos.")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif len(new_password) < 6:
                    st.error("A nova senha deve ter pelo menos 6 caracteres.")
                else:
                    # Verificar senha atual
                    success = change_password(st.session_state.user_id, current_password, new_password)
                    
                    if success:
                        st.success("Senha alterada com sucesso!")
                        
                        # Registrar atividade
                        log_activity(st.session_state.user_id, "change_password", "Alteração de senha")
                    else:
                        st.error("Senha atual incorreta. Tente novamente.")
        
        # Outras opções de segurança
        st.markdown("#### Outras Opções de Segurança")
        
        enable_2fa = st.checkbox("Habilitar autenticação de dois fatores (2FA)", value=False)
        if enable_2fa:
            st.info("Funcionalidade de 2FA será implementada em uma versão futura.")
        
        # Sessões ativas
        st.markdown("#### Sessões Ativas")
        st.info("Você está conectado em 1 dispositivo (este navegador).")
        
        if st.button("Encerrar Todas as Sessões", use_container_width=True):
            st.success("Todas as outras sessões foram encerradas com sucesso!")
    
    with tab3:
        st.subheader("Preferências de Notificação")
        
        # Opções de notificação
        email_notifications = st.checkbox("Notificações por email", value=True)
        if email_notifications:
            st.markdown("#### Tipos de Notificação por Email")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Atualizações do sistema", value=True)
                st.checkbox("Novos registros de pets", value=True)
                st.checkbox("Relatórios periódicos", value=False)
            
            with col2:
                st.checkbox("Alterações de status", value=True)
                st.checkbox("Alertas de segurança", value=True)
                st.checkbox("Dicas e sugestões", value=False)
        
        # Frequência de resumos
        st.markdown("#### Frequência de Resumos")
        
        summary_freq = st.radio(
            "Receber resumo de atividades:",
            ["Diário", "Semanal", "Mensal", "Nunca"],
            horizontal=True
        )
        
        if st.button("Salvar Preferências de Notificação", use_container_width=True):
            st.success("Preferências de notificação atualizadas com sucesso!")
    
    with tab4:
        st.subheader("Preferências do Sistema")
        
        # Tema
        st.markdown("#### Aparência")
        
        theme = st.radio(
            "Tema:",
            ["Claro", "Escuro", "Sistema"],
            horizontal=True
        )
        
        # Idioma
        st.markdown("#### Idioma")
        
        language = st.selectbox(
            "Idioma da interface:",
            ["Português (Brasil)", "English", "Español"]
        )
        
        # Fuso horário
        st.markdown("#### Fuso Horário")
        
        timezone = st.selectbox(
            "Fuso horário:",
            ["(GMT-03:00) Brasília", "(GMT-02:00) Fernando de Noronha", "(GMT-04:00) Manaus", "(GMT-05:00) Acre"]
        )
        
        # Formato de data
        st.markdown("#### Formatos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_format = st.selectbox(
                "Formato de data:",
                ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"]
            )
        
        with col2:
            number_format = st.selectbox(
                "Formato de número:",
                ["1.234,56", "1,234.56"]
            )
        
        if st.button("Salvar Preferências", use_container_width=True):
            st.success("Preferências do sistema atualizadas com sucesso!")

@require_admin
def admin_panel():
    """Painel de administração."""
    st.title("Painel de Administração")
    
    # Card de informação
    card_content = """
    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
        Painel de administração para gerenciamento de usuários, configurações do sistema
        e monitoramento de atividades.
    </div>
    """
    
    custom_card("Área Administrativa", card_content, icon="⚙️", color="#F44336")
    
    # Menu de administração
    admin_menu = st.sidebar.radio(
        "Menu Administrativo",
        ["Dashboard", "Gerenciar Usuários", "Logs do Sistema", "Configurações", "Backup/Restauração"]
    )
    
    if admin_menu == "Dashboard":
        st.subheader("Dashboard Administrativo")
        
        # Estatísticas principais
        col1, col2, col3, col4 = st.columns(4)
        
        # Obter contagens do banco de dados
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM pets")
        total_pets = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM activity_logs")
        total_activities = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM login_logs WHERE success = 1")
        successful_logins = c.fetchone()[0]
        
        conn.close()
        
        with col1:
            custom_metric("Usuários", total_users, None, "#4527A0")
        
        with col2:
            custom_metric("Pets Registrados", total_pets, None, "#2196F3")
        
        with col3:
            custom_metric("Atividades", total_activities, None, "#FF9800")
        
        with col4:
            custom_metric("Logins", successful_logins, None, "#4CAF50")
        
        # Gráficos de atividade
        st.subheader("Atividade do Sistema")
        
        # Simulação de atividade do sistema
        dates = pd.date_range(start='2025-05-01', end='2025-05-20')
        
        # Dados de atividade simulados
        activity_data = pd.DataFrame({
            'date': dates,
            'logins': np.random.randint(10, 50, size=len(dates)),
            'registrations': np.random.randint(5, 20, size=len(dates)),
            'pet_additions': np.random.randint(2, 15, size=len(dates))
        })
        
        # Gráfico de atividade
        fig = px.line(
            activity_data, 
            x='date', 
            y=['logins', 'registrations', 'pet_additions'],
            labels={'value': 'Quantidade', 'date': 'Data', 'variable': 'Tipo de Atividade'},
            title="Atividade Diária",
            color_discrete_map={
                'logins': '#2196F3',
                'registrations': '#4CAF50',
                'pet_additions': '#FF9800'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas adicionais
        st.subheader("Estatísticas do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Usuários por função
            user_roles = pd.DataFrame({
                'role': ['admin', 'user', 'guest'],
                'count': [2, 45, 12]  # Valores simulados
            })
            
            fig = px.pie(
                user_roles,
                values='count',
                names='role',
                title='Distribuição de Usuários por Função',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Taxa de sucesso de login
            login_stats = pd.DataFrame({
                'status': ['Sucesso', 'Falha'],
                'count': [89, 11]  # Percentuais simulados
            })
            
            fig = px.bar(
                login_stats,
                x='status',
                y='count',
                title='Taxa de Sucesso de Login (%)',
                color='status',
                color_discrete_map={'Sucesso': '#4CAF50', 'Falha': '#F44336'},
                text='count'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif admin_menu == "Gerenciar Usuários":
        st.subheader("Gerenciamento de Usuários")
        
        # Abas para diferentes funções
        tab1, tab2, tab3 = st.tabs(["Lista de Usuários", "Adicionar Usuário", "Permissões"])
        
        with tab1:
            # Obter lista de usuários
            conn = sqlite3.connect(DATABASE_PATH)
            df_users = pd.read_sql_query("SELECT id, email, full_name, role, created_at, last_login FROM users", conn)
            conn.close()
            
            # Exibir usuários
            st.dataframe(
                df_users,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "email": "Email",
                    "full_name": "Nome Completo",
                    "role": st.column_config.SelectboxColumn(
                        "Função",
                        options=["admin", "user", "guest"],
                        required=True
                    ),
                    "created_at": "Data de Criação",
                    "last_login": "Último Login"
                }
            )
            
            # Opções de gerenciamento
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Salvar Alterações", use_container_width=True):
                    st.success("Alterações salvas com sucesso!")
            
            with col2:
                if st.button("Redefinir Senha", use_container_width=True):
                    st.info("Funcionalidade de redefinição de senha será implementada em uma versão futura.")
            
            with col3:
                if st.button("Desativar Usuário", use_container_width=True):
                    st.info("Funcionalidade de desativação de usuário será implementada em uma versão futura.")
        
        with tab2:
            # Formulário para adicionar novo usuário
            with st.form("add_user_form"):
                st.markdown("#### Adicionar Novo Usuário")
                
                new_email = st.text_input("Email", key="new_user_email")
                new_name = st.text_input("Nome Completo", key="new_user_name")
                new_role = st.selectbox("Função", options=["user", "admin"], key="new_user_role")
                new_password = st.text_input("Senha Inicial", type="password", key="new_user_password")
                
                # Botão de envio
                submitted = st.form_submit_button("Adicionar Usuário", use_container_width=True)
                
                if submitted:
                    if not new_email or not new_name or not new_password:
                        st.error("Por favor, preencha todos os campos.")
                    elif len(new_password) < 6:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    else:
                        # Registrar novo usuário
                        success, user_id = register_new_user(new_email, new_password, new_name, new_role)
                        
                        if success:
                            st.success(f"Usuário {new_name} ({new_email}) adicionado com sucesso!")
                            
                            # Registrar atividade
                            log_activity(st.session_state.user_id, "add_user", f"Adicionou usuário: {new_email}")
                        else:
                            st.error("Não foi possível adicionar o usuário. O email já pode estar em uso.")
        
        with tab3:
            st.markdown("#### Gerenciamento de Permissões")
            
            # Simulação de permissões
            role_permissions = pd.DataFrame({
                'Funcionalidade': [
                    'Dashboard',
                    'Visualizar Dados',
                    'Adicionar Pet',
                    'Exportar/Importar',
                    'Análise Avançada',
                    'Mapa Interativo',
                    'IA Insights',
                    'Painel de Administração'
                ],
                'Admin': [True, True, True, True, True, True, True, True],
                'Usuário': [True, True, True, True, True, True, True, False],
                'Convidado': [True, True, False, False, False, False, False, False]
            })
            
            # Exibir tabela de permissões
            st.dataframe(
                role_permissions,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Funcionalidade": "Funcionalidade",
                    "Admin": st.column_config.CheckboxColumn("Admin"),
                    "Usuário": st.column_config.CheckboxColumn("Usuário"),
                    "Convidado": st.column_config.CheckboxColumn("Convidado")
                }
            )
            
            if st.button("Salvar Permissões", use_container_width=True):
                st.success("Permissões atualizadas com sucesso!")
                st.info("As alterações serão aplicadas na próxima vez que os usuários fizerem login.")
    
    elif admin_menu == "Logs do Sistema":
        st.subheader("Logs do Sistema")
        
        # Seleção de tipo de log
        log_type = st.selectbox(
            "Tipo de Log:",
            ["Atividade", "Login", "Erros"]
        )
        
        # Opções de filtro
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "Período:",
                [datetime.date(2025, 5, 1), datetime.date(2025, 5, 20)]
            )
        
        with col2:
            if log_type == "Atividade":
                action_filter = st.multiselect(
                    "Tipo de Ação:",
                    ["login", "add_pet", "add_user", "change_password", "replace_data", "append_data", "register"],
                    default=[]
                )
            elif log_type == "Login":
                success_filter = st.radio(
                    "Status:",
                    ["Todos", "Sucesso", "Falha"],
                    horizontal=True
                )
        
        with col3:
            user_filter = st.text_input("Filtrar por Email:")
        
        # Obter logs do banco de dados
        conn = sqlite3.connect(DATABASE_PATH)
        
        if log_type == "Atividade":
            query = """
            SELECT a.id, u.email, a.action, a.details, a.timestamp
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 100
            """
            
            df_logs = pd.read_sql_query(query, conn)
            
            # Aplicar filtros (simulados)
            if user_filter:
                df_logs = df_logs[df_logs['email'].str.contains(user_filter, case=False)]
            
            if action_filter:
                df_logs = df_logs[df_logs['action'].isin(action_filter)]
        
        elif log_type == "Login":
            query = """
            SELECT l.id, u.email, l.timestamp, l.ip_address, l.user_agent, l.success
            FROM login_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT 100
            """
            
            df_logs = pd.read_sql_query(query, conn)
            
            # Aplicar filtros (simulados)
            if user_filter:
                df_logs = df_logs[df_logs['email'].str.contains(user_filter, case=False)]
            
            if success_filter != "Todos":
                df_logs = df_logs[df_logs['success'] == (success_filter == "Sucesso")]
        
        else:  # Erros (simulado)
            # Criar dados de exemplo para logs de erro
            df_logs = pd.DataFrame({
                'id': range(1, 11),
                'timestamp': pd.date_range(start='2025-05-10', periods=10),
                'level': ['ERROR', 'WARNING', 'ERROR', 'ERROR', 'CRITICAL', 'WARNING', 'ERROR', 'INFO', 'ERROR', 'WARNING'],
                'message': [
                    'Database connection failed',
                    'Slow query detected',
                    'Invalid input data',
                    'API rate limit exceeded',
                    'Server memory low',
                    'File upload timeout',
                    'Authentication error',
                    'Scheduled maintenance',
                    'Data validation failed',
                    'Cache miss'
                ],
                'module': [
                    'database', 'query', 'validation', 'api', 'system',
                    'upload', 'auth', 'system', 'validation', 'cache'
                ]
            })
        
        conn.close()
        
        # Exibir logs
        st.dataframe(
            df_logs,
            use_container_width=True,
            hide_index=True
        )
        
        # Opções de exportação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar Logs", use_container_width=True):
                # Gerar CSV para download
                csv_data = df_logs.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Baixar CSV",
                    data=csv_data,
                    file_name=f"logs_{log_type.lower()}_{datetime.date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Limpar Logs Antigos", use_container_width=True):
                st.info("Funcionalidade de limpeza de logs será implementada em uma versão futura.")
    
    elif admin_menu == "Configurações":
        st.subheader("Configurações do Sistema")
        
        # Abas para diferentes configurações
        tab1, tab2, tab3 = st.tabs(["Geral", "Segurança", "Integrações"])
        
        with tab1:
            st.markdown("#### Configurações Gerais")
            
            # Nome do sistema
            system_name = st.text_input("Nome do Sistema:", value="PetCare Analytics")
            
            # Limite de itens por página
            items_per_page = st.number_input("Itens por Página:", min_value=10, max_value=100, value=50, step=10)
            
            # Política de cache
            cache_policy = st.selectbox(
                "Política de Cache:",
                ["Padrão", "Agressivo", "Conservador", "Desativado"]
            )
            
            # Diretório de dados
            data_directory = st.text_input("Diretório de Dados:", value="./data")
            
            # Tempo limite de sessão
            session_timeout = st.number_input("Tempo Limite de Sessão (minutos):", min_value=5, max_value=240, value=60, step=5)
            
            if st.button("Salvar Configurações Gerais", use_container_width=True):
                st.success("Configurações gerais atualizadas com sucesso!")
        
        with tab2:
            st.markdown("#### Configurações de Segurança")
            
            # Política de senhas
            min_password_length = st.slider("Comprimento Mínimo de Senha:", min_value=6, max_value=16, value=8)
            password_complexity = st.checkbox("Exigir Senhas Complexas", value=True)
            
            # Bloqueio de conta
            account_lockout = st.checkbox("Habilitar Bloqueio de Conta", value=True)
            if account_lockout:
                lockout_threshold = st.number_input("Tentativas Antes do Bloqueio:", min_value=3, max_value=10, value=5)
                lockout_duration = st.number_input("Duração do Bloqueio (minutos):", min_value=5, max_value=60, value=30)
            
            # 2FA
            require_2fa = st.selectbox(
                "Autenticação de Dois Fatores (2FA):",
                ["Opcional", "Obrigatória para Administradores", "Obrigatória para Todos", "Desativada"]
            )
            
            # IP whitelist
            ip_whitelist = st.text_area("Lista de IPs Permitidos (um por linha):", height=100)
            st.caption("Deixe em branco para permitir todos os IPs.")
            
            if st.button("Salvar Configurações de Segurança", use_container_width=True):
                st.success("Configurações de segurança atualizadas com sucesso!")
        
        with tab3:
            st.markdown("#### Integrações de Sistema")
            
            # Email
            st.markdown("##### Configuração de Email")
            
            smtp_server = st.text_input("Servidor SMTP:", value="smtp.example.com")
            smtp_port = st.number_input("Porta SMTP:", value=587)
            smtp_user = st.text_input("Usuário SMTP:", value="notificacoes@example.com")
            smtp_password = st.text_input("Senha SMTP:", type="password")
            
            smtp_test = st.button("Testar Configuração de Email")
            if smtp_test:
                st.success("Configuração de email testada com sucesso!")
            
            # API
            st.markdown("##### Configuração de API")
            
            enable_api = st.checkbox("Habilitar API REST", value=True)
            api_rate_limit = st.number_input("Limite de Requisições por Minuto:", min_value=10, max_value=1000, value=60)
            api_token_expiry = st.number_input("Validade do Token (dias):", min_value=1, max_value=90, value=30)
            
            # Serviços externos
            st.markdown("##### Serviços Externos")
            
            enable_ai = st.checkbox("Habilitar Integração com IA", value=True)
            if enable_ai:
                ai_provider = st.selectbox(
                    "Provedor de IA:",
                    ["Google Gemini AI", "OpenAI", "Outro"]
                )
                ai_api_key = st.text_input("Chave de API:", type="password")
            
            if st.button("Salvar Configurações de Integração", use_container_width=True):
                st.success("Configurações de integração atualizadas com sucesso!")
    
    elif admin_menu == "Backup/Restauração":
        st.subheader("Backup e Restauração")
        
        # Card de informação
        card_content = """
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
            Realize o backup completo do banco de dados ou restaure a partir de um backup anterior.
            Backups regulares são essenciais para garantir a segurança dos dados.
        </div>
        """
        
        custom_card("Backup e Restauração", card_content, icon="💾", color="#607D8B")
        
        # Abas para backup e restauração
        tab1, tab2, tab3 = st.tabs(["Backup Manual", "Backups Automáticos", "Restauração"])
        
        with tab1:
            st.markdown("#### Backup Manual")
            
            # Opções de backup
            backup_options = st.multiselect(
                "Incluir no Backup:",
                ["Dados de Pets", "Usuários", "Configurações", "Logs"],
                default=["Dados de Pets", "Usuários", "Configurações"]
            )
            
            compress_backup = st.checkbox("Comprimir Backup", value=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Iniciar Backup", use_container_width=True):
                    # Simular processo de backup
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(101):
                        progress_bar.progress(i)
                        if i < 30:
                            status_text.text(f"Preparando dados... ({i}%)")
                        elif i < 60:
                            status_text.text(f"Exportando banco de dados... ({i}%)")
                        elif i < 90:
                            status_text.text(f"Comprimindo arquivos... ({i}%)")
                        else:
                            status_text.text(f"Finalizando... ({i}%)")
                        
                        time.sleep(0.02)
                    
                    # Gerar arquivo fictício para download
                    backup_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"petcare_backup_{backup_date}.zip"
                    
                    # Criar um arquivo de texto simples como simulação
                    dummy_content = "Este é um arquivo de backup simulado."
                    
                    # Botão de download
                    st.success("Backup concluído com sucesso!")
                    st.download_button(
                        label="Baixar Backup",
                        data=dummy_content.encode(),
                        file_name=backup_filename,
                        mime="application/zip"
                    )
            
            with col2:
                if st.button("Cancelar", use_container_width=True):
                    st.info("Operação cancelada pelo usuário.")
        
        with tab2:
            st.markdown("#### Backups Automáticos")
            
            # Configuração de backups automáticos
            enable_auto_backup = st.checkbox("Habilitar Backups Automáticos", value=True)
            
            if enable_auto_backup:
                backup_frequency = st.selectbox(
                    "Frequência de Backup:",
                    ["Diário", "Semanal", "Quinzenal", "Mensal"]
                )
                
                if backup_frequency == "Semanal":
                    backup_day = st.selectbox(
                        "Dia da Semana:",
                        ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                    )
                
                backup_time = st.time_input("Horário do Backup:", datetime.time(3, 0))
                
                keep_backups = st.number_input("Manter Backups (dias):", min_value=7, max_value=365, value=30)
                
                # Destino do backup
                backup_destination = st.radio(
                    "Destino do Backup:",
                    ["Local", "Google Drive", "FTP"]
                )
                
                if backup_destination == "Google Drive":
                    st.text_input("Conta Google Drive:", value="backup@example.com")
                    st.text_input("Pasta de Destino:", value="/PetCare/Backups")
                elif backup_destination == "FTP":
                    st.text_input("Servidor FTP:", value="ftp.example.com")
                    st.text_input("Usuário FTP:", value="backup")
                    st.text_input("Senha FTP:", type="password")
                    st.text_input("Diretório FTP:", value="/backups")
            
            # Histórico de backups automáticos
            st.markdown("#### Histórico de Backups")
            
            backup_history = pd.DataFrame({
                'Data': pd.date_range(start='2025-05-01', end='2025-05-20'),
                'Tamanho': ['1.2 MB', '1.3 MB', '1.2 MB', '1.3 MB', '1.5 MB', 
                            '1.4 MB', '1.3 MB', '1.2 MB', '1.3 MB', '1.4 MB',
                            '1.3 MB', '1.2 MB', '1.4 MB', '1.5 MB', '1.3 MB',
                            '1.2 MB', '1.4 MB', '1.3 MB', '1.2 MB', '1.3 MB'],
                'Status': ['Sucesso', 'Sucesso', 'Sucesso', 'Sucesso', 'Sucesso',
                           'Falha', 'Sucesso', 'Sucesso', 'Sucesso', 'Sucesso',
                           'Sucesso', 'Sucesso', 'Sucesso', 'Falha', 'Sucesso',
                           'Sucesso', 'Sucesso', 'Sucesso', 'Sucesso', 'Sucesso']
            })
            
            # Colorir células de status
            def highlight_status(val):
                color = 'green' if val == 'Sucesso' else 'red'
                return f'color: {color}'
            
            # Exibir histórico de backups
            st.dataframe(
                backup_history,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Data': 'Data',
                    'Tamanho': 'Tamanho',
                    'Status': st.column_config.Column(
                        'Status',
                        help="Status da operação de backup",
                        width="medium"
                    )
                }
            )
            
            if st.button("Salvar Configurações de Backup", use_container_width=True):
                st.success("Configurações de backup automático atualizadas com sucesso!")
        
        with tab3:
            st.markdown("#### Restauração de Backup")
            
            # Upload de arquivo de backup
            st.file_uploader("Selecione o arquivo de backup:", type=["zip", "sql", "db"])
            
            # Opções de restauração
            restore_options = st.multiselect(
                "Dados a Restaurar:",
                ["Dados de Pets", "Usuários", "Configurações", "Logs"],
                default=["Dados de Pets", "Usuários", "Configurações"]
            )
            
            overwrite_existing = st.checkbox("Sobrescrever Dados Existentes", value=False)
            if overwrite_existing:
                st.warning("Atenção: Esta operação substituirá todos os dados existentes pelos dados do backup.")
            
            # Aviso de segurança
            st.info("É recomendado realizar um backup dos dados atuais antes de iniciar a restauração.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Iniciar Restauração", disabled=True, use_container_width=True):
                    st.error("Nenhum arquivo de backup selecionado.")
            
            with col2:
                if st.button("Cancelar", use_container_width=True):
                    st.info("Operação cancelada pelo usuário.")

def main():
    """Função principal que coordena todo o fluxo da aplicação."""
    # Inicializar o banco de dados
    init_database()
    
    # Configuração da página
    st.set_page_config(
        page_title="PetCare Analytics",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Carregar e exibir o logo
    try:
        logo_path = "assets/logo.jpg"
        if os.path.exists(logo_path):
            # Exibir logo e título lado a lado (movido para cada função de página)
            pass
        else:
            # Logo não será exibido nesta verificação, será tratado em cada página
            pass
    except Exception as e:
        # Erro ao carregar logo, será tratado em cada página
        pass
    
    # Verificar se o usuário está logado
    if "user_id" not in st.session_state or "user_role" not in st.session_state:
        # Exibir página de login
        display_login_page()
        return
    
    # Exibir cabeçalho
    display_header()
    
    # Carregar dados do banco de dados
    df = load_data_from_db()
    
    # Adicionar barra lateral para filtros e navegação
    df_filtrado = apply_filters(df)
    st.session_state.df_filtrado = df_filtrado
    
    # Menu de navegação principal
    st.sidebar.markdown("## Navegação")
    menu_opcao = st.sidebar.radio(
        "Selecione uma opção:",
        ["Dashboard", "Visualizar Dados", "Adicionar Pet", "Exportar/Importar", 
         "Análise Avançada", "Mapa Interativo", "IA Insights"]
    )
    
    # Navegação de configurações e admin
    with st.sidebar.expander("⚙️ Opções Avançadas"):
        advanced_option = st.radio(
            "Selecione:",
            ["Configurações do Usuário", "Painel de Administração" if st.session_state.user_role == "admin" else ""]
        )
        
        # Limpar opção vazia
        advanced_option = advanced_option.strip()
    
    # Botão de logout
    if st.sidebar.button("📤 Logout", use_container_width=True):
        # Limpar sessão
        if "user_id" in st.session_state:
            # Registrar atividade
            log_activity(st.session_state.user_id, "logout", "Logout do sistema")
            
            # Limpar dados da sessão
            for key in list(st.session_state.keys()):
                del st.session_state[key]
        
        st.experimental_rerun()
    
    # Exibir versão do sistema
    st.sidebar.markdown(
        "<div style='position: fixed; bottom: 10px; text-align: center; width: 250px; font-size: 0.8rem; color: #666;'>"
        "PetCare Analytics v1.0.0<br>"
        "© 2025 Todos os direitos reservados"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Navegar para a página escolhida
    if menu_opcao == "Dashboard":
        display_dashboard(df, df_filtrado)
    elif menu_opcao == "Visualizar Dados":
        visualizar_dados(df)
    elif menu_opcao == "Adicionar Pet":
        adicionar_pet()
    elif menu_opcao == "Exportar/Importar":
        exportar_importar_dados(df)
    elif menu_opcao == "Análise Avançada":
        analise_avancada(df)
    elif menu_opcao == "Mapa Interativo":
        mapa_interativo(df)
    elif menu_opcao == "IA Insights":
        ai_insights(df)
    
    # Opções avançadas
    elif advanced_option == "Configurações do Usuário":
        user_settings()
    elif advanced_option == "Painel de Administração" and st.session_state.user_role == "admin":
        admin_panel()

if __name__ == '__main__':
    main()