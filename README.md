
# PetCare Analytics - Sistema Avançado de Análise de Pets

## Descrição
PetCare Analytics é uma plataforma avançada desenvolvida para análise de dados sobre a distribuição e características de pets em Florianópolis. O sistema utiliza Streamlit para criar uma interface de usuário interativa e integra diversas ferramentas de análise de dados e inteligência artificial.

## Funcionalidades

### Dashboard Interativo
- Visualização abrangente de métricas e gráficos
- Filtros contextuais por região, tipo de pet, bairro e status de adoção
- Gráficos dinâmicos com tecnologia Plotly

### Mapa Interativo
- Visualização geoespacial da distribuição de pets
- Mapa de calor de densidade populacional de pets
- Comparação de múltiplas variáveis por localização

### Análise Avançada de Dados
- Correlações estatísticas entre variáveis
- Clusterização para identificação de grupos naturais
- Detecção de anomalias
- Análise de regressão com métricas completas
- Análise temporal de tendências
- Processamento de linguagem natural para campos de texto

### Previsões e Modelos Preditivos
- Regressão multivariada para prever características
- Previsão temporal com decomposição de séries
- Clusterização avançada com PCA

### Integração com IA (Google Gemini)
- Análise automática de dados através de IA
- Relatórios personalizados gerados por inteligência artificial
- Insights avançados e detecção de padrões complexos

### Gerenciamento de Dados
- Interface para visualização e filtragem de dados
- Adição de novos registros
- Importação e exportação em múltiplos formatos (CSV, Excel, JSON)

## Requisitos de Sistema
- Python 3.8+
- Navegador web moderno
- Mínimo de 4GB de RAM (8GB recomendado)
- Conexão com internet (para integração com Google Gemini AI)

## Instalação

### Instalação Automática (Recomendado)
Execute o script setup-sistema-.js com Node.js:
```
node setup-sistema-.js
```

### Instalação Manual
1. Clone o repositório ou crie uma pasta para o projeto
2. Crie um ambiente virtual:
   - `python -m venv venv`
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Instale as dependências:
   - `pip install -r requirements.txt`
5. Execute a aplicação:
   - `streamlit run app.py`

## Estrutura de Dados
O sistema trabalha com os seguintes dados de pets:
- **nome**: Nome do pet
- **bairro**: Bairro de residência
- **tipo_pet**: Tipo de animal (Cachorro, Gato, Ave, etc.)
- **raca**: Raça específica do pet
- **idade**: Idade em anos
- **peso**: Peso em kg
- **sexo**: Sexo biológico (Macho/Fêmea)
- **tipo_comida**: Preferência alimentar
- **humor_diario**: Estado emocional predominante
- **adotado**: Status de adoção (Sim/Não)
- **telefone**: Contato do tutor
- **status_vacinacao**: Situação vacinal
- **estado_saude**: Condição de saúde geral
- **comportamento**: Traços comportamentais
- **nivel_atividade**: Nível de energia e atividade
- **data_registro**: Data de cadastro no sistema
- **regiao**: Região da cidade

## Tecnologias Utilizadas
- **Streamlit**: Interface de usuário
- **Pandas/NumPy**: Manipulação de dados
- **Plotly/Matplotlib/Seaborn**: Visualização de dados
- **Scikit-learn**: Machine learning e análise estatística
- **NLTK/TextBlob**: Processamento de linguagem natural
- **Google Gemini AI**: Integração com inteligência artificial
- **Statsmodels**: Análise estatística avançada
- **PyDeck**: Visualização geoespacial

## Créditos
Sistema desenvolvido por PetCare Analytics.
