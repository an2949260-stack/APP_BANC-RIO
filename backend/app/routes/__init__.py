"""__init__ para routes"""
from .auth import router as auth_router
from .users import router as users_router
from .accounts import router as accounts_router
from .transactions import router as transactions_router

__all__ = [
    "auth_router",
    "users_router",
    "accounts_router",
    "transactions_router",
]
