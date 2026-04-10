"""Exceções personalizadas da aplicação"""


class AppException(Exception):
    """Exceção base da aplicação"""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserAlreadyExistsException(AppException):
    """Usuário já existe"""
    
    def __init__(self, message: str = "Usuário já existe"):
        super().__init__(message, 409)


class UserNotFoundException(AppException):
    """Usuário não encontrado"""
    
    def __init__(self, message: str = "Usuário não encontrado"):
        super().__init__(message, 404)


class InvalidCredentialsException(AppException):
    """Credenciais inválidas"""
    
    def __init__(self, message: str = "Credenciais inválidas"):
        super().__init__(message, 401)


class UnauthorizedException(AppException):
    """Não autorizado"""
    
    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, 401)


class AccountNotFoundException(AppException):
    """Conta não encontrada"""
    
    def __init__(self, message: str = "Conta não encontrada"):
        super().__init__(message, 404)


class InsufficientFundsException(AppException):
    """Saldo insuficiente"""
    
    def __init__(self, message: str = "Saldo insuficiente"):
        super().__init__(message, 400)


class TransactionException(AppException):
    """Erro na transação"""
    
    def __init__(self, message: str = "Erro ao processar transação"):
        super().__init__(message, 400)


class ValidationException(AppException):
    """Erro de validação"""
    
    def __init__(self, message: str = "Erro de validação"):
        super().__init__(message, 422)


class PermissionDeniedException(AppException):
    """Permissão negada"""
    
    def __init__(self, message: str = "Permissão negada"):
        super().__init__(message, 403)
