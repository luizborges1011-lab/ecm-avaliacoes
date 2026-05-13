FROM python:3.11-slim

WORKDIR /app

# Node.js 20 é necessário para o Reflex compilar o frontend
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Inicializa o Reflex (instala pacotes npm, prepara .web/)
RUN reflex init

# Railway auto-detecta EXPOSE e define PORT=3000
EXPOSE 3000

CMD ["reflex", "run", "--env", "prod"]
