#!/bin/bash

# PetCareAI Analytics - Script de Configuração
# Versão: 2.0.0
# Data: 29/06/2025

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="PetCareAI Analytics"
CONFIG_FILE=".env"
STREAMLIT_CONFIG_DIR="$HOME/.streamlit"
VENV_NAME="petcare-venv"

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Verificar se o ambiente virtual existe
check_virtual_environment() {
    if [[ ! -d "$VENV_NAME" ]]; then
        log_error "Ambiente virtual não encontrado. Execute install.sh primeiro."
        exit 1
    fi
    
    # Ativar ambiente virtual
    source "$VENV_NAME/bin/activate" 2>/dev/null || source "$VENV_NAME/Scripts/activate"
    log_success "Ambiente virtual ativado"
}

# Configurar variáveis de ambiente
configure_environment() {
    log_step "Configurando variáveis de ambiente..."
    
    echo "======================================"
    echo "  Configuração de Variáveis de Ambiente"
    echo "======================================"
    echo
    
    # Backup do arquivo existente
    if [[ -f "$CONFIG_FILE" ]]; then
        cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "Backup criado: ${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Configuração do Supabase
    echo -e "${BLUE}Configuração do Supabase:${NC}"
    echo "Para obter essas informações:"
    echo "1. Acesse https://supabase.com"
    echo "2. Crie/acesse seu projeto"
    echo "3. Vá em Settings > API"
    echo
    
    read -p "SUPABASE_URL: " supabase_url
    read -p "SUPABASE_ANON_KEY: " supabase_key
    
    # Configuração do ambiente
    echo
    echo -e "${BLUE}Configuração do Ambiente:${NC}"
    echo "1) Desenvolvimento (development)"
    echo "2) Produção (production)"
    echo "3) Teste (testing)"
    read -p "Escolha o ambiente [1-3]: " env_choice
    
    case $env_choice in
        1) environment="development"; debug="True"; cache="False" ;;
        2) environment="production"; debug="False"; cache="True" ;;
        3) environment="testing"; debug="True"; cache="False" ;;
        *) environment="development"; debug="True"; cache="False" ;;
    esac
    
    # Configurações opcionais
    echo
    echo -e "${BLUE}Configurações Opcionais (pressione Enter para pular):${NC}"
    read -p "Google Maps API Key: " google_maps_key
    read -p "OpenAI API Key: " openai_key
    read -p "Porta do Streamlit [8501]: " streamlit_port
    streamlit_port=${streamlit_port:-8501}
    
    # Criar arquivo .env
    cat > "$CONFIG_FILE" << EOF
# ====================================
# PetCareAI Analytics - Configurações
# Gerado automaticamente em $(date)
# ====================================

# ========================================
# CONFIGURAÇÕES DO SUPABASE (OBRIGATÓRIO)
# ========================================
SUPABASE_URL=$supabase_url
SUPABASE_ANON_KEY=$supabase_key

# ========================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ========================================
STREAMLIT_ENV=$environment
DEBUG=$debug
CACHE_ENABLED=$cache

# ========================================
# CONFIGURAÇÕES DO SERVIDOR
# ========================================
STREAMLIT_PORT=$streamlit_port
FORCE_HTTPS=False
SESSION_TIMEOUT=3600

# ========================================
# CONFIGURAÇÕES OPCIONAIS
# ========================================
GOOGLE_MAPS_API_KEY=$google_maps_key
OPENAI_API_KEY=$openai_key

# ========================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ========================================
LOG_LEVEL=INFO
ENABLE_PROFILING=False
MAX_UPLOAD_SIZE=10

# ========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ========================================
MIN_PASSWORD_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=1800

# ========================================
# CONFIGURAÇÕES DE CACHE
# ========================================
CACHE_TTL=3600
CACHE_MAX_SIZE=100

# ========================================
# CONFIGURAÇÕES DE BACKUP
# ========================================
AUTO_BACKUP=True
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 3 * * *"
EOF
    
    log_success "Arquivo .env criado com sucesso"
}

# Configurar Streamlit
configure_streamlit() {
    log_step "Configurando Streamlit..."
    
    # Criar diretório de configuração
    mkdir -p "$STREAMLIT_CONFIG_DIR"
    
    echo "======================================"
    echo "  Configuração do Streamlit"
    echo "======================================"
    echo
    
    # Escolher tema
    echo -e "${BLUE}Escolha o tema:${NC}"
    echo "1) Tema Padrão (Verde)"
    echo "2) Tema Escuro"
    echo "3) Tema Claro"
    echo "4) Personalizado"
    read -p "Escolha [1-4]: " theme_choice
    
    case $theme_choice in
        1)
            primary_color="#4CAF50"
            bg_color="#FFFFFF"
            secondary_bg="#F0F2F6"
            text_color="#262730"
            ;;
        2)
            primary_color="#FF6B6B"
            bg_color="#0E1117"
            secondary_bg="#262730"
            text_color="#FAFAFA"
            ;;
        3)
            primary_color="#1F77B4"
            bg_color="#FFFFFF"
            secondary_bg="#F0F2F6"
            text_color="#262730"
            ;;
        4)
            read -p "Cor primária (hex): " primary_color
            read -p "Cor de fundo (hex): " bg_color
            read -p "Cor de fundo secundária (hex): " secondary_bg
            read -p "Cor do texto (hex): " text_color
            ;;
        *)
            primary_color="#4CAF50"
            bg_color="#FFFFFF"
            secondary_bg="#F0F2F6"
            text_color="#262730"
            ;;
    esac
    
    # Configurações avançadas
    echo
    echo -e "${BLUE}Configurações Avançadas:${NC}"
    read -p "Habilitar coleta de estatísticas? [y/N]: " gather_stats
    read -p "Habilitar modo de desenvolvimento? [y/N]: " dev_mode
    read -p "Porta personalizada [$streamlit_port]: " custom_port
    custom_port=${custom_port:-$streamlit_port}
    
    gather_stats_bool=$([ "$gather_stats" = "y" ] && echo "true" || echo "false")
    dev_mode_bool=$([ "$dev_mode" = "y" ] && echo "true" || echo "false")
    
    # Criar arquivo de configuração
    cat > "$STREAMLIT_CONFIG_DIR/config.toml" << EOF
# ====================================
# Streamlit Configuration
# PetCareAI Analytics
# ====================================

[global]
developmentMode = $dev_mode_bool
showWarningOnDirectExecution = false

[server]
headless = true
port = $custom_port
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 10
maxMessageSize = 200

[browser]
gatherUsageStats = $gather_stats_bool

[theme]
primaryColor = "$primary_color"
backgroundColor = "$bg_color"
secondaryBackgroundColor = "$secondary_bg"
textColor = "$text_color"
font = "sans serif"

[client]
caching = true
displayEnabled = true
showErrorDetails = true

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true

[logger]
level = "info"
messageFormat = "%(asctime)s.%(msecs)03d %(name)s: %(levelname)s: %(message)s"
EOF
    
    # Configuração de secrets (se necessário)
    if [[ -n "$supabase_url" ]] && [[ -n "$supabase_key" ]]; then
        cat > "$STREAMLIT_CONFIG_DIR/secrets.toml" << EOF
# ====================================
# Streamlit Secrets
# PetCareAI Analytics
# ====================================

[supabase]
SUPABASE_URL = "$supabase_url"
SUPABASE_ANON_KEY = "$supabase_key"

[api_keys]
GOOGLE_MAPS = "$google_maps_key"
OPENAI = "$openai_key"
EOF
        
        # Proteger arquivo de secrets
        chmod 600 "$STREAMLIT_CONFIG_DIR/secrets.toml"
        log_success "Arquivo de secrets criado e protegido"
    fi
    
    log_success "Streamlit configurado com sucesso"
}

# Configurar banco de dados
configure_database() {
    log_step "Configurando banco de dados..."
    
    echo "======================================"
    echo "  Configuração do Banco de Dados"
    echo "======================================"
    echo
    
    if [[ -z "$supabase_url" ]] || [[ -z "$supabase_key" ]]; then
        log_error "Configurações do Supabase não encontradas."
        return 1
    fi
    
    # Testar conexão
    log_info "Testando conexão com Supabase..."
    
    python3 -c "
import os
from supabase import create_client

# Carregar variáveis de ambiente
url = '$supabase_url'
key = '$supabase_key'

try:
    client = create_client(url, key)
    # Testar conexão simples
    result = client.table('users_analytics').select('id').limit(1).execute()
    print('✓ Conexão com Supabase estabelecida com sucesso')
except Exception as e:
    print(f'✗ Erro na conexão: {e}')
    exit(1)
" || {
        log_error "Falha na conexão com Supabase. Verifique as credenciais."
        return 1
    }
    
    # Criar diretórios locais
    mkdir -p data/{temp,cache,exports,backups}
    mkdir -p models/{saved,temp}
    mkdir -p assets/{images,documents}
    
    log_success "Estrutura de diretórios criada"
    log_success "Banco de dados configurado com sucesso"
}

# Configurar logging
configure_logging() {
    log_step "Configurando sistema de logs..."
    
    # Criar diretório de logs
    mkdir -p logs
    
    # Configuração de logging Python
    cat > logging_config.ini << EOF
[loggers]
keys=root,petcare

[handlers]
keys=consoleHandler,fileHandler,rotatingHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_petcare]
level=DEBUG
handlers=consoleHandler,rotatingHandler
qualname=petcare
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/petcare.log',)

[handler_rotatingHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/petcare.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
EOF
    
    log_success "Sistema de logs configurado"
}

# Configurar scripts auxiliares
configure_scripts() {
    log_step "Configurando scripts auxiliares..."
    
    # Script de execução com configurações
    cat > run.sh << EOF
#!/bin/bash

# PetCareAI Analytics - Script de Execução
# Configurado automaticamente

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "\${GREEN}🐾 Iniciando PetCareAI Analytics...\${NC}"

# Verificar ambiente virtual
if [[ ! -d "$VENV_NAME" ]]; then
    echo -e "\${RED}❌ Ambiente virtual não encontrado. Execute install.sh primeiro.\${NC}"
    exit 1
fi

# Ativar ambiente virtual
source $VENV_NAME/bin/activate 2>/dev/null || source $VENV_NAME/Scripts/activate

# Verificar arquivo .env
if [[ ! -f ".env" ]]; then
    echo -e "\${RED}❌ Arquivo .env não encontrado. Execute configure.sh primeiro.\${NC}"
    exit 1
fi

# Carregar variáveis de ambiente
export \$(cat .env | grep -v '^#' | grep -v '^\s*\$' | xargs)

# Verificar dependências críticas
python -c "
try:
    import streamlit, pandas, numpy, plotly, supabase
    print('✓ Dependências verificadas')
except ImportError as e:
    print(f'❌ Dependência faltando: {e}')
    exit(1)
"

# Executar aplicação
echo -e "\${GREEN}🚀 Iniciando servidor Streamlit...\${NC}"
echo "📱 Acesse: http://localhost:\${STREAMLIT_PORT:-8501}"
echo "👤 Login padrão: admin@petcare.com / admin123"
echo

streamlit run app.py --server.port \${STREAMLIT_PORT:-8501}
EOF
    
    # Script de desenvolvimento
    cat > dev.sh << EOF
#!/bin/bash

# Script de desenvolvimento com hot reload

source $VENV_NAME/bin/activate 2>/dev/null || source $VENV_NAME/Scripts/activate
export \$(cat .env | grep -v '^#' | grep -v '^\s*\$' | xargs)

echo "🔧 Modo de desenvolvimento ativado"
echo "📁 Monitorando mudanças nos arquivos..."

streamlit run app.py --server.runOnSave true --server.port \${STREAMLIT_PORT:-8501}
EOF
    
    # Script de teste
    cat > test.sh << EOF
#!/bin/bash

# Script de testes

source $VENV_NAME/bin/activate 2>/dev/null || source $VENV_NAME/Scripts/activate

echo "🧪 Executando testes..."

# Testes básicos
python -c "
import sys
import importlib.util

def test_imports():
    required_modules = [
        'streamlit', 'pandas', 'numpy', 'plotly', 
        'scikit-learn', 'supabase', 'python-dotenv'
    ]
    
    failed = []
    for module in required_modules:
        try:
            if module == 'python-dotenv':
                importlib.import_module('dotenv')
            elif module == 'scikit-learn':
                importlib.import_module('sklearn')
            else:
                importlib.import_module(module)
            print(f'✓ {module}')
        except ImportError:
            print(f'✗ {module}')
            failed.append(module)
    
    return len(failed) == 0

def test_config():
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'SUPABASE_URL' in content and 'SUPABASE_ANON_KEY' in content:
                print('✓ Configuração .env')
                return True
            else:
                print('✗ Configuração .env incompleta')
                return False
    except FileNotFoundError:
        print('✗ Arquivo .env não encontrado')
        return False

if test_imports() and test_config():
    print('\\n✅ Todos os testes passaram!')
    sys.exit(0)
else:
    print('\\n❌ Alguns testes falharam')
    sys.exit(1)
"
EOF
    
    # Tornar scripts executáveis
    chmod +x run.sh dev.sh test.sh
    
    log_success "Scripts auxiliares configurados"
}

# Validar configuração
validate_configuration() {
    log_step "Validando configuração..."
    
    local errors=0
    
    # Verificar arquivo .env
    if [[ ! -f ".env" ]]; then
        log_error "Arquivo .env não encontrado"
        ((errors++))
    else
        # Verificar variáveis obrigatórias
        if ! grep -q "SUPABASE_URL=" .env; then
            log_error "SUPABASE_URL não configurado"
            ((errors++))
        fi
        
        if ! grep -q "SUPABASE_ANON_KEY=" .env; then
            log_error "SUPABASE_ANON_KEY não configurado"
            ((errors++))
        fi
    fi
    
    # Verificar configuração do Streamlit
    if [[ ! -f "$STREAMLIT_CONFIG_DIR/config.toml" ]]; then
        log_error "Configuração do Streamlit não encontrada"
        ((errors++))
    fi
    
    # Verificar estrutura de diretórios
    local required_dirs=("data" "models" "assets" "logs")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Diretório obrigatório não encontrado: $dir"
            ((errors++))
        fi
    done
    
    # Verificar scripts
    local required_scripts=("run.sh" "dev.sh" "test.sh")
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "$script" ]]; then
            log_error "Script não encontrado: $script"
            ((errors++))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        log_success "Configuração validada com sucesso"
        return 0
    else
        log_error "Encontrados $errors erros na configuração"
        return 1
    fi
}

# Exibir informações finais
show_configuration_summary() {
    echo
    echo "======================================"
    echo -e "${GREEN}🎉 CONFIGURAÇÃO CONCLUÍDA! 🎉${NC}"
    echo "======================================"
    echo
    echo -e "${BLUE}Resumo da Configuração:${NC}"
    echo "• Ambiente: $(grep STREAMLIT_ENV .env | cut -d'=' -f2)"
    echo "• Porta: $(grep STREAMLIT_PORT .env | cut -d'=' -f2)"
    echo "• Debug: $(grep DEBUG .env | cut -d'=' -f2)"
    echo "• Cache: $(grep CACHE_ENABLED .env | cut -d'=' -f2)"
    echo
    echo -e "${BLUE}Próximos Passos:${NC}"
    echo "1. Execute: ./test.sh (para testar a configuração)"
    echo "2. Execute: ./run.sh (para iniciar a aplicação)"
    echo "3. Acesse: http://localhost:$(grep STREAMLIT_PORT .env | cut -d'=' -f2)"
    echo
    echo -e "${BLUE}Scripts Disponíveis:${NC}"
    echo "• ./run.sh    - Executar aplicação"
    echo "• ./dev.sh    - Modo de desenvolvimento"
    echo "• ./test.sh   - Executar testes"
    echo "• ./backup.sh - Criar backup"
    echo
    echo -e "${YELLOW}Importante:${NC}"
    echo "• Login padrão: admin@petcare.com / admin123"
    echo "• Configure usuários adicionais no painel administrativo"
    echo "• Faça backup regular dos dados importantes"
    echo
}

# Menu principal
show_menu() {
    echo "======================================"
    echo "  $PROJECT_NAME - Configurador v2.0.0"
    echo "======================================"
    echo
    echo "Opções de configuração:"
    echo "1) Configuração completa (recomendado)"
    echo "2) Apenas variáveis de ambiente"
    echo "3) Apenas Streamlit"
    echo "4) Apenas banco de dados"
    echo "5) Apenas scripts auxiliares"
    echo "6) Validar configuração atual"
    echo "7) Reconfigurar tudo"
    echo "q) Sair"
    echo
    read -p "Escolha uma opção [1-7,q]: " choice
    
    case $choice in
        1) full_configuration ;;
        2) configure_environment ;;
        3) configure_streamlit ;;
        4) configure_database ;;
        5) configure_scripts ;;
        6) validate_configuration ;;
        7) reconfigure_all ;;
        q|Q) exit 0 ;;
        *) echo "Opção inválida"; show_menu ;;
    esac
}

# Configuração completa
full_configuration() {
    log_info "Iniciando configuração completa..."
    
    check_virtual_environment
    configure_environment
    configure_streamlit
    configure_database
    configure_logging
    configure_scripts
    
    if validate_configuration; then
        show_configuration_summary
    else
        log_error "Configuração incompleta. Revise os erros acima."
        exit 1
    fi
}

# Reconfigurar tudo
reconfigure_all() {
    log_warning "Isso irá sobrescrever todas as configurações existentes."
    read -p "Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup de configurações existentes
        if [[ -f ".env" ]]; then
            cp ".env" ".env.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        
        full_configuration
    else
        log_info "Operação cancelada"
    fi
}

# Função principal
main() {
    case "${1:-}" in
        --help|-h)
            echo "Uso: $0 [opção]"
            echo
            echo "Opções:"
            echo "  --help, -h        Mostrar esta ajuda"
            echo "  --full            Configuração completa"
            echo "  --env             Apenas variáveis de ambiente"
            echo "  --streamlit       Apenas Streamlit"
            echo "  --database        Apenas banco de dados"
            echo "  --scripts         Apenas scripts"
            echo "  --validate        Validar configuração"
            echo
            exit 0
            ;;
        --full)
            check_virtual_environment
            full_configuration
            ;;
        --env)
            check_virtual_environment
            configure_environment
            ;;
        --streamlit)
            configure_streamlit
            ;;
        --database)
            check_virtual_environment
            configure_database
            ;;
        --scripts)
            configure_scripts
            ;;
        --validate)
            validate_configuration
            ;;
        "")
            show_menu
            ;;
        *)
            log_error "Opção inválida: $1"
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
