FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Instala envsubst
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# Copia o entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini

ENTRYPOINT ["/app/entrypoint.sh"]
