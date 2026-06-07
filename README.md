# F1 Project

Projeto voltado a coleta, armazenamento e processamento de dados de Formula 1 para suporte a analises e modelos preditivos.

## Arquitetura inicial do projeto

<img src="./image/f1-project.png" alt="Arquitetura do projeto F1">

## Visao geral

Este repositório organiza a base de um pipeline de dados para Formula 1, cobrindo desde a coleta historica ate a disponibilizacao dos dados para consumo analitico e modelagem.

## Etapas do projeto

### Coleta

A coleta de dados sera feita com a biblioteca FastF1, por meio de scripts em Python responsaveis pela extracao das informacoes historicas.

Essa etapa sera executada em um servidor proprio, com agendamento automatico.

### Envio dos dados

Apos a coleta, os dados serao enviados para um bucket S3 na AWS. Dessa forma, a Nekt podera consumir os arquivos brutos e realizar a ingestao no Lakehouse.

Nesse contexto, o S3 atua como camada raw, ou camada de dados brutos.

### Camada Bronze

Na camada bronze, os dados serao consolidados em formato Delta, com historico de modificacoes e representacao fiel da origem dos registros.

### Camada Silver

A partir da camada anterior, o Lakehouse permite novas modelagens de dados e a criacao de Feature Stores com o historico de cada entidade de interesse.

### Camada Gold

Nesta camada, os dados sao organizados em tabelas sumarizadas e orientadas a relatorios, prontas para consumo em ferramentas de BI e dashboards.

### Treinamento do modelo

Com os dados das Feature Stores e dos eventos de interesse, sera gerada uma Analytical Base Table (ABT) para treinamento dos modelos de Machine Learning.

Os modelos serao treinados e comparados localmente, com uso do MLflow hospedado em servidor proprio.

### Aplicacao para usuario

Com o modelo treinado, a etapa final consiste em uma aplicacao para exibicao das predicoes a usuarios interessados em Formula 1.

> **Nota:** o front-end em `frontend/` (React + Vite + Tailwind) foi gerado com o aux\u00edlio de IA (opencode / MiniMax-M3) a partir do brief do projeto, e refinado para se integrar \u00e0 API FastAPI e ao MLflow descritos acima.

## Como rodar com Docker

O `docker-compose.yml` na raiz sobe tr\u00eas servi\u00e7os ligados \u00e0 rede `postgres-container_default` (onde j\u00e1 roda o Postgres `meu_postgres`):

| Servi\u00e7o     | Porta | Descri\u00e7\u00e3o                                       |
| -------------- | ----- | --------------------------------------------------------- |
| `mlflow`       | 5000  | Tracking server + UI do MLflow. Re-registra o modelo.    |
| `f1_api`       | 8000  | FastAPI que carrega o modelo do MLflow e prediz.          |
| `f1_frontend`  | 3000  | Frontend React servido por nginx (proxy `/api` \u2192 API). |

```bash
docker compose up -d --build
# Frontend: http://localhost:3000
# API:      http://localhost:8000/docs
# MLflow:   http://localhost:5000
```


