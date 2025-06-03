-- 1. Tabela de usuários
CREATE TABLE users_analytics (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user',
    preferences JSONB DEFAULT '{}',
    profile_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabela de pets
CREATE TABLE pets_analytics (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo_pet TEXT NOT NULL,
    raca TEXT,
    idade DECIMAL,
    peso DECIMAL,
    sexo TEXT,
    genero TEXT,
    bairro TEXT,
    regiao TEXT,
    telefone TEXT,
    cor_pelagem TEXT,
    status_vacinacao TEXT,
    estado_saude TEXT,
    necessidades_especiais TEXT,
    historico_medico TEXT,
    comportamento TEXT,
    temperamento TEXT,
    sociabilidade INTEGER,
    energia INTEGER,
    nivel_atividade INTEGER,
    adaptabilidade TEXT,
    adotado BOOLEAN DEFAULT FALSE,
    score_adocao DECIMAL,
    risco_abandono DECIMAL,
    observacoes TEXT,
    data_registro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by BIGINT REFERENCES users_analytics(id),
    foto_url TEXT,
    status TEXT DEFAULT 'Disponível',
    castrado BOOLEAN DEFAULT FALSE,
    microchip BOOLEAN DEFAULT FALSE,
    vacinas TEXT,
    cor TEXT,
    contato TEXT,
    endereco TEXT,
    nivel_energia TEXT,
    cuidados_especiais TEXT,
    custo_mensal DECIMAL,
    tempo_disponivel INTEGER,
    experiencia_tutor TEXT,
    ambiente_ideal TEXT,
    compatibilidade_criancas BOOLEAN,
    compatibilidade_pets BOOLEAN,
    cluster_comportamental INTEGER,
    data_nascimento DATE,
    cuidados_veterinarios TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabela de logs de atividade
CREATE TABLE activity_logs_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users_analytics(id),
    action TEXT NOT NULL,
    details TEXT,
    session_id TEXT,
    execution_time DECIMAL,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabela de logs de login
CREATE TABLE login_logs_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users_analytics(id),
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    failure_reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Índices para melhor performance
CREATE INDEX idx_users_analytics_email ON users_analytics(email);
CREATE INDEX idx_users_analytics_role ON users_analytics(role);
CREATE INDEX idx_pets_analytics_tipo_pet ON pets_analytics(tipo_pet);
CREATE INDEX idx_pets_analytics_adotado ON pets_analytics(adotado);
CREATE INDEX idx_pets_analytics_created_by ON pets_analytics(created_by);
CREATE INDEX idx_pets_analytics_bairro ON pets_analytics(bairro);
CREATE INDEX idx_pets_analytics_data_registro ON pets_analytics(data_registro);
CREATE INDEX idx_activity_logs_analytics_user_id ON activity_logs_analytics(user_id);
CREATE INDEX idx_activity_logs_analytics_timestamp ON activity_logs_analytics(timestamp);
CREATE INDEX idx_login_logs_analytics_user_id ON login_logs_analytics(user_id);
CREATE INDEX idx_login_logs_analytics_timestamp ON login_logs_analytics(timestamp);

-- 6. Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_analytics_updated_at 
    BEFORE UPDATE ON users_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pets_analytics_updated_at 
    BEFORE UPDATE ON pets_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7. RLS (Row Level Security) - Opcional
ALTER TABLE users_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE pets_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_logs_analytics ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajuste conforme necessário)
CREATE POLICY "Users can view their own data" ON users_analytics
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own data" ON users_analytics
    FOR UPDATE USING (auth.uid()::text = id::text);