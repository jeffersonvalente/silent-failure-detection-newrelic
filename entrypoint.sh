#!/bin/sh

echo "📦 Entrypoint iniciado..."

# Verifica se variáveis estão disponíveis
echo "🔍 Verificando variáveis de ambiente:"
echo "  - NEW_RELIC_LICENSE_KEY: ${NEW_RELIC_LICENSE_KEY:-<não definida>}"
echo "  - NEW_RELIC_APP_NAME: ${NEW_RELIC_APP_NAME:-<não definida>}"
echo "  - NEW_RELIC_LOG_LEVEL: ${NEW_RELIC_LOG_LEVEL:-<não definida>}"

# Garante que todas as variáveis existem
if [ -z "$NEW_RELIC_LICENSE_KEY" ] || [ -z "$NEW_RELIC_APP_NAME" ] || [ -z "$NEW_RELIC_LOG_LEVEL" ]; then
  echo "Erro: Variáveis de ambiente obrigatórias não estão definidas. Abortando."
  exit 1
fi

# Substitui as variáveis e gera o arquivo de configuração
echo "Gerando arquivo /app/newrelic.ini a partir do template..."
envsubst < /app/newrelic.ini.template > /app/newrelic.ini

echo "Conteúdo final do newrelic.ini:"
cat /app/newrelic.ini

# Executa o app com o agente
echo "Iniciando app com agente New Relic..."
exec newrelic-admin run-program python app.py
