import os
import requests
import subprocess
from datetime import datetime, timezone
from dotenv import load_dotenv

# Carrega variáveis do .env da raiz do projeto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Variáveis obrigatórias
NEW_RELIC_USER_KEY = os.getenv("NEW_RELIC_USER_KEY")
NEW_RELIC_INSERT_KEY = os.getenv("NEW_RELIC_INSERT_KEY")
NEW_RELIC_APP_NAME = os.getenv("NEW_RELIC_APP_NAME")
NEW_RELIC_ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID")

if not NEW_RELIC_USER_KEY or not NEW_RELIC_APP_NAME or not NEW_RELIC_ACCOUNT_ID or not NEW_RELIC_INSERT_KEY:
    print(" Variáveis necessárias não encontradas no .env:")
    print("- NEW_RELIC_USER_KEY")
    print("- NEW_RELIC_INSERT_KEY")
    print("- NEW_RELIC_APP_NAME")
    print("- NEW_RELIC_ACCOUNT_ID")
    exit(1)

# Headers do GraphQL (marker)
graphql_headers = {
    "Content-Type": "application/json",
    "API-Key": NEW_RELIC_USER_KEY
}

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "manual"

def get_entity_guid(app_name):
    query = f'''
    {{
      actor {{
        entitySearch(query: "name = '{app_name}'") {{
          results {{
            entities {{
              guid
              name
            }}
          }}
        }}
      }}
    }}
    '''
    response = requests.post("https://api.newrelic.com/graphql", json={"query": query}, headers=graphql_headers)
    entities = response.json().get("data", {}).get("actor", {}).get("entitySearch", {}).get("results", {}).get("entities", [])
    if not entities:
        return None
    return entities[0].get("guid")

def send_deploy_marker(guid, commit_hash):
    timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    mutation = f'''
    mutation {{
      changeTrackingCreateDeployment(deployment: {{
        entityGuid: "{guid}",
        version: "{commit_hash}",
        deploymentType: BASIC,
        description: "Deploy automático via script",
        timestamp: {timestamp_ms}
      }}) {{
        deploymentId
        entityGuid
      }}
    }}
    '''
    response = requests.post("https://api.newrelic.com/graphql", json={"query": mutation}, headers=graphql_headers)
    return response.json()

def send_deployment_event(account_id, insert_key, app_name, commit):
    payload = [{
        "eventType": "Deployment",
        "appName": app_name,
        "version": commit,
        "description": "Deploy automático com marker + evento custom"
    }]
    response = requests.post(
        f"https://insights-collector.newrelic.com/v1/accounts/{account_id}/events",
        headers={
            "Content-Type": "application/json",
            "X-Insert-Key": insert_key, 
        },
        json=payload
    )
    if response.status_code == 200:
        print("Evento custom Deployment enviado com sucesso!")
    else:
        print(f"Falha ao enviar evento Deployment: {response.status_code} — {response.text}")

def main():
    print("Buscando GUID da aplicação...")
    guid = get_entity_guid(NEW_RELIC_APP_NAME)
    if not guid:
        print(f"GUID não encontrado para aplicação '{NEW_RELIC_APP_NAME}'")
        exit(1)

    print(f" GUID encontrado: {guid}")

    commit = get_git_commit()
    print(f"Registrando deploy (commit: {commit})...")

    result = send_deploy_marker(guid, commit)
    deployment = result.get("data", {}).get("changeTrackingCreateDeployment", {})
    if deployment:
        print(f" Deploy anotado com sucesso: ID {deployment['deploymentId']}")
    else:
        print("Falha ao registrar marker:", result)

    # Envia também o evento custom (para dashboards NRQL)
    send_deployment_event(
        account_id=NEW_RELIC_ACCOUNT_ID,
        insert_key=NEW_RELIC_INSERT_KEY,
        app_name=NEW_RELIC_APP_NAME,
        commit=commit
    )

if __name__ == "__main__":
    main()
