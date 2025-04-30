import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
import newrelic.agent

# Carrega variáveis de ambiente do .env
load_dotenv()

# Inicializa o agente da New Relic
newrelic.agent.initialize('/app/newrelic.ini')

# Cria instância do app Flask
app = Flask(__name__)

# Configura logging (nível INFO, sem handler custom — usa stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

@app.route("/ok")
def rota_ok():
    logger.info("info: execução de sincronização concluída com sucesso.")
    return jsonify({"status": "ok", "message": "Tudo certo"}), 200

@app.route("/fail")
def rota_falha():
    logger.info("error: falha silenciosa ao tentar processar sincronização financeira.")
    return jsonify({"status": "ok", "message": "Erro silencioso simulado e logado"}), 200

@app.route("/healthz")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
