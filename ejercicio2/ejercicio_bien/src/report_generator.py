"""
Módulo de generación de informes para el sistema de ventas.

Este módulo se encarga de crear y escribir informes en varios formatos
(JSON, CSV) con un manejo de errores y logging adecuados.
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Genera informes de ventas en múltiples formatos.
    
    Soporta:
        - JSON: Informes jerárquicos estructurados
        - CSV: Informes tabulares planos
    """
    
    def __init__(self, output_format: str = 'json'):
        """
        Inicializa el generador de informes.
        
        Args:
            output_format: Formato de salida predeterminado ('json' o 'csv')
        """
        self.output_format = output_format.lower()
        self.reports_generated = 0
        
        if self.output_format not in ['json', 'csv']:
            logger.warning(
                f"Formato de salida inválido '{output_format}', se usará 'json' por defecto"
            )
            self.output_format = 'json'
    
    def generate(
        self, 
        report_data: Dict[str, Any], 
        output_dir: str, 
        filename: Optional[str] = None,
        output_format: Optional[str] = None
    ) -> str:
        """
        Genera un archivo de informe.
        
        Args:
            report_data: Diccionario que contiene los datos del informe
            output_dir: Directorio para guardar el informe
            filename: Nombre de archivo personalizado opcional (sin extensión)
            output_format: Formato de salida opcional ('json' o 'csv')
            
        Returns:
            Ruta al archivo de informe generado
            
        Raises:
            FileProcessingError: Si no se puede escribir el informe
        """
        fmt = output_format or self.output_format
        
        # Crear directorio de salida si no existe
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileProcessingError(f"No se puede crear el directorio de salida: {e}")
        
        # Generar nombre de archivo si no se proporciona
        if filename is None:
            user_id = report_data.get('user_id', 'desconocido')
            filename = f"informe_ventas_{user_id}"
        
        # Añadir extensión
        filename_with_ext = f"{filename}.{fmt}"
        filepath = output_path / filename_with_ext
        
        # Generar informe según el formato
        try:
            if fmt == 'json':
                self._generate_json(report_data, filepath)
            elif fmt == 'csv':
                self._generate_csv(report_data, filepath)
            else:
                raise FileProcessingError(f"Formato no soportado: {fmt}")
            
            self.reports_generated += 1
            logger.info(f"Informe generado: {filepath}")
            
            return str(filepath)
            
        except IOError as e:
            raise FileProcessingError(
                f"Fallo al escribir el informe en {filepath}: {e}"
            )
    
    def _generate_json(self, report_data: Dict[str, Any], filepath: Path):
        """
        Genera un informe en formato JSON.
        
        Args:
            report_data: Diccionario de datos del informe
            filepath: Ruta al archivo de salida
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def _generate_csv(self, report_data: Dict[str, Any], filepath: Path):
        """
        Genera un informe en formato CSV.
        
        Aplana la estructura jerárquica del informe a un formato tabular.
        
        Args:
            report_data: Diccionario de datos del informe
            filepath: Ruta al archivo de salida
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir encabezado
            writer.writerow([
                'Tipo de Periodo',
                'Periodo',
                'Ventas Totales',
                'Venta Promedio',
                'Número de Ventas',
                'Cantidad Total',
                'Precio Promedio'
            ])
            
            # Escribir datos mensuales
            if 'monthly' in report_data:
                for period, data in sorted(report_data['monthly'].items()):
                    writer.writerow([
                        'Mensual',
                        period,
                        f"{data.get('total', 0):.2f}",
                        f"{data.get('average', 0):.2f}",
                        data.get('count', 0),
                        data.get('total_quantity', 0),
                        f"{data.get('avg_price', 0):.2f}"
                    ])
            
            # Escribir datos anuales
            if 'yearly' in report_data:
                for period, data in sorted(report_data['yearly'].items()):
                    writer.writerow([
                        'Anual',
                        period,
                        f"{data.get('total', 0):.2f}",
                        f"{data.get('average', 0):.2f}",
                        data.get('count', 0),
                        data.get('total_quantity', 0),
                        f"{data.get('avg_price', 0):.2f}"
                    ])
            
            # Escribir fila de resumen
            writer.writerow([])  # Fila en blanco
            writer.writerow([
                'Resumen',
                'Total',
                f"{report_data.get('total_revenue', 0):.2f}",
                '',
                report_data.get('total_sales', 0),
                '',
                ''
            ])
    
    def generate_batch(
        self,
        reports: List[Dict[str, Any]],
        output_dir: str,
        output_format: Optional[str] = None
    ) -> List[str]:
        """
        Genera múltiples informes en lote.
        
        Args:
            reports: Lista de diccionarios de datos de informes
            output_dir: Directorio para guardar los informes
            output_format: Formato de salida opcional
            
        Returns:
            Lista de rutas de archivos generados
        """
        generated_files = []
        errors = 0
        
        for report in reports:
            try:
                filepath = self.generate(report, output_dir, output_format=output_format)
                generated_files.append(filepath)
            except FileProcessingError as e:
                logger.error(f"Fallo al generar el informe: {e}")
                errors += 1
        
        logger.info(
            f"Lote completo: {len(generated_files)} informes generados, "
            f"{errors} errores"
        )
        
        return generated_files
    
    def generate_summary_report(
        self,
        summary_data: Dict[str, Any],
        output_dir: str,
        filename: str = 'summary'
    ) -> str:
        """
        Genera un informe de resumen con estadísticas generales.
        
        Args:
            summary_data: Diccionario que contiene estadísticas de resumen
            output_dir: Directorio para guardar el informe
            filename: Nombre para el archivo de resumen
            
        Returns:
            Ruta al archivo de resumen generado
        """
        return self.generate(
            summary_data,
            output_dir,
            filename=filename,
            output_format='json'
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Obtiene las estadísticas de generación.
        
        Returns:
            Diccionario con estadísticas de generación
        """
        return {
            'reports_generated': self.reports_generated
        }