import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
import newrelic.agent

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa o agente da New Relic
newrelic.agent.initialize('newrelic.ini')

# Instancia a aplicação Flask
app = Flask(__name__)

# Configura logging com newrelic-logging
from newrelic_telemetry_sdk.integrations.logging import NewRelicLogHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(NewRelicLogHandler())

@app.route("/ok")
def ok():
    logger.info("info: execução de sincronização concluída com sucesso.")
    return jsonify({"status": "ok"}), 200

@app.route("/fail")
def fail():
    logger.info("error: falha silenciosa ao tentar processar sincronização financeira.")
    return jsonify({"status": "falha registrada em log"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
