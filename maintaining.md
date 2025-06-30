# Guia de Manutenção - PetCareAI Analytics

Este documento fornece diretrizes para mantenedores do projeto PetCareAI Analytics sobre como gerenciar e manter o projeto de forma efetiva.

## 👥 Equipe de Manutenção

### Roles e Responsabilidades

#### 🏆 Project Lead
- **Responsabilidades**:
  - Visão geral e direção do projeto
  - Decisões arquiteturais principais
  - Aprovação de releases
  - Gerenciamento da roadmap
- **Acesso**: Admin total no repositório
- **Contato**: lead@petcareai.com

#### 🔧 Core Maintainers
- **Responsabilidades**:
  - Review de código crítico
  - Gerenciamento de releases
  - Mentoria de contribuidores
  - Manutenção de infraestrutura
- **Acesso**: Write no repositório
- **Mínimo**: 2 pessoas ativas

#### 🤝 Community Maintainers
- **Responsabilidades**:
  - Triagem de issues
  - Review de PRs menores
  - Suporte à comunidade
  - Documentação
- **Acesso**: Triage no repositório

### Processo de Onboarding

#### Para Novos Mantenedores
1. **Nomeação**: Por core maintainer existente
2. **Período de Observação**: 3 meses como colaborador ativo
3. **Votação**: Aprovação por maioria dos core maintainers
4. **Onboarding**: Acesso gradual e mentoria

#### Checklist de Onboarding
- [ ] Acesso ao repositório configurado
- [ ] Adicionado aos canais de comunicação
- [ ] Documentação de processos revisada
- [ ] Ferramentas e acessos configurados
- [ ] Primeira review pair programming
- [ ] Introdução à comunidade

## 📋 Responsabilidades Diárias

### Triagem de Issues
```bash
# Processo de triagem (diário)
1. Revisar novas issues (label: needs-triage)
2. Classificar por tipo: bug, feature, docs, etc.
3. Definir prioridade: critical, high, medium, low
4. Atribuir labels apropriados
5. Responder ou atribuir a alguém
```

#### Labels do Sistema
- **Tipo**: `bug`, `feature`, `docs`, `enhancement`
- **Prioridade**: `critical`, `high`, `medium`, `low`
- **Status**: `needs-triage`, `in-progress`, `blocked`, `ready`
- **Área**: `ml`, `ui`, `backend`, `database`, `security`
- **Dificuldade**: `good-first-issue`, `intermediate`, `advanced`

### Review de Pull Requests

#### Critérios de Review
1. **Funcionalidade**: O código faz o que deveria?
2. **Qualidade**: Segue padrões de código?
3. **Testes**: Tem testes adequados?
4. **Documentação**: Está documentado?
5. **Performance**: Não degrada performance?
6. **Segurança**: Não introduz vulnerabilidades?

#### Processo de Review
```markdown
### Checklist de Review

#### ✅ Código
- [ ] Funcionalidade implementada corretamente
- [ ] Código limpo e legível
- [ ] Padrões de código seguidos
- [ ] Não há código morto ou comentado

#### ✅ Testes
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes passam localmente
- [ ] Cobertura de testes mantida/melhorada
- [ ] Edge cases considerados

#### ✅ Documentação
- [ ] Docstrings atualizadas
- [ ] README atualizado se necessário
- [ ] Changelog atualizado
- [ ] API docs atualizadas

#### ✅ Performance
- [ ] Sem degradação de performance
- [ ] Queries otimizadas
- [ ] Memory leaks verificados
- [ ] Load testing se aplicável

#### ✅ Segurança
- [ ] Inputs validados
- [ ] Outputs sanitizados
- [ ] Sem hardcoded secrets
- [ ] Dependencies verificadas
```

## 🚀 Gerenciamento de Releases

### Ciclo de Release

#### Release Schedule
- **Major**: A cada 6 meses
- **Minor**: A cada 2 meses
- **Patch**: Conforme necessário (bugs críticos)
- **Hotfix**: Imediato para vulnerabilidades

#### Processo de Release

##### 1. Preparação (1-2 semanas antes)
```bash
# Criar branch de release
git checkout develop
git checkout -b release/v2.1.0

# Atualizar versões
# - app.py (VERSION = "2.1.0")
# - requirements.txt se necessário
# - CHANGELOG.md

# Freeze de features
# Apenas bug fixes a partir deste ponto
```

##### 2. Testing Phase (1 semana)
```bash
# Deploy para staging
./deploy-staging.sh

# Testes automatizados
pytest tests/ --cov=app

# Testes manuais
./test-scenarios.sh

# Performance testing
./performance-tests.sh

# Security scan
bandit -r app.py
```

##### 3. Release (Release day)
```bash
# Merge para main
git checkout main
git merge --no-ff release/v2.1.0

# Criar tag
git tag -a v2.1.0 -m "Release v2.1.0"

# Push
git push origin main
git push origin v2.1.0

# Deploy para produção
./deploy-production.sh

# Merge de volta para develop
git checkout develop
git merge main
```

##### 4. Post-Release
```bash
# Comunicação
# - GitHub Release notes
# - Community announcement
# - Documentation update

# Monitoramento
# - Error tracking
# - Performance monitoring
# - User feedback

# Cleanup
git branch -d release/v2.1.0
```

### Release Notes Template

```markdown
# Release v2.1.0 - [Nome do Release]

## 🎯 Highlights

Breve descrição das principais mudanças desta versão.

## ✨ New Features

- **[Área]**: Descrição da nova funcionalidade (#123)
- **[Área]**: Outra funcionalidade importante (#456)

## 🐛 Bug Fixes

- **[Área]**: Correção de bug específico (#789)
- **[Área]**: Outro bug corrigido (#012)

## 🔄 Changes

- **[Área]**: Mudança de comportamento (#345)

## 🗑️ Deprecated

- **[Área]**: Funcionalidade marcada para remoção

## 🔒 Security

- **[Área]**: Correção de vulnerabilidade
- Atualização de dependências com vulnerabilidades

## 📊 Metrics

- **Performance**: Melhoria de X% na velocidade
- **Size**: Redução de Y% no tamanho
- **Tests**: Z% de cobertura de testes

## 🙏 Contributors

Agradecemos a todos que contribuíram para esta release:
- @contributor1
- @contributor2

## 📋 Full Changelog

https://github.com/PetCareAi/analytics/compare/v2.0.0...v2.1.0
```

## 🔧 Manutenção de Infraestrutura

### Monitoramento

#### Métricas Essenciais
- **Uptime**: >99.5%
- **Response Time**: <2s para dashboard
- **Error Rate**: <0.1%
- **User Satisfaction**: >4.0/5.0

#### Ferramentas de Monitoramento
```yaml
# monitoring-stack.yml
services:
  prometheus:
    image: prometheus/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
  
  alertmanager:
    image: prometheus/alertmanager
    ports:
      - "9093:9093"
```

### Backup e Recuperação

#### Backup Strategy
- **Database**: Backup diário incremental, semanal completo
- **Code**: Replicação automática no GitHub
- **Configs**: Backup semanal de configurações
- **User Data**: Backup contínuo com retenção de 90 dias

#### Disaster Recovery Plan
1. **RTO** (Recovery Time Objective): 2 horas
2. **RPO** (Recovery Point Objective): 1 hora
3. **Backup Locations**: Multi-region
4. **Testing**: Monthly DR drills

### Atualizações de Dependências

#### Schedule de Atualizações
```bash
# Atualizações de segurança (imediato)
pip-audit --fix

# Atualizações minor (semanal)
pip-check-updates --minor

# Atualizações major (mensal, com testes)
pip-check-updates --major
```

#### Processo de Atualização
1. **Security Updates**: Automático com CI/CD
2. **Minor Updates**: Review semanal
3. **Major Updates**: Planejamento trimestral
4. **Testing**: Ambiente staging primeiro

## 👥 Gerenciamento da Comunidade

### Comunicação

#### Canais de Comunicação
- **GitHub Discussions**: Perguntas e discussões gerais
- **Issues**: Bugs e feature requests
- **Email**: maintainers@petcareai.com
- **Social Media**: @petcareai (anúncios)

#### Diretrizes de Comunicação
- **Tempo de Resposta**: 24-48h para issues críticas
- **Tom**: Profissional, helpful, inclusivo
- **Idioma**: Português (primário), Inglês (secundário)
- **Templates**: Usar templates padronizados

### Suporte à Contribuidores

#### Programa de Mentoria
- **New Contributors**: Pair programming sessions
- **Regular Contributors**: Code review feedback
- **Advanced Contributors**: Architecture discussions

#### Reconhecimento
- **Monthly Highlights**: Top contributors
- **Annual Awards**: Most valuable contributors
- **Swag**: Camisetas, adesivos para contribuidores ativos

## 📊 Métricas e Análises

### KPIs do Projeto

#### Saúde do Projeto
- **Active Contributors**: >10 por mês
- **Issue Resolution Time**: <7 dias (médio)
- **PR Merge Time**: <3 dias (médio)
- **Test Coverage**: >80%
- **Documentation Coverage**: >90%

#### Qualidade do Código
- **Code Quality Score**: >8.0/10 (SonarQube)
- **Technical Debt**: <5% (SonarQube)
- **Security Vulnerabilities**: 0 críticas
- **Performance Regressions**: 0

#### Engajamento da Comunidade
- **GitHub Stars**: Crescimento mensal
- **Downloads**: Métricas de uso
- **Community Size**: Participantes ativos
- **Retention Rate**: Contribuidores que retornam

### Ferramentas de Análise

#### GitHub Analytics
```bash
# Script para coletar métricas
./scripts/github-analytics.sh

# Relatório mensal
./scripts/monthly-report.sh

# Análise de contribuidores
./scripts/contributor-analysis.sh
```

#### Dashboard de Manutenção
- **Grafana**: Métricas em tempo real
- **GitHub Insights**: Estatísticas do repositório
- **Custom Scripts**: Análises específicas

## 🔄 Processos Automatizados

### CI/CD Pipeline

#### GitHub Actions Workflows

##### Main CI Pipeline (`.github/workflows/ci.yml`)
```yaml
name: CI Pipeline

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
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Run security scan
      run: |
        pip install bandit safety
        bandit -r app.py
        safety check

  quality:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Quality checks
      run: |
        pip install flake8 black isort mypy
        flake8 .
        black --check .
        isort --check-only .
        mypy app.py
```

##### Dependency Updates (`.github/workflows/dependabot.yml`)
```yaml
name: Dependabot Auto-merge

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  auto-merge:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
    - name: Auto-merge
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.pulls.createReview({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: context.issue.number,
            event: 'APPROVE'
          });
          github.rest.pulls.merge({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: context.issue.number,
            merge_method: 'squash'
          });
```

### Automações de Manutenção

#### Issue Management
```yaml
# .github/workflows/issue-management.yml
name: Issue Management

on:
  issues:
    types: [opened, labeled]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
    - name: Add to project
      uses: actions/add-to-project@v0.3.0
      with:
        project-url: https://github.com/orgs/PetCareAi/projects/1
        github-token: ${{ secrets.GITHUB_TOKEN }}

    - name: Auto-assign labels
      uses: actions/github-script@v6
      with:
        script: |
          const labels = [];
          const title = context.payload.issue.title.toLowerCase();
          
          if (title.includes('bug')) labels.push('bug');
          if (title.includes('feature')) labels.push('enhancement');
          if (title.includes('doc')) labels.push('documentation');
          
          if (labels.length > 0) {
            github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: labels
            });
          }
```

#### Stale Issues
```yaml
# .github/workflows/stale.yml
name: Close stale issues

on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/stale@v5
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        stale-issue-message: |
          Esta issue está marcada como stale porque não teve atividade recente.
          Será fechada em 7 dias se não houver mais atividade.
        stale-pr-message: |
          Este PR está marcado como stale porque não teve atividade recente.
          Será fechado em 7 dias se não houver mais atividade.
        days-before-stale: 60
        days-before-close: 7
```

## 🛠️ Ferramentas de Manutenção

### Scripts Úteis

#### Verificação de Saúde do Projeto
```bash
#!/bin/bash
# scripts/health-check.sh

echo "🔍 Verificando saúde do projeto..."

# Verificar dependências
echo "📦 Verificando dependências..."
pip-audit --format=json > security-report.json

# Verificar qualidade do código
echo "🔍 Verificando qualidade do código..."
flake8 . --format=json > quality-report.json

# Verificar cobertura de testes
echo "🧪 Verificando cobertura de testes..."
pytest --cov=app --cov-report=json > coverage-report.json

# Verificar performance
echo "⚡ Verificando performance..."
python -m cProfile -o profile.stats app.py

# Relatório final
echo "📊 Gerando relatório..."
python scripts/generate-health-report.py
```

#### Cleanup de Branches
```bash
#!/bin/bash
# scripts/cleanup-branches.sh

echo "🧹 Limpando branches antigas..."

# Deletar branches merged
git branch --merged main | grep -v "main\|develop" | xargs -n 1 git branch -d

# Deletar branches remotas órfãs
git remote prune origin

echo "✅ Cleanup concluído"
```

#### Análise de Contribuidores
```bash
#!/bin/bash
# scripts/contributor-analysis.sh

echo "👥 Analisando contribuidores..."

# Top contribuidores por commits
echo "🏆 Top 10 contribuidores:"
git shortlog -sn | head -10

# Contribuidores ativos no último mês
echo "📅 Contribuidores ativos (último mês):"
git log --since="1 month ago" --pretty=format:"%an" | sort | uniq -c | sort -nr

# Primeira contribuição
echo "🌟 Primeiras contribuições:"
git log --reverse --pretty=format:"%an - %ad" --date=short | head -10
```

### Dashboard de Manutenção

#### Configuração do Grafana
```json
{
  "dashboard": {
    "title": "PetCareAI Maintenance Dashboard",
    "panels": [
      {
        "title": "Active Issues",
        "type": "stat",
        "targets": [
          {
            "expr": "github_issues_open_total"
          }
        ]
      },
      {
        "title": "PR Merge Time",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(github_pr_merge_time_hours)"
          }
        ]
      },
      {
        "title": "Test Coverage",
        "type": "gauge",
        "targets": [
          {
            "expr": "test_coverage_percentage"
          }
        ]
      }
    ]
  }
}
```

## 📚 Documentação de Manutenção

### Runbooks

#### Incident Response Runbook
```markdown
# Incident Response Runbook

## Severity 1 (Critical)
**Response Time**: Immediate

### Steps:
1. **Acknowledge** - Respond within 15 minutes
2. **Assess** - Determine impact and scope
3. **Communicate** - Update status page
4. **Investigate** - Root cause analysis
5. **Fix** - Implement solution
6. **Verify** - Confirm resolution
7. **Post-mortem** - Document lessons learned

### Contacts:
- **On-call**: +55 11 9999-0000
- **Escalation**: cto@petcareai.com
```

#### Deployment Runbook
```markdown
# Deployment Runbook

## Pre-deployment
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Performance tests passed
- [ ] Rollback plan ready

## Deployment
- [ ] Deploy to staging
- [ ] Smoke tests
- [ ] Deploy to production
- [ ] Health checks

## Post-deployment
- [ ] Monitor for errors
- [ ] Verify functionality
- [ ] Update documentation
- [ ] Communicate success
```

### Knowledge Base

#### Common Issues

##### Issue: High Memory Usage
```markdown
**Symptoms**: Application consuming excessive memory
**Cause**: Usually large datasets not being garbage collected
**Solution**: 
1. Check for memory leaks in ML models
2. Implement data pagination
3. Add explicit garbage collection
4. Monitor with memory profiler
```

##### Issue: Slow Dashboard Loading
```markdown
**Symptoms**: Dashboard takes >5 seconds to load
**Cause**: Unoptimized queries or large datasets
**Solution**:
1. Implement caching
2. Optimize database queries
3. Add loading indicators
4. Implement lazy loading
```

### Documentação de APIs Internas

#### Maintenance API
```python
# Internal maintenance API endpoints

@app.route('/api/maintenance/health')
def health_check():
    """System health check endpoint."""
    return {
        'status': 'healthy',
        'version': get_version(),
        'uptime': get_uptime(),
        'dependencies': check_dependencies()
    }

@app.route('/api/maintenance/metrics')
def get_metrics():
    """Get system metrics."""
    return {
        'active_users': get_active_users(),
        'response_time': get_avg_response_time(),
        'error_rate': get_error_rate(),
        'database_size': get_database_size()
    }
```

## 🎓 Treinamento de Mantenedores

### Programa de Onboarding

#### Semana 1: Fundamentos
- **Day 1-2**: Setup do ambiente e familiarização
- **Day 3-4**: Revisão da arquitetura e código
- **Day 5**: Primeira triagem de issues (shadowing)

#### Semana 2: Práticas
- **Day 1-2**: Revisão de PRs (com mentor)
- **Day 3-4**: Gerenciamento de releases (observação)
- **Day 5**: Incident response simulation

#### Semana 3: Independência
- **Day 1-5**: Atividades independentes com check-ins

### Recursos de Aprendizado

#### Documentação Obrigatória
- [ ] Architecture Overview
- [ ] Contributing Guidelines
- [ ] Security Policies
- [ ] Release Process
- [ ] Code Style Guide

#### Ferramentas Essenciais
- [ ] GitHub (advanced features)
- [ ] Git (advanced workflows)
- [ ] CI/CD pipelines
- [ ] Monitoring tools
- [ ] Security scanners

## 🔄 Evolução e Melhoria Contínua

### Retrospectivas

#### Monthly Retrospectives
- **Formato**: Start/Stop/Continue
- **Participantes**: Todos os mantenedores
- **Duração**: 1 hora
- **Output**: Action items com owners

#### Quarterly Reviews
- **Métricas**: Review de KPIs
- **Processo**: Avaliação de eficiência
- **Ferramentas**: Avaliação de stack
- **Roadmap**: Ajustes na direção

### Experimentação

#### A/B Testing para Processos
- **Release Frequency**: Testar cadências diferentes
- **Review Process**: Diferentes abordagens
- **Communication**: Canais e formatos
- **Automation**: Níveis de automação

### Feedback e Melhoria

#### Canais de Feedback
- **Mantenedores**: Slack interno
- **Comunidade**: GitHub Discussions
- **Usuários**: Formulários de feedback
- **Métricas**: Análise quantitativa

#### Implementação de Melhorias
1. **Identificação**: Via feedback ou métricas
2. **Planejamento**: Design da solução
3. **Implementação**: Execução controlada
4. **Avaliação**: Medição de impacto
5. **Iteração**: Refinamento contínuo

---

## 📞 Contatos de Emergência

### Equipe Principal
- **Project Lead**: lead@petcareai.com
- **Security Team**: security@petcareai.com
- **Infrastructure**: infra@petcareai.com

### Serviços Críticos
- **Hosting Provider**: [Contato do provedor]
- **Database Provider**: [Contato Supabase]
- **Monitoring**: [Contato do serviço]

### Escalation Matrix
1. **Level 1**: Community maintainers
2. **Level 2**: Core maintainers
3. **Level 3**: Project lead
4. **Level 4**: External support

---

**Importante**: Este documento é atualizado regularmente. Mantenedores devem revisar mensalmente e sugerir melhorias através de PRs.

*Última atualização: 29/06/2025*
*Próxima revisão: 29/07/2025*
