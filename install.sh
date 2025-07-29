#!/bin/bash
# Script de Instalação do PetCare Analytics
# Compatível com Linux, macOS e Windows (WSL)

set -e  # Parar execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command_exists apt-get; then
            DISTRO="ubuntu"
        elif command_exists yum; then
            DISTRO="centos"
        elif command_exists pacman; then
            DISTRO="arch"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        DISTRO="windows"
    else
        OS="unknown"
        DISTRO="unknown"
    fi
}

# Função para verificar versão mínima do Python
check_python_version() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python não encontrado. Instale Python 3.8 ou superior."
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt "3" ] || ([ "$PYTHON_MAJOR" -eq "3" ] && [ "$PYTHON_MINOR" -lt "8" ]); then
        print_error "Python 3.8 ou superior é necessário. Versão atual: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION encontrado"
}

# Função para instalar Python no Ubuntu/Debian
install_python_ubuntu() {
    print_status "Instalando Python 3.9 no Ubuntu/Debian..."
    sudo apt update
    sudo apt install -y python3.9 python3.9-pip python3.9-venv python3.9-dev
    sudo apt install -y build-essential libssl-dev libffi-dev

    # Criar links simbólicos se necessário
    if ! command_exists python3; then
        sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
    fi
}

# Função para instalar Python no CentOS/RHEL
install_python_centos() {
    print_status "Instalando Python 3.9 no CentOS/RHEL..."
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y python39 python39-pip python39-devel
    sudo yum install -y openssl-devel libffi-devel
}

# Função para instalar Python no macOS
install_python_macos() {
    if command_exists brew; then
        print_status "Instalando Python via Homebrew..."
        brew install python@3.9
        brew install pkg-config
    else
        print_warning "Homebrew não encontrado. Instale manualmente:"
        print_warning "1. Acesse https://www.python.org/downloads/"
        print_warning "2. Baixe Python 3.9 ou superior"
        print_warning "3. Execute este script novamente"
        exit 1
    fi
}

# Função para instalar dependências do sistema
install_system_dependencies() {
    print_status "Instalando dependências do sistema..."

    case $DISTRO in
        "ubuntu")
            sudo apt update
            sudo apt install -y git curl wget unzip
            sudo apt install -y libpq-dev  # Para psycopg2
            sudo apt install -y libjpeg-dev zlib1g-dev  # Para Pillow
            ;;
        "centos")
            sudo yum update -y
            sudo yum install -y git curl wget unzip
            sudo yum install -y postgresql-devel  # Para psycopg2
            sudo yum install -y libjpeg-turbo-devel zlib-devel  # Para Pillow
            ;;
        "macos")
            if command_exists brew; then
                brew install git curl wget
                brew install postgresql  # Para psycopg2
                brew install jpeg  # Para Pillow
            fi
            ;;
        *)
            print_warning "Sistema não reconhecido. Instale manualmente: git, curl, wget"
            ;;
    esac
}

# Função para criar ambiente virtual
create_virtual_environment() {
    print_status "Criando ambiente virtual Python..."

    if [ -d "venv" ]; then
        print_warning "Ambiente virtual já existe. Removendo..."
        rm -rf venv
    fi

    $PYTHON_CMD -m venv venv

    # Ativar ambiente virtual
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi

    print_success "Ambiente virtual criado e ativado"
}

# Função para atualizar pip
upgrade_pip() {
    print_status "Atualizando pip..."
    python -m pip install --upgrade pip setuptools wheel
    print_success "pip atualizado"
}

# Função para instalar dependências Python
install_python_dependencies() {
    print_status "Instalando dependências Python..."

    if [ ! -f "requirements.txt" ]; then
        print_error "Arquivo requirements.txt não encontrado!"
        exit 1
    fi

    # Instalar dependências com retry em caso de falha
    MAX_RETRIES=3
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if pip install -r requirements.txt; then
            print_success "Dependências instaladas com sucesso"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            print_warning "Tentativa $RETRY_COUNT de $MAX_RETRIES falhou. Tentando novamente..."
            sleep 2
        fi
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Falha ao instalar dependências após $MAX_RETRIES tentativas"
        exit 1
    fi
}

# Função para configurar variáveis de ambiente
setup_environment_variables() {
    print_status "Configurando variáveis de ambiente..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Arquivo .env criado a partir do exemplo"
        else
            # Criar arquivo .env básico
            cat > .env << EOF
# Configurações do Supabase
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima

# Configurações de Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app

# Configurações do Sistema
DEBUG_MODE=true
SESSION_TIMEOUT=3600
MAX_UPLOAD_SIZE=10485760

# APIs Externas (opcional)
GOOGLE_MAPS_API_KEY=sua_chave_do_google_maps
OPENAI_API_KEY=sua_chave_do_openai
EOF
            print_success "Arquivo .env básico criado"
        fi

        print_warning "IMPORTANTE: Configure suas credenciais no arquivo .env"
        print_warning "Edite o arquivo .env com suas credenciais do Supabase"
    else
        print_success "Arquivo .env já existe"
    fi
}

# Função para verificar conectividade com Supabase
test_supabase_connection() {
    print_status "Testando conectividade com Supabase..."

    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if not url or not key or 'sua_' in url or 'sua_' in key:
    print('❌ Credenciais do Supabase não configuradas no .env')
    exit(1)

try:
    from supabase import create_client
    client = create_client(url, key)
    # Teste simples de conectividade
    result = client.table('users_analytics').select('id').limit(1).execute()
    print('✅ Conexão com Supabase estabelecida')
except Exception as e:
    print(f'⚠️ Aviso: Erro na conexão com Supabase: {e}')
    print('Verifique suas credenciais no arquivo .env')
" 2>/dev/null || print_warning "Configure as credenciais do Supabase no arquivo .env"
}

# Função para criar estrutura de diretórios
create_directory_structure() {
    print_status "Criando estrutura de diretórios..."

    mkdir -p assets
    mkdir -p data
    mkdir -p models
    mkdir -p exports
    mkdir -p logs
    mkdir -p tests
    mkdir -p scripts
    mkdir -p config

    print_success "Estrutura de diretórios criada"
}

# Função para configurar scripts auxiliares
setup_scripts() {
    print_status "Configurando scripts auxiliares..."

    # Script para executar a aplicação
    cat > run.sh << 'EOF'
#!/bin/bash
# Script para executar o PetCare Analytics

# Ativar ambiente virtual
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Verificar se o .env existe
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "Configure suas credenciais primeiro"
    exit 1
fi

# Executar aplicação
echo "🚀 Iniciando PetCare Analytics..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
EOF

    chmod +x run.sh

    # Script de desenvolvimento
    cat > dev.sh << 'EOF'
#!/bin/bash
# Script para desenvolvimento

# Ativar ambiente virtual
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Executar em modo debug
echo "🔧 Iniciando em modo desenvolvimento..."
export DEBUG_MODE=true
streamlit run app.py --server.runOnSave true --server.port 8501
EOF

    chmod +x dev.sh

    print_success "Scripts auxiliares criados"
}

# Função para verificar instalação
verify_installation() {
    print_status "Verificando instalação..."

    # Verificar se Python funciona
    if ! python -c "import streamlit, pandas, numpy, plotly, supabase" 2>/dev/null; then
        print_error "Algumas dependências não foram instaladas corretamente"
        return 1
    fi

    # Verificar se arquivos principais existem
    if [ ! -f "app.py" ]; then
        print_error "Arquivo principal app.py não encontrado"
        return 1
    fi

    if [ ! -f "config/database.py" ]; then
        print_error "Arquivo de configuração database.py não encontrado"
        return 1
    fi

    print_success "Verificação concluída com sucesso"
    return 0
}

# Função para exibir informações finais
show_final_instructions() {
    echo
    echo "🎉 Instalação concluída com sucesso!"
    echo
    echo "📋 Próximos passos:"
    echo
    echo "1. Configure suas credenciais no arquivo .env:"
    echo "   nano .env"
    echo
    echo "2. Para executar a aplicação:"
    echo "   ./run.sh"
    echo "   ou"
    echo "   chmod +x run.sh && ./run.sh"
    echo
    echo "3. Para desenvolvimento:"
    echo "   ./dev.sh"
    echo
    echo "4. Acesse a aplicação em:"
    echo "   http://localhost:8501"
    echo
    echo "📚 Documentação adicional:"
    echo "   - README.md - Instruções gerais"
    echo "   - requisitos.md - Requisitos do sistema"
    echo "   - git-build-commit.md - Guia de desenvolvimento"
    echo
    print_success "PetCare Analytics pronto para uso!"
}

# Função principal
main() {
    echo "🐾 Instalação do PetCare Analytics 🐾"
    echo "===================================="
    echo

    # Detectar sistema operacional
    detect_os
    print_status "Sistema detectado: $OS ($DISTRO)"

    # Verificar Python
    if ! check_python_version; then
        case $DISTRO in
            "ubuntu")
                install_python_ubuntu
                ;;
            "centos")
                install_python_centos
                ;;
            "macos")
                install_python_macos
                ;;
            *)
                print_error "Sistema não suportado para instalação automática do Python"
                print_error "Instale Python 3.8+ manualmente e execute este script novamente"
                exit 1
                ;;
        esac
        check_python_version
    fi

    # Instalar dependências do sistema
    install_system_dependencies

    # Criar ambiente virtual
    create_virtual_environment

    # Atualizar pip
    upgrade_pip

    # Instalar dependências Python
    install_python_dependencies

    # Configurar ambiente
    setup_environment_variables

    # Criar estrutura de diretórios
    create_directory_structure

    # Configurar scripts
    setup_scripts

    # Testar conexão (opcional)
    test_supabase_connection

    # Verificar instalação
    if verify_installation; then
        show_final_instructions
    else
        print_error "Instalação incompleta. Verifique os erros acima."
        exit 1
    fi
}

# Verificar se está sendo executado como script principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
