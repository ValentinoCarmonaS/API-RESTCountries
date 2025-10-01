"""
Punto de entrada principal para el sistema de ventas refactorizado.

Este módulo demuestra el uso del sistema de ventas modular
y proporciona una interfaz de línea de comandos para operaciones comunes.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from data_loader import DataLoader
from sales_analyzer import SalesAnalyzer
from report_generator import ReportGenerator
from exceptions import SalesSystemError


def setup_logging(level: str = 'INFO') -> None:
    """
    Configura el logging para la aplicación.
    
    Args:
        level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


class SalesSystem:
    """
    Orquestador principal del sistema de ventas. 
    
    Coordina la carga de datos, el análisis y la generación de informes con
    manejo de errores y logging adecuados.
    """
    
    def __init__(self, output_format: str = 'json', log_level: str = 'INFO'):
        """
        Inicializa el sistema de ventas. 
        
        Args:
            output_format: Formato predeterminado para los informes ('json' o 'csv')
            log_level: Nivel de logging
        """
        setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        self.data_loader = DataLoader()
        self.analyzer = None
        self.report_generator = ReportGenerator(output_format)
        
        self.logger.info("Sistema de ventas inicializado")
    
    def load_data(self, file_paths: List[str]) -> bool:
        """
        Carga datos de ventas desde archivos.
        
        Args:
            file_paths: Lista de rutas de archivos para cargar
            
        Returns:
            True si los datos se cargaron correctamente, False en caso contrario
        """
        try:
            self.logger.info(f"Cargando datos de {len(file_paths)} archivo(s)")
            df = self.data_loader.load(file_paths)
            
            self.analyzer = SalesAnalyzer(df)
            
            stats = self.data_loader.get_statistics()
            self.logger.info(
                f"Datos cargados correctamente: {stats['records_loaded']} registros, "
                f"{stats['errors_found']} errores"
            )
            
            return True
            
        except SalesSystemError as e:
            self.logger.error(f"Fallo al cargar datos: {e}")
            return False
    
    def analyze_user(self, user_id: str) -> Optional[dict]:
        """
        Analiza las ventas de un usuario específico.
        
        Args:
            user_id: ID del usuario a analizar
            
        Returns:
            Resultados del análisis o None si falló
        """
        if self.analyzer is None:
            self.logger.error("No hay datos cargados. Llama a load_data() primero.")
            return None
        
        try:
            return self.analyzer.analyze_user(user_id)
        except SalesSystemError as e:
            self.logger.error(f"El análisis falló para el usuario {user_id}: {e}")
            return None
    
    def generate_user_report(
        self, 
        user_id: str, 
        output_dir: str,
        output_format: Optional[str] = None
    ) -> Optional[str]:
        """
        Genera un informe para un usuario específico.
        
        Args:
            user_id: ID del usuario para generar el informe
            output_dir: Directorio para guardar el informe
            output_format: Formato de salida opcional
            
        Returns:
            Ruta al informe generado o None si falló
        """
        analysis = self.analyze_user(user_id)
        if analysis is None:
            return None
        
        try:
            filepath = self.report_generator.generate(
                analysis,
                output_dir,
                output_format=output_format
            )
            self.logger.info(f"Informe generado: {filepath}")
            return filepath
            
        except SalesSystemError as e:
            self.logger.error(f"Fallo al generar el informe: {e}")
            return None
    
    def generate_batch_reports(
        self,
        user_ids: List[str],
        output_dir: str,
        output_format: Optional[str] = None
    ) -> List[str]:
        """
        Genera informes para múltiples usuarios.
        
        Args:
            user_ids: Lista de IDs de usuarios
            output_dir: Directorio para guardar los informes
            output_format: Formato de salida opcional
            
        Returns:
            Lista de rutas de archivos generados
        """
        if self.analyzer is None:
            self.logger.error("No hay datos cargados. Llama a load_data() primero.")
            return []
        
        self.logger.info(f"Generando informes para {len(user_ids)} usuarios")
        
        generated_files = []
        for user_id in user_ids:
            filepath = self.generate_user_report(user_id, output_dir, output_format)
            if filepath:
                generated_files.append(filepath)
        
        return generated_files
    
    def generate_summary(self, output_dir: str) -> Optional[str]:
        """
        Genera un informe de resumen general.
        
        Args:
            output_dir: Directorio para guardar el resumen
            
        Returns:
            Ruta al resumen generado o None si falló
        """
        if self.analyzer is None:
            self.logger.error("No hay datos cargados. Llama a load_data() primero.")
            return None
        
        try:
            stats = self.analyzer.get_statistics()
            return self.report_generator.generate_summary_report(
                stats,
                output_dir
            )
        except SalesSystemError as e:
            self.logger.error(f"Fallo al generar el resumen: {e}")
            return None


def main():
    """Ejemplo de uso del sistema refactorizado."""
    
    # Inicializar sistema
    system = SalesSystem(output_format='json', log_level='INFO')
    
    # Determinar directorio de datos (relativo a este archivo)
    current_dir = Path(__file__).parent.parent
    
    # Cargar datos de archivos de ejemplo
    data_files = [
        str('./sales.json'),
        str('./sales.csv')
    ]
    
    system.load_data(data_files)
    
    # Generar informes para usuarios específicos
    users_to_process = ['42', '101']
    output_directory = str(current_dir / 'reports')
        
    system.generate_batch_reports(
        users_to_process,
        output_directory
    )
    
    # Generar resumen general
    system.generate_summary(output_directory)


if __name__ == "__main__":
    main()
