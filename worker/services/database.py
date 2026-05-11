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
