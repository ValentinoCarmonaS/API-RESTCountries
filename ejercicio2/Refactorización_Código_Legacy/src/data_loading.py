# data_loading.py
import os
from abc import ABC, abstractmethod
import pandas as pd
from pandas import DataFrame
from typing import Dict

class SalesDataReader(ABC):
    """Interfaz para lectores de datos de ventas (Strategy Pattern)."""
    @abstractmethod
    def read(self, file_path: str) -> DataFrame:
        """Lee datos del archivo y los devuelve como un DataFrame de Pandas."""
        pass

class JsonSalesReader(SalesDataReader):
    """Implementación para leer datos de ventas desde un archivo JSON."""
    def read(self, file_path: str) -> DataFrame:
        try:
            # Asumiendo un formato de registro (orient='records')
            return pd.read_json(file_path, orient='records')
        except ValueError as e:
            # Excepción más específica para el fallo de formato
            raise ValueError(f"Formato JSON inválido en {file_path}. Detalle: {e}")

class CsvSalesReader(SalesDataReader):
    """Implementación para leer datos de ventas desde un archivo CSV."""
    def read(self, file_path: str) -> DataFrame:
        # Los errores de lectura de archivos son manejados por la capa superior (DataLoader)
        return pd.read_csv(file_path)

class DataLoader:
    """Orquesta la carga de datos usando el lector apropiado (Simple Factory Pattern)."""
    def __init__(self):
        # Mapeo de extensiones a implementaciones de lector.
        self._readers: Dict[str, SalesDataReader] = {
            '.json': JsonSalesReader(),
            '.csv': CsvSalesReader(),
        }

    def load_from_file(self, file_path: str) -> DataFrame:
        """Determina el lector por extensión y realiza la lectura."""
        _, extension = os.path.splitext(file_path)
        reader = self._readers.get(extension.lower()) # Usar lower() para robustez

        if not reader:
            raise ValueError(f"Formato de archivo no soportado: {extension}")
            
        return reader.read(file_path)
