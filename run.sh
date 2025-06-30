#!/bin/bash

# PetCareAI Analytics - Script de Execução
# Versão: 2.0.0
# Data: 29/06/2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="PetCareAI Analytics"
VENV_NAME="petcare-venv"
DEFAULT_PORT=8501
LOG_FILE="logs/runtime.log"

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$LOG_FILE" 2>/dev/null || true
}

# Banner de inicialização
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║                🐾 PetCareAI Analytics v2.0.0 🐾                 ║"
    echo "║                                                                  ║"
    echo "║              Sistema Avançado com Inteligência Artificial       ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# Verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    local errors=0
    
    # Verificar se está no diretório correto
    if [[ ! -f "app.py" ]]; then
        log_error "app.py não encontrado. Execute este script no diretório do projeto."
        ((errors++))
    fi
    
    # Verificar ambiente virtual
    if [[ ! -d "$VENV_NAME" ]]; then
        log_error "Ambiente virtual não encontrado. Execute install.sh primeiro."
        ((errors++))
    fi
    
    # Verificar arquivo .env
    if [[ ! -f ".env" ]]; then
        log_error "Arquivo .env não encontrado. Execute configure.sh primeiro."
        ((errors++))
    fi
    
    # Criar diretório de logs se não existir
    mkdir -p logs
    
    if [[ $errors -gt 0 ]]; then
        log_error "Encontrados $errors problemas. Resolva-os antes de continuar."
        exit 1
    fi
    
    log_success "Pré-requisitos verificados"
}

# Ativar ambiente virtual
activate_environment() {
    log_info "Ativando ambiente virtual..."
    
    # Tentar ativar ambiente virtual (Linux/Mac)
    if [[ -f "$VENV_NAME/bin/activate" ]]; then
        source "$VENV_NAME/bin/activate"
    # Tentar ativar ambiente virtual (Windows)
    elif [[ -f "$VENV_NAME/Scripts/activate" ]]; then
        source "$VENV_NAME/Scripts/activate"
    else
        log_error "Script de ativação do ambiente virtual não encontrado."
        exit 1
    fi
    
    log_success "Ambiente virtual ativado: $VIRTUAL_ENV"
}

# Carregar variáveis de ambiente
load_environment_variables() {
    log_info "Carregando variáveis de ambiente..."
    
    # Carregar .env
    if [[ -f ".env" ]]; then
        export $(cat .env | grep -v '^#' | grep -v '^\s* " | xargs)
        log_success "Variáveis de ambiente carregadas"
    else
        log_error "Arquivo .env não encontrado"
        exit 1
    fi
    
    # Definir valores padrão se não especificados
    export STREAMLIT_PORT=${STREAMLIT_PORT:-$DEFAULT_PORT}
    export STREAMLIT_ENV=${STREAMLIT_ENV:-development}
    export DEBUG=${DEBUG:-True}
    export CACHE_ENABLED=${CACHE_ENABLED:-False}
    
    log_info "Ambiente: $STREAMLIT_ENV"
    log_info "Porta: $STREAMLIT_PORT"
    log_info "Debug: $DEBUG"
}

# Verificar dependências Python
check_python_dependencies() {
    log_info "Verificando dependências Python..."
    
    python -c "
import sys
import pkg_resources

def check_dependencies():
    required_packages = [
        'streamlit>=1.31.1',
        'pandas>=2.2.0',
        'numpy>=1.24.0',
        'plotly>=5.18.0',
        'supabase>=2.3.0',
        'python-dotenv>=1.0.0'
    ]
    
    missing = []
    for package in required_packages:
        try:
            pkg_resources.require(package)
            print(f'✓ {package.split(\">=\" )[0]}')
        except pkg_resources.DistributionNotFound:
            print(f'✗ {package} - FALTANDO')
            missing.append(package)
        except pkg_resources.VersionConflict as e:
            print(f'⚠ {package} - VERSÃO INCOMPATÍVEL: {e}')
            missing.append(package)
    
    if missing:
        print(f'\\nDependências faltando: {len(missing)}')
        print('Execute: pip install -r requirements.txt')
        sys.exit(1)
    else:
        print('\\n✅ Todas as dependências estão OK')

check_dependencies()
" || {
        log_error "Dependências Python faltando ou incompatíveis"
        log_info "Execute: pip install -r requirements.txt"
        exit 1
    }
    
    log_success "Dependências Python verificadas"
}

# Testar conexão com banco de dados
test_database_connection() {
    log_info "Testando conexão com banco de dados..."
    
    python -c "
import os
from supabase import create_client

try:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print('❌ Credenciais do Supabase não encontradas')
        exit(1)
    
    client = create_client(url, key)
    
    # Teste simples de conexão
    result = client.table('users_analytics').select('id').limit(1).execute()
    print('✅ Conexão com Supabase estabelecida')
    
except Exception as e:
    print(f'❌ Erro na conexão com banco: {e}')
    print('Verifique suas credenciais SUPABASE_URL e SUPABASE_ANON_KEY')
    exit(1)
" || {
        log_error "Falha na conexão com banco de dados"
        log_info "Verifique as configurações no arquivo .env"
        exit 1
    }
    
    log_success "Conexão com banco de dados testada"
}

# Verificar porta disponível
check_port_availability() {
    local port=$1
    
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            return 1
        fi
    elif command -v lsof &> /dev/null; then
        if lsof -i :$port &> /dev/null; then
            return 1
        fi
    fi
    
    return 0
}

# Encontrar porta disponível
find_available_port() {
    local port=$STREAMLIT_PORT
    
    if check_port_availability $port; then
        echo $port
        return 0
    fi
    
    log_warning "Porta $port está em uso. Procurando porta alternativa..."
    
    for ((i=$port+1; i<=$port+10; i++)); do
        if check_port_availability $i; then
            log_info "Porta alternativa encontrada: $i"
            echo $i
            return 0
        fi
    done
    
    log_error "Nenhuma porta disponível encontrada no range $port-$((port+10))"
    exit 1
}

# Limpar cache se necessário
clear_cache() {
    if [[ "$1" == "--clear-cache" ]] || [[ "$CACHE_ENABLED" == "False" ]]; then
        log_info "Limpando cache do Streamlit..."
        
        # Limpar cache do Streamlit
        python -c "
import streamlit as st
try:
    st.cache_data.clear()
    print('✓ Cache de dados limpo')
except:
    print('⚠ Não foi possível limpar cache de dados')
"
        
        # Limpar arquivos temporários
        if [[ -d "data/temp" ]]; then
            rm -rf data/temp/*
            log_info "Arquivos temporários removidos"
        fi
        
        log_success "Cache limpo"
    fi
}

# Executar aplicação
run_application() {
    local port=$(find_available_port)
    local host=${STREAMLIT_HOST:-localhost}
    
    log_info "Iniciando servidor Streamlit..."
    echo
    echo -e "${GREEN}🚀 Iniciando $PROJECT_NAME${NC}"
    echo -e "${BLUE}📱 URL Local:${NC}    http://$host:$port"
    echo -e "${BLUE}🌐 URL de Rede:${NC} http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'N/A'):$port"
    echo -e "${BLUE}👤 Login Padrão:${NC} admin@petcare.com / admin123"
    echo -e "${BLUE}📝 Logs:${NC}        $LOG_FILE"
    echo
    echo -e "${YELLOW}Pressione Ctrl+C para parar o servidor${NC}"
    echo
    
    # Argumentos do Streamlit baseados no ambiente
    local streamlit_args="app.py"
    streamlit_args="$streamlit_args --server.port $port"
    streamlit_args="$streamlit_args --server.address $host"
    streamlit_args="$streamlit_args --server.headless true"
    streamlit_args="$streamlit_args --server.enableCORS false"
    streamlit_args="$streamlit_args --server.enableXsrfProtection true"
    
    # Configurações específicas do ambiente
    if [[ "$STREAMLIT_ENV" == "development" ]]; then
        streamlit_args="$streamlit_args --server.runOnSave true"
        streamlit_args="$streamlit_args --server.allowRunOnSave true"
        log_info "Modo de desenvolvimento: Hot reload ativado"
    fi
    
    if [[ "$DEBUG" == "True" ]]; then
        streamlit_args="$streamlit_args --logger.level debug"
        log_info "Modo debug ativado"
    fi
    
    # Registrar início da aplicação
    log_success "Servidor iniciado em http://$host:$port"
    
    # Executar Streamlit
    exec streamlit run $streamlit_args
}

# Lidar com sinais do sistema
setup_signal_handlers() {
    # Função para cleanup ao receber SIGINT (Ctrl+C)
    cleanup() {
        echo
        log_info "Recebido sinal de interrupção..."
        log_info "Encerrando aplicação..."
        
        # Tentar encerrar processos Streamlit em execução
        if command -v pkill &> /dev/null; then
            pkill -f "streamlit run" 2>/dev/null || true
        fi
        
        log_success "Aplicação encerrada"
        exit 0
    }
    
    # Registrar handler para SIGINT
    trap cleanup SIGINT SIGTERM
}

# Mostrar informações de sistema
show_system_info() {
    if [[ "$1" == "--system-info" ]]; then
        echo -e "${BLUE}Informações do Sistema:${NC}"
        echo "• OS: $(uname -s) $(uname -r)"
        echo "• Python: $(python --version 2>&1)"
        echo "• Streamlit: $(streamlit version 2>&1 | head -1)"
        echo "• Diretório: $(pwd)"
        echo "• Ambiente Virtual: ${VIRTUAL_ENV:-'Não ativado'}"
        echo "• Usuário: $(whoami)"
        echo "• Data/Hora: $(date)"
        echo
    fi
}

# Verificar saúde da aplicação
health_check() {
    if [[ "$1" == "--health-check" ]]; then
        log_info "Executando verificação de saúde..."
        
        local health_score=0
        local max_score=5
        
        # Verificar arquivos essenciais
        if [[ -f "app.py" ]]; then
            ((health_score++))
            echo "✓ Aplicação principal encontrada"
        else
            echo "✗ Aplicação principal não encontrada"
        fi
        
        # Verificar ambiente virtual
        if [[ -n "$VIRTUAL_ENV" ]]; then
            ((health_score++))
            echo "✓ Ambiente virtual ativo"
        else
            echo "✗ Ambiente virtual não ativo"
        fi
        
        # Verificar configuração
        if [[ -f ".env" ]]; then
            ((health_score++))
            echo "✓ Arquivo de configuração encontrado"
        else
            echo "✗ Arquivo de configuração não encontrado"
        fi
        
        # Verificar dependências críticas
        if python -c "import streamlit, pandas, supabase" 2>/dev/null; then
            ((health_score++))
            echo "✓ Dependências críticas instaladas"
        else
            echo "✗ Dependências críticas faltando"
        fi
        
        # Verificar conectividade
        if python -c "
import os
from supabase import create_client
client = create_client(os.getenv('SUPABASE_URL', ''), os.getenv('SUPABASE_ANON_KEY', ''))
client.table('users_analytics').select('id').limit(1).execute()
" 2>/dev/null; then
            ((health_score++))
            echo "✓ Conectividade com banco de dados"
        else
            echo "✗ Problemas de conectividade com banco"
        fi
        
        # Resultado
        local health_percentage=$((health_score * 100 / max_score))
        echo
        echo "Pontuação de Saúde: $health_score/$max_score ($health_percentage%)"
        
        if [[ $health_percentage -ge 80 ]]; then
            echo -e "${GREEN}✅ Sistema saudável${NC}"
            exit 0
        elif [[ $health_percentage -ge 60 ]]; then
            echo -e "${YELLOW}⚠️  Sistema com problemas menores${NC}"
            exit 1
        else
            echo -e "${RED}❌ Sistema com problemas críticos${NC}"
            exit 2
        fi
    fi
}

# Menu de opções de execução
show_run_menu() {
    echo "======================================"
    echo "  $PROJECT_NAME - Opções de Execução"
    echo "======================================"
    echo
    echo "1) Executar aplicação (modo normal)"
    echo "2) Executar em modo de desenvolvimento"
    echo "3) Executar com cache limpo"
    echo "4) Verificação de saúde do sistema"
    echo "5) Mostrar informações do sistema"
    echo "6) Executar testes"
    echo "q) Sair"
    echo
    read -p "Escolha uma opção [1-6,q]: " choice
    
    case $choice in
        1) run_normal ;;
        2) run_development ;;
        3) run_clean ;;
        4) health_check --health-check ;;
        5) show_system_info --system-info ;;
        6) run_tests ;;
        q|Q) exit 0 ;;
        *) echo "Opção inválida"; show_run_menu ;;
    esac
}

# Modos de execução
run_normal() {
    log_info "Executando em modo normal..."
    run_application
}

run_development() {
    log_info "Executando em modo de desenvolvimento..."
    export STREAMLIT_ENV=development
    export DEBUG=True
    run_application
}

run_clean() {
    log_info "Executando com cache limpo..."
    clear_cache --clear-cache
    run_application
}

run_tests() {
    log_info "Executando testes..."
    if [[ -f "test.sh" ]]; then
        ./test.sh
    else
        python -c "
print('🧪 Executando testes básicos...')
try:
    import streamlit, pandas, numpy, plotly, supabase
    print('✅ Importações: OK')
    
    import os
    if os.path.exists('.env'):
        print('✅ Configuração: OK')
    else:
        print('❌ Configuração: FALHA')
        
    print('✅ Testes concluídos')
except Exception as e:
    print(f'❌ Erro nos testes: {e}')
"
    fi
}

# Função principal
main() {
    # Configurar handlers de sinal
    setup_signal_handlers
    
    # Processar argumentos da linha de comando
    case "${1:-}" in
        --help|-h)
            echo "Uso: $0 [opção]"
            echo
            echo "Opções:"
            echo "  --help, -h          Mostrar esta ajuda"
            echo "  --normal            Executar em modo normal"
            echo "  --dev               Executar em modo de desenvolvimento"
            echo "  --clean             Executar com cache limpo"
            echo "  --health-check      Verificação de saúde"
            echo "  --system-info       Informações do sistema"
            echo "  --test              Executar testes"
            echo "  --port PORT         Especificar porta personalizada"
            echo "  --host HOST         Especificar host personalizado"
            echo
            exit 0
            ;;
        --normal)
            show_banner
            check_prerequisites
            activate_environment
            load_environment_variables
            check_python_dependencies
            test_database_connection
            run_normal
            ;;
        --dev)
            show_banner
            check_prerequisites
            activate_environment
            load_environment_variables
            check_python_dependencies
            test_database_connection
            run_development
            ;;
        --clean)
            show_banner
            check_prerequisites
            activate_environment
            load_environment_variables
            check_python_dependencies
            test_database_connection
            run_clean
            ;;
        --health-check)
            check_prerequisites
            activate_environment
            load_environment_variables
            health_check --health-check
            ;;
        --system-info)
            activate_environment
            load_environment_variables
            show_system_info --system-info
            ;;
        --test)
            check_prerequisites
            activate_environment
            load_environment_variables
            run_tests
            ;;
        --port)
            if [[ -n "$2" ]]; then
                export STREAMLIT_PORT="$2"
                shift 2
                main --normal
            else
                log_error "Porta não especificada"
                exit 1
            fi
            ;;
        --host)
            if [[ -n "$2" ]]; then
                export STREAMLIT_HOST="$2"
                shift 2
                main --normal
            else
                log_error "Host não especificado"
                exit 1
            fi
            ;;
        "")
            show_banner
            check_prerequisites
            activate_environment
            load_environment_variables
            check_python_dependencies
            test_database_connection
            
            # Se em modo interativo, mostrar menu
            if [[ -t 0 ]]; then
                show_run_menu
            else
                run_normal
            fi
            ;;
        *)
            log_error "Opção inválida: $1"
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@" "
