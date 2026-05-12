#!/bin/bash
# Inicia nginx como daemon (responde ao healthcheck imediatamente)
nginx

# Inicia o Reflex em modo produção (frontend na 3001, backend na 8000)
exec reflex run --env prod
