# Alerta Cego — Detecção de Falhas Silenciosas via Observabilidade (New Relic + K8s + GitHub Actions)

>  **Baseado em um incidente real:** Este projeto nasceu de um caso real em produção, onde uma falha crítica em sincronizações de dados passava despercebida — sem erro visível, sem crash de pod, sem alerta. Aqui, mostro como detecção inteligente por logs, mesmo em nível `INFO`, pode evitar prejuízos silenciosos.

Este projeto simula um problema real enfrentado em produção, onde uma aplicação executava sincronizações críticas via cron interna, mas falhas na execução passavam despercebidas por não haver crash de pod, nem logs em nível de erro.

A proposta aqui é mostrar como detectar essas falhas "silenciosas" via logs, configurando a observabilidade com New Relic, alertas via NRQL, e deploy rastreável via GitHub Actions em um ambiente local Kubernetes (Docker Desktop).

---

## Requisitos

- Docker Desktop com Kubernetes ativado
- Runner local GitHub configurado
- Conta gratuita no [New Relic](https://newrelic.com)
- Chaves da API (Insert Key e User Key)
- Python 3.x com `requests`, `python-dotenv`

---

## Estrutura do Projeto

```
silent-failure-detection-newrelic/
├── app/                       # App Python com rotas de teste (/ok e /fail)
│   ├── app.py
│   ├── requirements.txt
│   ├── newrelic.ini.template
├── k8s/                       # Manifests para K8s (namespace, deployment, service)
│   ├── namespace.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── scripts/                   # Scripts utilitários
│   ├── annotate_deploy.py    # Marca o deploy (GraphQL + evento custom)
│   └── create_alert_policy.py# Cria alerta NRQL automaticamente
├── newrelic/
│   └── dashboards/
│       └── dashboard.json     # Dashboard pronto para importar (substitua o "accountId")
├── .github/workflows/
│   └── deploy.yaml            # Pipeline GitHub Actions
├── .env.example              # Exemplo das variáveis sensíveis
├── Dockerfile
├── entrypoint.sh
└── README.md
```

---

## O App Dummy

- `GET /ok`: responde 200 OK e gera log de INFO
- `GET /fail`: responde 200 OK, mas gera um log `INFO` contendo a palavra "error" (simula erro silencioso)

Exemplo de log gerado:
```text
[INFO] Tudo parece ok, mas... error inesperado ocorreu durante a execução.
```

---

## Deploy Automatizado via GitHub Actions

O deploy é feito localmente em seu cluster do Docker Desktop:

- Cria namespace `observability-lab`
- Cria `Secret` com a Insert Key e `ConfigMap` com o nome da aplicação
- Faz build da imagem localmente (`imagePullPolicy: Never`)
- Faz rollout no Kubernetes com rastreio de sucesso

> Crie o segredo `NEW_RELIC_LICENSE_KEY` diretamente nos `Secrets` do repositório GitHub (Settings → Secrets → Actions)

Para testar localmente após o deploy:
```bash
kubectl port-forward -n observability-lab svc/alerta-cego 5000:5000
curl http://localhost:5000/fail
```

---

## Anotação do Deploy

Executando:
```bash
python3 scripts/annotate_deploy.py
```
- Marca o deploy via GraphQL (New Relic NerdGraph)
- Envia evento customizado para dashboards NRQL (eventType: Deployment)

> Combine com a chamada à rota `/fail` após o deploy para simular um cenário de erro em produção logo após uma entrega — e validar o rastreio do impacto.

---

## Importação dos Dashboards e Alertas

1. Acesse a UI do New Relic
2. Importe o JSON do dashboard:
   - Arquivo: `newrelic/dashboards/dashboard.json`
   - Substitua o campo `"accountId": "YOUR_ACCOUNT_ID_HERE"` pelo seu ID real
3. Importe a política de alertas:
   ```bash
   python3 scripts/create_alert_policy.py
   ```

---

## O que você verá no New Relic

- Logs em INFO com "error" sendo detectados (mesmo sem nível ERROR)
- Linha do tempo de deploys (eventType: Deployment)
- Gráficos de comportamento da aplicação antes/depois
- Alerta NRQL baseado em `count(*)` de logs com "error"

> O dashboard vem pronto com visões por severidade, distribuição de logs e histórico de alertas.

---

## Variáveis de Ambiente

Exemplo de `.env`:
```env
NEW_RELIC_LICENSE_KEY=
NEW_RELIC_APP_NAME=alerta-cego
NEW_RELIC_LOG_LEVEL=info
NEW_RELIC_USER_KEY=
NEW_RELIC_ACCOUNT_ID=
NEW_RELIC_INSERT_KEY=
```
Descrição de cada variável

|Variável	| Descrição |
|-----------|-----------|
| NEW_RELIC_LICENSE_KEY	| Chave de licença usada pelo agente do New Relic no container para envio de logs. |
| NEW_RELIC_APP_NAME	| Nome da aplicação para identificação no New Relic. Usado também no ConfigMap. |
| NEW_RELIC_LOG_LEVEL	| Nível de log capturado. Recomenda-se info para simular falha silenciosa. |
| NEW_RELIC_USER_KEY	| API Key de usuário para chamadas GraphQL (scripts de anotação e alertas). |
| NEW_RELIC_ACCOUNT_ID	| ID da conta New Relic, necessário nos dashboards e nas queries NRQL. |
| NEW_RELIC_INSERT_KEY	API | Key usada para envio de eventos customizados ao New Relic (como Deployment). |

---

## Habilidades demonstradas neste projeto

- Observabilidade baseada em logs, com NRQL avançado
- Deploy rastreável com marcação e eventos customizados
- GitHub Actions + Kubernetes local (Docker Desktop)
- Automação de alertas e dashboards no New Relic via código
- Simulação realista de falhas não detectáveis por monitoramento tradicional

---

## Contribuições

Pull requests com melhorias, plugins adicionais, suporte a outras ferramentas de observabilidade ou sugestões de simulações são bem-vindos.

---

## Contato

LinkedIn: [https://www.linkedin.com/in/jefferson-hoy-valente/](https://www.linkedin.com/in/jefferson-hoy-valente/)

