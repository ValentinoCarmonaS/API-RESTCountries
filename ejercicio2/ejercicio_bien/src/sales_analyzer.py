# SalesAnalyzer
# Responsabilidad: 
#   lógica de negocio: filtrar por usuario, agrupar por mes/año, calcular totales, promedios, detectar registros inválidos.
# Implementación eficiente: 
#   si usas pandas → (groupby + operaciones vectorizadas); 
#   si no → (usar itertools y collections pero evitar loops innecesarios).
# Métodos ejemplo:
#   analyze_for_user(df, user_id) -> dict (devuelve estructura con monthly/yearly totals, averages).
#   detect_bad_records(df) -> pd.DataFrame (registros con campos faltantes o tipos incorrectos).
# Posible optimización: cacheo con functools.lru_cache para resultados repetidos; o indexar DataFrame por user_id para consultas rápidas.

"""
Módulo de análisis de ventas para el sistema de ventas.

Este módulo proporciona un análisis eficiente de los datos de ventas utilizando pandas,
_incluyendo agregaciones por usuario, períodos de tiempo y cálculos estadísticos.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from functools import lru_cache
import pandas as pd

from exceptions import UserNotFoundError, DataValidationError
from utils import safe_divide

logger = logging.getLogger(__name__)


class SalesAnalyzer:
    """
    Analiza los datos de ventas y genera resúmenes estadísticos.
    
    Utiliza pandas para operaciones vectorizadas eficientes y soporta
    cacheo para consultas repetidas.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Inicializa el analizador con los datos de ventas.
        
        Args:
            data: DataFrame que contiene los datos de ventas normalizados
        """
        self.data = data
        self._validate_data()
        
        # Crear índice para búsquedas rápidas de usuarios
        self.data_indexed = self.data.set_index('user_id', drop=False)
        
        logger.info(f"SalesAnalyzer inicializado con {len(self.data)} registros")
    
    def _validate_data(self):
        """Valida que los datos tengan las columnas requeridas y los tipos adecuados."""
        required_columns = ['user_id', 'date', 'price', 'quantity', 'total']
        missing = set(required_columns) - set(self.data.columns)
        
        if missing:
            raise DataValidationError(
                f"Faltan columnas requeridas en los datos: {missing}"
            )
        
        if len(self.data) == 0:
            logger.warning("El analizador se inicializó con un conjunto de datos vacío")
    
    def analyze_user(self, user_id: Any) -> Dict[str, Any]:
        """
        Analiza las ventas de un usuario específico.
        
        Args:
            user_id: ID del usuario a analizar
            
        Returns:
            Diccionario que contiene agregaciones mensuales y anuales
            
        Raises:
            UserNotFoundError: Si el usuario no tiene datos de ventas
        """
        user_id_str = str(user_id)
        
        # Filtrar datos del usuario usando el DataFrame indexado para mayor eficiencia
        try:
            user_data = self.data_indexed.loc[user_id_str]
        except KeyError:
            raise UserNotFoundError(f"No se encontraron ventas para el usuario {user_id}")
        
        # Manejar el caso en que solo existe un registro (devuelve una Serie, no un DataFrame)
        if isinstance(user_data, pd.Series):
            user_data = user_data.to_frame().T
        
        logger.info(f"Analizando {len(user_data)} ventas para el usuario {user_id}")
        
        # Calcular agregaciones mensuales
        monthly_analysis = self._aggregate_by_period(user_data, 'year_month')
        
        # Calcular agregaciones anuales
        yearly_analysis = self._aggregate_by_period(user_data, 'year')
        
        return {
            'user_id': user_id_str,
            'monthly': monthly_analysis,
            'yearly': yearly_analysis,
            'generated_at': datetime.now().isoformat(),
            'total_sales': len(user_data),
            'total_revenue': float(user_data['total'].sum())
        }
    
    def _aggregate_by_period(
        self, 
        data: pd.DataFrame, 
        period_column: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrega los datos de ventas por período de tiempo.
        
        Args:
            data: DataFrame a agregar
            period_column: Nombre de la columna por la que agrupar ('year_month' o 'year')
            
        Returns:
            Diccionario con el período como clave y las estadísticas como valores
        """
        if len(data) == 0:
            return {}
        
        result = {}
        
        # Agrupar por período
        for period, group_df in data.groupby(period_column):
            period_data = {
                'total': float(group_df['total'].sum()),
                'count': int(len(group_df)),
            }
            
            # Añadir artículos solo para la agregación mensual (para coincidir con el comportamiento heredado)
            if period_column == 'year_month':
                # Convertir filas del DataFrame a lista de diccionarios (coincidiendo con el formato heredado)
                items = []
                for _, row in group_df.iterrows():
                    item = {
                        'user_id': row['user_id'],
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'price': float(row['price']),
                        'quantity': int(row['quantity'])
                    }
                    # Añadir campos opcionales si existen
                    for col in ['product', 'category', 'payment_method']:
                        if col in row and pd.notna(row[col]):
                            item[col] = row[col]
                    items.append(item)
                
                period_data['items'] = items
            
            # Calcular promedio
            if period_data['count'] > 0:
                period_data['average'] = period_data['total'] / period_data['count']
            else:
                period_data['average'] = 0
            
            result[period] = period_data
        
        return result
    
    def get_top_users(self, top_n: int = 10) -> pd.DataFrame:
        """
        Obtiene los mejores usuarios por ingresos totales de ventas.
        
        Args:
            top_n: Número de mejores usuarios a devolver
            
        Returns:
            DataFrame con los mejores usuarios y sus estadísticas
        """
        user_totals = self.data.groupby('user_id').agg({
            'total': 'sum',
            'quantity': 'sum',
            'user_id': 'count'  # Recuento de transacciones
        }).rename(columns={'user_id': 'transaction_count'})
        
        user_totals = user_totals.sort_values('total', ascending=False).head(top_n)
        
        logger.info(f"Se recuperaron los {len(user_totals)} mejores usuarios")
        
        return user_totals
    
    def get_period_summary(self, period: str = 'month') -> pd.DataFrame:
        """
        Obtiene estadísticas de resumen para todos los períodos.
        
        Args:
            period: 'month' o 'year'
            
        Returns:
            DataFrame con resúmenes de período
        """
        period_col = 'year_month' if period == 'month' else 'year'
        
        summary = self.data.groupby(period_col).agg({
            'total': ['sum', 'mean', 'count'],
            'user_id': 'nunique'  # Usuarios únicos por período
        })
        
        summary.columns = ['total_revenue', 'avg_sale', 'num_sales', 'unique_users']
        
        logger.info(f"Resumen de {period} generado para {len(summary)} períodos")
        
        return summary
    
    def detect_anomalies(self, threshold: float = 3.0) -> pd.DataFrame:
        """
        Detecta ventas anómalas (valores atípicos) utilizando la desviación estándar.
        
        Args:
            threshold: Número de desviaciones estándar desde la media
            
        Returns:
            DataFrame que contiene registros anómalos
        """
        mean_total = self.data['total'].mean()
        std_total = self.data['total'].std()
        
        # Encontrar ventas que están a más de 'threshold' desviaciones estándar de la media
        anomalies = self.data[
            abs(self.data['total'] - mean_total) > (threshold * std_total)
        ].copy()
        
        logger.info(
            f"Se detectaron {len(anomalies)} ventas anómalas "
            f"(umbral: {threshold} std dev)"
        )
        
        return anomalies
    
    def get_user_list(self) -> list:
        """
        Obtiene la lista de todos los ID de usuario únicos en el conjunto de datos.
        
        Returns:
            Lista ordenada de ID de usuario
        """
        return sorted(self.data['user_id'].unique().tolist())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas generales del conjunto de datos.
        
        Returns:
            Diccionario con estadísticas del conjunto de datos
        """
        return {
            'total_records': len(self.data),
            'unique_users': self.data['user_id'].nunique(),
            'date_range': {
                'start': self.data['date'].min().isoformat(),
                'end': self.data['date'].max().isoformat()
            },
            'total_revenue': float(self.data['total'].sum()),
            'avg_sale_value': float(self.data['total'].mean()),
            'total_quantity_sold': int(self.data['quantity'].sum())
        }