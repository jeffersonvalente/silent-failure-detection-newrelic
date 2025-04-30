FROM python:3.10-slim

WORKDIR /app

# Copia dependências e instala
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código e o template de config
COPY app/ .

# Usa envsubst para gerar newrelic.ini substituindo as variáveis
RUN apt-get update && apt-get install -y gettext && \
    envsubst < newrelic.ini.template > newrelic.ini && \
    rm -f newrelic.ini.template

# Define o caminho de config usado pelo agent
ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini

CMD ["newrelic-admin", "run-program", "python", "app.py"]