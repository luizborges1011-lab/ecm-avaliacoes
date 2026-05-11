import os
import reflex as rx
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class AvaliacaoItem(BaseModel):
    id: int = 0
    protocolo: str = ""
    cliente: str = ""
    responsavel: str = ""
    data_atendimento: str = ""
    hora_inicio: str = ""
    hora_fim: str = ""
    tempo_minutos: int = 0
    tempo_formatado: str = ""
    nota: float = 0.0
    status: str = ""
    kanban_status: str = ""
    pontos_criticos: str = ""
    feedback_final: str = ""


class MonthlyData(BaseModel):
    mes: str = ""
    nota_media: float = 0.0
    total: int = 0


class RankingItem(BaseModel):
    posicao: int = 0
    nome: str = ""
    nota: float = 0.0
    total: int = 0
    aprovados: int = 0


class AuditLogItem(BaseModel):
    id: int = 0
    usuario: str = ""
    acao: str = ""
    entidade: str = ""
    entidade_id: str = ""
    detalhes: str = ""
    criado_em: str = ""


class ErroItem(BaseModel):
    id: int = 0
    protocolo: str = ""
    erro: str = ""
    tentativas: int = 0
    criado_em: str = ""


class AtendenteItem(BaseModel):
    id: int = 0
    nome: str = ""
    email: str = ""
    ativo: bool = True
    total: int = 0
    nota_media: float = 0.0


_AVALIACOES_DICTS = [
    {"id": 1, "protocolo": "20251201094532", "cliente": "Maria Aparecida Santos", "responsavel": "Giulia Detoni", "data_atendimento": "01/12/2025", "hora_inicio": "09:45", "hora_fim": "10:12", "tempo_minutos": 27, "tempo_formatado": "0:27", "nota": 9.2, "status": "Excelente", "kanban_status": "Concluído Sem Ressalvas", "pontos_criticos": "Atendimento exemplar. Resposta clara, objetiva e dentro do prazo.", "feedback_final": "Parabéns pelo atendimento. Comunicação clara e resolução eficiente."},
    {"id": 2, "protocolo": "20251201103445", "cliente": "Carlos Eduardo Lima", "responsavel": "Bruna Madruga", "data_atendimento": "01/12/2025", "hora_inicio": "10:34", "hora_fim": "11:15", "tempo_minutos": 41, "tempo_formatado": "0:41", "nota": 8.5, "status": "Excelente", "kanban_status": "Concluído Sem Ressalvas", "pontos_criticos": "Boa resolução. Poderia ter sido mais direto na explicação.", "feedback_final": "Bom atendimento. Tente ser mais objetivo nas explicações técnicas."},
    {"id": 3, "protocolo": "20251130145622", "cliente": "Ana Paula Rodrigues", "responsavel": "Simone Chenet", "data_atendimento": "30/11/2025", "hora_inicio": "14:56", "hora_fim": "16:30", "tempo_minutos": 94, "tempo_formatado": "1:34", "nota": 6.8, "status": "Bom", "kanban_status": "Análise Humana", "pontos_criticos": "Demora na resposta. Cliente precisou aguardar mais de 1h30 para obter retorno.", "feedback_final": "O atendimento foi resolvido mas o tempo de resposta precisa melhorar."},
    {"id": 4, "protocolo": "20251130081233", "cliente": "Roberto Ferreira", "responsavel": "Franciele Favero", "data_atendimento": "30/11/2025", "hora_inicio": "08:12", "hora_fim": "08:45", "tempo_minutos": 33, "tempo_formatado": "0:33", "nota": 8.1, "status": "Excelente", "kanban_status": "Concluído Sem Ressalvas", "pontos_criticos": "Atendimento bem conduzido. Encerramento poderia ser mais formal.", "feedback_final": "Ótimo atendimento. Atenção ao fechamento formal da conversa."},
    {"id": 5, "protocolo": "20251129154432", "cliente": "Fernanda Oliveira", "responsavel": "Thais Seratto", "data_atendimento": "29/11/2025", "hora_inicio": "15:44", "hora_fim": "17:22", "tempo_minutos": 98, "tempo_formatado": "1:38", "nota": 5.5, "status": "Regular", "kanban_status": "Feedback", "pontos_criticos": "Falta de clareza técnica. O cliente não entendeu o que precisava fazer.", "feedback_final": "Revise a forma de comunicar informações técnicas. O cliente ficou confuso."},
    {"id": 6, "protocolo": "20251129092155", "cliente": "Marcos Antonio Costa", "responsavel": "Luiz Henrique Borges", "data_atendimento": "29/11/2025", "hora_inicio": "09:21", "hora_fim": "09:47", "tempo_minutos": 26, "tempo_formatado": "0:26", "nota": 9.5, "status": "Excelente", "kanban_status": "Concluído Sem Ressalvas", "pontos_criticos": "Atendimento perfeito. Rápido, claro e resolutivo.", "feedback_final": "Atendimento exemplar. Continue assim!"},
    {"id": 7, "protocolo": "20251128165544", "cliente": "Patrícia Mendes", "responsavel": "Ana Cristina Pinge", "data_atendimento": "28/11/2025", "hora_inicio": "16:55", "hora_fim": "17:30", "tempo_minutos": 35, "tempo_formatado": "0:35", "nota": 7.8, "status": "Bom", "kanban_status": "Pendente", "pontos_criticos": "Bom atendimento. Faltou mensagem de encerramento formal.", "feedback_final": "Bom trabalho. Lembre de fechar o atendimento com uma mensagem de encerramento."},
    {"id": 8, "protocolo": "20251128134004", "cliente": "José Carlos Pereira", "responsavel": "Greicy Pedroso", "data_atendimento": "28/11/2025", "hora_inicio": "13:40", "hora_fim": "15:10", "tempo_minutos": 90, "tempo_formatado": "1:30", "nota": 3.5, "status": "Crítico", "kanban_status": "Análise Humana", "pontos_criticos": "Atendimento inadequado. Linguagem informal, falta de clareza e demora excessiva.", "feedback_final": "Este atendimento precisa de revisão urgente. Múltiplas falhas identificadas."},
    {"id": 9, "protocolo": "20251127103322", "cliente": "Sandra Regina Lima", "responsavel": "Naiara Dalmora", "data_atendimento": "27/11/2025", "hora_inicio": "10:33", "hora_fim": "11:05", "tempo_minutos": 32, "tempo_formatado": "0:32", "nota": 8.7, "status": "Excelente", "kanban_status": "Concluído Sem Ressalvas", "pontos_criticos": "Excelente comunicação. Resolveu a demanda com clareza.", "feedback_final": "Ótimo atendimento. Cliente ficou satisfeito com a resolução."},
    {"id": 10, "protocolo": "20251127084512", "cliente": "Paulo Ricardo Souza", "responsavel": "Mauricio Vieira", "data_atendimento": "27/11/2025", "hora_inicio": "08:45", "hora_fim": "09:30", "tempo_minutos": 45, "tempo_formatado": "0:45", "nota": 7.2, "status": "Bom", "kanban_status": "Concluído Com Ressalvas", "pontos_criticos": "Resolução adequada mas com demora inicial de 20 minutos sem resposta.", "feedback_final": "Atendimento resolvido. Atenção ao tempo de primeira resposta."},
]

_MONTHLY_DICTS = [
    {"mes": "Jun", "nota_media": 7.8, "total": 38},
    {"mes": "Jul", "nota_media": 8.0, "total": 42},
    {"mes": "Ago", "nota_media": 7.6, "total": 35},
    {"mes": "Set", "nota_media": 8.2, "total": 44},
    {"mes": "Out", "nota_media": 8.4, "total": 51},
    {"mes": "Nov", "nota_media": 8.1, "total": 48},
    {"mes": "Dez", "nota_media": 8.7, "total": 37},
]

_RANKING_DICTS = [
    {"posicao": 1, "nome": "Luiz Henrique Borges", "nota": 9.1, "total": 34, "aprovados": 32},
    {"posicao": 2, "nome": "Bruna Madruga", "nota": 8.8, "total": 28, "aprovados": 26},
    {"posicao": 3, "nome": "Giulia Detoni", "nota": 8.6, "total": 31, "aprovados": 28},
    {"posicao": 4, "nome": "Franciele Favero", "nota": 8.3, "total": 22, "aprovados": 19},
    {"posicao": 5, "nome": "Naiara Dalmora", "nota": 8.2, "total": 18, "aprovados": 16},
    {"posicao": 6, "nome": "Simone Chenet", "nota": 7.9, "total": 19, "aprovados": 15},
    {"posicao": 7, "nome": "Thais Seratto", "nota": 7.7, "total": 25, "aprovados": 18},
]

_AUDIT_DICTS = [
    {"id": 1, "usuario": "Luiz Henrique Borges", "acao": "Nota revisada", "entidade": "Avaliação", "entidade_id": "20251130145622", "detalhes": "Nota alterada de 5.2 para 6.8 — contexto de demora por terceiro", "criado_em": "01/12/2025 14:32"},
    {"id": 2, "usuario": "Bruna Madruga", "acao": "Status Kanban alterado", "entidade": "Avaliação", "entidade_id": "20251129154432", "detalhes": "Movido de 'Pendente' para 'Feedback'", "criado_em": "01/12/2025 11:18"},
    {"id": 3, "usuario": "Luiz Henrique Borges", "acao": "Avaliação desconsiderada", "entidade": "Avaliação", "entidade_id": "20251127084512", "detalhes": "Desconsiderado — atendimento com terceiro sem resposta", "criado_em": "30/11/2025 17:05"},
    {"id": 4, "usuario": "Sistema", "acao": "Avaliação processada", "entidade": "Avaliação", "entidade_id": "20251201094532", "detalhes": "Processamento automático via IA — GPT-4.1-mini", "criado_em": "01/12/2025 10:00"},
    {"id": 5, "usuario": "Sistema", "acao": "Avaliação processada", "entidade": "Avaliação", "entidade_id": "20251201103445", "detalhes": "Processamento automático via IA — GPT-4.1-mini", "criado_em": "01/12/2025 12:00"},
]

_ERROS_DICTS = [
    {"id": 1, "protocolo": "20251130221100", "erro": "Timeout ao baixar áudio: URL expirada após 24h", "tentativas": 2, "criado_em": "30/11/2025 22:15"},
    {"id": 2, "protocolo": "20251129181544", "erro": "API Digisac retornou 429 (Rate limit)", "tentativas": 3, "criado_em": "29/11/2025 18:20"},
]

_ATENDENTES_DICTS = [
    {"id": 1, "nome": "Airon Capra", "email": "airon@ecm.com.br", "ativo": True, "total": 12, "nota_media": 8.1},
    {"id": 2, "nome": "Alesson Biezus", "email": "alesson@ecm.com.br", "ativo": True, "total": 8, "nota_media": 7.9},
    {"id": 3, "nome": "Ana Cristina Pinge", "email": "ana@ecm.com.br", "ativo": True, "total": 17, "nota_media": 7.5},
    {"id": 4, "nome": "Bruna Madruga", "email": "bruna@ecm.com.br", "ativo": True, "total": 28, "nota_media": 8.8},
    {"id": 5, "nome": "Danieli Kupper", "email": "danieli@ecm.com.br", "ativo": True, "total": 14, "nota_media": 7.8},
    {"id": 6, "nome": "Edson da Silva", "email": "edson@ecm.com.br", "ativo": False, "total": 5, "nota_media": 6.9},
    {"id": 7, "nome": "Franciele Favero", "email": "franciele@ecm.com.br", "ativo": True, "total": 22, "nota_media": 8.3},
    {"id": 8, "nome": "Giulia Detoni", "email": "giulia@ecm.com.br", "ativo": True, "total": 31, "nota_media": 8.6},
    {"id": 9, "nome": "Greicy Pedroso", "email": "greicy@ecm.com.br", "ativo": True, "total": 20, "nota_media": 7.4},
    {"id": 10, "nome": "Luiz Henrique Borges", "email": "luiz.h@ecm.com.br", "ativo": True, "total": 34, "nota_media": 9.1},
    {"id": 11, "nome": "Simone Chenet", "email": "simone@ecm.com.br", "ativo": True, "total": 19, "nota_media": 7.9},
    {"id": 12, "nome": "Thais Seratto", "email": "thais@ecm.com.br", "ativo": True, "total": 25, "nota_media": 7.7},
]


def _carregar_do_supabase() -> list[dict]:
    """Tenta carregar avaliações do Supabase. Retorna [] se não configurado."""
    try:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key or "PREENCHER" in key:
            return []
        from supabase import create_client
        client = create_client(url, key)
        result = client.table("avaliacao").select("*").order("data_avaliacao", desc=True).limit(500).execute()
        return result.data or []
    except Exception:
        return []


def _carregar_erros_supabase() -> list[dict]:
    try:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key or "PREENCHER" in key:
            return []
        from supabase import create_client
        client = create_client(url, key)
        result = client.table("filaerros").select("*").eq("resolvido", False).order("criado_em", desc=True).execute()
        return result.data or []
    except Exception:
        return []


def _carregar_audit_supabase() -> list[dict]:
    try:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if not url or not key or "PREENCHER" in key:
            return []
        from supabase import create_client
        client = create_client(url, key)
        result = client.table("auditlog").select("*").order("criado_em", desc=True).limit(100).execute()
        return result.data or []
    except Exception:
        return []


def _dict_to_avaliacao(d: dict) -> "AvaliacaoItem":
    return AvaliacaoItem(
        id=d.get("id", 0),
        protocolo=d.get("protocolo", ""),
        cliente=d.get("cliente", ""),
        responsavel=d.get("responsavel", ""),
        data_atendimento=d.get("data_atendimento", ""),
        hora_inicio=d.get("hora_inicio", ""),
        hora_fim=d.get("hora_fim", ""),
        tempo_minutos=d.get("tempo_minutos", 0),
        tempo_formatado=d.get("tempo_formatado", "0:00"),
        nota=float(d.get("nota", 0.0)),
        status=d.get("status", "Bom"),
        kanban_status=d.get("kanban_status", "Pendente"),
        pontos_criticos=d.get("pontos_criticos", ""),
        feedback_final=d.get("feedback_final", ""),
    )


class AppState(rx.State):
    avaliacoes: list[AvaliacaoItem] = [AvaliacaoItem(**d) for d in _AVALIACOES_DICTS]
    selected_avaliacao: AvaliacaoItem = AvaliacaoItem()
    show_drawer: bool = False

    monthly_data: list[dict] = _MONTHLY_DICTS
    ranking_data: list[RankingItem] = [RankingItem(**d) for d in _RANKING_DICTS]
    audit_logs: list[AuditLogItem] = [AuditLogItem(**d) for d in _AUDIT_DICTS]
    erros_fila: list[ErroItem] = [ErroItem(**d) for d in _ERROS_DICTS]
    atendentes: list[AtendenteItem] = [AtendenteItem(**d) for d in _ATENDENTES_DICTS]

    ultimo_processamento: str = "01/12/2025 às 12:04"
    proximo_processamento: str = "01/12/2025 às 16:00"
    status_automacao: str = "Operacional"

    search_query: str = ""
    filter_status: str = ""
    filter_responsavel: str = ""

    tv_mode: bool = False

    @rx.var
    def current_path(self) -> str:
        return self.router.url.path

    @rx.var
    def total_avaliacoes(self) -> int:
        return len(self.avaliacoes)

    @rx.var
    def nota_media(self) -> str:
        if not self.avaliacoes:
            return "0.0"
        media = sum(a.nota for a in self.avaliacoes) / len(self.avaliacoes)
        return f"{media:.1f}"

    @rx.var
    def taxa_aprovacao(self) -> str:
        if not self.avaliacoes:
            return "0%"
        aprovados = sum(1 for a in self.avaliacoes if a.nota >= 7.0)
        return f"{(aprovados / len(self.avaliacoes) * 100):.0f}%"

    @rx.var
    def tempo_medio(self) -> str:
        if not self.avaliacoes:
            return "0 min"
        media = sum(a.tempo_minutos for a in self.avaliacoes) / len(self.avaliacoes)
        return f"{int(media)} min"

    @rx.var
    def avaliacoes_filtradas(self) -> list[AvaliacaoItem]:
        result = self.avaliacoes
        if self.search_query:
            q = self.search_query.lower()
            result = [a for a in result if q in a.cliente.lower() or q in a.responsavel.lower() or q in a.protocolo.lower()]
        if self.filter_status:
            result = [a for a in result if a.status == self.filter_status]
        if self.filter_responsavel:
            result = [a for a in result if a.responsavel == self.filter_responsavel]
        return result

    @rx.var
    def avaliacoes_pendentes(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.kanban_status == "Pendente"]

    @rx.var
    def avaliacoes_analise(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.kanban_status == "Análise Humana"]

    @rx.var
    def avaliacoes_feedback(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.kanban_status == "Feedback"]

    @rx.var
    def avaliacoes_com_ressalvas(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.kanban_status == "Concluído Com Ressalvas"]

    @rx.var
    def avaliacoes_sem_ressalvas(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.kanban_status == "Concluído Sem Ressalvas"]

    @rx.var
    def atendentes_nomes(self) -> list[str]:
        return sorted(list(set(a.responsavel for a in self.avaliacoes)))

    @rx.var
    def avaliacoes_criticas(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes if a.nota < 6.0]

    @rx.event
    def open_avaliacao(self, avaliacao_id: int):
        for av in self.avaliacoes:
            if av.id == avaliacao_id:
                self.selected_avaliacao = av
                self.show_drawer = True
                break

    @rx.event
    def close_drawer(self):
        self.show_drawer = False
        self.selected_avaliacao = AvaliacaoItem()

    @rx.event
    def set_search(self, value: str):
        self.search_query = value

    @rx.event
    def set_filter_status(self, value: str):
        self.filter_status = value

    @rx.event
    def set_filter_responsavel(self, value: str):
        self.filter_responsavel = value

    @rx.event
    def clear_filters(self):
        self.search_query = ""
        self.filter_status = ""
        self.filter_responsavel = ""

    @rx.event
    def toggle_tv_mode(self):
        self.tv_mode = not self.tv_mode

    @rx.event
    def reprocessar_erro(self, erro_id: int):
        self.erros_fila = [e for e in self.erros_fila if e.id != erro_id]
        try:
            from worker.services.database import marcar_erro_resolvido
            marcar_erro_resolvido(erro_id)
        except Exception:
            pass

    @rx.event
    def carregar_dados(self):
        """Carrega dados reais do Supabase (substitui os dados mock)."""
        dados_db = _carregar_do_supabase()
        if dados_db:
            self.avaliacoes = [_dict_to_avaliacao(d) for d in dados_db]

        erros_db = _carregar_erros_supabase()
        if erros_db:
            self.erros_fila = [
                ErroItem(
                    id=e.get("id", 0),
                    protocolo=e.get("protocolo", ""),
                    erro=e.get("erro", ""),
                    tentativas=e.get("tentativas", 0),
                    criado_em=str(e.get("criado_em", "")),
                )
                for e in erros_db
            ]

        audit_db = _carregar_audit_supabase()
        if audit_db:
            self.audit_logs = [
                AuditLogItem(
                    id=a.get("id", 0),
                    usuario=a.get("usuario", ""),
                    acao=a.get("acao", ""),
                    entidade=a.get("entidade", ""),
                    entidade_id=a.get("entidade_id", ""),
                    detalhes=a.get("detalhes", ""),
                    criado_em=str(a.get("criado_em", "")),
                )
                for a in audit_db
            ]
