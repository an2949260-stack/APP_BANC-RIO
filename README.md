# 🏦 BancoApp - Sistema Bancário Completo em Python

Um sistema bancário profissional e robusto desenvolvido com **FastAPI**, **PostgreSQL** e **Streamlit**, implementando todos os requisitos de um banco de verdade.

## 📋 Características Principais

### ✅ Autenticação e Autorização
- **JWT Tokens** com Access e Refresh tokens
- **Senhas Seguras** com bcrypt (12 rounds)
- **Controle de Acesso** por roles (admin/usuário)
- **Revogação de Tokens** com banco de dados

### 🔐 Segurança e Criptografia
- **Encriptação Fernet** para dados sensíveis (CPF)
- **HTTPS Pronto** para produção
- **CORS Configurado** para origem/destino
- **Rate Limiting** para APIs
- **SQL Injection Prevention** com ORM
- **XSS Protection** implementado

### 💼 Sistema Bancário Completo
- **Gerenciamento de Usuários** (cadastro, perfil, autenticação)
- **Múltiplas Contas** (corrente, poupança, investimento)
- **Transações** (depósito, saque, transferência)
- **Saldo e Limite** de saque
- **Histórico** de transações

### 🗄️ Banco de Dados
- **PostgreSQL** com pool de conexões
- **Modelos Robustos** com relacionamentos
- **Migrações** com Alembic
- **Índices** para performance
- **Auditoria** de ações

### 🔍 Monitoramento e Auditoria
- **Logs Estruturados** em JSON
- **Auditoria** de todas as operações
- **Prometheus** para métricas
- **Grafana** para visualização

### 🧪 Testes
- **Testes Unitários** com pytest
- **Testes de Integração** da API
- **Cobertura de Código**
- **CI/CD Pronto**

### 📱 Interfaces
- **API REST** completa com FastAPI
- **Web UI** com Streamlit
- **Documentação Automática** (Swagger/ReDoc)

### 🐳 Containerização
- **Docker** para todos os serviços
- **Docker Compose** para orquestração
- **Redis** para cache
- **Multi-stage builds** para otimização

## 🚀 Inicio Rápido

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- Git

### Instalação Local

#### 1. Clone o repositório
```bash
cd APP_BANCO
```

#### 2. Configure o ambiente
```bash
# Crie arquivo .env
cp backend/.env.example backend/.env

# Edite com suas configurações
# DATABASE_URL=postgresql://user:password@localhost:5432/banco_app
# SECRET_KEY=sua-chave-super-secreta
```

#### 3. Instale dependências
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (outro terminal)
cd frontend
pip install -r requirements.txt
```

#### 4. Configure banco de dados
```bash
# Crie banco PostgreSQL
createdb banco_app

# No backend, execute as migrações (opcional com Alembic)
python -m alembic upgrade head
```

#### 5. Inicie a aplicação

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Acesse: http://localhost:8000/api/docs
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
# Acesse: http://localhost:8501
```

### Instalação com Docker

```bash
# Inicie todos os serviços
docker-compose up -d

# Visualize logs
docker-compose logs -f

# Pare os serviços
docker-compose down
```

Acesse:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:8501
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📚 Estrutura do Projeto

```
APP_BANCO/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── models/            # Modelos de BD (User, Account, Transaction)
│   │   ├── schemas/           # Schemas Pydantic para validação
│   │   ├── services/          # Lógica de negócio
│   │   ├── routes/            # Endpoints da API
│   │   ├── security/          # Autenticação e criptografia
│   │   ├── database/          # Configuração do BD
│   │   ├── utils/             # Utilitários e exceções
│   │   └── config.py          # Configurações
│   ├── main.py               # Aplicação FastAPI
│   ├── requirements.txt       # Dependências Python
│   ├── Dockerfile            # Container do backend
│   └── .env.example          # Variáveis de ambiente
│
├── frontend/                  # Web UI Streamlit
│   ├── app.py               # Aplicação Streamlit
│   ├── requirements.txt      # Dependências
│   └── Dockerfile           # Container do frontend
│
├── tests/                    # Testes
│   ├── conftest.py         # Configuração pytest
│   ├── test_auth.py        # Testes de autenticação
│   └── test_accounts.py    # Testes de contas
│
├── docs/                    # Documentação
│   ├── API.md              # Documentação da API
│   ├── ARCHITECTURE.md     # Arquitetura do projeto
│   └── DEPLOYMENT.md       # Guia de deployment
│
├── docker-compose.yml       # Orquestração Docker
├── prometheus.yml          # Configuração Prometheus
└── README.md              # Este arquivo
```

## 🔌 API REST Endpoints

### Autenticação
```bash
# Registro
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "user123",
  "full_name": "John Doe",
  "password": "SecurePass123",
  "cpf": "12345678900",
  "birth_date": "1990-01-01"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

# Refresh Token
POST /api/auth/refresh
{
  "refresh_token": "token_value"
}

# Logout
POST /api/auth/logout
{
  "refresh_token": "token_value"
}
```

### Usuários
```bash
# Perfil do usuário
GET /api/users/me
Authorization: Bearer <token>

# Atualizar perfil
PUT /api/users/me
Authorization: Bearer <token>
{
  "full_name": "New Name",
  "phone": "11999999999"
}

# Alterar senha
POST /api/users/change-password?old_password=old&new_password=new
Authorization: Bearer <token>
```

### Contas
```bash
# Criar conta
POST /api/accounts/
Authorization: Bearer <token>
{
  "account_type": "corrente",
  "overdraft_limit": 1000.0
}

# Listar contas
GET /api/accounts/?skip=0&limit=10
Authorization: Bearer <token>

# Obter saldo
GET /api/accounts/{account_id}/balance
Authorization: Bearer <token>

# Saldo total
GET /api/accounts/total-balance
Authorization: Bearer <token>
```

### Transações
```bash
# Depósito
POST /api/transactions/deposit?account_id=&amount=&description=
Authorization: Bearer <token>

# Saque
POST /api/transactions/withdrawal?account_id=&amount=&description=
Authorization: Bearer <token>

# Transferência
POST /api/transactions/transfer?source_account_id=
Authorization: Bearer <token>
{
  "target_account_number": "12345-6",
  "amount": 100.0,
  "description": "Pagamento"
}

# Histórico
GET /api/transactions/account/{account_id}/history
Authorization: Bearer <token>
```

## 🔒 Segurança Implementada

### Autenticação
- ✅ JWT com expiração configurável
- ✅ Refresh tokens com revogação
- ✅ Senhas com bcrypt (12 rounds)
- ✅ Rate limiting

### Dados
- ✅ Encriptação de CPF (Fernet)
- ✅ Senhas nunca armazenadas em texto
- ✅ HTTPS pronto para produção
- ✅ CORS configurado

### Autorização
- ✅ Validação por ownership
- ✅ Roles (admin/usuário)
- ✅ Permissões granulares

### Auditoria
- ✅ Logs de todas as ações
- ✅ Rastreamento de usuário
- ✅ IP do cliente registrado
- ✅ Status de resposta

## 🧪 Executar Testes

```bash
cd backend

# Testes rápidos
pytest

# Com cobertura
pytest --cov=app

# Modo verbose
pytest -v

# Teste específico
pytest tests/test_auth.py::test_login_success
```

## 📊 Monitoramento

### Grafana
Acesse http://localhost:3000
- **Usuario**: admin
- **Senha**: admin

### Prometheus
Acesse http://localhost:9090
- Métricas da API
- Saúde dos serviços

### Logs
```bash
# Backend
docker-compose logs -f backend

# Frontend
docker-compose logs -f frontend

# Banco de dados
docker-compose logs -f postgres
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente Críticas
```bash
# SEMPRE alterar em produção
SECRET_KEY=gere-uma-chave-segura-aqui
DATABASE_URL=postgresql://usuario:senha_forte@host:5432/banco_app
ENCRYPTION_KEY=gere-uma-chave-para-criptografia
ALLOWED_ORIGINS=https://seu-dominio.com
DEBUG=False
```

### Checklist de Deploy
- [ ] Altere todas as senhas padrão
- [ ] Configure HTTPS/TLS
- [ ] Ative CORS apenas para domínios conhecidos
- [ ] Configure backup automático do BD
- [ ] Ative logs centralizados
- [ ] Configure alertas no Prometheus
- [ ] Teste a recuperação de desastres
- [ ] Configure firewall

## 📖 Documentação Adicional

- [API Documentation](docs/API.md) - Referência completa da API
- [Architecture](docs/ARCHITECTURE.md) - Design e arquitetura
- [Deployment Guide](docs/DEPLOYMENT.md) - Guia de produção

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Consulte os testes para exemplos
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ para demonstrar excelência em desenvolvimento bancário**
