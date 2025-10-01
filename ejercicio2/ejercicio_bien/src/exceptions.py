"""
Excepciones personalizadas para el sistema de ventas.

Este módulo define excepciones específicas para manejar diferentes escenarios de error
en el pipeline de procesamiento de ventas.
"""


class SalesSystemError(Exception):
    """Excepción base para todos los errores del sistema de ventas."""
    pass


class InvalidFormatError(SalesSystemError):
    """Lanzada cuando el formato de los datos es inválido o inesperado."""
    pass


class DataValidationError(SalesSystemError):
    """Lanzada cuando los datos no superan las comprobaciones de validación."""
    pass


class FileProcessingError(SalesSystemError):
    """Lanzada cuando fallan las operaciones de lectura/escritura de archivos."""
    pass


class UserNotFoundError(SalesSystemError):
    """Lanzada cuando un usuario solicitado no tiene datos de ventas."""
    pass
