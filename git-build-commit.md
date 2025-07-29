# Guia de Build e Commit - PetCare Analytics

## Configuração Inicial do Git

### 1. Configuração do Usuário
```bash
# Configurar nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"

# Configurar editor padrão
git config --global core.editor "code --wait"  # VS Code
# ou
git config --global core.editor "nano"  # Nano

# Configurar merge tool
git config --global merge.tool vimdiff
```

### 2. Configurações Recomendadas
```bash
# Melhorar output dos comandos
git config --global color.ui auto
git config --global color.branch auto
git config --global color.diff auto
git config --global color.status auto

# Configurar push padrão
git config --global push.default simple

# Configurar linha de comando mais limpa
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

## Estrutura de Branches

### Branch Principal
- `main` - Branch de produção, sempre estável

### Branches de Desenvolvimento
- `develop` - Branch de desenvolvimento principal
- `feature/nome-da-funcionalidade` - Branches para novas funcionalidades
- `bugfix/nome-do-bug` - Branches para correções de bugs
- `hotfix/nome-do-hotfix` - Branches para correções urgentes em produção
- `release/vX.X.X` - Branches para preparação de releases

### Exemplos de Nomes de Branch
```bash
# Funcionalidades
feature/dashboard-analytics
feature/export-relatorios
feature/login-social

# Correções
bugfix/erro-calculo-score
bugfix/problema-upload-imagem

# Hotfixes
hotfix/falha-seguranca-login
hotfix/erro-critico-database

# Releases
release/v1.2.0
release/v2.0.0-beta
```

## Padrão de Commits (Conventional Commits)

### Formato
```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação, ponto e vírgula, etc (sem mudança de código)
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Alterações em ferramentas, configurações, dependências
- `perf`: Melhoria de performance
- `ci`: Alterações em CI/CD
- `build`: Alterações no sistema de build
- `revert`: Reversão de commit anterior

### Exemplos de Commits
```bash
# Novas funcionalidades
feat(dashboard): adicionar gráfico de taxa de adoção
feat(pets): implementar cadastro com validação de IA
feat(auth): adicionar login com Google OAuth

# Correções
fix(database): corrigir conexão com Supabase em produção
fix(export): resolver erro ao gerar relatório Excel
fix(ui): corrigir responsividade do menu lateral

# Documentação
docs(readme): atualizar instruções de instalação
docs(api): adicionar documentação dos endpoints
docs(deploy): criar guia de deploy para produção

# Refatoração
refactor(analytics): otimizar algoritmos de machine learning
refactor(components): simplificar estrutura de componentes
refactor(database): normalizar esquema de tabelas

# Testes
test(auth): adicionar testes para sistema de login
test(pets): implementar testes unitários para CRUD
test(integration): adicionar testes de integração com API

# Configurações
chore(deps): atualizar dependências do projeto
chore(docker): otimizar Dockerfile para produção
chore(lint): configurar ESLint e formatação

# Performance
perf(queries): otimizar consultas de banco de dados
perf(images): implementar lazy loading para imagens
perf(cache): adicionar cache Redis para sessões

# CI/CD
ci(github): configurar workflow de deploy automático
ci(tests): adicionar execução de testes no pipeline
ci(security): implementar verificação de vulnerabilidades
```

## Workflow de Desenvolvimento

### 1. Iniciar Nova Funcionalidade
```bash
# Atualizar branch principal
git checkout main
git pull origin main

# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Desenvolver e fazer commits
git add .
git commit -m "feat(scope): descrição da alteração"

# Push da branch
git push -u origin feature/nova-funcionalidade
```

### 2. Processo de Code Review
```bash
# Após desenvolvimento completo
git push origin feature/nova-funcionalidade

# Criar Pull Request no GitHub
# - Descrever mudanças
# - Adicionar screenshots se necessário
# - Marcar reviewers
# - Linkar issues relacionadas
```

### 3. Merge e Limpeza
```bash
# Após aprovação do PR
git checkout main
git pull origin main

# Deletar branch local
git branch -d feature/nova-funcionalidade

# Deletar branch remota
git push origin --delete feature/nova-funcionalidade
```

## Scripts de Build

### 1. Verificação Pre-commit
```bash
#!/bin/bash
# scripts/pre-commit.sh

echo "🔍 Executando verificações pre-commit..."

# Verificar formatação Python
echo "📝 Verificando formatação Python..."
black --check . || exit 1

# Verificar imports
echo "📦 Verificando imports..."
isort --check-only . || exit 1

# Executar linting
echo "🔍 Executando linting..."
flake8 . || exit 1

# Verificar tipos (se usar mypy)
echo "🏷️  Verificando tipos..."
# mypy . || exit 1

echo "✅ Todas as verificações passaram!"
```

### 2. Script de Build Completo
```bash
#!/bin/bash
# scripts/build.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando build do PetCare Analytics..."

# Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Verificar Python
echo "🐍 Verificando versão do Python..."
python --version

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Executar testes
echo "🧪 Executando testes..."
python -m pytest tests/ -v || echo "⚠️ Alguns testes falharam"

# Verificar sintaxe
echo "🔍 Verificando sintaxe..."
python -m py_compile app.py
python -m py_compile config/database.py

# Verificar variáveis de ambiente
echo "🔐 Verificando configurações..."
if [ ! -f ".env" ]; then
    echo "⚠️ Arquivo .env não encontrado, copiando exemplo..."
    cp .env.example .env
fi

echo "✅ Build concluído com sucesso!"
echo "🌐 Execute: streamlit run app.py"
```

### 3. Script de Deploy
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Iniciando deploy do PetCare Analytics..."

# Verificar branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Deploy deve ser feito a partir da branch main"
    exit 1
fi

# Verificar se está tudo commitado
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Existem alterações não commitadas"
    exit 1
fi

# Atualizar repositório
echo "📡 Atualizando repositório..."
git pull origin main

# Executar build
echo "🔨 Executando build..."
bash scripts/build.sh

# Backup do banco (se necessário)
echo "💾 Criando backup..."
# Implementar backup do Supabase se necessário

# Deploy específico da plataforma
if [ "$1" = "heroku" ]; then
    echo "🚀 Deploy para Heroku..."
    git push heroku main
elif [ "$1" = "railway" ]; then
    echo "🚂 Deploy para Railway..."
    # Comandos específicos do Railway
elif [ "$1" = "docker" ]; then
    echo "🐳 Build e push Docker..."
    docker build -t petcare-analytics .
    docker tag petcare-analytics your-registry/petcare-analytics:latest
    docker push your-registry/petcare-analytics:latest
fi

echo "✅ Deploy concluído!"
```

## Tags e Releases

### Versionamento Semântico
- `MAJOR.MINOR.PATCH` (ex: 1.2.3)
- `MAJOR`: Mudanças incompatíveis na API
- `MINOR`: Funcionalidades compatíveis
- `PATCH`: Correções de bugs

### Criar Release
```bash
# Criar tag
git tag -a v1.2.0 -m "Release v1.2.0 - Novos dashboards e ML"

# Push da tag
git push origin v1.2.0

# Criar release no GitHub
# - Ir para GitHub > Releases > Create Release
# - Selecionar tag v1.2.0
# - Adicionar changelog
# - Anexar binários se necessário
```

## Changelog

### Formato
```markdown
# Changelog

## [1.2.0] - 2025-01-15

### Adicionado
- Dashboard de analytics avançado
- Algoritmos de machine learning para predição
- Exportação de relatórios em múltiplos formatos
- Sistema de notificações inteligentes

### Alterado
- Interface do usuário mais responsiva
- Performance melhorada nas consultas
- Validação aprimorada nos formulários

### Corrigido
- Erro na conexão com Supabase
- Problema na geração de PDFs
- Bug no cálculo do score de adoção

### Removido
- Dependências desnecessárias
- Código legado comentado

## [1.1.0] - 2024-12-20

### Adicionado
- Sistema de backup automático
- Mapa interativo de pets
- Análise de séries temporais

### Corrigido
- Vazamento de memória em consultas grandes
- Problema de encoding em exports CSV

## [1.0.0] - 2024-11-01

### Adicionado
- Release inicial do sistema
- CRUD completo de pets
- Dashboard básico
- Sistema de autenticação
```

## Hooks do Git

### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Executar verificações antes do commit
bash scripts/pre-commit.sh

# Se o script falhar, abortar commit
if [ $? -ne 0 ]; then
    echo "❌ Pre-commit hooks falharam. Commit abortado."
    exit 1
fi

echo "✅ Pre-commit hooks passaram!"
```

### Commit-msg Hook
```bash
#!/bin/sh
# .git/hooks/commit-msg

# Verificar formato do commit
commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Formato de commit inválido!"
    echo "Use: <tipo>(<escopo>): <descrição>"
    echo "Exemplo: feat(auth): adicionar login com Google"
    exit 1
fi

echo "✅ Formato de commit válido!"
```

## Automatização com GitHub Actions

### Exemplo de Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Check code style
      run: |
        black --check .
        flake8 .

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Comandos de deploy
        echo "Deploy para produção"
```

## Comandos Úteis

### Git Básico
```bash
# Status e informações
git status
git log --oneline -10
git diff
git show HEAD

# Branches
git branch -a
git checkout -b nova-branch
git branch -d branch-local
git push origin --delete branch-remota

# Merge e Rebase
git merge feature-branch
git rebase main
git cherry-pick <commit-hash>

# Desfazer alterações
git reset --soft HEAD~1  # Desfaz último commit mantendo alterações
git reset --hard HEAD~1  # Desfaz último commit perdendo alterações
git revert <commit-hash>  # Cria commit que desfaz outro commit
```

### Limpeza e Manutenção
```bash
# Limpar branches locais órfãs
git remote prune origin
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -D

# Compactar repositório
git gc --prune=now

# Verificar integridade
git fsck

# Ver tamanho do repositório
git count-objects -vH
```

## Resolução de Problemas

### Conflitos de Merge
```bash
# Quando há conflitos
git status  # Ver arquivos em conflito

# Editar arquivos manualmente removendo marcadores
# <<<<<<< HEAD
# ======= 
# >>>>>>> branch-name

# Marcar como resolvido
git add arquivo-resolvido.py

# Finalizar merge
git commit
```

### Recuperar Commits Perdidos
```bash
# Ver histórico de referências
git reflog

# Recuperar commit específico
git cherry-pick <commit-hash>

# Criar branch a partir de commit perdido
git checkout -b recuperar-branch <commit-hash>
```

### Problemas com Push
```bash
# Forçar push (cuidado!)
git push --force-with-lease origin branch-name

# Push de tags
git push origin --tags

# Push de branch nova
git push -u origin nova-branch
```
