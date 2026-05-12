FROM python:3.11-slim

WORKDIR /app

# Instala Node.js 20, nginx e utilitários
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    nginx \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Inicializa o Reflex (instala pacotes npm, cria .web/)
RUN reflex init

# Copia configuração do nginx
COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x start.sh

EXPOSE 3000

CMD ["./start.sh"]
