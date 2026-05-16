"""
Monitoramento de atendimentos em atraso.

Roda a cada 5 minutos via APScheduler. Busca chamados abertos sem atendente
atribuído (userId vazio) que ultrapassaram o limite de espera:
  • Recepção (dept c6626f5b-...): 600s (10 min)
  • Demais departamentos:         300s (5 min)

Horário de funcionamento (BRT): 07:45–12:00 e 13:30–17:30.

Janelas de pausa (supressão por-ticket baseada em updatedAt):
  • Almoço 12:00–13:30 → grace de 5 min: notifica só após 13:35.
  • Fora do expediente 17:30–08:00 → grace de 5 min: notifica só após 08:05.

Para cada chamado em atraso fora das janelas: envia alerta no Google Chat
e registra no Supabase.
"""
import os
import logging
from datetime import datetime, timezone, timedelta

import httpx

logger = logging.getLogger(__name__)

BRT = timezone(timedelta(hours=-3))

_DEPT_NOMES = {
    "a9c9a482-89e6-4aec-942f-dcd1b7c11c03": "Financeiro",
    "e15c26e3-0afc-4fae-9c00-31dceec22060": "Legalização",
    "0c2459c8-eaf3-45f2-82e2-2b700d72cbda": "RH",
    "c3c6b1e0-5a81-412e-97fd-31688b5a8f96": "Fiscal/Contábil",
    "52983bee-ad68-4dda-bcc1-017451a22958": "Emissão de Notas",
    "c6626f5b-4dc6-4935-9e0d-60ec432deea8": "Recepção",
}

# Recepção tolera 10 min; todos os outros setores: 5 min
_THRESHOLD_RECEPCAO = 600
_THRESHOLD_PADRAO = 300
_DEPT_RECEPCAO = "c6626f5b-4dc6-4935-9e0d-60ec432deea8"


def _dentro_horario_comercial() -> bool:
    agora = datetime.now(BRT)
    if agora.weekday() >= 5:  # sábado=5, domingo=6
        return False
    minutos = agora.hour * 60 + agora.minute
    almoco = 720 <= minutos < 810        # 12:00–13:30
    fora = minutos >= 1050 or minutos < 465  # após 17:30 ou antes 07:45
    return not (almoco or fora)


def _nome_dept(dept_id: str) -> str:
    return _DEPT_NOMES.get(dept_id, "Recepção")


def _threshold(dept_id: str) -> int:
    return _THRESHOLD_RECEPCAO if dept_id == _DEPT_RECEPCAO else _THRESHOLD_PADRAO


def _segundos_espera(updated_at: str) -> float:
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return 0.0


def _inicio_espera_brt(ticket: dict) -> datetime | None:
    """Retorna o momento em que o ticket entrou em aguardo (horário BRT)."""
    updated_at = ticket.get("updatedAt", "")
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return dt.astimezone(BRT)
    except Exception:
        return None


def _em_janela_pausa(inicio_brt: datetime, agora_brt: datetime) -> bool:
    """
    Retorna True se a notificação deve ser suprimida porque o ticket entrou
    em aguardo durante uma janela de pausa e o período de grace ainda não passou.

    Regra almoço   — iniciou entre 12:00 e 13:30: suprimir até 13:35.
    Regra expediente — iniciou após 17:30 ou antes 08:00: suprimir até 08:05.
    """
    inicio_min = inicio_brt.hour * 60 + inicio_brt.minute
    agora_min  = agora_brt.hour  * 60 + agora_brt.minute
    diff_dias  = (agora_brt.date() - inicio_brt.date()).days

    # Almoço: iniciou entre 12:00 (720 min) e 13:30 (810 min) no mesmo dia
    # Grace termina às 13:35 (815 min)
    if diff_dias == 0 and 720 <= inicio_min < 810 and agora_min < 815:
        return True

    # Fora do expediente: iniciou após 17:30 (1050 min) e ainda é antes das 08:05
    # do dia seguinte (diff_dias entre 1 e 3 cobre fins de semana/feriados curtos)
    if inicio_min >= 1050 and 1 <= diff_dias <= 3 and agora_min < 485:
        return True

    # Madrugada: iniciou antes das 08:00 (480 min) no mesmo dia
    if diff_dias == 0 and inicio_min < 480 and agora_min < 485:
        return True

    return False


def _ticket_atrasado(ticket: dict) -> bool:
    if ticket.get("userId"):
        return False
    espera = _segundos_espera(ticket.get("updatedAt", ""))
    return espera > _threshold(ticket.get("departmentId", ""))


def _enviar_alerta_chat(ticket: dict, dept_nome: str, segundos: int) -> None:
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")
    if not webhook_url:
        logger.warning("[atrasados] GOOGLE_CHAT_WEBHOOK_URL não configurado.")
        return

    contact = ticket.get("contact") or {}
    nome_contato = contact.get("name") or "—"
    protocol = ticket.get("protocol") or "—"
    updated_at = ticket.get("updatedAt", "")
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        hora_brt = dt.astimezone(BRT).strftime("%H:%M:%S")
    except Exception:
        hora_brt = "—"

    texto = (
        f"🚨 *ALERTA ECM - {dept_nome}: Cliente aguardando na fila!*\n\n"
        f"*Contato:* {nome_contato}\n"
        f"*Protocolo:* {protocol}\n"
        f"*Aguardando desde as:* {hora_brt}\n\n"
        f"Por favor, assuma o atendimento no painel do Digisac."
    )

    try:
        httpx.post(webhook_url, json={"text": texto}, timeout=10.0)
    except Exception as e:
        logger.error(f"[atrasados] Erro ao enviar alerta Chat: {e}")


def executar_ciclo_atrasados() -> dict:
    if not _dentro_horario_comercial():
        logger.debug("[atrasados] Fora do horário comercial, ciclo ignorado.")
        return {"total": 0, "atrasados": 0, "skipped": True}

    from worker.services.digisac import buscar_chamados_abertos
    from worker.services.database import registrar_atrasado, carregar_protocolos_alertados_recentes

    try:
        chamados = buscar_chamados_abertos()
    except Exception as e:
        logger.error(f"[atrasados] Erro ao buscar chamados abertos: {e}")
        return {"total": 0, "atrasados": 0, "erro": str(e)}

    # Protocolos que já receberam alerta nos últimos 4 min (bloqueia duplicatas
    # de qualquer origem: n8n ainda ativo, múltiplos workers, etc.)
    try:
        ja_alertados = carregar_protocolos_alertados_recentes(janela_segundos=240)
    except Exception:
        ja_alertados = set()

    atrasados = 0
    vistos: set[str] = set()
    for ticket in chamados:
        if not _ticket_atrasado(ticket):
            continue

        dept_id = ticket.get("departmentId", "")
        dept_nome = _nome_dept(dept_id)
        contact = ticket.get("contact") or {}
        nome_contato = contact.get("name") or ""
        protocol = str(ticket.get("protocol") or "")

        if protocol in vistos:
            continue
        vistos.add(protocol)

        if protocol in ja_alertados:
            logger.debug(f"[atrasados] {protocol} já alertado recentemente, ignorando.")
            continue

        # Verifica se o ticket entrou em aguardo durante janela de pausa
        # (almoço 12:00–13:30 com grace até 13:35, ou fora do expediente com grace até 08:05)
        inicio_brt = _inicio_espera_brt(ticket)
        if inicio_brt and _em_janela_pausa(inicio_brt, datetime.now(BRT)):
            logger.debug(f"[atrasados] {protocol} suprimido — iniciou em janela de pausa ({inicio_brt.strftime('%H:%M')}).")
            continue

        segundos = int(_segundos_espera(ticket.get("updatedAt", "")))

        _enviar_alerta_chat(ticket, dept_nome, segundos)

        try:
            registrar_atrasado(
                protocolo=protocol,
                nome_contato=nome_contato,
                departamento=dept_nome,
                tempo_espera_segundos=segundos,
            )
        except Exception as e:
            logger.error(f"[atrasados] Erro ao registrar {protocol}: {e}")

        atrasados += 1
        logger.info(f"[atrasados] ⚠️  {protocol} — {dept_nome} — {segundos}s")

    logger.info(f"[atrasados] Ciclo concluído: {len(chamados)} abertos, {atrasados} em atraso.")
    return {"total": len(chamados), "atrasados": atrasados}
