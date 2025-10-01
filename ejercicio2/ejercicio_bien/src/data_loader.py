"""
Módulo de carga de datos para el sistema de ventas.

Este módulo maneja la carga de datos de ventas desde varios formatos de archivo (JSON, CSV),
valida la estructura de los datos y devuelve DataFrames de pandas normalizados.
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from exceptions import InvalidFormatError, FileProcessingError
from utils import validate_sale_record, parse_number, parse_date, normalize_user_id

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Maneja la carga y validación de datos de ventas desde múltiples formatos de archivo.
    
    Formatos soportados:
        - JSON: Lista de registros de venta
        - CSV: Valores separados por comas con encabezados
    """
    
    def __init__(self):
        """Inicializa el DataLoader con seguimiento de estadísticas."""
        self.records_loaded = 0
        self.errors_found = 0
        self.files_processed = 0
    
    def load(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Carga datos de ventas desde múltiples archivos.
        
        Args:
            file_paths: Lista de rutas de archivos para cargar
            
        Returns:
            DataFrame de pandas con datos de ventas normalizados
            
        Raises:
            FileProcessingError: Si no se pudieron cargar datos válidos
        """
        all_records = []
        
        for file_path in file_paths:
            try:
                records = self._load_single_file(file_path)
                all_records.extend(records)
                self.files_processed += 1
                logger.info(f"Cargados {len(records)} registros de {file_path}")
            except Exception as e:
                logger.error(f"Fallo al cargar {file_path}: {e}")
                self.errors_found += 1
                # Continuar procesando otros archivos
        
        if not all_records:
            raise FileProcessingError("No se cargaron datos válidos de ningún archivo")
        
        self.records_loaded = len(all_records)
        logger.info(
            f"Total: {self.records_loaded} registros cargados de "
            f"{self.files_processed} archivos con {self.errors_found} errores"
        )
        
        # Convertir a DataFrame y normalizar
        df = pd.DataFrame(all_records)
        return self._normalize_dataframe(df)
    
    def _load_single_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Carga datos de un solo archivo según su extensión.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de diccionarios que contienen registros de venta
            
        Raises:
            FileProcessingError: Si el archivo no se puede leer
            InvalidFormatError: Si el formato del archivo es inválido
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileProcessingError(f"Archivo no encontrado: {file_path}")
        
        if path.suffix.lower() == '.json':
            return self._load_json(path)
        elif path.suffix.lower() == '.csv':
            return self._load_csv(path)
        else:
            raise InvalidFormatError(
                f"Formato de archivo no soportado: {path.suffix}. "
                "Formatos soportados: .json, .csv"
            )
    
    def _load_json(self, path: Path) -> List[Dict[str, Any]]:
        """Carga y valida un archivo JSON."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise InvalidFormatError(
                    f"El archivo JSON debe contener una lista de registros, "
                    f"se obtuvo {type(data).__name__}"
                )
            
            valid_records = []
            for i, record in enumerate(data):
                if isinstance(record, dict):
                    valid_records.append(record)
                else:
                    logger.warning(
                        f"Omitiendo registro inválido en el índice {i} en {path.name}: "
                        f"se esperaba un diccionario, se obtuvo {type(record).__name__}"
                    )
                    self.errors_found += 1
            
            return valid_records
            
        except json.JSONDecodeError as e:
            raise InvalidFormatError(f"JSON inválido en {path.name}: {e}")
        except IOError as e:
            raise FileProcessingError(f"No se puede leer el archivo {path.name}: {e}")
    
    def _load_csv(self, path: Path) -> List[Dict[str, Any]]:
        """Carga y valida un archivo CSV."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
            
            if not records:
                logger.warning(f"El archivo CSV {path.name} está vacío")
                return []
            
            return records
            
        except csv.Error as e:
            raise InvalidFormatError(f"CSV inválido en {path.name}: {e}")
        except IOError as e:
            raise FileProcessingError(f"No se puede leer el archivo {path.name}: {e}")
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza y valida las columnas del DataFrame."""
        self._validate_required_columns(df)
        
        df_normalized = df.copy()
        
        # Normalizar tipos
        df_normalized['user_id'] = df_normalized['user_id'].apply(normalize_user_id)
        df_normalized['date'] = self._parse_dates(df_normalized)
        df_normalized[['price', 'quantity']] = df_normalized[['price', 'quantity']].apply(
            pd.to_numeric, errors='coerce'
        )
        
        # Filtrar inválidos
        df_normalized = self._remove_invalid_records(df_normalized)
        
        # Agregar campos calculados
        df_normalized['total'] = df_normalized['price'] * df_normalized['quantity']
        df_normalized['year_month'] = df_normalized['date'].dt.to_period('M').astype(str)
        df_normalized['year'] = df_normalized['date'].dt.year.astype(str)
        
        logger.info(f"Se normalizaron {len(df_normalized)} registros válidos")
        return df_normalized

    def _parse_dates(self, df_normalized: pd.DataFrame) -> pd.Series:
        """Analiza y normaliza las fechas."""
        try:
            df_normalized['date'] = pd.to_datetime(
                df_normalized['date'], 
                format='%Y-%m-%d',
                errors='coerce'
            )

            return df_normalized['date']
        
        except Exception as e:
            logger.error(f"Error al analizar fechas: {e}")

    def _validate_required_columns(self, df: pd.DataFrame) -> None:
        """Valida que existan las columnas requeridas."""
        required = {'user_id', 'date', 'price', 'quantity'}
        missing = required - set(df.columns)
        if missing:
            raise InvalidFormatError(f"Faltan columnas requeridas: {missing}")

    def _remove_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina registros con datos inválidos."""
        invalid_mask = df['date'].isna() | df['price'].isna() | df['quantity'].isna()
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            logger.warning(
                f"Se encontraron {invalid_count} registros con datos inválidos"
            )
            self.errors_found += invalid_count
        
        return df[~invalid_mask].copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Obtiene las estadísticas de carga.
        
        Returns:
            Diccionario con estadísticas de carga
        """
        return {
            'records_loaded': self.records_loaded,
            'errors_found': self.errors_found,
            'files_processed': self.files_processed
        }