# Scripts de Release - PetCareAi

Este diretório contém scripts automatizados para gerenciar releases, deployment e versionamento do projeto.

## 📋 Scripts Disponíveis

### 🏷️ Versionamento
- `bump_version.py` - Incrementar versão do projeto
- `create_tag.sh` - Criar tags Git com anotações
- `validate_version.py` - Validar formato de versão

### 📦 Build e Empacotamento
- `build_package.py` - Construir pacote Python
- `build_docker.sh` - Construir imagens Docker
- `prepare_artifacts.py` - Preparar artefatos de release

### 🚀 Deploy
- `deploy_staging.sh` - Deploy para ambiente de staging
- `deploy_production.sh` - Deploy para produção
- `rollback.sh` - Rollback de deployment

### 📝 Documentação
- `generate_changelog.py` - Gerar changelog automático
- `update_docs.py` - Atualizar documentação
- `generate_release_notes.py` - Criar notas de release

### 🧪 Validação
- `pre_release_checks.py` - Verificações antes do release
- `post_release_validation.py` - Validações após deployment
- `smoke_tests.py` - Testes de fumaça

## 🚀 Como Usar

### Release Completo
```bash
# Executar release completo
./release-scripts/full_release.sh v2.1.0
```

### Incrementar Versão
```bash
# Patch (2.0.0 -> 2.0.1)
python release-scripts/bump_version.py patch

# Minor (2.0.0 -> 2.1.0)
python release-scripts/bump_version.py minor

# Major (2.0.0 -> 3.0.0)
python release-scripts/bump_version.py major
```

### Deploy Manual
```bash
# Staging
./release-scripts/deploy_staging.sh

# Produção (requer confirmação)
./release-scripts/deploy_production.sh
```

## 📁 Estrutura dos Scripts

```
release-scripts/
├── README.md
├── config/
│   ├── release_config.yaml
│   ├── staging_config.yaml
│   └── production_config.yaml
├── templates/
│   ├── changelog_template.md
│   ├── release_notes_template.md
│   └── deployment_template.yaml
├── utils/
│   ├── __init__.py
│   ├── git_utils.py
│   ├── docker_utils.py
│   ├── notification_utils.py
│   └── validation_utils.py
└── hooks/
    ├── pre_release.py
    ├── post_release.py
    └── rollback_hooks.py
```

## ⚙️ Configuração

### Arquivo de Configuração Principal
`config/release_config.yaml`:
```yaml
project:
  name: "petcare-ai"
  repository: "github.com/petcare-ai/petcare-ai"
  main_branch: "main"
  develop_branch: "develop"

versioning:
  scheme: "semantic"  # semantic, calver, custom
  prefix: "v"
  
environments:
  staging:
    url: "https://staging.petcare.ai"
    branch: "develop"
  production:
    url: "https://petcare.ai"
    branch: "main"

notifications:
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channels: ["#releases", "#dev-team"]
  email:
    recipients: ["team@petcare.ai"]
    
docker:
  registry: "ghcr.io"
  namespace: "petcare-ai"
  images: ["app", "worker", "scheduler"]
```

### Variáveis de Ambiente
```bash
# Configurar variáveis necessárias
export GITHUB_TOKEN="seu_token_github"
export DOCKER_USERNAME="seu_usuario_docker"
export DOCKER_PASSWORD="sua_senha_docker"
export SLACK_WEBHOOK_URL="url_do_webhook_slack"
export SUPABASE_URL="url_do_supabase"
export SUPABASE_KEY="chave_do_supabase"
```

## 🔧 Scripts Detalhados

### bump_version.py
Incrementa a versão do projeto seguindo versionamento semântico.

```python
# Uso
python bump_version.py [patch|minor|major] [--dry-run] [--tag]

# Exemplos
python bump_version.py patch          # 2.0.0 -> 2.0.1
python bump_version.py minor --tag    # 2.0.0 -> 2.1.0 + criar tag
python bump_version.py major --dry-run # Simular major bump
```

### generate_changelog.py
Gera changelog baseado em commits e PRs.

```python
# Uso
python generate_changelog.py [--from=v2.0.0] [--to=HEAD] [--output=CHANGELOG.md]

# Gerar changelog desde última tag
python generate_changelog.py

# Gerar para range específico
python generate_changelog.py --from=v2.0.0 --to=v2.1.0
```

### deploy_staging.sh
Deploy automatizado para ambiente de staging.

```bash
#!/bin/bash
# Principais etapas:
# 1. Validar branch
# 2. Executar testes
# 3. Build da aplicação
# 4. Deploy para staging
# 5. Smoke tests
# 6. Notificações
```

### deploy_production.sh
Deploy para produção com verificações extras.

```bash
#!/bin/bash
# Principais etapas:
# 1. Verificar se é tag de release
# 2. Confirmação manual
# 3. Backup da versão atual
# 4. Deploy blue-green
# 5. Testes de produção
# 6. Switch de tráfego
# 7. Cleanup
```

## 🧪 Validações e Testes

### pre_release_checks.py
Executa verificações antes do release:

- ✅ Todos os testes passando
- ✅ Cobertura de testes adequada
- ✅ Linting sem erros
- ✅ Documentação atualizada
- ✅ Changelog preparado
- ✅ Dependências de segurança
- ✅ Performance dentro dos limites

### smoke_tests.py
Testes básicos após deployment:

- ✅ Aplicação inicializa
- ✅ Endpoints principais respondem
- ✅ Autenticação funciona
- ✅ Dashboard carrega
- ✅ Operações CRUD básicas

### post_release_validation.py
Validações completas pós-deployment:

- ✅ Métricas de performance
- ✅ Logs de erro
- ✅ Integrações externas
- ✅ Monitoramento ativo

## 📊 Monitoramento de Release

### Métricas Coletadas
- Tempo total de deployment
- Taxa de sucesso/falha
- Tempo de rollback (se necessário)
- Impacto na performance
- Feedback de usuários

### Dashboards
- Release Pipeline Status
- Deployment Frequency
- Lead Time for Changes
- Mean Time to Recovery

## 🔄 Workflow de Release

### 1. Preparação
```bash
# Atualizar develop com main
git checkout develop
git pull origin main

# Criar branch de release
git checkout -b release/v2.1.0
```

### 2. Desenvolvimento
```bash
# Implementar features
# Fazer commits seguindo conventional commits
# Abrir PRs para develop
```

### 3. Release Candidate
```bash
# Incrementar versão
python release-scripts/bump_version.py minor

# Gerar changelog
python release-scripts/generate_changelog.py

# Commit de release
git add .
git commit -m "chore(release): v2.1.0"
```

### 4. Testes e Validação
```bash
# Executar verificações
python release-scripts/pre_release_checks.py

# Deploy para staging
./release-scripts/deploy_staging.sh

# Testes manuais e automáticos
```

### 5. Produção
```bash
# Merge para main
git checkout main
git merge release/v2.1.0

# Criar tag
git tag -a v2.1.0 -m "Release v2.1.0"

# Deploy para produção
./release-scripts/deploy_production.sh
```

### 6. Pós-Release
```bash
# Validar deployment
python release-scripts/post_release_validation.py

# Notificar equipe
python release-scripts/send_notifications.py

# Cleanup
git branch -d release/v2.1.0
```

## 🚨 Rollback

### Rollback Automático
```bash
# Rollback para versão anterior
./release-scripts/rollback.sh --version=v2.0.9

# Rollback com motivo
./release-scripts/rollback.sh --reason="Critical bug found"
```

### Rollback Manual
1. Identificar versão estável anterior
2. Executar script de rollback
3. Validar funcionamento
4. Notificar stakeholders
5. Investigar causa do problema

## 📧 Notificações

### Canais de Notificação
- **Slack**: #releases, #dev-team
- **Email**: Stakeholders e equipe técnica
- **GitHub**: Release notes automáticas
- **Status Page**: Atualizações de status

### Templates de Notificação
- Release iniciado
- Deploy em staging concluído
- Deploy em produção iniciado
- Release concluído com sucesso
- Rollback executado
- Problemas identificados

## 🔐 Segurança

### Controle de Acesso
- Apenas tech leads podem fazer deploy para produção
- Require 2FA para operações críticas
- Logs de auditoria para todos os deployments
- Aprovação manual para releases major

### Proteções
- Branch protection em main
- Required status checks
- Signed commits obrigatórios
- Vulnerability scanning

## 📚 Documentação de Referência

### Versionamento Semântico
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Funcionalidades compatíveis
- **PATCH**: Correções compatíveis

### Conventional Commits
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `chore:` Manutenção

## 🤝 Contribuindo

### Adicionando Novos Scripts
1. Seguir estrutura padrão
2. Incluir documentação
3. Adicionar testes
4. Atualizar este README
5. Testar em staging primeiro

### Melhorias Sugeridas
- Integração com ferramentas de APM
- Deploy automático baseado em métricas
- Rollback inteligente
- A/B testing automático

---

Para dúvidas sobre os scripts de release, consulte a equipe de DevOps ou abra uma issue no GitHub.
