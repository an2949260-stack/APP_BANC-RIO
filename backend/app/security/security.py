"""Utilitários de segurança - Hash e Encryption"""
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib

# SHA-256 + bcrypt para hash de senhas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """Faz hash da senha usando bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


class EncryptionManager:
    """Gerenciador de encriptação para dados sensíveis"""
    
    def __init__(self, key: str = settings.ENCRYPTION_KEY):
        """Inicializa com chave de encriptação."""
        if isinstance(key, str):
            raw_key = key.encode("utf-8")
        else:
            raw_key = key

        digest = hashlib.sha256(raw_key).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        self.cipher = Fernet(fernet_key)
    
    def encrypt(self, data: str) -> str:
        """Encripta uma string"""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decripta uma string"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    @staticmethod
    def generate_key() -> str:
        """Gera uma nova chave de encriptação"""
        return Fernet.generate_key().decode()


# Instância global
encryption_manager = EncryptionManager()
