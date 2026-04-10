"""Serviço de usuários"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User, AuditLog
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.security import hash_password, verify_password, encryption_manager
from app.utils.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)
from app.utils.logging import log_action
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class UserService:
    """Serviço de gerenciamento de usuários"""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Cria um novo usuário"""
        try:
            # Encripta CPF
            encrypted_cpf = encryption_manager.encrypt(user_create.cpf)
            
            user = User(
                email=user_create.email.lower(),
                username=user_create.username.lower(),
                full_name=user_create.full_name,
                hashed_password=hash_password(user_create.password),
                cpf=encrypted_cpf,
                birth_date=user_create.birth_date,
                phone=user_create.phone,
                address=user_create.address,
                city=user_create.city,
                state=user_create.state,
                zip_code=user_create.zip_code,
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created successfully: {user.email}")
            return user
        
        except IntegrityError:
            db.rollback()
            raise UserAlreadyExistsException(
                "Email ou username já cadastrado"
            )
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Obtém usuário por email"""
        user = db.query(User).filter(
            User.email == email.lower()
        ).first()
        
        if not user:
            raise UserNotFoundException(f"Usuário {email} não encontrado")
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """Obtém usuário por ID"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundException(f"Usuário {user_id} não encontrado")
        
        return user
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> User:
        """Autentica um usuário"""
        user = db.query(User).filter(
            User.email == email.lower()
        ).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException("Email ou senha inválidos")
        
        if not user.is_active:
            raise InvalidCredentialsException("Usuário inativo")
        
        # Atualiza último login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        user_update: UserUpdate
    ) -> User:
        """Atualiza dados do usuário"""
        user = UserService.get_user_by_id(db, user_id)
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> User:
        """Altera a senha do usuário"""
        user = UserService.get_user_by_id(db, user_id)
        
        if not verify_password(old_password, user.hashed_password):
            raise InvalidCredentialsException("Senha atual inválida")
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Password changed for user: {user.email}")
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> User:
        """Desativa um usuário"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        
        logger.warning(f"User deactivated: {user.email}")
        return user
    
    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[list[User], int]:
        """Lista usuários com paginação"""
        query = db.query(User)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total
