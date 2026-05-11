import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    "ecm_worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["worker.tasks.celery_tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    beat_schedule={
        # Processa chamados 00:00–11:59 → executa às 12:00 BRT
        "ciclo-meio-dia": {
            "task": "worker.tasks.celery_tasks.task_executar_ciclo",
            "schedule": crontab(hour=12, minute=0),
        },
        # Processa chamados 12:00–15:59 → executa às 16:00 BRT
        "ciclo-dezesseis": {
            "task": "worker.tasks.celery_tasks.task_executar_ciclo",
            "schedule": crontab(hour=16, minute=0),
        },
        # Processa chamados 16:00–23:59 do dia anterior → executa às 00:01 BRT
        "ciclo-meia-noite": {
            "task": "worker.tasks.celery_tasks.task_executar_ciclo",
            "schedule": crontab(hour=0, minute=1),
        },
    },
)
