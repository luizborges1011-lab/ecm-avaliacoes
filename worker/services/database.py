import os
from datetime import datetime
from supabase import create_client, Client

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        _client = create_client(url, key)
    return _client


def protocolo_ja_processado(protocolo: str) -> bool:
    result = _get_client().table("avaliacao").select("id").eq("protocolo", protocolo).execute()
    return len(result.data) > 0


def salvar_avaliacao(dados: dict) -> dict:
    result = _get_client().table("avaliacao").insert(dados).execute()
    return result.data[0] if result.data else {}


def adicionar_erro_fila(protocolo: str, erro: str, tentativas: int = 1) -> None:
    existing = (
        _get_client()
        .table("filaerros")
        .select("id, tentativas")
        .eq("protocolo", protocolo)
        .eq("resolvido", False)
        .execute()
    )
    if existing.data:
        row_id = existing.data[0]["id"]
        current = existing.data[0]["tentativas"]
        _get_client().table("filaerros").update({
            "tentativas": current + 1,
            "erro": erro,
        }).eq("id", row_id).execute()
    else:
        _get_client().table("filaerros").insert({
            "protocolo": protocolo,
            "erro": erro,
            "tentativas": tentativas,
            "resolvido": False,
        }).execute()


def registrar_audit(usuario: str, acao: str, entidade: str, entidade_id: str, detalhes: str = "") -> None:
    _get_client().table("auditlog").insert({
        "usuario": usuario,
        "acao": acao,
        "entidade": entidade,
        "entidade_id": entidade_id,
        "detalhes": detalhes,
        "criado_em": datetime.utcnow().isoformat(),
    }).execute()


def listar_avaliacoes(limit: int = 500) -> list[dict]:
    result = (
        _get_client()
        .table("avaliacao")
        .select("*")
        .order("data_avaliacao", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def listar_erros_pendentes() -> list[dict]:
    result = (
        _get_client()
        .table("filaerros")
        .select("*")
        .eq("resolvido", False)
        .order("criado_em", desc=True)
        .execute()
    )
    return result.data or []


def marcar_erro_resolvido(erro_id: int) -> None:
    _get_client().table("filaerros").update({"resolvido": True}).eq("id", erro_id).execute()


def carregar_prompt_avaliacao() -> str | None:
    """Retorna o prompt customizado salvo no Supabase, ou None se não configurado."""
    try:
        result = _get_client().table("configuracoes").select("valor").eq("chave", "app_config").execute()
        if result.data:
            valor = result.data[0].get("valor") or {}
            if isinstance(valor, str):
                import json
                valor = json.loads(valor)
            prompt = valor.get("prompt_avaliacao")
            if prompt and "{relatorio}" in prompt:
                return prompt
        return None
    except Exception:
        return None


def registrar_ciclo_log(tipo: str, total: int, sucesso: int, erros: int, periodo: str) -> None:
    import json
    from datetime import datetime
    detalhes = json.dumps({"total": total, "sucesso": sucesso, "erros": erros, "periodo": periodo})
    _get_client().table("auditlog").insert({
        "usuario": "Sistema",
        "acao": "Ciclo executado",
        "entidade": "Ciclo",
        "entidade_id": tipo,
        "detalhes": detalhes,
        "criado_em": datetime.utcnow().isoformat(),
    }).execute()


def registrar_atrasado(protocolo: str, nome_contato: str, departamento: str, tempo_espera_segundos: int) -> None:
    from datetime import datetime
    _get_client().table("atendimentos_atrasados_log").insert({
        "protocolo": protocolo,
        "nome_contato": nome_contato,
        "departamento": departamento,
        "tempo_espera_segundos": tempo_espera_segundos,
        "data_hora_alerta": datetime.utcnow().isoformat(),
    }).execute()


def carregar_nomes_internos() -> set[str]:
    """Carrega todos os nomes internos (usuarios + atendentes vinculados) para filtragem."""
    try:
        result = _get_client().table("usuarios").select("nome, atendente_nome").execute()
        nomes: set[str] = set()
        for u in result.data or []:
            if u.get("nome"):
                nomes.add(u["nome"].strip().lower())
            if u.get("atendente_nome"):
                nomes.add(u["atendente_nome"].strip().lower())
        return nomes
    except Exception:
        return set()
