"""Testes de contas bancárias"""
import pytest
from tests.conftest import client


@pytest.fixture
def registered_user():
    """Fixture de usuário registrado"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "SecurePass123",
            "cpf": "12345678900",
            "birth_date": "1990-01-01T00:00:00",
        }
    )
    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """Fixture de headers de autenticação"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user@example.com",
            "password": "SecurePass123",
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_account(auth_headers):
    """Testa criação de conta bancária"""
    response = client.post(
        "/api/accounts/",
        json={
            "account_type": "corrente",
            "overdraft_limit": 1000.0,
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    assert response.json()["account_type"] == "corrente"


def test_list_accounts(auth_headers):
    """Testa listagem de contas"""
    # Cria uma conta
    client.post(
        "/api/accounts/",
        json={
            "account_type": "corrente",
            "overdraft_limit": 1000.0,
        },
        headers=auth_headers,
    )
    
    # Lista contas
    response = client.get("/api/accounts/", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_account_balance(auth_headers):
    """Testa obtenção de saldo"""
    # Cria uma conta
    create_response = client.post(
        "/api/accounts/",
        json={
            "account_type": "corrente",
            "overdraft_limit": 1000.0,
        },
        headers=auth_headers,
    )
    
    account_id = create_response.json()["id"]
    
    # Obtém saldo
    response = client.get(
        f"/api/accounts/{account_id}/balance",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    assert response.json()["balance"] == 0.0
