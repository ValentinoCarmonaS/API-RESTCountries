# sales_analyzer.py
import json
import logging
import pandas as pd
from pandas import DataFrame
from data_loading import DataLoader
from reporting import ReportCalculator, ReportGenerator
from typing import Dict, Any, Optional, List

# Configuración de logging (mantener al principio)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SalesAnalyzer:
    """
    Coordina la carga, procesamiento y generación de reportes de ventas.
    Utiliza inyección de dependencias para desacoplamiento (DIP).
    """
    DEFAULT_PREFS = {
        'currency': 'USD',
        'date_format': '%Y-%m-%d',
        'output_type': 'json'
    }

    def __init__(self, data_loader: DataLoader, report_calculator: ReportCalculator, report_generator: ReportGenerator):
        # Nomenclatura mejorada: prefijos privados claros.
        self._data_loader = data_loader
        self._report_calculator = report_calculator
        self._report_generator = report_generator
        
        self.sales_df: DataFrame = pd.DataFrame()
        self.calculated_reports: Dict[int, Dict[str, Any]] = {}
        self.user_prefs: Dict[str, str] = self.DEFAULT_PREFS.copy()

    def load_data(self, *file_paths: str):
        """
        Carga y consolida los datos de ventas de múltiples rutas de archivo.
        Separa la lógica de iteración de la lógica de carga unitaria.
        """
        loaded_dfs: List[DataFrame] = []
        for file_path in file_paths:
            df = self._safe_load_single_file(file_path)
            if df is not None:
                loaded_dfs.append(df)
        
        if loaded_dfs:
            # Concatenación de DataFrames cargados
            self.sales_df = pd.concat(loaded_dfs, ignore_index=True)

    def _safe_load_single_file(self, file_path: str) -> Optional[DataFrame]:
        """Extrae la responsabilidad del manejo de errores durante la carga de un solo archivo."""
        try:
            # Llamada al DataLoader inyectado
            new_df = self._data_loader.load_from_file(file_path)
            logging.info(f"Cargado exitosamente {file_path} con {len(new_df)} registros.")
            return new_df
        except (ValueError, IOError, json.JSONDecodeError) as e:
            # Manejo de errores específicos para una mejor información al usuario
            logging.error(f"Error crítico al cargar {file_path}: {type(e).__name__}: {str(e)}")
            return None # Devolver None en caso de fallo para continuar con otros archivos

    def calculate_and_store_report(self, user_id: int) -> bool:
        """
        Calcula y almacena el reporte para un usuario dado. 
        Nombre de función mejorado para reflejar sus efectos secundarios (almacenamiento).
        """
        report_data = self._report_calculator.calculate_for_user(self.sales_df, user_id)
        
        if report_data:
            self.calculated_reports[user_id] = report_data
            logging.info(f"Reporte calculado y almacenado para el usuario {user_id}.")
            return True
        else:
            logging.warning(f"No se encontraron datos de ventas válidos para el usuario {user_id}. Reporte omitido.")
            return False

    def generate_reports(self, output_dir: str, users: Optional[List[int]] = None):
        """Genera reportes para los usuarios especificados o para todos los calculados."""
        users_to_process = users if users is not None else self.calculated_reports.keys()

        if not users_to_process:
            logging.warning("No hay usuarios para procesar. Calcule reportes primero.")
            return

        for user_id in users_to_process:
            report_data = self.calculated_reports.get(user_id)
            if report_data is None:
                logging.warning(f"Reporte para el usuario {user_id} no encontrado. Omitiendo generación.")
                continue
            
            self._safe_generate_single_report(user_id, report_data, output_dir)

    def _safe_generate_single_report(self, user_id: int, report_data: Dict[str, Any], output_dir: str):
        """Extrae la responsabilidad del manejo de errores durante la generación del reporte."""
        try:
            # Pasa las preferencias completas, lo que hace al generador más configurable
            filepath = self._report_generator.generate(
                report_data,
                self.user_prefs['output_type'],
                output_dir,
                self.user_prefs
            )
            logging.info(f"Reporte generado exitosamente: {filepath}")
        except (ValueError, IOError) as e:
            logging.error(f"Fallo crítico al escribir el reporte para el usuario {user_id}. Detalle: {e}")

    def set_preferences(self, **prefs: str):
        """Permite establecer preferencias de usuario válidas."""
        for key, value in prefs.items():
            if key in self.user_prefs:
                # Se podría añadir validación de tipos aquí, pero se mantiene simple
                self.user_prefs[key] = value
                logging.debug(f"Preferencia '{key}' actualizada a '{value}'")
            else:
                logging.warning(f"Ignorando preferencia desconocida: {key}")


if __name__ == "__main__":
    import os

    # 1. Composición de la aplicación: se crean e inyectan las dependencias.
    loader = DataLoader()
    calculator = ReportCalculator()
    generator = ReportGenerator()
    system = SalesAnalyzer(loader, calculator, generator)
    
    # 2. Ejecución del ejemplo de uso.
    try:
        script_dir = os.path.dirname(__file__)

        project_root = os.path.dirname(script_dir) 
        output_directory = os.path.join(project_root, 'reports')

        # Se mantiene la misma interfaz pública
        system.load_data(
            os.path.join(script_dir, '../sales/sales.json'), 
            os.path.join(script_dir, '../sales/sales.csv')
        )
        system.set_preferences(output_type='json', currency='EUR')
        
        # Uso del nuevo nombre de función
        system.calculate_and_store_report(42)
        system.calculate_and_store_report(101)
        
        system.generate_reports(output_directory, users=[42, 101])
        
    except FileNotFoundError:
        logging.warning("sales.json y/o sales.csv no encontrados. Omitiendo ejecución de ejemplo.")
        logging.warning("Por favor, cree archivos dummy con esos nombres para ejecutar el ejemplo.")
    except Exception as e:
        # Captura de cualquier excepción no manejada en las capas inferiores
        logging.critical(f"Error no manejado en la ejecución principal: {e}")