# BancoApp - Sistema Bancário Profissional

BancoApp é uma solução bancária completa desenvolvida em **Python**, com **FastAPI** no backend, **Streamlit** no frontend e orquestração via **Docker Compose**.

##  Visão Geral

Este projeto implementa um sistema bancário com gerenciamento de usuários, autenticação JWT, contas financeiras, transações, histórico de movimentações, criptografia de dados sensíveis e monitoramento.

## Stack Tecnológica

- Backend: **FastAPI**, **SQLAlchemy**, **Pydantic**, **Uvicorn**
- Banco de dados: **PostgreSQL**
- Frontend: **Streamlit**
- Containerização: **Docker**, **Docker Compose**
- Segurança: **bcrypt**, **Fernet**, **JWT**
- Monitoramento: **Prometheus**, **Grafana**
- Testes: **pytest**

##  Funcionalidades Principais

- Registro e login de usuários
- Autenticação com Access Token e Refresh Token
- Perfil de usuário com edição de informações básicas
- Criação e listagem de contas (corrente, poupança, investimento)
- Depósito, saque e transferência entre contas
- Cálculo de saldo disponível e limite de saque
- Histórico de transações com paginação
- Proteção de dados sensíveis com criptografia (CPF)
- Auditoria de operações e logs estruturados
- Containerização completa com Docker

## Estrutura do Projeto

```text
APP_BANCO/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── models/            # Modelos do banco de dados
│   │   ├── schemas/           # Schemas Pydantic
│   │   ├── services/          # Regras de negócio
│   │   ├── routes/            # Endpoints da API
│   │   ├── security/          # Autenticação, criptografia e tokens
│   │   ├── database/          # Configuração e sessão do DB
│   │   ├── utils/             # Utilitários e exceções
│   │   └── config.py          # Configurações da aplicação
│   ├── main.py               # Entrada do backend
│   ├── requirements.txt       # Dependências Python
│   ├── Dockerfile            # Build do container backend
│   └── .env.example          # Exemplo de variáveis de ambiente
│
├── frontend/                  # Interface Streamlit
│   ├── app.py               # Aplicação Streamlit
│   ├── requirements.txt      # Dependências Python
│   └── Dockerfile           # Build do container frontend
│
├── tests/                    # Testes automatizados
│   ├── test_auth.py         # Testes de autenticação
│   ├── test_accounts.py     # Testes de contas
│   └── ...
├── docs/                     # Documentação do projeto
├── docker-compose.yml        # Orquestração Docker
├── prometheus.yml            # Configuração Prometheus
└── README.md                 # Documentação principal
```

## 🛠️ Como Executar

### Requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

### Executando com Docker

```bash
docker-compose up -d
```

Acesse:
- Frontend: `http://localhost:8501`
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/api/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

### Executando localmente

#### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Ajuste o .env com a variável DATABASE_URL e SECRET_KEY
python main.py
```

#### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Testes

Execute os testes com:

```bash
cd APP_BANCO
pytest
```

## Endpoints Principais

### Autenticação

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

### Usuários

- `GET /api/users/me`
- `PUT /api/users/me`
- `POST /api/users/change-password`

### Contas

- `POST /api/accounts/`
- `GET /api/accounts/`
- `GET /api/accounts/{account_id}/balance`
- `GET /api/accounts/total-balance`

### Transações

- `POST /api/transactions/deposit`
- `POST /api/transactions/withdrawal`
- `POST /api/transactions/transfer`
- `GET /api/transactions/{transaction_id}`
- `GET /api/transactions/account/{account_id}/history`

## Deploy

O deployment é feito por Docker Compose. Use:

```bash
docker-compose up -d --build
```

Para desligar os serviços:

```bash
docker-compose down
```

## Contato

Para dúvidas ou manutenção do projeto, utilize o canal de contato do proprietário do repositório.
