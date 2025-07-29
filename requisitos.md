# Requisitos do Sistema - PetCare Analytics

## Visão Geral

Sistema avançado de análise e gestão de pets com inteligência artificial, desenvolvido em Python usando Streamlit para interface web e Supabase como banco de dados.

## Requisitos de Software

### Sistema Operacional
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- **Windows**: Windows 10+ / Windows Server 2016+
- **macOS**: macOS 10.14+ (Mojave)

### Python
- **Versão mínima**: Python 3.8
- **Versão recomendada**: Python 3.9 ou superior
- **Gerenciador de pacotes**: pip 21.0+

### Dependências Principais

#### Framework Web
- `streamlit >= 1.28.0` - Framework para aplicações web
- `streamlit-option-menu >= 0.3.2` - Menus customizados

#### Banco de Dados
- `supabase >= 1.0.3` - Cliente para Supabase
- `psycopg2-binary >= 2.9.0` - Driver PostgreSQL

#### Análise de Dados
- `pandas >= 1.5.0` - Manipulação de dados
- `numpy >= 1.21.0` - Computação numérica
- `scipy >= 1.9.0` - Funções científicas

#### Visualização
- `plotly >= 5.11.0` - Gráficos interativos
- `matplotlib >= 3.5.0` - Plots básicos
- `seaborn >= 0.11.0` - Visualizações estatísticas

#### Machine Learning
- `scikit-learn >= 1.1.0` - Algoritmos de ML
- `statsmodels >= 0.13.0` - Modelos estatísticos

#### Utilitários
- `python-dotenv >= 0.19.0` - Variáveis de ambiente
- `openpyxl >= 3.0.9` - Manipulação de Excel
- `xlsxwriter >= 3.0.0` - Criação de Excel
- `Pillow >= 9.0.0` - Processamento de imagens
- `textblob >= 0.17.0` - Processamento de texto
- `wordcloud >= 1.8.0` - Nuvem de palavras

### Banco de Dados

#### Supabase (Recomendado)
- **Versão**: PostgreSQL 13+
- **Recursos necessários**:
  - Autenticação de usuários
  - Storage para arquivos
  - Real-time subscriptions
  - Edge Functions (opcional)

#### Estrutura de Tabelas
```sql
-- Tabela de usuários
users_analytics (
    id, email, password_hash, full_name, role, 
    created_at, last_login, preferences, profile_data
)

-- Tabela de pets
pets_analytics (
    id, nome, tipo_pet, raca, idade, peso, sexo, bairro,
    comportamento, estado_saude, adotado, score_adocao,
    sociabilidade, energia, nivel_atividade, created_by,
    created_at, updated_at
)

-- Logs de atividade
activity_logs_analytics (
    id, user_id, action, details, session_id,
    timestamp, execution_time, ip_address
)

-- Logs de login
login_logs_analytics (
    id, user_id, success, failure_reason,
    timestamp, ip_address
)
```

## Requisitos de Hardware

### Servidor de Desenvolvimento
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Armazenamento**: 10 GB livres
- **Rede**: Conexão banda larga estável

### Servidor de Produção
- **CPU**: 4+ cores, 2.5 GHz
- **RAM**: 8 GB mínimo, 16 GB recomendado
- **Armazenamento**: 50 GB SSD
- **Rede**: 100 Mbps dedicado
- **Backup**: Storage adicional para backups

### Cliente (Navegador)
- **Navegadores suportados**:
  - Chrome 80+
  - Firefox 75+
  - Safari 13+
  - Edge 80+
- **JavaScript**: Habilitado
- **Resolução mínima**: 1024x768
- **Conexão**: 1 Mbps mínimo

## Requisitos de Rede

### Portas Necessárias
- **Aplicação**: 8501 (Streamlit padrão)
- **HTTPS**: 443 (produção)
- **HTTP**: 80 (redirecionamento)

### Conectividade Externa
- **Supabase**: Acesso à API (supabase.co)
- **CDNs**: Para bibliotecas JavaScript
- **Email**: SMTP para envio de emails

## Variáveis de Ambiente

### Obrigatórias
```bash
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima
```

### Opcionais
```bash
# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email
SMTP_PASSWORD=sua_senha

# APIs Externas
GOOGLE_MAPS_API_KEY=sua_chave_maps
OPENAI_API_KEY=sua_chave_openai

# Configurações
DEBUG_MODE=false
SESSION_TIMEOUT=3600
MAX_UPLOAD_SIZE=10485760
```

## Requisitos de Segurança

### HTTPS/TLS
- Certificado SSL válido em produção
- Redirecionamento HTTP para HTTPS
- HSTS habilitado

### Autenticação
- Senhas com hash SHA-256 mínimo
- Política de senhas forte
- Bloqueio após tentativas falhadas
- Logs de acesso obrigatórios

### Proteção de Dados
- Validação de entrada em todos os forms
- Sanitização de dados
- Proteção contra CSRF/XSS
- Rate limiting em APIs

## Requisitos de Performance

### Tempo de Resposta
- **Páginas simples**: < 2 segundos
- **Dashboards**: < 5 segundos
- **Relatórios**: < 30 segundos
- **Exports grandes**: < 5 minutos

### Concurrent Users
- **Desenvolvimento**: 5-10 usuários
- **Produção pequena**: 50-100 usuários
- **Produção média**: 200-500 usuários

### Armazenamento
- **Dados base**: ~100 MB por 1000 pets
- **Logs**: ~1 GB por ano (uso médio)
- **Backups**: 3x tamanho dos dados
- **Cache**: 10-20% do tamanho dos dados

## Requisitos de Backup

### Frequência
- **Dados críticos**: Diário
- **Logs**: Semanal
- **Configurações**: Após mudanças

### Retenção
- **Backups diários**: 30 dias
- **Backups semanais**: 3 meses
- **Backups mensais**: 1 ano

### Localização
- **Primário**: Mesmo servidor
- **Secundário**: Cloud storage
- **Terciário**: Offline (opcional)

## Monitoramento

### Métricas Essenciais
- Tempo de resposta das páginas
- Uso de CPU e memória
- Espaço em disco
- Conexões de banco de dados
- Taxa de erro

### Alertas
- CPU > 80% por 5 min
- Memória > 90%
- Disco > 85%
- Erro rate > 5%
- Downtime > 1 min

## Compatibilidade

### Formatos de Arquivo
- **Import**: CSV, Excel (.xlsx), JSON
- **Export**: CSV, Excel, JSON, PDF (futuro)
- **Imagens**: PNG, JPG, JPEG
- **Backup**: ZIP, TAR.GZ

### Integrações Futuras
- WhatsApp Business API
- Telegram Bot API
- Facebook/Instagram API
- Google Maps API
- OpenAI API

## Instalação e Deploy

### Desenvolvimento Local
```bash
# Clonar repositório
git clone <repo-url>
cd petcare-analytics

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# Executar aplicação
streamlit run app.py
```

### Produção
- Deploy via Docker (recomendado)
- Proxy reverso (Nginx/Apache)
- Process manager (PM2/Supervisor)
- SSL/TLS configurado
- Monitoramento ativo

## Licenciamento

### Software Livre
- Python: PSF License
- Streamlit: Apache 2.0
- Pandas/NumPy: BSD
- Scikit-learn: BSD

### Serviços Pagos
- Supabase: Plano gratuito limitado
- APIs externas: Conforme uso
- Certificados SSL: Let's Encrypt gratuito
- Hospedagem: Conforme provedor
