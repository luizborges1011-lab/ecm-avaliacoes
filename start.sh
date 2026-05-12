#!/bin/bash
set -e

# Passo 1: compila o frontend com api_url correto (RAILWAY_PUBLIC_DOMAIN disponível em runtime)
echo "==> Compilando frontend..."
reflex export --frontend-only --no-zip

# Passo 2: sobe apenas o backend Python (uvicorn)
# O backend serve os arquivos estáticos compilados + WebSocket em /_event
echo "==> Iniciando backend..."
exec reflex run --env prod --backend-only
