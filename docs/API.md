# Documentação da API

## Base URL
```
http://localhost:8000/api
```

## Autenticação
Todas as rotas protegidas requerem:
```
Authorization: Bearer <access_token>
```

## Respostas

### Sucesso (2xx)
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  ...
}
```

### Erros (4xx, 5xx)
```json
{
  "detail": "Descrição do erro",
  "error": "NomeDaExcecao"
}
```

## Endpoints de Autenticação

### POST /auth/register
Registra um novo usuário.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "user123",
  "full_name": "John Doe",
  "password": "SecurePass123",
  "cpf": "12345678900",
  "birth_date": "1990-01-01T00:00:00"
}
```

**Response:** 201
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user123",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false
}
```

### POST /auth/login
Autentica usuário e retorna tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** 200
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/refresh
Renova o access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** 200
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/logout
Faz logout revogando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** 200
```json
{
  "message": "Logout realizado com sucesso"
}
```

## Endpoints de Usuários

### GET /users/me
Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "is_admin": false
}
```

### PUT /users/me
Atualiza perfil do usuário.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "full_name": "New Name",
  "phone": "11999999999",
  "address": "Rua X, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234567"
}
```

**Response:** 200
```json
{
  "id": "uuid",
  "full_name": "New Name",
  "phone": "11999999999"
}
```

### POST /users/change-password
Altera a senha do usuário.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `old_password` (string, required)
- `new_password` (string, required)

**Response:** 200
```json
{
  "message": "Senha alterada com sucesso"
}
```

### POST /users/deactivate
Desativa a conta do usuário.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "message": "Conta desativada com sucesso"
}
```

## Endpoints de Contas

### POST /accounts/
Cria uma nova conta bancária.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "account_type": "corrente",
  "overdraft_limit": 1000.0
}
```

**Response:** 201
```json
{
  "id": "uuid",
  "account_number": "12345-6",
  "account_type": "corrente",
  "balance": 0.0,
  "overdraft_limit": 1000.0,
  "is_active": true,
  "created_at": "2024-01-01T10:00:00"
}
```

### GET /accounts/
Lista contas do usuário com paginação.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 10, max: 100)

**Response:** 200
```json
{
  "total": 2,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": "uuid",
      "account_number": "12345-6",
      "account_type": "corrente",
      "balance": 1500.0
    }
  ]
}
```

### GET /accounts/{account_id}
Obtém detalhes de uma conta.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "id": "uuid",
  "account_number": "12345-6",
  "account_type": "corrente",
  "balance": 1500.0,
  "overdraft_limit": 1000.0,
  "available_balance": 2500.0
}
```

### GET /accounts/{account_id}/balance
Obtém saldo da conta.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "account_id": "uuid",
  "account_number": "12345-6",
  "balance": 1500.0,
  "overdraft_limit": 1000.0,
  "available_balance": 2500.0
}
```

### GET /accounts/total-balance
Obtém saldo total em todas as contas.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "user_id": "uuid",
  "total_balance": 5000.0
}
```

## Endpoints de Transações

### POST /transactions/deposit
Realiza um depósito.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `account_id` (string, required)
- `amount` (float, required, > 0)
- `description` (string, default: "Depósito")

**Response:** 201
```json
{
  "id": "uuid",
  "transaction_type": "deposito",
  "amount": 500.0,
  "status": "aprovada",
  "created_at": "2024-01-01T10:00:00",
  "processed_at": "2024-01-01T10:00:01"
}
```

### POST /transactions/withdrawal
Realiza um saque.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `account_id` (string, required)
- `amount` (float, required, > 0)
- `description` (string, default: "Saque")

**Response:** 201
```json
{
  "id": "uuid",
  "transaction_type": "saque",
  "amount": 100.0,
  "status": "aprovada",
  "created_at": "2024-01-01T10:00:00"
}
```

### POST /transactions/transfer
Realiza uma transferência.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `source_account_id` (string, required)

**Request:**
```json
{
  "target_account_number": "54321-0",
  "amount": 250.0,
  "description": "Pagamento"
}
```

**Response:** 201
```json
{
  "id": "uuid",
  "transaction_type": "transferencia",
  "amount": 250.0,
  "status": "aprovada",
  "reference_id": "target_account_id"
}
```

### GET /transactions/{transaction_id}
Obtém detalhes de uma transação.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200
```json
{
  "id": "uuid",
  "transaction_type": "transferencia",
  "amount": 250.0,
  "status": "aprovada",
  "description": "Pagamento",
  "created_at": "2024-01-01T10:00:00"
}
```

### GET /transactions/account/{account_id}/history
Histórico de transações da conta.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20, max: 100)

**Response:** 200
```json
{
  "total": 5,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "transaction_type": "deposito",
      "amount": 500.0,
      "status": "aprovada",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

### GET /transactions/user/{user_id}/history
Histórico de transações do usuário.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20)

**Response:** 200
```json
{
  "total": 10,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "uuid",
      "transaction_type": "saque",
      "amount": 100.0,
      "status": "aprovada"
    }
  ]
}
```

## Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Erro de validação |
| 401 | Unauthorized - Sem autenticação |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 409 | Conflict - Conflito (ex: email duplicado) |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Internal Server Error - Erro do servidor |

## Erros Comuns

### 401 - Token inválido ou expirado
```json
{
  "detail": "Token inválido ou expirado",
  "error": "UnauthorizedException"
}
```

### 400 - Saldo insuficiente
```json
{
  "detail": "Saldo insuficiente. Disponível: 500.0",
  "error": "InsufficientFundsException"
}
```

### 409 - Email já cadastrado
```json
{
  "detail": "Email ou username já cadastrado",
  "error": "UserAlreadyExistsException"
}
```

### 404 - Recurso não encontrado
```json
{
  "detail": "Conta 12345 não encontrada",
  "error": "AccountNotFoundException"
}
```

## Exemplos de Uso com cURL

### Registrar
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "full_name": "John Doe",
    "password": "SecurePass123",
    "cpf": "12345678900",
    "birth_date": "1990-01-01T00:00:00"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Obter Perfil
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Criar Conta
```bash
curl -X POST "http://localhost:8000/api/accounts/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_type": "corrente",
    "overdraft_limit": 1000.0
  }'
```

---

Para mais informações, visite http://localhost:8000/api/docs
