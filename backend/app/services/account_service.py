"""Serviço de contas bancárias"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Account, AccountType
from app.schemas import AccountCreate, AccountResponse
from app.utils.exceptions import (
    AccountNotFoundException,
    InsufficientFundsException,
)
import logging
import random

logger = logging.getLogger(__name__)


class AccountService:
    """Serviço de gerenciamento de contas bancárias"""
    
    @staticmethod
    def create_account(
        db: Session,
        user_id: str,
        account_create: AccountCreate
    ) -> Account:
        """Cria uma nova conta para o usuário"""
        # Gera número de conta único
        account_number = AccountService._generate_account_number(db)
        
        account = Account(
            user_id=user_id,
            account_number=account_number,
            account_type=account_create.account_type,
            overdraft_limit=account_create.overdraft_limit if account_create.account_type == AccountType.CORRENTE else 0.0,
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        logger.info(f"Account created for user {user_id}: {account_number}")
        return account
    
    @staticmethod
    def _generate_account_number(db: Session) -> str:
        """Gera um número de conta único"""
        while True:
            account_number = f"{random.randint(10000, 99999)}-{random.randint(0, 9)}"
            existing = db.query(Account).filter(
                Account.account_number == account_number
            ).first()
            if not existing:
                return account_number
    
    @staticmethod
    def get_account_by_id(db: Session, account_id: str) -> Account:
        """Obtém conta por ID"""
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise AccountNotFoundException(f"Conta {account_id} não encontrada")
        return account
    
    @staticmethod
    def get_account_by_number(db: Session, account_number: str) -> Account:
        """Obtém conta por número"""
        account = db.query(Account).filter(
            Account.account_number == account_number
        ).first()
        if not account:
            raise AccountNotFoundException(f"Conta {account_number} não encontrada")
        return account
    
    @staticmethod
    def get_user_accounts(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[list[Account], int]:
        """Lista contas do usuário"""
        query = db.query(Account).filter(Account.user_id == user_id)
        total = query.count()
        accounts = query.offset(skip).limit(limit).all()
        return accounts, total
    
    @staticmethod
    def update_balance(
        db: Session,
        account_id: str,
        amount: float,
        operation_type: str = "deposit"
    ) -> Account:
        """Atualiza o saldo da conta"""
        account = AccountService.get_account_by_id(db, account_id)
        
        if operation_type == "deposit":
            account.balance += amount
        elif operation_type == "withdrawal":
            # Verifica se há saldo suficiente
            available_balance = account.balance + account.overdraft_limit
            if amount > available_balance:
                raise InsufficientFundsException(
                    f"Saldo insuficiente. Disponível: {available_balance}"
                )
            account.balance -= amount
        
        db.commit()
        db.refresh(account)
        
        logger.info(f"Account balance updated: {account_id}, amount: {amount}, type: {operation_type}")
        return account
    
    @staticmethod
    def get_total_balance(db: Session, user_id: str) -> float:
        """Obtém saldo total do usuário em todas as contas"""
        result = db.query(func.sum(Account.balance)).filter(
            Account.user_id == user_id,
            Account.is_active == True
        ).scalar()
        return result or 0.0
