FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

CMD ["newrelic-admin", "run-program", "python", "app.py"]
