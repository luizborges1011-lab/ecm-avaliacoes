web: reflex run --env prod
worker: python -m celery -A worker.celery_app worker --beat --loglevel=info --concurrency=2
