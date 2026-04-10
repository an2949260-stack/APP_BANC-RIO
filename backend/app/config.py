"""Configurações da aplicação"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurações gerenciais da aplicação"""
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/banco_app"
    DATABASE_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "your-encryption-key-for-sensitive-data"
    
    # App Settings
    DEBUG: bool = False
    ENV: str = "production"
    APP_NAME: str = "BancoApp"
    APP_VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOKI_URL: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_PORT: int = 8001
    ENABLE_PROFILING: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_origins_list(self) -> list:
        """Retorna lista de origens permitidas"""
        return self.ALLOWED_ORIGINS.split(",")


settings = Settings()
