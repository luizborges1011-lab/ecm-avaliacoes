import os
import re
import secrets
import unicodedata
import reflex as rx
from pydantic import BaseModel
from dotenv import load_dotenv
from worker.services.ai_service import PROMPT_AVALIACAO

load_dotenv()


def _normalizar_setor(setor: str) -> str:
    """Strip accents and lowercase for deduplication comparisons."""
    s = unicodedata.normalize("NFD", setor.lower().strip())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _tem_acento(texto: str) -> bool:
    return any(ord(c) > 127 for c in texto)


# Session store: token → {nome, email, is_admin, atendente_nome}
_SESSIONS: dict[str, dict] = {}


class MensagemItem(BaseModel):
    autor: str = ""
    hora: str = ""
    conteudo: str = ""
    tipo: str = ""  # "cliente", "atendente", "bot", "sistema"


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
    pontos_criticos: str = ""
    feedback_final: str = ""
    justificativa_revisao: str = ""
    data_avaliacao: str = ""
    conferido: bool = False
    conferido_por: str = ""


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


class AtrasadoLogItem(BaseModel):
    id: int = 0
    chamado_id: str = ""
    cliente: str = ""
    setor: str = ""
    tempo_espera: int = 0
    criado_em: str = ""


class AtrasadoAgrupadoItem(BaseModel):
    cliente: str = ""
    total_esperas: int = 0
    setores: str = ""
    protocolos: str = ""
    ultima_data: str = ""


class DeptAtrasoItem(BaseModel):
    setor: str = ""
    clientes: int = 0
    ocorrencias: int = 0


class CicloLogItem(BaseModel):
    id: int = 0
    data_hora: str = ""
    tipo: str = "automatico"
    total: int = 0
    sucesso: int = 0
    erros: int = 0
    periodo: str = ""
    status: str = "Sucesso"


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


class UserItem(BaseModel):
    id: int = 0
    nome: str = ""
    email: str = ""
    is_admin: bool = False
    ativo: bool = True
    atendente_nome: str = ""




# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key or "PREENCHER" in key:
        return None
    from supabase import create_client
    return create_client(url, key)


def _carregar_do_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = (
            client.table("avaliacao")
            .select(
                "id, protocolo, cliente, responsavel, data_atendimento, hora_inicio, "
                "hora_fim, tempo_minutos, tempo_formatado, nota, status, "
                "pontos_criticos, feedback_final, justificativa_revisao, data_avaliacao, "
                "conferido, conferido_por"
            )
            .order("data_avaliacao", desc=True)
            .limit(5000)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _carregar_erros_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = client.table("filaerros").select("*").eq("resolvido", False).order("criado_em", desc=True).execute()
        return result.data or []
    except Exception:
        return []


def _carregar_audit_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = client.table("auditlog").select("*").order("criado_em", desc=True).limit(100).execute()
        return result.data or []
    except Exception:
        return []


def _carregar_usuarios_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = client.table("usuarios").select("id, nome, email, is_admin, ativo, atendente_nome").order("nome").execute()
        return result.data or []
    except Exception:
        return []


def _verificar_login_supabase(email: str, senha: str) -> dict | None:
    try:
        client = _supabase_client()
        if not client:
            return None
        import bcrypt
        result = client.table("usuarios").select("*").eq("email", email).eq("ativo", True).execute()
        if not result.data:
            return None
        user = result.data[0]
        stored_hash = user.get("senha_hash", "")
        if not stored_hash:
            return None
        if bcrypt.checkpw(senha.encode(), stored_hash.encode()):
            return user
        return None
    except Exception:
        return None


def _salvar_usuario_supabase(dados: dict) -> int | None:
    try:
        client = _supabase_client()
        if not client:
            return None
        import bcrypt
        payload: dict = {
            "nome": dados["nome"],
            "email": dados["email"],
            "is_admin": dados["is_admin"],
            "ativo": dados.get("ativo", True),
            "atendente_nome": dados.get("atendente_nome", ""),
        }
        senha = dados.get("senha", "")
        if senha:
            payload["senha_hash"] = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        uid = dados.get("id")
        if uid:
            client.table("usuarios").update(payload).eq("id", uid).execute()
            return uid
        else:
            res = client.table("usuarios").insert(payload).execute()
            return res.data[0]["id"] if res.data else None
    except Exception:
        return None


def _deletar_avaliacao_supabase(avaliacao_id: int) -> bool:
    try:
        client = _supabase_client()
        if not client:
            return False
        client.table("avaliacao").delete().eq("id", avaliacao_id).execute()
        return True
    except Exception:
        return False


def _registrar_audit_supabase(usuario: str, acao: str, entidade_id: str, detalhes: str) -> None:
    try:
        from datetime import datetime
        client = _supabase_client()
        if not client:
            return
        client.table("auditlog").insert({
            "usuario": usuario,
            "acao": acao,
            "entidade": "Avaliação",
            "entidade_id": entidade_id,
            "detalhes": detalhes,
            "criado_em": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass


def _deletar_usuario_supabase(user_id: int) -> bool:
    try:
        client = _supabase_client()
        if not client:
            return False
        client.table("usuarios").delete().eq("id", user_id).execute()
        return True
    except Exception:
        return False


def _fmt_minutos(m: int) -> str:
    h = m // 60
    mn = m % 60
    return f"{h}h {mn}min" if h > 0 else f"{mn} min"


def _carregar_atrasados_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = (
            client.table("atendimentos_atrasados_log")
            .select("*")
            .order("data_hora_alerta", desc=True)
            .limit(2000)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _dict_to_atrasado(d: dict) -> "AtrasadoLogItem":
    segundos = int(d.get("tempo_espera_segundos") or 0)
    return AtrasadoLogItem(
        id=0,
        chamado_id=str(d.get("protocolo") or ""),
        cliente=str(d.get("nome_contato") or ""),
        setor=str(d.get("departamento") or ""),
        tempo_espera=segundos // 60,
        criado_em=str(d.get("data_hora_alerta") or ""),
    )


def _carregar_ciclos_supabase() -> list[dict]:
    try:
        client = _supabase_client()
        if not client:
            return []
        result = (
            client.table("auditlog")
            .select("*")
            .eq("acao", "Ciclo executado")
            .order("criado_em", desc=True)
            .limit(20)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _dict_to_ciclo(d: dict) -> "CicloLogItem":
    import json
    try:
        info = json.loads(d.get("detalhes", "{}"))
    except Exception:
        info = {}
    total = int(info.get("total", 0))
    sucesso = int(info.get("sucesso", 0))
    erros = int(info.get("erros", 0))
    periodo = str(info.get("periodo", ""))
    if total == 0 and erros == 0:
        status = "Sem chamados"
    elif erros == 0:
        status = "Sucesso"
    elif sucesso > 0:
        status = "Com erros"
    else:
        status = "Falhou"
    return CicloLogItem(
        id=int(d.get("id", 0)),
        data_hora=str(d.get("criado_em", "")),
        tipo=str(d.get("entidade_id", "automatico")),
        total=total,
        sucesso=sucesso,
        erros=erros,
        periodo=periodo,
        status=status,
    )


def _executar_ciclo_manual_thread() -> dict:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from worker.tasks.avaliar import executar_ciclo
        from worker.services.database import registrar_ciclo_log
        resultado = executar_ciclo()
        registrar_ciclo_log(
            tipo="manual",
            total=resultado["total"],
            sucesso=resultado["sucesso"],
            erros=resultado["erro"],
            periodo=resultado.get("periodo", ""),
        )
        return resultado
    except Exception:
        return {"sucesso": 0, "erro": 1, "total": 0, "periodo": "—"}


def _carregar_historico_supabase(avaliacao_id: int) -> str:
    try:
        client = _supabase_client()
        if not client:
            return ""
        result = (
            client.table("avaliacao")
            .select("relatorio_conversa_original")
            .eq("id", avaliacao_id)
            .execute()
        )
        if result.data:
            return result.data[0].get("relatorio_conversa_original") or ""
        return ""
    except Exception:
        return ""


def _parse_historico_conversa(texto: str, cliente: str) -> list[dict]:
    if not texto:
        return []
    h_start = texto.find("HISTÓRICO DA CONVERSA")
    h_end = texto.find("FIM DO ATENDIMENTO")
    if h_start == -1:
        return []
    secao = texto[h_start + len("HISTÓRICO DA CONVERSA"):h_end if h_end != -1 else len(texto)]
    PATTERN = re.compile(
        r'(?:(?:💬|🤖)\s*\[([^\],]+),\s*\d{2}/\d{2}/\d{4}\s(\d{2}:\d{2}):\d{2}\]:)'
        r'|\[Sistema\]:',
        re.UNICODE,
    )
    matches = list(PATTERN.finditer(secao))
    cliente_lower = cliente.lower().strip()
    mensagens = []
    for i, m in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(secao)
        raw = secao[m.end():next_start]
        conteudo = re.sub(r'^[\s\n]+|[\s\n╔╚═]+$', '', raw).strip()
        if not conteudo:
            continue
        if m.group(1) is not None:
            autor = m.group(1).strip()
            hora = m.group(2) if m.group(2) else ""
            if autor.upper() == "BOT":
                tipo = "bot"
            elif autor.lower() == cliente_lower:
                tipo = "cliente"
            else:
                tipo = "atendente"
        else:
            autor = "Sistema"
            hora = ""
            tipo = "sistema"
        mensagens.append({"autor": autor, "hora": hora, "conteudo": conteudo, "tipo": tipo})
    return mensagens


def _carregar_config_supabase() -> dict:
    try:
        client = _supabase_client()
        if not client:
            return {}
        result = client.table("configuracoes").select("valor").eq("chave", "app_config").execute()
        if result.data:
            valor = result.data[0].get("valor") or {}
            if isinstance(valor, str):
                import json
                valor = json.loads(valor)
            return valor
        return {}
    except Exception:
        return {}


def _salvar_config_supabase(config: dict) -> None:
    try:
        client = _supabase_client()
        if not client:
            return
        client.table("configuracoes").upsert({"chave": "app_config", "valor": config}).execute()
    except Exception:
        pass


def _atualizar_nota_supabase(avaliacao_id: int, nova_nota: float, justificativa: str):
    try:
        client = _supabase_client()
        if not client:
            return
        nova_status = (
            "Excelente" if nova_nota >= 8 else
            "Bom" if nova_nota >= 6 else
            "Regular" if nova_nota >= 4 else
            "Crítico"
        )
        client.table("avaliacao").update({
            "nota": nova_nota,
            "nota_revisada": nova_nota,
            "status": nova_status,
            "justificativa_revisao": justificativa,
        }).eq("id", avaliacao_id).execute()
    except Exception:
        pass


def _vincular_atendente_supabase(avaliacao_id: int, responsavel: str) -> bool:
    try:
        client = _supabase_client()
        if not client:
            return False
        client.table("avaliacao").update({"responsavel": responsavel}).eq("id", avaliacao_id).execute()
        return True
    except Exception:
        return False


def _marcar_conferido_supabase(avaliacao_id: int, usuario: str) -> bool:
    try:
        from datetime import datetime
        client = _supabase_client()
        if not client:
            return False
        client.table("avaliacao").update({
            "conferido": True,
            "conferido_por": usuario,
            "conferido_em": datetime.utcnow().isoformat(),
        }).eq("id", avaliacao_id).execute()
        return True
    except Exception:
        return False


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
        pontos_criticos=d.get("pontos_criticos", ""),
        feedback_final=d.get("feedback_final", ""),
        justificativa_revisao=d.get("justificativa_revisao", "") or "",
        data_avaliacao=d.get("data_avaliacao", ""),
        conferido=bool(d.get("conferido", False)),
        conferido_por=d.get("conferido_por", "") or "",
    )


# ---------------------------------------------------------------------------
# App state
# ---------------------------------------------------------------------------

class AppState(rx.State):
    # Evaluations
    avaliacoes: list[AvaliacaoItem] = []
    selected_avaliacao: AvaliacaoItem = AvaliacaoItem()
    show_drawer: bool = False
    pending_open_avaliacao_id: int = 0
    show_desconsiderar_confirm: bool = False
    show_vincular_atendente: bool = False
    vincular_atendente_selecionado: str = ""
    editando_nota: bool = False
    revisar_nova_nota: str = ""
    revisar_justificativa: str = ""

    selected_atendente_nome: str = ""
    show_atendente_modal: bool = False

    audit_logs: list[AuditLogItem] = []
    erros_fila: list[ErroItem] = []
    atendentes: list[AtendenteItem] = []
    search_atendentes: str = ""

    # Users
    usuarios: list[UserItem] = []
    show_user_form: bool = False
    editando_usuario: bool = False
    user_form_id: int = 0
    user_form_nome: str = ""
    user_form_email: str = ""
    user_form_senha: str = ""
    user_form_is_admin: bool = False
    user_form_atendente_nome: str = ""
    show_delete_confirm: bool = False
    user_delete_id: int = 0

    # Auth — cookie persists across refreshes
    auth_token: str = rx.Cookie("")
    current_user_nome: str = ""
    current_user_email: str = ""
    current_user_is_admin: bool = False
    current_user_atendente_nome: str = ""
    is_auth_checking: bool = True

    # Login form
    login_email: str = ""
    login_senha: str = ""
    login_error: str = ""
    login_loading: bool = False

    proximo_processamento: str = ""
    status_automacao: str = "Operacional"

    search_query: str = ""
    filter_status: str = ""
    filter_responsavel: str = ""
    filter_mes: str = ""
    filter_conferido: str = ""
    filter_revisado: str = ""

    tv_mode: bool = False

    # Historico da conversa (carregado lazily ao abrir avaliação)
    selected_avaliacao_historico: str = ""
    historico_loading: bool = False
    drawer_tab: str = "informacoes"

    # Aba ativa na página de Configurações
    config_aba: str = "usuarios"

    # Config
    config_prompt_avaliacao: str = PROMPT_AVALIACAO
    config_prompt_editando: bool = False
    config_prompt_backup: str = ""
    config_nota_excelente: str = "8.0"
    config_nota_bom: str = "6.0"
    config_nota_regular: str = "4.0"
    config_etiqueta_revisao_nome: str = "Revisado"
    config_etiqueta_revisao_cor: str = "amber"

    # Atendimentos em atraso
    atrasados_log: list[AtrasadoLogItem] = []
    filter_mes_atrasos: str = ""
    atrasos_search: str = ""
    filter_setor_atrasos: str = ""
    filter_data_inicio_atrasos: str = ""
    filter_data_fim_atrasos: str = ""

    # Histórico de ciclos de automação
    ciclos_log: list[CicloLogItem] = []
    ciclo_rodando: bool = False

    # -----------------------------------------------------------------------
    # Computed vars
    # -----------------------------------------------------------------------

    @rx.var
    def current_path(self) -> str:
        return self.router.url.path

    @rx.var
    def ultimo_processamento(self) -> str:
        for log in self.audit_logs:
            if log.acao == "Avaliação processada":
                return log.criado_em
        return "Sem registros"

    @rx.var
    def processados_hoje(self) -> int:
        from datetime import datetime, timezone, timedelta
        hoje = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d")
        return sum(
            1 for av in self.avaliacoes
            if av.data_avaliacao and av.data_avaliacao[:10] == hoje
        )

    @rx.var
    def historico_da_conversa(self) -> list[MensagemItem]:
        items = _parse_historico_conversa(
            self.selected_avaliacao_historico,
            self.selected_avaliacao.cliente,
        )
        return [MensagemItem(**d) for d in items]


    @rx.var
    def meses_disponiveis(self) -> list[str]:
        meses = set()
        for av in self.avaliacoes:
            if av.data_avaliacao and len(av.data_avaliacao) >= 7 and av.data_avaliacao[4:5] == "-":
                meses.add(f"{av.data_avaliacao[5:7]}/{av.data_avaliacao[0:4]}")
            elif av.data_atendimento and len(av.data_atendimento) >= 7:
                partes = av.data_atendimento.split("/")
                if len(partes) == 3:
                    meses.add(f"{partes[1]}/{partes[2]}")
        return sorted(list(meses), reverse=True)

    @rx.var
    def avaliacoes_do_mes(self) -> list[AvaliacaoItem]:
        """Month filter only (no role filter here)."""
        if not self.filter_mes:
            return self.avaliacoes
        result = []
        for a in self.avaliacoes:
            if a.data_avaliacao and len(a.data_avaliacao) >= 7 and a.data_avaliacao[4:5] == "-":
                if self.filter_mes == f"{a.data_avaliacao[5:7]}/{a.data_avaliacao[0:4]}":
                    result.append(a)
            elif self.filter_mes in (a.data_atendimento or ""):
                result.append(a)
        return result

    @rx.var
    def avaliacoes_visiveis(self) -> list[AvaliacaoItem]:
        """Month + role filtered base for all UI computations."""
        base = self.avaliacoes_do_mes
        if self.current_user_is_admin:
            return base
        if not self.current_user_atendente_nome:
            return []
        return [a for a in base if a.responsavel == self.current_user_atendente_nome]

    @rx.var
    def monthly_data(self) -> list[dict]:
        _MESES = {
            "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
            "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
            "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
        }
        base = self.avaliacoes
        if not self.current_user_is_admin and self.current_user_atendente_nome:
            base = [a for a in base if a.responsavel == self.current_user_atendente_nome]
        month_stats: dict[str, list] = {}
        for av in base:
            key = ""
            if av.data_avaliacao and len(av.data_avaliacao) >= 7 and av.data_avaliacao[4:5] == "-":
                key = f"{av.data_avaliacao[5:7]}/{av.data_avaliacao[0:4]}"
            elif av.data_atendimento:
                partes = av.data_atendimento.split("/")
                if len(partes) == 3:
                    key = f"{partes[1]}/{partes[2]}"
            if not key:
                continue
            if key not in month_stats:
                month_stats[key] = []
            month_stats[key].append(av.nota)
        sorted_keys = sorted(
            month_stats.keys(),
            key=lambda k: (k.split("/")[1], k.split("/")[0]) if "/" in k else ("", ""),
        )
        result = []
        for key in sorted_keys:
            notas = month_stats[key]
            mes_num = key.split("/")[0]
            result.append({
                "mes": _MESES.get(mes_num, mes_num),
                "nota_media": round(sum(notas) / len(notas), 1) if notas else 0.0,
                "total": len(notas),
            })
        return result[-7:]

    @rx.var
    def ranking_data(self) -> list[RankingItem]:
        stats: dict[str, list] = {}
        for av in self.avaliacoes_visiveis:
            nome = av.responsavel
            if nome not in stats:
                stats[nome] = []
            stats[nome].append(av.nota)
        items = sorted(
            [
                {
                    "nome": k,
                    "nota": round(sum(v) / len(v), 1),
                    "total": len(v),
                    "aprovados": sum(1 for n in v if n >= 7.0),
                }
                for k, v in stats.items()
            ],
            key=lambda x: x["nota"],
            reverse=True,
        )
        return [
            RankingItem(posicao=i + 1, nome=x["nome"], nota=x["nota"], total=x["total"], aprovados=x["aprovados"])
            for i, x in enumerate(items[:7])
        ]

    @rx.var
    def total_avaliacoes(self) -> int:
        return len(self.avaliacoes_visiveis)

    @rx.var
    def nota_media(self) -> str:
        base = self.avaliacoes_visiveis
        if not base:
            return "0.0"
        return f"{sum(a.nota for a in base) / len(base):.1f}"

    @rx.var
    def taxa_aprovacao(self) -> str:
        base = self.avaliacoes_visiveis
        if not base:
            return "0%"
        aprovados = sum(1 for a in base if a.nota >= 7.0)
        return f"{(aprovados / len(base) * 100):.0f}%"

    @rx.var
    def tempo_medio(self) -> str:
        base = self.avaliacoes_visiveis
        if not base:
            return "0 min"
        tempos = sorted(a.tempo_minutos for a in base)
        mid = len(tempos) // 2
        mediana = tempos[mid] if len(tempos) % 2 else (tempos[mid - 1] + tempos[mid]) // 2
        return f"{mediana} min"

    @rx.var
    def avaliacoes_filtradas(self) -> list[AvaliacaoItem]:
        result = self.avaliacoes_visiveis
        if self.search_query:
            q = self.search_query.lower()
            result = [a for a in result if q in a.cliente.lower() or q in a.responsavel.lower() or q in a.protocolo.lower()]
        if self.filter_status:
            result = [a for a in result if a.status == self.filter_status]
        if self.filter_responsavel:
            result = [a for a in result if a.responsavel == self.filter_responsavel]
        if self.filter_conferido == "Atestado":
            result = [a for a in result if a.conferido]
        elif self.filter_conferido == "Pendente":
            result = [a for a in result if not a.conferido and a.status in ("Regular", "Crítico")]
        if self.filter_revisado == "Revisados":
            result = [a for a in result if a.justificativa_revisao != ""]
        elif self.filter_revisado == "Sem revisão":
            result = [a for a in result if a.justificativa_revisao == ""]
        return result


    @rx.var
    def atendentes_nomes(self) -> list[str]:
        return sorted(list(set(a.responsavel for a in self.avaliacoes)))

    @rx.var
    def meses_com_todos(self) -> list[str]:
        return ["Todos"] + self.meses_disponiveis

    @rx.var
    def atendentes_com_todos(self) -> list[str]:
        return ["Todos"] + self.atendentes_nomes

    @rx.var
    def atendentes_identificados(self) -> list[str]:
        return sorted([
            n for n in set(a.responsavel for a in self.avaliacoes)
            if n and "identificado" not in n.lower()
        ])

    @rx.var
    def selected_e_nao_identificado(self) -> bool:
        r = self.selected_avaliacao.responsavel
        return not r or "identificado" in r.lower()

    @rx.var
    def filter_mes_display(self) -> str:
        return self.filter_mes if self.filter_mes else "Todos"

    @rx.var
    def filter_status_display(self) -> str:
        return self.filter_status if self.filter_status else "Todos"

    @rx.var
    def filter_responsavel_display(self) -> str:
        return self.filter_responsavel if self.filter_responsavel else "Todos"

    @rx.var
    def filter_conferido_display(self) -> str:
        return self.filter_conferido if self.filter_conferido else "Todos"

    @rx.var
    def filter_revisado_display(self) -> str:
        return self.filter_revisado if self.filter_revisado else "Todos"

    @rx.var
    def avaliacoes_criticas(self) -> list[AvaliacaoItem]:
        return [a for a in self.avaliacoes_visiveis if a.nota < 6.0]

    @rx.var
    def selected_precisa_conferencia(self) -> bool:
        return self.selected_avaliacao.status in ("Regular", "Crítico")

    @rx.var
    def atendentes_do_mes(self) -> list[AtendenteItem]:
        stats: dict[str, dict] = {}
        for av in self.avaliacoes_visiveis:
            nome = av.responsavel
            if nome not in stats:
                stats[nome] = {"total": 0, "notas": []}
            stats[nome]["total"] += 1
            stats[nome]["notas"].append(av.nota)
        lookup = {at.nome: at for at in self.atendentes}
        result = []
        for nome, s in stats.items():
            base = lookup.get(nome, AtendenteItem(nome=nome, email=""))
            nota_media = round(sum(s["notas"]) / len(s["notas"]), 1) if s["notas"] else 0.0
            result.append(AtendenteItem(
                id=base.id,
                nome=nome,
                email=base.email,
                ativo=base.ativo,
                total=s["total"],
                nota_media=nota_media,
            ))
        return sorted(result, key=lambda x: x.nota_media, reverse=True)

    @rx.var
    def atendentes_filtrados(self) -> list[AtendenteItem]:
        items = self.atendentes_do_mes
        if self.search_atendentes:
            q = self.search_atendentes.lower()
            items = [a for a in items if q in a.nome.lower()]
        return items

    @rx.var
    def ranking_volume_data(self) -> list[RankingItem]:
        stats: dict[str, list] = {}
        for av in self.avaliacoes_visiveis:
            nome = av.responsavel
            if nome not in stats:
                stats[nome] = []
            stats[nome].append(av.nota)
        items = sorted(
            [
                {
                    "nome": k,
                    "nota": round(sum(v) / len(v), 1),
                    "total": len(v),
                    "aprovados": sum(1 for n in v if n >= 7.0),
                }
                for k, v in stats.items()
            ],
            key=lambda x: x["total"],
            reverse=True,
        )
        return [
            RankingItem(posicao=i + 1, nome=x["nome"], nota=x["nota"], total=x["total"], aprovados=x["aprovados"])
            for i, x in enumerate(items[:7])
        ]

    @rx.var
    def avaliacoes_do_atendente(self) -> list[AvaliacaoItem]:
        if not self.selected_atendente_nome:
            return []
        return sorted(
            [a for a in self.avaliacoes_visiveis if a.responsavel == self.selected_atendente_nome],
            key=lambda x: x.nota,
        )

    @rx.var
    def atendente_selecionado_stats(self) -> dict:
        avs = self.avaliacoes_do_atendente
        if not avs:
            return {"total": 0, "nota_media": 0.0, "aprovados": 0, "criticos": 0}
        notas = [a.nota for a in avs]
        return {
            "total": len(avs),
            "nota_media": round(sum(notas) / len(notas), 1),
            "aprovados": sum(1 for n in notas if n >= 7.0),
            "criticos": sum(1 for n in notas if n < 6.0),
        }

    # -----------------------------------------------------------------------
    # Atrasos computed vars
    # -----------------------------------------------------------------------

    @rx.var
    def meses_disponiveis_atrasos(self) -> list[str]:
        meses = set()
        for item in self.atrasados_log:
            ts = item.criado_em
            if ts and len(ts) >= 7:
                meses.add(f"{ts[5:7]}/{ts[0:4]}")
        return sorted(list(meses), reverse=True)

    @rx.var
    def atrasados_do_mes(self) -> list[AtrasadoLogItem]:
        if not self.filter_mes_atrasos:
            return self.atrasados_log
        if self.filter_mes_atrasos == "Personalizado":
            inicio = self.filter_data_inicio_atrasos
            fim = self.filter_data_fim_atrasos
            result = []
            for item in self.atrasados_log:
                ts = item.criado_em
                if ts and len(ts) >= 10:
                    date_str = ts[:10]
                    ok_inicio = (not inicio) or date_str >= inicio
                    ok_fim = (not fim) or date_str <= fim
                    if ok_inicio and ok_fim:
                        result.append(item)
            return result
        result = []
        for item in self.atrasados_log:
            ts = item.criado_em
            if ts and len(ts) >= 7:
                if f"{ts[5:7]}/{ts[0:4]}" == self.filter_mes_atrasos:
                    result.append(item)
        return result

    @rx.var
    def usar_periodo_personalizado(self) -> bool:
        return self.filter_mes_atrasos == "Personalizado"

    @rx.var
    def meses_atrasos_com_todos(self) -> list[str]:
        return ["Todos", "Personalizado"] + self.meses_disponiveis_atrasos

    @rx.var
    def filter_mes_atrasos_display(self) -> str:
        return self.filter_mes_atrasos if self.filter_mes_atrasos else "Todos"

    @rx.var
    def setores_disponiveis_atrasos(self) -> list[str]:
        grupos: dict = {}
        for item in self.atrasados_log:
            if item.setor:
                norm = _normalizar_setor(item.setor)
                if norm not in grupos:
                    grupos[norm] = item.setor
                elif _tem_acento(item.setor) and not _tem_acento(grupos[norm]):
                    grupos[norm] = item.setor
        return sorted(grupos.values())

    @rx.var
    def setores_com_todos_atrasos(self) -> list[str]:
        return ["Todos"] + self.setores_disponiveis_atrasos

    @rx.var
    def filter_setor_atrasos_display(self) -> str:
        return self.filter_setor_atrasos if self.filter_setor_atrasos else "Todos"

    @rx.var
    def atrasos_por_departamento(self) -> list[DeptAtrasoItem]:
        dept_canonical: dict = {}
        dept_clientes: dict = {}
        dept_ocorrencias: dict = {}
        for item in self.atrasados_do_mes:
            setor = item.setor if item.setor else "Não informado"
            norm = _normalizar_setor(setor)
            if norm not in dept_clientes:
                dept_canonical[norm] = setor
                dept_clientes[norm] = []
                dept_ocorrencias[norm] = 0
            elif _tem_acento(setor) and not _tem_acento(dept_canonical[norm]):
                dept_canonical[norm] = setor
            if item.cliente not in dept_clientes[norm]:
                dept_clientes[norm].append(item.cliente)
            dept_ocorrencias[norm] += 1
        result = [
            DeptAtrasoItem(setor=dept_canonical[n], clientes=len(dept_clientes[n]), ocorrencias=dept_ocorrencias[n])
            for n in dept_clientes
        ]
        return sorted(result, key=lambda x: x.ocorrencias, reverse=True)

    @rx.var
    def atrasados_agrupados(self) -> list[AtrasadoAgrupadoItem]:
        base = self.atrasados_do_mes
        if self.filter_setor_atrasos:
            norm_filter = _normalizar_setor(self.filter_setor_atrasos)
            base = [item for item in base if _normalizar_setor(item.setor) == norm_filter]
        grupos: dict = {}
        for item in base:
            cliente = item.cliente.strip() if item.cliente.strip() else "Não identificado"
            if cliente not in grupos:
                grupos[cliente] = {"count": 0, "setores": [], "protocolos": [], "ultima": ""}
            g = grupos[cliente]
            g["count"] += 1
            if item.setor and item.setor not in g["setores"]:
                g["setores"].append(item.setor)
            if item.chamado_id and item.chamado_id not in g["protocolos"]:
                g["protocolos"].append(item.chamado_id)
            if not g["ultima"] or item.criado_em > g["ultima"]:
                g["ultima"] = item.criado_em

        result = []
        for cliente, g in grupos.items():
            ultima = g["ultima"]
            if ultima and len(ultima) >= 10:
                p = ultima[:10].split("-")
                ultima_fmt = f"{p[2]}/{p[1]}/{p[0]}" if len(p) == 3 else ultima[:10]
            else:
                ultima_fmt = ultima or "—"
            protos = g["protocolos"]
            protos_fmt = ", ".join(protos[:3]) + (" ..." if len(protos) > 3 else "") if protos else "—"
            result.append(AtrasadoAgrupadoItem(
                cliente=cliente,
                total_esperas=g["count"],
                setores=", ".join(sorted(g["setores"])) if g["setores"] else "—",
                protocolos=protos_fmt,
                ultima_data=ultima_fmt,
            ))

        sorted_result = sorted(result, key=lambda x: x.total_esperas, reverse=True)
        if self.atrasos_search:
            q = self.atrasos_search.lower()
            sorted_result = [r for r in sorted_result if q in r.cliente.lower()]
        return sorted_result

    @rx.var
    def atrasos_total_registros(self) -> int:
        return len(self.atrasados_do_mes)

    @rx.var
    def atrasos_total_clientes(self) -> int:
        return len(self.atrasados_agrupados)

    @rx.var
    def atrasos_total_protocolos(self) -> int:
        protos = set()
        for item in self.atrasados_do_mes:
            if item.chamado_id:
                protos.add(item.chamado_id)
        return len(protos)

    @rx.var
    def periodo_atual_descricao(self) -> str:
        from datetime import datetime, timezone, timedelta
        hora = datetime.now(timezone(timedelta(hours=-3))).hour
        if 12 <= hora < 16:
            return "00:00 → 11:59 (manhã de hoje)"
        if 16 <= hora < 24:
            return "12:00 → 15:59 (tarde de hoje)"
        return "16:00 → 23:59 (noite de ontem)"

    @rx.var
    def atrasos_setor_mais_afetado(self) -> str:
        contador: dict = {}
        for item in self.atrasados_do_mes:
            if item.setor:
                contador[item.setor] = contador.get(item.setor, 0) + 1
        if not contador:
            return "—"
        return max(contador, key=lambda k: contador[k])

    # -----------------------------------------------------------------------
    # Auth event handlers
    # -----------------------------------------------------------------------

    @rx.event
    def set_login_email(self, value: str):
        self.login_email = value

    @rx.event
    def set_login_senha(self, value: str):
        self.login_senha = value

    @rx.event
    def fazer_login(self):
        self.login_error = ""
        self.login_loading = True
        if not self.login_email or not self.login_senha:
            self.login_error = "Preencha email e senha."
            self.login_loading = False
            return
        user = _verificar_login_supabase(self.login_email, self.login_senha)
        if not user:
            self.login_error = "Email ou senha incorretos."
            self.login_loading = False
            return
        token = secrets.token_urlsafe(32)
        _SESSIONS[token] = {
            "nome": user["nome"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
            "atendente_nome": user.get("atendente_nome", ""),
        }
        self.auth_token = token
        self.current_user_nome = user["nome"]
        self.current_user_email = user["email"]
        self.current_user_is_admin = user.get("is_admin", False)
        self.current_user_atendente_nome = user.get("atendente_nome", "")
        self.login_email = ""
        self.login_senha = ""
        self.login_loading = False
        return rx.redirect("/")

    @rx.event
    def fazer_logout(self):
        if self.auth_token in _SESSIONS:
            del _SESSIONS[self.auth_token]
        self.auth_token = ""
        self.current_user_nome = ""
        self.current_user_email = ""
        self.current_user_is_admin = False
        self.current_user_atendente_nome = ""
        return rx.redirect("/login")

    @rx.event
    def verificar_auth(self):
        """Guard for pages accessible by all authenticated users."""
        if not self.auth_token or self.auth_token not in _SESSIONS:
            self.auth_token = ""
            self.is_auth_checking = False
            return rx.redirect("/login")
        session = _SESSIONS[self.auth_token]
        self.current_user_nome = session["nome"]
        self.current_user_email = session["email"]
        self.current_user_is_admin = session["is_admin"]
        self.current_user_atendente_nome = session["atendente_nome"]
        self.is_auth_checking = False
        yield AppState.carregar_dados

    @rx.event
    def verificar_auth_admin(self):
        """Guard for admin-only pages."""
        if not self.auth_token or self.auth_token not in _SESSIONS:
            self.auth_token = ""
            self.is_auth_checking = False
            return rx.redirect("/login")
        session = _SESSIONS[self.auth_token]
        self.current_user_nome = session["nome"]
        self.current_user_email = session["email"]
        self.current_user_is_admin = session["is_admin"]
        self.current_user_atendente_nome = session["atendente_nome"]
        self.is_auth_checking = False
        if not self.current_user_is_admin:
            return rx.redirect("/")
        yield AppState.carregar_dados

    # -----------------------------------------------------------------------
    # Evaluation event handlers
    # -----------------------------------------------------------------------

    @rx.event
    def abrir_confirmar_desconsiderar(self):
        self.show_desconsiderar_confirm = True

    @rx.event
    def cancelar_desconsiderar(self, open: bool = False):
        if not open:
            self.show_desconsiderar_confirm = False

    @rx.event
    def fechar_desconsiderar(self):
        self.show_desconsiderar_confirm = False

    @rx.event
    def desconsiderar_avaliacao(self):
        av = self.selected_avaliacao
        _deletar_avaliacao_supabase(av.id)
        _registrar_audit_supabase(
            usuario=self.current_user_nome or "Sistema",
            acao="Avaliação desconsiderada",
            entidade_id=av.protocolo,
            detalhes=f"Desconsiderado por {self.current_user_nome} — removido do banco",
        )
        self.avaliacoes = [a for a in self.avaliacoes if a.id != av.id]
        self.show_desconsiderar_confirm = False
        self.show_drawer = False
        self.editando_nota = False
        self.selected_avaliacao = AvaliacaoItem()

    @rx.event
    def open_avaliacao(self, avaliacao_id: int):
        for av in self.avaliacoes:
            if av.id == avaliacao_id:
                self.selected_avaliacao = av
                self.show_drawer = True
                self.selected_avaliacao_historico = ""
                self.historico_loading = True
                self.drawer_tab = "informacoes"
                return AppState.carregar_historico

    @rx.event
    def navegar_para_avaliacao(self, avaliacao_id: int):
        self.pending_open_avaliacao_id = avaliacao_id
        return rx.redirect("/avaliacoes")

    @rx.event
    def close_drawer(self, open: bool = False):
        if not open:
            self.show_drawer = False
            self.editando_nota = False
            self.selected_avaliacao = AvaliacaoItem()
            self.selected_avaliacao_historico = ""
            self.historico_loading = False
            self.drawer_tab = "informacoes"

    @rx.event
    def set_config_aba(self, value: str):
        self.config_aba = value

    @rx.event
    def open_revisar_nota(self):
        self.revisar_nova_nota = str(self.selected_avaliacao.nota)
        self.revisar_justificativa = ""
        self.editando_nota = True

    @rx.event
    def cancelar_revisao(self):
        self.editando_nota = False
        self.revisar_nova_nota = ""
        self.revisar_justificativa = ""

    @rx.event
    def set_revisar_nova_nota(self, value: str):
        self.revisar_nova_nota = value

    @rx.event
    def set_revisar_justificativa(self, value: str):
        self.revisar_justificativa = value

    @rx.event
    def salvar_revisao_nota(self):
        try:
            nova_nota = float(self.revisar_nova_nota)
        except (ValueError, TypeError):
            return
        nova_nota = max(0.0, min(10.0, nova_nota))
        nova_status = (
            "Excelente" if nova_nota >= 8 else
            "Bom" if nova_nota >= 6 else
            "Regular" if nova_nota >= 4 else
            "Crítico"
        )
        av_id = self.selected_avaliacao.id
        justificativa = self.revisar_justificativa
        updated: AvaliacaoItem | None = None
        for av in self.avaliacoes:
            if av.id == av_id:
                updated = AvaliacaoItem(
                    id=av.id, protocolo=av.protocolo, cliente=av.cliente,
                    responsavel=av.responsavel, data_atendimento=av.data_atendimento,
                    hora_inicio=av.hora_inicio, hora_fim=av.hora_fim,
                    tempo_minutos=av.tempo_minutos, tempo_formatado=av.tempo_formatado,
                    nota=nova_nota, status=nova_status,
                    pontos_criticos=av.pontos_criticos, feedback_final=av.feedback_final,
                    justificativa_revisao=justificativa,
                    data_avaliacao=av.data_avaliacao,
                    conferido=av.conferido,
                    conferido_por=av.conferido_por,
                )
                break
        if updated is None:
            return
        # Reassign the full list so Reflex detects the change reliably
        self.avaliacoes = [updated if av.id == av_id else av for av in self.avaliacoes]
        self.selected_avaliacao = updated
        _atualizar_nota_supabase(av_id, nova_nota, justificativa)
        self.editando_nota = False
        self.revisar_nova_nota = ""
        self.revisar_justificativa = ""

    @rx.event
    def marcar_conferido(self):
        av = self.selected_avaliacao
        if not av.id or av.conferido:
            return
        usuario = self.current_user_nome
        _marcar_conferido_supabase(av.id, usuario)
        _registrar_audit_supabase(
            usuario=usuario,
            acao="Avaliação atestada",
            entidade_id=av.protocolo,
            detalhes=f"Conferido por {usuario} sem alteração de nota",
        )
        updated = AvaliacaoItem(
            id=av.id, protocolo=av.protocolo, cliente=av.cliente,
            responsavel=av.responsavel, data_atendimento=av.data_atendimento,
            hora_inicio=av.hora_inicio, hora_fim=av.hora_fim,
            tempo_minutos=av.tempo_minutos, tempo_formatado=av.tempo_formatado,
            nota=av.nota, status=av.status,
            pontos_criticos=av.pontos_criticos, feedback_final=av.feedback_final,
            justificativa_revisao=av.justificativa_revisao,
            data_avaliacao=av.data_avaliacao,
            conferido=True,
            conferido_por=usuario,
        )
        self.avaliacoes = [updated if a.id == av.id else a for a in self.avaliacoes]
        self.selected_avaliacao = updated

    @rx.event
    def open_vincular_atendente(self):
        self.vincular_atendente_selecionado = ""
        self.show_vincular_atendente = True

    @rx.event
    def fechar_vincular_atendente(self):
        self.show_vincular_atendente = False
        self.vincular_atendente_selecionado = ""

    @rx.event
    def close_vincular_atendente(self, open: bool = False):
        if not open:
            self.show_vincular_atendente = False
            self.vincular_atendente_selecionado = ""

    @rx.event
    def set_vincular_atendente_selecionado(self, value: str):
        self.vincular_atendente_selecionado = value

    @rx.event
    def confirmar_vincular_atendente(self):
        if not self.vincular_atendente_selecionado:
            return
        av = self.selected_avaliacao
        novo = self.vincular_atendente_selecionado
        _vincular_atendente_supabase(av.id, novo)
        _registrar_audit_supabase(
            usuario=self.current_user_nome,
            acao="Atendente vinculado",
            entidade_id=av.protocolo,
            detalhes=f"Atendente vinculado: {novo} (era: Não identificado)",
        )
        updated = AvaliacaoItem(
            id=av.id, protocolo=av.protocolo, cliente=av.cliente,
            responsavel=novo, data_atendimento=av.data_atendimento,
            hora_inicio=av.hora_inicio, hora_fim=av.hora_fim,
            tempo_minutos=av.tempo_minutos, tempo_formatado=av.tempo_formatado,
            nota=av.nota, status=av.status,
            pontos_criticos=av.pontos_criticos, feedback_final=av.feedback_final,
            justificativa_revisao=av.justificativa_revisao,
            data_avaliacao=av.data_avaliacao,
            conferido=av.conferido,
            conferido_por=av.conferido_por,
        )
        self.avaliacoes = [updated if a.id == av.id else a for a in self.avaliacoes]
        self.selected_avaliacao = updated
        self.show_vincular_atendente = False
        self.vincular_atendente_selecionado = ""

    # -----------------------------------------------------------------------
    # Filter event handlers
    # -----------------------------------------------------------------------

    @rx.event
    def set_search(self, value: str):
        self.search_query = value

    @rx.event
    def set_filter_status(self, value: str):
        self.filter_status = "" if value == "Todos" else value

    @rx.event
    def set_filter_responsavel(self, value: str):
        self.filter_responsavel = "" if value == "Todos" else value

    @rx.event
    def set_filter_conferido(self, value: str):
        self.filter_conferido = "" if value == "Todos" else value

    @rx.event
    def set_filter_revisado(self, value: str):
        self.filter_revisado = "" if value == "Todos" else value

    @rx.event
    def set_search_atendentes(self, value: str):
        self.search_atendentes = value

    @rx.event
    def set_mes_atual(self):
        from datetime import datetime
        now = datetime.now()
        self.filter_mes = f"{now.month:02d}/{now.year}"

    @rx.event
    def set_filter_mes(self, value: str):
        self.filter_mes = "" if value == "Todos" else value

    @rx.event
    def open_atendente(self, nome: str):
        self.selected_atendente_nome = nome
        self.show_atendente_modal = True

    @rx.event
    def close_atendente(self):
        self.selected_atendente_nome = ""
        self.show_atendente_modal = False

    @rx.event
    def clear_filters(self):
        self.search_query = ""
        self.filter_status = ""
        self.filter_responsavel = ""
        self.filter_mes = ""
        self.filter_conferido = ""
        self.filter_revisado = ""

    @rx.event
    def set_filter_mes_atrasos(self, value: str):
        self.filter_mes_atrasos = "" if value == "Todos" else value

    @rx.event
    def set_atrasos_search(self, value: str):
        self.atrasos_search = value

    @rx.event
    def set_filter_setor_atrasos(self, value: str):
        self.filter_setor_atrasos = "" if value == "Todos" else value

    @rx.event
    def set_filter_data_inicio_atrasos(self, value: str):
        self.filter_data_inicio_atrasos = value

    @rx.event
    def set_filter_data_fim_atrasos(self, value: str):
        self.filter_data_fim_atrasos = value

    @rx.event
    def clear_atrasos_filters(self):
        self.filter_mes_atrasos = ""
        self.atrasos_search = ""
        self.filter_setor_atrasos = ""
        self.filter_data_inicio_atrasos = ""
        self.filter_data_fim_atrasos = ""

    @rx.event
    def toggle_tv_mode(self):
        self.tv_mode = not self.tv_mode

    # -----------------------------------------------------------------------
    # User management event handlers
    # -----------------------------------------------------------------------

    @rx.event
    def open_add_user(self):
        self.editando_usuario = False
        self.user_form_id = 0
        self.user_form_nome = ""
        self.user_form_email = ""
        self.user_form_senha = ""
        self.user_form_is_admin = False
        self.user_form_atendente_nome = ""
        self.show_user_form = True

    @rx.event
    def open_edit_user(self, user_id: int):
        for u in self.usuarios:
            if u.id == user_id:
                self.editando_usuario = True
                self.user_form_id = u.id
                self.user_form_nome = u.nome
                self.user_form_email = u.email
                self.user_form_senha = ""
                self.user_form_is_admin = u.is_admin
                self.user_form_atendente_nome = u.atendente_nome
                self.show_user_form = True
                return

    @rx.event
    def close_user_form(self, open: bool = False):
        if not open:
            self.show_user_form = False
            self.editando_usuario = False

    @rx.event
    def set_user_form_nome(self, value: str):
        self.user_form_nome = value

    @rx.event
    def set_user_form_email(self, value: str):
        self.user_form_email = value

    @rx.event
    def set_user_form_senha(self, value: str):
        self.user_form_senha = value

    @rx.event
    def set_user_form_is_admin(self, value: str):
        self.user_form_is_admin = value == "Admin"

    @rx.event
    def set_user_form_atendente_nome(self, value: str):
        self.user_form_atendente_nome = value

    @rx.event
    def save_user(self):
        if not self.user_form_nome or not self.user_form_email:
            return
        dados = {
            "id": self.user_form_id if self.editando_usuario else 0,
            "nome": self.user_form_nome,
            "email": self.user_form_email,
            "senha": self.user_form_senha,
            "is_admin": self.user_form_is_admin,
            "ativo": True,
            "atendente_nome": self.user_form_atendente_nome,
        }
        new_id = _salvar_usuario_supabase(dados)
        if self.editando_usuario:
            for i, u in enumerate(self.usuarios):
                if u.id == self.user_form_id:
                    self.usuarios[i] = UserItem(
                        id=u.id,
                        nome=self.user_form_nome,
                        email=self.user_form_email,
                        is_admin=self.user_form_is_admin,
                        ativo=u.ativo,
                        atendente_nome=self.user_form_atendente_nome,
                    )
                    break
        else:
            use_id = new_id if new_id else (max((u.id for u in self.usuarios), default=0) + 1)
            self.usuarios.append(UserItem(
                id=use_id,
                nome=self.user_form_nome,
                email=self.user_form_email,
                is_admin=self.user_form_is_admin,
                ativo=True,
                atendente_nome=self.user_form_atendente_nome,
            ))
        self.show_user_form = False
        self.editando_usuario = False

    @rx.event
    def confirm_delete_user(self, user_id: int):
        self.user_delete_id = user_id
        self.show_delete_confirm = True

    @rx.event
    def cancel_delete_user(self, open: bool = False):
        if not open:
            self.user_delete_id = 0
            self.show_delete_confirm = False

    @rx.event
    def delete_user(self):
        _deletar_usuario_supabase(self.user_delete_id)
        self.usuarios = [u for u in self.usuarios if u.id != self.user_delete_id]
        self.user_delete_id = 0
        self.show_delete_confirm = False

    @rx.event
    def carregar_historico(self):
        historico = _carregar_historico_supabase(self.selected_avaliacao.id)
        self.selected_avaliacao_historico = historico
        self.historico_loading = False

    @rx.event
    def set_drawer_tab(self, value: str):
        self.drawer_tab = value

    @rx.event
    def set_config_prompt_avaliacao(self, value: str):
        self.config_prompt_avaliacao = value

    @rx.event
    def iniciar_edicao_prompt(self):
        self.config_prompt_backup = self.config_prompt_avaliacao
        self.config_prompt_editando = True

    @rx.event
    def cancelar_edicao_prompt(self):
        self.config_prompt_avaliacao = self.config_prompt_backup
        self.config_prompt_editando = False
        self.config_prompt_backup = ""

    @rx.event
    def salvar_prompt(self):
        if "{relatorio}" not in self.config_prompt_avaliacao:
            yield rx.toast.error("O marcador {relatorio} é obrigatório no prompt.")
            return
        _salvar_config_supabase({
            "nota_excelente": self.config_nota_excelente,
            "nota_bom": self.config_nota_bom,
            "nota_regular": self.config_nota_regular,
            "prompt_avaliacao": self.config_prompt_avaliacao,
            "etiqueta_revisao_nome": self.config_etiqueta_revisao_nome,
            "etiqueta_revisao_cor": self.config_etiqueta_revisao_cor,
        })
        self.config_prompt_editando = False
        self.config_prompt_backup = ""
        yield rx.toast.success("Prompt salvo com sucesso!")

    @rx.event
    def restaurar_prompt_padrao(self):
        self.config_prompt_avaliacao = PROMPT_AVALIACAO

    @rx.event
    def set_config_nota_excelente(self, value: str):
        self.config_nota_excelente = value

    @rx.event
    def set_config_nota_bom(self, value: str):
        self.config_nota_bom = value

    @rx.event
    def set_config_nota_regular(self, value: str):
        self.config_nota_regular = value

    @rx.event
    def set_config_etiqueta_revisao_nome(self, value: str):
        self.config_etiqueta_revisao_nome = value

    @rx.event
    def set_config_etiqueta_revisao_cor(self, value: str):
        self.config_etiqueta_revisao_cor = value

    @rx.event
    def salvar_configuracoes(self):
        _salvar_config_supabase({
            "nota_excelente": self.config_nota_excelente,
            "nota_bom": self.config_nota_bom,
            "nota_regular": self.config_nota_regular,
            "prompt_avaliacao": self.config_prompt_avaliacao,
            "etiqueta_revisao_nome": self.config_etiqueta_revisao_nome,
            "etiqueta_revisao_cor": self.config_etiqueta_revisao_cor,
        })

    @rx.event(background=True)
    async def rodar_ciclo_manual(self):
        import asyncio
        async with self:
            if self.ciclo_rodando:
                return
            self.ciclo_rodando = True

        resultado = await asyncio.to_thread(_executar_ciclo_manual_thread)

        ciclos_db = _carregar_ciclos_supabase()
        dados_db = _carregar_do_supabase()
        audit_db = _carregar_audit_supabase()

        async with self:
            self.ciclo_rodando = False
            self.ciclos_log = [_dict_to_ciclo(c) for c in ciclos_db]
            if dados_db:
                self.avaliacoes = [_dict_to_avaliacao(d) for d in dados_db]
            if audit_db:
                self.audit_logs = [
                    AuditLogItem(
                        id=a.get("id", 0),
                        usuario=a.get("usuario", ""),
                        acao=a.get("acao", ""),
                        entidade=a.get("entidade", ""),
                        entidade_id=a.get("entidade_id", ""),
                        detalhes=a.get("detalhes", "").replace(" — gpt-4.1-mini", ""),
                        criado_em=str(a.get("criado_em", "")),
                    )
                    for a in audit_db
                ]

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
        from datetime import datetime, timezone, timedelta
        BRT = timezone(timedelta(hours=-3))
        agora = datetime.now(BRT)
        hora = agora.hour
        if hora < 12:
            prox = agora.replace(hour=12, minute=0, second=0, microsecond=0)
        elif hora < 16:
            prox = agora.replace(hour=16, minute=0, second=0, microsecond=0)
        else:
            prox = (agora + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        self.proximo_processamento = prox.strftime("%d/%m/%Y às %H:%M")

        config_db = _carregar_config_supabase()
        if config_db:
            self.config_nota_excelente = str(config_db.get("nota_excelente", "8.0"))
            self.config_nota_bom = str(config_db.get("nota_bom", "6.0"))
            self.config_nota_regular = str(config_db.get("nota_regular", "4.0"))
            prompt_salvo = config_db.get("prompt_avaliacao", "")
            if prompt_salvo and "{relatorio}" in prompt_salvo:
                self.config_prompt_avaliacao = prompt_salvo
            etiqueta_nome = config_db.get("etiqueta_revisao_nome", "")
            if etiqueta_nome:
                self.config_etiqueta_revisao_nome = etiqueta_nome
            etiqueta_cor = config_db.get("etiqueta_revisao_cor", "")
            if etiqueta_cor:
                self.config_etiqueta_revisao_cor = etiqueta_cor

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
                    detalhes=a.get("detalhes", "").replace(" — gpt-4.1-mini", ""),
                    criado_em=str(a.get("criado_em", "")),
                )
                for a in audit_db
            ]

        usuarios_db = _carregar_usuarios_supabase()
        if usuarios_db:
            self.usuarios = [
                UserItem(
                    id=u.get("id", 0),
                    nome=u.get("nome", ""),
                    email=u.get("email", ""),
                    is_admin=u.get("is_admin", False),
                    ativo=u.get("ativo", True),
                    atendente_nome=u.get("atendente_nome", ""),
                )
                for u in usuarios_db
            ]

        atrasados_db = _carregar_atrasados_supabase()
        self.atrasados_log = [_dict_to_atrasado(a) for a in atrasados_db]

        ciclos_db = _carregar_ciclos_supabase()
        self.ciclos_log = [_dict_to_ciclo(c) for c in ciclos_db]

        if self.pending_open_avaliacao_id:
            pending_id = self.pending_open_avaliacao_id
            self.pending_open_avaliacao_id = 0
            yield AppState.open_avaliacao(pending_id)
