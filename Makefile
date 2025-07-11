# Makefile para PetCareAi
# Facilita execução de comandos comuns de desenvolvimento

.PHONY: help install dev test lint format clean build deploy docs backup

# Configurações
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit
PROJECT_NAME := petcare-ai
VERSION := $(shell cat .version)

# Cores para output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Help - comando padrão
help: ## Mostrar ajuda com comandos disponíveis
	@echo "$(BLUE)PetCareAi - Sistema Avançado com IA$(RESET)"
	@echo "$(YELLOW)Versão: $(VERSION)$(RESET)"
	@echo ""
	@echo "$(GREEN)Comandos disponíveis:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ===== INSTALAÇÃO E SETUP =====

install: ## Instalar dependências básicas
	@echo "$(BLUE)Instalando dependências...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependências instaladas com sucesso!$(RESET)"

install-dev: install ## Instalar dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências de desenvolvimento...$(RESET)"
	$(PIP) install -r requirements-dev.txt
	pre-commit install
	@echo "$(GREEN)Ambiente de desenvolvimento configurado!$(RESET)"

install-test: ## Instalar dependências de teste
	@echo "$(BLUE)Instalando dependências de teste...$(RESET)"
	$(PIP) install -r requirements-test.txt
	@echo "$(GREEN)Dependências de teste instaladas!$(RESET)"

setup: install-dev ## Setup completo do ambiente de desenvolvimento
	@echo "$(BLUE)Configurando ambiente completo...$(RESET)"
	mkdir -p logs data backups exports
	chmod +x scripts/*.sh
	$(PYTHON) -c "from config.database import init_database; init_database()"
	@echo "$(GREEN)Ambiente configurado com sucesso!$(RESET)"

# ===== DESENVOLVIMENTO =====

dev: ## Executar aplicação em modo desenvolvimento
	@echo "$(BLUE)Iniciando aplicação em modo desenvolvimento...$(RESET)"
	$(STREAMLIT) run app.py --server.runOnSave=true --server.address=0.0.0.0

run: ## Executar aplicação
	@echo "$(BLUE)Iniciando PetCareAi...$(RESET)"
	$(STREAMLIT) run app.py

serve: ## Servir aplicação na porta especificada
	@echo "$(BLUE)Servindo aplicação na porta 8501...$(RESET)"
	$(STREAMLIT) run app.py --server.port=8501

# ===== TESTES =====

test: ## Executar todos os testes
	@echo "$(BLUE)Executando testes...$(RESET)"
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-unit: ## Executar apenas testes unitários
	@echo "$(BLUE)Executando testes unitários...$(RESET)"
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## Executar testes de integração
	@echo "$(BLUE)Executando testes de integração...$(RESET)"
	$(PYTHON) -m pytest tests/integration/ -v

test-e2e: ## Executar testes end-to-end
	@echo "$(BLUE)Executando testes E2E...$(RESET)"
	$(PYTHON) -m pytest tests/e2e/ -v --maxfail=1

test-coverage: ## Executar testes com relatório de cobertura
	@echo "$(BLUE)Executando testes com cobertura...$(RESET)"
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-fail-under=80
	@echo "$(GREEN)Relatório de cobertura gerado em htmlcov/$(RESET)"

test-watch: ## Executar testes em modo watch
	@echo "$(BLUE)Executando testes em modo watch...$(RESET)"
	$(PYTHON) -m pytest-watch tests/

# ===== QUALIDADE DE CÓDIGO =====

lint: ## Executar verificações de qualidade de código
	@echo "$(BLUE)Executando linting...$(RESET)"
	flake8 --max-line-length=100 --ignore=E203,W503 .
	mypy --ignore-missing-imports .
	bandit -r . -f json -o bandit-report.json || true
	@echo "$(GREEN)Linting concluído!$(RESET)"

format: ## Formatar código automaticamente
	@echo "$(BLUE)Formatando código...$(RESET)"
	black --line-length=100 .
	isort --profile=black --line-length=100 .
	@echo "$(GREEN)Código formatado!$(RESET)"

format-check: ## Verificar formatação sem alterar arquivos
	@echo "$(BLUE)Verificando formatação...$(RESET)"
	black --check --line-length=100 .
	isort --check-only --profile=black --line-length=100 .

pre-commit: ## Executar hooks de pre-commit
	@echo "$(BLUE)Executando pre-commit...$(RESET)"
	pre-commit run --all-files

# ===== SEGURANÇA =====

security: ## Executar verificações de segurança
	@echo "$(BLUE)Executando verificações de segurança...$(RESET)"
	bandit -r . -f json -o reports/bandit-report.json
	safety check --json --output reports/safety-report.json || true
	@echo "$(GREEN)Verificações de segurança concluídas!$(RESET)"

secrets-scan: ## Verificar secrets expostos
	@echo "$(BLUE)Verificando secrets...$(RESET)"
	detect-secrets scan --baseline .secrets.baseline .
	@echo "$(GREEN)Verificação de secrets concluída!$(RESET)"

# ===== BANCO DE DADOS =====

db-init: ## Inicializar banco de dados
	@echo "$(BLUE)Inicializando banco de dados...$(RESET)"
	$(PYTHON) -c "from config.database import init_database; init_database()"
	@echo "$(GREEN)Banco de dados inicializado!$(RESET)"

db-reset: ## Resetar banco de dados
	@echo "$(YELLOW)ATENÇÃO: Isso irá apagar todos os dados!$(RESET)"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Resetando banco de dados...$(RESET)"; \
		$(PYTHON) -c "from config.database import reset_database; reset_database()"; \
		echo "$(GREEN)Banco de dados resetado!$(RESET)"; \
	else \
		echo "$(YELLOW)Operação cancelada.$(RESET)"; \
	fi

db-backup: ## Fazer backup do banco de dados
	@echo "$(BLUE)Fazendo backup do banco...$(RESET)"
	mkdir -p backups
	$(PYTHON) scripts/backup_database.py
	@echo "$(GREEN)Backup concluído!$(RESET)"

db-restore: ## Restaurar backup do banco de dados
	@echo "$(BLUE)Restaurando backup...$(RESET)"
	$(PYTHON) scripts/restore_database.py
	@echo "$(GREEN)Restauração concluída!$(RESET)"

# ===== BUILD E DISTRIBUIÇÃO =====

build: clean ## Construir pacote para distribuição
	@echo "$(BLUE)Construindo pacote...$(RESET)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)Pacote construído em dist/$(RESET)"

build-docker: ## Construir imagem Docker
	@echo "$(BLUE)Construindo imagem Docker...$(RESET)"
	docker build -t $(PROJECT_NAME):$(VERSION) .
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest
	@echo "$(GREEN)Imagem Docker construída!$(RESET)"

# ===== DOCUMENTAÇÃO =====

docs: ## Gerar documentação
	@echo "$(BLUE)Gerando documentação...$(RESET)"
	mkdir -p docs/build
	$(PYTHON) scripts/generate_docs.py
	@echo "$(GREEN)Documentação gerada em docs/build/$(RESET)"

docs-serve: ## Servir documentação localmente
	@echo "$(BLUE)Servindo documentação...$(RESET)"
	cd docs && python -m http.server 8000

docs-api: ## Gerar documentação da API
	@echo "$(BLUE)Gerando documentação da API...$(RESET)"
	$(PYTHON) scripts/generate_api_docs.py
	@echo "$(GREEN)Documentação da API gerada!$(RESET)"

# ===== LIMPEZA =====

clean: ## Limpar arquivos temporários e cache
	@echo "$(BLUE)Limpando arquivos temporários...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf logs/*.log tmp/* temp/*
	@echo "$(GREEN)Limpeza concluída!$(RESET)"

clean-data: ## Limpar dados de desenvolvimento (CUIDADO!)
	@echo "$(RED)ATENÇÃO: Isso irá apagar dados de desenvolvimento!$(RESET)"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/dev_* uploads/temp_* cache/*; \
		echo "$(GREEN)Dados de desenvolvimento limpos!$(RESET)"; \
	else \
		echo "$(YELLOW)Operação cancelada.$(RESET)"; \
	fi

clean-all: clean clean-data ## Limpeza completa (CUIDADO!)

# ===== DEPLOY =====

deploy-staging: ## Deploy para ambiente de staging
	@echo "$(BLUE)Fazendo deploy para staging...$(RESET)"
	./scripts/deploy-staging.sh
	@echo "$(GREEN)Deploy para staging concluído!$(RESET)"

deploy-production: ## Deploy para produção
	@echo "$(BLUE)Fazendo deploy para produção...$(RESET)"
	@read -p "Confirma deploy para PRODUÇÃO? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		./scripts/deploy-production.sh; \
		echo "$(GREEN)Deploy para produção concluído!$(RESET)"; \
	else \
		echo "$(YELLOW)Deploy cancelado.$(RESET)"; \
	fi

# ===== UTILITÁRIOS =====

requirements: ## Atualizar requirements.txt
	@echo "$(BLUE)Atualizando requirements.txt...$(RESET)"
	pip freeze > requirements.txt
	@echo "$(GREEN)Requirements atualizados!$(RESET)"

check-deps: ## Verificar dependências desatualizadas
	@echo "$(BLUE)Verificando dependências...$(RESET)"
	pip list --outdated
	@echo "$(GREEN)Verificação concluída!$(RESET)"

update-deps: ## Atualizar dependências
	@echo "$(BLUE)Atualizando dependências...$(RESET)"
	pip install --upgrade -r requirements.txt
	@echo "$(GREEN)Dependências atualizadas!$(RESET)"

logs: ## Mostrar logs da aplicação
	@echo "$(BLUE)Logs da aplicação:$(RESET)"
	tail -f logs/app.log

status: ## Mostrar status do sistema
	@echo "$(BLUE)Status do Sistema PetCareAi$(RESET)"
	@echo "Versão: $(VERSION)"
	@echo "Python: $(python --version)"
	@echo "Streamlit: $(streamlit version)"
	@echo "Diretório: $(pwd)"
	@echo "Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
	@echo "Último commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"

version: ## Mostrar versão atual
	@echo "$(GREEN)PetCareAi v$(VERSION)$(RESET)"

bump-version: ## Incrementar versão (patch)
	@echo "$(BLUE)Incrementando versão...$(RESET)"
	$(PYTHON) scripts/bump_version.py patch
	@echo "$(GREEN)Versão atualizada para: $(cat .version)$(RESET)"

bump-minor: ## Incrementar versão minor
	@echo "$(BLUE)Incrementando versão minor...$(RESET)"
	$(PYTHON) scripts/bump_version.py minor
	@echo "$(GREEN)Versão atualizada para: $(cat .version)$(RESET)"

bump-major: ## Incrementar versão major
	@echo "$(BLUE)Incrementando versão major...$(RESET)"
	$(PYTHON) scripts/bump_version.py major
	@echo "$(GREEN)Versão atualizada para: $(cat .version)$(RESET)"

# ===== MONITORAMENTO =====

monitor: ## Monitorar aplicação em execução
	@echo "$(BLUE)Monitorando aplicação...$(RESET)"
	$(PYTHON) scripts/monitor.py

health: ## Verificar saúde da aplicação
	@echo "$(BLUE)Verificando saúde da aplicação...$(RESET)"
	$(PYTHON) -c "from scripts.health_check import check_health; check_health()"

metrics: ## Mostrar métricas da aplicação
	@echo "$(BLUE)Métricas da aplicação:$(RESET)"
	$(PYTHON) scripts/show_metrics.py

# ===== DADOS =====

import-data: ## Importar dados de exemplo
	@echo "$(BLUE)Importando dados de exemplo...$(RESET)"
	$(PYTHON) scripts/import_sample_data.py
	@echo "$(GREEN)Dados importados com sucesso!$(RESET)"

export-data: ## Exportar dados atuais
	@echo "$(BLUE)Exportando dados...$(RESET)"
	$(PYTHON) scripts/export_data.py
	@echo "$(GREEN)Dados exportados para exports/$(RESET)"

seed-data: ## Popular banco com dados de desenvolvimento
	@echo "$(BLUE)Populando banco com dados de desenvolvimento...$(RESET)"
	$(PYTHON) scripts/seed_database.py
	@echo "$(GREEN)Dados de desenvolvimento inseridos!$(RESET)"

# ===== RELEASE =====

release: ## Preparar nova release
	@echo "$(BLUE)Preparando release...$(RESET)"
	$(PYTHON) scripts/prepare_release.py
	@echo "$(GREEN)Release preparada!$(RESET)"

changelog: ## Gerar changelog automático
	@echo "$(BLUE)Gerando changelog...$(RESET)"
	$(PYTHON) scripts/generate_changelog.py
	@echo "$(GREEN)Changelog atualizado!$(RESET)"

tag: ## Criar tag da versão atual
	@echo "$(BLUE)Criando tag v$(VERSION)...$(RESET)"
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@echo "$(GREEN)Tag v$(VERSION) criada!$(RESET)"

# ===== CONFIGURAÇÕES AVANÇADAS =====

# Configurar para usar cores sempre
export FORCE_COLOR = 1

# Evitar que make delete arquivos intermediários
.PRECIOUS: %.py %.md

# Definir shell para comandos
SHELL := /bin/bash

# Configurações para desenvolvimento Docker
docker-dev: ## Executar ambiente de desenvolvimento com Docker
	@echo "$(BLUE)Iniciando ambiente Docker para desenvolvimento...$(RESET)"
	docker-compose -f docker-compose.dev.yml up --build

docker-test: ## Executar testes em container Docker
	@echo "$(BLUE)Executando testes em Docker...$(RESET)"
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

docker-clean: ## Limpar containers e imagens Docker
	@echo "$(BLUE)Limpando containers Docker...$(RESET)"
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# ===== ALIASES ÚTEIS =====

start: run ## Alias para run
stop: ## Parar aplicação (se rodando em background)
	@echo "$(BLUE)Parando aplicação...$(RESET)"
	pkill -f "streamlit run" || echo "Aplicação não estava rodando"

restart: stop run ## Reiniciar aplicação

quick-test: test-unit lint ## Testes rápidos para desenvolvimento

full-check: clean install-dev test lint security docs ## Verificação completa antes de commit

ci: install test lint security ## Comandos para CI/CD

local-ci: clean full-check ## Simular CI localmente

# ===== CONFIGURAÇÕES DE VARIÁVEIS =====

# Verificar se .env existe e carregar
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Configurar PYTHONPATH
export PYTHONPATH := $(PWD):$(PYTHONPATH)

# Configurar cores baseado no terminal
ifeq ($(shell tput colors 2>/dev/null),256)
    GREEN := \033[38;5;82m
    BLUE := \033[38;5;39m
    YELLOW := \033[38;5;226m
    RED := \033[38;5;196m
endif
