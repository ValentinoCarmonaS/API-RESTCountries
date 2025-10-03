import sys
import pytest
import os
import json
import csv
import pandas as pd
from pandas.testing import assert_frame_equal
from typing import List, Dict, Any, Callable

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importamos las clases a probar desde data_loading.py
from data_loading import DataLoader, JsonSalesReader, CsvSalesReader, SalesDataReader

# Definimos datos de prueba estándar que cumplen con el esquema esperado
TEST_DATA: List[Dict[str, Any]] = [
    {'user_id': 1, 'date': '2025-01-01', 'price': 100.5, 'quantity': 2, 'product': 'A', 'category': 'Tech'},
    {'user_id': 2, 'date': '2025-01-02', 'price': 50.0, 'quantity': 1, 'product': 'B', 'category': 'Books'},
]
EXPECTED_COLUMNS: List[str] = ['user_id', 'date', 'price', 'quantity', 'product', 'category']

# --- DEFINICIÓN DE DATAFRAME ESPERADO Y CORRECCIÓN DE TIPO ---
# Creamos el DataFrame y forzamos el tipo datetime64[ns] en la columna 'date' para que coincida 
# con el comportamiento de pd.read_json.
EXPECTED_DF_VALID = pd.DataFrame(TEST_DATA, columns=EXPECTED_COLUMNS)

EXPECTED_DF_VALID_JSON = EXPECTED_DF_VALID.copy()
EXPECTED_DF_VALID_JSON['date'] = pd.to_datetime(EXPECTED_DF_VALID_JSON['date']).dt.normalize()

EXPECTED_DF_VALID_CSV = EXPECTED_DF_VALID.copy()

# -----------------------------------------------------------

# --- Fixtures para Manejo de Archivos Temporales (Pytest) ---

@pytest.fixture
def create_temp_json(tmp_path: os.PathLike) -> Callable[[List[Dict[str, Any]]], os.PathLike]:
    """Fixture que devuelve una función para crear un archivo JSON temporal."""
    def _creator(data):
        file_path = tmp_path / "temp_data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            # Si data no es una lista/dict, json.dump fallará, lo cual está bien para simular JSON inválido.
            json.dump(data, f) 
        return str(file_path)
    return _creator

@pytest.fixture
def create_temp_csv(tmp_path: os.PathLike) -> Callable[[List[Dict[str, Any]]], os.PathLike]:
    """Fixture que devuelve una función para crear un archivo CSV temporal."""
    def _creator(data):
        file_path = tmp_path / "temp_data.csv"
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS)
            writer.writeheader()
            writer.writerows(data)
        return str(file_path)
    return _creator

# --- Pruebas para las Estrategias (Readers) ---

def test_json_reader_successful(create_temp_json):
    """Prueba la lectura exitosa de datos JSON válidos (Verifica la corrección de tipo)."""
    temp_file = create_temp_json(TEST_DATA)
    reader = JsonSalesReader()
    actual_df = reader.read(temp_file)
    assert_frame_equal(EXPECTED_DF_VALID_JSON, actual_df)

def test_csv_reader_successful(create_temp_csv):
    """Prueba la lectura exitosa de datos CSV válidos."""
    temp_file = create_temp_csv(TEST_DATA)
    reader = CsvSalesReader()
    actual_df = reader.read(temp_file)
    
    # Usamos check_dtype=False porque pd.read_csv no realiza la conversión automática de fecha 
    # como lo hace pd.read_json, y la columna 'date' será de tipo 'object' (string), lo cual 
    # es consistente con la capa de lectura.
    assert_frame_equal(EXPECTED_DF_VALID_CSV, actual_df, check_dtype=False)

def test_json_reader_invalid_content(create_temp_json):
    """Prueba que el lector JSON levante ValueError con contenido inválido (no es una lista de registros)."""
    # Intentamos crear un JSON inválido (un string simple en lugar de una lista de registros)
    temp_file = create_temp_json("Esto no es una lista de registros") 
    reader = JsonSalesReader()
    
    with pytest.raises(ValueError) as excinfo:
        reader.read(temp_file)
    # Verificamos que el mensaje incluya la frase de formato inválido o el detalle de Pandas/JSON
    assert "Formato JSON inválido" in str(excinfo.value) or "expected object or array" in str(excinfo.value)

def test_json_reader_empty_file(create_temp_json):
    """Prueba que el lector JSON devuelva un DF vacío para un archivo con lista vacía."""
    temp_file = create_temp_json([])
    reader = JsonSalesReader()
    actual_df = reader.read(temp_file)
    
    # Creamos un DF vacío esperado con las columnas definidas
    expected_empty_df = pd.DataFrame()
    
    # check_names=False y check_dtype=False para la robustez con DFs vacíos.
    assert_frame_equal(expected_empty_df, actual_df, check_names=False, check_dtype=False) 

def test_csv_reader_empty_file(tmp_path):
    """Prueba que el lector CSV devuelva un DF vacío para un archivo con solo encabezados."""
    file_path = tmp_path / "empty.csv"
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader() # Solo escribimos el encabezado
        
    reader = CsvSalesReader()
    actual_df = reader.read(str(file_path))
    
    # Creamos un DF vacío esperado con las columnas definidas
    expected_empty_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    
    assert_frame_equal(expected_empty_df, actual_df, check_dtype=False)

# --- Pruebas para el Orquestador (DataLoader) ---

@pytest.fixture
def data_loader():
    """Fixture para inicializar el DataLoader."""
    return DataLoader()

def test_data_loader_load_from_json(data_loader, create_temp_json):
    """Prueba que DataLoader seleccione el lector JSON y cargue correctamente."""
    temp_file = create_temp_json(TEST_DATA)
    actual_df = data_loader.load_from_file(temp_file)
    assert_frame_equal(EXPECTED_DF_VALID_JSON, actual_df)

def test_data_loader_load_from_csv(data_loader, create_temp_csv):
    """Prueba que DataLoader seleccione el lector CSV y cargue correctamente."""
    temp_file = create_temp_csv(TEST_DATA)
    actual_df = data_loader.load_from_file(temp_file)
    # Requerimos check_dtype=False ya que la capa de lectura CSV no convierte la fecha.
    assert_frame_equal(EXPECTED_DF_VALID_CSV.astype(object), actual_df.astype(object), check_dtype=False)

# --- Casos Borde: Archivos y Formatos ---

def test_data_loader_unsupported_format(data_loader):
    """Prueba que se levante ValueError para formatos no soportados (ej. .txt)."""
    with pytest.raises(ValueError, match="Formato de archivo no soportado"):
        data_loader.load_from_file("data.txt")

def test_data_loader_file_not_found(data_loader):
    """Prueba que se levante FileNotFoundError si el archivo no existe."""
    # Intentamos cargar un archivo JSON que no existe.
    with pytest.raises(FileNotFoundError):
        data_loader.load_from_file("ruta/a/archivo_que_no_existe.json")
        
def test_data_loader_case_insensitivity(data_loader, create_temp_json, tmp_path):
    """Prueba la robustez del DataLoader con extensiones en mayúsculas (ej. .JSON)."""
    
    # 1. Crear archivo JSON válido
    original_path = create_temp_json(TEST_DATA)
    
    # 2. Simular un archivo con la extensión en mayúsculas (renombrar)
    upper_path = str(tmp_path / "data.JSON")
    os.rename(original_path, upper_path)
    
    # 3. Cargar el archivo con la extensión en mayúsculas
    actual_df = data_loader.load_from_file(upper_path)
    
    # 4. Verificar que se cargó correctamente (DataLoader usa .lower() internamente)
    assert_frame_equal(EXPECTED_DF_VALID_JSON, actual_df)
