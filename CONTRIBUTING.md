# Guia de Contribuição - PetCareAI Analytics

Obrigado por seu interesse em contribuir com o PetCareAI Analytics! Este documento fornece diretrizes para contribuições que ajudem a manter a qualidade e consistência do projeto.

## 🎯 Como Contribuir

### Formas de Contribuição

- **🐛 Reportar Bugs**: Encontrou um problema? Nos ajude a corrigi-lo!
- **💡 Sugerir Funcionalidades**: Tem uma ideia interessante? Compartilhe conosco!
- **📝 Melhorar Documentação**: Documentação clara é essencial
- **🔧 Contribuir com Código**: Implementar novas funcionalidades ou correções
- **🧪 Escrever Testes**: Ajudar a manter a qualidade do código
- **🎨 Melhorar UI/UX**: Tornar a interface mais intuitiva
- **🌍 Tradução**: Ajudar com internacionalização

## 🚀 Começando

### 1. Configuração do Ambiente

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU_USUARIO/petcare-analytics.git
cd petcare-analytics

# Adicione o repositório original como upstream
git remote add upstream https://github.com/PetCareAi/analytics.git

# Configure o ambiente
./install.sh
./configure.sh
```

### 2. Estrutura do Projeto

```
petcare-analytics/
├── app.py                    # Aplicação principal
├── config/
│   └── database.py          # Configuração do banco
├── tests/                   # Testes automatizados
├── docs/                    # Documentação
├── assets/                  # Assets estáticos
├── data/                    # Dados temporários
├── models/                  # Modelos ML salvos
├── requirements.txt         # Dependências Python
├── .env.example            # Template de configuração
└── README.md               # Documentação principal
```

### 3. Configuração de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Executar testes
python -m pytest tests/

# Executar aplicação em modo dev
./run.sh --dev
```

## 📋 Processo de Contribuição

### 1. Antes de Começar

- 🔍 **Verifique Issues Existentes**: Procure se já existe uma issue relacionada
- 💬 **Discuta Grandes Mudanças**: Para funcionalidades grandes, abra uma issue primeiro
- 📖 **Leia a Documentação**: Familiarize-se com o projeto e arquitetura
- ✅ **Configure o Ambiente**: Certifique-se que tudo está funcionando

### 2. Criando uma Issue

#### Para Bugs 🐛

```markdown
**Descrição do Bug**
Descrição clara e concisa do que está errado.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
Descrição clara do que deveria acontecer.

**Comportamento Atual**
O que realmente acontece.

**Screenshots**
Se aplicável, adicione screenshots para ajudar a explicar o problema.

**Ambiente:**
- OS: [ex: Ubuntu 20.04]
- Python: [ex: 3.9.0]
- Streamlit: [ex: 1.31.1]
- Navegador: [ex: Chrome 120]

**Informações Adicionais**
Qualquer outra informação sobre o problema.
```

#### Para Funcionalidades 💡

```markdown
**Descrição da Funcionalidade**
Descrição clara e concisa da funcionalidade desejada.

**Problema que Resolve**
Qual problema esta funcionalidade resolve? Ex: Eu sempre fico frustrado quando [...]

**Solução Proposta**
Descrição clara e concisa do que você gostaria que acontecesse.

**Alternativas Consideradas**
Descrição de soluções alternativas ou funcionalidades que você considerou.

**Informações Adicionais**
Qualquer outra informação ou screenshots sobre a funcionalidade.
```

### 3. Workflow de Desenvolvimento

#### Criando uma Branch

```bash
# Atualize sua branch main
git checkout main
git pull upstream main

# Crie uma branch para sua feature
git checkout -b feature/nome-da-funcionalidade

# Ou para bug fix
git checkout -b bugfix/descricao-do-bug
```

#### Fazendo Commits

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Funcionalidade
git commit -m "feat(dashboard): adicionar gráfico de tendências"

# Bug fix
git commit -m "fix(auth): corrigir problema de timeout"

# Documentação
git commit -m "docs(api): adicionar exemplos de uso"

# Testes
git commit -m "test(ml): adicionar testes para clustering"
```

#### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação, ponto e vírgula faltando, etc
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Manutenção de código

### 4. Padrões de Código

#### Python Code Style

Seguimos o [PEP 8](https://pep8.org/) com algumas adaptações:

```python
# ✅ Bom
def calculate_adoption_score(pet_data: dict) -> float:
    """
    Calcula o score de adoção baseado nos dados do pet.
    
    Args:
        pet_data (dict): Dados do pet contendo idade, comportamento, etc.
        
    Returns:
        float: Score de adoção entre 0.0 e 5.0
        
    Raises:
        ValueError: Se dados obrigatórios estão faltando
    """
    if not pet_data.get('idade'):
        raise ValueError("Idade é obrigatória")
    
    score = 0.0
    
    # Calcular baseado na idade
    if pet_data['idade'] < 1:
        score += 1.0
    elif pet_data['idade'] <= 3:
        score += 0.8
    
    return min(5.0, score)

# ❌ Ruim
def calc_score(data):
    if not data.get('idade'):return 0
    score=0.0
    if data['idade']<1:score+=1.0
    elif data['idade']<=3:score+=0.8
    return min(5.0,score)
```

#### Streamlit Components

```python
# ✅ Bom
def display_pet_metrics(df: pd.DataFrame) -> None:
    """Exibe métricas dos pets de forma organizada."""
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_pets = len(df)
        st.metric("Total de Pets", total_pets)
    
    with col2:
        adopted_pets = df['adotado'].sum()
        st.metric("Pets Adotados", adopted_pets)
    
    with col3:
        adoption_rate = (adopted_pets / total_pets) * 100 if total_pets > 0 else 0
        st.metric("Taxa de Adoção", f"{adoption_rate:.1f}%")

# ❌ Ruim
def show_metrics(df):
    st.metric("Total", len(df))
    st.metric("Adotados", df['adotado'].sum())
```

#### Machine Learning Code

```python
# ✅ Bom
class PetMLAnalyzer:
    """Analisador de Machine Learning para dados de pets."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Inicializa o analisador com dados dos pets.
        
        Args:
            data (pd.DataFrame): DataFrame com dados dos pets
        """
        self.data = data.copy()
        self.models = {}
        self.scalers = {}
        
    def preprocess_data(self, target_column: str = None) -> pd.DataFrame:
        """
        Preprocessa os dados para análise ML.
        
        Args:
            target_column (str, optional): Coluna alvo para supervised learning
            
        Returns:
            pd.DataFrame: Dados preprocessados
        """
        # Implementação...
        pass
```

### 5. Testes

#### Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── test_auth.py
│   ├── test_ml.py
│   └── test_database.py
├── integration/             # Testes de integração
│   ├── test_api.py
│   └── test_workflows.py
├── e2e/                    # Testes end-to-end
│   └── test_user_journey.py
├── fixtures/               # Dados para testes
│   └── sample_data.csv
└── conftest.py            # Configurações pytest
```

#### Exemplo de Teste

```python
import pytest
import pandas as pd
from app import calculate_adoption_score, PetMLAnalyzer

class TestAdoptionScore:
    """Testes para cálculo de score de adoção."""
    
    def test_young_pet_high_score(self):
        """Pets jovens devem ter score alto."""
        pet_data = {'idade': 0.5, 'sociabilidade': 5, 'energia': 4}
        score = calculate_adoption_score(pet_data)
        assert score >= 4.0
        
    def test_old_pet_lower_score(self):
        """Pets idosos devem ter score menor."""
        pet_data = {'idade': 12, 'sociabilidade': 3, 'energia': 2}
        score = calculate_adoption_score(pet_data)
        assert score < 3.0
        
    def test_invalid_data_raises_error(self):
        """Dados inválidos devem gerar erro."""
        with pytest.raises(ValueError):
            calculate_adoption_score({})

class TestMLAnalyzer:
    """Testes para analisador ML."""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes."""
        return pd.DataFrame({
            'nome': ['Rex', 'Bella', 'Max'],
            'idade': [2, 5, 1],
            'peso': [25, 8, 30],
            'sociabilidade': [5, 3, 4],
            'adotado': [True, False, True]
        })
    
    def test_analyzer_initialization(self, sample_data):
        """Testa inicialização do analisador."""
        analyzer = PetMLAnalyzer(sample_data)
        assert len(analyzer.data) == 3
        assert 'nome' in analyzer.data.columns
```

#### Executando Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/test_ml.py

# Com cobertura
pytest --cov=app tests/

# Verbose
pytest -v

# Parar no primeiro erro
pytest -x
```

### 6. Documentação

#### Docstrings

Use docstrings no formato Google:

```python
def complex_function(param1: int, param2: str, param3: bool = False) -> dict:
    """
    Função que executa operação complexa.
    
    Args:
        param1 (int): Primeiro parâmetro
        param2 (str): Segundo parâmetro
        param3 (bool, optional): Terceiro parâmetro. Defaults to False.
        
    Returns:
        dict: Resultado da operação com as chaves:
            - success (bool): Se a operação foi bem-sucedida
            - data (any): Dados resultantes
            - message (str): Mensagem descritiva
            
    Raises:
        ValueError: Se param1 for negativo
        TypeError: Se param2 não for string
        
    Example:
        >>> result = complex_function(42, "test", True)
        >>> print(result['success'])
        True
    """
```

#### README e Documentação

- Mantenha o README atualizado
- Adicione exemplos de uso
- Documente APIs e configurações
- Use screenshots quando apropriado

### 7. Pull Request

#### Preparando o PR

```bash
# Certifique-se que está na branch correta
git status

# Execute testes
pytest

# Execute linting
flake8 .
black --check .
isort --check-only .

# Push da branch
git push origin feature/minha-funcionalidade
```

#### Template de Pull Request

```markdown
## Descrição
Breve descrição do que este PR faz.

## Tipo de Mudança
- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação (mudança apenas na documentação)

## Como Testar
Descreva como testar as mudanças:
1. Execute `./run.sh`
2. Navegue para '...'
3. Clique em '...'
4. Verifique que '...'

## Checklist
- [ ] Meu código segue as diretrizes de estilo do projeto
- [ ] Realizei uma auto-revisão do meu código
- [ ] Comentei meu código em partes difíceis de entender
- [ ] Fiz mudanças correspondentes na documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Adicionei testes que provam que minha correção funciona
- [ ] Testes novos e existentes passam localmente

## Screenshots (se aplicável)
Adicione screenshots para mudanças visuais.

## Issues Relacionadas
Fixes #123
```

### 8. Code Review

#### Para Revisores

- ✅ **Seja Construtivo**: Feedback deve ajudar a melhorar
- ✅ **Seja Específico**: Aponte problemas exatos e sugira soluções
- ✅ **Teste Localmente**: Se possível, teste as mudanças
- ✅ **Verifique Docs**: Documentação foi atualizada?

#### Para Autores

- ✅ **Responda Rapidamente**: Endereçe feedback em tempo hábil
- ✅ **Seja Receptivo**: Use feedback para aprender
- ✅ **Teste Suas Mudanças**: Certifique-se que tudo funciona
- ✅ **Mantenha PRs Pequenos**: Facilita revisão

## 🎨 UI/UX Guidelines

### Princípios de Design

1. **Simplicidade**: Interface limpa e intuitiva
2. **Consistência**: Padrões visuais uniformes
3. **Acessibilidade**: Funciona para todos os usuários
4. **Performance**: Carregamento rápido e responsivo

### Padrões Visuais

```python
# Cores padrão
PRIMARY_COLOR = "#4CAF50"
SECONDARY_COLOR = "#66BB6A"
ERROR_COLOR = "#F44336"
WARNING_COLOR = "#FF9800"
SUCCESS_COLOR = "#4CAF50"

# Uso em Streamlit
st.success("✅ Operação realizada com sucesso!")
st.error("❌ Erro ao executar operação")
st.warning("⚠️ Atenção necessária")
st.info("ℹ️ Informação importante")
```

### Componentes Reutilizáveis

```python
def custom_metric(titulo: str, valor: str, subtexto: str = None, cor: str = "#2196F3"):
    """Componente de métrica personalizada."""
    st.markdown(f"""
        <div style="background-color: #FFFFFF; border-radius: 5px; 
                    padding: 15px; margin-bottom: 10px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
            <h3 style="color: {cor}; margin: 0; font-size: 36px; 
                       font-weight: bold;">{valor}</h3>
            <p style="color: #666; margin: 0; font-size: 14px; 
                      margin-top: 5px;">{titulo}</p>
            {"" if subtexto is None else f'<p style="color: #888; margin: 0; font-size: 12px;">{subtexto}</p>'}
        </div>
    """, unsafe_allow_html=True)
```

## 🔒 Segurança

### Diretrizes de Segurança

1. **Nunca commite credenciais**: Use .env para configurações sensíveis
2. **Valide entradas**: Sempre valide dados de usuário
3. **Sanitize outputs**: Previna XSS em conteúdo dinâmico
4. **Use HTTPS**: Em produção, sempre force HTTPS

### Exemplo de Validação

```python
def validate_pet_data(data: dict) -> tuple[bool, str]:
    """Valida dados de entrada de pet."""
    if not data.get('nome') or len(data['nome'].strip()) == 0:
        return False, "Nome é obrigatório"
    
    if data.get('idade', 0) < 0 or data.get('idade', 0) > 30:
        return False, "Idade deve estar entre 0 e 30 anos"
    
    allowed_types = ['Cachorro', 'Gato', 'Ave', 'Roedor', 'Réptil']
    if data.get('tipo_pet') not in allowed_types:
        return False, f"Tipo deve ser um de: {', '.join(allowed_types)}"
    
    return True, ""
```

## 🆘 Suporte

### Onde Obter Ajuda

- **📖 Documentação**: Verifique docs/ primeiro
- **💬 Discussions**: Para perguntas gerais
- **🐛 Issues**: Para bugs específicos
- **📧 Email**: contato@petcareai.com

### FAQ

**P: Como configurar o ambiente de desenvolvimento?**
R: Execute `./install.sh` seguido de `./configure.sh`

**P: Posso contribuir sem conhecimento em ML?**
R: Sim! Há muitas áreas como UI, documentação, testes, etc.

**P: Como reportar vulnerabilidades de segurança?**
R: Envie email para security@petcareai.com (não abra issue pública)

## 🙏 Reconhecimento

Contribuições são reconhecidas em:

- 📋 **CONTRIBUTORS.md**: Lista de todos os contribuidores
- 🏆 **Release Notes**: Destaques em releases
- 🌟 **GitHub**: Stars e badges de contribuidor

### Tipos de Contribuidores

- 🐛 **Bug Hunters**: Reportam e corrigem bugs
- 💡 **Feature Creators**: Implementam novas funcionalidades
- 📝 **Documentarians**: Melhoram documentação
- 🎨 **Designers**: Aprimoram UI/UX
- 🧪 **Testers**: Escrevem e mantêm testes
- 🌍 **Translators**: Ajudam com internacionalização

---

**Obrigado por contribuir com o PetCareAI Analytics! Juntos, estamos criando uma ferramenta que realmente faz a diferença na vida dos pets e famílias. 🐾❤️**
