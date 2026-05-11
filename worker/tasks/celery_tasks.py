import logging
from dotenv import load_dotenv

load_dotenv()

from worker.celery_app import app
from worker.tasks.avaliar import executar_ciclo

logger = logging.getLogger(__name__)


@app.task(
    name="worker.tasks.celery_tasks.task_executar_ciclo",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def task_executar_ciclo(self):
    try:
        resultado = executar_ciclo()
        logger.info(f"Ciclo finalizado: {resultado}")
        return resultado
    except Exception as exc:
        logger.error(f"Erro no ciclo: {exc}")
        raise self.retry(exc=exc)
