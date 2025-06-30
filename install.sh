#!/bin/bash

# PetCareAI Analytics - Script de Instalação
# Versão: 2.0.0
# Data: 29/06/2025

set -e  # Exit on any error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="PetCareAI Analytics"
PYTHON_MIN_VERSION="3.8"
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

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Este script não deve ser executado como root para instalação local."
        log_info "Para instalação global, use: sudo -E $0 --global"
        read -p "Continuar mesmo assim? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Verificar sistema operacional
check_os() {
    log_info "Verificando sistema operacional..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
        log_info "Sistema: Linux ($DISTRO)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Sistema: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        log_info "Sistema: Windows (WSL/Cygwin)"
    else
        log_error "Sistema operacional não suportado: $OSTYPE"
        exit 1
    fi
}

# Verificar dependências do sistema
check_system_dependencies() {
    log_info "Verificando dependências do sistema..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python não encontrado. Instale Python $PYTHON_MIN_VERSION ou superior."
        exit 1
    fi
    
    # Verificar versão do Python
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION=$PYTHON_MIN_VERSION
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$REQUIRED_VERSION'.split('.'))) else 1)" 2>/dev/null; then
        log_error "Python $PYTHON_MIN_VERSION+ requerido. Versão atual: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION encontrado"
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_error "pip não encontrado. Instale python3-pip."
        exit 1
    fi
    
    # Verificar git
    if ! command -v git &> /dev/null; then
        log_warning "Git não encontrado. Algumas funcionalidades podem não funcionar."
    fi
    
    # Verificar curl/wget para downloads
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        log_error "curl ou wget requerido para downloads."
        exit 1
    fi
}

# Instalar dependências do sistema baseado na distribuição
install_system_packages() {
    log_info "Instalando dependências do sistema..."
    
    case $OS in
        "linux")
            case $DISTRO in
                "Ubuntu"|"Debian")
                    sudo apt-get update
                    sudo apt-get install -y python3-pip python3-venv python3-dev build-essential
                    sudo apt-get install -y libpq-dev postgresql-client  # Para PostgreSQL
                    sudo apt-get install -y pkg-config libhdf5-dev  # Para ciência de dados
                    ;;
                "CentOS"|"RedHat"|"Fedora")
                    if command -v dnf &> /dev/null; then
                        sudo dnf install -y python3-pip python3-devel gcc gcc-c++ make
                        sudo dnf install -y postgresql-devel libpq-devel
                    else
                        sudo yum install -y python3-pip python3-devel gcc gcc-c++ make
                        sudo yum install -y postgresql-devel libpq-devel
                    fi
                    ;;
                *)
                    log_warning "Distribuição Linux não reconhecida. Pode ser necessário instalar dependências manualmente."
                    ;;
            esac
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install python@3.10 postgresql
            else
                log_warning "Homebrew não encontrado. Instale manualmente as dependências."
            fi
            ;;
        "windows")
            log_info "No Windows, certifique-se de ter o Visual C++ Build Tools instalado."
            ;;
    esac
}

# Criar ambiente virtual
create_virtual_environment() {
    log_info "Criando ambiente virtual..."
    
    if [[ -d "$VENV_NAME" ]]; then
        log_warning "Ambiente virtual já existe. Removendo..."
        rm -rf "$VENV_NAME"
    fi
    
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    # Ativar ambiente virtual
    source "$VENV_NAME/bin/activate" || source "$VENV_NAME/Scripts/activate"
    
    # Atualizar pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Ambiente virtual criado e ativado"
}

# Instalar dependências Python
install_python_dependencies() {
    log_info "Instalando dependências Python..."
    
    # Verificar se requirements.txt existe
    if [[ ! -f "requirements.txt" ]]; then
        log_error "Arquivo requirements.txt não encontrado."
        exit 1
    fi
    
    # Instalar dependências básicas primeiro
    pip install --upgrade pip wheel setuptools
    
    # Instalar dependências principais
    pip install -r requirements.txt
    
    # Verificar instalação crítica
    python -c "import streamlit, pandas, numpy, plotly" 2>/dev/null || {
        log_error "Falha na instalação de dependências críticas."
        exit 1
    }
    
    log_success "Dependências Python instaladas com sucesso"
}

# Configurar banco de dados
setup_database() {
    log_info "Configurando banco de dados..."
    
    # Verificar se .env existe
    if [[ ! -f ".env" ]]; then
        log_warning "Arquivo .env não encontrado. Criando template..."
        cat > .env << EOF
# Configurações do Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Configurações da aplicação
STREAMLIT_ENV=development
DEBUG=True
CACHE_ENABLED=False

# Configurações opcionais
GOOGLE_MAPS_API_KEY=
OPENAI_API_KEY=
EOF
        log_warning "Configure as variáveis de ambiente em .env antes de executar a aplicação."
    fi
    
    # Criar diretórios necessários
    mkdir -p data models exports assets
    
    log_success "Configuração do banco de dados concluída"
}

# Configurar Streamlit
setup_streamlit() {
    log_info "Configurando Streamlit..."
    
    # Criar diretório de configuração
    mkdir -p ~/.streamlit
    
    # Configuração básica do Streamlit
    cat > ~/.streamlit/config.toml << EOF
[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOF

    log_success "Streamlit configurado"
}

# Verificar instalação
verify_installation() {
    log_info "Verificando instalação..."
    
    # Testar importações Python
    python -c "
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client
print('✓ Todas as dependências principais importadas com sucesso')
"
    
    # Verificar estrutura de arquivos
    local required_files=("app.py" "requirements.txt" "config/database.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Arquivo obrigatório não encontrado: $file"
            exit 1
        fi
    done
    
    log_success "Verificação da instalação concluída com sucesso"
}

# Criar scripts auxiliares
create_helper_scripts() {
    log_info "Criando scripts auxiliares..."
    
    # Script de execução
    cat > run.sh << 'EOF'
#!/bin/bash
source petcare-venv/bin/activate || source petcare-venv/Scripts/activate
streamlit run app.py
EOF
    chmod +x run.sh
    
    # Script de backup
    cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp -r data exports models "backups/backup_$DATE"
echo "Backup criado em backups/backup_$DATE"
EOF
    chmod +x backup.sh
    
    # Script de atualização
    cat > update.sh << 'EOF'
#!/bin/bash
source petcare-venv/bin/activate || source petcare-venv/Scripts/activate
pip install --upgrade -r requirements.txt
echo "Dependências atualizadas"
EOF
    chmod +x update.sh
    
    log_success "Scripts auxiliares criados"
}

# Exibir informações finais
show_final_info() {
    echo
    echo "======================================"
    echo -e "${GREEN}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉${NC}"
    echo "======================================"
    echo
    echo -e "${BLUE}Próximos passos:${NC}"
    echo "1. Configure as variáveis de ambiente em .env"
    echo "2. Execute: source $VENV_NAME/bin/activate"
    echo "3. Execute: streamlit run app.py"
    echo "   OU use: ./run.sh"
    echo
    echo -e "${BLUE}Scripts disponíveis:${NC}"
    echo "• ./run.sh       - Executar aplicação"
    echo "• ./backup.sh    - Criar backup"
    echo "• ./update.sh    - Atualizar dependências"
    echo
    echo -e "${BLUE}Documentação:${NC}"
    echo "• README.md      - Guia geral"
    echo "• requisitos.md  - Requisitos detalhados"
    echo "• configure.sh   - Script de configuração"
    echo
    echo -e "${YELLOW}Importante:${NC}"
    echo "• Configure SUPABASE_URL e SUPABASE_ANON_KEY em .env"
    echo "• A aplicação estará disponível em http://localhost:8501"
    echo "• Login padrão: admin@petcare.com / admin123"
    echo
}

# Menu de opções
show_menu() {
    echo "======================================"
    echo "  $PROJECT_NAME - Instalador v2.0.0"
    echo "======================================"
    echo
    echo "Opções de instalação:"
    echo "1) Instalação completa (recomendado)"
    echo "2) Apenas dependências Python"
    echo "3) Apenas configuração"
    echo "4) Verificar sistema"
    echo "5) Desinstalar"
    echo "q) Sair"
    echo
    read -p "Escolha uma opção [1-5,q]: " choice
    
    case $choice in
        1) full_installation ;;
        2) python_only_installation ;;
        3) configuration_only ;;
        4) system_check ;;
        5) uninstall ;;
        q|Q) exit 0 ;;
        *) echo "Opção inválida"; show_menu ;;
    esac
}

# Instalação completa
full_installation() {
    log_info "Iniciando instalação completa..."
    
    check_os
    check_system_dependencies
    
    if [[ "$1" != "--skip-system" ]]; then
        install_system_packages
    fi
    
    create_virtual_environment
    install_python_dependencies
    setup_database
    setup_streamlit
    create_helper_scripts
    verify_installation
    show_final_info
}

# Instalação apenas Python
python_only_installation() {
    log_info "Instalando apenas dependências Python..."
    
    check_system_dependencies
    create_virtual_environment
    install_python_dependencies
    verify_installation
    
    log_success "Dependências Python instaladas"
}

# Apenas configuração
configuration_only() {
    log_info "Executando apenas configuração..."
    
    setup_database
    setup_streamlit
    create_helper_scripts
    
    log_success "Configuração concluída"
}

# Verificação do sistema
system_check() {
    log_info "Verificando sistema..."
    
    check_os
    check_system_dependencies
    
    if [[ -f "$VENV_NAME/bin/activate" ]] || [[ -f "$VENV_NAME/Scripts/activate" ]]; then
        log_success "Ambiente virtual encontrado"
        source "$VENV_NAME/bin/activate" 2>/dev/null || source "$VENV_NAME/Scripts/activate"
        
        python -c "
import sys
print(f'Python: {sys.version}')
try:
    import streamlit, pandas, numpy, plotly, supabase
    print('✓ Dependências principais: OK')
except ImportError as e:
    print(f'✗ Dependência faltando: {e}')
"
    else
        log_warning "Ambiente virtual não encontrado"
    fi
    
    if [[ -f ".env" ]]; then
        log_success "Arquivo .env encontrado"
    else
        log_warning "Arquivo .env não encontrado"
    fi
    
    if [[ -f "app.py" ]]; then
        log_success "Aplicação principal encontrada"
    else
        log_error "app.py não encontrado"
    fi
}

# Desinstalação
uninstall() {
    log_warning "Iniciando desinstalação..."
    
    read -p "Tem certeza que deseja desinstalar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Desinstalação cancelada"
        exit 0
    fi
    
    # Remover ambiente virtual
    if [[ -d "$VENV_NAME" ]]; then
        rm -rf "$VENV_NAME"
        log_success "Ambiente virtual removido"
    fi
    
    # Remover scripts auxiliares
    rm -f run.sh backup.sh update.sh
    log_success "Scripts auxiliares removidos"
    
    # Manter dados e configurações por segurança
    log_info "Dados e configurações mantidos por segurança"
    log_info "Para remoção completa, delete manualmente:"
    echo "  - data/"
    echo "  - exports/"
    echo "  - models/"
    echo "  - .env"
    
    log_success "Desinstalação concluída"
}

# Função principal
main() {
    # Verificar argumentos da linha de comando
    case "${1:-}" in
        --help|-h)
            echo "Uso: $0 [opção]"
            echo
            echo "Opções:"
            echo "  --help, -h          Mostrar esta ajuda"
            echo "  --full              Instalação completa"
            echo "  --python-only       Apenas dependências Python"
            echo "  --config-only       Apenas configuração"
            echo "  --check             Verificar sistema"
            echo "  --uninstall         Desinstalar"
            echo "  --skip-system       Pular instalação de pacotes do sistema"
            echo
            exit 0
            ;;
        --full)
            check_root
            full_installation
            ;;
        --python-only)
            python_only_installation
            ;;
        --config-only)
            configuration_only
            ;;
        --check)
            system_check
            ;;
        --uninstall)
            uninstall
            ;;
        --skip-system)
            check_root
            full_installation --skip-system
            ;;
        "")
            check_root
            show_menu
            ;;
        *)
            log_error "Opção inválida: $1"
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
}

# Trap para cleanup em caso de erro
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Instalação falhou com código de saída $exit_code"
        log_info "Verifique os logs acima para detalhes do erro"
        log_info "Para suporte, acesse: https://github.com/PetCareAi/analytics/issues"
    fi
}

trap cleanup EXIT

# Executar função principal
main "$@"
