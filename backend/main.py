"""Aplicação FastAPI principal"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database import init_db, get_db
from app.routes import auth_router, users_router, accounts_router, transactions_router
from app.utils import setup_logging
from app.utils.exceptions import AppException

# Setup logging
setup_logging(settings.APP_NAME, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Contexto de inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia eventos de startup e shutdown"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Criação da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    description="API Bancária Profissional com Autenticação, Segurança e Encriptação",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """Handler para exceções da aplicação"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error": exc.__class__.__name__},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handler para exceções genéricas"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"},
    )


# Health check
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Verificação de saúde da aplicação"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }


# Rotas
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(accounts_router)
app.include_router(transactions_router)


@app.get("/", tags=["Root"])
async def root():
    """Rota raiz da aplicação"""
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
