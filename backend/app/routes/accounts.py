"""Rotas de contas bancárias"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import AccountCreate, AccountResponse, AccountDetailResponse, PaginatedResponse
from app.services import AccountService
from app.utils import get_current_user
from app.utils.exceptions import AccountNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_create: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova conta bancária"""
    try:
        account = AccountService.create_account(db, current_user.id, account_create)
        logger.info(f"Account created for user {current_user.email}: {account.account_number}")
        return account
    except Exception as e:
        logger.error(f"Create account error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar conta"
        )


@router.get("/", response_model=PaginatedResponse)
async def list_accounts(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista as contas do usuário"""
    try:
        accounts, total = AccountService.get_user_accounts(
            db,
            current_user.id,
            skip,
            limit
        )
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": accounts
        }
    except Exception as e:
        logger.error(f"List accounts error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao listar contas"
        )


@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de uma conta"""
    try:
        account = AccountService.get_account_by_id(db, account_id)
        
        # Valida se a conta pertence ao usuário
        if account.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        return account
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get account error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter conta"
        )


@router.get("/{account_id}/balance", response_model=dict)
async def get_account_balance(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o saldo de uma conta"""
    try:
        account = AccountService.get_account_by_id(db, account_id)
        
        # Valida se a conta pertence ao usuário
        if account.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        available_balance = account.balance + account.overdraft_limit
        
        return {
            "account_id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
            "overdraft_limit": account.overdraft_limit,
            "available_balance": available_balance
        }
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get balance error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter saldo"
        )


@router.get("/total-balance", response_model=dict)
async def get_total_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o saldo total do usuário em todas as contas"""
    try:
        total_balance = AccountService.get_total_balance(db, current_user.id)
        return {
            "user_id": current_user.id,
            "total_balance": total_balance
        }
    except Exception as e:
        logger.error(f"Get total balance error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter saldo total"
        )
