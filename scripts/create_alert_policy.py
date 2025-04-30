import os
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

NEW_RELIC_USER_KEY = os.getenv("NEW_RELIC_USER_KEY")
ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID")

if not NEW_RELIC_USER_KEY or not ACCOUNT_ID:
    print("NEW_RELIC_USER_KEY e NEW_RELIC_ACCOUNT_ID precisam estar definidos no ambiente ou no .env")
    exit(1)

headers = {
    "Content-Type": "application/json",
    "API-Key": NEW_RELIC_USER_KEY
}

# 1. Criar a Alert Policy
create_policy_query = f'''
mutation {{
  alertsPolicyCreate(accountId: {ACCOUNT_ID}, policy: {{
    name: "Alerta Cego — Logs com 'error'",
    incidentPreference: PER_CONDITION
  }}) {{
    id
    name
  }}
}}
'''

# 2. Criar a Condition (com base nos parâmetros definidos nas imagens)
def build_condition_query(account_id, policy_id):
    return f'''
mutation {{
  alertsNrqlConditionStaticCreate(accountId: {account_id}, policyId: {policy_id}, condition: {{
    name: "Logs com erro textual (alerta cego)",
    enabled: true,
    nrql: {{
      query: "FROM Log SELECT count(*) WHERE (message LIKE '%error%' OR level LIKE '%error%' OR message LIKE '%Error%' OR message LIKE '%ERROR%') AND entity.name = 'alerta-cego'"
    }},
    terms: [{{
      threshold: 0,
      thresholdDuration: 60,
      thresholdOccurrences: AT_LEAST_ONCE,
      operator: ABOVE,
      priority: CRITICAL
    }}],
    valueFunction: SINGLE_VALUE
  }}) {{
    id
    name
  }}
}}
'''

def execute_graphql(query):
    response = requests.post(
        "https://api.newrelic.com/graphql",
        json={"query": query},
        headers=headers
    )
    return response.json()

def main():
    print("Criando Alert Policy...")
    policy_response = execute_graphql(create_policy_query)
    policy_data = policy_response.get("data", {}).get("alertsPolicyCreate", {})
    policy_id = policy_data.get("id")

    if not policy_id:
        print("Falha ao criar policy:", policy_response)
        return

    print(f"Policy criada: {policy_data['name']} (ID: {policy_id})")

    print("Criando Condition associada...")
    condition_query = build_condition_query(ACCOUNT_ID, policy_id)
    condition_response = execute_graphql(condition_query)

    condition_data = condition_response.get("data", {}).get("alertsNrqlConditionStaticCreate", {})
    if condition_data:
        print(f"Condição criada: {condition_data['name']} (ID: {condition_data['id']})")
    else:
        print("Falha ao criar condição:", condition_response)

if __name__ == "__main__":
    main()
