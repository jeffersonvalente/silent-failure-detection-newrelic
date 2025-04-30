#!/bin/sh
set -e

echo " Entrypoint iniciado..."
echo " Variáveis atuais:"
env | grep NEW_RELIC

echo " Gerando newrelic.ini a partir do template..."
envsubst < /app/newrelic.ini.template > /app/newrelic.ini

echo " newrelic.ini gerado:"
cat /app/newrelic.ini

echo " Iniciando app com agente New Relic..."
exec newrelic-admin run-program python app.py
