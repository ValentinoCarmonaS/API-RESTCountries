"""
Sales System - Refactored modular sales analysis system.

This package provides tools for loading, analyzing, and reporting on sales data.
"""

__version__ = "2.0.0"
__author__ = "Your Name"

from data_loader import DataLoader
from sales_analyzer import SalesAnalyzer
from report_generator import ReportGenerator
from exceptions import (
    SalesSystemError,
    InvalidFormatError,
    DataValidationError,
    FileProcessingError,
    UserNotFoundError
)

__all__ = [
    'DataLoader',
    'SalesAnalyzer',
    'ReportGenerator',
    'SalesSystemError',
    'InvalidFormatError',
    'DataValidationError',
    'FileProcessingError',
    'UserNotFoundError',
]