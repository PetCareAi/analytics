# Git Build & Commit Guidelines

## 🔄 Workflow de Desenvolvimento

### Estrutura de Branches

```
main (production)
├── develop (development)
│   ├── feature/nova-funcionalidade
│   ├── feature/ai-improvements
│   └── feature/dashboard-upgrade
├── hotfix/critical-bug-fix
└── release/v2.1.0
```

### Padrão de Branches

| Branch Type | Formato | Propósito |
|------------|---------|-----------|
| `main` | `main` | Código em produção |
| `develop` | `develop` | Branch principal de desenvolvimento |
| `feature` | `feature/nome-da-funcionalidade` | Novas funcionalidades |
| `bugfix` | `bugfix/descricao-do-bug` | Correções de bugs |
| `hotfix` | `hotfix/nome-do-fix` | Correções críticas para produção |
| `release` | `release/v2.1.0` | Preparação para release |

## 📝 Padrão de Commits

### Formato de Commit Message

```
<tipo>(<escopo>): <descrição>

<corpo da mensagem (opcional)>

<rodapé (opcional)>
```

### Tipos de Commit

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(dashboard): adicionar gráficos de ML` |
| `fix` | Correção de bug | `fix(auth): corrigir problema de login` |
| `docs` | Documentação | `docs(api): atualizar documentação` |
| `style` | Formatação/estilo | `style(ui): ajustar cores do tema` |
| `refactor` | Refatoração de código | `refactor(database): otimizar queries` |
| `test` | Testes | `test(unit): adicionar testes para ML` |
| `chore` | Tarefas de manutenção | `chore(deps): atualizar dependências` |
| `perf` | Melhorias de performance | `perf(charts): otimizar renderização` |
| `ci` | CI/CD | `ci(github): adicionar workflow` |
| `build` | Sistema de build | `build(docker): atualizar Dockerfile` |

### Escopos Comuns

- `auth` - Sistema de autenticação
- `dashboard` - Dashboard principal
- `ml` - Machine Learning
- `database` - Banco de dados
- `ui` - Interface do usuário
- `api` - API e endpoints
- `config` - Configurações
- `docs` - Documentação
- `tests` - Testes
- `deploy` - Deploy e DevOps

### Exemplos de Commit Messages

#### ✅ Boas Práticas

```bash
# Commit simples
feat(ml): implementar clustering comportamental

# Commit com corpo
feat(dashboard): adicionar visualização de mapas

Implementa visualização geográfica dos pets usando Plotly.
Inclui filtros por região e densidade populacional.

# Commit com breaking change
feat(auth)!: migrar para novo sistema de autenticação

BREAKING CHANGE: Remove suporte ao login com SQLite.
Agora requer configuração do Supabase.

# Bug fix
fix(export): corrigir encoding de caracteres especiais

Resolve problema com acentos em relatórios CSV.
Closes #123

# Chore
chore(deps): atualizar Streamlit para v1.31.1

# Documentação
docs(readme): adicionar guia de instalação
```

#### ❌ Práticas a Evitar

```bash
# Muito vago
fix: correção

# Muito longo no título
feat(dashboard): implementar novo dashboard com gráficos interativos, mapas geográficos e análises de ML

# Sem tipo
adicionar nova funcionalidade

# Caps Lock desnecessário
FEAT(ML): ADICIONAR CLUSTERING

# Português misturado com inglês inconsistente
feat(dashboard): adicionar new charts
```

## 🏗️ Build Process

### Pre-commit Hooks

Instalar pre-commit hooks:

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install
```

Configuração em `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile, black]
```

### Comandos de Build

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes
python -m pytest tests/

# Verificar qualidade do código
flake8 .
black --check .
isort --check-only .

# Executar aplicação
streamlit run app.py

# Build para produção
docker build -t petcare-analytics .
```

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest flake8 black isort
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88
    
    - name: Format check with black
      run: black --check .
    
    - name: Import sort check with isort
      run: isort --check-only .
    
    - name: Test with pytest
      run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Streamlit Cloud
      run: |
        echo "Deploy para produção"
        # Comandos de deploy específicos
```

## 🔀 Workflow de Desenvolvimento

### 1. Criando uma Nova Feature

```bash
# Atualizar develop
git checkout develop
git pull origin develop

# Criar branch de feature
git checkout -b feature/nova-funcionalidade

# Fazer alterações e commits
git add .
git commit -m "feat(dashboard): adicionar nova visualização"

# Push da branch
git push origin feature/nova-funcionalidade

# Criar Pull Request no GitHub
```

### 2. Code Review Process

#### Checklist para Pull Requests

- [ ] **Código**
  - [ ] Código segue padrões do projeto
  - [ ] Testes adicionados/atualizados
  - [ ] Documentação atualizada
  - [ ] Sem código comentado desnecessário

- [ ] **Funcionalidade**
  - [ ] Feature funciona conforme especificado
  - [ ] Não quebra funcionalidades existentes
  - [ ] Performance adequada
  - [ ] UI/UX consistente

- [ ] **Segurança**
  - [ ] Não expõe dados sensíveis
  - [ ] Validação de entrada adequada
  - [ ] Tratamento de erros robusto

- [ ] **CI/CD**
  - [ ] Pipeline de CI passa
  - [ ] Testes unitários passam
  - [ ] Linting sem erros

### 3. Merge Strategy

```bash
# Squash commits para features pequenas
git checkout develop
git merge --squash feature/nova-funcionalidade
git commit -m "feat(dashboard): adicionar nova visualização"

# Merge normal para features grandes
git checkout develop
git merge --no-ff feature/nova-funcionalidade
```

### 4. Release Process

```bash
# Criar branch de release
git checkout develop
git checkout -b release/v2.1.0

# Atualizar versão nos arquivos
# - app.py
# - requirements.txt
# - CHANGELOG.md

# Commit das alterações
git commit -m "chore(release): preparar v2.1.0"

# Merge para main
git checkout main
git merge --no-ff release/v2.1.0

# Criar tag
git tag -a v2.1.0 -m "Release v2.1.0"

# Push
git push origin main
git push origin v2.1.0

# Merge de volta para develop
git checkout develop
git merge main
```

## 🏷️ Versionamento Semântico

### Formato: MAJOR.MINOR.PATCH

- **MAJOR**: Mudanças que quebram compatibilidade
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

### Exemplos de Versionamento

```bash
# Correção de bug: 2.0.0 → 2.0.1
fix(auth): corrigir validação de senha

# Nova funcionalidade: 2.0.1 → 2.1.0
feat(ml): adicionar algoritmo de predição

# Breaking change: 2.1.0 → 3.0.0
feat(database)!: migrar para PostgreSQL

BREAKING CHANGE: Remove suporte ao SQLite
```

## 🔍 Quality Assurance

### Code Standards

#### Python (PEP 8)
```python
# ✅ Bom
def calculate_adoption_score(idade, sociabilidade, energia):
    """Calcula score de adoção baseado em características."""
    if idade < 1:
        score = 1.0
    elif idade <= 3:
        score = 0.8
    else:
        score = 0.6
    
    return min(5.0, score + (sociabilidade + energia) / 10)

# ❌ Ruim
def calc_score(i,s,e):
    if i<1:score=1.0
    elif i<=3:score=0.8
    else:score=0.6
    return min(5.0,score+(s+e)/10)
```

#### Docstrings
```python
def advanced_clustering(self, n_clusters=5):
    """
    Executa clustering avançado nos dados dos pets.
    
    Args:
        n_clusters (int): Número de clusters desejado
        
    Returns:
        tuple: (resultados_clustering, dados_pca, erro)
        
    Raises:
        ValueError: Se n_clusters < 2
        
    Example:
        >>> analyzer = PetMLAnalyzer(df)
        >>> results, pca, error = analyzer.advanced_clustering(4)
    """
```

### Testing Strategy

#### Estrutura de Testes
```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_ml.py
│   └── test_database.py
├── integration/
│   ├── test_api.py
│   └── test_workflows.py
├── e2e/
│   └── test_user_journey.py
└── conftest.py
```

#### Exemplo de Teste Unitário
```python
import pytest
from app import calculate_adoption_score

class TestAdoptionScore:
    def test_young_pet_high_score(self):
        """Pets jovens devem ter score alto."""
        score = calculate_adoption_score(0.5, 5, 5)
        assert score >= 4.0
        
    def test_old_pet_lower_score(self):
        """Pets idosos devem ter score menor."""
        score = calculate_adoption_score(12, 3, 2)
        assert score < 3.0
        
    def test_score_bounds(self):
        """Score deve estar entre 0 e 5."""
        score = calculate_adoption_score(1, 5, 5)
        assert 0 <= score <= 5
```

## 📦 Deployment

### Staging Deployment

```bash
# Branch: develop → Staging
git checkout develop
git pull origin develop

# Deploy automático via GitHub Actions
# ou manual:
./deploy-staging.sh
```

### Production Deployment

```bash
# Branch: main → Production
git checkout main
git pull origin main

# Verificações finais
./health-check.sh
./run-tests.sh

# Deploy
./deploy-production.sh
```

### Rollback Strategy

```bash
# Rollback rápido para versão anterior
git checkout main
git reset --hard v2.0.5
git push --force-with-lease origin main

# Ou via tag específica
git checkout v2.0.5
git checkout -b hotfix/rollback-v2.0.5
# Fazer correções necessárias
git tag v2.0.6
```

## 🚨 Hotfix Process

### Processo de Hotfix Crítico

```bash
# 1. Criar branch de hotfix a partir da main
git checkout main
git checkout -b hotfix/critical-security-fix

# 2. Fazer correção
git add .
git commit -m "fix(security): corrigir vulnerabilidade XSS"

# 3. Merge para main
git checkout main
git merge --no-ff hotfix/critical-security-fix

# 4. Tag de release
git tag -a v2.0.6 -m "Hotfix v2.0.6: Security fix"

# 5. Deploy imediato
./deploy-production.sh

# 6. Merge para develop
git checkout develop
git merge main

# 7. Limpeza
git branch -d hotfix/critical-security-fix
```

## 📊 Metrics & Monitoring

### Git Metrics

```bash
# Commits por autor
git shortlog -sn

# Atividade por período
git log --since="1 month ago" --oneline

# Estatísticas de arquivos
git log --stat

# Complexidade de branches
git show-branch --all
```

### Code Quality Metrics

```bash
# Cobertura de testes
pytest --cov=app tests/

# Complexidade ciclomática
radon cc app.py

# Duplicação de código
radon raw app.py

# Métricas de manutenibilidade
radon mi app.py
```

## 🔧 Tools & Automation

### Git Aliases Úteis

```bash
# Adicionar ao ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    
    # Logs formatados
    lg = log --oneline --graph --decorate --all
    lgs = log --oneline --graph --decorate --all --stat
    
    # Comandos de commit padronizados
    feat = "!f() { git commit -m \"feat($1): $2\"; }; f"
    fix = "!f() { git commit -m \"fix($1): $2\"; }; f"
    docs = "!f() { git commit -m \"docs($1): $2\"; }; f"
```

### Scripts de Automação

#### pre-push hook
```bash
#!/bin/sh
# .git/hooks/pre-push

echo "Executando verificações antes do push..."

# Executar testes
echo "Executando testes..."
if ! python -m pytest tests/; then
    echo "❌ Testes falharam. Push cancelado."
    exit 1
fi

# Verificar linting
echo "Verificando código..."
if ! flake8 .; then
    echo "❌ Problemas de linting encontrados. Push cancelado."
    exit 1
fi

echo "✅ Verificações passaram. Prosseguindo com push."
```

#### Commit Message Validation
```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Commit message inválido!"
    echo "Formato: tipo(escopo): descrição"
    echo "Exemplo: feat(auth): adicionar login com Google"
    exit 1
fi
```

## 📚 Resources

### Git Best Practices
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)

### Tools
- [Commitizen](https://commitizen-tools.github.io/commitizen/) - Ferramenta para commits padronizados
- [Pre-commit](https://pre-commit.com/) - Git hooks automatizados
- [GitKraken](https://www.gitkraken.com/) - Cliente Git visual
- [Sourcetree](https://www.sourcetreeapp.com/) - Cliente Git gratuito

### Code Quality
- [Black](https://black.readthedocs.io/) - Formatador Python
- [Flake8](https://flake8.pycqa.org/) - Linter Python
- [isort](https://pycqa.github.io/isort/) - Organizar imports
- [Pytest](https://pytest.org/) - Framework de testes

---

*Este documento é atualizado regularmente. Para sugestões ou dúvidas sobre o processo de desenvolvimento, abra uma issue no GitHub.*
