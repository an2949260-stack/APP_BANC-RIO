"""Sistema de logging centralizado"""
import logging
import json
from datetime import datetime
from typing import Any, Optional
from pythonjsonlogger import jsonlogger
import sys

# Configuração básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def setup_logging(app_name: str, log_level: str = "INFO"):
    """Configura logging para a aplicação"""
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter JSON para logs estruturados
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Obtém logger raiz
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)
    
    logger.info(f"Logging configured for {app_name}")


def log_action(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Registra uma ação de usuário para auditoria"""
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": ip_address,
    }
    
    logger.info(json.dumps(log_entry))


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    details: Optional[dict] = None,
    severity: str = "WARNING"
) -> None:
    """Registra eventos de segurança"""
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "severity": severity,
        "details": details or {},
    }
    
    if severity == "CRITICAL":
        logger.critical(json.dumps(log_entry))
    elif severity == "WARNING":
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))


def log_transaction(
    transaction_id: str,
    user_id: str,
    transaction_type: str,
    amount: float,
    status: str,
    details: Optional[dict] = None
) -> None:
    """Registra transação para auditoria"""
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "transaction_id": transaction_id,
        "user_id": user_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "status": status,
        "details": details or {},
    }
    
    logger.info(json.dumps(log_entry))
