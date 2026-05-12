#!/bin/bash

# Railway injeta PORT automaticamente; default 3000 se não estiver setada
LISTEN_PORT=${PORT:-3000}

# Gera o nginx.conf com a porta correta em runtime
cat > /etc/nginx/nginx.conf << NGINX_CONF
worker_processes 1;
error_log /dev/stderr warn;
pid /tmp/nginx.pid;

events { worker_connections 1024; }

http {
    access_log /dev/stdout;

    server {
        listen $LISTEN_PORT;

        # Healthcheck — sempre responde 200, mesmo antes do Reflex iniciar
        location = /health {
            return 200 'ok';
            add_header Content-Type text/plain;
        }

        # Backend WebSocket (Reflex state engine)
        location /_event {
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_read_timeout 86400;
        }

        # Upload de arquivos
        location /_upload {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host \$host;
            client_max_body_size 100M;
        }

        # Ping do backend
        location /ping {
            proxy_pass http://127.0.0.1:8000;
        }

        # Frontend — retorna 200 enquanto o Reflex ainda está compilando
        location / {
            proxy_pass http://127.0.0.1:3001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_connect_timeout 5s;
            proxy_read_timeout 300s;
            error_page 502 503 504 = @starting;
        }

        location @starting {
            default_type text/html;
            return 200 "<html><body><p>Iniciando aplicacao...</p></body></html>";
        }
    }
}
NGINX_CONF

# Valida o config antes de iniciar
nginx -t || { echo "nginx config inválido"; exit 1; }

# Inicia nginx como daemon (responde ao /health imediatamente)
nginx

echo "nginx iniciado na porta $LISTEN_PORT"

# Inicia o Reflex em modo produção (frontend na 3001, backend na 8000)
exec reflex run --env prod
