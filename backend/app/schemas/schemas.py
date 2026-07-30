"""Schemas Pydantic para validação de dados"""
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Any, Optional
from app.models import AccountType, TransactionType, TransactionStatus


# ===== USER SCHEMAS =====
class UserBase(BaseModel):
    """Schema base de usuário"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=14)
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8)
    birth_date: datetime
    
    @validator("password")
    def validate_password(cls, v):
        """Valida força da senha"""
        if not any(char.isupper() for char in v):
            raise ValueError("Senha deve conter letras maiúsculas")
        if not any(char.isdigit() for char in v):
            raise ValueError("Senha deve conter números")
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class UserResponse(UserBase):
    """Schema de resposta de usuário"""
    id: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    cpf: str = Field(..., max_length=255)
    
    class Config:
        from_attributes = True


# ===== AUTHENTICATION SCHEMAS =====
class LoginRequest(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema de resposta com token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema para refresh de token"""
    refresh_token: str


# ===== ACCOUNT SCHEMAS =====
class AccountBase(BaseModel):
    """Schema base de conta"""
    account_type: AccountType
    overdraft_limit: float = 0.0


class AccountCreate(AccountBase):
    """Schema para criação de conta"""
    pass


class AccountResponse(AccountBase):
    """Schema de resposta de conta"""
    id: str
    user_id: str
    account_number: str
    balance: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AccountDetailResponse(AccountResponse):
    """Schema detalhado de conta"""
    available_balance: float
    
    @property
    def available_balance(self) -> float:
        """Retorna saldo disponível incluindo limite de saque"""
        return self.balance + self.overdraft_limit


# ===== TRANSACTION SCHEMAS =====
class TransactionBase(BaseModel):
    """Schema base de transação"""
    transaction_type: TransactionType
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema para criação de transação"""
    pass


class TransactionTransfer(BaseModel):
    """Schema para transferência entre contas"""
    target_account_number: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema de resposta de transação"""
    id: str
    account_id: str
    status: TransactionStatus
    reference_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== AUDIT LOG SCHEMAS =====
class AuditLogResponse(BaseModel):
    """Schema de resposta de auditoria"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    status_code: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== PAGINAÇÃO =====
class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Response com paginação"""
    total: int
    skip: int
    limit: int
    items: list[Any]
