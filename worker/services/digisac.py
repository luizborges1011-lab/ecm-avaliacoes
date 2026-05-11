import json
import os
import httpx
from datetime import datetime

BASE_URL = os.getenv("DIGISAC_BASE_URL", "https://contabilmadruga.digisac.me/api/v1")
TOKEN = os.getenv("DIGISAC_TOKEN", "")

_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def _headers() -> dict:
    token = os.getenv("DIGISAC_TOKEN", TOKEN)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def buscar_chamados_fechados(data_inicio: datetime, data_fim: datetime) -> list[dict]:
    query = {
        "where": {
            "isOpen": False,
            "endedAt": {
                "$gte": data_inicio.isoformat(),
                "$lte": data_fim.isoformat(),
            },
        },
        "include": [{"model": "contact", "attributes": ["id", "name"]}],
        "page": 1,
        "perPage": 200,
    }
    resp = httpx.get(
        f"{BASE_URL}/tickets",
        headers=_headers(),
        params={"query": json.dumps(query)},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def exportar_historico(protocol: str) -> str:
    resp = httpx.post(
        f"{BASE_URL}/tickets/export",
        headers=_headers(),
        json={"protocol": protocol},
        timeout=60.0,
    )
    resp.raise_for_status()
    # Digisac retorna texto com encoding Windows-1252 às vezes
    try:
        return resp.text
    except Exception:
        return resp.content.decode("latin-1")


def baixar_midia(url: str) -> bytes:
    resp = httpx.get(url, timeout=60.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.content
