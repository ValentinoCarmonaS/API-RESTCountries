# reporting.py
import json
import csv
from datetime import datetime
from abc import ABC, abstractmethod
import os
import pandas as pd
from pandas import DataFrame
from typing import Dict, Any, Optional, List
import logging

log = logging.getLogger(__name__)

# --- Clases de Cálculo de Reporte (Responsabilidad Única Aplicada) ---

class ReportCalculator:
    """
    Orquesta el cálculo de reportes de ventas. 
    Se enfoca en el flujo: Preparar -> Filtrar -> Agregar.
    """
    def calculate_for_user(self, sales_df: DataFrame, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Calcula reportes de ventas mensuales y anuales para un usuario.
        Devuelve None si el DataFrame está vacío o no hay ventas para el usuario.
        """
        if sales_df.empty:
            return None

        # 1. Preparación y enriquecimiento de datos
        processed_df = self._process_and_enrich_data(sales_df.copy())
        
        # 2. Filtrado por usuario
        user_sales = processed_df[processed_df['user_id'] == user_id].copy()
        if user_sales.empty:
            return None # Devolvemos None, ya que 'ReportCalculator' no encontró datos.

        # 3. Agregación de datos
        return self._create_user_report_data(user_sales, user_id)

    def _process_and_enrich_data(self, df: DataFrame) -> DataFrame:
        """
        Función orquestadora que limpia tipos y añade columnas de cálculo.
        Mezcla de niveles de abstracción es aceptable aquí como función de pipeline.
        """
        cleaned_df = self._clean_data_types(df)
        enriched_df = self._calculate_total_sale(cleaned_df)
        
        # Garantizar que no haya NaN en columnas críticas después de la limpieza
        rows_before = len(enriched_df)
        enriched_df.dropna(subset=['date', 'price', 'quantity', 'user_id'], inplace=True)
        
        if len(enriched_df) < rows_before:
            log.warning(f"Se descartaron {rows_before - len(enriched_df)} registros por datos inválidos después de la conversión de tipos.")
            
        return enriched_df

    def _clean_data_types(self, df: DataFrame) -> DataFrame:
        """Convierte las columnas relevantes a sus tipos de datos esperados (Limpieza)."""
        df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        return df

    def _calculate_total_sale(self, df: DataFrame) -> DataFrame:
        """Calcula la columna de venta total (Generación de Features)."""
        df['total_sale'] = df['price'] * df['quantity']
        return df

    def _create_user_report_data(self, user_sales: DataFrame, user_id: int) -> Dict[str, Any]:
        """Agrupa los resultados de las agregaciones en la estructura de reporte final."""
        return {
            'monthly': self._aggregate_monthly(user_sales),
            'yearly': self._aggregate_yearly(user_sales),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat()
        }

    def _aggregate_monthly(self, df: DataFrame) -> Dict[str, Any]:
        """Agrega ventas por mes y añade los ítems detallados (Cohesión mejorada)."""
        if df.empty:
            return {}
        
        # 1. Creación de la clave de periodo
        df['period'] = df['date'].dt.to_period('M').astype(str)
        
        # 2. Agregación numérica básica (SRP: Solo agregación)
        monthly_aggregation = df.groupby('period').agg(
            total=('total_sale', 'sum'),
            count=('total_sale', 'count')
        )
        monthly_aggregation['average'] = monthly_aggregation['total'] / monthly_aggregation['count']
        
        # 3. Obtención y unión de los detalles (Responsabilidad Separada)
        items_detail = self._extract_transaction_items_detail(df)
        monthly_aggregation = monthly_aggregation.join(items_detail)

        return monthly_aggregation.to_dict('index')

    def _extract_transaction_items_detail(self, df: DataFrame) -> DataFrame:
        """Extrae los detalles de la transacción y los agrupa en una lista por periodo."""
        # Se asegura de no modificar el DF original y usa solo las columnas de interés
        detail_cols = ['date', 'price', 'quantity', 'product', 'category', 'payment_method']
        
        # Filtrar columnas disponibles para evitar errores.
        cols_to_keep = [col for col in detail_cols if col in df.columns]
        df_detail = df[cols_to_keep].copy()
        
        # Formatear la fecha para la salida del reporte.
        df_detail['date'] = df_detail['date'].dt.strftime('%Y-%m-%d')

        def row_to_clean_dict(row: pd.Series) -> Dict[str, Any]:
            """Convierte una fila a dict, eliminando NaNs (Guardian Pattern para nulos)."""
            item_dict = row.to_dict()
            return {k: v for k, v in item_dict.items() if pd.notna(v)}

        # Crear la lista de diccionarios (items)
        items = df_detail.apply(row_to_clean_dict, axis=1).rename('items')
        
        # Agrupar la lista de items por el periodo ('period')
        return items.groupby(df['period']).apply(list)
        
    def _aggregate_yearly(self, df: DataFrame) -> Dict[str, Any]:
        """Agrega ventas por año."""
        if df.empty:
            return {}
            
        df['period'] = df['date'].dt.to_period('Y').astype(str)
        yearly_aggregation = df.groupby('period').agg(
            total=('total_sale', 'sum'),
            count=('total_sale', 'count')
        )
        yearly_aggregation['average'] = yearly_aggregation['total'] / yearly_aggregation['count']
        return yearly_aggregation.to_dict('index')


# --- Clases de Escritura de Reporte (Strategy Pattern) ---

class ReportWriter(ABC):
    """Interfaz para escritores de reportes."""
    @abstractmethod
    def write(self, report_data: Dict[str, Any], file_path: str):
        """Escribe los datos del reporte en la ruta especificada."""
        pass

class JsonReportWriter(ReportWriter):
    """Escribe un reporte en formato JSON."""
    def write(self, report_data: Dict[str, Any], file_path: str):
        # Se elimina la clave de preferencia 'preferences' ya que no se usa en JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

class CsvReportWriter(ReportWriter):
    """Escribe un reporte en formato CSV."""
    def write(self, report_data: Dict[str, Any], file_path: str):
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Nombres de encabezado más descriptivos y conscientes de la moneda
            writer.writerow(['Period', f'Total Sales', 'Average Sale', 'Number of Sales'])
            
            # Usar las claves refactorizadas
            for period_type in ['monthly', 'yearly']:
                # Protección (Guardian Pattern) por si el reporte no tiene ese periodo
                if period_type not in report_data:
                    continue 
                
                for period_name, data in sorted(report_data[period_type].items()):
                    writer.writerow([
                        period_name,
                        f"{data['total']:.2f}", # Formato de dos decimales para total
                        f"{data.get('average', 0):.2f}", # Formato de dos decimales para promedio
                        data['count']
                    ])

class ReportGenerator:
    """Orquesta la escritura de reportes usando el escritor apropiado (Factory)."""
    def __init__(self):
        self._writers: Dict[str, ReportWriter] = {
            'json': JsonReportWriter(),
            'csv': CsvReportWriter(),
        }

    def generate(self, report_data: Dict[str, Any], output_format: str, output_dir: str, preferences: Dict[str, str]) -> str:
        """Genera el reporte final basado en el formato de salida y las preferencias de usuario."""
        writer = self._writers.get(output_format.lower())

        if not writer:
            log.error(f"Formato de salida no soportado: {output_format}")
            raise ValueError(f"Formato de salida no soportado: {output_format}")

        user_id = report_data['user_id']
        filename = f"sales_report_{user_id}.{output_format.lower()}"
        filepath = os.path.join(output_dir, filename)
        
        # Garantizar que el directorio exista (Separación de Concerns: OS vs Writer)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise IOError(f"No se pudo crear el directorio de salida {output_dir}: {e}")
            
        writer.write(report_data, filepath)
        return filepath
