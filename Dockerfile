FROM python:3.11-slim

WORKDIR /app

# Instala Node.js 20 (necessário para Reflex buildar o frontend)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
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

EXPOSE 3000 8000

CMD ["reflex", "run", "--env", "prod"]
