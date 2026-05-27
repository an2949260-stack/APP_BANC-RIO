"""Rotas de transações"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionTransfer,
    PaginatedResponse
)
from app.services import TransactionService, AccountService
from app.utils import get_current_user
from app.utils.exceptions import (
    AccountNotFoundException,
    TransactionException,
    InsufficientFundsException,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit(
    account_id: str,
    amount: float = Query(..., gt=0),
    description: str = Query(default="Depósito", max_length=255),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Realiza um depósito em uma conta"""
    try:
        # Valida se a conta pertence ao usuário
        account = AccountService.get_account_by_id(db, account_id)
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        transaction = TransactionService.create_deposit(
            db,
            account_id,
            current_user.id,
            amount,
            description
        )
        
        logger.info(f"Deposit: user={current_user.email}, amount={amount}")
        return transaction
    
    except (AccountNotFoundException, TransactionException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deposit error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao realizar depósito"
        )


@router.post("/withdrawal", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def withdrawal(
    account_id: str,
    amount: float = Query(..., gt=0),
    description: str = Query(default="Saque", max_length=255),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Realiza um saque de uma conta"""
    try:
        # Valida se a conta pertence ao usuário
        account = AccountService.get_account_by_id(db, account_id)
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        transaction = TransactionService.create_withdrawal(
            db,
            account_id,
            current_user.id,
            amount,
            description
        )
        
        logger.info(f"Withdrawal: user={current_user.email}, amount={amount}")
        return transaction
    
    except (AccountNotFoundException, InsufficientFundsException, TransactionException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Withdrawal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao realizar saque"
        )


@router.post("/transfer", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def transfer(
    source_account_id: str,
    transfer_data: TransactionTransfer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Realiza uma transferência entre contas"""
    try:
        # Valida se a conta de origem pertence ao usuário
        source_account = AccountService.get_account_by_id(db, source_account_id)
        if source_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado à conta de origem"
            )
        
        # Valida se a conta de destino existe
        target_account = AccountService.get_account_by_number(
            db,
            transfer_data.target_account_number
        )
        
        if source_account_id == target_account.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível transferir para a mesma conta"
            )
        
        transaction = TransactionService.create_transfer(
            db,
            source_account_id,
            current_user.id,
            transfer_data
        )
        
        logger.info(
            f"Transfer: from_user={current_user.email}, "
            f"to_account={transfer_data.target_account_number}, "
            f"amount={transfer_data.amount}"
        )
        return transaction
    
    except (AccountNotFoundException, InsufficientFundsException, TransactionException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao realizar transferência"
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de uma transação"""
    try:
        transaction = TransactionService.get_transaction_by_id(db, transaction_id)
        
        # Valida se a transação pertence ao usuário
        if transaction.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        return transaction
    except TransactionException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get transaction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter transação"
        )


@router.get("/account/{account_id}/history", response_model=PaginatedResponse[TransactionResponse])
async def get_account_transactions(
    account_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o histórico de transações de uma conta"""
    try:
        # Valida se a conta pertence ao usuário
        account = AccountService.get_account_by_id(db, account_id)
        if account.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        transactions, total = TransactionService.get_account_transactions(
            db,
            account_id,
            skip,
            limit
        )
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": transactions
        }
    except AccountNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get account transactions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter histórico"
        )


@router.get("/user/{user_id}/history", response_model=PaginatedResponse[TransactionResponse])
async def get_user_transactions(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o histórico de transações de um usuário"""
    try:
        # Valida se o usuário está acessando seus próprios dados
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
        
        transactions, total = TransactionService.get_user_transactions(
            db,
            user_id,
            skip,
            limit
        )
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": transactions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user transactions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao obter histórico"
        )
