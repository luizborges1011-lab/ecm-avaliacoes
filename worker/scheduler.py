"""
Scheduler de automação — roda dentro do processo Reflex, sem Celery.

Inicia um BackgroundScheduler (APScheduler) com os mesmos três ciclos
definidos anteriormente no celery beat:
  • 12:00 BRT — avalia chamados de 00:00–11:59
  • 16:00 BRT — avalia chamados de 12:00–15:59
  • 00:01 BRT — avalia chamados de 16:00–23:59 do dia anterior
"""
import logging
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None
_lock = threading.Lock()


def _executar():
    """Wrapper para importar executar_ciclo apenas quando a tarefa dispara."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from worker.tasks.avaliar import executar_ciclo
        from worker.services.database import registrar_ciclo_log
        resultado = executar_ciclo()
        registrar_ciclo_log(
            tipo="automatico",
            total=resultado["total"],
            sucesso=resultado["sucesso"],
            erros=resultado["erro"],
            periodo=resultado.get("periodo", ""),
        )
        logger.info(f"[scheduler] Ciclo finalizado: {resultado}")
    except Exception as exc:
        logger.error(f"[scheduler] Erro no ciclo: {exc}", exc_info=True)


def iniciar():
    """
    Inicia o scheduler em background.
    Idempotente — chamadas duplicadas (hot-reload do Reflex) são ignoradas.
    """
    global _scheduler
    with _lock:
        if _scheduler is not None and _scheduler.running:
            return

        _scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

        _scheduler.add_job(
            _executar,
            CronTrigger(hour=12, minute=0, timezone="America/Sao_Paulo"),
            id="ciclo-meio-dia",
            replace_existing=True,
        )
        _scheduler.add_job(
            _executar,
            CronTrigger(hour=16, minute=0, timezone="America/Sao_Paulo"),
            id="ciclo-dezesseis",
            replace_existing=True,
        )
        _scheduler.add_job(
            _executar,
            CronTrigger(hour=0, minute=1, timezone="America/Sao_Paulo"),
            id="ciclo-meia-noite",
            replace_existing=True,
        )

        _scheduler.start()
        logger.info("[scheduler] Automação iniciada — ciclos: 12:00, 16:00, 00:01 BRT")


def parar():
    global _scheduler
    with _lock:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)
            _scheduler = None
