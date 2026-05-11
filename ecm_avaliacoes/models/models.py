import enum
from datetime import datetime
from typing import Optional
import sqlmodel


class KanbanStatus(str, enum.Enum):
    PENDENTE = "Pendente"
    ANALISE_HUMANA = "Análise Humana"
    FEEDBACK = "Feedback"
    CONCLUIDO_COM_RESSALVAS = "Concluído Com Ressalvas"
    CONCLUIDO_SEM_RESSALVAS = "Concluído Sem Ressalvas"


class StatusNota(str, enum.Enum):
    EXCELENTE = "Excelente"
    BOM = "Bom"
    REGULAR = "Regular"
    CRITICO = "Crítico"


class Atendente(sqlmodel.SQLModel, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    nome_digisac: str = sqlmodel.Field(index=True)
    nome_real: str
    email: Optional[str] = None
    ativo: bool = True
    criado_em: datetime = sqlmodel.Field(default_factory=datetime.utcnow)


class Avaliacao(sqlmodel.SQLModel, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    protocolo: str = sqlmodel.Field(unique=True, index=True)
    cliente: str
    responsavel: str
    data_atendimento: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    tempo_minutos: int = 0
    tempo_formatado: str = "0:00"
    nota: float = 0.0
    status: StatusNota = StatusNota.BOM
    pontos_criticos: Optional[str] = None
    feedback_final: Optional[str] = None
    avaliacao_ai_completa: Optional[str] = None
    relatorio_conversa_original: Optional[str] = None
    data_avaliacao: datetime = sqlmodel.Field(default_factory=datetime.utcnow)
    kanban_status: KanbanStatus = KanbanStatus.PENDENTE
    nota_revisada: Optional[float] = None
    justificativa_revisao: Optional[str] = None
    desconsiderado: bool = False
    justificativa_desconsiderar: Optional[str] = None


class Comentario(sqlmodel.SQLModel, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    avaliacao_id: int = sqlmodel.Field(foreign_key="avaliacao.id", index=True)
    usuario: str
    texto: str
    criado_em: datetime = sqlmodel.Field(default_factory=datetime.utcnow)


class AuditLog(sqlmodel.SQLModel, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    usuario: str
    acao: str
    entidade: str
    entidade_id: str
    detalhes: Optional[str] = None
    criado_em: datetime = sqlmodel.Field(default_factory=datetime.utcnow)


class FilaErros(sqlmodel.SQLModel, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    protocolo: str
    erro: str
    tentativas: int = 0
    resolvido: bool = False
    criado_em: datetime = sqlmodel.Field(default_factory=datetime.utcnow)
