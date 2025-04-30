#!/bin/sh

# Substitui as variáveis no template para gerar o arquivo final
envsubst < /app/newrelic.ini.template > /app/newrelic.ini

# Executa o app com o agente da New Relic
exec newrelic-admin run-program python app.py
