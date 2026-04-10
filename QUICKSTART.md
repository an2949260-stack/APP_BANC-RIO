# 🚀 Quick Start Guide

## Iniciar em 5 Minutos

### 1. Com Docker Compose (Recomendado)
```bash
cd APP_BANCO
docker-compose up -d
```

**Esperar 30s para inicializar...**

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)

### 2. Localmente (Sem Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
python main.py
```

#### Frontend (Outro Terminal)
```bash
cd frontend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
streamlit run app.py
```

## Primeiro Teste

### Registrar Usuário (API Docs)
1. Vá para: http://localhost:8000/api/docs
2. Clique em **POST /api/auth/register**
3. Click **Try it out**
4. Preencha:
```json
{
  "email": "teste@example.com",
  "username": "testeuser",
  "full_name": "Usuário Teste",
  "password": "SecurePass123",
  "cpf": "12345678900",
  "birth_date": "1990-01-01T00:00:00"
}
```
5. Click **Execute**

### Fazer Login
1. POST /api/auth/login
2. Teste:
```json
{
  "email": "teste@example.com",
  "password": "SecurePass123"
}
```

### Criar Conta
1. POST /api/accounts/
2. Use o token do login no header:
```
Authorization: Bearer <seu_token>
```
3. Teste:
```json
{
  "account_type": "corrente",
  "overdraft_limit": 1000
}
```

### Fazer Transação
1. POST /api/transactions/deposit
2. Com header de autenticação
3. Query params:
   - `account_id`: ID da conta criada
   - `amount`: 500
   - `description`: Depósito teste

## Comandos Úteis

### Docker
```bash
# Ver serviços
docker-compose ps

# Logs
docker-compose logs -f backend

# Parar
docker-compose down

# Limpar tudo
docker-compose down -v
```

### Banco de Dados
```bash
# Acesso psql
docker-compose exec postgres psql -U bancario -d banco_app

# Listar tabelas
\dt

# Sair
\q
```

### Testes
```bash
cd backend
pytest
pytest -v
pytest --cov=app
```

## Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `backend/.env` | Variáveis de ambiente |
| `backend/main.py` | Aplicação principal |
| `backend/app/models/` | Modelos de dados |
| `backend/app/routes/` | Endpoints da API |
| `frontend/app.py` | Interface web |
| `docker-compose.yml` | Orquestração |

## Troubleshooting

### Erro: "Connection refused" (Banco)
```bash
# Espere o containers inicializar
docker-compose logs postgres

# Recrie o container
docker-compose down
docker-compose up -d --build
```

### Erro: "Port already in use"
```bash
# Encontre o processo
lsof -i :8000

# Mate o processo
kill -9 <PID>

# Ou mude a porta no docker-compose.yml
```

### Erro: "Database doesn't exist"
```bash
# Reinicie os containers
docker-compose down -v
docker-compose up -d
```

## Estrutura Rápida

```
backend/
├── app/
│   ├── models/         # BD
│   ├── routes/         # API endpoints
│   ├── services/       # Lógica
│   ├── security/       # JWT/Crypto
│   └── utils/          # Helpers
├── main.py            # App principal
└── requirements.txt   # Dependências

frontend/
├── app.py            # Streamlit app
└── requirements.txt

tests/
├── test_auth.py
└── test_accounts.py
```

---

**Tudo pronto para começar! 🎉**
