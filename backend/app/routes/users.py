"""Rotas de usuários"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate, PaginationParams, PaginatedResponse
from app.services import UserService
from app.utils import get_current_user, get_admin_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Retorna papel do usuário autenticado"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza o perfil do usuário autenticado"""
    try:
        user = UserService.update_user(db, current_user.id, user_update)
        logger.info(f"User profile updated: {current_user.email}")
        return user
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar perfil"
        )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Altera a senha do usuário"""
    try:
        UserService.change_password(db, current_user.id, old_password, new_password)
        logger.info(f"Password changed for user: {current_user.email}")
        return {"message": "Senha alterada com sucesso"}
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desativa a conta do usuário"""
    try:
        UserService.deactivate_user(db, current_user.id)
        logger.warning(f"User account deactivated: {current_user.email}")
        return {"message": "Conta desativada com sucesso"}
    except Exception as e:
        logger.error(f"Deactivate account error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao desativar conta"
        )


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Lista todos os usuários (apenas admin)"""
    try:
        users, total = UserService.list_users(db, skip, limit)
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": users
        }
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao listar usuários"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém dados de um usuário"""
    try:
        # Usuários normais só podem acessar seus próprios dados
        if current_user.id != user_id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        user = UserService.get_user_by_id(db, user_id)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
