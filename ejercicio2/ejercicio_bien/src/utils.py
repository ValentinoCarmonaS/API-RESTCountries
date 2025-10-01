# utils.py
# Parsers, validadores de esquema, conversor de tipos, excepción custom.

"""
Funciones de utilidad para validación de datos y conversión de tipos.

Este módulo proporciona funciones reutilizables para analizar, validar,
y convertir tipos de datos en todo el sistema de ventas.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from decimal import Decimal, InvalidOperation

from exceptions import DataValidationError

logger = logging.getLogger(__name__)


def parse_date(date_str: str, date_format: str = '%Y-%m-%d') -> datetime:
    """
    Analiza una cadena de fecha en un objeto datetime.
    
    Args:
        date_str: Cadena de fecha a analizar
        date_format: Formato de fecha esperado (predeterminado: '%Y-%m-%d')
        
    Returns:
        Objeto datetime analizado
        
    Raises:
        DataValidationError: Si la cadena de fecha es inválida
    """
    try:
        return datetime.strptime(date_str, date_format)
    except (ValueError, TypeError) as e:
        raise DataValidationError(f"Formato de fecha inválido '{date_str}': {e}")


def parse_number(value: Any, field_name: str = "value") -> float:
    """
    Analiza un valor numérico, manejando cadenas y varios formatos.
    
    Args:
        value: Valor a analizar (puede ser str, int, float)
        field_name: Nombre del campo (para mensajes de error)
        
    Returns:
        Valor flotante
        
    Raises:
        DataValidationError: Si el valor no se puede convertir a flotante
    """
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise DataValidationError(
            f"Valor numérico inválido para {field_name}: '{value}' - {e}"
        )


def validate_sale_record(record: Dict[str, Any]) -> Dict[str, str]:
    """
    Valida que un registro de venta tenga todos los campos requeridos.
    
    Args:
        record: Diccionario que contiene los datos de la venta
        
    Returns:
        Diccionario de errores de validación (vacío si es válido)
    """
    errors = {}
    required_fields = ['user_id', 'date', 'price', 'quantity']
    
    for field in required_fields:
        if field not in record or record[field] is None or record[field] == '':
            errors[field] = f"Campo requerido faltante o vacío: {field}"
    
    return errors


def normalize_user_id(user_id: Any) -> str:
    """
    Normaliza el user_id a formato de cadena para una comparación consistente.
    
    Args:
        user_id: ID de usuario en cualquier formato
        
    Returns:
        ID de usuario normalizado como cadena
    """
    return str(user_id).strip()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Divide dos números de forma segura, devolviendo un valor predeterminado si el denominador es cero.
    
    Args:
        numerator: Valor del numerador
        denominator: Valor del denominador
        default: Valor a devolver si el denominador es cero
        
    Returns:
        Resultado de la división o valor predeterminado
    """
    if denominator == 0:
        logger.warning(f"Intento de división por cero: {numerator}/{denominator}")
        return default
    return numerator / denominator
