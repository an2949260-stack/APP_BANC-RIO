"""Rotas de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services import UserService
from app.security import create_tokens, verify_token
from app.models import RefreshToken
from app.utils.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from datetime import datetime, timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registra um novo usuário"""
    try:
        user = UserService.create_user(db, user_data)
        logger.info(f"New user registered: {user.email}")
        return user
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao registrar usuário"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Autentica usuário e retorna tokens"""
    try:
        user = UserService.authenticate_user(
            db,
            credentials.email,
            credentials.password
        )
        
        tokens = create_tokens(user.id)
        
        # Salva refresh token no banco
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=tokens.refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_token_obj)
        db.commit()
        
        logger.info(f"User login successful: {user.email}")
        return tokens
    
    except InvalidCredentialsException as e:
        logger.warning(f"Login failed for {credentials.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao fazer login"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Renova o access token usando refresh token"""
    try:
        # Verifica o refresh token
        payload = verify_token(request.refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        # Verifica se o token existe no banco e não foi revogado
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == request.refresh_token,
            RefreshToken.is_revoked == False
        ).first()
        
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revogado ou expirado"
            )
        
        user_id = payload.get("sub")
        tokens = create_tokens(user_id)
        
        # Revoga o refresh token antigo
        token_obj.is_revoked = True
        
        # Salva novo refresh token
        new_token_obj = RefreshToken(
            user_id=user_id,
            token=tokens.refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_token_obj)
        db.commit()
        
        logger.info(f"Token refreshed for user: {user_id}")
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao renovar token"
        )


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Faz logout revogando o refresh token"""
    try:
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == request.refresh_token
        ).first()
        
        if token_obj:
            token_obj.is_revoked = True
            db.commit()
            logger.info(f"User logged out: {token_obj.user_id}")
        
        return {"message": "Logout realizado com sucesso"}
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao fazer logout"
        )
