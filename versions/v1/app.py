
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk
import altair as alt
from PIL import Image
import os
import json
import requests
import base64
from io import StringIO
import time

# Análises estatísticas avançadas
from scipy import stats
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import silhouette_score

# Processamento de linguagem natural
import nltk
from wordcloud import WordCloud
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# Integração com Google Gemini AI
import google.generativeai as genai

# Evitar avisos
import warnings
warnings.filterwarnings('ignore')

# Inicializar NLTK (opcional)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
    except:
        pass

# Configuração da página
st.set_page_config(
    page_title="PetCare Analytics",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avançados
st.markdown("""
<style>
/* Estilo base */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Ajustes para o tema claro/escuro */
@media (prefers-color-scheme: dark) {
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .st-bx {
        background-color: #262730;
    }
    .css-1544g2n {
        padding: 2rem 1rem;
    }
}

@media (prefers-color-scheme: light) {
    .main {
        background-color: #f5f7f9;
        color: #262730;
    }
    .st-bx {
        background-color: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
}

/* Card com sombra e borda arredondada */
.card {
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    background-color: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Tabelas mais elegantes */
.dataframe {
    border-collapse: collapse;
    border-radius: 8px;
    overflow: hidden;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: 'Inter', sans-serif;
    min-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}

.dataframe thead tr {
    background-color: #4e7fff;
    color: #ffffff;
    text-align: left;
    font-weight: bold;
}

.dataframe th, .dataframe td {
    padding: 12px 15px;
}

.dataframe tbody tr {
    border-bottom: 1px solid #dddddd;
}

.dataframe tbody tr:nth-of-type(even) {
    background-color: rgba(0, 0, 0, 0.03);
}

.dataframe tbody tr:last-of-type {
    border-bottom: 2px solid #4e7fff;
}

/* Título e cabeçalhos elegantes */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: #2c3e50;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 {
    font-size: 2.5rem;
    border-bottom: 3px solid #4e7fff;
    padding-bottom: 10px;
    margin-bottom: 1em;
    background: linear-gradient(90deg, #4e7fff, #6edae5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2 {
    font-size: 1.8rem;
    color: #3d5a80;
    border-left: 4px solid #4e7fff;
    padding-left: 10px;
}

h3 {
    font-size: 1.4rem;
    color: #293241;
}

/* Botões estilizados */
.stButton>button {
    background-color: #4e7fff;
    color: white;
    font-weight: 500;
    padding: 0.6em 1.2em;
    border: none;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: #3a68e0;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* Métricas mais destacadas */
div[data-testid="metric-container"] {
    background-color: rgba(78, 127, 255, 0.1);
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

div[data-testid="metric-container"] > div {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

div[data-testid="stMetricValue"] > div {
    font-size: 2.2rem !important;
    font-weight: 800;
    color: #4e7fff;
}

div[data-testid="stMetricLabel"] {
    font-size: 1rem;
    font-weight: 500;
    color: #555;
}

/* Abas estilizadas */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 10px;
    padding: 5px;
}

.stTabs [data-baseweb="tab"] {
    height: 40px;
    border-radius: 8px;
    color: #666;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #4e7fff;
    color: white;
}

/* Barra lateral */
.css-1d391kg, .css-163ttbj, .sidebar-content {
    background-color: #f8f9fa;
}

/* Tooltips */
.tooltip {
    position: relative;
    display: inline-block;
    border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

/* Animações */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.st-emotion-cache-1y4p8pa {
    animation: fadeIn 0.5s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# Configurar API Google Gemini
GEMINI_API_KEY = "AIzaSyAv0uCuLKv7FH71OP4v2u58rdGukDP8K9c"
genai.configure(api_key=GEMINI_API_KEY)

# Configuração global
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# Funções utilitárias
def create_data_directory():
    """Cria diretório de dados se não existir"""
    os.makedirs('data', exist_ok=True)

def load_image(image_path):
    """Carrega uma imagem do caminho especificado"""
    try:
        return Image.open(image_path)
    except:
        return None

def get_pet_icon(pet_type):
    """Retorna emojis baseados no tipo de pet"""
    icons = {
        'Cachorro': '🐕',
        'Gato': '🐈',
        'Ave': '🦜',
        'Peixe': '🐠',
        'Roedor': '🐹',
        'Réptil': '🦎'
    }
    return icons.get(pet_type, '🐾')

# Função para chamar a API Gemini
def analisar_com_ia(dados, pergunta, temperatura=0.7):
    """Analisa dados usando Google Gemini API com temperatura ajustável"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Preparar dados para envio à API
        df_info = dados.describe().to_string()
        dados_resumo = dados.head(50).to_csv(index=False)
        
        prompt = f"""
        # Análise de Dados de Pets em Florianópolis

        ## Resumo dos Dados
        {df_info}
        
        ## Amostra dos Dados (primeiras 50 linhas)
        {dados_resumo}
        
        ## Tarefa de Análise
        {pergunta}
        
        Seu objetivo é fornecer uma análise profunda e insights valiosos baseados nos dados fornecidos.
        Considere tendências, padrões, correlações e anomalias nos dados.
        
        Sua resposta deve:
        1. Incluir insights específicos apoiados em dados
        2. Destacar padrões importantes
        3. Sugerir ações práticas baseadas na análise
        4. Usar linguagem simples e clara
        5. Ser estruturada com subseções para facilitar a leitura
        
        Responda em português do Brasil, por favor.
        """
        
        generation_config = {
            "temperature": temperatura,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"Erro ao chamar a API Gemini: {str(e)}"

# Função para análise de sentimento
def analyze_sentiment(text):
    """Analisa o sentimento de um texto usando TextBlob"""
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.3:
            return "Positivo", polarity
        elif polarity < -0.3:
            return "Negativo", polarity
        else:
            return "Neutro", polarity
    except:
        return "Erro na análise", 0

# Criar ou carregar dados de exemplo
def carregar_dados():
    """Carrega dados existentes ou cria um conjunto de dados de exemplo"""
    try:
        create_data_directory()
        return pd.read_csv('data/pets_data.csv')
    except:
        # Criar dataset de exemplo
        bairros_florianopolis = [
            'Centro', 'Trindade', 'Itacorubi', 'Córrego Grande', 'Santa Mônica',
            'Pantanal', 'Carvoeira', 'Saco dos Limões', 'Costeira do Pirajubaé',
            'José Mendes', 'Prainha', 'Saco Grande', 'João Paulo', 'Monte Verde',
            'Cacupé', 'Santo Antônio de Lisboa', 'Sambaqui', 'Daniela', 'Jurerê',
            'Canasvieiras', 'Cachoeira do Bom Jesus', 'Ponta das Canas', 'Lagoinha',
            'Praia Brava', 'Ingleses', 'Santinho', 'Rio Vermelho', 'Barra da Lagoa',
            'Lagoa da Conceição', 'Joaquina', 'Campeche', 'Morro das Pedras', 'Armação',
            'Pântano do Sul', 'Ribeirão da Ilha', 'Caiacangaçu', 'Tapera', 'Carianos',
            'Ressacada', 'Abraão', 'Coqueiros', 'Itaguaçu', 'Bom Abrigo', 'Estreito',
            'Balneário', 'Jardim Atlântico', 'Coloninha', 'Capoeiras'
        ]
        
        # Para densidade populacional (fictícia)
        densidade_populacional = {
            'Centro': 95, 'Trindade': 85, 'Itacorubi': 65, 'Córrego Grande': 60,
            'Santa Mônica': 70, 'Pantanal': 50, 'Carvoeira': 60, 'Saco dos Limões': 65,
            'Costeira do Pirajubaé': 55, 'José Mendes': 45, 'Prainha': 60, 'Saco Grande': 40,
            'João Paulo': 45, 'Monte Verde': 35, 'Cacupé': 25, 'Santo Antônio de Lisboa': 30,
            'Sambaqui': 20, 'Daniela': 15, 'Jurerê': 35, 'Canasvieiras': 40,
            'Cachoeira do Bom Jesus': 30, 'Ponta das Canas': 25, 'Lagoinha': 20,
            'Praia Brava': 25, 'Ingleses': 50, 'Santinho': 30, 'Rio Vermelho': 35,
            'Barra da Lagoa': 40, 'Lagoa da Conceição': 55, 'Joaquina': 15,
            'Campeche': 45, 'Morro das Pedras': 30, 'Armação': 25, 'Pântano do Sul': 20,
            'Ribeirão da Ilha': 30, 'Caiacangaçu': 15, 'Tapera': 45, 'Carianos': 50,
            'Ressacada': 30, 'Abraão': 60, 'Coqueiros': 70, 'Itaguaçu': 50,
            'Bom Abrigo': 55, 'Estreito': 80, 'Balneário': 75, 'Jardim Atlântico': 65,
            'Coloninha': 70, 'Capoeiras': 75
        }
        
        # Categorias de região
        regiao_por_bairro = {
            'Centro': 'Centro', 'Trindade': 'Centro', 'Itacorubi': 'Centro-Leste', 
            'Córrego Grande': 'Centro-Leste', 'Santa Mônica': 'Centro-Leste',
            'Pantanal': 'Centro-Leste', 'Carvoeira': 'Centro', 'Saco dos Limões': 'Centro-Sul',
            'Costeira do Pirajubaé': 'Centro-Sul', 'José Mendes': 'Centro-Sul', 'Prainha': 'Centro',
            'Saco Grande': 'Norte', 'João Paulo': 'Norte', 'Monte Verde': 'Norte',
            'Cacupé': 'Norte', 'Santo Antônio de Lisboa': 'Norte', 'Sambaqui': 'Norte',
            'Daniela': 'Norte', 'Jurerê': 'Norte', 'Canasvieiras': 'Norte',
            'Cachoeira do Bom Jesus': 'Norte', 'Ponta das Canas': 'Norte', 'Lagoinha': 'Norte',
            'Praia Brava': 'Norte', 'Ingleses': 'Norte', 'Santinho': 'Norte',
            'Rio Vermelho': 'Leste', 'Barra da Lagoa': 'Leste', 'Lagoa da Conceição': 'Leste',
            'Joaquina': 'Leste', 'Campeche': 'Sul', 'Morro das Pedras': 'Sul',
            'Armação': 'Sul', 'Pântano do Sul': 'Sul', 'Ribeirão da Ilha': 'Sul',
            'Caiacangaçu': 'Sul', 'Tapera': 'Sul', 'Carianos': 'Sul',
            'Ressacada': 'Sul', 'Abraão': 'Continental', 'Coqueiros': 'Continental',
            'Itaguaçu': 'Continental', 'Bom Abrigo': 'Continental', 'Estreito': 'Continental',
            'Balneário': 'Continental', 'Jardim Atlântico': 'Continental', 'Coloninha': 'Continental',
            'Capoeiras': 'Continental'
        }
        
        # Renda média por bairro (fictícia)
        renda_media = {
            'Centro': 8500, 'Trindade': 7800, 'Itacorubi': 8200, 'Córrego Grande': 7900,
            'Santa Mônica': 9500, 'Pantanal': 5600, 'Carvoeira': 6300, 'Saco dos Limões': 5200,
            'Costeira do Pirajubaé': 4300, 'José Mendes': 4800, 'Prainha': 6700, 'Saco Grande': 5100,
            'João Paulo': 7400, 'Monte Verde': 5600, 'Cacupé': 12500, 'Santo Antônio de Lisboa': 9800,
            'Sambaqui': 8600, 'Daniela': 15800, 'Jurerê': 18700, 'Canasvieiras': 7600,
            'Cachoeira do Bom Jesus': 6500, 'Ponta das Canas': 5900, 'Lagoinha': 6800,
            'Praia Brava': 10800, 'Ingleses': 6300, 'Santinho': 5800, 'Rio Vermelho': 5200,
            'Barra da Lagoa': 6900, 'Lagoa da Conceição': 9800, 'Joaquina': 6200,
            'Campeche': 7500, 'Morro das Pedras': 6200, 'Armação': 7100, 'Pântano do Sul': 5300,
            'Ribeirão da Ilha': 4900, 'Caiacangaçu': 4200, 'Tapera': 3800, 'Carianos': 5600,
            'Ressacada': 4900, 'Abraão': 6200, 'Coqueiros': 7800, 'Itaguaçu': 8900,
            'Bom Abrigo': 8500, 'Estreito': 5900, 'Balneário': 6300, 'Jardim Atlântico': 5800,
            'Coloninha': 4900, 'Capoeiras': 5300
        }
        
        tipos_pet = ['Cachorro', 'Gato', 'Ave', 'Peixe', 'Roedor', 'Réptil']
        racas_cachorro = ['Vira-lata', 'Poodle', 'Labrador', 'Golden Retriever', 'Bulldog', 'Pitbull', 'Shih Tzu', 'Yorkshire', 'Pastor Alemão', 'Pinscher']
        racas_gato = ['SRD', 'Siamês', 'Persa', 'Maine Coon', 'Ragdoll', 'Sphynx', 'Angorá', 'Bengal', 'British Shorthair', 'Norueguês da Floresta']
        racas_ave = ['Canário', 'Periquito', 'Calopsita', 'Papagaio', 'Arara', 'Agapornis', 'Mandarim']
        racas_peixe = ['Betta', 'Kinguio', 'Guppy', 'Tetra', 'Acará', 'Coridora', 'Pleco']
        racas_roedor = ['Hamster', 'Porquinho da Índia', 'Chinchila', 'Rato', 'Gerbil']
        racas_reptil = ['Tartaruga', 'Jabuti', 'Iguana', 'Gecko', 'Cobra']
        
        tipos_comida = ['Ração Premium', 'Ração Super Premium', 'Comida Natural', 'Comida Caseira', 'Ração Medicinal', 'Mista']
        humor = ['Feliz', 'Calmo', 'Agitado', 'Ansioso', 'Entediado', 'Brincalhão', 'Agressivo', 'Medroso']
        
        # Dados de saúde e vacinação
        status_vacinacao = ['Em dia', 'Parcial', 'Pendente', 'Não se aplica']
        estado_saude = ['Excelente', 'Bom', 'Regular', 'Requer atenção']
        
        # Dados de comportamento
        comportamentos = ['Sociável', 'Tímido', 'Territorialista', 'Independente', 'Carente', 'Dominante', 'Submisso']
        nivel_atividade = ['Muito Ativo', 'Ativo', 'Moderado', 'Tranquilo', 'Sedentário']
        
        # Criar dados aleatórios mais realistas
        np.random.seed(42)  # Para reproducibilidade
        n_registros = 1000
        
        # Distribuição por bairro seguindo a densidade populacional
        probabilidades_bairro = [densidade_populacional[b]/sum(densidade_populacional.values()) for b in bairros_florianopolis]
        
        # Distribuição de pets mais realista (com variação por bairro)
        def get_tipo_probabilidades(bairro):
            """Retorna probabilidades de tipos de pet baseado no bairro"""
            renda = renda_media[bairro]
            if renda > 10000:  # Bairros mais ricos
                return [0.40, 0.35, 0.12, 0.05, 0.04, 0.04]  # Mais aves exóticas e répteis
            elif renda > 7000:  # Classe média alta
                return [0.45, 0.38, 0.08, 0.04, 0.03, 0.02]
            elif renda > 5000:  # Classe média
                return [0.48, 0.40, 0.06, 0.03, 0.02, 0.01]
            else:  # Classe média baixa
                return [0.55, 0.40, 0.03, 0.01, 0.01, 0.00]  # Mais cachorros e gatos
        
        # Lista para armazenar dados
        data = {
            'nome': [f'Pet{i}' for i in range(1, n_registros+1)],
            'bairro': np.random.choice(bairros_florianopolis, n_registros, p=probabilidades_bairro),
            'tipo_pet': [],
            'raca': [],
            'idade': [],
            'peso': [],
            'sexo': np.random.choice(['Macho', 'Fêmea'], n_registros),
            'tipo_comida': [],
            'humor_diario': np.random.choice(humor, n_registros),
            'adotado': [],
            'telefone': [f'(48) 9{np.random.randint(8000, 10000)}-{np.random.randint(1000, 10000)}' for _ in range(n_registros)],
            'status_vacinacao': [],
            'estado_saude': [],
            'comportamento': np.random.choice(comportamentos, n_registros),
            'nivel_atividade': [],
            'data_registro': pd.date_range(start='2023-01-01', periods=n_registros, freq='D'),
            'regiao': [],
            'renda_media_bairro': []
        }
        
        # Preencher dados baseados em correlações realistas
        for i in range(n_registros):
            bairro = data['bairro'][i]
            
            # Adicionar região e renda média
            data['regiao'].append(regiao_por_bairro[bairro])
            data['renda_media_bairro'].append(renda_media[bairro])
            
            # Tipo de pet baseado em renda do bairro
            tipo_probs = get_tipo_probabilidades(bairro)
            tipo = np.random.choice(tipos_pet, p=tipo_probs)
            data['tipo_pet'].append(tipo)
            
            # Adoção mais comum em bairros de menor renda
            prob_adocao = max(0.1, min(0.7, 1 - (renda_media[bairro] / 20000)))
            data['adotado'].append(np.random.choice([True, False], p=[prob_adocao, 1-prob_adocao]))
            
            # Status de vacinação correlacionado com renda
            if renda_media[bairro] > 10000:
                vac_probs = [0.85, 0.10, 0.02, 0.03]  # Mais em dia
            elif renda_media[bairro] > 7000:
                vac_probs = [0.75, 0.15, 0.05, 0.05]
            elif renda_media[bairro] > 5000:
                vac_probs = [0.65, 0.20, 0.10, 0.05]
            else:
                vac_probs = [0.50, 0.25, 0.20, 0.05]  # Menos em dia
                
            data['status_vacinacao'].append(np.random.choice(status_vacinacao, p=vac_probs))
            
            # Raça baseada no tipo de pet
            if tipo == 'Cachorro':
                # Probabilidade de vira-lata maior para adotados
                if data['adotado'][i]:
                    raca_probs = [0.6, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.03, 0.02]
                else:
                    raca_probs = [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05]
                data['raca'].append(np.random.choice(racas_cachorro, p=raca_probs))
                
                # Idade (cachorros adotados tendem a ser mais velhos)
                if data['adotado'][i]:
                    data['idade'].append(np.random.randint(2, 12))
                else:
                    data['idade'].append(np.random.randint(1, 15))
                
                # Peso baseado na raça
                raca_atual = data['raca'][i]
                if raca_atual in ['Vira-lata', 'Pinscher', 'Yorkshire']:
                    data['peso'].append(round(np.random.uniform(2, 15), 1))
                elif raca_atual in ['Poodle', 'Shih Tzu']:
                    data['peso'].append(round(np.random.uniform(4, 12), 1))
                elif raca_atual in ['Bulldog', 'Pitbull']:
                    data['peso'].append(round(np.random.uniform(15, 30), 1))
                else:  # Raças maiores
                    data['peso'].append(round(np.random.uniform(20, 45), 1))
                
                # Nível de atividade baseado na raça
                if raca_atual in ['Labrador', 'Golden Retriever', 'Pastor Alemão']:
                    data['nivel_atividade'].append(np.random.choice(['Muito Ativo', 'Ativo'], p=[0.7, 0.3]))
                elif raca_atual in ['Bulldog']:
                    data['nivel_atividade'].append(np.random.choice(['Tranquilo', 'Sedentário'], p=[0.6, 0.4]))
                else:
                    data['nivel_atividade'].append(np.random.choice(nivel_atividade))
                
                # Tipo de comida mais provável baseado na renda e raça
                if renda_media[bairro] > 10000 or raca_atual in ['Golden Retriever', 'Labrador']:
                    data['tipo_comida'].append(np.random.choice(tipos_comida, p=[0.1, 0.5, 0.2, 0.1, 0.05, 0.05]))
                elif renda_media[bairro] > 6000:
                    data['tipo_comida'].append(np.random.choice(tipos_comida, p=[0.3, 0.3, 0.15, 0.15, 0.05, 0.05]))
                else:
                    data['tipo_comida'].append(np.random.choice(tipos_comida, p=[0.5, 0.1, 0.1, 0.2, 0.05, 0.05]))
                
            elif tipo == 'Gato':
                # SRD mais comum em adotados
                if data['adotado'][i]:
                    data['raca'].append(np.random.choice(racas_gato, p=[0.7, 0.05, 0.05, 0.05, 0.05, 0.03, 0.03, 0.02, 0.01, 0.01]))
                else:
                    data['raca'].append(np.random.choice(racas_gato, p=[0.3, 0.1, 0.1, 0.1, 0.1, 0.08, 0.08, 0.06, 0.04, 0.04]))
                
                # Idade
                data['idade'].append(np.random.randint(1, 18))
                
                # Peso
                data['peso'].append(round(np.random.uniform(2.5, 8.5), 1))
                
                # Nível de atividade (gatos tendem a ser mais independentes)
                data['nivel_atividade'].append(np.random.choice(nivel_atividade, p=[0.15, 0.25, 0.3, 0.2, 0.1]))
                
                # Tipo de comida
                if renda_media[bairro] > 8000:
                    data['tipo_comida'].append(np.random.choice(tipos_comida, p=[0.2, 0.4, 0.2, 0.1, 0.05, 0.05]))
                else:
                    data['tipo_comida'].append(np.random.choice(tipos_comida, p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05]))
                
            elif tipo == 'Ave':
                data['raca'].append(np.random.choice(racas_ave))
                data['idade'].append(np.random.randint(1, 10))
                data['peso'].append(round(np.random.uniform(0.1, 2.0), 1))
                data['nivel_atividade'].append(np.random.choice(nivel_atividade, p=[0.1, 0.2, 0.4, 0.2, 0.1]))
                data['tipo_comida'].append(np.random.choice(tipos_comida))
                
            elif tipo == 'Peixe':
                data['raca'].append(np.random.choice(racas_peixe))
                data['idade'].append(np.random.randint(1, 5))
                data['peso'].append(round(np.random.uniform(0.01, 1.0), 2))
                data['nivel_atividade'].append(np.random.choice(['Ativo', 'Moderado', 'Tranquilo'], p=[0.3, 0.4, 0.3]))
                data['tipo_comida'].append('Ração Premium')
                
            elif tipo == 'Roedor':
                data['raca'].append(np.random.choice(racas_roedor))
                data['idade'].append(np.random.randint(1, 4))
                data['peso'].append(round(np.random.uniform(0.1, 2.0), 1))
                data['nivel_atividade'].append(np.random.choice(['Muito Ativo', 'Ativo', 'Moderado'], p=[0.5, 0.3, 0.2]))
                data['tipo_comida'].append(np.random.choice(tipos_comida))
                
            else:  # Réptil
                data['raca'].append(np.random.choice(racas_reptil))
                data['idade'].append(np.random.randint(1, 20))
                raca_atual = data['raca'][i]
                if raca_atual in ['Tartaruga', 'Jabuti']:
                    data['peso'].append(round(np.random.uniform(0.5, 10.0), 1))
                else:
                    data['peso'].append(round(np.random.uniform(0.1, 5.0), 1))
                data['nivel_atividade'].append(np.random.choice(['Tranquilo', 'Sedentário'], p=[0.3, 0.7]))
                data['tipo_comida'].append(np.random.choice(['Ração Premium', 'Comida Natural', 'Mista']))
            
            # Estado de saúde correlacionado com renda, vacinação
            status_vac = data['status_vacinacao'][i]
            if status_vac == 'Em dia':
                data['estado_saude'].append(np.random.choice(estado_saude, p=[0.6, 0.3, 0.08, 0.02]))
            elif status_vac == 'Parcial':
                data['estado_saude'].append(np.random.choice(estado_saude, p=[0.3, 0.4, 0.2, 0.1]))
            elif status_vac == 'Pendente':
                data['estado_saude'].append(np.random.choice(estado_saude, p=[0.1, 0.3, 0.4, 0.2]))
            else:  # Não se aplica
                data['estado_saude'].append(np.random.choice(estado_saude))
        
        df = pd.DataFrame(data)
        
        # Adicionar alguns dados faltantes para simular dados reais
        for col in ['peso', 'idade', 'status_vacinacao', 'estado_saude']:
            mask = np.random.random(len(df)) < 0.03  # 3% de dados faltantes
            df.loc[mask, col] = np.nan
        
        # Salvar o dataset
        create_data_directory()
        df.to_csv('data/pets_data.csv', index=False)
        return df

# Adicionar novo pet ao conjunto de dados
def adicionar_pet(novo_pet, df):
    """Adiciona um novo pet ao dataframe e salva no CSV"""
    df_novo = pd.DataFrame([novo_pet])
    df = pd.concat([df, df_novo], ignore_index=True)
    df.to_csv('data/pets_data.csv', index=False)
    return df

# Coordenadas aproximadas dos bairros de Florianópolis
def coordenadas_bairros():
    """Retorna dicionário com coordenadas dos bairros de Florianópolis"""
    return {
        'Centro': [-48.5489, -27.5945],
        'Trindade': [-48.5182, -27.5886],
        'Itacorubi': [-48.5010, -27.5780],
        'Córrego Grande': [-48.5075, -27.6010],
        'Santa Mônica': [-48.5120, -27.5915],
        'Pantanal': [-48.5246, -27.6154],
        'Carvoeira': [-48.5258, -27.6012],
        'Saco dos Limões': [-48.5397, -27.6106],
        'Costeira do Pirajubaé': [-48.5232, -27.6275],
        'José Mendes': [-48.5493, -27.6128],
        'Prainha': [-48.5512, -27.6019],
        'Saco Grande': [-48.5019, -27.5541],
        'João Paulo': [-48.5195, -27.5647],
        'Monte Verde': [-48.5082, -27.5665],
        'Cacupé': [-48.5387, -27.5432],
        'Santo Antônio de Lisboa': [-48.5278, -27.5070],
        'Sambaqui': [-48.5313, -27.4925],
        'Daniela': [-48.5325, -27.4447],
        'Jurerê': [-48.5000, -27.4367],
        'Canasvieiras': [-48.4750, -27.4267],
        'Cachoeira do Bom Jesus': [-48.4500, -27.4083],
        'Ponta das Canas': [-48.4325, -27.3983],
        'Lagoinha': [-48.4175, -27.3883],
        'Praia Brava': [-48.4000, -27.3700],
        'Ingleses': [-48.3900, -27.4350],
        'Santinho': [-48.3800, -27.4550],
        'Rio Vermelho': [-48.4100, -27.5100],
        'Barra da Lagoa': [-48.4214, -27.5731],
        'Lagoa da Conceição': [-48.4681, -27.6044],
        'Joaquina': [-48.4500, -27.6300],
        'Campeche': [-48.4900, -27.6800],
        'Morro das Pedras': [-48.5100, -27.7100],
        'Armação': [-48.5250, -27.7450],
        'Pântano do Sul': [-48.5150, -27.7800],
        'Ribeirão da Ilha': [-48.5650, -27.7150],
        'Caiacangaçu': [-48.5550, -27.6950],
        'Tapera': [-48.5750, -27.6750],
        'Carianos': [-48.5550, -27.6550],
        'Ressacada': [-48.5650, -27.6650],
        'Abraão': [-48.5850, -27.6050],
        'Coqueiros': [-48.5750, -27.6050],
        'Itaguaçu': [-48.5850, -27.5950],
        'Bom Abrigo': [-48.5850, -27.5850],
        'Estreito': [-48.5950, -27.5800],
        'Balneário': [-48.6050, -27.5750],
        'Jardim Atlântico': [-48.6050, -27.5900],
        'Coloninha': [-48.6050, -27.5850],
        'Capoeiras': [-48.6150, -27.5950]
    }

# Função para realizar análises estatísticas avançadas
def realizar_analise_estatistica(df, tipo_analise, var1=None, var2=None, num_clusters=3):
    """Realiza diversos tipos de análise estatística nos dados"""
    resultado = {}
    
    if tipo_analise == "correlacao":
        # Selecionar apenas colunas numéricas
        df_num = df.select_dtypes(include=['number'])
        matriz_corr = df_num.corr()
        resultado['matriz'] = matriz_corr
        resultado['tipo'] = 'correlacao'
        
    elif tipo_analise == "clusters":
        # Selecionar as variáveis para clusterização
        if var1 is None or var2 is None:
            # Usar idade e peso como padrão
            vars_cluster = ['idade', 'peso']
        else:
            vars_cluster = [var1, var2]
        
        # Verificar se as variáveis existem e são numéricas
        vars_validas = [var for var in vars_cluster if var in df.columns and pd.api.types.is_numeric_dtype(df[var])]
        
        if len(vars_validas) < 2:
            return {"erro": "Variáveis insuficientes para clusterização"}
        
        # Preparar dados
        X = df[vars_validas].dropna()
        
        # Escalar os dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Adicionar clusters ao dataframe
        df_clusters = X.copy()
        df_clusters['cluster'] = clusters
        
        # Calcular estatísticas por cluster
        stats_clusters = df_clusters.groupby('cluster').agg(['mean', 'count'])
        
        # Preparar resultado
        resultado['df_clusters'] = df_clusters
        resultado['centros'] = kmeans.cluster_centers_
        resultado['estatisticas'] = stats_clusters
        resultado['vars_usadas'] = vars_validas
        resultado['tipo'] = 'clusters'
        
        # Calcular silhouette score
        if len(np.unique(clusters)) > 1:  # Mais de um cluster
            silhouette = silhouette_score(X_scaled, clusters)
            resultado['silhouette_score'] = silhouette
        
    elif tipo_analise == "anomalias":
        # Detectar anomalias com Isolation Forest
        # Selecionar variáveis numéricas
        df_num = df.select_dtypes(include=['number']).dropna()
        
        if df_num.shape[1] < 2:
            return {"erro": "Dados numéricos insuficientes para detecção de anomalias"}
        
        # Aplicar Isolation Forest
        clf = IsolationForest(contamination=0.05, random_state=42)
        outliers = clf.fit_predict(df_num)
        
        # Adicionar resultado ao dataframe
        df_outliers = df_num.copy()
        df_outliers['outlier'] = outliers == -1  # True para anomalias
        
        # Resumo das anomalias
        anomalias = df_outliers[df_outliers['outlier']].describe()
        normais = df_outliers[~df_outliers['outlier']].describe()
        
        resultado['df_anomalias'] = df_outliers
        resultado['resumo_anomalias'] = anomalias
        resultado['resumo_normais'] = normais
        resultado['qtd_anomalias'] = df_outliers['outlier'].sum()
        resultado['tipo'] = 'anomalias'
        
    elif tipo_analise == "regressao":
        # Análise de regressão linear
        if var1 is None or var2 is None:
            # Usar idade e peso como padrão
            x_var, y_var = 'idade', 'peso'
        else:
            x_var, y_var = var1, var2
            
        if x_var not in df.columns or y_var not in df.columns:
            return {"erro": f"Variáveis {x_var} ou {y_var} não encontradas no dataframe"}
            
        if not pd.api.types.is_numeric_dtype(df[x_var]) or not pd.api.types.is_numeric_dtype(df[y_var]):
            return {"erro": f"Variáveis {x_var} e {y_var} devem ser numéricas"}
        
        # Preparar dados
        df_reg = df[[x_var, y_var]].dropna()
        X = df_reg[x_var].values.reshape(-1, 1)
        y = df_reg[y_var].values
        
        # Dividir em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treinar modelo
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Fazer previsões
        y_pred = model.predict(X_test)
        
        # Métricas
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        resultado['coeficiente'] = model.coef_[0]
        resultado['intercepto'] = model.intercept_
        resultado['mse'] = mse
        resultado['r2'] = r2
        resultado['x_var'] = x_var
        resultado['y_var'] = y_var
        resultado['x_test'] = X_test.flatten()
        resultado['y_test'] = y_test
        resultado['y_pred'] = y_pred
        resultado['equacao'] = f"{y_var} = {model.coef_[0]:.4f} * {x_var} + {model.intercept_:.4f}"
        resultado['tipo'] = 'regressao'
    
    elif tipo_analise == "tendencia_temporal":
        # Análise de tendência ao longo do tempo
        if 'data_registro' not in df.columns:
            return {"erro": "Coluna 'data_registro' não encontrada para análise temporal"}
            
        if var1 is None:
            # Usar tipo_pet como padrão
            var_analise = 'tipo_pet'
        else:
            var_analise = var1
            
        if var_analise not in df.columns:
            return {"erro": f"Variável {var_analise} não encontrada no dataframe"}
        
        # Converter para datetime se necessário
        if not pd.api.types.is_datetime64_dtype(df['data_registro']):
            df['data_registro'] = pd.to_datetime(df['data_registro'])
        
        # Agrupar por mês
        df['mes_ano'] = df['data_registro'].dt.to_period('M')
        
        if pd.api.types.is_numeric_dtype(df[var_analise]):
            # Se variável for numérica, calcular média por mês
            tendencia = df.groupby('mes_ano')[var_analise].agg(['mean', 'count', 'std']).reset_index()
            tendencia['mes_ano'] = tendencia['mes_ano'].astype(str)
        else:
            # Se variável for categórica, contar frequência por mês e categoria
            tendencia = df.groupby(['mes_ano', var_analise]).size().unstack(fill_value=0)
            tendencia = tendencia.reset_index()
            tendencia['mes_ano'] = tendencia['mes_ano'].astype(str)
            tendencia['total'] = tendencia.iloc[:, 1:].sum(axis=1)
            
            # Converter para porcentagem
            for col in tendencia.columns:
                if col != 'mes_ano' and col != 'total':
                    tendencia[f'pct_{col}'] = tendencia[col] / tendencia['total'] * 100
        
        resultado['tendencia'] = tendencia
        resultado['var_analise'] = var_analise
        resultado['tipo'] = 'tendencia_temporal'
    
    elif tipo_analise == "analise_texto":
        # Análise de texto para colunas de texto
        if var1 is None:
            # Usar humor_diario como padrão
            var_texto = 'humor_diario'
        else:
            var_texto = var1
            
        if var_texto not in df.columns:
            return {"erro": f"Variável {var_texto} não encontrada no dataframe"}
        
        # Contar frequência das palavras
        texto_completo = ' '.join(df[var_texto].dropna().astype(str).values)
        
        # Análise de sentimento
        sentimentos = df[var_texto].dropna().apply(analyze_sentiment)
        df_sentimentos = pd.DataFrame(sentimentos.tolist(), columns=['sentimento', 'polaridade'])
        
        # Contar sentimentos
        contagem_sentimentos = df_sentimentos['sentimento'].value_counts()
        
        # Média de polaridade
        polaridade_media = df_sentimentos['polaridade'].mean()
        
        # Palavras mais comuns
        palavras = re.findall(r'w+', texto_completo.lower())
        frequencia_palavras = pd.Series(palavras).value_counts().head(20)
        
        resultado['contagem_sentimentos'] = contagem_sentimentos
        resultado['polaridade_media'] = polaridade_media
        resultado['palavras_frequentes'] = frequencia_palavras
        resultado['var_texto'] = var_texto
        resultado['texto_completo'] = texto_completo
        resultado['tipo'] = 'analise_texto'
    
    return resultado

# Função para criar visualizações personalizadas
def criar_visualizacao(df, tipo_viz, *args, **kwargs):
    """Cria visualizações personalizadas para diferentes análises"""
    if tipo_viz == "mapa_calor_correlacao":
        # Matriz de correlação
        cols = kwargs.get('cols', None)
        if cols:
            df_corr = df[cols].corr()
        else:
            df_corr = df.select_dtypes(include=['number']).corr()
        
        # Criar mapa de calor
        fig = px.imshow(
            df_corr,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale=px.colors.diverging.RdBu_r,
            title="Matriz de Correlação"
        )
        return fig
    
    elif tipo_viz == "mapa_densidade":
        # Mapa de densidade de pets por bairro
        coluna = kwargs.get('coluna', 'tipo_pet')
        valor = kwargs.get('valor', None)
        
        # Filtrar dados se necessário
        if valor:
            df_filtrado = df[df[coluna] == valor]
        else:
            df_filtrado = df
            
        # Contar pets por bairro
        contagem = df_filtrado['bairro'].value_counts().reset_index()
        contagem.columns = ['bairro', 'quantidade']
        
        # Adicionar coordenadas
        coords = coordenadas_bairros()
        contagem['lon'] = contagem['bairro'].map(lambda x: coords.get(x, [0, 0])[0])
        contagem['lat'] = contagem['bairro'].map(lambda x: coords.get(x, [0, 0])[1])
        
        # Remover bairros sem coordenadas
        contagem = contagem[(contagem['lon'] != 0) & (contagem['lat'] != 0)]
        
        # Criar mapa
        fig = px.density_mapbox(
            contagem,
            lat='lat',
            lon='lon',
            z='quantidade',
            radius=20,
            center={"lat": -27.5945, "lon": -48.5489},
            zoom=10,
            mapbox_style="carto-positron",
            title=f"Densidade de Pets por Bairro{f' - {valor}' if valor else ''}",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        return fig
    
    elif tipo_viz == "clustering":
        # Visualização de clusters
        resultado = kwargs.get('resultado', None)
        if not resultado or 'df_clusters' not in resultado:
            return None
            
        df_clusters = resultado['df_clusters']
        vars_usadas = resultado['vars_usadas']
        
        if len(vars_usadas) < 2:
            return None
            
        # Criar gráfico de dispersão com clusters
        fig = px.scatter(
            df_clusters, 
            x=vars_usadas[0], 
            y=vars_usadas[1],
            color='cluster',
            title=f"Clusterização por {vars_usadas[0]} e {vars_usadas[1]}",
            color_continuous_scale=px.colors.qualitative.Bold
        )
        
        # Adicionar centróides
        centroids = resultado['centros']
        fig.add_scatter(
            x=centroids[:, 0], 
            y=centroids[:, 1],
            mode='markers',
            marker=dict(color='black', size=12, symbol='x'),
            name='Centróides'
        )
        
        return fig
    
    elif tipo_viz == "anomalias":
        # Visualização de anomalias
        resultado = kwargs.get('resultado', None)
        if not resultado or 'df_anomalias' not in resultado:
            return None
            
        df_outliers = resultado['df_anomalias']
        
        # Selecionar duas colunas numéricas (não incluindo 'outlier')
        cols_num = [col for col in df_outliers.columns if pd.api.types.is_numeric_dtype(df_outliers[col]) and col != 'outlier']
        
        if len(cols_num) < 2:
            return None
            
        x_col = cols_num[0]
        y_col = cols_num[1]
        
        # Criar gráfico de dispersão com outliers destacados
        fig = px.scatter(
            df_outliers, 
            x=x_col, 
            y=y_col,
            color='outlier',
            title=f"Detecção de Anomalias - {x_col} vs {y_col}",
            color_discrete_map={True: 'red', False: 'blue'},
            labels={'outlier': 'Anomalia'},
            hover_data=cols_num
        )
        
        return fig
    
    elif tipo_viz == "regressao":
        # Visualização de regressão linear
        resultado = kwargs.get('resultado', None)
        if not resultado or 'x_test' not in resultado:
            return None
            
        # Dados do teste
        x_var = resultado['x_var']
        y_var = resultado['y_var']
        x_test = resultado['x_test']
        y_test = resultado['y_test']
        y_pred = resultado['y_pred']
        equacao = resultado['equacao']
        r2 = resultado['r2']
        
        # Criar gráfico
        fig = px.scatter(
            x=x_test, 
            y=y_test,
            title=f"Regressão Linear: {x_var} vs {y_var}<br><sup>{equacao} (R² = {r2:.4f})</sup>",
            labels={'x': x_var, 'y': y_var}
        )
        
        # Adicionar linha de regressão
        x_range = np.linspace(min(x_test), max(x_test), 100)
        y_range = resultado['coeficiente'] * x_range + resultado['intercepto']
        
        fig.add_traces(
            go.Scatter(
                x=x_range, 
                y=y_range,
                mode='lines',
                name='Linha de Regressão',
                line=dict(color='red', width=2)
            )
        )
        
        return fig
    
    elif tipo_viz == "tendencia_temporal":
        # Visualização de tendência temporal
        resultado = kwargs.get('resultado', None)
        if not resultado or 'tendencia' not in resultado:
            return None
            
        tendencia = resultado['tendencia']
        var_analise = resultado['var_analise']
        
        if 'mean' in tendencia.columns:
            # Variável numérica
            fig = px.line(
                tendencia, 
                x='mes_ano', 
                y='mean',
                error_y='std',
                labels={'mes_ano': 'Mês/Ano', 'mean': f'Média de {var_analise}'},
                title=f"Tendência de {var_analise} ao Longo do Tempo",
                markers=True
            )
            
            # Adicionar contagem como linha secundária
            fig.add_trace(
                go.Scatter(
                    x=tendencia['mes_ano'],
                    y=tendencia['count'],
                    mode='lines+markers',
                    name='Quantidade',
                    yaxis='y2'
                )
            )
            
            # Configurar eixo y secundário
            fig.update_layout(
                yaxis2=dict(
                    title='Quantidade',
                    overlaying='y',
                    side='right'
                )
            )
            
        else:
            # Variável categórica
            colunas_pct = [col for col in tendencia.columns if col.startswith('pct_')]
            if colunas_pct:
                # Usar colunas de porcentagem
                fig = px.line(
                    tendencia, 
                    x='mes_ano', 
                    y=colunas_pct,
                    labels={'mes_ano': 'Mês/Ano', 'value': 'Porcentagem (%)'},
                    title=f"Tendência de {var_analise} ao Longo do Tempo (%))",
                    markers=True
                )
            else:
                # Usar contagens absolutas
                colunas_cat = [col for col in tendencia.columns if col != 'mes_ano' and col != 'total']
                fig = px.line(
                    tendencia, 
                    x='mes_ano', 
                    y=colunas_cat,
                    labels={'mes_ano': 'Mês/Ano', 'value': 'Quantidade'},
                    title=f"Tendência de {var_analise} ao Longo do Tempo",
                    markers=True
                )
        
        return fig
    
    elif tipo_viz == "word_cloud":
        # Nuvem de palavras
        resultado = kwargs.get('resultado', None)
        if not resultado or 'texto_completo' not in resultado:
            return None
            
        texto = resultado['texto_completo']
        
        # Criar nuvem de palavras
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate(texto)
        
        # Criar figura matplotlib
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        
        # Converter para formato base64 para exibir no Streamlit
        buf = StringIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_str
    
    elif tipo_viz == "radar_chart":
        # Gráfico de radar para comparação de características
        grupo_por = kwargs.get('grupo_por', 'tipo_pet')
        metricas = kwargs.get('metricas', ['idade', 'peso'])
        
        if not all(col in df.columns for col in metricas):
            return None
            
        # Calcular médias por grupo
        df_radar = df.groupby(grupo_por)[metricas].mean().reset_index()
        
        # Normalizar os dados para escala de 0 a 1
        scaler = MinMaxScaler()
        df_radar[metricas] = scaler.fit_transform(df_radar[metricas])
        
        # Criar gráfico de radar
        fig = go.Figure()
        
        for i, grupo in enumerate(df_radar[grupo_por]):
            fig.add_trace(go.Scatterpolar(
                r=df_radar.loc[i, metricas].values.tolist() + [df_radar.loc[i, metricas].values[0]],
                theta=metricas + [metricas[0]],
                fill='toself',
                name=grupo
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title=f"Comparação de {grupo_por} por {', '.join(metricas)}"
        )
        
        return fig
    
    elif tipo_viz == "sunburst":
        # Gráfico sunburst para hierarquia
        nivel1 = kwargs.get('nivel1', 'regiao')
        nivel2 = kwargs.get('nivel2', 'bairro')
        nivel3 = kwargs.get('nivel3', 'tipo_pet')
        
        if not all(col in df.columns for col in [nivel1, nivel2, nivel3]):
            return None
            
        # Contar ocorrências
        df_sunburst = df.groupby([nivel1, nivel2, nivel3]).size().reset_index(name='contagem')
        
        # Criar gráfico sunburst
        fig = px.sunburst(
            df_sunburst, 
            path=[nivel1, nivel2, nivel3], 
            values='contagem',
            title=f"Distribuição Hierárquica por {nivel1}, {nivel2} e {nivel3}"
        )
        
        return fig
    
    return None

# Funções para análise preditiva
def realizar_previsao(df, var_target, vars_preditoras, test_size=0.2):
    """Realiza uma previsão usando regressão linear multivariada"""
    # Verificar se as variáveis existem e são numéricas
    if var_target not in df.columns or not pd.api.types.is_numeric_dtype(df[var_target]):
        return {"erro": f"Variável alvo '{var_target}' não encontrada ou não é numérica"}
        
    vars_validas = [var for var in vars_preditoras if var in df.columns and pd.api.types.is_numeric_dtype(df[var])]
    
    if len(vars_validas) == 0:
        return {"erro": "Nenhuma variável preditora válida"}
    
    # Preparar dados
    df_model = df[[var_target] + vars_validas].dropna()
    X = df_model[vars_validas]
    y = df_model[var_target]
    
    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Treinar modelo
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Fazer previsões
    y_pred = model.predict(X_test)
    
    # Métricas
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Importância das variáveis
    coefs = pd.DataFrame({
        'Variável': vars_validas,
        'Coeficiente': model.coef_
    }).sort_values('Coeficiente', ascending=False)
    
    return {
        'modelo': model,
        'mse': mse,
        'r2': r2,
        'coeficientes': coefs,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'var_target': var_target,
        'vars_preditoras': vars_validas
    }

def realizar_previsao_temporal(df, var_alvo, freq='M', periodos=12):
    """Realiza uma previsão temporal usando SARIMA"""
    if var_alvo not in df.columns or not pd.api.types.is_numeric_dtype(df[var_alvo]):
        return {"erro": f"Variável alvo '{var_alvo}' não encontrada ou não é numérica"}
        
    # Converter 'data_registro' para datetime se necessário
    if 'data_registro' not in df.columns:
        return {"erro": "Coluna 'data_registro' não encontrada para análise temporal"}
        
    # Converter para datetime se necessário
    if not pd.api.types.is_datetime64_dtype(df['data_registro']):
        df['data_registro'] = pd.to_datetime(df['data_registro'])
    
    # Agrupar por período
    df_time = df.set_index('data_registro')
    serie_temporal = df_time[var_alvo].resample(freq).mean().fillna(method='ffill')
    
    # Dividir em treino e teste
    train_size = int(len(serie_temporal) * 0.8)
    train, test = serie_temporal[:train_size], serie_temporal[train_size:]
    
    # Ajustar modelo SARIMA
    try:
        model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        model_fit = model.fit(disp=False)
        
        # Prever para o período de teste
        pred = model_fit.forecast(len(test))
        
        # Prever para o futuro
        future_pred = model_fit.forecast(steps=periodos)
        
        # Criar datas para previsão futura
        last_date = serie_temporal.index[-1]
        future_dates = pd.date_range(start=last_date, periods=periodos+1, freq=freq)[1:]
        
        # Decomposição da série
        decomposicao = seasonal_decompose(serie_temporal, model='additive')
        
        return {
            'serie_original': serie_temporal,
            'treino': train,
            'teste': test,
            'predicao_teste': pred,
            'predicao_futura': future_pred,
            'datas_futuras': future_dates,
            'var_alvo': var_alvo,
            'tendencia': decomposicao.trend,
            'sazonalidade': decomposicao.seasonal,
            'residuo': decomposicao.resid
        }
    except Exception as e:
        return {"erro": f"Erro ao criar modelo de previsão temporal: {str(e)}"}

# Interface principal
def main():
    # Carregar dados
    df = carregar_dados()
    
    # Verifica se o dataframe tem os campos necessários para análise
    campos_necessarios = ['bairro', 'tipo_pet', 'raca', 'idade', 'peso', 'adotado']
    for campo in campos_necessarios:
        if campo not in df.columns:
            st.error(f"O dataframe não possui o campo '{campo}' necessário para análise.")
            st.stop()
    
    # Barra lateral
    with st.sidebar:
        st.image("./assets/logo.jpg", width=300)
        st.title("PetCare Analytics")
        
        # Navegação principal
        menu = st.radio(
            "Navegação",
            ["Dashboard", "Mapa Interativo", "Análise Avançada", "Previsões", "Relatório IA", "Gerenciar Dados"]
        )
        
        st.markdown("---")
        
        # Filtros globais aplicáveis a todas as páginas
        st.subheader("Filtros Globais")
        
        # Filtro por região
        if 'regiao' in df.columns:
            regioes = ["Todas"] + sorted(df['regiao'].unique().tolist())
            regiao_selecionada = st.selectbox("Região", regioes)
        else:
            regiao_selecionada = "Todas"
        
        # Filtro por tipo de pet
        tipos_pet = ["Todos"] + sorted(df['tipo_pet'].unique().tolist())
        tipo_pet_selecionado = st.selectbox("Tipo de Pet", tipos_pet)
        
        # Filtro por bairro (top 15 mais populares)
        top_bairros = df['bairro'].value_counts().nlargest(15).index.tolist()
        bairros_opcoes = ["Todos"] + sorted(top_bairros)
        bairro_selecionado = st.selectbox("Bairro", bairros_opcoes)
        
        # Filtro por status de adoção
        adocao_opcoes = ["Todos", "Adotados", "Não Adotados"]
        adocao_selecionada = st.selectbox("Status de Adoção", adocao_opcoes)
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if regiao_selecionada != "Todas" and 'regiao' in df.columns:
            df_filtrado = df_filtrado[df_filtrado['regiao'] == regiao_selecionada]
            
        if tipo_pet_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['tipo_pet'] == tipo_pet_selecionado]
            
        if bairro_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['bairro'] == bairro_selecionado]
            
        if adocao_selecionada == "Adotados":
            df_filtrado = df_filtrado[df_filtrado['adotado'] == True]
        elif adocao_selecionada == "Não Adotados":
            df_filtrado = df_filtrado[df_filtrado['adotado'] == False]
            
        # Mostrar contagem de registros após filtros
        st.info(f"Mostrando {len(df_filtrado)} de {len(df)} registros")
        
        st.markdown("---")
        st.caption("Desenvolvido por PetCare Analytics")
        
    # Conteúdo principal baseado na navegação
    if menu == "Dashboard":
        display_dashboard(df, df_filtrado)
    elif menu == "Mapa Interativo":
        display_map(df, df_filtrado)
    elif menu == "Análise Avançada":
        display_advanced_analysis(df, df_filtrado)
    elif menu == "Previsões":
        display_predictions(df, df_filtrado)
    elif menu == "Relatório IA":
        display_ai_insights(df, df_filtrado)
    elif menu == "Gerenciar Dados":
        display_data_management(df, df_filtrado)

def display_dashboard(df, df_filtrado):
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
    media_idade = df_filtrado['idade'].mean() if 'idade' in df_filtrado.columns else 0
    media_peso = df_filtrado['peso'].mean() if 'peso' in df_filtrado.columns else 0
    
    # Verificar se 'adotado' está presente e é booleano/numérico
    taxa_adocao = 0
    if 'adotado' in df_filtrado.columns:
        if df_filtrado['adotado'].dtype == bool or pd.api.types.is_numeric_dtype(df_filtrado['adotado']):
            taxa_adocao = df_filtrado['adotado'].mean() * 100
            
    # Cards com métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Pets", f"{total_pets}")
    
    with col2:
        # Garantir que temos pelo menos um valor válido para calcular média de idade
        if 'idade' in df_filtrado.columns and not df_filtrado['idade'].isna().all():
            st.metric("Média de Idade", f"{media_idade:.1f} anos")
        else:
            st.metric("Média de Idade", "N/A")
    
    with col3:
        # Garantir que temos pelo menos um valor válido para calcular média de peso
        if 'peso' in df_filtrado.columns and not df_filtrado['peso'].isna().all():
            st.metric("Média de Peso", f"{media_peso:.1f} kg")
        else:
            st.metric("Média de Peso", "N/A")
    
    with col4:
        if 'adotado' in df_filtrado.columns:
            st.metric("Taxa de Adoção", f"{taxa_adocao:.1f}%")
        else:
            st.metric("Taxa de Adoção", "N/A")
    
    # Gráficos principais
    st.subheader("Visão Geral")
    
    # Distribuição por tipo de pet e status de adoção
    col1, col2 = st.columns(2)
    
    with col1:
        if 'tipo_pet' in df_filtrado.columns:
            st.markdown("### Distribuição por Tipo")
            
            # Contar ocorrências de cada tipo
            tipo_counts = df_filtrado['tipo_pet'].value_counts().reset_index()
            tipo_counts.columns = ['tipo_pet', 'count']
            
            # Criar gráfico de pizza
            fig = px.pie(
                tipo_counts, 
                values='count', 
                names='tipo_pet',
                title='Distribuição por Tipo de Pet',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'tipo_pet' não disponível nos dados.")
    
    with col2:
        if 'adotado' in df_filtrado.columns:
            st.markdown("### Status de Adoção")
            
            # Contar pets adotados vs não adotados
            adocao_counts = df_filtrado['adotado'].map({True: 'Adotado', False: 'Não Adotado'}).value_counts().reset_index()
            adocao_counts.columns = ['status', 'count']
            
            # Criar gráfico de barras
            fig = px.bar(
                adocao_counts,
                x='status',
                y='count',
                color='status',
                title='Status de Adoção',
                color_discrete_map={'Adotado': '#2ECC71', 'Não Adotado': '#E74C3C'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'adotado' não disponível nos dados.")
    
    # Gráfico de dispersão para relacionar idade e peso
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Distribuição de Idade vs Peso")
        st.markdown("Analise a relação entre idade e peso dos pets, com a possibilidade de coloração por tipo.")
    
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
                    title="Relação entre Idade e Peso",
                    trendline='ols',
                    trendline_scope='overall'
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
        
        # Gráfico de barras horizontal
        fig = px.bar(
            top_bairros,
            y='bairro',
            x='count',
            orientation='h',
            title='Top 10 Bairros por Quantidade de Pets',
            color='count',
            color_continuous_scale='Viridis',
            labels={'count': 'Quantidade', 'bairro': 'Bairro'}
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
                
                fig = px.pie(
                    tipo_bairro,
                    values='count',
                    names='tipo_pet',
                    title=f'Tipos de Pet em {bairro_selecionado}',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'tipo_pet' não disponível nos dados do bairro.")
        
        with col2:
            if 'adotado' in df_bairro.columns:
                # Taxa de adoção no bairro
                try:
                    taxa_adocao_bairro = df_bairro['adotado'].mean() * 100
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=taxa_adocao_bairro,
                        title={'text': f'Taxa de Adoção em {bairro_selecionado}'},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 30], 'color': "red"},
                                {'range': [30, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "green"}
                            ]
                        }
                    ))
                    
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
            st.metric("Total de Pets", f"{len(df_bairro)}")
        
        with col2:
            if 'idade' in df_bairro.columns and not df_bairro['idade'].isna().all():
                media_idade_bairro = df_bairro['idade'].mean()
                st.metric("Média de Idade", f"{media_idade_bairro:.1f} anos")
            else:
                st.metric("Média de Idade", "N/A")
        
        with col3:
            if 'peso' in df_bairro.columns and not df_bairro['peso'].isna().all():
                media_peso_bairro = df_bairro['peso'].mean()
                st.metric("Média de Peso", f"{media_peso_bairro:.1f} kg")
            else:
                st.metric("Média de Peso", "N/A")
        
        # Raças mais comuns no bairro
        if 'raca' in df_bairro.columns:
            st.markdown("#### Raças mais comuns no bairro")
            
            racas_bairro = df_bairro['raca'].value_counts().nlargest(5).reset_index()
            racas_bairro.columns = ['raca', 'count']
            
            fig = px.bar(
                racas_bairro,
                x='raca',
                y='count',
                title=f'Top 5 Raças em {bairro_selecionado}',
                color='count',
                labels={'count': 'Quantidade', 'raca': 'Raça'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coluna 'bairro' não disponível nos dados.")
    
    # Tendências e Padrões
    st.subheader("Tendências e Padrões")
    
    if 'tipo_pet' in df_filtrado.columns and 'peso' in df_filtrado.columns:
        # Distribuição de peso por tipo de pet (boxplot)
        # Remover valores NaN nas colunas relevantes
        df_box = df_filtrado.dropna(subset=['tipo_pet', 'peso']).copy()
        
        if len(df_box) > 0:
            fig = px.box(
                df_box,
                x='tipo_pet',
                y='peso',
                color='tipo_pet',
                title='Distribuição de Peso por Tipo de Pet',
                labels={'peso': 'Peso (kg)', 'tipo_pet': 'Tipo de Pet'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes para gerar o boxplot (valores de tipo_pet e/ou peso ausentes).")
    else:
        st.info("Colunas 'tipo_pet' e/ou 'peso' não disponíveis nos dados.")
    
    # Análise Temporal caso haja dados temporais
    if 'data_registro' in df_filtrado.columns:
        st.subheader("Análise Temporal")
        
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
            title='Evolução de Registros ao Longo do Tempo',
            labels={'count': 'Quantidade de Registros', 'mes_str': 'Mês'},
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição por tipo ao longo do tempo (se houver tipo_pet)
        if 'tipo_pet' in df_filtrado.columns:
            tipos_por_mes = df_filtrado.groupby(['mes', 'tipo_pet']).size().reset_index(name='count')
            tipos_por_mes['mes_str'] = tipos_por_mes['mes'].astype(str)
            
            fig = px.line(
                tipos_por_mes,
                x='mes_str',
                y='count',
                color='tipo_pet',
                title='Evolução de Tipos de Pet ao Longo do Tempo',
                labels={'count': 'Quantidade', 'mes_str': 'Mês', 'tipo_pet': 'Tipo de Pet'},
                markers=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Comparações e Correlações
    st.subheader("Comparações e Correlações")
    
    # Verificar se temos dados suficientes para análise de correlação
    df_num = df_filtrado.select_dtypes(include=['number'])
    if len(df_num.columns) >= 2:
        # Calcular matriz de correlação
        corr = df_num.corr()
        
        # Criar mapa de calor
        fig = px.imshow(
            corr,
            text_auto='.2f',
            aspect="auto",
            title="Matriz de Correlação",
            color_continuous_scale='RdBu_r'
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
            st.markdown("#### Correlações mais significativas")
            
            correlacoes = []
            for var1, var2, valor in corr_pairs[:5]:  # Top 5 correlações
                correlacoes.append({
                    "Variável 1": var1,
                    "Variável 2": var2,
                    "Correlação": f"{valor:.2f}"
                })
            
            st.table(pd.DataFrame(correlacoes))
            
            # Mostrar scatter plot para a correlação mais forte
            if len(corr_pairs) > 0:
                var1, var2, _ = corr_pairs[0]
                
                # Remover valores NaN das colunas relevantes
                df_corr = df_filtrado.dropna(subset=[var1, var2]).copy()
                
                if len(df_corr) > 0:
                    fig = px.scatter(
                        df_corr,
                        x=var1,
                        y=var2,
                        color='tipo_pet' if 'tipo_pet' in df_corr.columns else None,
                        trendline='ols',
                        title=f'Correlação entre {var1} e {var2}',
                        labels={var1: var1, var2: var2}
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
                humor_counts = df_filtrado['humor_diario'].value_counts().reset_index()
                humor_counts.columns = ['humor', 'count']
                
                fig = px.bar(
                    humor_counts,
                    x='humor',
                    y='count',
                    title='Distribuição de Humor Diário',
                    color='humor',
                    labels={'count': 'Quantidade', 'humor': 'Humor'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'humor_diario' não disponível nos dados.")
        
        with col2:
            if 'comportamento' in df_filtrado.columns:
                comportamento_counts = df_filtrado['comportamento'].value_counts().reset_index()
                comportamento_counts.columns = ['comportamento', 'count']
                
                fig = px.pie(
                    comportamento_counts,
                    values='count',
                    names='comportamento',
                    title='Distribuição de Comportamento',
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Coluna 'comportamento' não disponível nos dados.")
    
    # Análise de preferência alimentar (se houver dados)
    if 'tipo_comida' in df_filtrado.columns:
        st.subheader("Preferências Alimentares")
        
        # Contar preferências alimentares
        comida_counts = df_filtrado['tipo_comida'].value_counts().reset_index()
        comida_counts.columns = ['tipo_comida', 'count']
        
        fig = px.bar(
            comida_counts,
            x='tipo_comida',
            y='count',
            title='Distribuição de Preferências Alimentares',
            color='tipo_comida',
            labels={'count': 'Quantidade', 'tipo_comida': 'Tipo de Comida'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Relação entre tipo de pet e preferência alimentar
        if 'tipo_pet' in df_filtrado.columns:
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
                title='Preferência Alimentar por Tipo de Pet (%)',
                labels={'percentual': 'Percentual', 'tipo_pet': 'Tipo de Pet', 'tipo_comida': 'Tipo de Comida'},
                barmode='stack'
            )
            
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
                    title=f'Evolução de {caract_temporal} ao Longo do Tempo',
                    labels={caract_temporal: f'{caract_temporal.capitalize()}', 'mes_str': 'Mês'},
                    markers=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Se tivermos tipo_pet, mostrar evolução por tipo
                if 'tipo_pet' in df_filtrado.columns:
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
                            title=f'Evolução de {caract_temporal} por Tipo de Pet',
                            labels={caract_temporal: f'{caract_temporal.capitalize()}', 'mes_str': 'Mês', 'tipo_pet': 'Tipo de Pet'},
                            markers=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Dados insuficientes para análise temporal de {caract_temporal}.")
    
    # Botão para exportar relatório
    if st.button("📊 Exportar Relatório Completo"):
        # Aqui você adicionaria código para gerar um relatório completo
        st.success("Funcionalidade de exportação de relatório será implementada em uma versão futura.")

# Função para exibir o mapa interativo
def display_map(df, df_filtrado):
    st.title("Mapa Interativo de Pets")
    st.markdown("Visualização geográfica da distribuição de pets por bairro")
    
    # Opções de visualização do mapa
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Opções de Visualização")
        
        # Tipo de visualização
        tipo_mapa = st.radio(
            "Tipo de Mapa",
            ["Distribuição", "Densidade", "Comparativo", "3D"]
        )
        
        # Variável para cor do mapa
        var_cor = st.selectbox(
            "Colorir por",
            ["Quantidade", "Tipo de Pet", "Taxa de Adoção", "Idade Média", "Peso Médio"]
        )
        
        # Estilo do mapa base
        estilo_mapa = st.selectbox(
            "Estilo do Mapa",
            ["Claro", "Escuro", "Satélite", "Ruas"]
        )
        
        mapbox_style = {
            "Claro": "light",
            "Escuro": "dark",
            "Satélite": "satellite",
            "Ruas": "streets"
        }[estilo_mapa]
        
        # Botão para atualizar o mapa
        st.button("Atualizar Mapa", type="primary")
    
    with col2:
        # Contar pets por bairro
        bairro_counts = df_filtrado['bairro'].value_counts().reset_index()
        bairro_counts.columns = ['bairro', 'quantidade']
        
        # Adicionar dados adicionais por bairro
        for bairro in bairro_counts['bairro']:
            # Taxa de adoção
            bairro_counts.loc[bairro_counts['bairro'] == bairro, 'taxa_adocao'] =                 df_filtrado[df_filtrado['bairro'] == bairro]['adotado'].mean() * 100
            
            # Idade média
            bairro_counts.loc[bairro_counts['bairro'] == bairro, 'idade_media'] =                 df_filtrado[df_filtrado['bairro'] == bairro]['idade'].mean()
            
            # Peso médio
            bairro_counts.loc[bairro_counts['bairro'] == bairro, 'peso_medio'] =                 df_filtrado[df_filtrado['bairro'] == bairro]['peso'].mean()
            
            # Tipo de pet mais comum
            if len(df_filtrado[df_filtrado['bairro'] == bairro]) > 0:
                tipo_comum = df_filtrado[df_filtrado['bairro'] == bairro]['tipo_pet'].value_counts().index[0]
                bairro_counts.loc[bairro_counts['bairro'] == bairro, 'tipo_comum'] = tipo_comum
            else:
                bairro_counts.loc[bairro_counts['bairro'] == bairro, 'tipo_comum'] = "N/A"
        
        # Adicionar coordenadas
        coords = coordenadas_bairros()
        bairro_counts['lon'] = bairro_counts['bairro'].map(lambda x: coords.get(x, [0, 0])[0])
        bairro_counts['lat'] = bairro_counts['bairro'].map(lambda x: coords.get(x, [0, 0])[1])
        
        # Remover bairros sem coordenadas
        bairro_counts = bairro_counts[(bairro_counts['lon'] != 0) & (bairro_counts['lat'] != 0)]
        
        # Variável para colorir
        color_column = {
            "Quantidade": "quantidade",
            "Taxa de Adoção": "taxa_adocao",
            "Idade Média": "idade_media",
            "Peso Médio": "peso_medio",
            "Tipo de Pet": "tipo_comum"
        }[var_cor]
        
        # Criar mapa
        if tipo_mapa == "Distribuição":
            # Mapa de pontos com tamanho proporcional à quantidade
            fig = px.scatter_mapbox(
                bairro_counts,
                lat="lat",
                lon="lon",
                size="quantidade",
                color=color_column if color_column != "tipo_comum" else None,
                color_discrete_map={"Cachorro": "#1f77b4", "Gato": "#ff7f0e", "Ave": "#2ca02c", 
                                     "Peixe": "#d62728", "Roedor": "#9467bd", "Réptil": "#8c564b"} 
                                     if color_column == "tipo_comum" else None,
                hover_name="bairro",
                hover_data=["quantidade", "taxa_adocao", "idade_media", "peso_medio", "tipo_comum"],
                color_continuous_scale=px.colors.sequential.Viridis,
                size_max=40,
                zoom=11,
                height=600,
                title=f"Distribuição de Pets por Bairro"
            )
            
            fig.update_layout(mapbox_style=f"mapbox://{mapbox_style}")
            
        elif tipo_mapa == "Densidade":
            # Mapa de densidade heatmap
            fig = px.density_mapbox(
                bairro_counts,
                lat="lat",
                lon="lon",
                z="quantidade",
                radius=20,
                center={"lat": -27.5945, "lon": -48.5489},
                zoom=11,
                hover_name="bairro",
                hover_data=["quantidade", "taxa_adocao", "idade_media", "peso_medio", "tipo_comum"],
                height=600,
                color_continuous_scale=px.colors.sequential.Viridis,
                title=f"Densidade de Pets por Bairro"
            )
            
            fig.update_layout(mapbox_style=f"mapbox://{mapbox_style}")
            
        elif tipo_mapa == "Comparativo":
            # Criar um mapa comparativo lado a lado
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "mapbox"}, {"type": "mapbox"}]],
                subplot_titles=("Quantidade de Pets", "Taxa de Adoção")
            )
            
            # Mapa 1: Quantidade
            fig.add_trace(
                go.Scattermapbox(
                    lat=bairro_counts["lat"],
                    lon=bairro_counts["lon"],
                    mode="markers",
                    marker=dict(
                        size=bairro_counts["quantidade"]/3,
                        color=bairro_counts["quantidade"],
                        colorscale="Viridis",
                        showscale=True,
                        colorbar=dict(title="Quantidade", x=0.45)
                    ),
                    text=bairro_counts["bairro"],
                    hoverinfo="text+lat+lon",
                    hovertemplate="<b>%{text}</b><br>Quantidade: %{marker.color:.0f}<extra></extra>"
                ),
                row=1, col=1
            )
            
            # Mapa 2: Taxa de Adoção
            fig.add_trace(
                go.Scattermapbox(
                    lat=bairro_counts["lat"],
                    lon=bairro_counts["lon"],
                    mode="markers",
                    marker=dict(
                        size=bairro_counts["quantidade"]/3,
                        color=bairro_counts["taxa_adocao"],
                        colorscale="RdBu",
                        showscale=True,
                        colorbar=dict(title="% Adoção", x=1.0)
                    ),
                    text=bairro_counts["bairro"],
                    hoverinfo="text+lat+lon",
                    hovertemplate="<b>%{text}</b><br>Taxa de Adoção: %{marker.color:.1f}%<extra></extra>"
                ),
                row=1, col=2
            )
            
            # Layout
            fig.update_layout(
                height=600,
                mapbox1=dict(
                    center=dict(lat=-27.5945, lon=-48.5489),
                    style=mapbox_style,
                    zoom=10
                ),
                mapbox2=dict(
                    center=dict(lat=-27.5945, lon=-48.5489),
                    style=mapbox_style,
                    zoom=10
                )
            )
            
        elif tipo_mapa == "3D":
            # Mapa 3D com elevação
            fig = go.Figure(
                go.Scattermapbox(
                    lat=bairro_counts["lat"],
                    lon=bairro_counts["lon"],
                    mode="markers+text",
                    marker=dict(
                        size=bairro_counts["quantidade"]/2,
                        color=bairro_counts[color_column] if color_column != "tipo_comum" else None,
                        colorscale="Viridis",
                        showscale=True
                    ),
                    text=bairro_counts["bairro"],
                    textposition="top center",
                    hoverinfo="text+lat+lon",
                    hovertemplate="<b>%{text}</b><br>Quantidade: %{marker.size:.0f}<extra></extra>"
                )
            )
            
            # Layout com elevação
            fig.update_layout(
                height=700,
                mapbox=dict(
                    style=mapbox_style,
                    center=dict(lat=-27.5945, lon=-48.5489),
                    zoom=11,
                    pitch=45,  # Ângulo de inclinação
                    bearing=0   # Ângulo de rotação
                )
            )
        
        # Exibir mapa
        st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas e tabelas abaixo do mapa
    st.subheader("Estatísticas por Bairro")
    
    tab1, tab2 = st.tabs(["Resumo", "Tabela Completa"])
    
    with tab1:
        # Mostrar os top 5 bairros em diferentes categorias
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Top 5 Bairros por Quantidade")
            top_qtd = bairro_counts.sort_values('quantidade', ascending=False).head(5)
            top_qtd = top_qtd[['bairro', 'quantidade']]
            top_qtd.columns = ['Bairro', 'Quantidade']
            st.table(top_qtd)
        
        with col2:
            st.markdown("### Top 5 Bairros por Taxa de Adoção")
            # Filtrar bairros com pelo menos 5 pets
            min_pets = 5
            top_adocao = bairro_counts[bairro_counts['quantidade'] >= min_pets]
            top_adocao = top_adocao.sort_values('taxa_adocao', ascending=False).head(5)
            top_adocao = top_adocao[['bairro', 'taxa_adocao', 'quantidade']]
            top_adocao.columns = ['Bairro', 'Taxa de Adoção (%)', 'Quantidade']
            st.table(top_adocao)
        
        with col3:
            st.markdown("### Distribuição por Região")
            if 'regiao' in df_filtrado.columns:
                regiao_counts = df_filtrado['regiao'].value_counts().reset_index()
                regiao_counts.columns = ['Região', 'Quantidade']
                
                fig = px.pie(
                    regiao_counts,
                    names='Região',
                    values='Quantidade',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Informação de região não disponível nos dados.")
    
    with tab2:
        # Tabela completa com todas as estatísticas por bairro
        tabela_completa = bairro_counts.sort_values('quantidade', ascending=False)
        
        # Renomear colunas para melhor visualização
        colunas_exibicao = {
            'bairro': 'Bairro',
            'quantidade': 'Quantidade',
            'taxa_adocao': 'Taxa de Adoção (%)',
            'idade_media': 'Idade Média',
            'peso_medio': 'Peso Médio',
            'tipo_comum': 'Tipo de Pet mais Comum'
        }
        
        tabela_formatada = tabela_completa[colunas_exibicao.keys()].rename(columns=colunas_exibicao)
        
        # Formatar casas decimais
        tabela_formatada['Taxa de Adoção (%)'] = tabela_formatada['Taxa de Adoção (%)'].round(1)
        tabela_formatada['Idade Média'] = tabela_formatada['Idade Média'].round(1)
        tabela_formatada['Peso Médio'] = tabela_formatada['Peso Médio'].round(1)
        
        st.dataframe(tabela_formatada, use_container_width=True)
        
        # Opção para download
        tabela_formatada_csv = tabela_formatada.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Tabela (CSV)",
            data=tabela_formatada_csv,
            file_name="estatisticas_bairros.csv",
            mime="text/csv"
        )

# Função para exibir análise avançada
def display_advanced_analysis(df, df_filtrado):
    st.title("Análise Avançada de Dados")
    st.markdown("Ferramentas estatísticas e visualizações para explorar relações entre variáveis")
    
    # Escolher tipo de análise
    tipo_analise = st.selectbox(
        "Selecione o tipo de análise:",
        ["Correlação", "Clusterização", "Detecção de Anomalias", 
         "Regressão", "Análise Temporal", "Análise de Texto"]
    )
    
    # Correlação
    if tipo_analise == "Correlação":
        st.markdown("### Análise de Correlação")
        st.markdown("Identifique relações lineares entre variáveis numéricas")
        
        # Selecionar variáveis para correlação
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        
        if len(colunas_numericas) < 2:
            st.warning("Não há variáveis numéricas suficientes para análise de correlação.")
        else:
            vars_selecionadas = st.multiselect(
                "Selecione variáveis para análise:",
                options=colunas_numericas,
                default=colunas_numericas[:4] if len(colunas_numericas) > 4 else colunas_numericas
            )
            
            if len(vars_selecionadas) >= 2:
                # Realizar análise
                resultado = realizar_analise_estatistica(df_filtrado, "correlacao", vars_selecionadas)
                
                # Visualizar matriz de correlação
                if 'matriz' in resultado:
                    fig = criar_visualizacao(df_filtrado, "mapa_calor_correlacao", cols=vars_selecionadas)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Destacar correlações mais fortes
                    st.markdown("#### Correlações mais significativas")
                    
                    # Pegar o triângulo superior da matriz de correlação
                    corr = resultado['matriz']
                    corr_upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
                    
                    # Reorganizar para formato longo
                    corr_long = corr_upper.stack().reset_index()
                    corr_long.columns = ['Variável 1', 'Variável 2', 'Correlação']
                    
                    # Ordenar por valor absoluto de correlação
                    corr_long['Abs. Correlação'] = corr_long['Correlação'].abs()
                    corr_long = corr_long.sort_values('Abs. Correlação', ascending=False)
                    
                    # Mostrar as correlações mais fortes
                    st.dataframe(corr_long[['Variável 1', 'Variável 2', 'Correlação']], use_container_width=True)
                    
                    # Visualização de dispersão para par com maior correlação
                    if len(corr_long) > 0:
                        var1 = corr_long.iloc[0]['Variável 1']
                        var2 = corr_long.iloc[0]['Variável 2']
                        corr_valor = corr_long.iloc[0]['Correlação']
                        
                        st.markdown(f"#### Dispersão entre {var1} e {var2} (Corr: {corr_valor:.2f})")
                        
                        fig = px.scatter(
                            df_filtrado,
                            x=var1,
                            y=var2,
                            color='tipo_pet' if 'tipo_pet' in df_filtrado.columns else None,
                            title=f"Correlação: {corr_valor:.2f}",
                            trendline="ols"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione pelo menos duas variáveis para análise de correlação.")
    
    # Clusterização
    elif tipo_analise == "Clusterização":
        st.markdown("### Análise de Clusterização")
        st.markdown("Agrupe pets por características similares")
        
        # Selecionar variáveis para clusterização
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        
        if len(colunas_numericas) < 2:
            st.warning("Não há variáveis numéricas suficientes para clusterização.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                var1 = st.selectbox(
                    "Variável X:", 
                    options=colunas_numericas,
                    index=colunas_numericas.index('idade') if 'idade' in colunas_numericas else 0
                )
            
            with col2:
                var2 = st.selectbox(
                    "Variável Y:", 
                    options=colunas_numericas,
                    index=colunas_numericas.index('peso') if 'peso' in colunas_numericas else min(1, len(colunas_numericas)-1)
                )
            
            # Número de clusters
            num_clusters = st.slider("Número de clusters:", 2, 10, 3)
            
            # Realizar clusterização
            resultado = realizar_analise_estatistica(df_filtrado, "clusters", var1, var2, num_clusters)
            
            if 'erro' in resultado:
                st.error(resultado['erro'])
            else:
                # Visualizar resultado
                fig = criar_visualizacao(df_filtrado, "clustering", resultado=resultado)
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar estatísticas por cluster
                if 'estatisticas' in resultado:
                    st.markdown("#### Estatísticas por Cluster")
                    st.dataframe(resultado['estatisticas'], use_container_width=True)
                
                # Avaliação da qualidade dos clusters
                if 'silhouette_score' in resultado:
                    silhouette = resultado['silhouette_score']
                    st.markdown(f"#### Qualidade dos Clusters")
                    st.markdown(f"Silhouette Score: **{silhouette:.3f}**")
                    
                    if silhouette > 0.7:
                        st.success("Excelente separação entre clusters")
                    elif silhouette > 0.5:
                        st.info("Boa separação entre clusters")
                    elif silhouette > 0.3:
                        st.warning("Separação razoável entre clusters")
                    else:
                        st.error("Baixa separação entre clusters. Considere ajustar o número de clusters ou usar outras variáveis.")
    
    # Detecção de Anomalias
    elif tipo_analise == "Detecção de Anomalias":
        st.markdown("### Detecção de Anomalias")
        st.markdown("Identifique registros com comportamento incomum")
        
        # Parâmetros
        metodo = st.radio(
            "Método de detecção:",
            ["Isolation Forest", "Regra de 3-sigma"]
        )
        
        if metodo == "Isolation Forest":
            # Realizar detecção de anomalias
            resultado = realizar_analise_estatistica(df_filtrado, "anomalias")
            
            if 'erro' in resultado:
                st.error(resultado['erro'])
            else:
                # Exibir resultados
                st.markdown(f"#### Anomalias detectadas: {resultado['qtd_anomalias']} de {len(df_filtrado)} registros")
                
                # Visualizar resultado
                fig = criar_visualizacao(df_filtrado, "anomalias", resultado=resultado)
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas comparativas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Estatísticas das Anomalias")
                    st.dataframe(resultado['resumo_anomalias'])
                
                with col2:
                    st.markdown("##### Estatísticas dos Registros Normais")
                    st.dataframe(resultado['resumo_normais'])
                
                # Exibir registros anômalos
                with st.expander("Ver registros anômalos"):
                    if 'df_anomalias' in resultado:
                        anomalias_df = resultado['df_anomalias'][resultado['df_anomalias']['outlier']]
                        
                        # Adicionar informações do pet
                        pets_info = df_filtrado[df_filtrado.index.isin(anomalias_df.index)]
                        
                        st.dataframe(pets_info, use_container_width=True)
        
        else:  # Regra de 3-sigma
            # Selecionar variável para analisar
            var_analise = st.selectbox(
                "Variável para análise:",
                options=df_filtrado.select_dtypes(include=['number']).columns.tolist(),
                index=df_filtrado.select_dtypes(include=['number']).columns.tolist().index('peso') 
                if 'peso' in df_filtrado.select_dtypes(include=['number']).columns else 0
            )
            
            # Aplicar regra de 3-sigma
            media = df_filtrado[var_analise].mean()
            desvio = df_filtrado[var_analise].std()
            
            limite_sup = media + 3 * desvio
            limite_inf = media - 3 * desvio
            
            anomalias = df_filtrado[(df_filtrado[var_analise] > limite_sup) | (df_filtrado[var_analise] < limite_inf)]
            
            # Exibir resultados
            st.markdown(f"#### Anomalias detectadas: {len(anomalias)} de {len(df_filtrado)} registros")
            st.markdown(f"Limites: {limite_inf:.2f} a {limite_sup:.2f} (Média: {media:.2f}, Desvio: {desvio:.2f})")
            
            # Visualizar resultado
            fig = px.histogram(
                df_filtrado,
                x=var_analise,
                color_discrete_sequence=['blue'],
                title=f"Distribuição de {var_analise} com limites de 3-sigma"
            )
            
            fig.add_vline(x=limite_inf, line_dash="dash", line_color="red", annotation_text="Limite Inferior")
            fig.add_vline(x=limite_sup, line_dash="dash", line_color="red", annotation_text="Limite Superior")
            fig.add_vline(x=media, line_dash="dash", line_color="green", annotation_text="Média")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Exibir registros anômalos
            with st.expander("Ver registros anômalos"):
                st.dataframe(anomalias, use_container_width=True)
    
    # Regressão
    elif tipo_analise == "Regressão":
        st.markdown("### Análise de Regressão")
        st.markdown("Explore relações causais entre variáveis")
        
        # Selecionar variáveis para regressão
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        
        if len(colunas_numericas) < 2:
            st.warning("Não há variáveis numéricas suficientes para análise de regressão.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                var1 = st.selectbox(
                    "Variável Independente (X):", 
                    options=colunas_numericas,
                    index=colunas_numericas.index('idade') if 'idade' in colunas_numericas else 0
                )
            
            with col2:
                var2 = st.selectbox(
                    "Variável Dependente (Y):", 
                    options=colunas_numericas,
                    index=colunas_numericas.index('peso') if 'peso' in colunas_numericas else min(1, len(colunas_numericas)-1)
                )
            
            # Realizar regressão
            resultado = realizar_analise_estatistica(df_filtrado, "regressao", var1, var2)
            
            if 'erro' in resultado:
                st.error(resultado['erro'])
            else:
                # Mostrar equação e métricas
                st.markdown(f"#### Equação da Regressão Linear")
                st.markdown(f"**{resultado['equacao']}**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Coeficiente", f"{resultado['coeficiente']:.4f}")
                
                with col2:
                    st.metric("R-squared", f"{resultado['r2']:.4f}")
                
                with col3:
                    st.metric("Erro Quadrático Médio", f"{resultado['mse']:.4f}")
                
                # Visualizar resultado
                fig = criar_visualizacao(df_filtrado, "regressao", resultado=resultado)
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretação dos resultados
                st.markdown("#### Interpretação do Resultado")
                
                if resultado['r2'] < 0.3:
                    interpretacao = f"Existe uma correlação **fraca** entre {var1} e {var2}. O modelo explica apenas {resultado['r2']*100:.1f}% da variação em {var2}."
                elif resultado['r2'] < 0.7:
                    interpretacao = f"Existe uma correlação **moderada** entre {var1} e {var2}. O modelo explica {resultado['r2']*100:.1f}% da variação em {var2}."
                else:
                    interpretacao = f"Existe uma correlação **forte** entre {var1} e {var2}. O modelo explica {resultado['r2']*100:.1f}% da variação em {var2}."
                
                coef_interpretacao = f"Para cada aumento de 1 unidade em {var1}, {var2} {'aumenta' if resultado['coeficiente'] > 0 else 'diminui'} em {abs(resultado['coeficiente']):.4f} unidades."
                
                st.markdown(interpretacao)
                st.markdown(coef_interpretacao)
    
    # Análise Temporal
    elif tipo_analise == "Análise Temporal":
        st.markdown("### Análise Temporal")
        st.markdown("Explore tendências ao longo do tempo")
        
        # Verificar se há dados temporais
        if 'data_registro' not in df_filtrado.columns:
            st.warning("O conjunto de dados não possui a coluna 'data_registro' necessária para análise temporal.")
        else:
            # Selecionar variável para análise
            opcoes_analise = df_filtrado.columns.tolist()
            opcoes_analise.remove('data_registro')
            
            var_analise = st.selectbox(
                "Variável para análise:",
                options=opcoes_analise,
                index=opcoes_analise.index('tipo_pet') if 'tipo_pet' in opcoes_analise else 0
            )
            
            # Realizar análise
            resultado = realizar_analise_estatistica(df_filtrado, "tendencia_temporal", var_analise)
            
            if 'erro' in resultado:
                st.error(resultado['erro'])
            else:
                # Visualizar resultado
                fig = criar_visualizacao(df_filtrado, "tendencia_temporal", resultado=resultado)
                st.plotly_chart(fig, use_container_width=True)
                
                # Exibir tabela de dados
                if 'tendencia' in resultado:
                    st.markdown("#### Dados da Tendência")
                    st.dataframe(resultado['tendencia'], use_container_width=True)
                    
                    # Download dos dados
                    csv_data = resultado['tendencia'].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Baixar dados da tendência (CSV)",
                        csv_data,
                        file_name="tendencia_temporal.csv",
                        mime="text/csv"
                    )
    
    # Análise de Texto
    elif tipo_analise == "Análise de Texto":
        st.markdown("### Análise de Texto")
        st.markdown("Explore padrões em campos de texto")
        
        # Selecionar campos de texto
        colunas_texto = df_filtrado.select_dtypes(include=['object']).columns.tolist()
        colunas_texto = [col for col in colunas_texto if col not in ['data_registro']]
        
        if len(colunas_texto) == 0:
            st.warning("Não há campos de texto disponíveis para análise.")
        else:
            var_texto = st.selectbox(
                "Campo de texto para análise:",
                options=colunas_texto,
                index=colunas_texto.index('humor_diario') if 'humor_diario' in colunas_texto else 0
            )
            
            # Realizar análise
            resultado = realizar_analise_estatistica(df_filtrado, "analise_texto", var_texto)
            
            if 'erro' in resultado:
                st.error(resultado['erro'])
            else:
                # Mostrar resultados
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Distribuição de Sentimentos")
                    
                    if 'contagem_sentimentos' in resultado:
                        fig = px.pie(
                            names=resultado['contagem_sentimentos'].index,
                            values=resultado['contagem_sentimentos'].values,
                            title=f"Sentimentos em '{var_texto}'",
                            color=resultado['contagem_sentimentos'].index,
                            color_discrete_map={'Positivo': 'green', 'Neutro': 'gray', 'Negativo': 'red'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### Palavras Mais Frequentes")
                    
                    if 'palavras_frequentes' in resultado:
                        fig = px.bar(
                            x=resultado['palavras_frequentes'].index,
                            y=resultado['palavras_frequentes'].values,
                            title=f"Palavras mais frequentes em '{var_texto}'",
                            labels={'x': 'Palavra', 'y': 'Frequência'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Nuvem de palavras
                st.markdown("#### Nuvem de Palavras")
                
                img_str = criar_visualizacao(df_filtrado, "word_cloud", resultado=resultado)
                if img_str:
                    st.markdown(f"<img src='data:image/png;base64,{img_str}' style='width:100%'>", unsafe_allow_html=True)
                    
                # Polaridade média
                if 'polaridade_media' in resultado:
                    st.markdown("#### Análise de Sentimento")
                    polaridade = resultado['polaridade_media']
                    
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col2:
                        # Criar gráfico de gauge
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = polaridade,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Polaridade do Sentimento"},
                            gauge = {
                                'axis': {'range': [-1, 1]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [-1, -0.3], 'color': "red"},
                                    {'range': [-0.3, 0.3], 'color': "gray"},
                                    {'range': [0.3, 1], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "black", 'width': 4},
                                    'thickness': 0.75,
                                    'value': polaridade
                                }
                            }
                        ))
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Interpretação
                    if polaridade > 0.3:
                        st.success(f"O conteúdo de '{var_texto}' tem um sentimento predominantemente **positivo**.")
                    elif polaridade < -0.3:
                        st.error(f"O conteúdo de '{var_texto}' tem um sentimento predominantemente **negativo**.")
                    else:
                        st.info(f"O conteúdo de '{var_texto}' tem um sentimento predominantemente **neutro**.")

# Função para exibir previsões
def display_predictions(df, df_filtrado):
    st.title("Previsões e Modelos")
    st.markdown("Utilize modelos preditivos para antecipar tendências")
    
    # Tipo de previsão
    tipo_previsao = st.radio(
        "Tipo de Previsão",
        ["Regressão Multivariada", "Previsão Temporal", "Clusterização Avançada"]
    )
    
    # Regressão Multivariada
    if tipo_previsao == "Regressão Multivariada":
        st.markdown("### Regressão Multivariada")
        st.markdown("Preveja uma variável com base em múltiplas características")
        
        # Selecionar variável alvo
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        
        if len(colunas_numericas) < 2:
            st.warning("Não há variáveis numéricas suficientes para criar um modelo de previsão.")
        else:
            var_target = st.selectbox(
                "Variável a ser prevista:",
                options=colunas_numericas,
                index=colunas_numericas.index('peso') if 'peso' in colunas_numericas else 0
            )
            
            # Selecionar variáveis preditoras
            opcoes_preditoras = [col for col in colunas_numericas if col != var_target]
            vars_preditoras = st.multiselect(
                "Variáveis preditoras:",
                options=opcoes_preditoras,
                default=opcoes_preditoras[:min(3, len(opcoes_preditoras))]
            )
            
            # Criar modelo
            if len(vars_preditoras) > 0 and st.button("Criar Modelo"):
                with st.spinner("Treinando modelo..."):
                    resultado = realizar_previsao(df_filtrado, var_target, vars_preditoras)
                    
                    if 'erro' in resultado:
                        st.error(resultado['erro'])
                    else:
                        # Métricas do modelo
                        st.markdown("#### Desempenho do Modelo")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("R² (Coeficiente de Determinação)", f"{resultado['r2']:.4f}")
                        with col2:
                            st.metric("Erro Quadrático Médio", f"{resultado['mse']:.4f}")
                        
                        # Importância das variáveis
                        st.markdown("#### Importância das Variáveis")
                        
                        # Coeficientes
                        coefs = resultado['coeficientes']
                        
                        fig = px.bar(
                            coefs,
                            x='Coeficiente',
                            y='Variável',
                            orientation='h',
                            title="Importância das Variáveis",
                            color='Coeficiente',
                            color_continuous_scale=px.colors.diverging.RdBu_r
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Valores reais vs. previstos
                        st.markdown("#### Valores Reais vs. Previstos")
                        
                        df_pred = pd.DataFrame({
                            'Valor Real': resultado['y_test'],
                            'Valor Previsto': resultado['y_pred']
                        })
                        
                        fig = px.scatter(
                            df_pred,
                            x='Valor Real',
                            y='Valor Previsto',
                            trendline='ols',
                            title=f"Valores Reais vs. Previstos para {var_target}"
                        )
                        
                        # Adicionar linha diagonal (perfeita previsão)
                        min_val = min(df_pred['Valor Real'].min(), df_pred['Valor Previsto'].min())
                        max_val = max(df_pred['Valor Real'].max(), df_pred['Valor Previsto'].max())
                        
                        fig.add_trace(
                            go.Scatter(
                                x=[min_val, max_val],
                                y=[min_val, max_val],
                                mode='lines',
                                line=dict(color='green', dash='dash'),
                                name='Previsão Perfeita'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Simulador
                        st.markdown("#### Simulador de Previsão")
                        st.markdown("Ajuste os valores para prever o resultado")
                        
                        # Criar sliders para cada variável preditora
                        valores_simulacao = {}
                        for var in vars_preditoras:
                            min_val = df_filtrado[var].min()
                            max_val = df_filtrado[var].max()
                            medio_val = df_filtrado[var].mean()
                            
                            valores_simulacao[var] = st.slider(
                                f"{var}:",
                                min_value=float(min_val),
                                max_value=float(max_val),
                                value=float(medio_val),
                                step=(max_val - min_val) / 100
                            )
                        
                        # Botão para prever
                        if st.button("Fazer Previsão"):
                            # Preparar dados para previsão
                            X_pred = pd.DataFrame([valores_simulacao])
                            
                            # Fazer previsão
                            modelo = resultado['modelo']
                            previsao = modelo.predict(X_pred)[0]
                            
                            # Exibir resultado
                            st.markdown(f"#### Resultado da Previsão")
                            st.markdown(f"O valor previsto para **{var_target}** é:")
                            st.markdown(f"<h2 style='text-align: center; color: #4e7fff;'>{previsao:.2f}</h2>", unsafe_allow_html=True)
    
    # Previsão Temporal
    elif tipo_previsao == "Previsão Temporal":
        st.markdown("### Previsão Temporal")
        st.markdown("Projete tendências futuras com base em dados históricos")
        
        # Verificar se há dados temporais
        if 'data_registro' not in df_filtrado.columns:
            st.warning("O conjunto de dados não possui a coluna 'data_registro' necessária para previsão temporal.")
        else:
            # Selecionar variável para prever
            colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
            
            if len(colunas_numericas) == 0:
                st.warning("Não há variáveis numéricas para realizar previsão temporal.")
            else:
                var_alvo = st.selectbox(
                    "Variável para prever:",
                    options=colunas_numericas,
                    index=0
                )
                
                # Período de previsão
                col1, col2 = st.columns(2)
                
                with col1:
                    frequencia = st.selectbox(
                        "Frequência da previsão:",
                        options=[("Diária", "D"), ("Semanal", "W"), ("Mensal", "M"), ("Trimestral", "Q")],
                        format_func=lambda x: x[0],
                        index=2
                    )
                
                with col2:
                    periodos = st.slider(
                        "Períodos a prever:",
                        min_value=1,
                        max_value=24,
                        value=12
                    )
                
                # Criar modelo
                if st.button("Gerar Previsão"):
                    with st.spinner("Gerando previsão temporal..."):
                        resultado = realizar_previsao_temporal(df_filtrado, var_alvo, frequencia[1], periodos)
                        
                        if 'erro' in resultado:
                            st.error(resultado['erro'])
                        else:
                            # Visualizar série temporal
                            st.markdown("#### Série Temporal e Previsão")
                            
                            # Preparar dados para plotagem
                            serie_original = resultado['serie_original']
                            treino = resultado['treino']
                            teste = resultado['teste']
                            predicao_teste = resultado['predicao_teste']
                            predicao_futura = resultado['predicao_futura']
                            datas_futuras = resultado['datas_futuras']
                            
                            # Criar figura
                            fig = go.Figure()
                            
                            # Adicionar dados originais
                            fig.add_trace(
                                go.Scatter(
                                    x=serie_original.index,
                                    y=serie_original.values,
                                    mode='lines+markers',
                                    name='Dados Originais',
                                    line=dict(color='blue')
                                )
                            )
                            
                            # Adicionar dados de treino
                            fig.add_trace(
                                go.Scatter(
                                    x=treino.index,
                                    y=treino.values,
                                    mode='lines',
                                    name='Treino',
                                    line=dict(color='green')
                                )
                            )
                            
                            # Adicionar dados de teste
                            fig.add_trace(
                                go.Scatter(
                                    x=teste.index,
                                    y=teste.values,
                                    mode='lines',
                                    name='Teste',
                                    line=dict(color='red')
                                )
                            )
                            
                            # Adicionar previsão para o teste
                            fig.add_trace(
                                go.Scatter(
                                    x=teste.index,
                                    y=predicao_teste,
                                    mode='lines',
                                    name='Previsão (Teste)',
                                    line=dict(color='orange', dash='dash')
                                )
                            )
                            
                            # Adicionar previsão futura
                            fig.add_trace(
                                go.Scatter(
                                    x=datas_futuras,
                                    y=predicao_futura,
                                    mode='lines+markers',
                                    name='Previsão Futura',
                                    line=dict(color='purple', dash='dash')
                                )
                            )
                            
                            # Adicionar área sombreada para indicar projeção
                            fig.add_vrect(
                                x0=serie_original.index[-1],
                                x1=datas_futuras[-1],
                                fillcolor="gray",
                                opacity=0.2,
                                layer="below",
                                line_width=0
                            )
                            
                            # Layout
                            fig.update_layout(
                                title=f"Previsão Temporal para {var_alvo}",
                                xaxis_title="Data",
                                yaxis_title=var_alvo,
                                legend=dict(x=0, y=1)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Decomposição da série temporal
                            st.markdown("#### Decomposição da Série Temporal")
                            
                            # Criar subplots para componentes
                            fig = make_subplots(
                                rows=4, cols=1,
                                subplot_titles=("Série Original", "Tendência", "Sazonalidade", "Resíduo")
                            )
                            
                            # Adicionar série original
                            fig.add_trace(
                                go.Scatter(
                                    x=serie_original.index,
                                    y=serie_original.values,
                                    mode='lines',
                                    name='Original'
                                ),
                                row=1, col=1
                            )
                            
                            # Adicionar tendência
                            fig.add_trace(
                                go.Scatter(
                                    x=resultado['tendencia'].index,
                                    y=resultado['tendencia'].values,
                                    mode='lines',
                                    name='Tendência',
                                    line=dict(color='red')
                                ),
                                row=2, col=1
                            )
                            
                            # Adicionar sazonalidade
                            fig.add_trace(
                                go.Scatter(
                                    x=resultado['sazonalidade'].index,
                                    y=resultado['sazonalidade'].values,
                                    mode='lines',
                                    name='Sazonalidade',
                                    line=dict(color='green')
                                ),
                                row=3, col=1
                            )
                            
                            # Adicionar resíduo
                            fig.add_trace(
                                go.Scatter(
                                    x=resultado['residuo'].index,
                                    y=resultado['residuo'].values,
                                    mode='lines',
                                    name='Resíduo',
                                    line=dict(color='purple')
                                ),
                                row=4, col=1
                            )
                            
                            # Layout
                            fig.update_layout(height=800)
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Valores previstos
                            st.markdown("#### Valores Previstos")
                            
                            df_previsao = pd.DataFrame({
                                'Data': datas_futuras,
                                'Previsão': predicao_futura
                            })
                            
                            st.dataframe(df_previsao, use_container_width=True)
                            
                            # Download da previsão
                            csv_data = df_previsao.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Baixar previsão (CSV)",
                                csv_data,
                                file_name="previsao_temporal.csv",
                                mime="text/csv"
                            )
    
    # Clusterização Avançada
    elif tipo_previsao == "Clusterização Avançada":
        st.markdown("### Clusterização Avançada")
        st.markdown("Identificação de grupos naturais e perfis de pets")
        
        # Método de clusterização
        metodo = st.selectbox(
            "Método de clusterização:",
            ["K-Means", "DBSCAN", "PCA + K-Means"]
        )
        
        # Selecionar variáveis
        colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
        
        if len(colunas_numericas) < 2:
            st.warning("Não há variáveis numéricas suficientes para clusterização.")
        else:
            vars_selecionadas = st.multiselect(
                "Selecione variáveis para clusterização:",
                options=colunas_numericas,
                default=colunas_numericas[:min(4, len(colunas_numericas))]
            )
            
            if len(vars_selecionadas) >= 2:
                # Parâmetros específicos por método
                if metodo == "K-Means":
                    n_clusters = st.slider("Número de clusters:", 2, 10, 4)
                    
                    if st.button("Executar Clusterização"):
                        # Preparar dados
                        X = df_filtrado[vars_selecionadas].dropna()
                        
                        # Escalar dados
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # Aplicar K-means
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(X_scaled)
                        
                        # Adicionar clusters ao dataframe
                        X_clusters = X.copy()
                        X_clusters['cluster'] = clusters
                        
                        # Calcular silhouette score
                        silhouette = silhouette_score(X_scaled, clusters)
                        
                        # Exibir métricas
                        st.markdown("#### Qualidade dos Clusters")
                        st.markdown(f"Silhouette Score: **{silhouette:.3f}**")
                        
                        # Interpretar qualidade
                        if silhouette > 0.7:
                            st.success("Excelente separação entre clusters")
                        elif silhouette > 0.5:
                            st.info("Boa separação entre clusters")
                        elif silhouette > 0.3:
                            st.warning("Separação razoável entre clusters")
                        else:
                            st.error("Baixa separação entre clusters")
                        
                        # Visualização
                        st.markdown("#### Visualização dos Clusters")
                        
                        if len(vars_selecionadas) == 2:
                            # Visualização direta para 2 dimensões
                            fig = px.scatter(
                                X_clusters,
                                x=vars_selecionadas[0],
                                y=vars_selecionadas[1],
                                color='cluster',
                                title=f"Clusterização com K-means ({vars_selecionadas[0]} vs {vars_selecionadas[1]})"
                            )
                            
                            # Adicionar centróides
                            centros = scaler.inverse_transform(kmeans.cluster_centers_)
                            
                            for i in range(n_clusters):
                                fig.add_trace(
                                    go.Scatter(
                                        x=[centros[i, 0]],
                                        y=[centros[i, 1]],
                                        mode='markers',
                                        marker=dict(symbol='x', size=15, color='black'),
                                        name=f'Centróide {i}'
                                    )
                                )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                        else:
                            # Para mais de 2 dimensões, mostrar matriz de dispersão
                            vars_plot = vars_selecionadas[:4]  # Limitar a 4 variáveis
                            
                            fig = px.scatter_matrix(
                                X_clusters,
                                dimensions=vars_plot,
                                color='cluster',
                                title="Matriz de Dispersão com Clusters"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Estatísticas por cluster
                        st.markdown("#### Perfil dos Clusters")
                        
                        perfil_clusters = X_clusters.groupby('cluster').mean()
                        
                        fig = go.Figure()
                        
                        # Normalizar para comparação
                        for var in vars_selecionadas:
                            min_val = perfil_clusters[var].min()
                            max_val = perfil_clusters[var].max()
                            
                            if max_val > min_val:
                                perfil_clusters[f'{var}_norm'] = (perfil_clusters[var] - min_val) / (max_val - min_val)
                            else:
                                perfil_clusters[f'{var}_norm'] = perfil_clusters[var] - min_val
                        
                        # Preparar variáveis normalizadas
                        vars_norm = [f'{var}_norm' for var in vars_selecionadas]
                        
                        # Criar gráfico de radar
                        for i in range(n_clusters):
                            fig.add_trace(
                                go.Scatterpolar(
                                    r=perfil_clusters.loc[i, vars_norm].values.tolist() + [perfil_clusters.loc[i, vars_norm[0]]],
                                    theta=vars_selecionadas + [vars_selecionadas[0]],
                                    fill='toself',
                                    name=f'Cluster {i}'
                                )
                            )
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 1]
                                )
                            ),
                            title="Perfil dos Clusters"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Mostrar estatísticas detalhadas
                        st.markdown("#### Estatísticas por Cluster")
                        
                        st.dataframe(perfil_clusters[vars_selecionadas], use_container_width=True)
                
                elif metodo == "DBSCAN":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        eps = st.slider("Epsilon (distância máxima):", 0.1, 2.0, 0.5, 0.1)
                    
                    with col2:
                        min_samples = st.slider("Mínimo de amostras:", 2, 20, 5)
                    
                    if st.button("Executar Clusterização"):
                        # Preparar dados
                        X = df_filtrado[vars_selecionadas].dropna()
                        
                        # Escalar dados
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # Aplicar DBSCAN
                        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
                        clusters = dbscan.fit_predict(X_scaled)
                        
                        # Adicionar clusters ao dataframe
                        X_clusters = X.copy()
                        X_clusters['cluster'] = clusters
                        
                        # Contar número de clusters (-1 é ruído)
                        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
                        n_ruido = list(clusters).count(-1)
                        
                        # Exibir métricas
                        st.markdown("#### Resultados da Clusterização")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Número de Clusters", n_clusters)
                        
                        with col2:
                            st.metric("Pontos de Ruído", n_ruido)
                        
                        with col3:
                            st.metric("% de Ruído", f"{n_ruido/len(clusters)*100:.1f}%")
                        
                        # Visualização
                        st.markdown("#### Visualização dos Clusters")
                        
                        if len(vars_selecionadas) == 2:
                            # Visualização direta para 2 dimensões
                            fig = px.scatter(
                                X_clusters,
                                x=vars_selecionadas[0],
                                y=vars_selecionadas[1],
                                color='cluster',
                                title=f"Clusterização com DBSCAN ({vars_selecionadas[0]} vs {vars_selecionadas[1]})",
                                color_continuous_scale=px.colors.qualitative.Bold
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                        else:
                            # Para mais de 2 dimensões, reduzir com PCA
                            pca = PCA(n_components=2)
                            X_pca = pca.fit_transform(X_scaled)
                            
                            X_pca_df = pd.DataFrame(X_pca, columns=['Componente 1', 'Componente 2'])
                            X_pca_df['cluster'] = clusters
                            
                            fig = px.scatter(
                                X_pca_df,
                                x='Componente 1',
                                y='Componente 2',
                                color='cluster',
                                title="Clusterização com DBSCAN (PCA)",
                                color_continuous_scale=px.colors.qualitative.Bold
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Estatísticas por cluster
                        if n_clusters > 0:
                            st.markdown("#### Estatísticas por Cluster")
                            
                            cluster_stats = X_clusters.groupby('cluster').agg(['mean', 'count'])
                            st.dataframe(cluster_stats, use_container_width=True)
                
                elif metodo == "PCA + K-Means":
                    n_clusters = st.slider("Número de clusters:", 2, 10, 4)
                    
                    if st.button("Executar Clusterização"):
                        # Preparar dados
                        X = df_filtrado[vars_selecionadas].dropna()
                        
                        # Escalar dados
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # Aplicar PCA
                        pca = PCA(n_components=min(2, len(vars_selecionadas)))
                        X_pca = pca.fit_transform(X_scaled)
                        
                        # Explicação da variância
                        var_explicada = pca.explained_variance_ratio_
                        
                        # Aplicar K-means nos dados reduzidos
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(X_pca)
                        
                        # Adicionar clusters ao dataframe
                        X_clusters = pd.DataFrame(X_pca, columns=['Componente 1', 'Componente 2'])
                        X_clusters['cluster'] = clusters
                        
                        # Exibir métricas
                        st.markdown("#### Análise de Componentes Principais (PCA)")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Variância Explicada (Componente 1)", f"{var_explicada[0]*100:.1f}%")
                        
                        with col2:
                            if len(var_explicada) > 1:
                                st.metric("Variância Explicada (Componente 2)", f"{var_explicada[1]*100:.1f}%")
                        
                        # Mostrar gráfico de variância explicada
                        var_cumulativa = np.cumsum(var_explicada)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(
                            go.Bar(
                                x=[f'PC{i+1}' for i in range(len(var_explicada))],
                                y=var_explicada,
                                name='Variância Explicada'
                            )
                        )
                        
                        fig.add_trace(
                            go.Scatter(
                                x=[f'PC{i+1}' for i in range(len(var_explicada))],
                                y=var_cumulativa,
                                mode='lines+markers',
                                name='Variância Cumulativa'
                            )
                        )
                        
                        fig.update_layout(
                            title='Variância Explicada por Componente',
                            yaxis_title='Proporção da Variância',
                            yaxis=dict(range=[0, 1])
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Visualização dos clusters
                        st.markdown("#### Visualização dos Clusters (PCA)")
                        
                        fig = px.scatter(
                            X_clusters,
                            x='Componente 1',
                            y='Componente 2',
                            color='cluster',
                            title="Clusterização com K-means (após PCA)"
                        )
                        
                        # Adicionar centróides
                        for i in range(n_clusters):
                            fig.add_trace(
                                go.Scatter(
                                    x=[kmeans.cluster_centers_[i, 0]],
                                    y=[kmeans.cluster_centers_[i, 1]],
                                    mode='markers',
                                    marker=dict(symbol='x', size=15, color='black'),
                                    name=f'Centróide {i}'
                                )
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Importância das variáveis para os componentes
                        st.markdown("#### Importância das Variáveis nos Componentes Principais")
                        
                        loadings = pca.components_
                        
                        loadings_df = pd.DataFrame(
                            loadings.T,
                            columns=[f'Componente {i+1}' for i in range(loadings.shape[0])],
                            index=vars_selecionadas
                        )
                        
                        st.dataframe(loadings_df, use_container_width=True)
                        
                        # Visualizar loading plot
                        fig = go.Figure()
                        
                        for i, var in enumerate(vars_selecionadas):
                            fig.add_trace(
                                go.Scatter(
                                    x=[0, loadings[0, i]],
                                    y=[0, loadings[1, i]],
                                    mode='lines+markers+text',
                                    name=var,
                                    text=['', var],
                                    textposition='top center'
                                )
                            )
                        
                        # Adicionar círculo de correlação
                        theta = np.linspace(0, 2*np.pi, 100)
                        x = np.cos(theta)
                        y = np.sin(theta)
                        
                        fig.add_trace(
                            go.Scatter(
                                x=x,
                                y=y,
                                mode='lines',
                                line=dict(color='gray', dash='dash'),
                                name='Círculo de Correlação'
                            )
                        )
                        
                        fig.update_layout(
                            title='Loading Plot - Importância das Variáveis',
                            xaxis_title='Componente 1',
                            yaxis_title='Componente 2',
                            xaxis=dict(range=[-1, 1]),
                            yaxis=dict(range=[-1, 1])
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione pelo menos duas variáveis para continuar.")

# Função para exibir insights com IA
def display_ai_insights(df, df_filtrado):
    st.title("Relatórios com IA")
    st.markdown("Análises avançadas geradas por inteligência artificial")
    
    # Tipo de análise
    tipo_analise = st.selectbox(
        "Tipo de Análise",
        ["Análise Geral", "Padrões por Região", "Tendências por Tipo de Pet", 
         "Oportunidades de Negócio", "Análise Personalizada"]
    )
    
    # Configurar parâmetros da IA
    with st.expander("Configurações da IA"):
        temperatura = st.slider("Temperatura (criatividade):", 0.0, 1.0, 0.7, 0.1)
        st.info("Temperaturas mais baixas produzem análises mais conservadoras, enquanto temperaturas mais altas geram insights mais criativos, mas potencialmente menos precisos.")
    
    # Definir a pergunta com base no tipo de análise
    if tipo_analise == "Análise Geral":
        pergunta = """
        Forneça uma análise geral dos dados de pets em Florianópolis. 
        Identifique:
        1. Padrões de distribuição geográfica
        2. Características predominantes
        3. Correlações entre variáveis
        4. Insights principais que não sejam óbvios
        5. Recomendações práticas baseadas nos dados
        """
    elif tipo_analise == "Padrões por Região":
        pergunta = """
        Analise a distribuição de pets por região/bairro de Florianópolis. 
        Responda:
        1. Existem concentrações específicas de tipos de pets em certas regiões?
        2. Como as características dos pets variam entre diferentes bairros?
        3. Há correlação entre renda média do bairro e características dos pets?
        4. Quais bairros apresentam maior taxa de adoção?
        5. Identifique padrões únicos por região que não são imediatamente óbvios
        """
    elif tipo_analise == "Tendências por Tipo de Pet":
        pergunta = """
        Analise as tendências para cada tipo de pet nos dados. 
        Considere:
        1. Distribuição de idade, peso e outras métricas por tipo de pet
        2. Comportamentos e características específicas de cada espécie
        3. Preferências alimentares por tipo
        4. Taxa de adoção e saúde por tipo de pet
        5. Identifique quaisquer padrões incomuns ou inesperados nos dados
        """
    elif tipo_analise == "Oportunidades de Negócio":
        pergunta = """
        Com base nos dados de pets em Florianópolis, identifique oportunidades de negócio:
        1. Áreas geográficas com potencial para novos serviços para pets
        2. Tipos de serviços ou produtos que poderiam atender necessidades não supridas
        3. Segmentos específicos de mercado (tipos de pet, faixas etárias) com demandas particulares
        4. Tendências emergentes que poderiam indicar futuras demandas
        5. Recomendações para negócios na área pet com base nos insights dos dados
        """
    else:  # Análise Personalizada
        pergunta = st.text_area(
            "Digite sua pergunta personalizada:",
            height=150,
            value="Analise os dados de pets em Florianópolis e identifique padrões, tendências e insights relevantes. Considere as características dos pets, distribuição geográfica, e qualquer correlação interessante entre variáveis."
        )
    
    # Botão para gerar análise
    if st.button("Gerar Relatório com IA", type="primary"):
        with st.spinner("A IA está analisando os dados... Isso pode levar alguns segundos."):
            # Chamar a API Gemini
            resultado_ia = analisar_com_ia(df_filtrado, pergunta, temperatura)
            
            # Exibir resultado
            st.markdown("## Relatório de Análise")
            st.markdown(resultado_ia)
            
            # Opção para download
            report_download = resultado_ia.encode('utf-8')
            st.download_button(
                label="Baixar Relatório (TXT)",
                data=report_download,
                file_name="relatorio_ia_pets.txt",
                mime="text/plain"
            )
    
    # Exemplos de perguntas
    with st.expander("Exemplos de perguntas para análise personalizada"):
        st.markdown("""
        - Como a saúde dos pets varia em função da alimentação e idade?
        - Quais são os perfis típicos de pets adotados versus não adotados?
        - Existe relação entre características dos pets e renda média dos bairros?
        - Quais bairros apresentam maior diversidade de tipos de pets?
        - Baseado nos dados, quais seriam os melhores locais para abrir uma clínica veterinária especializada?
        - Quais são as raças de cachorro mais populares em cada região da cidade?
        - Existe correlação entre peso e humor diário dos pets?
        - Que insights os dados fornecem sobre as preferências alimentares dos diferentes tipos de pets?
        """)
    
    # Análises pré-geradas
    st.subheader("Análises Rápidas Pré-geradas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Distribuição de Tipos"):
            with st.spinner("Gerando análise..."):
                pergunta_rapida = "Analise a distribuição dos diferentes tipos de pets nos dados. Quais tipos são mais comuns? Existem variações significativas por bairro ou região? Forneça um resumo conciso."
                resultado = analisar_com_ia(df_filtrado, pergunta_rapida, 0.5)
                st.info(resultado)
    
    with col2:
        if st.button("🐕 Perfil de Adoção"):
            with st.spinner("Gerando análise..."):
                pergunta_rapida = "Analise o perfil dos pets adotados. Quais características são mais comuns entre pets adotados? Existem diferenças significativas entre pets adotados e não adotados? Forneça um resumo conciso."
                resultado = analisar_com_ia(df_filtrado, pergunta_rapida, 0.5)
                st.info(resultado)
    
    with col3:
        if st.button("🏙️ Análise por Bairro"):
            with st.spinner("Gerando análise..."):
                pergunta_rapida = "Analise as diferenças entre bairros em termos de quantidade e tipos de pets. Quais bairros se destacam? Existem padrões interessantes? Forneça um resumo conciso."
                resultado = analisar_com_ia(df_filtrado, pergunta_rapida, 0.5)
                st.info(resultado)

# Função para gerenciar dados
def display_data_management(df, df_filtrado):
    st.title("Gerenciar Dados")
    st.markdown("Visualize, adicione e modifique dados de pets")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Visualizar Dados", "➕ Adicionar Pet", "📤 Exportar", "📥 Importar"])
    
    # Visualizar Dados
    with tab1:
        st.subheader("Dados Atuais")
        
        # Opções de visualização
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Seleção de colunas para exibir
            todas_colunas = df.columns.tolist()
            colunas_padrao = ['nome', 'bairro', 'tipo_pet', 'raca', 'idade', 'peso', 'adotado']
            colunas_padrao = [col for col in colunas_padrao if col in todas_colunas]
            
            colunas_selecionadas = st.multiselect(
                "Selecionar colunas:",
                options=todas_colunas,
                default=colunas_padrao
            )
            
            # Número de registros para exibir
            n_registros = st.slider(
                "Número de registros:",
                min_value=10,
                max_value=min(1000, len(df_filtrado)),
                value=min(100, len(df_filtrado)),
                step=10
            )
            
            # Opção de ordenação
            if len(colunas_selecionadas) > 0:
                coluna_ordem = st.selectbox(
                    "Ordenar por:",
                    options=['Nenhum'] + colunas_selecionadas
                )
                
                ordem_asc = st.checkbox("Ordem ascendente", value=True)
        
        with col2:
            # Aplicar filtros de visualização
            if len(colunas_selecionadas) > 0:
                df_exibir = df_filtrado[colunas_selecionadas].copy()
                
                if coluna_ordem != 'Nenhum' and coluna_ordem in df_exibir.columns:
                    df_exibir = df_exibir.sort_values(coluna_ordem, ascending=ordem_asc)
                
                # Exibir dataframe
                st.dataframe(df_exibir.head(n_registros), use_container_width=True)
                
                # Opção para baixar os dados exibidos
                csv_dados_exibidos = df_exibir.head(n_registros).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar dados exibidos (CSV)",
                    data=csv_dados_exibidos,
                    file_name="dados_filtrados.csv",
                    mime="text/csv"
                )
            else:
                st.info("Selecione pelo menos uma coluna para exibir os dados.")
        
        # Estatísticas resumidas
        with st.expander("Ver estatísticas resumidas"):
            if len(df_filtrado) > 0:
                # Selecionar apenas colunas numéricas
                df_num = df_filtrado.select_dtypes(include=['number'])
                
                if not df_num.empty:
                    st.dataframe(df_num.describe(), use_container_width=True)
                else:
                    st.info("Não há colunas numéricas para exibir estatísticas.")
            else:
                st.info("Não há dados para exibir estatísticas.")
    
    # Adicionar Pet
    with tab2:
        st.subheader("Adicionar Novo Pet")
        
        with st.form("form_adicionar_pet"):
            # Dividir em duas colunas
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Pet")
                
                # Tipo de pet
                tipo_pet = st.selectbox(
                    "Tipo de Pet",
                    options=['Cachorro', 'Gato', 'Ave', 'Peixe', 'Roedor', 'Réptil']
                )
                
                # Raças baseadas no tipo selecionado
                racas_por_tipo = {
                    'Cachorro': ['Vira-lata', 'Poodle', 'Labrador', 'Golden Retriever', 'Bulldog', 'Pitbull', 'Shih Tzu', 'Yorkshire', 'Pastor Alemão', 'Pinscher', 'Outro'],
                    'Gato': ['SRD', 'Siamês', 'Persa', 'Maine Coon', 'Ragdoll', 'Sphynx', 'Angorá', 'Bengal', 'British Shorthair', 'Norueguês da Floresta', 'Outro'],
                    'Ave': ['Canário', 'Periquito', 'Calopsita', 'Papagaio', 'Arara', 'Agapornis', 'Mandarim', 'Outro'],
                    'Peixe': ['Betta', 'Kinguio', 'Guppy', 'Tetra', 'Acará', 'Coridora', 'Pleco', 'Outro'],
                    'Roedor': ['Hamster', 'Porquinho da Índia', 'Chinchila', 'Rato', 'Gerbil', 'Outro'],
                    'Réptil': ['Tartaruga', 'Jabuti', 'Iguana', 'Gecko', 'Cobra', 'Outro']
                }
                
                racas_disponiveis = racas_por_tipo.get(tipo_pet, ['Não especificado'])
                raca = st.selectbox("Raça", options=racas_disponiveis)
                
                # Opção para especificar "Outro"
                if raca == 'Outro':
                    raca = st.text_input("Especifique a raça")
                
                idade = st.number_input("Idade (anos)", min_value=0, max_value=30, value=1)
                peso = st.number_input("Peso (kg)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
            
            with col2:
                # Obter bairros existentes
                bairros = sorted(df['bairro'].unique().tolist())
                bairro = st.selectbox("Bairro", options=bairros)
                
                sexo = st.radio("Sexo", options=["Macho", "Fêmea"])
                
                # Tipo de alimentação
                tipo_comida = st.selectbox(
                    "Tipo de Comida", 
                    options=['Ração Premium', 'Ração Super Premium', 'Comida Natural', 'Comida Caseira', 'Ração Medicinal', 'Mista']
                )
                
                # Humor
                humor_diario = st.selectbox(
                    "Humor Diário", 
                    options=['Feliz', 'Calmo', 'Agitado', 'Ansioso', 'Entediado', 'Brincalhão', 'Agressivo', 'Medroso']
                )
                
                adotado = st.checkbox("É adotado?")
            
            # Informações de contato
            telefone = st.text_input("Telefone de Contato", placeholder="(48) 9XXXX-XXXX")
            
            # Campos adicionais se disponíveis
            campos_extras = {}
            
            if 'status_vacinacao' in df.columns:
                campos_extras['status_vacinacao'] = st.selectbox(
                    "Status de Vacinação",
                    options=['Em dia', 'Parcial', 'Pendente', 'Não se aplica']
                )
            
            if 'estado_saude' in df.columns:
                campos_extras['estado_saude'] = st.selectbox(
                    "Estado de Saúde",
                    options=['Excelente', 'Bom', 'Regular', 'Requer atenção']
                )
            
            if 'comportamento' in df.columns:
                campos_extras['comportamento'] = st.selectbox(
                    "Comportamento",
                    options=['Sociável', 'Tímido', 'Territorialista', 'Independente', 'Carente', 'Dominante', 'Submisso']
                )
            
            if 'nivel_atividade' in df.columns:
                campos_extras['nivel_atividade'] = st.selectbox(
                    "Nível de Atividade",
                    options=['Muito Ativo', 'Ativo', 'Moderado', 'Tranquilo', 'Sedentário']
                )
            
            # Data de registro
            if 'data_registro' in df.columns:
                campos_extras['data_registro'] = st.date_input("Data de Registro", value=pd.Timestamp.today())
            
            # Região
            if 'regiao' in df.columns:
                regioes_disponiveis = sorted(df['regiao'].unique().tolist())
                campos_extras['regiao'] = st.selectbox("Região", options=regioes_disponiveis)
            
            # Botão de submissão
            submitted = st.form_submit_button("Adicionar Pet")
            
            if submitted:
                if not nome:
                    st.error("Por favor, informe o nome do pet.")
                elif not raca:
                    st.error("Por favor, informe a raça do pet.")
                elif not telefone:
                    st.error("Por favor, informe um telefone de contato.")
                else:
                    # Criar novo pet
                    novo_pet = {
                        'nome': nome,
                        'bairro': bairro,
                        'tipo_pet': tipo_pet,
                        'raca': raca,
                        'idade': idade,
                        'peso': peso,
                        'sexo': sexo,
                        'tipo_comida': tipo_comida,
                        'humor_diario': humor_diario,
                        'adotado': adotado,
                        'telefone': telefone
                    }
                    
                    # Adicionar campos extras se disponíveis
                    for campo, valor in campos_extras.items():
                        novo_pet[campo] = valor
                    
                    # Adicionar ao dataframe
                    df_atualizado = adicionar_pet(novo_pet, df)
                    
                    # Mostrar mensagem de sucesso
                    st.success(f"Pet {nome} adicionado com sucesso!")
                    st.balloons()
    
    # Exportar Dados
    with tab3:
        st.subheader("Exportar Dados")
        
        # Opções de exportação
        formato_exportacao = st.radio(
            "Formato de exportação:",
            options=["CSV", "Excel", "JSON"]
        )
        
        # Opção para incluir apenas dados filtrados
        incluir_filtrados = st.checkbox("Exportar apenas dados filtrados", value=True)
        
        df_exportar = df_filtrado if incluir_filtrados else df
        
        # Mostrar prévia
        st.markdown(f"**Prévia dos dados a serem exportados ({len(df_exportar)} registros):**")
        st.dataframe(df_exportar.head(5), use_container_width=True)
        
        # Opções específicas por formato
        if formato_exportacao == "CSV":
            # Opções de CSV
            col1, col2 = st.columns(2)
            with col1:
                separador = st.selectbox("Separador:", options=[",", ";", "\t"], format_func=lambda x: "Vírgula (,)" if x == "," else "Ponto e vírgula (;)" if x == ";" else "Tab (\t)")
            with col2:
                incluir_cabecalho = st.checkbox("Incluir cabeçalho", value=True)
            
            # Preparar dados CSV
            csv_data = df_exportar.to_csv(sep=separador, index=False, header=incluir_cabecalho).encode('utf-8')
            
            # Botão de download
            st.download_button(
                label="Baixar CSV",
                data=csv_data,
                file_name="pets_data.csv",
                mime="text/csv"
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
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
                mime="application/json"
            )
    
    # Importar Dados
    with tab4:
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
                            options=[",", ";", "\t"], 
                            format_func=lambda x: "Vírgula (,)" if x == "," else "Ponto e vírgula (;)" if x == ";" else "Tab (\t)",
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
                st.dataframe(df_importado.head(5), use_container_width=True)
                
                # Opções de importação
                modo_importacao = st.radio(
                    "Modo de importação:",
                    options=["Substituir dados existentes", "Anexar aos dados existentes"]
                )
                
                # Mapeamento de colunas
                if st.checkbox("Mapear colunas", value=False):
                    st.markdown("**Mapeamento de colunas (opcional):**")
                    st.markdown("Selecione a coluna do arquivo importado que corresponde a cada coluna do sistema.")
                    
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
                    if st.button("Aplicar Mapeamento"):
                        if mapeamento:
                            # Criar dataframe mapeado
                            df_mapeado = pd.DataFrame()
                            
                            for col_destino, col_origem in mapeamento.items():
                                df_mapeado[col_destino] = df_importado[col_origem]
                            
                            # Atualizar dataframe importado
                            df_importado = df_mapeado
                            
                            st.success("Mapeamento aplicado com sucesso!")
                            st.dataframe(df_importado.head(5), use_container_width=True)
                
                # Botão de importação
                if st.button("Importar Dados"):
                    if modo_importacao == "Substituir dados existentes":
                        # Verificar se todas as colunas obrigatórias estão presentes
                        colunas_obrigatorias = ['nome', 'bairro', 'tipo_pet', 'raca']
                        faltando = [col for col in colunas_obrigatorias if col not in df_importado.columns]
                        
                        if faltando:
                            st.error(f"O arquivo importado não contém as colunas obrigatórias: {', '.join(faltando)}")
                        else:
                            # Substituir dados
                            df_importado.to_csv('data/pets_data.csv', index=False)
                            st.success(f"Dados importados com sucesso! {len(df_importado)} registros substituíram os dados existentes.")
                            st.balloons()
                            
                            # Recarregar a página para atualizar os dados
                            st.experimental_rerun()
                    else:
                        # Anexar aos dados existentes
                        df_combinado = pd.concat([df, df_importado], ignore_index=True)
                        df_combinado.to_csv('data/pets_data.csv', index=False)
                        
                        st.success(f"Dados importados com sucesso! {len(df_importado)} registros adicionados aos dados existentes.")
                        st.balloons()
                        
                        # Recarregar a página para atualizar os dados
                        st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Erro ao importar dados: {str(e)}")
                st.exception(e)

# Executar aplicação
if __name__ == '__main__':
    main()
