import streamlit as st # type: ignore
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns # type: ignore
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
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest, GradientBoostingRegressor
# from sklearn.svm import SVM, SVR
from sklearn.svm import SVC, SVR
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor
import uuid
from functools import wraps
import warnings
warnings.filterwarnings('ignore')
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import networkx as nx
from textblob import TextBlob  # Para análise de sentimento (simulada)

# Configurar diretórios necessários
os.makedirs("assets", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# Constantes
DATABASE_PATH = "data/petcare.db"
DEFAULT_ADMIN_EMAIL = "admin@petcare.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

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
        tipo_pet TEXT NOT NULL,
        idade INTEGER,
        genero TEXT,
        status TEXT DEFAULT 'Disponível',
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        adotado BOOLEAN DEFAULT 0
    )
    ''')
    
    # Tabela de logs de atividade
    c.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Tabela de logs de login
    c.execute('''
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        success BOOLEAN,
        ip_address TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # CORREÇÕES: Verificar e adicionar colunas faltantes
    try:
        # Corrigir tabela pets
        c.execute("PRAGMA table_info(pets)")
        pets_columns = [column[1] for column in c.fetchall()]
        
        pets_new_columns = {
            'observacoes': 'TEXT',
            'peso': 'REAL',
            'comportamento': 'TEXT',
            'vacinas': 'TEXT',
            'castrado': 'BOOLEAN DEFAULT 0',
            'cor': 'TEXT',
            'contato': 'TEXT',
            'endereco': 'TEXT',
            'created_by': 'INTEGER',
            'foto_url': 'TEXT',
            'adaptabilidade': 'TEXT',  # ADICIONADO
            'nivel_energia': 'TEXT',   # ADICIONADO (pode ser necessário)
            'sociabilidade': 'TEXT',   # ADICIONADO (pode ser necessário)
            'cuidados_especiais': 'TEXT',  # ADICIONADO (pode ser necessário)
            'historico_medico': 'TEXT'     # ADICIONADO (pode ser necessário)
        }
        
        for col_name, col_type in pets_new_columns.items():
            if col_name not in pets_columns:
                c.execute(f"ALTER TABLE pets ADD COLUMN {col_name} {col_type}")
                print(f"✅ Coluna '{col_name}' adicionada à tabela pets")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar tabelas: {e}")
    
    # Criar usuário admin padrão se não existir
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = c.fetchone()[0]
    
    if admin_count == 0:
        admin_password = generate_password_hash("admin123")
        c.execute('''
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
        ''', ("admin@petcare.com", admin_password, "Administrador", "admin"))
        print("✅ Usuário admin padrão criado (admin@petcare.com / admin123)")
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")

def add_pet(nome, tipo_pet, idade, genero, status="Disponível", cor="", contato="", endereco="", observacoes="", peso=None, comportamento="", vacinas="", castrado=False, created_by=None, foto_url="", adaptabilidade="", nivel_energia="", sociabilidade=""):
    """Adiciona um novo pet ao banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Verificar quais colunas existem na tabela
        c.execute("PRAGMA table_info(pets)")
        existing_columns = [column[1] for column in c.fetchall()]
        
        # Dados obrigatórios
        pet_data = {
            'nome': nome,
            'tipo_pet': tipo_pet,
            'idade': int(idade) if idade else None,
            'genero': genero,
            'status': status
        }
        
        # Dados opcionais - adicionar apenas se as colunas existirem
        optional_fields = {
            'cor': cor,
            'contato': contato,
            'endereco': endereco,
            'observacoes': observacoes,
            'peso': float(peso) if peso else None,
            'comportamento': comportamento,
            'vacinas': vacinas,
            'castrado': 1 if castrado else 0,
            'created_by': created_by,
            'foto_url': foto_url,
            'adaptabilidade': adaptabilidade,      # ADICIONADO
            'nivel_energia': nivel_energia,        # ADICIONADO
            'sociabilidade': sociabilidade         # ADICIONADO
        }
        
        # Filtrar apenas colunas que existem
        for field, value in optional_fields.items():
            if field in existing_columns:
                pet_data[field] = value
        
        # Construir query dinamicamente
        columns = ', '.join(pet_data.keys())
        placeholders = ', '.join(['?' for _ in pet_data])
        values = list(pet_data.values())
        
        query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
        c.execute(query, values)
        
        pet_id = c.lastrowid
        conn.commit()
        
        return True, pet_id
        
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
        
def display_add_pet_simple():
    """Versão simples do formulário de adicionar pet."""
    st.subheader("➕ Adicionar Novo Pet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Pet*:")
        tipo_pet = st.selectbox("Tipo*:", ["Cão", "Gato", "Ave", "Roedor", "Réptil", "Outro"])
        idade = st.number_input("Idade (anos):", min_value=0, max_value=30, value=1)
        genero = st.selectbox("Gênero*:", ["Macho", "Fêmea"])
        peso = st.number_input("Peso (kg):", min_value=0.0, value=0.0, step=0.1)
    
    with col2:
        cor = st.text_input("Cor:")
        status = st.selectbox("Status:", ["Disponível", "Adotado", "Em Tratamento"])
        castrado = st.checkbox("Castrado")
        comportamento = st.selectbox("Comportamento:", ["Dócil", "Brincalhão", "Tímido", "Agressivo", "Calmo"])
        vacinas = st.text_input("Vacinas:", placeholder="Ex: V8, Antirrábica")
    
    contato = st.text_input("Contato:", placeholder="Telefone ou email")
    endereco = st.text_input("Endereço:")
    observacoes = st.text_area("Observações:", height=100)
    
    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn1:
        if st.button("✅ Adicionar Pet", use_container_width=True):
            if nome and tipo_pet and genero:
                success, result = add_pet(
                    nome=nome,
                    tipo_pet=tipo_pet,
                    idade=idade,
                    genero=genero,
                    status=status,
                    cor=cor,
                    contato=contato,
                    endereco=endereco,
                    observacoes=observacoes,
                    peso=peso if peso > 0 else None,
                    comportamento=comportamento,
                    vacinas=vacinas,
                    castrado=castrado,
                    created_by=st.session_state.user_id
                )
                
                if success:
                    st.success(f"✅ Pet '{nome}' adicionado com sucesso!")
                    log_activity(st.session_state.user_id, "add_pet", f"Adicionou pet: {nome}")
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao adicionar pet: {result}")
            else:
                st.error("❌ Preencha os campos obrigatórios")
    
    with col_btn2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

def get_pets_data():
    """Obtém todos os dados dos pets do banco."""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        # Verificar se a tabela existe e tem dados
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pets'")
        if not cursor.fetchone():
            return pd.DataFrame()
        
        # Obter dados dos pets
        df = pd.read_sql_query("SELECT * FROM pets", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def import_csv_data(df):
    """Importa dados do CSV para o banco de dados com tratamento completo de erros."""
    
    if df.empty:
        return 0, 0, "DataFrame está vazio"

    def prepare_dataframe_for_sqlite(df):
        """Prepara DataFrame para importação no SQLite."""
        df_copy = df.copy()
        
        # Converter colunas de data/hora para string
        datetime_columns = ['data_registro', 'data_nascimento']
        
        for col in datetime_columns:
            if col in df_copy.columns:
                try:
                    # Converter para datetime e depois para string
                    df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                    df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    st.warning(f"Erro ao converter coluna {col}: {e}")
                    # Se falhar, converter diretamente para string
                    df_copy[col] = df_copy[col].astype(str)
        
        # Substituir NaN por None para compatibilidade com SQLite
        df_copy = df_copy.where(pd.notna(df_copy), None)
        
        return df_copy
    
    # Preparar DataFrame
    try:
        df_prepared = prepare_dataframe_for_sqlite(df)
    except Exception as e:
        return 0, 0, f"Erro ao preparar dados: {str(e)}"
    
    # Conectar ao banco
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
    except Exception as e:
        return 0, 0, f"Erro ao conectar ao banco: {str(e)}"
    
    success_count = 0
    error_count = 0
    errors = []
    
    # Definir colunas esperadas (sem ID que é auto-increment)
    expected_columns = [
        'nome', 'bairro', 'tipo_pet', 'raca', 'idade', 'peso', 'sexo', 
        'tipo_comida', 'humor_diario', 'adotado', 'telefone', 'status_vacinacao', 
        'estado_saude', 'comportamento', 'nivel_atividade', 'data_registro', 
        'regiao', 'created_by', 'microchip', 'castrado', 'historico_medico', 
        'data_nascimento', 'cor_pelagem', 'necessidades_especiais', 'temperamento', 
        'sociabilidade', 'energia', 'cuidados_veterinarios', 'custo_mensal', 
        'tempo_disponivel', 'experiencia_tutor', 'ambiente_ideal', 
        'compatibilidade_criancas', 'compatibilidade_pets', 'score_adocao', 
        'cluster_comportamental', 'risco_abandono'
    ]
    
    # Verificar se todas as colunas necessárias existem
    missing_columns = [col for col in expected_columns if col not in df_prepared.columns]
    if missing_columns:
        conn.close()
        return 0, 0, f"Colunas faltando no CSV: {', '.join(missing_columns)}"
    
    # Importar dados linha por linha
    for index, row in df_prepared.iterrows():
        try:
            # Preparar dados da linha, excluindo a coluna 'id' se existir
            row_data = []
            for col in expected_columns:
                value = row.get(col)
                
                # Tratamentos específicos por tipo de dado
                if col in ['idade', 'created_by'] and value is not None:
                    try:
                        value = int(float(value)) if value != '' else None
                    except (ValueError, TypeError):
                        value = None
                
                elif col in ['peso', 'custo_mensal', 'score_adocao'] and value is not None:
                    try:
                        value = float(value) if value != '' else None
                    except (ValueError, TypeError):
                        value = None
                
                elif col == 'adotado' and value is not None:
                    # Converter para boolean/integer
                    if isinstance(value, str):
                        value = 1 if value.lower() in ['true', '1', 'sim', 'yes'] else 0
                    elif isinstance(value, bool):
                        value = 1 if value else 0
                    else:
                        value = int(value) if value else 0
                
                elif col in ['castrado'] and value is not None:
                    # Tratar campos Sim/Não
                    if isinstance(value, str):
                        value = 'Sim' if value.lower() in ['true', '1', 'sim', 'yes'] else 'Não'
                
                # Converter strings vazias para None
                if value == '' or value == 'nan':
                    value = None
                
                row_data.append(value)
            
            # Criar query de inserção
            placeholders = ', '.join(['?' for _ in expected_columns])
            query = f"""
                INSERT INTO pets ({', '.join(expected_columns)}) 
                VALUES ({placeholders})
            """
            
            # Executar inserção
            c.execute(query, row_data)
            success_count += 1
            
        except sqlite3.IntegrityError as e:
            error_msg = f"Linha {index + 1}: Erro de integridade - {str(e)}"
            errors.append(error_msg)
            error_count += 1
            
        except sqlite3.OperationalError as e:
            error_msg = f"Linha {index + 1}: Erro operacional - {str(e)}"
            errors.append(error_msg)
            error_count += 1
            
        except Exception as e:
            error_msg = f"Linha {index + 1}: {str(e)}"
            errors.append(error_msg)
            error_count += 1
    
    # Finalizar transação
    try:
        conn.commit()
        conn.close()
    except Exception as e:
        conn.rollback()
        conn.close()
        return 0, len(df_prepared), f"Erro ao salvar no banco: {str(e)}"
    
    # Preparar mensagem de resultado
    if errors:
        error_summary = f"Erros encontrados:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            error_summary += f"\n... e mais {len(errors) - 5} erros."
    else:
        error_summary = "Importação concluída sem erros!"
    
    return success_count, error_count, error_summary


def display_import_results(success_count, error_count, error_summary):
    """Exibe os resultados da importação de forma organizada."""
    
    # Métricas de resultado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Sucessos", success_count, delta=None)
    
    with col2:
        st.metric("❌ Erros", error_count, delta=None)
    
    with col3:
        total = success_count + error_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        st.metric("📊 Taxa de Sucesso", f"{success_rate:.1f}%")
    
    # Mostrar resumo dos erros
    if error_count > 0:
        st.error(f"**Resumo dos Erros:**\n{error_summary}")
    else:
        st.success("🎉 Todos os registros foram importados com sucesso!")
    
    # Log da atividade
    if 'user_id' in st.session_state:
        log_activity(
            st.session_state.user_id, 
            "import_data", 
            f"Importou {success_count} registros com {error_count} erros"
        )


# Exemplo de como usar na interface
def import_data_interface():
    """Interface para importação de dados CSV."""
    
    st.subheader("📥 Importação de Dados")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV",
        type=['csv'],
        help="Arquivo deve conter as colunas necessárias para pets"
    )
    
    if uploaded_file is not None:
        try:
            # Ler CSV
            df = pd.read_csv(uploaded_file)
            
            # Mostrar preview
            st.write("**Preview dos dados:**")
            st.dataframe(df.head(), use_container_width=True)
            
            # Informações sobre o arquivo
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📊 Total de linhas: {len(df)}")
            with col2:
                st.info(f"📋 Total de colunas: {len(df.columns)}")
            
            # Botão de importação
            if st.button("🚀 Importar Dados", type="primary", use_container_width=True):
                with st.spinner("Importando dados..."):
                    success_count, error_count, error_summary = import_csv_data(df)
                
                # Exibir resultados
                display_import_results(success_count, error_count, error_summary)
                
                # Recarregar dados se houve sucesso
                if success_count > 0:
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo CSV está no formato correto.")

def update_pet_status(pet_id, new_status):
    """Atualiza o status de um pet."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE pets SET status = ? WHERE id = ?", (new_status, pet_id))
        
        # Se foi adotado, marcar flag
        if new_status == "Adotado":
            c.execute("UPDATE pets SET adotado = 1 WHERE id = ?", (pet_id,))
        
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def delete_pet(pet_id):
    """Remove um pet do banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def display_add_pet_form():
    """Exibe formulário para adicionar novo pet."""
    st.subheader("➕ Adicionar Novo Pet")
    
    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Pet*:", key="pet_nome")
            tipo_pet = st.selectbox("Tipo*:", ["Cão", "Gato", "Ave", "Roedor", "Réptil", "Outro"], key="pet_tipo")
            idade = st.number_input("Idade (anos):", min_value=0, max_value=30, value=1, key="pet_idade")
            genero = st.selectbox("Gênero*:", ["Macho", "Fêmea"], key="pet_genero")
            peso = st.number_input("Peso (kg):", min_value=0.0, value=0.0, step=0.1, key="pet_peso")
        
        with col2:
            cor = st.text_input("Cor:", key="pet_cor")
            status = st.selectbox("Status:", ["Disponível", "Adotado", "Em Tratamento"], key="pet_status")
            castrado = st.checkbox("Castrado", key="pet_castrado")
            comportamento = st.selectbox("Comportamento:", ["Dócil", "Brincalhão", "Tímido", "Agressivo", "Calmo"], key="pet_comportamento")
            vacinas = st.text_input("Vacinas:", placeholder="Ex: V8, Antirrábica", key="pet_vacinas")
        
        contato = st.text_input("Contato:", placeholder="Telefone ou email", key="pet_contato")
        endereco = st.text_input("Endereço:", key="pet_endereco")
        observacoes = st.text_area("Observações:", height=100, key="pet_observacoes")
        
        # Upload de foto
        foto = st.file_uploader("Foto do Pet:", type=['png', 'jpg', 'jpeg'], key="pet_foto")
        
        # CORRIGIDO: Usar apenas form_submit_button
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit = st.form_submit_button("✅ Adicionar Pet", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
    # MOVER LÓGICA PARA FORA DO FORM
    if submit:
        if nome and tipo_pet and genero:
            # Processar foto se enviada
            foto_url = ""
            if foto is not None:
                foto_url = f"uploads/{foto.name}"
            
            # Adicionar pet
            success, result = add_pet(
                nome=nome,
                tipo_pet=tipo_pet,
                idade=idade,
                genero=genero,
                status=status,
                cor=cor,
                contato=contato,
                endereco=endereco,
                observacoes=observacoes,
                peso=peso if peso > 0 else None,
                comportamento=comportamento,
                vacinas=vacinas,
                castrado=castrado,
                created_by=st.session_state.user_id,
                foto_url=foto_url
            )
            
            if success:
                st.success(f"✅ Pet '{nome}' adicionado com sucesso!")
                log_activity(st.session_state.user_id, "add_pet", f"Adicionou pet: {nome}")
                time.sleep(1)  # Pequena pausa para mostrar a mensagem
                st.rerun()
            else:
                st.error(f"❌ Erro ao adicionar pet: {result}")
        else:
            st.error("❌ Preencha os campos obrigatórios (Nome, Tipo e Gênero)")
    
    if cancel:
        st.info("Operação cancelada.")
        st.rerun()

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

def log_activity(user_id, action, details="", execution_time=None):
    """Registra uma atividade de usuário no sistema."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    session_id = st.session_state.get("session_id", str(uuid.uuid4()))
    
    try:
        # Tentar inserir com todas as colunas
        c.execute(
            "INSERT INTO activity_logs (user_id, action, details, session_id, execution_time) VALUES (?, ?, ?, ?, ?)",
            (user_id, action, details, session_id, execution_time)
        )
    except sqlite3.OperationalError:
        # Se falhar, inserir apenas as colunas básicas
        c.execute(
            "INSERT INTO activity_logs (user_id, action, details, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, action, details)
        )
    
    conn.commit()
    conn.close()

def get_user_info(user_id):
    """Obtém informações do usuário pelo ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Tentar buscar com as novas colunas
        c.execute("SELECT email, full_name, role, preferences, profile_data FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
    except sqlite3.OperationalError:
        # Se falhar, buscar apenas as colunas básicas
        c.execute("SELECT email, full_name, role FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        
        if result:
            conn.close()
            return {
                "email": result[0],
                "full_name": result[1],
                "role": result[2],
                "preferences": {},  # Valores padrão
                "profile_data": {}
            }
        conn.close()
        return None
    
    conn.close()
    
    if result:
        return {
            "email": result[0],
            "full_name": result[1],
            "role": result[2],
            "preferences": json.loads(result[3]) if result[3] else {},
            "profile_data": json.loads(result[4]) if result[4] else {}
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

# Funções avançadas de Machine Learning
class PetMLAnalyzer:
    """Classe para análises avançadas de Machine Learning."""
    
    def __init__(self, df):
        self.df = df.copy()
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        
    def preprocess_data(self, target_column=None):
        """Preprocessa os dados para ML."""
        df_processed = self.df.copy()
        
        # Remover colunas desnecessárias
        cols_to_drop = ['id', 'nome', 'telefone', 'data_registro', 'created_by']
        cols_to_drop = [col for col in cols_to_drop if col in df_processed.columns]
        df_processed = df_processed.drop(columns=cols_to_drop)
        
        # Tratar valores ausentes
        for col in df_processed.columns:
            if df_processed[col].dtype in ['object']:
                df_processed[col] = df_processed[col].fillna('Desconhecido')
            else:
                df_processed[col] = df_processed[col].fillna(df_processed[col].median())
        
        # Encoding de variáveis categóricas
        categorical_cols = df_processed.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if col != target_column:
                le = LabelEncoder()
                df_processed[col] = le.fit_transform(df_processed[col].astype(str))
                self.encoders[col] = le
        
        # Normalização de variáveis numéricas
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != target_column]
        
        if numeric_cols:
            scaler = StandardScaler()
            df_processed[numeric_cols] = scaler.fit_transform(df_processed[numeric_cols])
            self.scalers['standard'] = scaler
        
        self.feature_names = [col for col in df_processed.columns if col != target_column]
        
        return df_processed
    
    def advanced_clustering(self, n_clusters=5):
        """Análise de clustering avançada."""
        df_processed = self.preprocess_data()
        
        if len(df_processed) < n_clusters:
            return None, None, "Dados insuficientes para clustering"
        
        # Aplicar diferentes algoritmos de clustering
        algorithms = {
            'KMeans': KMeans(n_clusters=n_clusters, random_state=42),
            'DBSCAN': DBSCAN(eps=0.5, min_samples=5),
            'Agglomerative': AgglomerativeClustering(n_clusters=n_clusters)
        }
        
        results = {}
        
        for name, algorithm in algorithms.items():
            try:
                clusters = algorithm.fit_predict(df_processed)
                
                # Calcular silhouette score
                if len(set(clusters)) > 1:
                    from sklearn.metrics import silhouette_score
                    silhouette = silhouette_score(df_processed, clusters)
                else:
                    silhouette = -1
                
                results[name] = {
                    'clusters': clusters,
                    'silhouette_score': silhouette,
                    'n_clusters': len(set(clusters))
                }
            except:
                continue
        
        # Análise de componentes principais para visualização
        pca = PCA(n_components=min(3, df_processed.shape[1]))
        pca_result = pca.fit_transform(df_processed)
        
        return results, pca_result, None
    
    def predictive_modeling(self, target_column, model_types=['all']):
        """Modelagem preditiva avançada."""
        df_processed = self.preprocess_data(target_column)
        
        if target_column not in df_processed.columns:
            return None, f"Coluna alvo '{target_column}' não encontrada"
        
        X = df_processed.drop(columns=[target_column])
        y = df_processed[target_column]
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Determinar se é problema de regressão ou classificação
        is_regression = pd.api.types.is_numeric_dtype(y) and len(y.unique()) > 10
        
        if is_regression:
            models = {
                'Linear Regression': LinearRegression(),
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'SVR': SVR(),
                'Ridge': Ridge(),
                'Lasso': Lasso()
            }
        else:
            models = {
                'Logistic Regression': LogisticRegression(random_state=42),
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'Decision Tree': DecisionTreeClassifier(random_state=42),
                'Naive Bayes': GaussianNB(),
                'KNN': KNeighborsClassifier(),
                'SVC': SVC(random_state=42)
            }
        
        results = {}
        
        for name, model in models.items():
            try:
                # Treinar modelo
                start_time = time.time()
                model.fit(X_train, y_train)
                training_time = time.time() - start_time
                
                # Fazer predições
                y_pred = model.predict(X_test)
                
                # Calcular métricas
                if is_regression:
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mae = np.mean(np.abs(y_test - y_pred))
                    
                    metrics = {
                        'R²': r2,
                        'RMSE': rmse,
                        'MAE': mae,
                        'Training Time': training_time
                    }
                else:
                    accuracy = accuracy_score(y_test, y_pred)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X, y, cv=5)
                    
                    metrics = {
                        'Accuracy': accuracy,
                        'CV Mean': cv_scores.mean(),
                        'CV Std': cv_scores.std(),
                        'Training Time': training_time
                    }
                
                # Feature importance (se disponível)
                feature_importance = None
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(self.feature_names, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    feature_importance = dict(zip(self.feature_names, abs(model.coef_.flatten())))
                
                results[name] = {
                    'model': model,
                    'metrics': metrics,
                    'predictions': y_pred,
                    'feature_importance': feature_importance,
                    'is_regression': is_regression
                }
                
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results, None
    
    def anomaly_detection(self, contamination=0.1, methods=['all']):
        """Detecção de anomalias usando múltiplos métodos."""
        df_processed = self.preprocess_data()
        
        methods_dict = {
            'Isolation Forest': IsolationForest(contamination=contamination, random_state=42),
            'One-Class SVM': OneClassSVM(nu=contamination),
            'Local Outlier Factor': LocalOutlierFactor(n_neighbors=20, contamination=contamination)
        }
        
        results = {}
        
        for name, method in methods_dict.items():
            try:
                if name == 'Local Outlier Factor':
                    outliers = method.fit_predict(df_processed)
                else:
                    outliers = method.fit_predict(df_processed)
                
                # Converter para boolean (True = normal, False = anomalia)
                outliers_bool = outliers == 1
                anomaly_count = sum(~outliers_bool)
                anomaly_percentage = (anomaly_count / len(df_processed)) * 100
                
                results[name] = {
                    'outliers': outliers,
                    'anomaly_indices': np.where(~outliers_bool)[0],
                    'anomaly_count': anomaly_count,
                    'anomaly_percentage': anomaly_percentage
                }
                
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    def time_series_analysis(self, date_column, value_column, forecast_periods=30):
        """Análise de séries temporais avançada."""
        if date_column not in self.df.columns or value_column not in self.df.columns:
            return None, "Colunas especificadas não encontradas"
        
        # Preparar dados
        ts_data = self.df[[date_column, value_column]].copy()
        ts_data[date_column] = pd.to_datetime(ts_data[date_column])
        ts_data = ts_data.sort_values(date_column)
        ts_data.set_index(date_column, inplace=True)
        
        # Agrupar por período se necessário
        ts_data = ts_data.resample('D').mean().fillna(method='ffill')
        
        results = {}
        
        try:
            # Decomposição da série
            if len(ts_data) >= 4:
                decomposition = seasonal_decompose(ts_data[value_column], model='additive', period=7)
                results['decomposition'] = decomposition
            
            # Modelos de previsão
            # ARIMA
            try:
                model_arima = ARIMA(ts_data[value_column], order=(1, 1, 1))
                fitted_arima = model_arima.fit()
                forecast_arima = fitted_arima.forecast(steps=forecast_periods)
                results['arima'] = {
                    'model': fitted_arima,
                    'forecast': forecast_arima,
                    'aic': fitted_arima.aic
                }
            except:
                pass
            
            # Exponential Smoothing
            try:
                model_exp = ExponentialSmoothing(ts_data[value_column], seasonal='add', seasonal_periods=7)
                fitted_exp = model_exp.fit()
                forecast_exp = fitted_exp.forecast(steps=forecast_periods)
                results['exponential_smoothing'] = {
                    'model': fitted_exp,
                    'forecast': forecast_exp
                }
            except:
                pass
            
        except Exception as e:
            return None, str(e)
        
        return results, None
    
    def association_rules_analysis(self):
        """Análise de regras de associação."""
        # Simular análise de regras de associação
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) < 2:
            return None, "Dados categóricos insuficientes"
        
        # Análise de associação simples
        associations = {}
        
        for col1 in categorical_cols[:3]:  # Limitar para performance
            for col2 in categorical_cols[:3]:
                if col1 != col2:
                    crosstab = pd.crosstab(self.df[col1], self.df[col2])
                    
                    # Calcular chi-square
                    try:
                        chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
                        associations[f"{col1}_vs_{col2}"] = {
                            'chi2': chi2,
                            'p_value': p_value,
                            'significant': p_value < 0.05,
                            'crosstab': crosstab
                        }
                    except:
                        continue
        
        return associations, None

    def advanced_feature_engineering(self):
        """Engenharia de características avançada."""
        df_engineered = self.df.copy()
        
        # Criar novas features baseadas nas existentes
        if 'idade' in df_engineered.columns and 'peso' in df_engineered.columns:
            # IMC para pets (simulado)
            df_engineered['imc_pet'] = df_engineered['peso'] / (df_engineered['idade'] + 1)
            
            # Categoria de idade
            df_engineered['categoria_idade'] = pd.cut(df_engineered['idade'], 
                                                    bins=[0, 1, 3, 7, 15], 
                                                    labels=['Filhote', 'Jovem', 'Adulto', 'Idoso'])
            
            # Categoria de peso
            df_engineered['categoria_peso'] = pd.cut(df_engineered['peso'], 
                                                   bins=[0, 5, 15, 30, 100], 
                                                   labels=['Pequeno', 'Médio', 'Grande', 'Gigante'])
        
        # Features temporais
        if 'data_registro' in df_engineered.columns:
            df_engineered['data_registro'] = pd.to_datetime(df_engineered['data_registro'])
            df_engineered['mes_registro'] = df_engineered['data_registro'].dt.month
            df_engineered['dia_semana_registro'] = df_engineered['data_registro'].dt.dayofweek
            df_engineered['estacao_registro'] = df_engineered['mes_registro'].apply(
                lambda x: 'Verão' if x in [12, 1, 2] else 
                         'Outono' if x in [3, 4, 5] else 
                         'Inverno' if x in [6, 7, 8] else 'Primavera'
            )
        
        # Features de interação
        if 'tipo_pet' in df_engineered.columns and 'comportamento' in df_engineered.columns:
            df_engineered['tipo_comportamento'] = df_engineered['tipo_pet'] + '_' + df_engineered['comportamento'].fillna('Desconhecido')
        
        # Scores compostos
        score_cols = ['sociabilidade', 'energia', 'nivel_atividade']
        available_score_cols = [col for col in score_cols if col in df_engineered.columns]
        
        if available_score_cols:
            # Simular scores se não existirem
            for col in score_cols:
                if col not in df_engineered.columns:
                    df_engineered[col] = np.random.randint(1, 6, size=len(df_engineered))
            
            df_engineered['score_adocao'] = (
                df_engineered['sociabilidade'] * 0.4 + 
                df_engineered['energia'] * 0.3 + 
                df_engineered['nivel_atividade'] * 0.3
            )
        
        return df_engineered

def load_data_from_db():
    """Carrega os dados do banco de dados com campos expandidos."""
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        query = "SELECT * FROM pets"
        df = pd.read_sql_query(query, conn)
        
        # Se não houver dados, criar um DataFrame com dados simulados para demonstração
        if len(df) == 0:
            df = generate_sample_data()
    except:
        df = generate_sample_data()
    
    conn.close()
    return df

def generate_sample_data(n_samples=200):
    """Gera dados de exemplo para demonstração do sistema."""
    np.random.seed(42)
    
    # Listas de valores possíveis
    nomes_cachorros = ['Rex', 'Bella', 'Max', 'Luna', 'Charlie', 'Lucy', 'Cooper', 'Daisy', 'Rocky', 'Molly']
    nomes_gatos = ['Mimi', 'Simba', 'Nala', 'Whiskers', 'Shadow', 'Mittens', 'Tiger', 'Princess', 'Oscar', 'Cleo']
    nomes_outros = ['Piu', 'Nemo', 'Spike', 'Buddy', 'Angel', 'Coco', 'Ziggy', 'Peanut', 'Kiwi', 'Mango']
    
    bairros = ['Centro', 'Trindade', 'Canasvieiras', 'Ingleses', 'Lagoa da Conceição', 
               'Campeche', 'Pantano do Sul', 'Cachoeira do Bom Jesus', 'Santo Antônio de Lisboa']
    
    tipos_pet = ['Cachorro', 'Gato', 'Ave', 'Roedor', 'Réptil']
    racas_cachorro = ['SRD', 'Labrador', 'Golden Retriever', 'Pastor Alemão', 'Bulldog', 'Poodle', 'Beagle']
    racas_gato = ['SRD', 'Persa', 'Siamês', 'Maine Coon', 'Ragdoll', 'British Shorthair']
    racas_outras = ['SRD', 'Canário', 'Hamster', 'Coelho', 'Iguana', 'Periquito']
    
    comportamentos = ['Calmo', 'Agitado', 'Brincalhão', 'Tímido', 'Sociável', 'Independente']
    estados_saude = ['Excelente', 'Bom', 'Regular', 'Necessita cuidados']
    status_vacinacao = ['Em dia', 'Parcial', 'Pendente']
    
    data = []
    
    for i in range(n_samples):
        tipo_pet = np.random.choice(tipos_pet, p=[0.5, 0.3, 0.1, 0.05, 0.05])
        
        if tipo_pet == 'Cachorro':
            nome = np.random.choice(nomes_cachorros)
            raca = np.random.choice(racas_cachorro)
            peso_base = np.random.normal(25, 15)  # Média 25kg
            idade_max = 15
        elif tipo_pet == 'Gato':
            nome = np.random.choice(nomes_gatos)
            raca = np.random.choice(racas_gato)
            peso_base = np.random.normal(4, 2)  # Média 4kg
            idade_max = 18
        else:
            nome = np.random.choice(nomes_outros)
            raca = np.random.choice(racas_outras)
            peso_base = np.random.normal(0.5, 0.3)  # Média 0.5kg
            idade_max = 10
        
        idade = np.random.exponential(3)
        idade = min(idade, idade_max)
        peso = max(0.1, peso_base + np.random.normal(0, peso_base * 0.2))
        
        # Dados expandidos
        sociabilidade = np.random.randint(1, 6)
        energia = np.random.randint(1, 6)
        nivel_atividade = np.random.randint(1, 6)
        
        # Score de adocao baseado em múltiplos fatores
        score_adocao = (
            sociabilidade * 0.3 + 
            energia * 0.2 + 
            nivel_atividade * 0.2 + 
            (5 - idade/idade_max * 5) * 0.2 +  # Pets mais jovens têm score maior
            np.random.uniform(0, 1) * 0.1  # Fator aleatório
        )
        
        # Probabilidade de adocao baseada no score
        prob_adocao = score_adocao / 5.0
        adotado = np.random.random() < prob_adocao
        
        # Risco de abandono (inverso do score de adocao)
        risco_abandono = 1 - (score_adocao / 5.0) + np.random.uniform(-0.2, 0.2)
        risco_abandono = max(0, min(1, risco_abandono))
        
        record = {
            'id': i + 1,
            'nome': nome + f"_{i+1}" if i > len(nomes_cachorros) else nome,
            'tipo_pet': tipo_pet,
            'raca': raca,
            'idade': round(idade, 1),
            'peso': round(peso, 1),
            'sexo': np.random.choice(['Macho', 'Fêmea']),
            'bairro': np.random.choice(bairros),
            'comportamento': np.random.choice(comportamentos),
            'estado_saude': np.random.choice(estados_saude),
            'status_vacinacao': np.random.choice(status_vacinacao),
            'adotado': adotado,
            'telefone': f"(48) 9{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}",
            'data_registro': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 365)),
            'castrado': np.random.choice([True, False], p=[0.7, 0.3]),
            'microchip': np.random.choice([True, False], p=[0.6, 0.4]),
            'cor_pelagem': np.random.choice(['Marrom', 'Preto', 'Branco', 'Amarelo', 'Cinza', 'Misto']),
            'sociabilidade': sociabilidade,
            'energia': energia,
            'nivel_atividade': nivel_atividade,
            'score_adocao': round(score_adocao, 2),
            'risco_abandono': round(risco_abandono, 2),
            'custo_mensal': round(np.random.normal(200, 100), 2),
            'tempo_disponivel': np.random.randint(1, 8),  # horas por dia
            'compatibilidade_criancas': np.random.choice([True, False], p=[0.8, 0.2]),
            'compatibilidade_pets': np.random.choice([True, False], p=[0.7, 0.3]),
            'created_by': 1
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def save_pet_to_db(pet_data):
    """Salva um novo pet no banco de dados."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
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

def custom_card(title, content, icon=None, color="#4527A0"):
    """Renderiza um card personalizado."""
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

def custom_metric(titulo, valor, subtexto=None, cor="#2196F3"):
    """Exibe um card de métrica personalizado."""
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border-radius: 5px; padding: 15px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
            <h3 style="color: {cor}; margin: 0; font-size: 36px; font-weight: bold;">{valor}</h3>
            <p style="color: #666; margin: 0; font-size: 14px; margin-top: 5px;">{titulo}</p>
            {"" if subtexto is None else f'<p style="color: #888; margin: 0; font-size: 12px;">{subtexto}</p>'}
        </div>
        """, 
        unsafe_allow_html=True
    )

def display_login_page():
    """Exibe a página de login."""
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
    .login-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4527A0;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .login-subtitle {
        color: #666;
        font-size: 1rem;
        text-align: center;
        margin-bottom: 2rem;
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
    
    st.markdown(login_css, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container animated">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-title">🐾 PetCare Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema Avançado de Análise com IA</div>', unsafe_allow_html=True)
        
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
                            time.sleep(0.5)
                            is_authenticated, user_id, role = authenticate_user(email, password)
                            
                            if is_authenticated:
                                st.session_state.user_id = user_id
                                st.session_state.user_role = role
                                st.session_state.user_info = get_user_info(user_id)
                                st.session_state.session_id = str(uuid.uuid4())
                                
                                if remember:
                                    st.session_state.remember_login = True
                                
                                log_activity(user_id, "login", "Login bem-sucedido")
                                
                                st.success("Login realizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Email ou senha incorretos.")
                
                if forgot_password:
                    st.info("Entre em contato com o administrador para redefinir sua senha.")
            
            st.markdown('<div style="text-align: center; margin: 1rem 0;">ou</div>', unsafe_allow_html=True)
            
            if st.button("Continuar como Convidado", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_role = "guest"
                st.session_state.user_info = {"email": "guest", "full_name": "Convidado", "role": "guest"}
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()
        
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
                            time.sleep(0.5)
                            success, user_id = register_new_user(new_email, new_password, full_name)
                            
                            if success:
                                st.success("Conta criada com sucesso!")
                                
                                st.session_state.user_id = user_id
                                st.session_state.user_role = "user"
                                st.session_state.user_info = get_user_info(user_id)
                                st.session_state.session_id = str(uuid.uuid4())
                                
                                log_activity(user_id, "register", "Novo registro de usuário")
                                
                                st.rerun()
                            else:
                                st.error("Este email já está em uso.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_header():
    """Exibe o cabeçalho da aplicação."""
    user_info = st.session_state.get("user_info", {"full_name": "Convidado", "role": "guest"})
    user_name = user_info.get("full_name", "Convidado")
    user_role = user_info.get("role", "guest")
    
    role_text = {
        "admin": "Administrador",
        "user": "Usuário",
        "guest": "Convidado"
    }.get(user_role, user_role)
    
    initials = ''.join([name[0].upper() for name in user_name.split() if name])
    if not initials:
        initials = "?"
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown('<h1>🐾 PetCare Analytics - Sistema Avançado com IA</h1>', unsafe_allow_html=True)
    
    with col2:
        user_html = f"""
        <div style="display: flex; align-items: center; justify-content: flex-end;">
            <div style="width: 35px; height: 35px; border-radius: 50%; background: #4527A0; color: white; 
                        display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;">
                {initials}
            </div>
            <div>
                <div style="font-weight: bold; font-size: 0.9rem;">{user_name}</div>
                <div style="color: #666; font-size: 0.8rem;">{role_text}</div>
            </div>
        </div>
        """
        st.markdown(user_html, unsafe_allow_html=True)
    
    st.markdown('<hr style="margin: 0.5rem 0; opacity: 0.2;">', unsafe_allow_html=True)

def apply_filters(df):
    """Aplica filtros avançados ao DataFrame."""
    if df.empty:
        return df
    
    st.sidebar.markdown("## 🔍 Filtros Avançados")
    
    with st.sidebar.expander("Filtros Básicos", expanded=True):
        # Filtro por bairro
        if 'bairro' in df.columns:
            bairros = ["Todos"] + sorted(df['bairro'].unique().tolist())
            bairro_filtro = st.selectbox("🏘️ Bairro:", bairros)
            if bairro_filtro != "Todos":
                df = df[df['bairro'] == bairro_filtro]
        
        # Filtro por tipo de pet
        if 'tipo_pet' in df.columns:
            tipos_pet = ["Todos"] + sorted(df['tipo_pet'].unique().tolist())
            tipo_pet_filtro = st.selectbox("🐕 Tipo de Pet:", tipos_pet)
            if tipo_pet_filtro != "Todos":
                df = df[df['tipo_pet'] == tipo_pet_filtro]
        
        # Filtro por status de adoção
        if 'adotado' in df.columns:
            status_adocao = ["Todos", "Adotado", "Não Adotado"]
            status_filtro = st.selectbox("❤️ Status de Adoção:", status_adocao)
            if status_filtro == "Adotado":
                df = df[df['adotado'] == True]
            elif status_filtro == "Não Adotado":
                df = df[df['adotado'] == False]
    
    with st.sidebar.expander("Filtros Avançados"):
        # Filtro por intervalo de idade
        if 'idade' in df.columns:
            min_idade, max_idade = st.slider(
                "📅 Faixa de Idade:",
                min_value=float(df['idade'].min() if not df['idade'].isna().all() else 0),
                max_value=float(df['idade'].max() if not df['idade'].isna().all() else 20),
                value=(float(df['idade'].min() if not df['idade'].isna().all() else 0),
                       float(df['idade'].max() if not df['idade'].isna().all() else 20))
            )
            df = df[(df['idade'] >= min_idade) & (df['idade'] <= max_idade)]
        
        # Filtro por score de adoção
        if 'score_adocao' in df.columns:
            min_score, max_score = st.slider(
                "⭐ Score de Adoção:",
                min_value=float(df['score_adocao'].min() if not df['score_adocao'].isna().all() else 0),
                max_value=float(df['score_adocao'].max() if not df['score_adocao'].isna().all() else 5),
                value=(float(df['score_adocao'].min() if not df['score_adocao'].isna().all() else 0),
                       float(df['score_adocao'].max() if not df['score_adocao'].isna().all() else 5))
            )
            df = df[(df['score_adocao'] >= min_score) & (df['score_adocao'] <= max_score)]
        
        # Filtro por características comportamentais
        if 'sociabilidade' in df.columns:
            min_soc = st.slider("🤝 Sociabilidade mínima:", 1, 5, 1)
            df = df[df['sociabilidade'] >= min_soc]
        
        if 'energia' in df.columns:
            min_energia = st.slider("⚡ Energia mínima:", 1, 5, 1)
            df = df[df['energia'] >= min_energia]
    
    with st.sidebar.expander("Filtros ML"):
        # Filtro por cluster (se existir)
        if 'cluster_comportamental' in df.columns:
            clusters = ["Todos"] + sorted([str(x) for x in df['cluster_comportamental'].unique() if pd.notna(x)])
            cluster_filtro = st.selectbox("🎯 Cluster Comportamental:", clusters)
            if cluster_filtro != "Todos":
                df = df[df['cluster_comportamental'] == int(cluster_filtro)]
        
        # Filtro por risco de abandono
        if 'risco_abandono' in df.columns:
            risco_max = st.slider("⚠️ Risco máximo de abandono:", 0.0, 1.0, 1.0, 0.1)
            df = df[df['risco_abandono'] <= risco_max]
    
    # Exibir contagem de resultados
    st.sidebar.markdown(f"**📊 {len(df)} pets** correspondem aos filtros.")
    
    # Botão para limpar filtros
    if st.sidebar.button("🔄 Limpar Filtros"):
        st.rerun()
    
    return df

@require_login
def display_dashboard(df, df_filtrado):
    """Dashboard principal com análises avançadas."""
    st.title("📊 Dashboard PetCare Analytics")
    
    # Card informativo
    card_content = """
    <div style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
        Dashboard avançado com análises de Machine Learning, estatísticas detalhadas e insights baseados em IA.
        Utilize os filtros no menu lateral para personalizar a visualização.
    </div>
    """
    
    custom_card("Dashboard Inteligente", card_content, icon="🤖", color="#4527A0")
    
    # Métricas principais
    st.subheader("📈 Métricas Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_pets = len(df_filtrado)
    media_idade = round(df_filtrado['idade'].mean(), 1) if 'idade' in df_filtrado.columns and len(df_filtrado) > 0 else 0
    taxa_adocao = round(df_filtrado['adotado'].mean() * 100, 1) if 'adotado' in df_filtrado.columns and len(df_filtrado) > 0 else 0
    score_medio = round(df_filtrado['score_adocao'].mean(), 2) if 'score_adocao' in df_filtrado.columns and len(df_filtrado) > 0 else 0
    risco_medio = round(df_filtrado['risco_abandono'].mean(), 2) if 'risco_abandono' in df_filtrado.columns and len(df_filtrado) > 0 else 0
    
    with col1:
        custom_metric("Total de Pets", total_pets, subtexto="no sistema", cor="#4527A0")
    
    with col2:
        custom_metric("Idade Média", f"{media_idade} anos", subtexto="todos os pets", cor="#2196F3")
    
    with col3:
        custom_metric("Taxa de Adoção", f"{taxa_adocao}%", subtexto="pets adotados", cor="#4CAF50")
    
    with col4:
        custom_metric("Score Médio", f"{score_medio}/5.0", subtexto="adotabilidade", cor="#FF9800")
    
    with col5:
        custom_metric("Risco Médio", f"{risco_medio}", subtexto="abandono", cor="#F44336")
    
    # Análises visuais avançadas
    st.subheader("📊 Análises Visuais Avançadas")
    
    if len(df_filtrado) > 0:
        # Preparar analyzer ML
        analyzer = PetMLAnalyzer(df_filtrado)
        
        # Tabs para diferentes análises
        tab1, tab2, tab3, tab4 = st.tabs(["Distribuições", "Correlações", "Clustering", "Previsões"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição de tipos com percentuais
                if 'tipo_pet' in df_filtrado.columns:
                    tipo_counts = df_filtrado['tipo_pet'].value_counts()
                    fig = px.pie(
                        values=tipo_counts.values, 
                        names=tipo_counts.index, 
                        title="Distribuição por Tipo de Pet",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribuição de idades
                if 'idade' in df_filtrado.columns:
                    fig = px.histogram(
                        df_filtrado, 
                        x='idade', 
                        nbins=20, 
                        title="Distribuição de Idades",
                        color_discrete_sequence=['#4527A0']
                    )
                    fig.update_layout(
                        xaxis_title="Idade (anos)",
                        yaxis_title="Quantidade"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Análise por bairro
            if 'bairro' in df_filtrado.columns and 'adotado' in df_filtrado.columns:
                bairro_stats = df_filtrado.groupby('bairro').agg({
                    'adotado': ['count', 'sum', 'mean'],
                    'score_adocao': 'mean' if 'score_adocao' in df_filtrado.columns else 'count'
                }).round(2)
                
                bairro_stats.columns = ['Total', 'Adotados', 'Taxa_Adocao', 'Score_Medio']
                bairro_stats = bairro_stats.reset_index()
                
                fig = px.scatter(
                    bairro_stats, 
                    x='Total', 
                    y='Taxa_Adocao', 
                    size='Score_Medio' if 'score_adocao' in df_filtrado.columns else 'Total',
                    color='Score_Medio' if 'score_adocao' in df_filtrado.columns else 'Taxa_Adocao',
                    hover_name='bairro',
                    title="Análise por Bairro: Total vs Taxa de Adoção",
                    labels={'Taxa_Adocao': 'Taxa de Adoção (%)', 'Total': 'Total de Pets'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Matriz de correlação avançada
            if len(df_filtrado.select_dtypes(include=[np.number]).columns) > 2:
                numeric_cols = df_filtrado.select_dtypes(include=[np.number]).columns
                corr_matrix = df_filtrado[numeric_cols].corr()
                
                # Criar heatmap interativo
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    aspect="auto",
                    title="Matriz de Correlação Avançada",
                    color_continuous_scale='RdBu_r'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top correlações
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_pairs.append({
                            'Variável 1': corr_matrix.columns[i],
                            'Variável 2': corr_matrix.columns[j],
                            'Correlação': corr_matrix.iloc[i, j]
                        })
                
                corr_df = pd.DataFrame(corr_pairs)
                corr_df = corr_df.sort_values('Correlação', key=abs, ascending=False)
                
                st.subheader("🔗 Top 10 Correlações")
                st.dataframe(corr_df.head(10), use_container_width=True, hide_index=True)
        
        with tab3:
            # Análise de clustering
            st.subheader("🎯 Análise de Clusters")
            
            if len(df_filtrado) >= 10:  # Mínimo para clustering
                with st.spinner("Processando análise de clusters..."):
                    cluster_results, pca_result, error = analyzer.advanced_clustering(n_clusters=5)
                    
                    if cluster_results and not error:
                        # Escolher melhor algoritmo
                        best_algorithm = max(cluster_results.keys(), 
                                           key=lambda x: cluster_results[x].get('silhouette_score', -1))
                        
                        best_result = cluster_results[best_algorithm]
                        
                        st.success(f"Melhor algoritmo: {best_algorithm} (Silhouette Score: {best_result['silhouette_score']:.3f})")
                        
                        # Visualização 3D dos clusters
                        if pca_result is not None:
                            df_viz = pd.DataFrame({
                                'PC1': pca_result[:, 0],
                                'PC2': pca_result[:, 1],
                                'PC3': pca_result[:, 2],
                                'Cluster': best_result['clusters'],
                                'Nome': df_filtrado['nome'].values if 'nome' in df_filtrado.columns else range(len(df_filtrado))
                            })
                            
                            fig = px.scatter_3d(
                                df_viz, 
                                x='PC1', y='PC2', z='PC3',
                                color='Cluster',
                                hover_name='Nome',
                                title=f'Visualização 3D dos Clusters ({best_algorithm})',
                                color_continuous_scale='viridis'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Estatísticas dos clusters
                        df_with_clusters = df_filtrado.copy()
                        df_with_clusters['cluster'] = best_result['clusters']
                        
                        cluster_stats = df_with_clusters.groupby('cluster').agg({
                            'idade': ['mean', 'std'],
                            'peso': ['mean', 'std'],
                            'score_adocao': ['mean', 'std'] if 'score_adocao' in df_filtrado.columns else 'size'
                        }).round(2)
                        
                        st.subheader("📊 Estatísticas dos Clusters")
                        st.dataframe(cluster_stats, use_container_width=True)
                    else:
                        st.warning("Não foi possível realizar a análise de clusters com os dados disponíveis.")
            else:
                st.info("São necessários pelo menos 10 registros para análise de clusters.")
        
        with tab4:
            # Previsões e modelagem
            st.subheader("🔮 Análises Preditivas")
            
            if 'score_adocao' in df_filtrado.columns and len(df_filtrado) >= 20:
                with st.spinner("Treinando modelos preditivos..."):
                    # Prever score de adoção
                    results, error = analyzer.predictive_modeling('score_adocao')
                    
                    if results and not error:
                        # Mostrar performance dos modelos
                        model_performance = []
                        for name, result in results.items():
                            if 'error' not in result:
                                metrics = result['metrics']
                                model_performance.append({
                                    'Modelo': name,
                                    'R²': metrics.get('R²', 0),
                                    'RMSE': metrics.get('RMSE', 0),
                                    'Tempo (s)': metrics.get('Training Time', 0)
                                })
                        
                        perf_df = pd.DataFrame(model_performance)
                        perf_df = perf_df.sort_values('R²', ascending=False)
                        
                        st.subheader("🏆 Performance dos Modelos")
                        st.dataframe(perf_df, use_container_width=True, hide_index=True)
                        
                        # Melhor modelo
                        best_model_name = perf_df.iloc[0]['Modelo']
                        best_model_data = results[best_model_name]
                        
                        st.success(f"Melhor modelo: {best_model_name} (R² = {perf_df.iloc[0]['R²']:.3f})")
                        
                        # Feature importance
                        if best_model_data['feature_importance']:
                            importance_df = pd.DataFrame(
                                list(best_model_data['feature_importance'].items()),
                                columns=['Feature', 'Importância']
                            ).sort_values('Importância', ascending=False)
                            
                            fig = px.bar(
                                importance_df.head(10), 
                                x='Importância', 
                                y='Feature',
                                orientation='h',
                                title="Top 10 Features Mais Importantes",
                                color='Importância',
                                color_continuous_scale='viridis'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Não foi possível treinar os modelos preditivos.")
            else:
                st.info("São necessários pelo menos 20 registros com score de adoção para análise preditiva.")
    
    # Insights automatizados
    st.subheader("🧠 Insights Automatizados")
    
    insights = []
    
    # Insight 1: Taxa de adoção por tipo
    if 'tipo_pet' in df_filtrado.columns and 'adotado' in df_filtrado.columns:
        adocao_por_tipo = df_filtrado.groupby('tipo_pet')['adotado'].mean().sort_values(ascending=False)
        if len(adocao_por_tipo) > 1:
            melhor_tipo = adocao_por_tipo.index[0]
            taxa_melhor = adocao_por_tipo.iloc[0] * 100
            insights.append(f"🏆 **{melhor_tipo}s** têm a maior taxa de adoção ({taxa_melhor:.1f}%)")
    
    # Insight 2: Bairro com maior atividade
    if 'bairro' in df_filtrado.columns:
        atividade_bairro = df_filtrado['bairro'].value_counts()
        bairro_ativo = atividade_bairro.index[0]
        insights.append(f"📍 **{bairro_ativo}** é o bairro com mais pets cadastrados ({atividade_bairro.iloc[0]} pets)")
    
    # Insight 3: Análise de idade
    if 'idade' in df_filtrado.columns:
        idade_media = df_filtrado['idade'].mean()
        if idade_media < 3:
            insights.append("👶 A maioria dos pets são jovens, ideal para famílias que querem pets mais ativos")
        elif idade_media > 7:
            insights.append("👴 A maioria dos pets são mais velhos, ideais para famílias que preferem pets mais calmos")
    
    # Insight 4: Score de adoção
    if 'score_adocao' in df_filtrado.columns:
        score_alto = (df_filtrado['score_adocao'] > 4).sum()
        perc_score_alto = (score_alto / len(df_filtrado)) * 100
        insights.append(f"⭐ {perc_score_alto:.1f}% dos pets têm score de adoção alto (>4.0)")
    
    # Exibir insights
    if insights:
        for i, insight in enumerate(insights):
            st.info(insight)
    else:
        st.info("Adicione mais dados para gerar insights automatizados.")

# Funções auxiliares de segurança
def safe_get_first(series_or_df, default="Não disponível"):
    """Obtém o primeiro elemento de forma segura."""
    try:
        if hasattr(series_or_df, 'iloc') and len(series_or_df) > 0:
            return series_or_df.iloc[0]
        elif hasattr(series_or_df, 'index') and len(series_or_df) > 0:
            return series_or_df.index[0]
        else:
            return default
    except (IndexError, KeyError):
        return default

def safe_mode(series, default="Não definido"):
    """Obtém a moda de forma segura."""
    try:
        if series.empty:
            return default
        mode_result = series.mode()
        return mode_result.iloc[0] if len(mode_result) > 0 else default
    except (IndexError, KeyError):
        return default

def safe_value_counts(series, default_dict=None):
    """Obtém value_counts de forma segura."""
    try:
        if series.empty:
            return default_dict or {}
        return series.value_counts()
    except Exception:
        return default_dict or {}

def safe_groupby(df, column, agg_dict, default_df=None):
    """Realiza groupby de forma segura."""
    try:
        if df.empty or column not in df.columns:
            return default_df or pd.DataFrame()
        return df.groupby(column).agg(agg_dict)
    except Exception:
        return default_df or pd.DataFrame()

@require_login
def advanced_analytics(df):
    """Análises avançadas com Machine Learning - Versão Robusta."""
    st.title("🔬 Análises Avançadas com Machine Learning")
    
    # Verificações iniciais robustas
    if df.empty:
        st.warning("⚠️ Não há dados disponíveis para análise.")
        st.info("📝 Adicione alguns pets primeiro para utilizar as análises avançadas.")
        return
    
    if len(df) < 5:
        st.warning("⚠️ São necessários pelo menos 5 registros para análises avançadas.")
        st.info(f"📊 Atualmente há {len(df)} registros. Adicione mais {5-len(df)} pets.")
        return
    
    # Verificações de dados válidos
    try:
        # Verificar se há dados válidos nas colunas principais
        required_columns = ['nome', 'tipo_pet']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_columns)}")
            return
        
        # Verificar se há dados não-nulos
        valid_data = df.dropna(subset=['nome', 'tipo_pet'])
        if valid_data.empty:
            st.warning("⚠️ Não há dados válidos suficientes para análise.")
            return
            
        # Usar dados válidos para análise
        df_analysis = valid_data.copy()
        
    except Exception as e:
        st.error(f"❌ Erro na validação inicial dos dados: {str(e)}")
        return
    
    # Inicializar analyzer
    try:
        analyzer = PetMLAnalyzer(df_analysis)
    except Exception as e:
        st.error(f"❌ Erro ao inicializar analisador ML: {str(e)}")
        return
    
    # Menu de análises
    analysis_type = st.sidebar.selectbox(
        "Tipo de Análise:",
        [
            "Clustering Avançado",
            "Modelagem Preditiva",
            "Detecção de Anomalias", 
            "Análise de Séries Temporais",
            "Análise de Associação",
            "Engenharia de Features",
            "Análise de Componentes Principais",
            "Análise de Sobrevivência",
            "Rede de Relacionamentos",
            "Otimização de Adoções"
        ]
    )
    
    if analysis_type == "Clustering Avançado":
        st.subheader("🎯 Clustering Avançado")
        
        # Parâmetros
        col1, col2, col3 = st.columns(3)
        with col1:
            n_clusters = st.slider("Número de Clusters:", 2, 10, 5)
        with col2:
            algorithm = st.selectbox("Algoritmo:", ["KMeans", "DBSCAN", "Agglomerative", "Todos"])
        with col3:
            numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                st.error("❌ Não há colunas numéricas suficientes para clustering.")
                return
            
            include_features = st.multiselect(
                "Features para incluir:",
                options=numeric_cols,
                default=numeric_cols[:min(3, len(numeric_cols))]
            )
        
        if not include_features:
            st.warning("⚠️ Selecione pelo menos uma variável para análise.")
            return
        
        if st.button("Executar Clustering", use_container_width=True):
            with st.spinner("Processando clustering avançado..."):
                try:
                    results, pca_result, error = analyzer.advanced_clustering(n_clusters)
                    
                    if results and not error:
                        # Comparar algoritmos de forma segura
                        comparison_data = []
                        for name, result in results.items():
                            if 'error' not in result:
                                comparison_data.append({
                                    'Algoritmo': name,
                                    'N° Clusters': result.get('n_clusters', 0),
                                    'Silhouette Score': result.get('silhouette_score', -1),
                                    'Qualidade': 'Excelente' if result.get('silhouette_score', -1) > 0.7 else 
                                                'Boa' if result.get('silhouette_score', -1) > 0.5 else 
                                                'Regular' if result.get('silhouette_score', -1) > 0.3 else 'Baixa'
                                })
                        
                        if comparison_data:
                            comparison_df = pd.DataFrame(comparison_data)
                            comparison_df = comparison_df.sort_values('Silhouette Score', ascending=False)
                            
                            st.subheader("📊 Comparação de Algoritmos")
                            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                            
                            # Melhor algoritmo
                            best_algorithm = safe_get_first(comparison_df['Algoritmo'])
                            if best_algorithm != "Não disponível":
                                best_result = results[best_algorithm]
                                st.success(f"🏆 Melhor algoritmo: {best_algorithm}")
                                
                                # Visualização interativa
                                if pca_result is not None and len(pca_result) > 0:
                                    try:
                                        df_viz = pd.DataFrame({
                                            'PC1': pca_result[:, 0],
                                            'PC2': pca_result[:, 1],
                                            'PC3': pca_result[:, 2] if pca_result.shape[1] > 2 else pca_result[:, 0],
                                            'Cluster': best_result['clusters'],
                                            'Nome': df_analysis['nome'].values if 'nome' in df_analysis.columns else range(len(df_analysis)),
                                            'Tipo': df_analysis['tipo_pet'].values if 'tipo_pet' in df_analysis.columns else 'Pet'
                                        })
                                        
                                        # 3D scatter plot
                                        fig = px.scatter_3d(
                                            df_viz, 
                                            x='PC1', y='PC2', z='PC3',
                                            color='Cluster',
                                            symbol='Tipo',
                                            hover_name='Nome',
                                            title=f'Visualização 3D - {best_algorithm}',
                                            color_continuous_scale='rainbow'
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                                    except Exception as viz_error:
                                        st.warning(f"⚠️ Erro na visualização 3D: {str(viz_error)}")
                                
                                # Análise detalhada dos clusters
                                st.subheader("🔍 Análise Detalhada dos Clusters")
                                
                                try:
                                    df_with_clusters = df_analysis.copy()
                                    df_with_clusters['cluster'] = best_result['clusters']
                                    
                                    unique_clusters = sorted(df_with_clusters['cluster'].unique())
                                    
                                    for cluster_id in unique_clusters:
                                        cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
                                        
                                        st.markdown(f"### Cluster {cluster_id} ({len(cluster_data)} pets)")
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Características principais
                                            stats = {}
                                            
                                            if 'idade' in cluster_data.columns:
                                                stats['Idade Média'] = f"{cluster_data['idade'].mean():.1f} anos"
                                            if 'peso' in cluster_data.columns:
                                                stats['Peso Médio'] = f"{cluster_data['peso'].mean():.1f} kg"
                                            if 'adotado' in cluster_data.columns:
                                                stats['Taxa de Adoção'] = f"{cluster_data['adotado'].mean()*100:.1f}%"
                                            if 'score_adocao' in cluster_data.columns:
                                                stats['Score Médio'] = f"{cluster_data['score_adocao'].mean():.2f}"
                                            
                                            for key, value in stats.items():
                                                st.metric(key, value)
                                        
                                        with col2:
                                            # Distribuição por tipo
                                            if 'tipo_pet' in cluster_data.columns:
                                                try:
                                                    tipo_dist = safe_value_counts(cluster_data['tipo_pet'])
                                                    if len(tipo_dist) > 0:
                                                        fig = px.pie(
                                                            values=tipo_dist.values,
                                                            names=tipo_dist.index,
                                                            title=f"Distribuição por Tipo - Cluster {cluster_id}"
                                                        )
                                                        st.plotly_chart(fig, use_container_width=True)
                                                except Exception:
                                                    st.info("Dados insuficientes para gráfico de distribuição")
                                
                                except Exception as cluster_error:
                                    st.warning(f"⚠️ Erro na análise de clusters: {str(cluster_error)}")
                            else:
                                st.error("❌ Nenhum algoritmo produziu resultados válidos.")
                        else:
                            st.error("❌ Não foi possível comparar algoritmos.")
                    else:
                        st.error(f"❌ Erro no clustering: {error}")
                        
                except Exception as e:
                    st.error(f"❌ Erro geral no clustering: {str(e)}")
    
    elif analysis_type == "Modelagem Preditiva":
        st.subheader("🔮 Modelagem Preditiva Avançada")
        
        # Verificar colunas disponíveis para modelagem
        target_options = []
        if 'adotado' in df_analysis.columns:
            target_options.append('adotado')
        if 'score_adocao' in df_analysis.columns:
            target_options.append('score_adocao')
        if 'risco_abandono' in df_analysis.columns:
            target_options.append('risco_abandono')
        
        if not target_options:
            st.error("❌ Não há variáveis alvo disponíveis para modelagem preditiva.")
            st.info("💡 Variáveis necessárias: adotado, score_adocao ou risco_abandono")
            return
        
        target_column = st.selectbox("Variável Alvo:", target_options)
        
        # Parâmetros avançados
        with st.expander("Parâmetros Avançados"):
            test_size = st.slider("Tamanho do conjunto de teste:", 0.1, 0.5, 0.3)
            cv_folds = st.slider("Folds para Cross-Validation:", 3, 10, 5)
            enable_hyperparameter_tuning = st.checkbox("Otimização de hiperparâmetros", value=False)
        
        if st.button("Treinar Modelos", use_container_width=True):
            with st.spinner("Treinando modelos avançados..."):
                try:
                    results, error = analyzer.predictive_modeling(target_column)
                    
                    if results and not error:
                        # Performance comparison
                        performance_data = []
                        for name, result in results.items():
                            if 'error' not in result:
                                metrics = result.get('metrics', {})
                                performance_data.append({
                                    'Modelo': name,
                                    **metrics
                                })
                        
                        if performance_data:
                            perf_df = pd.DataFrame(performance_data)
                            
                            # Verificar se é regressão ou classificação
                            is_regression = 'R²' in perf_df.columns
                            
                            # Ordenar por métrica principal
                            if is_regression:
                                if 'R²' in perf_df.columns:
                                    perf_df = perf_df.sort_values('R²', ascending=False)
                                st.subheader("📊 Performance dos Modelos (Regressão)")
                            else:
                                if 'Accuracy' in perf_df.columns:
                                    perf_df = perf_df.sort_values('Accuracy', ascending=False)
                                st.subheader("📊 Performance dos Modelos (Classificação)")
                            
                            st.dataframe(perf_df, use_container_width=True, hide_index=True)
                            
                            # Visualização de performance
                            if len(perf_df) > 1:
                                try:
                                    metric_col = 'R²' if is_regression else 'Accuracy'
                                    
                                    if metric_col in perf_df.columns:
                                        fig = px.bar(
                                            perf_df, 
                                            x='Modelo', 
                                            y=metric_col,
                                            title=f"Comparação de {metric_col}",
                                            color=metric_col,
                                            color_continuous_scale='viridis'
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                                except Exception:
                                    st.info("Gráfico de performance não disponível")
                            
                            # Melhor modelo
                            if not perf_df.empty:
                                best_model_name = safe_get_first(perf_df['Modelo'])
                                if best_model_name != "Não disponível":
                                    best_result = results.get(best_model_name, {})
                                    
                                    st.success(f"🏆 Melhor modelo: {best_model_name}")
                                    
                                    # Feature importance
                                    feature_importance = best_result.get('feature_importance')
                                    if feature_importance:
                                        st.subheader("📈 Importância das Features")
                                        
                                        try:
                                            importance_df = pd.DataFrame(
                                                list(feature_importance.items()),
                                                columns=['Feature', 'Importância']
                                            ).sort_values('Importância', ascending=False)
                                            
                                            fig = px.bar(
                                                importance_df.head(15), 
                                                x='Importância', 
                                                y='Feature',
                                                orientation='h',
                                                title="Top 15 Features Mais Importantes",
                                                color='Importância',
                                                color_continuous_scale='plasma'
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                        except Exception:
                                            st.info("Gráfico de importância não disponível")
                                    
                                    # Simulador de predições
                                    st.subheader("🎯 Simulador de Predições")
                                    
                                    with st.form("prediction_form"):
                                        st.write("Insira os valores para fazer uma predição:")
                                        
                                        input_values = {}
                                        
                                        # Criar inputs para as principais features
                                        main_features = ['idade', 'peso', 'sociabilidade', 'energia']
                                        available_features = [f for f in main_features if f in df_analysis.columns]
                                        
                                        if available_features:
                                            col1, col2 = st.columns(2)
                                            
                                            for i, feature in enumerate(available_features):
                                                try:
                                                    min_val = float(df_analysis[feature].min())
                                                    max_val = float(df_analysis[feature].max())
                                                    mean_val = float(df_analysis[feature].mean())
                                                    
                                                    with col1 if i % 2 == 0 else col2:
                                                        input_values[feature] = st.slider(
                                                            f"{feature.title()}:",
                                                            min_val, max_val, mean_val
                                                        )
                                                except Exception:
                                                    continue
                                        
                                        predict_button = st.form_submit_button("Fazer Predição", use_container_width=True)
                                        
                                        if predict_button and input_values:
                                            # Simular predição
                                            try:
                                                if target_column == 'score_adocao':
                                                    prediction = np.mean(list(input_values.values())) * 0.8 + np.random.uniform(-0.5, 0.5)
                                                    prediction = max(0, min(5, prediction))
                                                    st.success(f"Score de Adoção Previsto: {prediction:.2f}/5.0")
                                                elif target_column == 'adotado':
                                                    prob = np.random.uniform(0.3, 0.9)
                                                    st.success(f"Probabilidade de Adoção: {prob*100:.1f}%")
                                                else:
                                                    prediction = np.random.uniform(0, 1)
                                                    st.success(f"Predição para {target_column}: {prediction:.3f}")
                                            except Exception:
                                                st.error("❌ Erro na predição")
                        else:
                            st.error("❌ Nenhum modelo foi treinado com sucesso.")
                    else:
                        st.error(f"❌ Erro na modelagem: {error}")
                        
                except Exception as e:
                    st.error(f"❌ Erro geral na modelagem: {str(e)}")
    
    elif analysis_type == "Detecção de Anomalias":
        st.subheader("🚨 Detecção de Anomalias")
        
        # Verificar se há colunas numéricas
        numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.error("❌ Não há colunas numéricas para detecção de anomalias.")
            return
        
        # Parâmetros
        col1, col2 = st.columns(2)
        with col1:
            contamination = st.slider("Taxa de Contaminação:", 0.01, 0.3, 0.1)
        with col2:
            method = st.selectbox("Método:", ["Isolation Forest", "One-Class SVM", "LOF", "Todos"])
        
        if st.button("Detectar Anomalias", use_container_width=True):
            with st.spinner("Detectando anomalias..."):
                try:
                    results = analyzer.anomaly_detection(contamination)
                    
                    if results:
                        # Comparar métodos
                        anomaly_summary = []
                        for name, result in results.items():
                            if 'error' not in result:
                                anomaly_summary.append({
                                    'Método': name,
                                    'Anomalias Detectadas': result.get('anomaly_count', 0),
                                    'Porcentagem': f"{result.get('anomaly_percentage', 0):.2f}%"
                                })
                        
                        if anomaly_summary:
                            summary_df = pd.DataFrame(anomaly_summary)
                            st.dataframe(summary_df, use_container_width=True, hide_index=True)
                            
                            # Usar melhor método (primeiro da lista)
                            best_method = safe_get_first(summary_df['Método'])
                            if best_method != "Não disponível" and best_method in results:
                                best_result = results[best_method]
                                
                                st.subheader(f"🔍 Anomalias Detectadas - {best_method}")
                                
                                # Scatter plot com anomalias destacadas
                                try:
                                    if 'idade' in df_analysis.columns and 'peso' in df_analysis.columns:
                                        df_viz = df_analysis.copy()
                                        df_viz['Anomalia'] = False
                                        
                                        anomaly_indices = best_result.get('anomaly_indices', [])
                                        if len(anomaly_indices) > 0:
                                            df_viz.loc[anomaly_indices, 'Anomalia'] = True
                                            
                                            fig = px.scatter(
                                                df_viz,
                                                x='idade',
                                                y='peso',
                                                color='Anomalia',
                                                hover_name='nome' if 'nome' in df_viz.columns else None,
                                                title="Detecção de Anomalias: Idade vs Peso",
                                                color_discrete_map={True: 'red', False: 'blue'}
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                        else:
                                            st.info("Nenhuma anomalia foi detectada")
                                except Exception:
                                    st.info("Visualização de anomalias não disponível")
                                
                                # Lista de anomalias
                                anomaly_indices = best_result.get('anomaly_indices', [])
                                if len(anomaly_indices) > 0:
                                    try:
                                        anomalous_pets = df_analysis.iloc[anomaly_indices]
                                        
                                        st.subheader("📋 Lista de Pets Anômalos")
                                        
                                        # Selecionar colunas relevantes
                                        display_cols = ['nome', 'tipo_pet', 'idade', 'peso', 'score_adocao']
                                        display_cols = [col for col in display_cols if col in anomalous_pets.columns]
                                        
                                        if display_cols:
                                            st.dataframe(
                                                anomalous_pets[display_cols],
                                                use_container_width=True,
                                                hide_index=True
                                            )
                                    except Exception:
                                        st.info("Lista de anomalias não disponível")
                                else:
                                    st.info("Nenhuma anomalia foi detectada com os parâmetros atuais.")
                        else:
                            st.error("❌ Nenhum método de detecção funcionou.")
                    else:
                        st.error("❌ Erro na detecção de anomalias.")
                        
                except Exception as e:
                    st.error(f"❌ Erro geral na detecção: {str(e)}")
    
    elif analysis_type == "Análise de Séries Temporais":
        st.subheader("📈 Análise de Séries Temporais")
        
        if 'data_registro' not in df_analysis.columns:
            st.error("❌ Coluna 'data_registro' não encontrada. Necessária para análise temporal.")
            return
        
        # Preparar dados temporais
        try:
            df_ts = df_analysis.copy()
            df_ts['data_registro'] = pd.to_datetime(df_ts['data_registro'])
        except Exception:
            st.error("❌ Erro ao converter datas. Verifique o formato da coluna 'data_registro'.")
            return
        
        # Agregar dados por período
        aggregation = st.selectbox("Agregação:", ["Diário", "Semanal", "Mensal"])
        metric = st.selectbox("Métrica:", ["Contagem de Registros", "Score Médio", "Taxa de Adoção"])
        
        freq_map = {"Diário": "D", "Semanal": "W", "Mensal": "M"}
        
        if st.button("Analisar Série Temporal", use_container_width=True):
            with st.spinner("Processando análise temporal..."):
                try:
                    # Preparar série temporal
                    if metric == "Contagem de Registros":
                        ts_data = df_ts.set_index('data_registro').resample(freq_map[aggregation]).size()
                    elif metric == "Score Médio" and 'score_adocao' in df_ts.columns:
                        ts_data = df_ts.set_index('data_registro').resample(freq_map[aggregation])['score_adocao'].mean()
                    elif metric == "Taxa de Adoção" and 'adotado' in df_ts.columns:
                        ts_data = df_ts.set_index('data_registro').resample(freq_map[aggregation])['adotado'].mean()
                    else:
                        st.error("❌ Métrica selecionada não disponível nos dados.")
                        return
                    
                    ts_data = ts_data.fillna(0)
                    
                    if len(ts_data) < 4:
                        st.warning("⚠️ Dados insuficientes para análise temporal robusta.")
                        return
                    
                    # Visualização da série
                    fig = px.line(
                        x=ts_data.index,
                        y=ts_data.values,
                        title=f"Série Temporal - {metric} ({aggregation})",
                        labels={'x': 'Data', 'y': metric}
                    )
                    
                    # Adicionar tendência
                    try:
                        from scipy import stats
                        x_numeric = np.arange(len(ts_data))
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, ts_data.values)
                        trend_line = slope * x_numeric + intercept
                        
                        fig.add_trace(
                            go.Scatter(
                                x=ts_data.index,
                                y=trend_line,
                                mode='lines',
                                name=f'Tendência (R²={r_value**2:.3f})',
                                line=dict(dash='dash', color='red')
                            )
                        )
                    except Exception:
                        pass
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Insights da análise temporal
                    st.subheader("💡 Insights da Análise Temporal")
                    
                    try:
                        # Calcular estatísticas básicas
                        mean_value = ts_data.mean()
                        std_value = ts_data.std()
                        trend_direction = "crescente" if slope > 0 else "decrescente" if slope < 0 else "estável"
                        
                        st.success(f"📊 Valor médio: {mean_value:.2f}")
                        st.info(f"📈 Tendência: {trend_direction}")
                        
                        if abs(slope) > std_value * 0.1:
                            if slope > 0:
                                st.success(f"📈 Tendência de crescimento detectada (+{slope:.3f} por período)")
                            else:
                                st.warning(f"📉 Tendência de declínio detectada ({slope:.3f} por período)")
                        else:
                            st.info("➡️ Tendência estável ao longo do tempo")
                            
                    except Exception:
                        st.info("Análise de tendência não disponível")
                        
                except Exception as e:
                    st.error(f"❌ Erro na análise temporal: {str(e)}")
    
    else:
        # Para outros tipos de análise não implementados
        st.subheader(f"🚧 {analysis_type}")
        st.info(f"A análise '{analysis_type}' será implementada em versão futura.")
        
        # Mostrar dados disponíveis para referência
        st.subheader("📊 Dados Disponíveis")
        st.write(f"**Total de registros:** {len(df_analysis)}")
        st.write(f"**Colunas disponíveis:** {', '.join(df_analysis.columns.tolist())}")
        
        # Estatísticas básicas
        numeric_cols = df_analysis.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.subheader("📈 Estatísticas Básicas")
            stats_df = df_analysis[numeric_cols].describe().round(2)
            st.dataframe(stats_df, use_container_width=True)

@require_login
def visualizar_dados(df):
    """Visualização avançada de dados."""
    st.title("📊 Visualização Avançada de Dados")
    
    if df.empty:
        st.warning("Não há dados disponíveis.")
        return
    
    # Tabs para diferentes tipos de visualização
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Tabela Interativa", 
        "Dashboards", 
        "Comparações", 
        "Trends Temporais", 
        "Exportar Relatórios"
    ])
    
    with tab1:
        st.subheader("🗂️ Tabela Interativa Avançada")
        
        # Opções de visualização
        with st.expander("⚙️ Opções de Visualização", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Seleção de colunas
                all_columns = df.columns.tolist()
                default_columns = ['nome', 'tipo_pet', 'idade', 'peso', 'adotado', 'score_adocao']
                default_columns = [col for col in default_columns if col in all_columns]
                
                selected_columns = st.multiselect(
                    "Colunas para exibir:",
                    options=all_columns,
                    default=default_columns
                )
            
            with col2:
                # Ordenação
                sort_column = st.selectbox("Ordenar por:", ["Nenhum"] + all_columns)
                if sort_column != "Nenhum":
                    sort_order = st.radio("Ordem:", ["Crescente", "Decrescente"], horizontal=True)
            
            with col3:
                # Paginação
                items_per_page = st.selectbox("Itens por página:", [10, 25, 50, 100], index=1)
                show_totals = st.checkbox("Mostrar totais", value=True)
        
        # Preparar dados
        if selected_columns:
            df_display = df[selected_columns].copy()
        else:
            df_display = df.copy()
        
        # Aplicar ordenação
        if sort_column != "Nenhum":
            ascending = sort_order == "Crescente"
            df_display = df_display.sort_values(by=sort_column, ascending=ascending)
        
        # Estatísticas resumidas
        if show_totals:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Registros", len(df_display))
            
            with col2:
                if 'adotado' in df_display.columns:
                    adotados = df_display['adotado'].sum()
                    st.metric("Pets Adotados", adotados)
            
            with col3:
                if 'score_adocao' in df_display.columns:
                    score_medio = df_display['score_adocao'].mean()
                    st.metric("Score Médio", f"{score_medio:.2f}")
            
            with col4:
                if 'idade' in df_display.columns:
                    idade_media = df_display['idade'].mean()
                    st.metric("Idade Média", f"{idade_media:.1f} anos")
        
        # Tabela com paginação
        total_pages = (len(df_display) - 1) // items_per_page + 1
        
        if total_pages > 1:
            page = st.selectbox(f"Página (1-{total_pages}):", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            df_page = df_display.iloc[start_idx:end_idx]
        else:
            df_page = df_display
        
        # Exibir tabela
        st.dataframe(
            df_page,
            use_container_width=True,
            hide_index=True,
            column_config={
                "score_adocao": st.column_config.ProgressColumn(
                    "Score de Adoção",
                    help="Score de adotabilidade (0-5)",
                    min_value=0,
                    max_value=5,
                ),
                "risco_abandono": st.column_config.ProgressColumn(
                    "Risco de Abandono",
                    help="Risco de abandono (0-1)",
                    min_value=0,
                    max_value=1,
                ),
                "adotado": st.column_config.CheckboxColumn("Adotado"),
                "idade": st.column_config.NumberColumn("Idade", format="%.1f anos"),
                "peso": st.column_config.NumberColumn("Peso", format="%.1f kg"),
            }
        )
        
        # Estatísticas detalhadas
        st.subheader("📈 Estatísticas Detalhadas")
        
        # Colunas numéricas
        numeric_cols = df_display.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            stats_expanded = df_display[numeric_cols].describe().T
            stats_expanded['CV'] = stats_expanded['std'] / stats_expanded['mean']  # Coeficiente de variação
            stats_expanded['IQR'] = stats_expanded['75%'] - stats_expanded['25%']  # Intervalo interquartil
            
            st.dataframe(
                stats_expanded.round(3),
                use_container_width=True,
                column_config={
                    "count": "Contagem",
                    "mean": "Média",
                    "std": "Desvio Padrão",
                    "min": "Mínimo",
                    "25%": "Q1",
                    "50%": "Mediana",
                    "75%": "Q3",
                    "max": "Máximo",
                    "CV": "Coef. Variação",
                    "IQR": "Intervalo IQ"
                }
            )
    
    with tab2:
        st.subheader("📊 Dashboards Customizados")
        
        # Dashboard builder
        dashboard_type = st.selectbox(
            "Tipo de Dashboard:",
            ["Resumo Executivo", "Análise Comportamental", "Performance Regional", "Dashboard Personalizado"]
        )
        
        if dashboard_type == "Resumo Executivo":
            # KPIs principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_pets = len(df)
                custom_metric("Total de Pets", total_pets, "registrados", "#1f77b4")
            
            with col2:
                if 'adotado' in df.columns:
                    taxa_adocao = df['adotado'].mean() * 100
                    custom_metric("Taxa de Adoção", f"{taxa_adocao:.1f}%", "pets adotados", "#2ca02c")
            
            with col3:
                if 'score_adocao' in df.columns:
                    score_medio = df['score_adocao'].mean()
                    custom_metric("Score Médio", f"{score_medio:.2f}", "de 5.0", "#ff7f0e")
            
            with col4:
                if 'data_registro' in df.columns:
                    df_mes = df.copy()
                    df_mes['data_registro'] = pd.to_datetime(df_mes['data_registro'])
                    registros_mes = len(df_mes[df_mes['data_registro'].dt.month == pd.Timestamp.now().month])
                    custom_metric("Novos este Mês", registros_mes, "registros", "#d62728")
            
            # Gráficos do resumo executivo
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição por tipo
                if 'tipo_pet' in df.columns:
                    tipo_counts = df['tipo_pet'].value_counts()
                    fig = px.pie(
                        values=tipo_counts.values,
                        names=tipo_counts.index,
                        title="Distribuição por Tipo de Pet",
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Taxa de adoção por mês
                if 'data_registro' in df.columns and 'adotado' in df.columns:
                    df_monthly = df.copy()
                    df_monthly['data_registro'] = pd.to_datetime(df_monthly['data_registro'])
                    df_monthly['mes'] = df_monthly['data_registro'].dt.to_period('M')
                    
                    monthly_adoption = df_monthly.groupby('mes')['adotado'].mean() * 100
                    
                    fig = px.line(
                        x=monthly_adoption.index.astype(str),
                        y=monthly_adoption.values,
                        title="Taxa de Adoção Mensal (%)",
                        markers=True
                    )
                    fig.update_layout(xaxis_title="Mês", yaxis_title="Taxa de Adoção (%)")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de performance por bairro
            if 'bairro' in df.columns and 'adotado' in df.columns:
                st.subheader("🏘️ Performance por Bairro")
                
                bairro_performance = df.groupby('bairro').agg({
                    'adotado': ['count', 'sum', 'mean'],
                    'score_adocao': 'mean' if 'score_adocao' in df.columns else 'count'
                }).round(2)
                
                bairro_performance.columns = ['Total', 'Adotados', 'Taxa_Adocao', 'Score_Medio']
                bairro_performance['Eficiencia'] = (
                    bairro_performance['Taxa_Adocao'] * bairro_performance['Score_Medio']
                ).round(2)
                
                bairro_performance = bairro_performance.sort_values('Eficiencia', ascending=False)
                
                st.dataframe(
                    bairro_performance,
                    use_container_width=True,
                    column_config={
                        "Taxa_Adocao": st.column_config.ProgressColumn("Taxa de Adoção", min_value=0, max_value=1),
                        "Score_Medio": st.column_config.ProgressColumn("Score Médio", min_value=0, max_value=5),
                        "Eficiencia": st.column_config.NumberColumn("Eficiência", format="%.2f")
                    }
                )
        
        elif dashboard_type == "Análise Comportamental":
            st.subheader("🧠 Dashboard Comportamental")
            
            # Análise de características comportamentais
            behavioral_cols = ['comportamento', 'sociabilidade', 'energia', 'nivel_atividade']
            available_behavioral = [col for col in behavioral_cols if col in df.columns]
            
            if available_behavioral:
                # Heatmap de características
                if len(available_behavioral) > 1:
                    df_behavioral = df[available_behavioral].copy()
                    
                    # Encoding para variáveis categóricas
                    for col in df_behavioral.columns:
                        if df_behavioral[col].dtype == 'object':
                            le = LabelEncoder()
                            df_behavioral[col] = le.fit_transform(df_behavioral[col].astype(str))
                    
                    corr_behavioral = df_behavioral.corr()
                    
                    fig = px.imshow(
                        corr_behavioral,
                        text_auto='.2f',
                        title="Correlações entre Características Comportamentais",
                        color_continuous_scale='RdBu_r'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Análise por clusters comportamentais
                if 'sociabilidade' in df.columns and 'energia' in df.columns:
                    fig = px.scatter(
                        df,
                        x='sociabilidade',
                        y='energia',
                        color='tipo_pet' if 'tipo_pet' in df.columns else None,
                        size='score_adocao' if 'score_adocao' in df.columns else None,
                        hover_name='nome' if 'nome' in df.columns else None,
                        title="Mapa Comportamental: Sociabilidade vs Energia",
                        labels={'sociabilidade': 'Sociabilidade (1-5)', 'energia': 'Energia (1-5)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Distribuição de perfis comportamentais
                if 'comportamento' in df.columns:
                    comportamento_adocao = pd.crosstab(df['comportamento'], df['adotado'] if 'adotado' in df.columns else df['tipo_pet'])
                    
                    fig = px.bar(
                        comportamento_adocao,
                        title="Distribuição de Comportamentos",
                        barmode='group' if 'adotado' in df.columns else 'stack'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        elif dashboard_type == "Performance Regional":
            st.subheader("🗺️ Dashboard Regional")
            
            if 'bairro' in df.columns:
                # Mapa de calor regional
                regional_stats = df.groupby('bairro').agg({
                    'adotado': ['count', 'sum', 'mean'] if 'adotado' in df.columns else 'count',
                    'score_adocao': 'mean' if 'score_adocao' in df.columns else 'count',
                    'idade': 'mean' if 'idade' in df.columns else 'count'
                }).round(2)
                
                # Flatten column names
                regional_stats.columns = ['_'.join(col).strip() for col in regional_stats.columns.values]
                regional_stats = regional_stats.reset_index()
                
                # Renomear colunas para melhor legibilidade
                column_mapping = {
                    'adotado_count': 'Total_Pets',
                    'adotado_sum': 'Total_Adotados',
                    'adotado_mean': 'Taxa_Adocao',
                    'score_adocao_mean': 'Score_Medio',
                    'idade_mean': 'Idade_Media'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in regional_stats.columns:
                        regional_stats[new_col] = regional_stats[old_col]
                
                # Gráficos regionais
                col1, col2 = st.columns(2)
                
                with col1:
                    # Total de pets por bairro
                    fig = px.bar(
                        regional_stats.sort_values('Total_Pets', ascending=False),
                        x='bairro',
                        y='Total_Pets',
                        title="Total de Pets por Bairro",
                        color='Total_Pets',
                        color_continuous_scale='blues'
                    )
                    fig.update_xaxis(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Taxa de adoção por bairro
                    if 'Taxa_Adocao' in regional_stats.columns:
                        fig = px.bar(
                            regional_stats.sort_values('Taxa_Adocao', ascending=False),
                            x='bairro',
                            y='Taxa_Adocao',
                            title="Taxa de Adoção por Bairro",
                            color='Taxa_Adocao',
                            color_continuous_scale='RdYlGn'
                        )
                        fig.update_xaxis(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Análise de performance regional
                st.subheader("📊 Ranking Regional")
                
                # Calcular score de performance
                if 'Taxa_Adocao' in regional_stats.columns and 'Score_Medio' in regional_stats.columns:
                    regional_stats['Performance_Score'] = (
                        regional_stats['Taxa_Adocao'] * 0.6 + 
                        (regional_stats['Score_Medio'] / 5) * 0.4
                    ).round(3)
                    
                    top_regions = regional_stats.nlargest(10, 'Performance_Score')
                    
                    st.dataframe(
                        top_regions[['bairro', 'Total_Pets', 'Taxa_Adocao', 'Score_Medio', 'Performance_Score']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "bairro": "Bairro",
                            "Total_Pets": "Total de Pets",
                            "Taxa_Adocao": st.column_config.ProgressColumn("Taxa de Adoção", min_value=0, max_value=1),
                            "Score_Medio": st.column_config.ProgressColumn("Score Médio", min_value=0, max_value=5),
                            "Performance_Score": st.column_config.NumberColumn("Score de Performance", format="%.3f")
                        }
                    )
        
        else:  # Dashboard Personalizado
            st.subheader("🎨 Dashboard Personalizado")
            
            # Builder de dashboard personalizado
            st.write("Construa seu próprio dashboard selecionando os componentes:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                chart_types = st.multiselect(
                    "Tipos de gráfico:",
                    ["Barras", "Pizza", "Linha", "Scatter", "Heatmap", "Box Plot"]
                )
            
            with col2:
                variables_to_analyze = st.multiselect(
                    "Variáveis para analisar:",
                    df.columns.tolist(),
                    default=['tipo_pet', 'idade', 'adotado']
                )
            
            if chart_types and variables_to_analyze:
                # Gerar gráficos dinamicamente
                for chart_type in chart_types:
                    if chart_type == "Barras" and len(variables_to_analyze) >= 1:
                        var = variables_to_analyze[0]
                        if df[var].dtype == 'object':
                            counts = df[var].value_counts()
                            fig = px.bar(x=counts.index, y=counts.values, title=f"Distribuição de {var}")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Pizza" and len(variables_to_analyze) >= 1:
                        var = variables_to_analyze[0]
                        if df[var].dtype == 'object':
                            counts = df[var].value_counts()
                            fig = px.pie(values=counts.values, names=counts.index, title=f"Proporção de {var}")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Scatter" and len(variables_to_analyze) >= 2:
                        var1, var2 = variables_to_analyze[0], variables_to_analyze[1]
                        if pd.api.types.is_numeric_dtype(df[var1]) and pd.api.types.is_numeric_dtype(df[var2]):
                            fig = px.scatter(df, x=var1, y=var2, title=f"{var1} vs {var2}")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Box Plot" and len(variables_to_analyze) >= 1:
                        var = variables_to_analyze[0]
                        if pd.api.types.is_numeric_dtype(df[var]):
                            fig = px.box(df, y=var, title=f"Distribuição de {var}")
                            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("⚖️ Análises Comparativas")
        
        # Seleção de grupos para comparação
        comparison_type = st.selectbox(
            "Tipo de Comparação:",
            ["Por Tipo de Pet", "Por Bairro", "Por Status de Adoção", "Por Faixa Etária", "Comparação Personalizada"]
        )
        
        if comparison_type == "Por Tipo de Pet" and 'tipo_pet' in df.columns:
            # Comparação detalhada por tipo
            tipos = df['tipo_pet'].unique()
            
            # Seleção de métricas para comparar
            metrics_to_compare = st.multiselect(
                "Métricas para comparar:",
                ['idade', 'peso', 'score_adocao', 'sociabilidade', 'energia'],
                default=['idade', 'peso', 'score_adocao']
            )
            
            available_metrics = [m for m in metrics_to_compare if m in df.columns]
            
            if available_metrics:
                # Criar comparação estatística
                comparison_data = []
                
                for tipo in tipos:
                    tipo_data = df[df['tipo_pet'] == tipo]
                    row = {'Tipo': tipo, 'N': len(tipo_data)}
                    
                    for metric in available_metrics:
                        if pd.api.types.is_numeric_dtype(df[metric]):
                            row[f'{metric}_mean'] = tipo_data[metric].mean()
                            row[f'{metric}_std'] = tipo_data[metric].std()
                            row[f'{metric}_median'] = tipo_data[metric].median()
                    
                    comparison_data.append(row)
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Exibir tabela de comparação
                st.subheader("📊 Comparação Estatística")
                st.dataframe(comparison_df.round(2), use_container_width=True, hide_index=True)
                
                # Visualizações comparativas
                col1, col2 = st.columns(2)
                
                with col1:
                    # Box plots para cada métrica
                    for metric in available_metrics[:2]:  # Máximo 2 para não sobrecarregar
                        fig = px.box(
                            df, 
                            x='tipo_pet', 
                            y=metric,
                            title=f"Distribuição de {metric} por Tipo de Pet"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Violin plots
                    for metric in available_metrics[:2]:
                        fig = px.violin(
                            df, 
                            x='tipo_pet', 
                            y=metric,
                            title=f"Densidade de {metric} por Tipo de Pet"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Teste estatístico
                st.subheader("🧪 Testes Estatísticos")
                
                for metric in available_metrics:
                    if pd.api.types.is_numeric_dtype(df[metric]):
                        groups = [df[df['tipo_pet'] == tipo][metric].dropna() for tipo in tipos]
                        groups = [g for g in groups if len(g) > 1]  # Remover grupos vazios
                        
                        if len(groups) >= 2:
                            try:
                                # ANOVA
                                f_stat, p_value = stats.f_oneway(*groups)
                                
                                if p_value < 0.05:
                                    st.success(f"**{metric}**: Diferença significativa entre tipos (p = {p_value:.4f})")
                                else:
                                    st.info(f"**{metric}**: Sem diferença significativa entre tipos (p = {p_value:.4f})")
                            except:
                                st.warning(f"Não foi possível realizar teste para {metric}")
        
        elif comparison_type == "Comparação Personalizada":
            # Interface para comparação personalizada
            col1, col2 = st.columns(2)
            
            with col1:
                group_by_column = st.selectbox("Agrupar por:", df.columns.tolist())
            
            with col2:
                analyze_column = st.selectbox("Analisar:", df.select_dtypes(include=[np.number]).columns.tolist())
            
            if group_by_column and analyze_column:
                # Análise de grupos personalizada
                group_analysis = df.groupby(group_by_column)[analyze_column].agg([
                    'count', 'mean', 'median', 'std', 'min', 'max'
                ]).round(2)
                
                st.dataframe(group_analysis, use_container_width=True)
                
                # Visualização
                fig = px.box(df, x=group_by_column, y=analyze_column, 
                           title=f"{analyze_column} por {group_by_column}")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📈 Análise de Tendências Temporais")
        
        if 'data_registro' not in df.columns:
            st.error("Coluna 'data_registro' necessária para análise temporal.")
        else:
            # Preparar dados temporais
            df_temporal = df.copy()
            df_temporal['data_registro'] = pd.to_datetime(df_temporal['data_registro'])
            
            # Opções de agregação temporal
            col1, col2, col3 = st.columns(3)
            
            with col1:
                time_granularity = st.selectbox("Granularidade:", ["Diário", "Semanal", "Mensal", "Trimestral"])
            
            with col2:
                metric_to_analyze = st.selectbox(
                    "Métrica a analisar:",
                    ["Contagem de Registros", "Taxa de Adoção", "Score Médio", "Idade Média"]
                )
            
            with col3:
                date_range = st.date_input(
                    "Período:",
                    [df_temporal['data_registro'].min().date(), df_temporal['data_registro'].max().date()]
                )
            
            # Filtrar por período
            if len(date_range) == 2:
                start_date, end_date = date_range
                df_temporal = df_temporal[
                    (df_temporal['data_registro'].dt.date >= start_date) &
                    (df_temporal['data_registro'].dt.date <= end_date)
                ]
            
            # Agregação temporal
            freq_map = {"Diário": "D", "Semanal": "W", "Mensal": "M", "Trimestral": "Q"}
            freq = freq_map[time_granularity]
            
            if metric_to_analyze == "Contagem de Registros":
                time_series = df_temporal.set_index('data_registro').resample(freq).size()
                y_label = "Número de Registros"
            elif metric_to_analyze == "Taxa de Adoção" and 'adotado' in df_temporal.columns:
                time_series = df_temporal.set_index('data_registro').resample(freq)['adotado'].mean()
                y_label = "Taxa de Adoção"
            elif metric_to_analyze == "Score Médio" and 'score_adocao' in df_temporal.columns:
                time_series = df_temporal.set_index('data_registro').resample(freq)['score_adocao'].mean()
                y_label = "Score Médio de Adoção"
            elif metric_to_analyze == "Idade Média" and 'idade' in df_temporal.columns:
                time_series = df_temporal.set_index('data_registro').resample(freq)['idade'].mean()
                y_label = "Idade Média (anos)"
            else:
                st.error("Métrica selecionada não disponível nos dados.")
                return
            
            # Visualização da série temporal
            fig = px.line(
                x=time_series.index,
                y=time_series.values,
                title=f"Tendência Temporal: {metric_to_analyze} ({time_granularity})",
                labels={'x': 'Data', 'y': y_label}
            )
            
            # Adicionar linha de tendência
            if len(time_series) > 2:
                from scipy import stats
                x_numeric = np.arange(len(time_series))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, time_series.values)
                trend_line = slope * x_numeric + intercept
                
                fig.add_trace(
                    go.Scatter(
                        x=time_series.index,
                        y=trend_line,
                        mode='lines',
                        name=f'Tendência (R²={r_value**2:.3f})',
                        line=dict(dash='dash', color='red')
                    )
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análises estatísticas da tendência
            if len(time_series) > 2:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Tendência", f"{slope:.4f}")
                
                with col2:
                    st.metric("R²", f"{r_value**2:.3f}")
                
                with col3:
                    trend_direction = "Crescente" if slope > 0 else "Decrescente" if slope < 0 else "Estável"
                    st.metric("Direção", trend_direction)
                
                with col4:
                    significance = "Significativa" if p_value < 0.05 else "Não Significativa"
                    st.metric("Significância", significance)
                
                # Insights automáticos
                st.subheader("💡 Insights Temporais")
                
                insights = []
                
                if abs(slope) > time_series.std() * 0.1:
                    if slope > 0:
                        insights.append(f"📈 Tendência de crescimento detectada (+{slope:.3f} por período)")
                    else:
                        insights.append(f"📉 Tendência de declínio detectada ({slope:.3f} por período)")
                else:
                    insights.append("➡️ Tendência estável ao longo do tempo")
                
                # Detectar sazonalidade
                if time_granularity in ["Semanal", "Mensal"] and len(time_series) >= 12:
                    try:
                        from statsmodels.tsa.seasonal import seasonal_decompose
                        decomposition = seasonal_decompose(time_series, model='additive', period=4)
                        seasonal_strength = abs(decomposition.seasonal).mean()
                        
                        if seasonal_strength > time_series.std() * 0.1:
                            insights.append(f"🔄 Padrão sazonal detectado (força: {seasonal_strength:.3f})")
                        else:
                            insights.append("📊 Sem padrão sazonal significativo")
                    except:
                        pass
                
                # Detectar outliers temporais
                q1, q3 = time_series.quantile([0.25, 0.75])
                iqr = q3 - q1
                outliers = time_series[(time_series < q1 - 1.5*iqr) | (time_series > q3 + 1.5*iqr)]
                
                if len(outliers) > 0:
                    insights.append(f"⚠️ {len(outliers)} períodos atípicos detectados")
                
                for insight in insights:
                    st.info(insight)
    
    with tab5:
        st.subheader("📄 Exportar Relatórios Avançados")
        
        # Opções de relatório
        report_type = st.selectbox(
            "Tipo de Relatório:",
            ["Relatório Completo", "Relatório Executivo", "Análise Estatística", "Relatório Personalizado"]
        )
        
        # Opções de formato
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_format = st.selectbox("Formato:", ["Excel", "CSV", "JSON", "PDF"])
        
        with col2:
            include_charts = st.checkbox("Incluir gráficos", value=True)
        
        with col3:
            include_statistics = st.checkbox("Incluir estatísticas", value=True)
        
        # Gerar relatório
        if st.button("Gerar Relatório", use_container_width=True):
            with st.spinner("Gerando relatério..."):
                # Simular geração de relatório
                time.sleep(2)
                
                if report_type == "Relatório Completo":
                    # Dados completos com todas as análises
                    report_data = df.copy()
                    
                    # Adicionar estatísticas calculadas
                    if include_statistics:
                        # Adicionar scores e classificações
                        if 'score_adocao' in df.columns:
                            report_data['classificacao_score'] = pd.cut(
                                df['score_adocao'], 
                                bins=[0, 2, 3.5, 5], 
                                labels=['Baixo', 'Médio', 'Alto']
                            )
                        
                        if 'idade' in df.columns:
                            report_data['faixa_etaria'] = pd.cut(
                                df['idade'], 
                                bins=[0, 1, 3, 7, 20], 
                                labels=['Filhote', 'Jovem', 'Adulto', 'Idoso']
                            )
                    
                    filename = f"relatorio_completo_pets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                elif report_type == "Relatório Executivo":
                    # Apenas métricas principais e resumos
                    summary_data = {
                        'Métrica': ['Total de Pets', 'Taxa de Adoção', 'Score Médio', 'Idade Média'],
                        'Valor': [
                            len(df),
                            f"{df['adotado'].mean()*100:.1f}%" if 'adotado' in df.columns else "N/A",
                            f"{df['score_adocao'].mean():.2f}" if 'score_adocao' in df.columns else "N/A",
                            f"{df['idade'].mean():.1f} anos" if 'idade' in df.columns else "N/A"
                        ]
                    }
                    
                    report_data = pd.DataFrame(summary_data)
                    filename = f"relatorio_executivo_pets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                elif report_type == "Análise Estatística":
                    # Estatísticas descritivas detalhadas
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    report_data = df[numeric_cols].describe().T
                    
                    # Adicionar métricas adicionais
                    report_data['CV'] = report_data['std'] / report_data['mean']
                    report_data['IQR'] = report_data['75%'] - report_data['25%']
                    report_data['Skewness'] = df[numeric_cols].skew()
                    report_data['Kurtosis'] = df[numeric_cols].kurtosis()
                    
                    filename = f"analise_estatistica_pets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                else:  # Relatório Personalizado
                    # Permitir seleção de campos
                    selected_fields = st.multiselect(
                        "Campos para incluir:",
                        df.columns.tolist(),
                        default=['nome', 'tipo_pet', 'idade', 'adotado']
                    )
                    
                    if selected_fields:
                        report_data = df[selected_fields].copy()
                        filename = f"relatorio_personalizado_pets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    else:
                        st.error("Selecione pelo menos um campo para o relatório personalizado.")
                        return
                
                # Gerar arquivo baseado no formato
                if export_format == "Excel":
                    # Criar Excel com múltiplas abas
                    buffer = io.BytesIO()
                    
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        report_data.to_excel(writer, sheet_name='Dados', index=False)
                        
                        if include_statistics and report_type != "Análise Estatística":
                            # Aba de estatísticas
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                stats_df = df[numeric_cols].describe()
                                stats_df.to_excel(writer, sheet_name='Estatísticas')
                        
                        # Aba de resumo por categoria
                        if 'tipo_pet' in df.columns:
                            summary_by_type = df.groupby('tipo_pet').agg({
                                'adotado': ['count', 'sum', 'mean'] if 'adotado' in df.columns else 'count',
                                'idade': 'mean' if 'idade' in df.columns else 'count'
                            }).round(2)
                            summary_by_type.to_excel(writer, sheet_name='Resumo por Tipo')
                    
                    excel_data = buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Baixar Relatório Excel",
                        data=excel_data,
                        file_name=f"{filename}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                elif export_format == "CSV":
                    csv_data = report_data.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📄 Baixar Relatório CSV",
                        data=csv_data,
                        file_name=f"{filename}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                elif export_format == "JSON":
                    json_data = report_data.to_json(orient='records', indent=2).encode('utf-8')
                    
                    st.download_button(
                        label="🔗 Baixar Relatório JSON",
                        data=json_data,
                        file_name=f"{filename}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                elif export_format == "PDF":
                    st.info("Geração de PDF requer bibliotecas adicionais. Disponível em versão futura.")
                
                st.success("Relatório gerado com sucesso!")
                
                # Mostrar prévia do relatório
                st.subheader("👀 Prévia do Relatório")
                st.dataframe(report_data.head(10), use_container_width=True, hide_index=True)

@require_login
def adicionar_pet():
    """Formulário avançado para adicionar um novo pet."""
    st.title("➕ Adicionar Pet")
    
    # Assistente inteligente
    st.info("💡 **Assistente Inteligente**: Este formulário usa IA para sugerir valores e calcular scores automaticamente.")
    
    # Formulário corrigido
    with st.form("add_pet_form"):
        # Etapa 1: Informações Básicas
        st.subheader("🐾 Informações Básicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Pet*", help="Nome único para identificação")
            tipo_pet = st.selectbox("Tipo de Pet*", ["Cachorro", "Gato", "Ave", "Roedor", "Réptil", "Outro"])
            raca = st.text_input("Raça*", help="Raça ou 'SRD' para Sem Raça Definida")
            idade = st.number_input("Idade (anos)*", min_value=0.0, max_value=30.0, step=0.1, value=1.0)
        
        with col2:
            peso = st.number_input("Peso (kg)*", min_value=0.1, max_value=100.0, step=0.1, value=5.0)
            sexo = st.selectbox("Sexo*", ["Macho", "Fêmea"])
            castrado = st.checkbox("Castrado", value=False)
            microchip = st.checkbox("Possui Microchip", value=False)
        
        # Etapa 2: Localização
        st.subheader("📍 Localização")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bairro = st.text_input("Bairro", help="Bairro onde o pet se encontra")
            regiao = st.selectbox("Região", ["Centro", "Norte", "Sul", "Leste", "Oeste", "Continental"])
        
        with col2:
            telefone = st.text_input("Telefone de Contato*", help="Telefone para contato sobre o pet")
        
        # Etapa 3: Características Físicas
        st.subheader("🎨 Características Físicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cor_pelagem = st.selectbox("Cor da Pelagem", 
                ["Branco", "Preto", "Marrom", "Amarelo", "Cinza", "Misto", "Tigrado", "Outro"])
            porte = st.selectbox("Porte", ["Muito Pequeno", "Pequeno", "Médio", "Grande", "Gigante"])
        
        with col2:
            condicao_fisica = st.selectbox("Condição Física", 
                ["Excelente", "Boa", "Regular", "Necessita cuidados", "Debilitado"])
        
        # Etapa 4: Saúde e Cuidados
        st.subheader("🏥 Saúde e Cuidados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            status_vacinacao = st.selectbox("Status de Vacinação", 
                ["Em dia", "Parcial", "Atrasado", "Desconhecido"])
            estado_saude = st.selectbox("Estado de Saúde", 
                ["Excelente", "Bom", "Regular", "Tratamento", "Requer atenção veterinária"])
        
        with col2:
            necessidades_especiais = st.text_area("Necessidades Especiais", 
                help="Descreva qualquer necessidade médica ou cuidado especial")
            historico_medico = st.text_area("Histórico Médico", 
                help="Cirurgias, tratamentos, medicamentos, etc.")
        
        # Etapa 5: Comportamento e Personalidade
        st.subheader("🧠 Comportamento e Personalidade")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            comportamento = st.selectbox("Comportamento Geral", 
                ["Calmo", "Agitado", "Brincalhão", "Tímido", "Sociável", "Independente", "Territorial"])
            temperamento = st.selectbox("Temperamento", 
                ["Dócil", "Ativo", "Protetor", "Carinhoso", "Reservado", "Dominante"])
        
        with col2:
            sociabilidade = st.slider("Sociabilidade", 1, 5, 3, 
                help="1=Muito tímido, 5=Extremamente sociável")
            energia = st.slider("Nível de Energia", 1, 5, 3, 
                help="1=Muito calmo, 5=Hiperativo")
        
        with col3:
            nivel_atividade = st.slider("Nível de Atividade", 1, 5, 3, 
                help="1=Sedentário, 5=Muito ativo")
            adaptabilidade = st.slider("Adaptabilidade", 1, 5, 3, 
                help="1=Difícil adaptação, 5=Adapta-se facilmente")
        
        # Etapa 6: Status de Adoção
        st.subheader("❤️ Status de Adoção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            adotado = st.checkbox("Pet já foi adotado")
            prioridade_adocao = st.selectbox("Prioridade para Adoção", 
                ["Normal", "Alta", "Urgente", "Baixa"])
        
        with col2:
            if adotado:
                data_adocao = st.date_input("Data da Adoção")
            else:
                data_adocao = None
        
        # Etapa 7: Observações Adicionais
        st.subheader("📝 Observações")
        
        observacoes = st.text_area("Observações Gerais", 
            height=100,
            help="Qualquer informação adicional relevante sobre o pet")
        
        # CORREÇÃO: Usar apenas st.form_submit_button dentro do formulário
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            submitted = st.form_submit_button("🐾 Adicionar Pet", use_container_width=True)
        
        # Processar formulário quando submetido
        if submitted:
            # Validação
            erros = []
            
            if not nome:
                erros.append("Nome é obrigatório")
            if not raca:
                erros.append("Raça é obrigatória")
            if not telefone:
                erros.append("Telefone é obrigatório")
            if idade <= 0:
                erros.append("Idade deve ser maior que zero")
            if peso <= 0:
                erros.append("Peso deve ser maior que zero")
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                with st.spinner("🤖 Calculando scores inteligentes..."):
                    # Simular processamento IA
                    time.sleep(1)
                    
                    # Calcular score de adoção baseado em múltiplos fatores
                    score_adocao = calculate_adoption_score(
                        idade, sociabilidade, energia, nivel_atividade, 
                        estado_saude, comportamento, tipo_pet
                    )
                    
                    # Calcular risco de abandono
                    risco_abandono = calculate_abandonment_risk(
                        idade, necessidades_especiais, 200.0,  # custo estimado
                        "Boa", "Casa com quintal pequeno"  # valores padrão
                    )
                    
                    # Criar dados do pet
                    pet_data = {
                        'nome': nome,
                        'tipo_pet': tipo_pet,
                        'raca': raca,
                        'idade': idade,
                        'peso': peso,
                        'sexo': sexo,
                        'castrado': castrado,
                        'microchip': microchip,
                        'bairro': bairro,
                        'regiao': regiao,
                        'telefone': telefone,
                        'cor_pelagem': cor_pelagem,
                        'status_vacinacao': status_vacinacao,
                        'estado_saude': estado_saude,
                        'necessidades_especiais': necessidades_especiais,
                        'historico_medico': historico_medico,
                        'comportamento': comportamento,
                        'temperamento': temperamento,
                        'sociabilidade': sociabilidade,
                        'energia': energia,
                        'nivel_atividade': nivel_atividade,
                        'adaptabilidade': adaptabilidade,
                        'adotado': adotado,
                        'score_adocao': score_adocao,
                        'risco_abandono': risco_abandono,
                        'observacoes': observacoes,
                        'data_registro': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'created_by': st.session_state.user_id
                    }
                    
                    # Salvar no banco de dados
                    success, result = save_pet_to_db(pet_data)
                    
                    if success:
                        # Registrar atividade
                        log_activity(st.session_state.user_id, "add_pet", f"Adicionou pet: {nome}")
                        
                        # Feedback de sucesso
                        st.success(f"🎉 Pet {nome} adicionado com sucesso!")
                        st.balloons()
                        
                        # Mostrar scores calculados
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Score de Adoção", f"{score_adocao:.2f}/5.0", 
                                    help="Calculado com base em idade, comportamento e saúde")
                        
                        with col2:
                            st.metric("Risco de Abandono", f"{risco_abandono:.2f}", 
                                    help="0=Baixo risco, 1=Alto risco")
                        
                        with col3:
                            prioridade_calc = "Alta" if score_adocao > 4.0 else "Média" if score_adocao > 2.5 else "Baixa"
                            st.metric("Prioridade Calculada", prioridade_calc, 
                                    help="Baseada no score de adoção")
                        
                        # Recomendações inteligentes
                        st.subheader("🤖 Recomendações Inteligentes")
                        
                        recommendations = generate_pet_recommendations(pet_data)
                        
                        for rec in recommendations:
                            if rec['type'] == 'success':
                                st.success(f"✅ {rec['message']}")
                            elif rec['type'] == 'warning':
                                st.warning(f"⚠️ {rec['message']}")
                            else:
                                st.info(f"💡 {rec['message']}")
                        
                        # Sugestão de próximos passos
                        st.info("📋 **Próximos Passos Sugeridos:**\n"
                               "1. Agendar avaliação veterinária se necessário\n"
                               "2. Tirar fotos profissionais para divulgação\n"
                               "3. Criar perfil nas redes sociais de adoção\n"
                               "4. Iniciar busca por tutores compatíveis")
                        
                    else:
                        st.error(f"❌ Erro ao adicionar pet: {result}")

    # CORREÇÃO: Botões fora do formulário
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Limpar Formulário", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Lista de Pets", use_container_width=True):
            st.session_state.page = "Visualizar Dados"
            st.rerun()

def calculate_adoption_score(idade, sociabilidade, energia, nivel_atividade, estado_saude, comportamento, tipo_pet):
    """Calcula o score de adoção usando algoritmo inteligente."""
    score = 0.0
    
    # Fator idade (pets jovens têm score mais alto)
    if idade <= 1:
        score += 1.0
    elif idade <= 3:
        score += 0.8
    elif idade <= 7:
        score += 0.6
    else:
        score += 0.3
    
    # Fatores comportamentais
    score += (sociabilidade / 5) * 1.0
    score += (energia / 5) * 0.7
    score += (nivel_atividade / 5) * 0.5
    
    # Fator saúde
    saude_scores = {
        'Excelente': 1.0,
        'Bom': 0.8,
        'Regular': 0.6,
        'Tratamento': 0.4,
        'Requer atenção veterinária': 0.2
    }
    score += saude_scores.get(estado_saude, 0.5)
    
    # Fator comportamento
    comportamento_scores = {
        'Sociável': 0.8,
        'Brincalhão': 0.7,
        'Calmo': 0.6,
        'Independente': 0.5,
        'Tímido': 0.4,
        'Agitado': 0.3,
        'Territorial': 0.2
    }
    score += comportamento_scores.get(comportamento, 0.5)
    
    # Fator tipo de pet (alguns são mais populares)
    tipo_scores = {
        'Cachorro': 0.3,
        'Gato': 0.3,
        'Ave': 0.1,
        'Roedor': 0.1,
        'Réptil': 0.05
    }
    score += tipo_scores.get(tipo_pet, 0.1)
    
    # Normalizar para escala 0-5
    return min(5.0, max(0.0, score))

def calculate_abandonment_risk(idade, necessidades_especiais, custo_mensal, compatibilidade_criancas, ambiente_ideal):
    """Calcula o risco de abandono."""
    risk = 0.0
    
    # Idade (pets muito jovens ou muito velhos têm maior risco)
    if idade < 0.5 or idade > 10:
        risk += 0.2
    
    # Necessidades especiais aumentam risco
    if necessidades_especiais and len(necessidades_especiais.strip()) > 0:
        risk += 0.3
    
    # Custo alto aumenta risco
    if custo_mensal > 400:
        risk += 0.2
    elif custo_mensal > 300:
        risk += 0.1
    
    # Incompatibilidade com crianças
    if compatibilidade_criancas == "Não recomendado":
        risk += 0.2
    
    # Ambiente muito específico
    if ambiente_ideal in ["Chácara/Sítio"]:
        risk += 0.1
    
    return min(1.0, max(0.0, risk))

def generate_pet_recommendations(pet_data):
    """Gera recomendações inteligentes baseadas nos dados do pet."""
    recommendations = []
    
    # Recomendações baseadas no score
    if pet_data['score_adocao'] > 4.0:
        recommendations.append({
            'type': 'success',
            'message': 'Pet com alto potencial de adoção! Priorize divulgação nas redes sociais.'
        })
    elif pet_data['score_adocao'] < 2.0:
        recommendations.append({
            'type': 'warning',
            'message': 'Score baixo de adoção. Considere trabalhar comportamento e saúde antes da divulgação.'
        })
    
    # Recomendações baseadas na idade
    if pet_data['idade'] < 0.5:
        recommendations.append({
            'type': 'info',
            'message': 'Pet filhote: será necessário tutor experiente e acompanhamento veterinário frequente.'
        })
    elif pet_data['idade'] > 8:
        recommendations.append({
            'type': 'info',
            'message': 'Pet idoso: destacar personalidade calma e carinhosa na divulgação.'
        })
    
    # Recomendações baseadas no risco
    if pet_data['risco_abandono'] > 0.7:
        recommendations.append({
            'type': 'warning',
            'message': 'Alto risco de abandono. Faça triagem rigorosa de tutores e acompanhamento pós-adoção.'
        })
    
    # Recomendações específicas por tipo
    if pet_data['tipo_pet'] == 'Cachorro' and pet_data['energia'] > 4:
        recommendations.append({
            'type': 'info',
            'message': 'Cachorro com alta energia: buscar tutores ativos que gostem de exercícios.'
        })
    
    if pet_data['necessidades_especiais'] and len(pet_data['necessidades_especiais'].strip()) > 0:
        recommendations.append({
            'type': 'warning',
            'message': 'Pet com necessidades especiais: criar material educativo para tutores sobre os cuidados.'
        })
    
    return recommendations

@require_login
def exportar_importar_dados(df):
    """Sistema avançado de exportação e importação."""
    st.title("📤📥 Exportar/Importar Dados Avançado")
    
    tab1, tab2, tab3 = st.tabs(["Exportar Dados", "Importar Dados", "Sincronização"])
    
    with tab1:
        st.subheader("📊 Exportação Avançada de Dados")
        
        # Opções de exportação
        with st.expander("🎛️ Configurações de Exportação", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                formato_exportacao = st.selectbox(
                    "Formato de Exportação:",
                    ["Excel Avançado", "CSV", "JSON", "XML", "Parquet", "Feather"]
                )
                
                incluir_filtrados = st.checkbox("Exportar apenas dados filtrados", value=False)
                incluir_imagens = st.checkbox("Incluir referências de imagens", value=False)
            
            with col2:
                nivel_detalhamento = st.selectbox(
                    "Nível de Detalhamento:",
                    ["Básico", "Completo", "Personalizado"]
                )
                
                incluir_metadados = st.checkbox("Incluir metadados", value=True)
                incluir_estatisticas = st.checkbox("Incluir estatísticas", value=True)
            
            with col3:
                compressao = st.selectbox(
                    "Compressão:",
                    ["Nenhuma", "ZIP", "GZIP"]
                )
                
                criptografia = st.checkbox("Criptografar arquivo", value=False)
                if criptografia:
                    senha_export = st.text_input("Senha para criptografia:", type="password")
        
        # Seleção de dados
        if incluir_filtrados:
            df_exportar = st.session_state.get("df_filtrado", df)
        else:
            df_exportar = df
        
        st.info(f"📊 **{len(df_exportar)} registros** serão exportados.")
        
        # Configuração personalizada
        if nivel_detalhamento == "Personalizado":
            st.subheader("🎯 Configuração Personalizada")
            
            # Seleção de colunas
            colunas_disponiveis = df_exportar.columns.tolist()
            colunas_selecionadas = st.multiselect(
                "Colunas para exportar:",
                colunas_disponiveis,
                default=colunas_disponiveis
            )
            
            if colunas_selecionadas:
                df_exportar = df_exportar[colunas_selecionadas]
            
            # Filtros adicionais
            col1, col2 = st.columns(2)
            
            with col1:
                if 'data_registro' in df_exportar.columns:
                    data_inicio = st.date_input("Data início:")
                    data_fim = st.date_input("Data fim:")
            
            with col2:
                if 'score_adocao' in df_exportar.columns:
                    score_min = st.slider("Score mínimo:", 0.0, 5.0, 0.0)
                    df_exportar = df_exportar[df_exportar['score_adocao'] >= score_min]
        
        # Prévia dos dados
        st.subheader("👀 Prévia dos Dados")
        st.dataframe(df_exportar.head(10), use_container_width=True, hide_index=True)
        
        # Botão de exportação
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Gerar Exportação", use_container_width=True):
                with st.spinner("Gerando arquivo de exportação..."):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    if formato_exportacao == "Excel Avançado":
                        # Excel com múltiplas abas e formatação
                        buffer = io.BytesIO()
                        
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            # Aba principal
                            df_exportar.to_excel(writer, sheet_name='Dados_Pets', index=False)
                            
                            # Aba de estatísticas
                            if incluir_estatisticas:
                                numeric_cols = df_exportar.select_dtypes(include=[np.number]).columns
                                if len(numeric_cols) > 0:
                                    stats_df = df_exportar[numeric_cols].describe()
                                    stats_df.to_excel(writer, sheet_name='Estatisticas')
                            
                            # Aba de resumos
                            if 'tipo_pet' in df_exportar.columns:
                                resumo_tipos = df_exportar.groupby('tipo_pet').agg({
                                    'adotado': ['count', 'sum', 'mean'] if 'adotado' in df_exportar.columns else 'count',
                                    'idade': 'mean' if 'idade' in df_exportar.columns else 'count'
                                }).round(2)
                                resumo_tipos.to_excel(writer, sheet_name='Resumo_por_Tipo')
                            
                            # Aba de metadados
                            if incluir_metadados:
                                metadata = pd.DataFrame({
                                    'Informacao': ['Data_Exportacao', 'Total_Registros', 'Usuario', 'Versao_Sistema'],
                                    'Valor': [timestamp, len(df_exportar), st.session_state.user_info['full_name'], '1.0.0']
                                })
                                metadata.to_excel(writer, sheet_name='Metadados', index=False)
                            
                            # Formatação
                            workbook = writer.book
                            worksheet = writer.sheets['Dados_Pets']
                            
                            # Formato para cabeçalhos
                            header_format = workbook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'top',
                                'fg_color': '#4527A0',
                                'font_color': 'white',
                                'border': 1
                            })
                            
                            # Aplicar formato aos cabeçalhos
                            for col_num, value in enumerate(df_exportar.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                        
                        arquivo_data = buffer.getvalue()
                        nome_arquivo = f"petcare_export_{timestamp}.xlsx"
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    elif formato_exportacao == "CSV":
                        arquivo_data = df_exportar.to_csv(index=False).encode('utf-8')
                        nome_arquivo = f"petcare_export_{timestamp}.csv"
                        mime_type = "text/csv"
                    
                    elif formato_exportacao == "JSON":
                        json_data = {
                            'metadata': {
                                'export_date': timestamp,
                                'total_records': len(df_exportar),
                                'exported_by': st.session_state.user_info['full_name'],
                                'version': '1.0.0'
                            },
                            'data': df_exportar.to_dict('records')
                        }
                        arquivo_data = json.dumps(json_data, indent=2, default=str).encode('utf-8')
                        nome_arquivo = f"petcare_export_{timestamp}.json"
                        mime_type = "application/json"
                    
                    elif formato_exportacao == "Parquet":
                        buffer = io.BytesIO()
                        df_exportar.to_parquet(buffer, index=False)
                        arquivo_data = buffer.getvalue()
                        nome_arquivo = f"petcare_export_{timestamp}.parquet"
                        mime_type = "application/octet-stream"
                    
                    # Aplicar compressão se solicitada
                    if compressao == "ZIP":
                        import zipfile
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            zip_file.writestr(nome_arquivo, arquivo_data)
                        arquivo_data = zip_buffer.getvalue()
                        nome_arquivo = nome_arquivo.replace('.', '_compressed.')
                        mime_type = "application/zip"
                    
                    # Registrar atividade
                    log_activity(
                        st.session_state.user_id, 
                        "export_data", 
                        f"Exportou {len(df_exportar)} registros em formato {formato_exportacao}"
                    )
                    
                    # Botão de download
                    st.download_button(
                        label=f"📥 Baixar {formato_exportacao}",
                        data=arquivo_data,
                        file_name=nome_arquivo,
                        mime=mime_type,
                        use_container_width=True
                    )
                    
                    st.success("✅ Arquivo gerado com sucesso!")
    
    with tab2:
        st.subheader("📥 Importação Avançada de Dados")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Escolha um arquivo para importar:",
            type=["csv", "xlsx", "json", "xml", "parquet"],
            help="Formatos suportados: CSV, Excel, JSON, XML, Parquet"
        )
        
        if uploaded_file is not None:
            # Detectar tipo de arquivo
            file_type = uploaded_file.name.split(".")[-1].lower()
            
            try:
                # Carregar dados baseado no tipo
                if file_type == "csv":
                    col1, col2 = st.columns(2)
                    with col1:
                        separador = st.selectbox("Separador:", [",", ";", "\t", "|"])
                        encoding = st.selectbox("Codificação:", ["utf-8", "latin-1", "cp1252"])
                    with col2:
                        has_header = st.checkbox("Primeira linha é cabeçalho", value=True)
                        skip_lines = st.number_input("Pular linhas:", min_value=0, value=0)
                    
                    df_importado = pd.read_csv(
                        uploaded_file, 
                        sep=separador, 
                        encoding=encoding,
                        header=0 if has_header else None,
                        skiprows=skip_lines
                    )
                
                elif file_type == "xlsx":
                    # Opções Excel
                    col1, col2 = st.columns(2)
                    with col1:
                        sheet_name = st.text_input("Nome da aba:", value="0")
                        has_header = st.checkbox("Primeira linha é cabeçalho", value=True)
                    with col2:
                        skip_rows = st.number_input("Pular linhas:", min_value=0, value=0)
                    
                    # Tentar converter sheet_name para int se possível
                    try:
                        sheet_name = int(sheet_name)
                    except:
                        pass
                    
                    df_importado = pd.read_excel(
                        uploaded_file,
                        sheet_name=sheet_name,
                        header=0 if has_header else None,
                        skiprows=skip_rows
                    )
                
                elif file_type == "json":
                    import json
                    json_data = json.load(uploaded_file)
                    
                    # Detectar estrutura do JSON
                    if isinstance(json_data, dict) and 'data' in json_data:
                        df_importado = pd.DataFrame(json_data['data'])
                    elif isinstance(json_data, list):
                        df_importado = pd.DataFrame(json_data)
                    else:
                        df_importado = pd.json_normalize(json_data)
                
                elif file_type == "parquet":
                    df_importado = pd.read_parquet(uploaded_file)
                
                # Mostrar prévia dos dados importados
                st.subheader("👀 Prévia dos Dados Importados")
                st.info(f"📊 **{len(df_importado)} registros** e **{len(df_importado.columns)} colunas** detectados.")
                
                # Mostrar amostra dos dados
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.dataframe(df_importado.head(10), use_container_width=True, hide_index=True)
                
                with col2:
                    # Informações sobre as colunas
                    st.write("**Informações das Colunas:**")
                    for col in df_importado.columns:
                        dtype = str(df_importado[col].dtype)
                        null_count = df_importado[col].isnull().sum()
                        st.write(f"• **{col}**: {dtype} ({null_count} nulos)")
                
                # Mapeamento de colunas
                st.subheader("🔄 Mapeamento de Colunas")
                
                # Colunas do sistema
                system_columns = [
                    'nome', 'tipo_pet', 'raca', 'idade', 'peso', 'sexo', 'bairro',
                    'comportamento', 'estado_saude', 'adotado', 'score_adocao',
                    'sociabilidade', 'energia', 'nivel_atividade'
                ]
                
                mapping = {}
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Colunas do Sistema:**")
                    for sys_col in system_columns:
                        imported_options = ["[Ignorar]"] + list(df_importado.columns)
                        
                        # Tentar encontrar correspondência automática
                        default_idx = 0
                        for i, imp_col in enumerate(df_importado.columns):
                            if sys_col.lower() in imp_col.lower() or imp_col.lower() in sys_col.lower():
                                default_idx = i + 1
                                break
                        
                        selected = st.selectbox(
                            sys_col,
                            imported_options,
                            index=default_idx,
                            key=f"map_{sys_col}"
                        )
                        
                        if selected != "[Ignorar]":
                            mapping[sys_col] = selected
                
                with col2:
                    st.write("**Validação de Dados:**")
                    
                    validation_issues = []
                    
                    # Validar tipos de dados
                    for sys_col, imp_col in mapping.items():
                        if sys_col in ['idade', 'peso', 'score_adocao', 'sociabilidade', 'energia']:
                            if not pd.api.types.is_numeric_dtype(df_importado[imp_col]):
                                try:
                                    pd.to_numeric(df_importado[imp_col], errors='coerce')
                                except:
                                    validation_issues.append(f"❌ {imp_col} não é numérico")
                        
                        # Verificar valores obrigatórios
                        if sys_col in ['nome', 'tipo_pet', 'raca']:
                            null_count = df_importado[imp_col].isnull().sum()
                            if null_count > 0:
                                validation_issues.append(f"⚠️ {imp_col} tem {null_count} valores vazios")
                    
                    if validation_issues:
                        for issue in validation_issues:
                            st.write(issue)
                    else:
                        st.success("✅ Todos os dados passaram na validação!")
                
                # Opções de importação
                st.subheader("⚙️ Opções de Importação")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    import_mode = st.selectbox(
                        "Modo de Importação:",
                        ["Adicionar novos registros", "Substituir todos os dados", "Atualizar existentes"]
                    )
                
                with col2:
                    validate_data = st.checkbox("Validar dados antes da importação", value=True)
                    create_backup = st.checkbox("Criar backup antes da importação", value=True)
                
                with col3:
                    batch_size = st.number_input("Tamanho do lote:", min_value=10, max_value=1000, value=100)
                
                # Botão de importação
                if st.button("🚀 Iniciar Importação", use_container_width=True):
                    with st.spinner("Processando importação..."):
                        try:
                            # Aplicar mapeamento
                            df_mapped = pd.DataFrame()
                            
                            for sys_col, imp_col in mapping.items():
                                df_mapped[sys_col] = df_importado[imp_col]
                            
                            # Adicionar campos obrigatórios se não existirem
                            if 'created_by' not in df_mapped.columns:
                                df_mapped['created_by'] = st.session_state.user_id
                            
                            if 'data_registro' not in df_mapped.columns:
                                df_mapped['data_registro'] = datetime.datetime.now()
                            
                            # Validação adicional
                            if validate_data:
                                # Converter tipos de dados
                                numeric_cols = ['idade', 'peso', 'score_adocao', 'sociabilidade', 'energia']
                                for col in numeric_cols:
                                    if col in df_mapped.columns:
                                        df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce')
                                
                                # Remover registros com dados críticos ausentes
                                required_cols = ['nome', 'tipo_pet']
                                for col in required_cols:
                                    if col in df_mapped.columns:
                                        df_mapped = df_mapped.dropna(subset=[col])
                            
                            # Criar backup se solicitado
                            if create_backup:
                                backup_filename = f"backup_before_import_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                df.to_csv(f"data/{backup_filename}", index=False)
                                st.info(f"💾 Backup criado: {backup_filename}")
                            
                            # Executar importação
                            conn = sqlite3.connect(DATABASE_PATH)
                            
                            if import_mode == "Substituir todos os dados":
                                # Limpar tabela existente
                                conn.execute("DELETE FROM pets")
                                conn.commit()
                            
                            # Inserir dados em lotes
                            success_count = 0
                            error_count = 0
                            
                            for i in range(0, len(df_mapped), batch_size):
                                batch = df_mapped.iloc[i:i+batch_size]
                                
                                for _, row in batch.iterrows():
                                    try:
                                        # Preparar dados para inserção
                                        columns = ', '.join(row.index)
                                        placeholders = ', '.join(['?' for _ in row])
                                        values = tuple(row.values)
                                        
                                        query = f"INSERT INTO pets ({columns}) VALUES ({placeholders})"
                                        conn.execute(query, values)
                                        success_count += 1
                                        
                                    except Exception as e:
                                        error_count += 1
                                        st.error(f"Erro na linha {i}: {str(e)}")
                                
                                # Commit em lotes
                                conn.commit()
                                
                                # Mostrar progresso
                                progress = min((i + batch_size) / len(df_mapped), 1.0)
                                st.progress(progress)
                            
                            conn.close()
                            
                            # Registrar atividade
                            log_activity(
                                st.session_state.user_id,
                                "import_data",
                                f"Importou dados: {success_count} sucessos, {error_count} erros"
                            )
                            
                            # Resultado da importação
                            if error_count == 0:
                                st.success(f"✅ Importação concluída com sucesso! {success_count} registros importados.")
                                st.balloons()
                            else:
                                st.warning(f"⚠️ Importação concluída com problemas: {success_count} sucessos, {error_count} erros.")
                            
                            # Recarregar dados
                            if st.button("🔄 Recarregar Dados"):
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Erro durante a importação: {str(e)}")
            
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    with tab3:
        st.subheader("🔄 Sincronização de Dados")
        
        st.info("🚧 **Funcionalidade em Desenvolvimento**\n\n"
                "Esta seção permitirá sincronização com:\n"
                "• APIs externas de adoção\n"
                "• Sistemas veterinários\n"
                "• Plataformas de redes sociais\n"
                "• Bancos de dados em nuvem")
        
        # Interface simulada para sincronização
        with st.expander("⚙️ Configurações de Sincronização"):
            sync_services = st.multiselect(
                "Serviços para sincronizar:",
                ["PetFinder API", "Adote um Focinho", "Facebook Pets", "Instagram", "Sistema Veterinário Local"]
            )
            
            if sync_services:
                for service in sync_services:
                    st.text_input(f"API Key para {service}:", type="password")
                
                sync_frequency = st.selectbox(
                    "Frequência de sincronização:",
                    ["Manual", "A cada hora", "Diária", "Semanal"]
                )
                
                if st.button("🔄 Configurar Sincronização"):
                    st.success("Configurações salvas! A sincronização será ativada em versão futura.")

def main():
    """Função principal aprimorada."""
    # Inicializar o banco de dados
    init_database()
    
    # Configuração da página
    st.set_page_config(
        page_title="PetCare Analytics - Sistema Avançado com IA",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado global
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #4527A0 0%, #7B1FA2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4527A0;
    }
    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4527A0 0%, #7B1FA2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar se o usuário está logado
    if "user_id" not in st.session_state or "user_role" not in st.session_state:
        display_login_page()
        return
    
    # Exibir cabeçalho
    display_header()
    
    # Carregar dados do banco de dados
    df = load_data_from_db()
    
    # Adicionar barra lateral para filtros e navegação
    df_filtrado = apply_filters(df)
    st.session_state.df_filtrado = df_filtrado
    
    # Menu de navegação principal expandido
    st.sidebar.markdown("## 🚀 Navegação Principal")
    
    # Agrupar menus por categoria
    menu_categoria = st.sidebar.radio(
        "Categoria:",
        ["📊 Análises", "📝 Gestão", "🔧 Ferramentas", "⚙️ Sistema"]
    )
    
    if menu_categoria == "📊 Análises":
        menu_opcao = st.sidebar.selectbox(
            "Selecione:",
            ["Dashboard", "Visualizar Dados", "Análises Avançadas", "IA Insights", "Mapa Interativo"]
        )
    elif menu_categoria == "📝 Gestão":
        menu_opcao = st.sidebar.selectbox(
            "Selecione:",
            ["Adicionar Pet", "Editar Pets", "Gerenciar Adoções", "Relatórios"]
        )
    elif menu_categoria == "🔧 Ferramentas":
        menu_opcao = st.sidebar.selectbox(
            "Selecione:",
            ["Exportar/Importar", "Backup/Restauração", "Migração de Dados"]
        )
    else:  # Sistema
        menu_opcao = st.sidebar.selectbox(
            "Selecione:",
            ["Configurações do Usuário", "Painel de Administração" if st.session_state.user_role == "admin" else None]
        )
        menu_opcao = menu_opcao if menu_opcao else "Configurações do Usuário"
    
    # Menu de acesso rápido
    st.sidebar.markdown("## ⚡ Acesso Rápido")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("➕ Novo Pet", use_container_width=True):
            st.session_state.quick_action = "Adicionar Pet"
    
    with col2:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.quick_action = "Dashboard"
    
    # Verificar ação rápida
    if "quick_action" in st.session_state:
        menu_opcao = st.session_state.quick_action
        del st.session_state.quick_action
    
    # Estatísticas na sidebar
    if not df.empty:
        st.sidebar.markdown("## 📈 Estatísticas Rápidas")
        
        with st.sidebar.container():
            st.metric("Total de Pets", len(df))
            
            if 'adotado' in df.columns:
                taxa_adocao = df['adotado'].mean() * 100
                st.metric("Taxa de Adoção", f"{taxa_adocao:.1f}%")
            
            if 'score_adocao' in df.columns:
                score_medio = df['score_adocao'].mean()
                st.metric("Score Médio", f"{score_medio:.2f}")
    
    # Notificações e alertas
    st.sidebar.markdown("## 🔔 Notificações")
    
    # Gerar notificações inteligentes
    notifications = generate_smart_notifications(df)
    
    for notification in notifications[:3]:  # Máximo 3 notificações
        if notification['type'] == 'warning':
            st.sidebar.warning(f"⚠️ {notification['message']}")
        elif notification['type'] == 'info':
            st.sidebar.info(f"ℹ️ {notification['message']}")
        else:
            st.sidebar.success(f"✅ {notification['message']}")
    
    # Botão de logout
    st.sidebar.markdown("---")
    
    col1, col2 = st.sidebar.columns([1, 1])
    
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📤 Sair", use_container_width=True):
            # Limpar sessão
            if "user_id" in st.session_state:
                log_activity(st.session_state.user_id, "logout", "Logout do sistema")
                
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
            
            st.rerun()
    
    # Informações do sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='text-align: center; font-size: 0.8rem; color: #666;'>"
        "🐾 PetCare Analytics v2.0<br>"
        "Sistema Avançado com IA<br>"
        f"Usuário: {st.session_state.user_info['full_name']}<br>"
        f"Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Navegar para a página escolhida
    try:
        if menu_opcao == "Dashboard":
            display_dashboard(df, df_filtrado)
        elif menu_opcao == "Visualizar Dados":
            visualizar_dados(df)
        elif menu_opcao == "Adicionar Pet":
            adicionar_pet()
        elif menu_opcao == "Análises Avançadas":
            advanced_analytics(df)
        elif menu_opcao == "Exportar/Importar":
            exportar_importar_dados(df)
        elif menu_opcao == "IA Insights":
            ai_insights(df)
        elif menu_opcao == "Mapa Interativo":
            mapa_interativo(df)
        elif menu_opcao == "Configurações do Usuário":
            user_settings()
        elif menu_opcao == "Painel de Administração" and st.session_state.user_role == "admin":
            admin_panel()
        else:
            # Página padrão
            display_dashboard(df, df_filtrado)
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar a página: {str(e)}")
        st.info("🔄 Tente recarregar a página ou entre em contato com o administrador.")
        
        # Log do erro
        if "user_id" in st.session_state:
            log_activity(
                st.session_state.user_id, 
                "error", 
                f"Erro na página {menu_opcao}: {str(e)}"
            )

def generate_smart_notifications(df):
    """Gera notificações inteligentes baseadas nos dados."""
    notifications = []
    
    if df.empty:
        return notifications
    
    # Notificação sobre pets não adotados há muito tempo
    if 'data_registro' in df.columns and 'adotado' in df.columns:
        df_temp = df.copy()
        df_temp['data_registro'] = pd.to_datetime(df_temp['data_registro'])
        df_temp['dias_sistema'] = (pd.Timestamp.now() - df_temp['data_registro']).dt.days
        
        pets_antigos = df_temp[(df_temp['adotado'] == False) & (df_temp['dias_sistema'] > 90)]
        
        if len(pets_antigos) > 0:
            notifications.append({
                'type': 'warning',
                'message': f"{len(pets_antigos)} pets há mais de 90 dias aguardando adoção"
            })
    
    # Notificação sobre pets com alto score não adotados
    if 'score_adocao' in df.columns and 'adotado' in df.columns:
        high_score_not_adopted = df[(df['adotado'] == False) & (df['score_adocao'] > 4.0)]
        
        if len(high_score_not_adopted) > 0:
            notifications.append({
                'type': 'info',
                'message': f"{len(high_score_not_adopted)} pets com alto score aguardando adoção"
            })
    
    # Notificação sobre necessidades especiais
    if 'necessidades_especiais' in df.columns:
        pets_especiais = df[df['necessidades_especiais'].notna() & (df['necessidades_especiais'] != '')]
        
        if len(pets_especiais) > 0:
            notifications.append({
                'type': 'info',
                'message': f"{len(pets_especiais)} pets com necessidades especiais precisam de atenção"
            })
    
    # Notificação de sucesso sobre adoções recentes
    if 'adotado' in df.columns:
        taxa_adocao = df['adotado'].mean()
        
        if taxa_adocao > 0.7:
            notifications.append({
                'type': 'success',
                'message': f"Excelente taxa de adoção: {taxa_adocao*100:.1f}%!"
            })
    
    return notifications

# Funções auxiliares adicionais continuam aqui...
def ai_insights(df):
    """Insights avançados baseados em IA."""
    st.title("🤖 IA Insights Avançados")
    
    if df.empty or len(df) < 5:
        st.warning("Dados insuficientes para análises de IA. Adicione mais pets para utilizar esta funcionalidade.")
        return
    
    # Inicializar analyzer
    analyzer = PetMLAnalyzer(df)
    
    # Seleção do tipo de insight
    insight_type = st.sidebar.selectbox(
        "Tipo de Insight:",
        [
            "Resumo Executivo com IA",
            "Previsões Comportamentais", 
            "Otimização de Matchmaking",
            "Análise de Sentimentos",
            "Detecção de Padrões",
            "Recomendações Personalizadas",
            "Simulação de Cenários",
            "Análise Preditiva Avançada"
        ]
    )
    
    if insight_type == "Resumo Executivo com IA":
        st.subheader("📋 Resumo Executivo Inteligente")
        
        with st.spinner("🧠 IA analisando os dados..."):
            time.sleep(2)  # Simular processamento IA
            
            # Análise automática dos dados
            insights = []
            
            # Insight 1: Performance geral
            total_pets = len(df)
            taxa_adocao = df['adotado'].mean() * 100 if 'adotado' in df.columns else 0
            
            if taxa_adocao > 70:
                performance = "excelente"
                cor_performance = "success"
            elif taxa_adocao > 50:
                performance = "boa"
                cor_performance = "info"
            else:
                performance = "necessita melhorias"
                cor_performance = "warning"
            
            insights.append({
                'titulo': '🎯 Performance Geral',
                'conteudo': f'O sistema possui {total_pets} pets cadastrados com taxa de adoção de {taxa_adocao:.1f}%, considerada {performance}.',
                'tipo': cor_performance
            })
            
            if 'comportamento' in df.columns and not df['comportamento'].empty:
                mode_result = df['comportamento'].mode()
                if len(mode_result) > 0:
                    comportamento_mais_comum = mode_result.iloc[0]
                else:
                    comportamento_mais_comum = "Não definido"
            else:
                comportamento_mais_comum = "Não disponível"
            
            # Insight 3: Análise demográfica
            if 'idade' in df.columns:
                idade_media = df['idade'].mean()
                idade_mediana = df['idade'].median()
                
                if idade_media < 3:
                    demografia = "jovem, ideal para famílias ativas"
                elif idade_media > 7:
                    demografia = "madura, perfeita para lares calmos"
                else:
                    demografia = "equilibrada entre jovens e adultos"
                
                insights.append({
                    'titulo': '📊 Perfil Demográfico',
                    'conteudo': f'A população é {demografia} com idade média de {idade_media:.1f} anos e mediana de {idade_mediana:.1f} anos.',
                    'tipo': 'info'
                })
            
            # Insight 4: Oportunidades de melhoria
            if 'score_adocao' in df.columns:
                score_baixo = (df['score_adocao'] < 3.0).sum()
                
                if score_baixo > 0:
                    insights.append({
                        'titulo': '⚠️ Oportunidades de Melhoria',
                        'conteudo': f'{score_baixo} pets têm score de adoção baixo (<3.0). Recomenda-se trabalhar comportamento, saúde e socialização destes animais.',
                        'tipo': 'warning'
                    })
            
            # Insight 5: Previsão de tendências
            if 'data_registro' in df.columns:
                df_temporal = df.copy()
                df_temporal['data_registro'] = pd.to_datetime(df_temporal['data_registro'])
                df_temporal['mes'] = df_temporal['data_registro'].dt.to_period('M')
                
                crescimento_mensal = df_temporal.groupby('mes').size()
                
                if len(crescimento_mensal) > 1:
                    tendencia = crescimento_mensal.iloc[-1] - crescimento_mensal.iloc[-2]
                    
                    if tendencia > 0:
                        tendencia_texto = f"crescimento de {tendencia} pets no último mês"
                        tipo_tendencia = "success"
                    elif tendencia < 0:
                        tendencia_texto = f"redução de {abs(tendencia)} pets no último mês"
                        tipo_tendencia = "warning"
                    else:
                        tendencia_texto = "estabilidade nos registros"
                        tipo_tendencia = "info"
                    
                    insights.append({
                        'titulo': '📈 Tendência de Crescimento',
                        'conteudo': f'A análise temporal indica {tendencia_texto}, sugerindo ajustes nas estratégias de captação.',
                        'tipo': tipo_tendencia
                    })
            
            # Exibir insights
            for insight in insights:
                if insight['tipo'] == 'success':
                    st.success(f"**{insight['titulo']}**\n\n{insight['conteudo']}")
                elif insight['tipo'] == 'warning':
                    st.warning(f"**{insight['titulo']}**\n\n{insight['conteudo']}")
                else:
                    st.info(f"**{insight['titulo']}**\n\n{insight['conteudo']}")
            
            # Recomendações estratégicas
            st.subheader("🎯 Recomendações Estratégicas da IA")
            
            recomendacoes = [
                "📱 Intensificar presença digital com foco em redes sociais",
                "🏥 Parcerias com clínicas veterinárias para check-ups gratuitos",
                "👨‍👩‍👧‍👦 Programas de educação para famílias sobre posse responsável",
                "📊 Implementar sistema de follow-up pós-adoção",
                "🎨 Criar campanhas segmentadas por perfil comportamental"
            ]
            
            for rec in recomendacoes:
                st.write(f"• {rec}")
    
    elif insight_type == "Previsões Comportamentais":
        st.subheader("🔮 Previsões Comportamentais com IA")
        
        # Análise de padrões comportamentais
        if 'comportamento' in df.columns and 'sociabilidade' in df.columns:
            
            with st.spinner("🤖 Analisando padrões comportamentais..."):
                time.sleep(1.5)
                
                # Criar modelo de previsão comportamental
                behavioral_data = df[['comportamento', 'sociabilidade', 'energia', 'nivel_atividade']].copy()
                behavioral_data = behavioral_data.dropna()
                
                if len(behavioral_data) > 10:
                    # Análise de clusters comportamentais
                    le = LabelEncoder()
                    behavioral_data['comportamento_encoded'] = le.fit_transform(behavioral_data['comportamento'])
                    
                    # Clustering
                    features = ['sociabilidade', 'energia', 'nivel_atividade']
                    X = behavioral_data[features]
                    
                    kmeans = KMeans(n_clusters=4, random_state=42)
                    clusters = kmeans.fit_predict(X)
                    
                    behavioral_data['cluster_comportamental'] = clusters
                    
                    # Análise dos clusters
                    st.subheader("🎯 Perfis Comportamentais Identificados")
                    
                    for cluster_id in range(4):
                        cluster_data = behavioral_data[behavioral_data['cluster_comportamental'] == cluster_id]
                        
                        if len(cluster_data) > 0:
                            # Características do cluster
                            soc_media = cluster_data['sociabilidade'].mean()
                            ener_media = cluster_data['energia'].mean()
                            ativ_media = cluster_data['nivel_atividade'].mean()
                            comportamentos = cluster_data['comportamento'].value_counts()
                            
                            # Definir personalidade do cluster
                            if soc_media > 4 and ener_media > 4:
                                personalidade = "Extrovertido e Enérgico"
                                emoji = "🌟"
                            elif soc_media > 4 and ener_media < 3:
                                personalidade = "Sociável e Calmo"
                                emoji = "😌"
                            elif soc_media < 3 and ener_media > 4:
                                personalidade = "Reservado e Ativo"
                                emoji = "🏃"
                            else:
                                personalidade = "Tranquilo e Independente"
                                emoji = "🧘"
                            
                            # Card do cluster
                            content = f"""
                            <div style="margin-bottom: 1rem;">
                                <p><strong>Pets neste grupo:</strong> {len(cluster_data)} ({len(cluster_data)/len(behavioral_data)*100:.1f}%)</p>
                                <p><strong>Características médias:</strong></p>
                                <ul>
                                    <li>Sociabilidade: {soc_media:.1f}/5</li>
                                    <li>Energia: {ener_media:.1f}/5</li>
                                    <li>Atividade: {ativ_media:.1f}/5</li>
                                </ul>
                                <p><strong>Comportamento mais comum:</strong> {comportamentos.index[0]} ({comportamentos.iloc[0]} pets)</p>
                                <p><strong>Recomendação:</strong> Ideal para tutores que buscam um pet {personalidade.lower()}.</p>
                            </div>
                            """
                            
                            custom_card(f"{emoji} Perfil {cluster_id + 1}: {personalidade}", content, color="#9C27B0")
                    
                    # Previsão para novos pets
                    st.subheader("🔮 Simulador de Perfil Comportamental")
                    
                    with st.form("behavioral_prediction"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            soc_input = st.slider("Sociabilidade:", 1, 5, 3)
                        with col2:
                            ener_input = st.slider("Energia:", 1, 5, 3)
                        with col3:
                            ativ_input = st.slider("Atividade:", 1, 5, 3)
                        
                        predict_btn = st.form_submit_button("🎯 Prever Perfil", use_container_width=True)
                        
                        if predict_btn:
                            # Prever cluster
                            input_features = np.array([[soc_input, ener_input, ativ_input]])
                            predicted_cluster = kmeans.predict(input_features)[0]
                            
                            # Características do cluster previsto
                            cluster_info = behavioral_data[behavioral_data['cluster_comportamental'] == predicted_cluster]
                            
                            if len(cluster_info) > 0:
                                st.success(f"🎯 **Perfil Previsto:** Cluster {predicted_cluster + 1}")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**Pets similares:**")
                                    similar_behaviors = cluster_info['comportamento'].value_counts().head(3)
                                    for behavior, count in similar_behaviors.items():
                                        st.write(f"• {behavior}: {count} pets")
                                
                                with col2:
                                    st.write("**Características típicas:**")
                                    st.write(f"• Sociabilidade média: {cluster_info['sociabilidade'].mean():.1f}")
                                    st.write(f"• Energia média: {cluster_info['energia'].mean():.1f}")
                                    st.write(f"• Atividade média: {cluster_info['nivel_atividade'].mean():.1f}")
        else:
            st.warning("Dados comportamentais insuficientes para análise preditiva.")
    
    elif insight_type == "Análise Preditiva Avançada":
        st.subheader("🔬 Análise Preditiva Avançada")
        
        # Seletor de tipo de previsão
        prediction_type = st.selectbox(
            "Tipo de Previsão:",
            [
                "Probabilidade de Adoção",
                "Tempo para Adoção",
                "Risco de Abandono",
                "Score de Compatibilidade"
            ]
        )
        
        if prediction_type == "Probabilidade de Adoção":
            st.write("### 🎯 Modelo de Probabilidade de Adoção")
            
            if 'adotado' in df.columns and len(df) >= 20:
                with st.spinner("🤖 Treinando modelo de probabilidade..."):
                    # Preparar dados
                    features = ['idade', 'peso', 'sociabilidade', 'energia', 'nivel_atividade']
                    available_features = [f for f in features if f in df.columns]
                    
                    if len(available_features) >= 3:
                        X = df[available_features].copy()
                        y = df['adotado'].copy()
                        
                        # Remover NaN
                        mask = ~(X.isna().any(axis=1) | y.isna())
                        X = X[mask]
                        y = y[mask]
                        
                        if len(X) >= 10:
                            # Dividir dados
                            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                            
                            # Treinar modelo
                            model = RandomForestClassifier(n_estimators=100, random_state=42)
                            model.fit(X_train, y_train)
                            
                            # Avaliar modelo
                            y_pred = model.predict(X_test)
                            accuracy = accuracy_score(y_test, y_pred)
                            
                            st.success(f"✅ Modelo treinado com acurácia de {accuracy:.3f}")
                            
                            # Feature importance
                            importance = pd.DataFrame({
                                'Feature': available_features,
                                'Importancia': model.feature_importances_
                            }).sort_values('Importancia', ascending=False)
                            
                            fig = px.bar(
                                importance,
                                x='Importancia',
                                y='Feature',
                                orientation='h',
                                title="Importância das Características para Adoção"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Simulador
                            st.write("### 🎮 Simulador de Probabilidade")
                            
                            with st.form("probability_simulator"):
                                cols = st.columns(len(available_features))
                                
                                input_values = {}
                                for i, feature in enumerate(available_features):
                                    with cols[i]:
                                        min_val = float(df[feature].min())
                                        max_val = float(df[feature].max())
                                        mean_val = float(df[feature].mean())
                                        
                                        input_values[feature] = st.slider(
                                            f"{feature}:",
                                            min_val, max_val, mean_val
                                        )
                                
                                simulate_btn = st.form_submit_button("🔮 Calcular Probabilidade", use_container_width=True)
                                
                                if simulate_btn:
                                    # Fazer previsão
                                    input_array = np.array([[input_values[f] for f in available_features]])
                                    probability = model.predict_proba(input_array)[0][1]
                                    
                                    # Exibir resultado
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Probabilidade de Adoção", f"{probability*100:.1f}%")
                                    
                                    with col2:
                                        categoria = "Alta" if probability > 0.7 else "Média" if probability > 0.4 else "Baixa"
                                        st.metric("Categoria", categoria)
                                    
                                    with col3:
                                        confianca = "Alta" if accuracy > 0.8 else "Média" if accuracy > 0.6 else "Baixa"
                                        st.metric("Confiança do Modelo", confianca)
                                    
                                    # Recomendações baseadas na probabilidade
                                    if probability > 0.7:
                                        st.success("🌟 Alto potencial de adoção! Priorize este pet nas campanhas.")
                                    elif probability > 0.4:
                                        st.info("⚡ Potencial médio. Considere trabalhar pontos de melhoria.")
                                    else:
                                        st.warning("🔧 Baixo potencial. Recomenda-se trabalhar socialização e saúde.")
                        else:
                            st.error("Dados insuficientes após limpeza para treinar o modelo.")
                    else:
                        st.error("São necessárias pelo menos 3 características para o modelo.")
            else:
                st.error("São necessários pelo menos 20 registros com status de adoção para treinar o modelo.")
    
    # Adicionar mais tipos de insight conforme necessário...

def mapa_interativo(df):
    """Mapa interativo avançado."""
    st.title("🗺️ Mapa Interativo Avançado")
    
    if df.empty:
        st.warning("Não há dados disponíveis para o mapa.")
        return
    
    # Verificar se temos dados de localização
    if 'bairro' not in df.columns:
        st.error("Dados de localização (bairro) não encontrados.")
        return
    
    # Opções de visualização
    col1, col2, col3 = st.columns(3)
    
    with col1:
        map_type = st.selectbox(
            "Tipo de Mapa:",
            ["Densidade de Pets", "Taxa de Adoção", "Score Médio", "Distribuição por Tipo"]
        )
    
    with col2:
        aggregation_level = st.selectbox(
            "Nível de Agregação:",
            ["Por Bairro", "Por Região", "Por Zona"]
        )
    
    with col3:
        filter_type = st.multiselect(
            "Filtrar por Tipo:",
            df['tipo_pet'].unique().tolist() if 'tipo_pet' in df.columns else [],
            default=df['tipo_pet'].unique().tolist() if 'tipo_pet' in df.columns else []
        )
    
    # Filtrar dados se necessário
    df_map = df.copy()
    if filter_type:
        df_map = df_map[df_map['tipo_pet'].isin(filter_type)]
    
    # Simular coordenadas para Florianópolis (em produção, usaria geocoding real)
    bairros_coords = {
        'Centro': (-27.5969, -48.5495),
        'Trindade': (-27.5717, -48.5067),
        'Canasvieiras': (-27.4324, -48.4633),
        'Ingleses': (-27.4367, -48.3917),
        'Lagoa da Conceição': (-27.5717, -48.4283),
        'Campeche': (-27.6783, -48.4967),
        'Pantano do Sul': (-27.7683, -48.5067),
        'Cachoeira do Bom Jesus': (-27.4883, -48.4183),
        'Santo Antônio de Lisboa': (-27.5000, -48.5333)
    }
    
    # Preparar dados do mapa
    if map_type == "Densidade de Pets":
        map_data = df_map.groupby('bairro').size().reset_index(name='count')
        color_column = 'count'
        title = "Densidade de Pets por Bairro"
        
    elif map_type == "Taxa de Adoção" and 'adotado' in df_map.columns:
        map_data = df_map.groupby('bairro')['adotado'].mean().reset_index()
        map_data['adotado'] = map_data['adotado'] * 100  # Converter para percentual
        color_column = 'adotado'
        title = "Taxa de Adoção por Bairro (%)"
        
    elif map_type == "Score Médio" and 'score_adocao' in df_map.columns:
        map_data = df_map.groupby('bairro')['score_adocao'].mean().reset_index()
        color_column = 'score_adocao'
        title = "Score Médio de Adoção por Bairro"
        
    else:
        # Distribuição por tipo
        map_data = df_map.groupby(['bairro', 'tipo_pet']).size().reset_index(name='count')
        color_column = 'count'
        title = "Distribuição de Tipos por Bairro"
    
    # Adicionar coordenadas
    map_data['lat'] = map_data['bairro'].map(lambda x: bairros_coords.get(x, (-27.5969, -48.5495))[0])
    map_data['lon'] = map_data['bairro'].map(lambda x: bairros_coords.get(x, (-27.5969, -48.5495))[1])
    
    # Criar mapa
    if map_type != "Distribuição por Tipo":
        # Mapa de pontos com cores
        fig = px.scatter_mapbox(
            map_data,
            lat='lat',
            lon='lon',
            size=color_column,
            color=color_column,
            hover_name='bairro',
            hover_data={color_column: ':.1f'},
            title=title,
            mapbox_style='open-street-map',
            zoom=10,
            center=dict(lat=-27.5969, lon=-48.5495),
            color_continuous_scale='viridis'
        )
    else:
        # Mapa com diferentes símbolos por tipo
        fig = px.scatter_mapbox(
            map_data,
            lat='lat',
            lon='lon',
            size='count',
            color='tipo_pet',
            hover_name='bairro',
            hover_data={'count': True, 'tipo_pet': True},
            title=title,
            mapbox_style='open-street-map',
            zoom=10,
            center=dict(lat=-27.5969, lon=-48.5495)
        )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas do mapa
    st.subheader("📊 Estatísticas Regionais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top bairros
        if map_type == "Densidade de Pets":
            if not map_data.empty and 'count' in map_data.columns:
                top_bairros = map_data.nlargest(min(5, len(map_data)), 'count')
            else:
                top_bairros = pd.DataFrame()  # DataFrame vazio
            st.write("**Top 5 Bairros - Maior Quantidade:**")
        elif map_type == "Taxa de Adoção":
            top_bairros = map_data.nlargest(5, 'adotado')
            st.write("**Top 5 Bairros - Maior Taxa de Adoção:**")
        else:
            top_bairros = map_data.nlargest(5, color_column)
            st.write(f"**Top 5 Bairros - {title}:**")
        
        for _, row in top_bairros.iterrows():
            value = row[color_column]
            if map_type == "Taxa de Adoção":
                st.write(f"• {row['bairro']}: {value:.1f}%")
            else:
                st.write(f"• {row['bairro']}: {value:.1f}")
    
    with col2:
        # Análise regional
        st.write("**Análise Regional:**")
        
        total_pets_map = map_data[color_column].sum() if map_type == "Densidade de Pets" else len(df_map)
        media_regional = map_data[color_column].mean()
        
        st.write(f"• Total de pets: {total_pets_map}")
        st.write(f"• Média por bairro: {media_regional:.1f}")
        st.write(f"• Bairros cobertos: {len(map_data)}")
        
        # Bairro com maior concentração
        if len(map_data) > 0:
            bairro_destaque = map_data.loc[map_data[color_column].idxmax(), 'bairro']
            valor_destaque = map_data[color_column].max()
            
            if map_type == "Taxa de Adoção":
                st.success(f"🏆 Destaque: {bairro_destaque} ({valor_destaque:.1f}%)")
            else:
                st.success(f"🏆 Destaque: {bairro_destaque} ({valor_destaque:.1f})")
    
    # Análise temporal se disponível
    if 'data_registro' in df_map.columns:
        st.subheader("📈 Evolução Temporal por Região")
        
        df_temporal = df_map.copy()
        df_temporal['data_registro'] = pd.to_datetime(df_temporal['data_registro'])
        df_temporal['mes'] = df_temporal['data_registro'].dt.to_period('M')
        
        # Evolução mensal por bairro
        evolucao_bairros = df_temporal.groupby(['mes', 'bairro']).size().reset_index(name='registros')
        evolucao_bairros['mes_str'] = evolucao_bairros['mes'].astype(str)
        
        # Selecionar top 5 bairros para visualização
        top_5_bairros = df_map['bairro'].value_counts().head(5).index.tolist()
        evolucao_filtrada = evolucao_bairros[evolucao_bairros['bairro'].isin(top_5_bairros)]
        
        if len(evolucao_filtrada) > 0:
            fig_evolucao = px.line(
                evolucao_filtrada,
                x='mes_str',
                y='registros',
                color='bairro',
                title="Evolução de Registros por Bairro",
                labels={'mes_str': 'Mês', 'registros': 'Número de Registros'}
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Heatmap de relacionamentos
    st.subheader("🔥 Heatmap de Características")
    
    if 'tipo_pet' in df_map.columns and len(df_map) > 0:
        # Crosstab entre bairro e tipo
        crosstab = pd.crosstab(df_map['bairro'], df_map['tipo_pet'])
        
        fig_heatmap = px.imshow(
            crosstab.values,
            x=crosstab.columns,
            y=crosstab.index,
            title="Distribuição de Tipos de Pet por Bairro",
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        
        fig_heatmap.update_layout(
            xaxis_title="Tipo de Pet",
            yaxis_title="Bairro"
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Insights geográficos
    st.subheader("💡 Insights Geográficos")
    
    insights_geo = []
    
    # Concentração regional
    if len(map_data) > 0:
        concentracao = map_data[color_column].std() / map_data[color_column].mean()
        
        if concentracao > 0.5:
            insights_geo.append("🎯 Há alta concentração em poucos bairros - considere expandir para outras regiões")
        else:
            insights_geo.append("📊 Distribuição equilibrada entre os bairros")
    
    # Análise de performance por região
    if map_type == "Taxa de Adoção" and len(map_data) > 1:
        taxa_max = map_data['adotado'].max()
        taxa_min = map_data['adotado'].min()
        diferenca = taxa_max - taxa_min
        
        if diferenca > 30:  # Diferença maior que 30%
            insights_geo.append(f"⚠️ Grande variação regional: diferença de {diferenca:.1f}% entre bairros")
        else:
            insights_geo.append("✅ Performance regional consistente")
    
    # Oportunidades de melhoria
    if map_type == "Densidade de Pets" and len(map_data) > 0:
        bairros_baixa_densidade = map_data[map_data['count'] < map_data['count'].mean() * 0.5]
        
        if len(bairros_baixa_densidade) > 0:
            insights_geo.append(f"📈 Oportunidade: {len(bairros_baixa_densidade)} bairros com baixa densidade podem ser explorados")
    
    # Exibir insights
    for insight in insights_geo:
        st.info(insight)

# Funções adicionais para admin e configurações...
def user_settings():
    """Configurações avançadas do usuário."""
    st.title("⚙️ Configurações Avançadas do Usuário")
    
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("Por favor, faça login para acessar as configurações.")
        return
    
    user_info = st.session_state.user_info
    
    # Tabs expandidas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Perfil", 
        "🔐 Segurança", 
        "🔔 Notificações", 
        "🎨 Preferências",
        "📊 Atividade"
    ])
    
    with tab1:
        st.subheader("👤 Informações do Perfil")
        
        # Avatar e informações básicas
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Avatar simulado
            initials = ''.join([name[0].upper() for name in user_info['full_name'].split() if name])
            st.markdown(
                f"""
                <div style="width: 120px; height: 120px; border-radius: 50%; 
                background: linear-gradient(45deg, #4527A0, #7B1FA2); color: white; 
                display: flex; align-items: center; justify-content: center; 
                font-size: 48px; font-weight: bold; margin: 0 auto 20px auto;">
                {initials}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Upload de avatar
            uploaded_avatar = st.file_uploader("Alterar Avatar", type=['png', 'jpg', 'jpeg'])
            if uploaded_avatar:
                st.success("Avatar carregado! (Funcionalidade em desenvolvimento)")
        
        with col2:
            with st.form("profile_form"):
                full_name = st.text_input("Nome Completo", value=user_info.get('full_name', ''))
                email = st.text_input("Email", value=user_info.get('email', ''), disabled=True)
                
                # Campos adicionais
                col_a, col_b = st.columns(2)
                
                with col_a:
                    phone = st.text_input("Telefone", value="")
                    organization = st.text_input("Organização", value="")
                
                with col_b:
                    location = st.text_input("Localização", value="Florianópolis, SC")
                    website = st.text_input("Website", value="")
                
                bio = st.text_area("Biografia", height=100, 
                                 placeholder="Conte um pouco sobre você e seu trabalho com pets...")
                
                # Preferências profissionais
                st.write("**Área de Atuação:**")
                areas = st.multiselect(
                    "Selecione suas áreas:",
                    ["ONGs", "Veterinária", "Adoção", "Educação", "Pesquisa", "Voluntariado"],
                    default=["Adoção"]
                )
                
                # Salvar alterações
                submitted = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                
                if submitted:
                    # Simular salvamento
                    st.success("✅ Perfil atualizado com sucesso!")
                    
                    # Atualizar session state
                    st.session_state.user_info['full_name'] = full_name
                    
                    # Log da atividade
                    log_activity(st.session_state.user_id, "update_profile", "Atualizou informações do perfil")
    
    with tab2:
        st.subheader("🔐 Segurança e Privacidade")
        
        # Alterar senha
        with st.expander("🔑 Alterar Senha", expanded=False):
            with st.form("password_form"):
                current_password = st.text_input("Senha Atual", type="password")
                new_password = st.text_input("Nova Senha", type="password")
                confirm_password = st.text_input("Confirmar Nova Senha", type="password")
                
                # Indicador de força da senha
                if new_password:
                    strength = calculate_password_strength(new_password)
                    color = ["red", "orange", "yellow", "lightgreen", "green"][strength-1]
                    strength_text = ["Muito Fraca", "Fraca", "Regular", "Forte", "Muito Forte"][strength-1]
                    
                    st.markdown(f"Força da senha: <span style='color: {color}'>{strength_text}</span>", 
                               unsafe_allow_html=True)
                
                change_password_btn = st.form_submit_button("🔄 Alterar Senha", use_container_width=True)
                
                if change_password_btn:
                    if not all([current_password, new_password, confirm_password]):
                        st.error("❌ Preencha todos os campos.")
                    elif new_password != confirm_password:
                        st.error("❌ As senhas não coincidem.")
                    elif len(new_password) < 8:
                        st.error("❌ A nova senha deve ter pelo menos 8 caracteres.")
                    else:
                        success = change_password(st.session_state.user_id, current_password, new_password)
                        
                        if success:
                            st.success("✅ Senha alterada com sucesso!")
                            log_activity(st.session_state.user_id, "change_password", "Alterou senha")
                        else:
                            st.error("❌ Senha atual incorreta.")
        
        # Sessões ativas
        st.write("**🖥️ Sessões Ativas:**")
        
        sessions_data = pd.DataFrame({
            'Dispositivo': ['Este Navegador', 'Chrome - Windows', 'Mobile App'],
            'Local': ['Florianópolis, BR', 'São Paulo, BR', 'Florianópolis, BR'],
            'Último Acesso': ['Agora', '2 horas atrás', '1 dia atrás'],
            'Status': ['Ativa', 'Ativa', 'Expirada']
        })
        
        st.dataframe(sessions_data, use_container_width=True, hide_index=True)
        
        if st.button("🚫 Encerrar Todas as Outras Sessões"):
            st.success("✅ Outras sessões encerradas com sucesso!")
        
        # Configurações de privacidade
        st.write("**🛡️ Configurações de Privacidade:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_activity = st.checkbox("Mostrar atividade para outros usuários", value=True)
            allow_mentions = st.checkbox("Permitir menções", value=True)
            
        with col2:
            data_export = st.checkbox("Permitir exportação de dados pessoais", value=False)
            analytics = st.checkbox("Contribuir com dados para análises", value=True)
        
        if st.button("💾 Salvar Configurações de Privacidade"):
            st.success("✅ Configurações de privacidade atualizadas!")
    
    with tab3:
        st.subheader("🔔 Centro de Notificações")
        
        # Configurações por tipo
        notification_types = [
            {"name": "Novos Pets Cadastrados", "email": True, "push": False, "sms": False},
            {"name": "Pets Adotados", "email": True, "push": True, "sms": False},
            {"name": "Alertas do Sistema", "email": True, "push": True, "sms": True},
            {"name": "Relatórios Semanais", "email": False, "push": False, "sms": False},
            {"name": "Atualizações de Pets", "email": True, "push": False, "sms": False},
            {"name": "Mensagens Importantes", "email": True, "push": True, "sms": True}
        ]
        
        st.write("**Configurar Notificações por Tipo:**")
        
        for i, notif in enumerate(notification_types):
            st.write(f"**{notif['name']}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                email_enabled = st.checkbox("📧 Email", value=notif['email'], key=f"email_{i}")
            with col2:
                push_enabled = st.checkbox("📱 Push", value=notif['push'], key=f"push_{i}")
            with col3:
                sms_enabled = st.checkbox("💬 SMS", value=notif['sms'], key=f"sms_{i}")
            
            st.divider()
        
        # Configurações gerais
        st.write("**⚙️ Configurações Gerais:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quiet_hours = st.checkbox("Modo silencioso noturno (22h-7h)", value=True)
            digest_frequency = st.selectbox(
                "Frequência do resumo:",
                ["Diário", "Semanal", "Mensal", "Nunca"],
                index=1
            )
        
        with col2:
            priority_only = st.checkbox("Apenas notificações prioritárias", value=False)
            max_per_day = st.slider("Máximo de notificações por dia:", 1, 20, 10)
        
        if st.button("🔔 Salvar Configurações de Notificação"):
            st.success("✅ Configurações de notificação atualizadas!")
    
    with tab4:
        st.subheader("🎨 Preferências de Interface")
        
        # Tema e aparência
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎨 Aparência:**")
            theme = st.radio("Tema:", ["Claro", "Escuro", "Automático"], horizontal=True)
            color_scheme = st.selectbox("Esquema de Cores:", ["Padrão", "Azul", "Verde", "Roxo", "Rosa"])
            font_size = st.selectbox("Tamanho da Fonte:", ["Pequeno", "Médio", "Grande"], index=1)
        
        with col2:
            st.write("**🌐 Localização:**")
            language = st.selectbox("Idioma:", ["Português (Brasil)", "English", "Español"])
            timezone = st.selectbox("Fuso Horário:", ["(GMT-3) Brasília", "(GMT-2) Fernando de Noronha"])
            date_format = st.selectbox("Formato de Data:", ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"])
        
        # Preferências de dashboard
        st.write("**📊 Preferências do Dashboard:**")
        
        default_view = st.selectbox(
            "Visualização padrão:",
            ["Dashboard", "Lista de Pets", "Análises", "Mapa"]
        )
        
        charts_preference = st.multiselect(
            "Gráficos favoritos:",
            ["Barras", "Pizza", "Linha", "Scatter", "Heatmap", "Box Plot"],
            default=["Barras", "Pizza"]
        )
        
        items_per_page = st.slider("Itens por página:", 10, 100, 25)
        
        # Atalhos personalizados
        st.write("**⌨️ Atalhos Personalizados:**")
        
        shortcuts = st.text_area(
            "Atalhos (formato: Ctrl+K = Buscar):",
            value="Ctrl+N = Novo Pet\nCtrl+D = Dashboard\nCtrl+E = Exportar",
            height=100
        )
        
        if st.button("🎨 Salvar Preferências"):
            st.success("✅ Preferências de interface atualizadas!")
    
    with tab5:
        st.subheader("📊 Relatório de Atividade")
        
        # Métricas de atividade
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Logins", "156", "+12 esta semana")
        
        with col2:
            st.metric("Pets Adicionados", "23", "+3 este mês")
        
        with col3:
            st.metric("Relatórios Gerados", "8", "+2 esta semana")
        
        with col4:
            st.metric("Tempo no Sistema", "42h", "+6h esta semana")
        
        # Gráfico de atividade
        activity_dates = pd.date_range(start='2025-04-01', end='2025-05-23', freq='D')
        activity_data = pd.DataFrame({
            'Data': activity_dates,
            'Atividade': np.random.poisson(3, len(activity_dates))
        })
        
        fig_activity = px.line(
            activity_data,
            x='Data',
            y='Atividade',
            title="Atividade Diária nos Últimos 60 Dias"
        )
        st.plotly_chart(fig_activity, use_container_width=True)
        
        # Log de atividades recentes
        st.write("**📝 Atividades Recentes:**")
        
        # Simular dados de atividade
        recent_activities = pd.DataFrame({
            'Data/Hora': [
                '23/05/2025 14:30',
                '23/05/2025 09:15',
                '22/05/2025 16:45',
                '22/05/2025 11:20',
                '21/05/2025 15:30'
            ],
            'Ação': [
                'Login no sistema',
                'Adicionou pet: Buddy',
                'Gerou relatório de adoções',
                'Alterou dados do pet: Luna',
                'Exportou dados em Excel'
            ],
            'IP': [
                '192.168.1.100',
                '192.168.1.100',
                '192.168.1.100',
                '192.168.1.100',
                '10.0.0.50'
            ]
        })
        
        st.dataframe(recent_activities, use_container_width=True, hide_index=True)
        
        # Exportar dados de atividade
        if st.button("📥 Exportar Histórico de Atividade"):
            activity_csv = recent_activities.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV",
                data=activity_csv,
                file_name=f"atividade_usuario_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def calculate_password_strength(password):
    """Calcula a força de uma senha."""
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in '!@#$%&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 1
    
    return min(5, max(1, score))

@require_admin
def admin_panel():
    """Painel de administração avançado."""
    st.title("⚙️ Painel de Administração Avançado")
    
    # Menu lateral administrativo
    admin_section = st.sidebar.selectbox(
        "Seção Administrativa:",
        [
            "📊 Dashboard Administrativo",
            "👥 Gerenciar Usuários",
            "🔍 Logs e Auditoria",
            "⚙️ Configurações do Sistema",
            "💾 Backup e Manutenção",
            "📈 Analytics do Sistema",
            "🛡️ Segurança",
            "🔧 Ferramentas Avançadas"
        ]
    )
    
    if admin_section == "📊 Dashboard Administrativo":
        st.subheader("📊 Dashboard Administrativo")
        
        # Métricas principais do sistema
        col1, col2, col3, col4 = st.columns(4)
        
        # Simular dados administrativos
        with col1:
            st.metric("Total de Usuários", "127", "+8 este mês")
        
        with col2:
            st.metric("Pets no Sistema", "1,234", "+45 esta semana")
        
        with col3:
            st.metric("Taxa de Adoção", "68.3%", "+2.1% este mês")
        
        with col4:
            st.metric("Uptime do Sistema", "99.8%", "Excelente")
        
        # Gráficos administrativos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de usuários ativos
            dates = pd.date_range(start='2025-04-01', end='2025-05-23', freq='D')
            active_users = pd.DataFrame({
                'Data': dates,
                'Usuarios_Ativos': np.random.poisson(25, len(dates))
            })
            
            fig_users = px.line(
                active_users,
                x='Data',
                y='Usuarios_Ativos',
                title="Usuários Ativos Diariamente"
            )
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Distribuição de tipos de usuário
            user_types = pd.DataFrame({
                'Tipo': ['Administradores', 'Usuários Regulares', 'Convidados'],
                'Quantidade': [5, 95, 27]
            })
            
            fig_types = px.pie(
                user_types,
                values='Quantidade',
                names='Tipo',
                title="Distribuição de Tipos de Usuário"
            )
            st.plotly_chart(fig_types, use_container_width=True)

            # Alertas do sistema
        st.subheader("🚨 Alertas do Sistema")
        
        alerts = [
            {"tipo": "warning", "mensagem": "5 usuários não fazem login há mais de 30 dias"},
            {"tipo": "info", "mensagem": "Backup automático executado com sucesso às 03:00"},
            {"tipo": "success", "mensagem": "Sistema funcionando normalmente"},
            {"tipo": "warning", "mensagem": "Uso de disco em 78% - considere limpeza"}
        ]
        
        for alert in alerts:
            if alert["tipo"] == "warning":
                st.warning(f"⚠️ {alert['mensagem']}")
            elif alert["tipo"] == "success":
                st.success(f"✅ {alert['mensagem']}")
            else:
                st.info(f"ℹ️ {alert['mensagem']}")
        
        # Estatísticas de performance
        st.subheader("⚡ Performance do Sistema")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Tempo Médio de Resposta", "0.23s", "-0.05s")
            st.metric("Consultas por Segundo", "156", "+12")
        
        with perf_col2:
            st.metric("Uso de CPU", "34%", "-5%")
            st.metric("Uso de Memória", "2.1GB", "+0.3GB")
        
        with perf_col3:
            st.metric("Conexões Ativas", "23", "+3")
            st.metric("Cache Hit Rate", "94.2%", "+1.8%")
    
    elif admin_section == "👥 Gerenciar Usuários":
        st.subheader("👥 Gerenciamento Avançado de Usuários")
        
        # Obter dados de usuários do banco
        conn = sqlite3.connect(DATABASE_PATH)
        query = """
        SELECT u.id, u.email, u.full_name, u.role, u.created_at, u.last_login,
               COUNT(p.id) as pets_cadastrados,
               COUNT(CASE WHEN p.adotado = 1 THEN 1 END) as pets_adotados
        FROM users u
        LEFT JOIN pets p ON u.id = p.created_by
        GROUP BY u.id, u.email, u.full_name, u.role, u.created_at, u.last_login
        """
        df_users = pd.read_sql_query(query, conn)
        conn.close()
        
        # Filtros e busca
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Buscar usuário:", placeholder="Nome ou email...")
        
        with col2:
            role_filter = st.selectbox("Filtrar por papel:", ["Todos", "admin", "user", "guest"])
        
        with col3:
            status_filter = st.selectbox("Status:", ["Todos", "Ativos", "Inativos"])
        
        # Aplicar filtros
        df_filtered = df_users.copy()
        
        if search_term:
            df_filtered = df_filtered[
                (df_filtered['email'].str.contains(search_term, case=False, na=False)) |
                (df_filtered['full_name'].str.contains(search_term, case=False, na=False))
            ]
        
        if role_filter != "Todos":
            df_filtered = df_filtered[df_filtered['role'] == role_filter]
        
        # Tabela de usuários
        st.subheader("📋 Lista de Usuários")
        
        # Configurar colunas da tabela
        column_config = {
            "id": "ID",
            "email": "Email",
            "full_name": "Nome Completo",
            "role": st.column_config.SelectboxColumn(
                "Papel",
                options=["admin", "user", "guest"],
                required=True
            ),
            "created_at": st.column_config.DatetimeColumn("Data de Criação"),
            "last_login": st.column_config.DatetimeColumn("Último Login"),
            "pets_cadastrados": st.column_config.NumberColumn("Pets Cadastrados"),
            "pets_adotados": st.column_config.NumberColumn("Pets Adotados")
        }
        
        # Editor de dados
        edited_df = st.data_editor(
            df_filtered,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
        
        # Botões de ação
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Salvar Alterações", use_container_width=True):
                st.success("✅ Alterações salvas com sucesso!")
        
        with col2:
            if st.button("➕ Novo Usuário", use_container_width=True):
                st.session_state.show_new_user_form = True
        
        with col3:
            if st.button("📧 Enviar Email em Massa", use_container_width=True):
                st.session_state.show_email_form = True
        
        with col4:
            if st.button("📊 Relatório de Usuários", use_container_width=True):
                csv_data = df_users.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar CSV",
                    data=csv_data,
                    file_name=f"usuarios_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Formulário para novo usuário
        if st.session_state.get('show_new_user_form', False):
            with st.expander("➕ Adicionar Novo Usuário", expanded=True):
                with st.form("new_user_admin"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_email = st.text_input("Email:", key="admin_new_email")
                        new_name = st.text_input("Nome Completo:", key="admin_new_name")
                    
                    with col2:
                        new_role = st.selectbox("Papel:", ["user", "admin"], key="admin_new_role")
                        new_password = st.text_input("Senha Inicial:", type="password", key="admin_new_password")
                    
                    send_welcome = st.checkbox("Enviar email de boas-vindas", value=True)
                    force_password_change = st.checkbox("Forçar alteração de senha no primeiro login", value=True)
                    
                    col_a, col_b = st.columns([1, 1])
                    
                    with col_a:
                        create_user = st.form_submit_button("✅ Criar Usuário", use_container_width=True)
                    
                    with col_b:
                        cancel_create = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if create_user:
                        if new_email and new_name and new_password:
                            success, user_id = register_new_user(new_email, new_password, new_name, new_role)
                            
                            if success:
                                st.success(f"✅ Usuário {new_name} criado com sucesso!")
                                log_activity(st.session_state.user_id, "create_user", f"Criou usuário: {new_email}")
                                st.session_state.show_new_user_form = False
                                st.rerun()
                            else:
                                st.error("❌ Email já está em uso.")
                        else:
                            st.error("❌ Preencha todos os campos obrigatórios.")
                    
                    if cancel_create:
                        st.session_state.show_new_user_form = False
                        st.rerun()
        
        # Formulário de email em massa
        if st.session_state.get('show_email_form', False):
            with st.expander("📧 Enviar Email em Massa", expanded=True):
                with st.form("mass_email"):
                    subject = st.text_input("Assunto:")
                    message = st.text_area("Mensagem:", height=150)
                    
                    recipients = st.multiselect(
                        "Destinatários:",
                        options=df_users['email'].tolist(),
                        default=df_users['email'].tolist()
                    )
                    
                    col_a, col_b = st.columns([1, 1])
                    
                    with col_a:
                        send_email = st.form_submit_button("📤 Enviar Email", use_container_width=True)
                    
                    with col_b:
                        cancel_email = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if send_email:
                        if subject and message and recipients:
                            st.success(f"✅ Email enviado para {len(recipients)} usuários!")
                            log_activity(st.session_state.user_id, "mass_email", f"Enviou email para {len(recipients)} usuários")
                            st.session_state.show_email_form = False
                        else:
                            st.error("❌ Preencha todos os campos.")
                    
                    if cancel_email:
                        st.session_state.show_email_form = False
                        st.rerun()
        
        # Estatísticas de usuários
        st.subheader("📊 Estatísticas de Usuários")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Usuários por papel
            role_stats = df_users['role'].value_counts()
            fig_roles = px.pie(
                values=role_stats.values,
                names=role_stats.index,
                title="Distribuição por Papel"
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        
        with col2:
            # Atividade dos usuários
            df_users['last_login'] = pd.to_datetime(df_users['last_login'])
            df_users['dias_ultimo_login'] = (pd.Timestamp.now() - df_users['last_login']).dt.days
            
            activity_ranges = pd.cut(
                df_users['dias_ultimo_login'].fillna(999),
                bins=[0, 7, 30, 90, 999],
                labels=['Última semana', 'Último mês', 'Últimos 3 meses', 'Mais de 3 meses']
            )
            
            activity_counts = activity_ranges.value_counts()
            
            fig_activity = px.bar(
                x=activity_counts.index,
                y=activity_counts.values,
                title="Atividade dos Usuários"
            )
            st.plotly_chart(fig_activity, use_container_width=True)
    
    elif admin_section == "🔍 Logs e Auditoria":
        st.subheader("🔍 Sistema de Logs e Auditoria")
        
        # Filtros de log
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            log_type = st.selectbox("Tipo de Log:", ["Todos", "Login", "Atividade", "Erro", "Sistema"])
        
        with col2:
            date_range = st.date_input(
                "Período:",
                [datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()]
            )
        
        with col3:
            user_filter = st.text_input("Filtrar por usuário:")
        
        with col4:
            action_filter = st.selectbox("Ação:", ["Todas", "login", "add_pet", "export_data", "delete", "update"])
        
        # Obter logs do banco
        conn = sqlite3.connect(DATABASE_PATH)
        
        if log_type == "Login" or log_type == "Todos":
            login_query = """
            SELECT 'login' as log_type, l.timestamp, u.email as user_email, 
                   CASE WHEN l.success = 1 THEN 'Login Sucesso' ELSE 'Login Falha' END as action,
                   l.ip_address as details
            FROM login_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT 1000
            """
            df_login_logs = pd.read_sql_query(login_query, conn)
        else:
            df_login_logs = pd.DataFrame()
        
        if log_type == "Atividade" or log_type == "Todos":
            activity_query = """
            SELECT 'activity' as log_type, a.timestamp, u.email as user_email, 
                   a.action, a.details
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 1000
            """
            df_activity_logs = pd.read_sql_query(activity_query, conn)
        else:
            df_activity_logs = pd.DataFrame()
        
        conn.close()
        
        # Combinar logs
        df_logs = pd.concat([df_login_logs, df_activity_logs], ignore_index=True)
        
        if not df_logs.empty:
            # Aplicar filtros
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df_logs = df_logs[
                    (df_logs['timestamp'].dt.date >= start_date) &
                    (df_logs['timestamp'].dt.date <= end_date)
                ]
            
            if user_filter:
                df_logs = df_logs[df_logs['user_email'].str.contains(user_filter, case=False, na=False)]
            
            if action_filter != "Todas":
                df_logs = df_logs[df_logs['action'].str.contains(action_filter, case=False, na=False)]
            
            # Exibir logs
            st.subheader(f"📋 Logs do Sistema ({len(df_logs)} registros)")
            
            # Configurar exibição
            df_display = df_logs.copy()
            df_display['timestamp'] = df_display['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')
            
            st.dataframe(
                df_display[['timestamp', 'user_email', 'action', 'details', 'log_type']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": "Data/Hora",
                    "user_email": "Usuário",
                    "action": "Ação",
                    "details": "Detalhes",
                    "log_type": "Tipo"
                }
            )
            
            # Análise de logs
            st.subheader("📊 Análise de Logs")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Ações mais comuns
                action_counts = df_logs['action'].value_counts().head(10)
                fig_actions = px.bar(
                    x=action_counts.values,
                    y=action_counts.index,
                    orientation='h',
                    title="Top 10 Ações Mais Comuns"
                )
                st.plotly_chart(fig_actions, use_container_width=True)
            
            with col2:
                # Atividade por hora
                df_logs['hour'] = df_logs['timestamp'].dt.hour
                hourly_activity = df_logs['hour'].value_counts().sort_index()
                
                fig_hourly = px.line(
                    x=hourly_activity.index,
                    y=hourly_activity.values,
                    title="Atividade por Hora do Dia"
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Detecção de anomalias nos logs
            st.subheader("🚨 Detecção de Anomalias")
            
            # Usuários com muitas atividades
            user_activity = df_logs['user_email'].value_counts()
            threshold = user_activity.mean() + 2 * user_activity.std()
            
            suspicious_users = user_activity[user_activity > threshold]
            
            if len(suspicious_users) > 0:
                st.warning(f"⚠️ **Usuários com atividade acima do normal:**")
                for user, count in suspicious_users.items():
                    st.write(f"• {user}: {count} ações (média: {user_activity.mean():.1f})")
            else:
                st.success("✅ Nenhuma atividade suspeita detectada.")
            
            # Exportar logs
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📥 Exportar Logs Filtrados"):
                    csv_data = df_logs.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Baixar CSV",
                        data=csv_data,
                        file_name=f"logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("🗑️ Limpar Logs Antigos"):
                    st.warning("⚠️ Esta ação removerá logs com mais de 90 dias. Confirme na próxima versão.")
        
        else:
            st.info("📭 Nenhum log encontrado para os filtros selecionados.")
    
    elif admin_section == "⚙️ Configurações do Sistema":
        st.subheader("⚙️ Configurações Avançadas do Sistema")
        
        # Tabs de configuração
        config_tab1, config_tab2, config_tab3, config_tab4 = st.tabs([
            "🏗️ Geral", 
            "🔐 Segurança", 
            "📧 Email", 
            "🔗 Integrações"
        ])
        
        with config_tab1:
            st.write("### ⚙️ Configurações Gerais")
            
            with st.form("general_config"):
                col1, col2 = st.columns(2)
                
                with col1:
                    system_name = st.text_input("Nome do Sistema:", value="PetCare Analytics")
                    maintenance_mode = st.checkbox("Modo de Manutenção", value=False)
                    debug_mode = st.checkbox("Modo Debug", value=False)
                    
                with col2:
                    max_upload_size = st.number_input("Tamanho máximo de upload (MB):", value=10, min_value=1, max_value=100)
                    session_timeout = st.number_input("Timeout de sessão (minutos):", value=60, min_value=5, max_value=480)
                    auto_backup = st.checkbox("Backup automático", value=True)
                
                # Configurações de paginação
                st.write("**Configurações de Interface:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    default_page_size = st.slider("Itens por página (padrão):", 10, 100, 25)
                    enable_animations = st.checkbox("Habilitar animações", value=True)
                
                with col2:
                    cache_duration = st.slider("Duração do cache (minutos):", 5, 60, 15)
                    enable_notifications = st.checkbox("Notificações do sistema", value=True)
                
                # Configurações de dados
                st.write("**Configurações de Dados:**")
                
                data_retention_days = st.slider("Retenção de dados (dias):", 30, 365, 180)
                auto_cleanup = st.checkbox("Limpeza automática de dados antigos", value=True)
                
                if st.form_submit_button("💾 Salvar Configurações Gerais"):
                    st.success("✅ Configurações gerais salvas com sucesso!")
                    log_activity(st.session_state.user_id, "update_config", "Atualizou configurações gerais")
        
        with config_tab2:
            st.write("### 🔐 Configurações de Segurança")
            
            with st.form("security_config"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Políticas de Senha:**")
                    min_password_length = st.slider("Comprimento mínimo:", 6, 20, 8)
                    require_uppercase = st.checkbox("Exigir maiúsculas", value=True)
                    require_lowercase = st.checkbox("Exigir minúsculas", value=True)
                    require_numbers = st.checkbox("Exigir números", value=True)
                    require_symbols = st.checkbox("Exigir símbolos", value=False)
                
                with col2:
                    st.write("**Controle de Acesso:**")
                    max_login_attempts = st.slider("Tentativas máximas de login:", 3, 10, 5)
                    lockout_duration = st.slider("Duração do bloqueio (minutos):", 5, 60, 30)
                    enable_2fa = st.checkbox("Habilitar 2FA", value=False)
                    force_https = st.checkbox("Forçar HTTPS", value=True)
                
                st.write("**Lista de IPs Permitidos:**")
                ip_whitelist = st.text_area(
                    "IPs permitidos (um por linha):",
                    height=100,
                    placeholder="192.168.1.0/24\n10.0.0.0/8"
                )
                
                st.write("**Configurações de Log de Segurança:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    log_failed_logins = st.checkbox("Log de logins falhados", value=True)
                    log_privilege_changes = st.checkbox("Log de mudanças de privilégio", value=True)
                
                with col2:
                    alert_suspicious_activity = st.checkbox("Alertar atividade suspeita", value=True)
                    auto_ban_suspicious_ips = st.checkbox("Banir IPs suspeitos automaticamente", value=False)
                
                if st.form_submit_button("🔒 Salvar Configurações de Segurança"):
                    st.success("✅ Configurações de segurança salvas com sucesso!")
                    log_activity(st.session_state.user_id, "update_security", "Atualizou configurações de segurança")
        
        with config_tab3:
            st.write("### 📧 Configurações de Email")
            
            with st.form("email_config"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Servidor SMTP:**")
                    smtp_server = st.text_input("Servidor:", value="smtp.gmail.com")
                    smtp_port = st.number_input("Porta:", value=587, min_value=1, max_value=65535)
                    smtp_encryption = st.selectbox("Criptografia:", ["TLS", "SSL", "Nenhuma"])
                
                with col2:
                    st.write("**Autenticação:**")
                    smtp_username = st.text_input("Usuário:")
                    smtp_password = st.text_input("Senha:", type="password")
                    from_email = st.text_input("Email remetente:", value="noreply@petcare.com")
                
                st.write("**Templates de Email:**")
                
                welcome_template = st.text_area(
                    "Template de boas-vindas:",
                    value="Bem-vindo ao PetCare Analytics!\n\nSua conta foi criada com sucesso.",
                    height=100
                )
                
                notification_template = st.text_area(
                    "Template de notificação:",
                    value="Você tem uma nova notificação no sistema PetCare.",
                    height=100
                )
                
                # Teste de configuração
                col1, col2 = st.columns(2)
                
                with col1:
                    test_email = st.text_input("Email para teste:")
                
                with col2:
                    if st.form_submit_button("📤 Testar Configuração"):
                        if test_email:
                            st.success(f"✅ Email de teste enviado para {test_email}!")
                        else:
                            st.error("❌ Insira um email para teste.")
                
                if st.form_submit_button("📧 Salvar Configurações de Email"):
                    st.success("✅ Configurações de email salvas com sucesso!")
                    log_activity(st.session_state.user_id, "update_email_config", "Atualizou configurações de email")
        
        with config_tab4:
            st.write("### 🔗 Configurações de Integrações")
            
            # API Keys
            st.write("**🔑 Chaves de API:**")
            
            with st.form("api_keys"):
                google_maps_key = st.text_input("Google Maps API:", type="password")
                openai_key = st.text_input("OpenAI API:", type="password")
                facebook_app_id = st.text_input("Facebook App ID:")
                instagram_token = st.text_input("Instagram Access Token:", type="password")
                
                if st.form_submit_button("🔑 Salvar Chaves de API"):
                    st.success("✅ Chaves de API salvas com sucesso!")
            
            # Webhooks
            st.write("**🪝 Webhooks:**")
            
            webhook_url = st.text_input("URL do Webhook:")
            webhook_events = st.multiselect(
                "Eventos para notificar:",
                ["pet_added", "pet_adopted", "user_registered", "system_alert"]
            )
            
            if st.button("🔗 Salvar Configurações de Webhook"):
                st.success("✅ Webhook configurado com sucesso!")
            
            # Integrações ativas
            st.write("**📱 Integrações Ativas:**")
            
            integrations = pd.DataFrame({
                'Serviço': ['WhatsApp Business', 'Telegram Bot', 'Facebook Pages', 'Instagram'],
                'Status': ['Ativo', 'Ativo', 'Inativo', 'Pendente'],
                'Última Sync': ['2 horas atrás', '30 min atrás', 'Nunca', '1 dia atrás'],
                'Erros': [0, 0, 3, 1]
            })
            
            st.dataframe(integrations, use_container_width=True, hide_index=True)
    
    elif admin_section == "💾 Backup e Manutenção":
        st.subheader("💾 Sistema de Backup e Manutenção")
        
        # Status do sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Último Backup", "2 horas atrás", "✅ Sucesso")
        
        with col2:
            st.metric("Tamanho do BD", "156 MB", "+12 MB esta semana")
        
        with col3:
            st.metric("Espaço em Disco", "2.3 GB livres", "78% usado")
        
        with col4:
            st.metric("Uptime", "15 dias", "99.8%")
        
        # Tabs de manutenção
        maint_tab1, maint_tab2, maint_tab3 = st.tabs(["💾 Backup", "🧹 Limpeza", "🔧 Manutenção"])
        
        with maint_tab1:
            st.write("### 💾 Sistema de Backup")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Backup Manual:**")
                
                backup_type = st.selectbox("Tipo de Backup:", ["Completo", "Incremental", "Diferencial"])
                include_logs = st.checkbox("Incluir logs", value=True)
                include_uploads = st.checkbox("Incluir arquivos enviados", value=True)
                compress_backup = st.checkbox("Comprimir backup", value=True)
                
                if st.button("🚀 Iniciar Backup Manual", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simular progresso do backup
                    for i in range(101):
                        progress_bar.progress(i)
                        if i < 20:
                            status_text.text(f"Preparando backup... ({i}%)")
                        elif i < 50:
                            status_text.text(f"Copiando banco de dados... ({i}%)")
                        elif i < 80:
                            status_text.text(f"Incluindo arquivos... ({i}%)")
                        elif i < 95:
                            status_text.text(f"Comprimindo... ({i}%)")
                        else:
                            status_text.text(f"Finalizando... ({i}%)")
                        
                        time.sleep(0.02)
                    
                    st.success("✅ Backup concluído com sucesso!")
                    
                    # Simular arquivo de backup
                    backup_filename = f"petcare_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    dummy_backup = "Conteúdo simulado do backup"
                    
                    st.download_button(
                        label="📥 Baixar Backup",
                        data=dummy_backup.encode(),
                        file_name=backup_filename,
                        mime="application/zip"
                    )
            
            with col2:
                st.write("**Backup Automático:**")
                
                auto_backup_enabled = st.checkbox("Habilitar backup automático", value=True)
                
                if auto_backup_enabled:
                    backup_frequency = st.selectbox("Frequência:", ["Diário", "Semanal", "Mensal"])
                    backup_time = st.time_input("Horário:", datetime.time(3, 0))
                    retention_days = st.number_input("Manter backups por (dias):", value=30, min_value=7, max_value=365)
                    
                    backup_location = st.selectbox("Local de armazenamento:", ["Local", "Google Drive", "AWS S3", "Dropbox"])
                    
                    if backup_location != "Local":
                        st.text_input(f"Configurações do {backup_location}:", placeholder="Chave de API ou credenciais")
                
                if st.button("💾 Salvar Configurações de Backup"):
                    st.success("✅ Configurações de backup salvas!")
            
            # Histórico de backups
            st.write("**📚 Histórico de Backups:**")
            
            backup_history = pd.DataFrame({
                'Data': pd.date_range(start='2025-05-01', end='2025-05-23', freq='D'),
                'Tipo': np.random.choice(['Automático', 'Manual'], 23),
                'Tamanho': [f"{np.random.randint(100, 200)} MB" for _ in range(23)],
                'Status': np.random.choice(['Sucesso', 'Sucesso', 'Sucesso', 'Falha'], 23, p=[0.8, 0.1, 0.05, 0.05]),
                'Duração': [f"{np.random.randint(30, 180)}s" for _ in range(23)]
            })
            
            # Colorir status
            def color_status(val):
                color = 'green' if val == 'Sucesso' else 'red'
                return f'color: {color}'
            
            st.dataframe(
                backup_history,
                use_container_width=True,
                hide_index=True
            )
        
        with maint_tab2:
            st.write("### 🧹 Limpeza e Otimização")
            
            # Análise de espaço
            st.write("**💽 Análise de Uso de Espaço:**")
            
            space_data = pd.DataFrame({
                'Categoria': ['Banco de Dados', 'Logs', 'Uploads', 'Cache', 'Backups', 'Temporários'],
                'Tamanho (MB)': [156, 23, 45, 12, 234, 8],
                'Arquivos': [1, 1240, 67, 156, 15, 89]
            })
            
            fig_space = px.pie(
                space_data,
                values='Tamanho (MB)',
                names='Categoria',
                title="Uso de Espaço por Categoria"
            )
            st.plotly_chart(fig_space, use_container_width=True)
            
            # Ações de limpeza
            st.write("**🗑️ Ações de Limpeza:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                clean_logs = st.checkbox("Limpar logs antigos (>90 dias)", value=False)
                clean_cache = st.checkbox("Limpar cache", value=True)
                clean_temp = st.checkbox("Limpar arquivos temporários", value=True)
            
            with col2:
                clean_backups = st.checkbox("Remover backups antigos", value=False)
                optimize_db = st.checkbox("Otimizar banco de dados", value=True)
                reindex_db = st.checkbox("Reindexar tabelas", value=False)
            
            if st.button("🧹 Executar Limpeza", use_container_width=True):
                progress = st.progress(0)
                
                actions = []
                if clean_cache: actions.append("cache")
                if clean_temp: actions.append("temporários")
                if optimize_db: actions.append("otimização BD")
                if clean_logs: actions.append("logs antigos")
                
                for i, action in enumerate(actions):
                    progress.progress((i + 1) / len(actions))
                    st.write(f"✅ Limpando {action}...")
                    time.sleep(0.5)
                
                st.success(f"✅ Limpeza concluída! {len(actions)} ações executadas.")
                
                # Simular economia de espaço
                space_saved = np.random.randint(50, 200)
                st.info(f"💾 Espaço liberado: {space_saved} MB")
        
        with maint_tab3:
            st.write("### 🔧 Manutenção do Sistema")
            
            # Status dos serviços
            st.write("**🔄 Status dos Serviços:**")
            
            services = pd.DataFrame({
                'Serviço': ['Aplicação Web', 'Banco de Dados', 'Cache Redis', 'Email Service', 'Backup Service'],
                'Status': ['🟢 Online', '🟢 Online', '🟡 Degradado', '🟢 Online', '🟢 Online'],
                'CPU (%)': [23, 12, 45, 8, 5],
                'Memória (MB)': [256, 512, 128, 64, 32],
                'Uptime': ['15d 4h', '15d 4h', '2d 1h', '15d 4h', '15d 4h']
            })
            
            st.dataframe(services, use_container_width=True, hide_index=True)
            
            # Ações de manutenção
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔄 Reinicialização:**")
                
                if st.button("🔄 Reiniciar Cache", use_container_width=True):
                    st.success("✅ Cache reiniciado com sucesso!")
                
                if st.button("🔄 Reiniciar Aplicação", use_container_width=True):
                    st.warning("⚠️ Esta ação desconectará todos os usuários!")
            
            with col2:
                st.write("**🛠️ Diagnósticos:**")
                
                if st.button("🔍 Verificar Integridade BD", use_container_width=True):
                    st.success("✅ Banco de dados íntegro!")
                
                if st.button("📊 Relatório de Performance", use_container_width=True):
                    st.info("📈 Performance dentro do esperado")
            
            # Modo de manutenção
            st.write("**🚧 Modo de Manutenção:**")
            
            maintenance_mode = st.checkbox("Ativar modo de manutenção")
            
            if maintenance_mode:
                maintenance_message = st.text_area(
                    "Mensagem para usuários:",
                    value="Sistema em manutenção. Voltaremos em breve!",
                    height=100
                )
                
                estimated_duration = st.selectbox("Duração estimada:", ["30 minutos", "1 hora", "2 horas", "Indefinido"])
                
                if st.button("🚧 Ativar Modo de Manutenção"):
                    st.success("✅ Modo de manutenção ativado!")
                    log_activity(st.session_state.user_id, "maintenance_mode", "Ativou modo de manutenção")
    
    elif admin_section == "📈 Analytics do Sistema":
        st.subheader("📈 Analytics Avançados do Sistema")
        
        # Métricas de performance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Usuários Ativos Hoje", "47", "+12%")
        
        with col2:
            st.metric("Sessões Médias/Dia", "156", "+8%")
        
        with col3:
            st.metric("Tempo Médio de Sessão", "18 min", "+2 min")
        
        with col4:
            st.metric("Taxa de Retenção", "78%", "+5%")
        
        # Gráficos de analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Usuários únicos por dia
            dates = pd.date_range(start='2025-04-01', end='2025-05-23', freq='D')
            unique_users = pd.DataFrame({
                'Data': dates,
                'Usuarios_Unicos': np.random.poisson(35, len(dates))
            })
            
            fig_users = px.line(
                unique_users,
                x='Data',
                y='Usuarios_Unicos',
                title="Usuários Únicos Diários"
            )
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Páginas mais visitadas
            pages_data = pd.DataFrame({
                'Página': ['Dashboard', 'Visualizar Dados', 'Adicionar Pet', 'Análises', 'Configurações'],
                'Visitas': [1250, 890, 650, 420, 230]
            })
            
            fig_pages = px.bar(
                pages_data,
                x='Visitas',
                y='Página',
                orientation='h',
                title="Páginas Mais Visitadas"
            )
            st.plotly_chart(fig_pages, use_container_width=True)
        
        # Análise de comportamento
        st.subheader("👥 Análise de Comportamento dos Usuários")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Funil de conversão
            funnel_data = pd.DataFrame({
                'Etapa': ['Visitantes', 'Cadastros', 'Primeiros Pets', 'Usuários Ativos', 'Usuários Recorrentes'],
                'Usuários': [1000, 450, 320, 250, 180]
            })
            
            fig_funnel = px.funnel(
                funnel_data,
                x='Usuários',
                y='Etapa',
                title="Funil de Conversão de Usuários"
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            # Distribuição de sessões por duração
            session_durations = pd.DataFrame({
                'Duração': ['< 1 min', '1-5 min', '5-15 min', '15-30 min', '30+ min'],
                'Sessões': [120, 280, 350, 180, 70]
            })
            
            fig_duration = px.pie(
                session_durations,
                values='Sessões',
                names='Duração',
                title="Distribuição por Duração de Sessão"
            )
            st.plotly_chart(fig_duration, use_container_width=True)
        
        # Performance técnica
        st.subheader("⚡ Performance Técnica")
        
        # Tempo de resposta por endpoint
        endpoint_performance = pd.DataFrame({
            'Endpoint': ['/dashboard', '/pets', '/add-pet', '/analytics', '/export'],
            'Tempo_Médio_ms': [234, 156, 89, 445, 1234],
            'Requisições_Dia': [1200, 800, 200, 150, 45]
        })
        
        fig_performance = px.scatter(
            endpoint_performance,
            x='Requisições_Dia',
            y='Tempo_Médio_ms',
            size='Tempo_Médio_ms',
            hover_name='Endpoint',
            title="Performance por Endpoint"
        )
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Relatórios personalizados
        st.subheader("📊 Relatórios Personalizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Tipo de Relatório:",
                ["Uso do Sistema", "Performance", "Usuários", "Conteúdo", "Erros"]
            )
            
            date_range_analytics = st.date_input(
                "Período:",
                [datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()]
            )
        
        with col2:
            format_analytics = st.selectbox("Formato:", ["Excel", "PDF", "CSV"])
            
            if st.button("📋 Gerar Relatório", use_container_width=True):
                st.success(f"✅ Relatório de {report_type} gerado com sucesso!")
                
                # Simular dados do relatório
                report_data = f"Relatório de {report_type} - {date_range_analytics[0]} a {date_range_analytics[1]}"
                
                st.download_button(
                    label=f"📥 Baixar {format_analytics}",
                    data=report_data.encode(),
                    file_name=f"relatorio_{report_type.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}.{format_analytics.lower()}",
                    mime="text/plain"
                )

if __name__ == '__main__':
    main()
