"""Serviço de transações"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models import Transaction, TransactionType, TransactionStatus
from app.schemas import TransactionCreate, TransactionTransfer
from app.services.account_service import AccountService
from app.utils.exceptions import TransactionException
import logging
import json

logger = logging.getLogger(__name__)


class TransactionService:
    """Serviço de gerenciamento de transações"""
    
    @staticmethod
    def create_deposit(
        db: Session,
        account_id: str,
        user_id: str,
        amount: float,
        description: str = "Depósito"
    ) -> Transaction:
        """Cria uma transação de depósito"""
        transaction = Transaction(
            user_id=user_id,
            account_id=account_id,
            transaction_type=TransactionType.DEPOSITO,
            amount=amount,
            description=description,
            status=TransactionStatus.PENDENTE,
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Processa o depósito
        TransactionService._process_transaction(db, transaction)
        
        return transaction
    
    @staticmethod
    def create_withdrawal(
        db: Session,
        account_id: str,
        user_id: str,
        amount: float,
        description: str = "Saque"
    ) -> Transaction:
        """Cria uma transação de saque"""
        transaction = Transaction(
            user_id=user_id,
            account_id=account_id,
            transaction_type=TransactionType.SAQUE,
            amount=amount,
            description=description,
            status=TransactionStatus.PENDENTE,
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Processa o saque
        TransactionService._process_transaction(db, transaction)
        
        return transaction
    
    @staticmethod
    def create_transfer(
        db: Session,
        source_account_id: str,
        user_id: str,
        transfer_data: TransactionTransfer
    ) -> Transaction:
        """Cria uma transação de transferência"""
        target_account = AccountService.get_account_by_number(
            db,
            transfer_data.target_account_number
        )
        
        # Cria transação de saída
        transaction = Transaction(
            user_id=user_id,
            account_id=source_account_id,
            transaction_type=TransactionType.TRANSFERENCIA,
            amount=transfer_data.amount,
            description=f"Transferência para {transfer_data.target_account_number}",
            status=TransactionStatus.PENDENTE,
            reference_id=target_account.id,
            metadata_json=json.dumps({
                "target_account_number": transfer_data.target_account_number,
                "target_account_id": target_account.id,
                "initiated_by": user_id,
            }),
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Processa a transferência
        TransactionService._process_transaction(db, transaction)
        
        return transaction
    
    @staticmethod
    def _process_transaction(db: Session, transaction: Transaction) -> None:
        """Processa uma transação"""
        try:
            account = AccountService.get_account_by_id(db, transaction.account_id)
            
            if transaction.transaction_type == TransactionType.DEPOSITO:
                AccountService.update_balance(
                    db,
                    account.id,
                    transaction.amount,
                    "deposit"
                )
            
            elif transaction.transaction_type == TransactionType.SAQUE:
                AccountService.update_balance(
                    db,
                    account.id,
                    transaction.amount,
                    "withdrawal"
                )
            
            elif transaction.transaction_type == TransactionType.TRANSFERENCIA:
                # Saída da conta de origem
                AccountService.update_balance(
                    db,
                    account.id,
                    transaction.amount,
                    "withdrawal"
                )
                
                # Entrada na conta de destino
                if transaction.reference_id:
                    target_account = AccountService.get_account_by_id(
                        db,
                        transaction.reference_id
                    )
                    AccountService.update_balance(
                        db,
                        target_account.id,
                        transaction.amount,
                        "deposit"
                    )
            
            transaction.status = TransactionStatus.APROVADA
            transaction.processed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Transaction processed: {transaction.id}")
        
        except Exception as e:
            transaction.status = TransactionStatus.REJEITADA
            db.commit()
            logger.error(f"Transaction processing failed: {transaction.id}, {str(e)}")
            raise TransactionException(f"Erro ao processar transação: {str(e)}")
    
    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: str) -> Transaction:
        """Obtém transação por ID"""
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        if not transaction:
            raise TransactionException(f"Transação {transaction_id} não encontrada")
        return transaction
    
    @staticmethod
    def get_account_transactions(
        db: Session,
        account_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Transaction], int]:
        """Lista transações da conta"""
        query = db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).order_by(desc(Transaction.created_at))
        
        total = query.count()
        transactions = query.offset(skip).limit(limit).all()
        
        return transactions, total
    
    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Transaction], int]:
        """Lista transações do usuário"""
        query = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(desc(Transaction.created_at))
        
        total = query.count()
        transactions = query.offset(skip).limit(limit).all()
        
        return transactions, total
