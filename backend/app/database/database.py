"""Configuração do banco de dados"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Engine de banco de dados com pool de conexões
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_recycle=3600,   # Recicla conexões a cada hora
)

# Session local
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()


def get_db():
    """Dependência para obter sessão de banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa banco de dados criando todas as tabelas"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Configurações de conexão do banco"""
    pass  # Modificar conforme necessário para PostgreSQL


def get_engine():
    """Retorna o engine do banco de dados"""
    return engine
