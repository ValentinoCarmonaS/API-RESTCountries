import os
import sys
import pytest
import pandas as pd
from unittest.mock import MagicMock, call
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Necesitamos importar SalesAnalyzer, que está en main.py (asumiendo que está disponible)
from sales_analyzer import SalesAnalyzer 
# Importamos excepciones para manejar posibles errores en mocks
from data_loading import DataLoader 

# --- 1. DATOS DE PRUEBA Y CONSTANTES ---

# DataFrames dummy para simular la salida del DataLoader
DUMMY_DF_1 = pd.DataFrame({'col': [1, 2]})
DUMMY_DF_2 = pd.DataFrame({'col': [3, 4]})
EXPECTED_MERGED_DF = pd.concat([DUMMY_DF_1, DUMMY_DF_2], ignore_index=True)

# Reportes dummy para simular la salida del ReportCalculator
DUMMY_REPORT_42 = {'user_id': 42, 'data': 'reporte_usuario_42'}
DUMMY_REPORT_101 = {'user_id': 101, 'data': 'reporte_usuario_101'}

# --- 2. FIXTURES DE PYTEST Y MOCKS ---

@pytest.fixture
def mock_data_loader():
    """Mock para simular el comportamiento de DataLoader."""
    loader = MagicMock(spec=DataLoader)
    # Configuramos el comportamiento por defecto de load_from_file para devolver DataFrames dummy
    loader.load_from_file.side_effect = [DUMMY_DF_1, DUMMY_DF_2]
    return loader

@pytest.fixture
def mock_report_calculator():
    """Mock para simular el comportamiento de ReportCalculator."""
    calculator = MagicMock()
    # Configuramos el comportamiento por defecto de calculate_for_user
    calculator.calculate_for_user.return_value = DUMMY_REPORT_42
    return calculator

@pytest.fixture
def mock_report_generator():
    """Mock para simular el comportamiento de ReportGenerator."""
    generator = MagicMock()
    return generator

@pytest.fixture
def analyzer(mock_data_loader, mock_report_calculator, mock_report_generator):
    """Fixture para inicializar SalesAnalyzer con mocks."""
    return SalesAnalyzer(mock_data_loader, mock_report_calculator, mock_report_generator)

# --- 3. PRUEBAS PARA SalesAnalyzer ---

class TestSalesAnalyzer:
    
    # --- Pruebas para load_data ---
    
    def test_load_data_successful_merge(self, analyzer, mock_data_loader):
        """Prueba la carga exitosa y la consolidación de múltiples DataFrames."""
        
        # Act
        analyzer.load_data('file1.json', 'file2.csv')
        
        # Assert - El loader debe ser llamado dos veces
        assert mock_data_loader.load_from_file.call_count == 2
        
        # Assert - El sales_df interno debe contener los datos combinados
        pd.testing.assert_frame_equal(analyzer.sales_df, EXPECTED_MERGED_DF)

    def test_load_data_with_loading_errors(self, analyzer, mock_data_loader, caplog):
        """Prueba que los errores de carga se manejen (loggeen) y la carga continúe."""
        # Configurar el mock para que falle la primera carga y tenga éxito la segunda
        mock_data_loader.load_from_file.side_effect = [ValueError("Mocked Load Error"), DUMMY_DF_2]
        
        # Act
        with caplog.at_level(logging.ERROR):
            analyzer.load_data('bad_file.json', 'good_file.csv')
        
        # Assert - El error debe haber sido loggeado
        assert 'Error crítico al cargar bad_file.json' in caplog.text
        
        # Assert - El DF debe contener solo los datos del archivo exitoso
        pd.testing.assert_frame_equal(analyzer.sales_df, DUMMY_DF_2.reset_index(drop=True))

    def test_load_data_no_files(self, analyzer):
        """Prueba que el DF interno permanezca vacío si no se proporcionan rutas."""
        analyzer.sales_df = pd.DataFrame() 
        analyzer.load_data()
        
        # Assert - El DF debe estar vacío
        assert analyzer.sales_df.empty

    # --- Pruebas para set_preferences ---
    
    def test_set_preferences_successful(self, analyzer):
        """Prueba la actualización de preferencias válidas."""
        
        # Act
        analyzer.set_preferences(currency='EUR', output_type='csv')
        
        # Assert
        assert analyzer.user_prefs['currency'] == 'EUR'
        assert analyzer.user_prefs['output_type'] == 'csv'
        
    def test_set_preferences_unknown_ignored(self, analyzer, caplog):
        """Prueba que las preferencias desconocidas sean ignoradas y loggeadas."""
        
        # Act
        with caplog.at_level(logging.WARNING):
            analyzer.set_preferences(unknown_key='invalid_value', currency='GBP')
            
        # Assert - La clave desconocida no debe estar en las preferencias
        assert 'unknown_key' not in analyzer.user_prefs
        
        # Assert - Debe haber un log de advertencia
        assert "Ignorando preferencia desconocida: unknown_key" in caplog.text

    # --- Pruebas para calculate_and_store_report ---
    
    def test_calculate_and_store_report_successful(self, analyzer, mock_report_calculator):
        """Prueba el cálculo exitoso y el almacenamiento de un reporte."""
        
        # Setup: Pre-poblamos el DF de ventas que usa el calculador
        analyzer.sales_df = EXPECTED_MERGED_DF.copy()
        
        # Act
        analyzer.calculate_and_store_report(42)
        
        # Assert - El calculador debe ser llamado con el DF interno y el ID
        mock_report_calculator.calculate_for_user.assert_called_once_with(
            analyzer.sales_df, 42
        )
        
        # Assert - El reporte debe estar almacenado
        assert 42 in analyzer.calculated_reports
        assert analyzer.calculated_reports[42] == DUMMY_REPORT_42

    def test_calculate_and_store_report_no_sales_found(self, analyzer, mock_report_calculator, caplog):
        """Prueba cuando el calculador no encuentra ventas (retorna None)."""
        
        # Setup: Configurar el mock para que retorne None
        mock_report_calculator.calculate_for_user.return_value = None
        
        # Act
        with caplog.at_level(logging.INFO):
            analyzer.calculate_and_store_report(99)
            
        # Assert - El reporte no debe estar almacenado
        assert 99 not in analyzer.calculated_reports
        
        # Assert - Debe haber un log de información
        assert "No se encontraron datos de ventas válidos para el usuario 99" in caplog.text

    # --- Pruebas para generate_reports ---
    
    def test_generate_reports_successful(self, analyzer, mock_report_generator):
        """Prueba la generación exitosa para un conjunto de usuarios con reportes almacenados."""
        
        # Setup: Almacenamos reportes pre-calculados y configuramos preferencias
        analyzer.calculated_reports = {
            42: DUMMY_REPORT_42,
            101: DUMMY_REPORT_101
        }
        analyzer.user_prefs['output_type'] = 'csv'
        
        OUTPUT_DIR = '/mock/reports'
        
        # Act
        analyzer.generate_reports(OUTPUT_DIR, users=[42, 101])
        
        # Assert - El generador debe ser llamado para cada usuario
        # CORRECCIÓN: Se ajusta a la llamada posicional que se registra en la práctica.
        expected_calls = [
            call(DUMMY_REPORT_42, 'csv', OUTPUT_DIR, analyzer.user_prefs),
            call(DUMMY_REPORT_101, 'csv', OUTPUT_DIR, analyzer.user_prefs),
        ]
        
        mock_report_generator.generate.assert_has_calls(expected_calls, any_order=True)
        assert mock_report_generator.generate.call_count == 2

    def test_generate_reports_skips_uncalculated(self, analyzer, mock_report_generator, caplog):
        """Prueba que el generador salte a los usuarios sin reportes calculados."""
        
        # Setup: Solo reportes para 42
        analyzer.calculated_reports = {
            42: DUMMY_REPORT_42,
        }
        
        OUTPUT_DIR = '/mock/reports'
        
        # Act
        with caplog.at_level(logging.WARNING):
            analyzer.generate_reports(OUTPUT_DIR, users=[42, 999])
            
        # Assert - El generador solo debe ser llamado una vez (para 42)
        mock_report_generator.generate.assert_called_once()
        
        # Assert - Debe haber un log de advertencia
        assert "Reporte para el usuario 999 no encontrado" in caplog.text

    def test_generate_reports_handles_generator_error(self, analyzer, mock_report_generator, caplog):
        """Prueba que se maneje un error lanzado por el ReportGenerator."""
        
        # Setup: Almacenamos reportes y configuramos el mock para fallar
        analyzer.calculated_reports = {
            42: DUMMY_REPORT_42,
        }
        mock_report_generator.generate.side_effect = ValueError("Mocked Generator Error")
        OUTPUT_DIR = '/mock/reports'

        # Act
        with caplog.at_level(logging.ERROR):
            analyzer.generate_reports(OUTPUT_DIR, users=[42])
            
        # Assert - El generador fue llamado
        mock_report_generator.generate.assert_called_once()
        
        # Assert - El error debe ser loggeado
        assert "Fallo crítico al escribir el reporte para el usuario 42" in caplog.text
