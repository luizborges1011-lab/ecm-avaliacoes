#!/usr/bin/env python3
"""
Script chamado pelo cron para executar um ciclo de avaliação.
Uso: python run_ciclo.py
"""
import logging
import sys
import os

# Garante que o diretório do projeto está no path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_DIR, "logs", "ciclo.log")),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("run_ciclo")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))

    os.makedirs(os.path.join(PROJECT_DIR, "logs"), exist_ok=True)

    try:
        from worker.tasks.avaliar import executar_ciclo
        resultado = executar_ciclo()
        logger.info(f"Ciclo concluído: {resultado}")
    except Exception as e:
        logger.error(f"Erro no ciclo: {e}", exc_info=True)
        sys.exit(1)
