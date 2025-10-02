import sys
import pytest
import os
import json
import csv
import pandas as pd
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importamos las clases a probar desde reporting.py
from reporting import ReportCalculator, ReportGenerator, JsonReportWriter, CsvReportWriter

# --- 1. DATOS DE PRUEBA Y CONSTANTES ---

# DataFrame de ventas limpio y listo para ser procesado.
# Simula la salida de la función _process_and_enrich_data de ReportCalculator.
TEST_SALES_DATA: List[Dict[str, Any]] = [
    # Usuario 42: Enero 2025, Febrero 2025
    {'user_id': 42, 'date': pd.Timestamp('2025-01-10'), 'price': 100.0, 'quantity': 2, 'category': 'A', 'total_sale': 200.0, 'year': 2025, 'month': 1, 'month_name': '2025-01'},
    {'user_id': 42, 'date': pd.Timestamp('2025-01-15'), 'price': 50.0, 'quantity': 1, 'category': 'B', 'total_sale': 50.0, 'year': 2025, 'month': 1, 'month_name': '2025-01'},
    {'user_id': 42, 'date': pd.Timestamp('2025-02-01'), 'price': 150.0, 'quantity': 3, 'category': 'A', 'total_sale': 450.0, 'year': 2025, 'month': 2, 'month_name': '2025-02'},
    
    # Usuario 101: Febrero 2025
    {'user_id': 101, 'date': pd.Timestamp('2025-02-20'), 'price': 200.0, 'quantity': 1, 'category': 'C', 'total_sale': 200.0, 'year': 2025, 'month': 2, 'month_name': '2025-02'},
]

# DataFrame base con los tipos correctos
TEST_DF = pd.DataFrame(TEST_SALES_DATA)

# Diccionario de reporte esperado para el Usuario 42 (Base para comparación)
EXPECTED_REPORT_42: Dict[str, Any] = {
    'user_id': 42,
    'monthly': {
        '2025-01': {'total': 250.0, 'count': 2, 'average': 125.0},
        '2025-02': {'total': 450.0, 'count': 1, 'average': 450.0},
    },
    'yearly': {
        '2025': {'total': 700.0, 'count': 3, 'average': 233.33333333333334},
    }
    # Nota: 'generated_at' se ignora en la prueba ya que varía.
}

# Diccionario de reporte esperado para el Usuario 101 (Base para comparación)
EXPECTED_REPORT_101: Dict[str, Any] = {
    'user_id': 101,
    'monthly': {
        '2025-02': {'total': 200.0, 'count': 1, 'average': 200.0},
    },
    'yearly': {
        '2025': {'total': 200.0, 'count': 1, 'average': 200.0},
    }
}

# Datos de reporte base para la prueba de ReportGenerator
GENERATOR_REPORT_DATA = {
    'user_id': 99,
    'generated_at': '2025-01-01T10:00:00',
    'monthly': {
        '2025-01': {'total': 1500.5, 'count': 5, 'average': 300.1},
    },
    'yearly': {
        '2025': {'total': 1500.5, 'count': 5, 'average': 300.1},
    }
}

# --- 2. FIXTURES DE PYTEST ---

@pytest.fixture
def calculator():
    """Retorna una instancia de ReportCalculator."""
    return ReportCalculator()

@pytest.fixture
def generator():
    """Retorna una instancia de ReportGenerator."""
    return ReportGenerator()

# --- 3. PRUEBAS PARA REPORTCALCULATOR ---

class TestReportCalculator:
    """Pruebas unitarias para ReportCalculator."""
    
    def test_calculate_for_user_42(self, calculator):
        """Prueba el cálculo de reportes para un usuario con datos."""
        report = calculator.calculate_for_user(TEST_DF, 42)
        
        # 1. Verificar que el reporte no sea None
        assert report is not None
        
        # 2. Verificar datos de usuario
        assert report['user_id'] == EXPECTED_REPORT_42['user_id']
        assert 'generated_at' in report
        
        # 3. Verificar agregación mensual (usamos assert_almost_equal para flotantes)
        assert len(report['monthly']) == 2
        
        m_jan = report['monthly']['2025-01']
        assert m_jan['total'] == pytest.approx(250.0)
        assert m_jan['count'] == 2
        assert m_jan['average'] == pytest.approx(125.0)

        m_feb = report['monthly']['2025-02']
        assert m_feb['total'] == pytest.approx(450.0)
        assert m_feb['count'] == 1
        assert m_feb['average'] == pytest.approx(450.0)
        
        # 4. Verificar agregación anual
        y_2025 = report['yearly']['2025']
        assert y_2025['total'] == pytest.approx(700.0)
        assert y_2025['count'] == 3
        assert y_2025['average'] == pytest.approx(233.33333333333334)

    def test_calculate_for_user_101(self, calculator):
        """Prueba el cálculo de reportes para otro usuario."""
        report = calculator.calculate_for_user(TEST_DF, 101)
        
        assert report is not None
        assert report['user_id'] == EXPECTED_REPORT_101['user_id']
        assert report['yearly']['2025']['total'] == pytest.approx(200.0)
        
    def test_calculate_no_sales_for_user(self, calculator):
        """Prueba que devuelve None cuando el usuario no tiene ventas."""
        report = calculator.calculate_for_user(TEST_DF, 999)
        assert report is None

    def test_calculate_empty_sales_df(self, calculator):
        """Prueba que devuelve None cuando el DataFrame inicial está vacío."""
        empty_df = pd.DataFrame(columns=TEST_DF.columns)
        report = calculator.calculate_for_user(empty_df, 42)
        assert report is None

    def test_prepare_dataframe_cleans_types(self, calculator):
        """Prueba que la función de preparación de datos convierte tipos correctamente."""
        # Datos con strings que deben ser convertidos
        raw_data = pd.DataFrame([{
            'user_id': '42',
            'date': '2025-01-01',
            'price': '10.00',
            'quantity': '1',
            'product': 'Test',
            'category': 'Test',
        }])
        
        processed_df = calculator._process_and_enrich_data(raw_data)
        
        # 1. Verificar tipos
        assert processed_df['user_id'].dtype == 'int64'
        assert processed_df['price'].dtype == 'float64'
        assert processed_df['quantity'].dtype == 'int64'
        assert processed_df['date'].dtype == 'datetime64[ns]'
        
        # 2. Verificar columna calculada
        assert processed_df['total_sale'].iloc[0] == 10.0

    def test_prepare_dataframe_handles_bad_data(self, calculator):
        """Prueba que el preparador maneje datos no numéricos (NaN/NaT)."""
        raw_data = pd.DataFrame([{
            'user_id': 'bad_id',
            'date': 'bad_date',
            'price': 'bad_price',
            'quantity': 'bad_qty',
        }])
        
        processed_df = calculator._process_and_enrich_data(raw_data)
        
        # pd.to_numeric con errors='coerce' convierte fallos a NaN
        assert processed_df['user_id'].isna().all()
        assert processed_df['price'].isna().all()
        assert processed_df['quantity'].isna().all()
        # pd.to_datetime con errors='coerce' convierte fallos a NaT (Not a Time)
        assert processed_df['date'].isnull().all()


# --- 4. PRUEBAS PARA REPORTGENERATOR y WRITERS ---

class TestReportGeneratorAndWriters:
    """Pruebas unitarias para ReportGenerator, JsonReportWriter y CsvReportWriter."""

    def test_generator_unsupported_format(self, generator, tmp_path):
        """Prueba que ReportGenerator levante ValueError para formatos no soportados."""
        output_dir = str(tmp_path / "reports")
        
        with pytest.raises(ValueError, match="Formato de salida no soportado"):
            generator.generate(GENERATOR_REPORT_DATA, 'xml', output_dir, preferences={})

    def test_generator_json_successful(self, generator, tmp_path):
        """Prueba la generación exitosa de un reporte JSON."""
        output_dir = str(tmp_path / "reports")
        user_id = GENERATOR_REPORT_DATA['user_id']
        output_format = 'json'
        
        # Generar el reporte
        filepath = generator.generate(GENERATOR_REPORT_DATA, output_format, output_dir, preferences={})
        
        # 1. Verificar la ruta y existencia del archivo
        expected_filepath = os.path.join(output_dir, f"sales_report_{user_id}.{output_format}")
        assert filepath == expected_filepath
        assert os.path.exists(filepath)
        
        # 2. Verificar el contenido del archivo JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # El reporte escrito debe coincidir con el reporte original
        assert data['user_id'] == user_id
        assert data['monthly']['2025-01']['total'] == 1500.5
        assert 'generated_at' in data # Se asegura que el timestamp se incluyó

    def test_generator_csv_successful(self, generator, tmp_path):
        """Prueba la generación exitosa de un reporte CSV."""
        output_dir = str(tmp_path / "reports")
        user_id = GENERATOR_REPORT_DATA['user_id']
        output_format = 'csv'
        
        # Generar el reporte
        filepath = generator.generate(GENERATOR_REPORT_DATA, output_format, output_dir, preferences={})
        
        # 1. Verificar la ruta y existencia del archivo
        expected_filepath = os.path.join(output_dir, f"sales_report_{user_id}.{output_format}")
        assert filepath == expected_filepath
        assert os.path.exists(filepath)
        
        # 2. Verificar el contenido del archivo CSV (lectura línea por línea)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        # Encabezado: Period, Total Sales, Average Sale, Number of Sales
        assert rows[0] == ['Period', 'Total Sales', 'Average Sale', 'Number of Sales']
        
        # Fila mensual: '2025-01'
        assert rows[1] == ['2025-01', '1500.50', '300.10', '5']
        
        # Fila anual: '2025'
        assert rows[2] == ['2025', '1500.50', '300.10', '5']

    def test_generator_creates_output_dir(self, generator, tmp_path):
        """Prueba que el ReportGenerator cree el directorio de salida si no existe."""
        
        non_existent_dir = str(tmp_path / "new_reports" / "sub_dir")
        
        # El directorio no debe existir antes de la llamada
        assert not os.path.exists(non_existent_dir)
        
        # Generar el reporte
        generator.generate(GENERATOR_REPORT_DATA, 'json', non_existent_dir, preferences={})
        
        # Verificar que el directorio y subdirectorio se hayan creado
        assert os.path.isdir(non_existent_dir)

    def test_csv_writer_zero_average_format(self, tmp_path):
        """Prueba que el CSV Writer formatee el promedio a 0.00 cuando no hay ventas (count=0)."""
        writer = CsvReportWriter()
        output_dir = str(tmp_path / "test")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "zero.csv")
        
        zero_report = {
            'user_id': 1,
            'monthly': {'2025-01': {'total': 0.0, 'count': 0}},
            'yearly': {'2025': {'total': 0.0, 'count': 0}}
        }
        
        writer.write(zero_report, filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        # La línea debe mostrar '0.00' para Total Sales y Average Sale.
        # Fila mensual: '2025-01'
        assert rows[1] == ['2025-01', '0.00', '0.00', '0'] 
        # Fila anual: '2025'
        assert rows[2] == ['2025', '0.00', '0.00', '0']
