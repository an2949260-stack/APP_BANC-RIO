# 🏗️ Arquitetura do Sistema Bancário

## Visão Geral

Este é um sistema bancário profissional construído com arquitetura em camadas, seguindo padrões de design bem estabelecidos e melhores práticas da indústria.

## Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (UI)                      │
│       Streamlit Web Interface - Porta 8501          │
└────────────────────┬────────────────────────────────┘
                     │
    ┌────────────────│────────────────────────────┐
    │                │                            │  
┌───►GET / POST   ┌─┴──────────────────────────┐ │
│                 │   FastAPI REST API         │◄┘
│                 │   (Porta 8000)             │
│                 └────────────────────────────┘
│                        │
│         ┌──────────────┼──────────────┐
│         │              │              │
│     ┌───▼────┐    ┌───▼──────┐  ┌───▼───┐
│     │Schemas │    │Services  │  │Routes │
│     │Pydantic│    │Business  │  │API    │
│     └────────┘    │Logic     │  └───────┘
│                   └──────────┘
│
│         ┌──────────────┬──────────────┐
│         │              │              │
│     ┌───▼────┐    ┌───▼──────┐  ┌───▼──────┐
│     │Security│    │Database  │  │Utils     │
│     │JWT/Crypto   │ORM       │  │Exceções  │
│     └────────┘    └────┬─────┘  └──────────┘
│                        │
└────────────────────────┼─────────────────────┘
                         │
         ┌───────────────┼────────────────┐
         │               │                │
    ┌────▼────┐     ┌───▼──────┐    ┌───▼────┐
    │PostgreSQL    │Redis      │    │Prometheus
    │Database      │Cache      │    │Monitoring
    └────────┘     └───────────┘    └────────┘
```

## Componentes Principales

### 1. Frontend (Streamlit)
- **Localização**: `frontend/app.py`
- **Responsabilidades**:
  - Interface visual para usuários
  - Gerenciamento de estado da sessão
  - Consumo da API REST
  - Validação básica de entrada

### 2. Backend API (FastAPI)
- **Localização**: `backend/main.py`
- **Responsabilidades**:
  - Exposição de endpoints REST
  - Validação de requisições
  - Processamento de lógica de negócio
  - Segurança (autenticação/autorização)

### 3. Modelos de Dados
- **Localização**: `backend/app/models/`
- **Entidades**:
  - `User`: Usuários do sistema
  - `Account`: Contas bancárias
  - `Transaction`: Movimentações financeiras
  - `AuditLog`: Registro de ações
  - `RefreshToken`: Tokens de renovação

### 4. Serviços (Lógica de Negócio)
- **Localização**: `backend/app/services/`
- **Classes**:
  - `UserService`: Gerenciamento de usuários
  - `AccountService`: Operações com contas
  - `TransactionService`: Processamento de transações

### 5. Rotas (Endpoints)
- **Localização**: `backend/app/routes/`
- **Grupos**:
  - `auth.py`: Autenticação e autorização
  - `users.py`: Gerenciamento de usuários
  - `accounts.py`: Operações com contas
  - `transactions.py`: Transações financeiras

### 6. Segurança
- **Localização**: `backend/app/security/`
- **Componentes**:
  - `security.py`: Hash de senhas e encriptação
  - `jwt_handler.py`: Geração e validação de tokens JWT

### 7. Database
- **Localização**: `backend/app/database/`
- **Recursos**:
  - Conexão com PostgreSQL
  - Pool de conexões
  - Sessões SQLAlchemy

### 8. Utilitários
- **Localização**: `backend/app/utils/`
- **Componentes**:
  - `exceptions.py`: Exceções personalizadas
  - `logging.py`: Sistema de logs
  - `dependencies.py`: Dependências FastAPI

## Fluxos de Dados Principais

### 1. Fluxo de Autenticação
```
Usuario (UI)
    │
    ├─► POST /api/auth/register
    │   └─> UserService.create_user()
    │       └─> Banco de dados
    │       └─> JWT gerado
    │
    └─► POST /api/auth/login
        └─> UserService.authenticate_user()
            └─> Verifica senha
            └─> Gera tokens (access + refresh)
```

### 2. Fluxo de Transação (Saque)
```
Usuario (UI)
    │
    └─► POST /api/transactions/withdrawal
        │
        ├─► Valida autenticação (JWT)
        │
        ├─► TransactionService.create_withdrawal()
        │   ├─> Cria registro de transação
        │   ├─> AccountService.update_balance()
        │   │   └─> Valida saldo disponível
        │   │   └─> Atualiza saldo
        │   ├─> Registra auditoria
        │   └─> Retorna confirmação
        │
        └─► Resposta HTTP 201 (Sucesso)
```

### 3. Fluxo de Transferência
```
Usuario A (UI)
    │
    └─► POST /api/transactions/transfer
        │
        ├─► Valida autenticação (Usuario A)
        ├─► Valida ownership da conta de origem
        ├─► Valida existência da conta destino
        │
        ├─► TransactionService.create_transfer()
        │   ├─> Saque da conta A
        │   ├─► Depósito na conta B
        │   └─> Registra relacionamento
        │
        └─► Resposta (Sucesso/Erro)
```

## Padrões de Design

### 1. MVC (Model-View-Controller)
- **Models**: `app/models/` - Representação de dados
- **Views**: `frontend/` - Interface web
- **Controllers**: `app/routes/` + `app/services/` - Lógica

### 2. Dependência (Dependency Injection)
```python
# FastAPI injeta dependências automaticamente
async def endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
```

### 3. Service Layer
- Separa lógica de negócio das rotas
- Reutilizável por múltiplos endpoints
- Testável independentemente

### 4. Factory Pattern
- `SessionLocal()`: Cria sessões de BD
- `create_tokens()`: Cria tokens JWT

### 5. Singleton
- `encryption_manager`: Instância única
- `settings`: Configurações globais

## Segurança em Camadas

### Nível 1: Autenticação
- JWT com expiração
- Refresh token com revogação
- Senha bcrypt com 12 rounds

### Nível 2: Autorização
- Validação de ownership
- Roles (admin/usuário)
- Permissões granulares

### Nível 3: Encriptação
- CPF encriptado com Fernet
- Conexão HTTPS em produção
- CORS configurado

### Nível 4: Auditoria
- Logs de todas as ações
- Rastreamento de usuário/IP
- Timestamps para tudo

### Nível 5: Validação
- Schemas Pydantic
- Constraints de BD
- Context de negócio

## Performance

### Caching
- Redis para dados frequentes
- Cache de resultado de queries

### Índices no Banco
```sql
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_account_user ON accounts(user_id);
CREATE INDEX idx_transaction_created ON transactions(created_at);
```

### Pool de Conexões
- Min: 10 conexões
- Max: 30 conexões
- Timeout: 30s

### Async/Await
- FastAPI é assíncrona
- Operações não-bloqueantes

## Monitoramento

### Logs
- Estruturados em JSON
- Enviados para Loki
- Searchable no Grafana

### Métricas
- Prometheus scrapa `/metrics`
- Dashboards no Grafana
- Alertas configuráveis

### Health Check
- Endpoint: `GET /api/health`
- Status de banco de dados
- Status de dependências

## Testes

### Unitários
- Testam funções individuais
- Mock de dependências
- Rápidos (< 1s)

### Integração
- Testam endpoints da API
- Banco de testes SQLite
- Mais lentes mas realísticos

### Cobertura
- Meta: 80%+
- Crítico: 100%

## Deployment

### Desenvolvimento
```bash
docker-compose up -d
```

### Produção
1. Build das imagens
2. Push para registry
3. Orquestração com Kubernetes
4. Nginx como load balancer
5. PostgreSQL managed

## Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| Backend | FastAPI + Python 3.11 |
| Frontend | Streamlit + React |
| Banco | PostgreSQL 16 |
| Cache | Redis 7 |
| Autenticação | JWT + bcrypt |
| Criptografia | Fernet (cryptography) |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic v2 |
| Testes | pytest |
| Monitoramento | Prometheus + Grafana |
| Logging | Structured JSON |
| Container | Docker |

## Escalabilidade

### Horizontal
- Múltiplas instâncias da API
- Load balancer (Nginx/HAProxy)
- Redis compartilhado
- PostgreSQL com replicação

### Vertical
- Aumentar recursos dos containers
- Otimizar queries
- Cache mais eficiente

## Próximas Melhorias

1. **GraphQL**: Interface alternativa às REST
2. **WebSocket**: Notificações em tempo real
3. **Mobile**: App nativo iOS/Android
4. **Machine Learning**: Detecção de fraude
5. **Blockchain**: Auditoria imutável
6. **Microserviços**: Separar domínios
7. **CQRS**: Separar leitura/escrita
8. **Event Sourcing**: Auditoria de eventos

---

**Arquitetura robusta para ambientes de produção profissional**
