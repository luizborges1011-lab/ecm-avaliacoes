-- Executar no Supabase: Dashboard > SQL Editor > New query

CREATE TABLE IF NOT EXISTS atendente (
    id SERIAL PRIMARY KEY,
    nome_digisac TEXT NOT NULL,
    nome_real TEXT NOT NULL,
    email TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_atendente_nome ON atendente(nome_digisac);

CREATE TABLE IF NOT EXISTS avaliacao (
    id SERIAL PRIMARY KEY,
    protocolo TEXT UNIQUE NOT NULL,
    cliente TEXT NOT NULL DEFAULT '',
    responsavel TEXT NOT NULL DEFAULT '',
    data_atendimento TEXT,
    hora_inicio TEXT,
    hora_fim TEXT,
    tempo_minutos INT DEFAULT 0,
    tempo_formatado TEXT DEFAULT '0:00',
    nota FLOAT DEFAULT 0.0,
    status TEXT DEFAULT 'Bom',
    pontos_criticos TEXT,
    feedback_final TEXT,
    avaliacao_ai_completa TEXT,
    relatorio_conversa_original TEXT,
    data_avaliacao TIMESTAMPTZ DEFAULT NOW(),
    kanban_status TEXT DEFAULT 'Pendente',
    nota_revisada FLOAT,
    justificativa_revisao TEXT,
    desconsiderado BOOLEAN DEFAULT FALSE,
    justificativa_desconsiderar TEXT
);
CREATE INDEX IF NOT EXISTS idx_avaliacao_protocolo ON avaliacao(protocolo);
CREATE INDEX IF NOT EXISTS idx_avaliacao_data ON avaliacao(data_avaliacao DESC);
CREATE INDEX IF NOT EXISTS idx_avaliacao_responsavel ON avaliacao(responsavel);

CREATE TABLE IF NOT EXISTS comentario (
    id SERIAL PRIMARY KEY,
    avaliacao_id INT NOT NULL REFERENCES avaliacao(id) ON DELETE CASCADE,
    usuario TEXT NOT NULL,
    texto TEXT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_comentario_avaliacao ON comentario(avaliacao_id);

CREATE TABLE IF NOT EXISTS auditlog (
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL,
    acao TEXT NOT NULL,
    entidade TEXT NOT NULL,
    entidade_id TEXT NOT NULL,
    detalhes TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_criado ON auditlog(criado_em DESC);

CREATE TABLE IF NOT EXISTS filaerros (
    id SERIAL PRIMARY KEY,
    protocolo TEXT NOT NULL,
    erro TEXT NOT NULL,
    tentativas INT DEFAULT 0,
    resolvido BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_erros_resolvido ON filaerros(resolvido);
