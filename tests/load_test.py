"""Testes de carga com Locust"""
from locust import HttpUser, task, between
import random
import string


class BankAppUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.token = None
        self.account_id = None
    
    @task(1)
    def register(self):
        """Teste de registro"""
        email = f"user_{random.randint(1,100000)}@test.com"
        payload = {
            "email": email,
            "username": f"user_{random.randint(1,100000)}",
            "full_name": "Test User",
            "password": "SecurePass123",
            "cpf": f"{random.randint(10000000000, 99999999999)}",
            "birth_date": "1990-01-01T00:00:00"
        }
        self.client.post("/api/auth/register", json=payload)
    
    @task(2)
    def login(self):
        """Teste de login"""
        payload = {
            "email": "teste@example.com",
            "password": "SecurePass123"
        }
        response = self.client.post("/api/auth/login", json=payload)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    @task(1)
    def get_profile(self):
        """Teste de obter perfil"""
        if self.token:
            self.client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
    
    @task(2)
    def list_accounts(self):
        """Teste de listar contas"""
        if self.token:
            self.client.get(
                "/api/accounts/",
                headers={"Authorization": f"Bearer {self.token}"}
            )
    
    @task(1)
    def create_account(self):
        """Teste de criar conta"""
        if self.token:
            payload = {
                "account_type": "corrente",
                "overdraft_limit": 1000.0
            }
            response = self.client.post(
                "/api/accounts/",
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 201:
                self.account_id = response.json()["id"]
    
    @task(2)
    def health_check(self):
        """Teste de health check"""
        self.client.get("/api/health")


if __name__ == "__main__":
    """
    Executar com:
    locust -f tests/load_test.py -u 100 -r 10 --run-time 60s
    
    Parâmetros:
    -u: número de usuários
    -r: taxa de spawn (usuários por segundo)
    --run-time: duração do teste
    -H: URL base (padrão http://localhost:8000)
    """
    print(__doc__)
