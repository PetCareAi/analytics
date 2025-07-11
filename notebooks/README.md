# Notebooks de Análise - PetCareAi

Este diretório contém notebooks Jupyter para análises exploratórias, prototipagem de algoritmos e experimentos de ciência de dados.

## 📋 Estrutura dos Notebooks

### 📊 Análises Exploratórias
- `01_exploratory_data_analysis.ipynb` - Análise inicial dos dados de pets
- `02_data_quality_assessment.ipynb` - Avaliação da qualidade dos dados
- `03_statistical_analysis.ipynb` - Análises estatísticas descritivas
- `04_correlation_analysis.ipynb` - Análises de correlação entre variáveis

### 🤖 Machine Learning
- `ml_01_clustering_experiments.ipynb` - Experimentos com algoritmos de clustering
- `ml_02_classification_models.ipynb` - Modelos de classificação para adoção
- `ml_03_regression_analysis.ipynb` - Análises de regressão
- `ml_04_anomaly_detection.ipynb` - Detecção de anomalias em dados

### 📈 Visualizações
- `viz_01_dashboard_prototypes.ipynb` - Protótipos de dashboards
- `viz_02_interactive_plots.ipynb` - Gráficos interativos
- `viz_03_geospatial_analysis.ipynb` - Análises geoespaciais
- `viz_04_time_series_viz.ipynb` - Visualizações de séries temporais

### 🔬 Experimentos
- `exp_01_feature_engineering.ipynb` - Engenharia de características
- `exp_02_model_optimization.ipynb` - Otimização de modelos
- `exp_03_hyperparameter_tuning.ipynb` - Ajuste de hiperparâmetros
- `exp_04_ensemble_methods.ipynb` - Métodos de ensemble

## 🚀 Como Usar

### Pré-requisitos
```bash
pip install jupyter notebook
pip install ipython ipykernel
pip install pandas numpy matplotlib seaborn plotly
```

### Iniciar Jupyter
```bash
jupyter notebook
# ou
jupyter lab
```

### Executar Notebooks
1. Abra o Jupyter no navegador
2. Navegue para o diretório `notebooks/`
3. Clique no notebook desejado
4. Execute as células sequencialmente

## 📝 Convenções

### Estrutura Padrão dos Notebooks
1. **Introdução** - Objetivo e contexto
2. **Imports** - Bibliotecas necessárias
3. **Configurações** - Setup inicial
4. **Carregamento de Dados** - Importação e preparação
5. **Análise/Experimento** - Conteúdo principal
6. **Resultados** - Conclusões e insights
7. **Próximos Passos** - Recomendações

### Nomenclatura
- Use prefixos numéricos para ordem (`01_`, `02_`, etc.)
- Use nomes descritivos em inglês
- Use underscores para separar palavras
- Inclua categoria quando relevante (`ml_`, `viz_`, `exp_`)

### Boas Práticas
- Sempre documente o propósito do notebook
- Use markdown para explicar análises
- Mantenha células de código organizadas
- Limpe outputs antes de fazer commit
- Inclua versão dos dados utilizados

## 🗂️ Organização por Categoria

### `/exploratory/` - Análises Exploratórias
Notebooks focados em entender os dados, identificar padrões e gerar insights iniciais.

### `/modeling/` - Modelagem
Desenvolvimento e teste de modelos de machine learning.

### `/visualization/` - Visualizações
Criação de gráficos, dashboards e visualizações interativas.

### `/experiments/` - Experimentos
Testes de hipóteses, validação de conceitos e prototipagem.

### `/production/` - Produção
Notebooks que geram artefatos para produção (modelos, relatórios, etc.).

## 🔧 Configuração do Ambiente

### Jupyter Extensions Recomendadas
```bash
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

### Extensões Úteis
- **Variable Inspector** - Ver variáveis em tempo real
- **Table of Contents** - Navegação fácil
- **Code Folding** - Organizar código
- **ExecuteTime** - Tempo de execução das células

## 📊 Dados Utilizados

### Fonte Principal
- Banco de dados PostgreSQL via Supabase
- Tabela: `pets_analytics`
- Acesso via: `config/database.py`

### Dados de Exemplo
```python
# Template para carregar dados
import pandas as pd
from config.database import supabase

# Carregar dados
result = supabase.table('pets_analytics').select('*').execute()
df = pd.DataFrame(result.data)
```

### Colunas Principais
- `id` - Identificador único
- `nome` - Nome do pet
- `tipo_pet` - Tipo (Cão, Gato, etc.)
- `idade` - Idade em anos
- `peso` - Peso em kg
- `comportamento` - Perfil comportamental
- `score_adocao` - Score de adotabilidade
- `adotado` - Status de adoção

## 📈 Métricas e KPIs

### Métricas de Negócio
- Taxa de adoção por tipo de pet
- Tempo médio para adoção
- Score de adotabilidade médio
- Distribuição geográfica

### Métricas de Modelo
- Acurácia, Precisão, Recall
- R² para regressões
- Silhouette Score para clustering
- AUC-ROC para classificação

## 🔄 Workflow de Desenvolvimento

### 1. Exploração
- Carregue e explore os dados
- Identifique padrões e anomalias
- Documente insights

### 2. Prototipagem
- Teste algoritmos rapidamente
- Valide hipóteses
- Experimente com parâmetros

### 3. Desenvolvimento
- Implemente soluções robustas
- Otimize performance
- Documente metodologia

### 4. Validação
- Teste com dados novos
- Valide resultados
- Compare com baseline

### 5. Produção
- Exporte modelos
- Gere código de produção
- Documente para deploy

## 🔍 Exemplos de Análises

### Análise de Clustering
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Preparar dados
features = ['idade', 'peso', 'sociabilidade', 'energia']
X = df[features].fillna(df[features].mean())

# Normalizar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

# Visualizar
import plotly.express as px
fig = px.scatter(df, x='idade', y='peso', color=clusters)
fig.show()
```

### Análise Preditiva
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Preparar dados
X = df[features]
y = df['adotado']

# Dividir dados
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Treinar modelo
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Avaliar
accuracy = rf.score(X_test, y_test)
print(f"Acurácia: {accuracy:.3f}")
```

## 📚 Recursos Úteis

### Documentação
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Plotly Documentation](https://plotly.com/python/)
- [Jupyter Documentation](https://jupyter.org/documentation)

### Tutorials
- [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)
- [Kaggle Learn](https://www.kaggle.com/learn)
- [Towards Data Science](https://towardsdatascience.com/)

## 🤝 Contribuindo

### Adicionando Novos Notebooks
1. Use template padrão
2. Documente objetivo claramente
3. Inclua células de setup
4. Teste completamente
5. Limpe outputs antes do commit

### Review de Notebooks
- Verifique se executa do início ao fim
- Confirme se dados estão acessíveis
- Valide resultados e conclusões
- Aprove documentação

---

Para dúvidas ou sugestões sobre os notebooks, abra uma issue ou entre em contato com a equipe de Data Science.
