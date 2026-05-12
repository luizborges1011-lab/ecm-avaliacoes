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

RUN chmod +x start.sh

# Railway roteia para a porta definida em PORT (auto-detectada do EXPOSE)
EXPOSE 8000

CMD ["./start.sh"]
