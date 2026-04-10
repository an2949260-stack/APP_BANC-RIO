"""Testes de autenticação"""
import pytest
from tests.conftest import client


def test_register_new_user():
    """Testa registro de novo usuário"""
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
    
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"


def test_register_duplicate_email():
    """Testa registro com email duplicado"""
    user_data = {
        "email": "user@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "SecurePass123",
        "cpf": "12345678900",
        "birth_date": "1990-01-01T00:00:00",
    }
    
    # Primeiro registro
    client.post("/api/auth/register", json=user_data)
    
    # Segundo registro com mesma email
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 409


def test_login_success():
    """Testa login bem-sucedido"""
    # Registra usuário
    client.post(
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
    
    # Faz login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user@example.com",
            "password": "SecurePass123",
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password():
    """Testa login com senha inválida"""
    # Registra usuário
    client.post(
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
    
    # Tenta login com senha errada
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user@example.com",
            "password": "WrongPassword",
        }
    )
    
    assert response.status_code == 401


def test_health_check():
    """Testa health check"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
