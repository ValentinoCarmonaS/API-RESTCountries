import os
import sys
import json
import tempfile

# Agregar el directorio padre al path para importar el módulo
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sales_system_legacy import SalesSystem


class TestJSONLoading:
    """Tests específicos para la carga de archivos JSON usando pytest"""
    
    def test_load_and_process_single_json_file(self):
        """Test que verifica la carga y procesamiento de un único archivo JSON"""
        
        # Crear un archivo JSON temporal de prueba
        test_data = [
            {
                "user_id": 100,
                "date": "2024-01-15", 
                "price": 100.0,
                "quantity": 2,
                "product": "Test Product 1",
                "category": "Test Category"
            },
            {
                "user_id": 100,
                "date": "2024-02-20",
                "price": 50.0,
                "quantity": 3, 
                "product": "Test Product 2",
                "category": "Test Category"
            },
            {
                "user_id": 200,
                "date": "2024-01-10",
                "price": 200.0,
                "quantity": 1,
                "product": "Test Product 3", 
                "category": "Test Category"
            }
        ]
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_json_path = f.name
        
        try:
            # Inicializar sistema
            system = SalesSystem()
            
            # Cargar SOLO el archivo JSON de prueba
            system.load_data(temp_json_path)
            
            # Verificar que los datos se cargaron correctamente
            assert len(system.data) == 3, f"Se esperaban 3 registros, se obtuvieron {len(system.data)}"
            
            # Verificar estructura de los datos cargados
            for record in system.data:
                assert 'user_id' in record
                assert 'date' in record
                assert 'price' in record
                assert 'quantity' in record
                assert 'product' in record
                assert 'category' in record
            
            # Procesar usuario 100
            result = system.process_user(100)
            assert result == True, "El procesamiento del usuario 100 debería ser exitoso"
            
            # Verificar que el reporte se generó
            assert 100 in system.reports, "El usuario 100 debería estar en los reportes"
            
            report = system.reports[100]
            
            # Verificar estructura del reporte
            assert 'monthly' in report
            assert 'yearly' in report
            assert 'user_id' in report
            assert 'generated_at' in report
            
            # Verificar datos mensuales
            assert '2024-01' in report['monthly']
            assert '2024-02' in report['monthly']
            
            january_data = report['monthly']['2024-01']
            february_data = report['monthly']['2024-02']
            
            # Verificar cálculos para enero
            assert january_data['total'] == 200.0  # 100.0 * 2
            assert january_data['count'] == 1
            assert january_data['average'] == 200.0
            
            # Verificar cálculos para febrero
            assert february_data['total'] == 150.0  # 50.0 * 3
            assert february_data['count'] == 1
            assert february_data['average'] == 150.0
            
            # Verificar datos anuales
            assert '2024' in report['yearly']
            yearly_data = report['yearly']['2024']
            
            assert yearly_data['total'] == 350.0  # 200 + 150
            assert yearly_data['count'] == 2
            assert yearly_data['average'] == 175.0
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_json_path)
    
    def test_json_file_not_found(self):
        """Test para verificar el manejo de archivos JSON que no existen"""
        system = SalesSystem()
        
        # Intentar cargar un archivo que no existe
        system.load_data('archivo_que_no_existe.json')
        
        # El sistema debería manejar el error gracefuly y continuar
        # sin lanzar excepciones que detengan la ejecución
        assert len(system.data) == 0, "No debería haber datos cargados"