#!/bin/bash
# Script para executar o PetCare Analytics
# Compatível com Linux, macOS e Windows (WSL/Git Bash)

set -e  # Parar execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Função para detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para ativar ambiente virtual
activate_venv() {
    print_info "Ativando ambiente virtual..."

    if [ ! -d "venv" ]; then
        print_error "Ambiente virtual não encontrado!"
        print_info "Execute primeiro: bash install.sh"
        exit 1
    fi

    # Ativar ambiente virtual baseado no OS
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi

    print_success "Ambiente virtual ativado"
}

# Função para verificar arquivo .env
check_env_file() {
    print_info "Verificando configurações..."

    if [ ! -f ".env" ]; then
        print_error "Arquivo .env não encontrado!"
        print_info "Criando arquivo .env básico..."

        cat > .env << 'EOF'
# Configurações do Supabase - CONFIGURE SUAS CREDENCIAIS
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima

# Configurações de Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app

# Configurações do Sistema
DEBUG_MODE=false
SESSION_TIMEOUT=3600
MAX_UPLOAD_SIZE=10485760

# Porta da aplicação
PORT=8501

# APIs Externas (opcional)
GOOGLE_MAPS_API_KEY=sua_chave_do_google_maps
OPENAI_API_KEY=sua_chave_do_openai
EOF

        print_warning "Arquivo .env criado. CONFIGURE suas credenciais antes de continuar!"
        print_info "Edite o arquivo .env com suas credenciais do Supabase"

        # Verificar se há editor disponível
        if command_exists nano; then
            read -p "Deseja editar o arquivo .env agora? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                nano .env
            fi
        elif command_exists code; then
            read -p "Deseja abrir o arquivo .env no VS Code? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                code .env
            fi
        fi

        exit 0
    fi

    # Verificar se credenciais estão configuradas
    if grep -q "sua_url_do_supabase\|sua_chave_anonima" .env; then
        print_error "Credenciais do Supabase não configuradas no arquivo .env!"
        print_info "Configure suas credenciais antes de executar a aplicação"
        exit 1
    fi

    print_success "Arquivo .env encontrado e configurado"
}

# Função para verificar dependências
check_dependencies() {
    print_info "Verificando dependências..."

    # Verificar se Python funciona
    if ! python -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
        print_error "Python não funciona no ambiente virtual!"
        print_info "Execute: bash install.sh"
        exit 1
    fi

    # Verificar dependências principais
    missing_deps=()

    if ! python -c "import streamlit" 2>/dev/null; then
        missing_deps+=("streamlit")
    fi

    if ! python -c "import pandas" 2>/dev/null; then
        missing_deps+=("pandas")
    fi

    if ! python -c "import supabase" 2>/dev/null; then
        missing_deps+=("supabase")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Dependências faltando: ${missing_deps[*]}"
        print_info "Execute: pip install -r requirements.txt"
        exit 1
    fi

    print_success "Todas as dependências estão instaladas"
}

# Função para verificar arquivos principais
check_main_files() {
    print_info "Verificando arquivos principais..."

    if [ ! -f "app.py" ]; then
        print_error "Arquivo principal app.py não encontrado!"
        exit 1
    fi

    if [ ! -f "config/database.py" ]; then
        print_error "Arquivo de configuração database.py não encontrado!"
        exit 1
    fi

    print_success "Arquivos principais encontrados"
}

# Função para testar conexão com Supabase
test_supabase_connection() {
    print_info "Testando conexão com Supabase..."

    python3 -c "
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if not url or not key:
    print('❌ Credenciais do Supabase não encontradas')
    sys.exit(1)

try:
    from supabase import create_client
    client = create_client(url, key)

    # Teste de conectividade simples
    response = client.table('users_analytics').select('id').limit(1).execute()
    print('✅ Conexão com Supabase estabelecida')
    print(f'🌐 URL: {url}')

except Exception as e:
    print(f'⚠️ Erro na conexão: {str(e)}')
    print('Verifique suas credenciais no arquivo .env')
    # Não sair com erro, pois a aplicação pode funcionar mesmo assim
" 2>/dev/null || print_warning "Problemas na conexão com Supabase - verifique credenciais"
}

# Função para limpar cache e arquivos temporários
cleanup_cache() {
    print_info "Limpando cache e arquivos temporários..."

    # Limpar cache do Python
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

    # Limpar cache do Streamlit
    if [ -d ".streamlit" ]; then
        rm -rf .streamlit 2>/dev/null || true
    fi

    # Limpar logs antigos
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi

    print_success "Cache limpo"
}

# Função para configurar porta
setup_port() {
    # Verificar se porta está definida no .env
    if [ -f ".env" ]; then
        PORT=$(grep "^PORT=" .env | cut -d '=' -f2 | tr -d ' ')
    fi

    # Porta padrão se não definida
    if [ -z "$PORT" ]; then
        PORT=8501
    fi

    # Verificar se porta está em uso
    if command_exists lsof && lsof -i :$PORT >/dev/null 2>&1; then
        print_warning "Porta $PORT já está em uso"
        PORT=$((PORT + 1))
        print_info "Usando porta alternativa: $PORT"
    fi

    export STREAMLIT_SERVER_PORT=$PORT
}

# Função para configurar variáveis de ambiente para execução
setup_runtime_env() {
    print_info "Configurando ambiente de execução..."

    # Carregar variáveis do .env
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    # Configurações do Streamlit
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_PORT=$PORT
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

    # Configurações de cache
    export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
    export STREAMLIT_SERVER_ENABLE_CORS=false

    # Configurações de desenvolvimento se DEBUG_MODE=true
    if [ "$DEBUG_MODE" = "true" ]; then
        export STREAMLIT_SERVER_RUN_ON_SAVE=true
        export STREAMLIT_SERVER_FILE_WATCHER_TYPE=auto
        print_info "Modo debug ativado - auto-reload habilitado"
    fi

    print_success "Ambiente configurado"
}

# Função para mostrar informações de status
show_system_info() {
    print_header "=== INFORMAÇÕES DO SISTEMA ==="
    echo -e "${CYAN}Sistema Operacional:${NC} $OS"
    echo -e "${CYAN}Python:${NC} $(python --version 2>&1)"
    echo -e "${CYAN}Streamlit:${NC} $(python -c 'import streamlit; print(streamlit.__version__)' 2>/dev/null || echo 'Não instalado')"
    echo -e "${CYAN}Porta:${NC} $PORT"
    echo -e "${CYAN}URL Local:${NC} http://localhost:$PORT"
    echo -e "${CYAN}Modo Debug:${NC} ${DEBUG_MODE:-false}"
    echo -e "${CYAN}Diretório:${NC} $(pwd)"
    echo "================================"
    echo
}

# Função para criar arquivos de configuração do Streamlit
create_streamlit_config() {
    print_info "Configurando Streamlit..."

    # Criar diretório de configuração
    mkdir -p .streamlit

    # Criar arquivo de configuração
    cat > .streamlit/config.toml << EOF
[server]
port = $PORT
address = "0.0.0.0"
headless = true
runOnSave = false
maxUploadSize = 200
enableCORS = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = $PORT

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[client]
showErrorDetails = true
toolbarMode = "minimal"
EOF

    # Criar arquivo de credenciais se necessário
    if [ ! -f ".streamlit/secrets.toml" ]; then
        cat > .streamlit/secrets.toml << 'EOF'
# Secrets do Streamlit
# Este arquivo é usado para armazenar credenciais sensíveis

[supabase]
SUPABASE_URL = ""
SUPABASE_ANON_KEY = ""

# Para usar, descomente e configure:
# [email]
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "seu_email@gmail.com"
# SMTP_PASSWORD = "sua_senha"
EOF
    fi

    print_success "Configuração do Streamlit criada"
}

# Função para verificar e criar logs
setup_logging() {
    print_info "Configurando sistema de logs..."

    # Criar diretório de logs
    mkdir -p logs

    # Arquivo de log da aplicação
    APP_LOG="logs/app_$(date +%Y%m%d).log"

    # Arquivo de log de erro
    ERROR_LOG="logs/error_$(date +%Y%m%d).log"

    # Criar arquivos se não existirem
    touch "$APP_LOG"
    touch "$ERROR_LOG"

    # Exportar para uso da aplicação
    export APP_LOG_FILE="$APP_LOG"
    export ERROR_LOG_FILE="$ERROR_LOG"

    print_success "Sistema de logs configurado"
}

# Função para monitorar aplicação
monitor_app() {
    local pid=$1
    local start_time=$(date +%s)

    print_info "Monitorando aplicação (PID: $pid)..."

    while kill -0 $pid 2>/dev/null; do
        sleep 5
        current_time=$(date +%s)
        uptime=$((current_time - start_time))

        # Mostrar status a cada 60 segundos
        if [ $((uptime % 60)) -eq 0 ] && [ $uptime -gt 0 ]; then
            print_info "Aplicação rodando há $((uptime / 60)) minuto(s)"
        fi
    done

    print_warning "Aplicação parou de executar"
}

# Função para tratar sinais (CTRL+C)
cleanup_on_exit() {
    print_info "Encerrando aplicação..."

    # Matar processo do Streamlit se estiver rodando
    if [ ! -z "$APP_PID" ]; then
        kill $APP_PID 2>/dev/null || true
    fi

    # Limpar arquivos temporários
    cleanup_cache

    print_success "Aplicação encerrada"
    exit 0
}

# Função para verificar updates
check_for_updates() {
    if command_exists git && [ -d ".git" ]; then
        print_info "Verificando atualizações..."

        # Buscar mudanças remotas
        git fetch origin main 2>/dev/null || true

        # Verificar se há commits novos
        LOCAL=$(git rev-parse HEAD 2>/dev/null)
        REMOTE=$(git rev-parse origin/main 2>/dev/null)

        if [ "$LOCAL" != "$REMOTE" ] 2>/dev/null; then
            print_warning "Atualizações disponíveis!"
            print_info "Execute: git pull origin main"
        fi
    fi
}

# Função para executar pré-verificações
run_pre_checks() {
    print_header "🔍 EXECUTANDO PRÉ-VERIFICAÇÕES"

    # Verificar se está no diretório correto
    if [ ! -f "app.py" ]; then
        print_error "Execute este script no diretório raiz do projeto!"
        exit 1
    fi

    # Detectar sistema operacional
    detect_os

    # Ativar ambiente virtual
    activate_venv

    # Verificar arquivo .env
    check_env_file

    # Verificar dependências
    check_dependencies

    # Verificar arquivos principais
    check_main_files

    # Configurar porta
    setup_port

    # Configurar ambiente de execução
    setup_runtime_env

    # Configurar Streamlit
    create_streamlit_config

    # Configurar logs
    setup_logging

    # Testar Supabase
    test_supabase_connection

    # Verificar updates
    check_for_updates

    # Limpar cache
    cleanup_cache

    print_success "Pré-verificações concluídas"
    echo
}

# Função para executar aplicação
run_application() {
    print_header "🚀 INICIANDO PETCARE ANALYTICS"

    # Mostrar informações do sistema
    show_system_info

    # Configurar trap para cleanup
    trap cleanup_on_exit INT TERM EXIT

    print_info "Iniciando aplicação Streamlit..."
    print_info "Pressione CTRL+C para parar"
    echo

    # Executar Streamlit
    if [ "$DEBUG_MODE" = "true" ]; then
        print_warning "Executando em modo DEBUG"
        streamlit run app.py \
            --server.port $PORT \
            --server.address 0.0.0.0 \
            --server.runOnSave true \
            --server.fileWatcherType auto \
            --logger.level debug 2>&1 | tee "$APP_LOG" &
    else
        streamlit run app.py \
            --server.port $PORT \
            --server.address 0.0.0.0 \
            --server.headless true 2>&1 | tee "$APP_LOG" &
    fi

    APP_PID=$!

    # Aguardar inicialização
    sleep 3

    # Verificar se a aplicação iniciou
    if ! kill -0 $APP_PID 2>/dev/null; then
        print_error "Falha ao iniciar aplicação!"
        print_info "Verifique o log em: $APP_LOG"
        exit 1
    fi

    print_success "Aplicação iniciada com sucesso!"
    echo
    print_header "📱 ACESSE A APLICAÇÃO:"
    echo -e "${GREEN}🌐 Local:${NC}    http://localhost:$PORT"
    echo -e "${GREEN}🌍 Rede:${NC}     http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'IP_DA_MAQUINA'):$PORT"
    echo
    print_info "Logs sendo salvos em: $APP_LOG"
    print_info "Para parar a aplicação, pressione CTRL+C"
    echo

    # Monitorar aplicação
    monitor_app $APP_PID
}

# Função para mostrar ajuda
show_help() {
    echo "🐾 PetCare Analytics - Script de Execução"
    echo "========================================="
    echo
    echo "Uso: $0 [opções]"
    echo
    echo "Opções:"
    echo "  -h, --help         Mostrar esta ajuda"
    echo "  -d, --debug        Executar em modo debug"
    echo "  -p, --port PORT    Especificar porta (padrão: 8501)"
    echo "  -c, --clean        Limpar cache antes de executar"
    echo "  --dev              Executar em modo desenvolvimento"
    echo "  --prod             Executar em modo produção"
    echo "  --check            Apenas verificar dependências"
    echo "  --install          Executar instalação"
    echo
    echo "Exemplos:"
    echo "  $0                 # Executar normalmente"
    echo "  $0 --debug         # Executar em modo debug"
    echo "  $0 --port 8080     # Executar na porta 8080"
    echo "  $0 --check         # Apenas verificar sistema"
    echo
}

# Função principal
main() {
    # Processar argumentos da linha de comando
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--debug)
                export DEBUG_MODE=true
                shift
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -c|--clean)
                cleanup_cache
                shift
                ;;
            --dev)
                export DEBUG_MODE=true
                shift
                ;;
            --prod)
                export DEBUG_MODE=false
                shift
                ;;
            --check)
                run_pre_checks
                print_success "Sistema OK!"
                exit 0
                ;;
            --install)
                if [ -f "install.sh" ]; then
                    bash install.sh
                else
                    print_error "Script install.sh não encontrado!"
                fi
                exit 0
                ;;
            *)
                print_error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Executar pré-verificações
    run_pre_checks

    # Executar aplicação
    run_application
}

# Verificar se está sendo executado como script principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
