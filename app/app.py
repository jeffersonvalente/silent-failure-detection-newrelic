import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
import newrelic.agent

# Carrega variáveis de ambiente do .env
load_dotenv()

# Inicializa o agente da New Relic
newrelic.agent.initialize('newrelic.ini')

# Instancia o Flask app
app = Flask(__name__)

# Configura o logging com nível INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Usa o handler do newrelic-logging para enviar logs ao NR Logs
from newrelic_telemetry_sdk.integrations.logging import NewRelicLogHandler
logger.addHandler(NewRelicLogHandler())

@app.route("/ok")
def rota_sucesso():
    logger.info("info: execução de sincronização concluída com sucesso.")
    return jsonify({"status": "ok", "message": "Tudo certo"}), 200

@app.route("/fail")
def rota_falha_silenciosa():
    logger.info("error: falha silenciosa ao tentar processar sincronização financeira.")
    return jsonify({"status": "ok", "message": "Erro silencioso simulado e logado"}), 200

@app.route("/healthz")
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
