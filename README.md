# Ejercicio 1 (API mínima con ayuda de IA):
## Objetivo:
Desarrollar una API que consuma datos externos, los persista en una base de datos local, y
permita consultarlos eficientemente, utilizando IA para acelerar el desarrollo.

### Tarea:
1. Consumir y Persistir Datos:
    1. Crear una API en Python (FastAPI) o Ruby (Sinatra) que:
        1. Consuma datos de una API pública (RESTCountries o
OpenWeatherMap).
        2. Guarde los datos en una base de datos local (SQLite para simplificar,
PostgreSQL para mayor realismo).
    2. Ejemplos de transformaciones:
        1. Para países: almacenar nombre, región, población, y área.
        2. Para clima: almacenar temperatura, humedad, y fecha de consulta.
2. Endpoints con Consultas a DB:
    1. GET /countries?region={region}: Devuelve países filtrados por región
(consulta a DB).
    2. GET /countries/stats?metric={metric}: Devuelve estadísticas calculadas (ej:
población promedio por región).
    3. GET /weather/{city}: Devuelve clima actual, almacenando cada consulta en
DB.
3. Documentar el Uso de IA:
    1. Ejemplo:
        1. "Usé ChatGPT para generar el modelo de la base de datos (prompt:
'SQLAlchemy model for countries with name, region, population')."
        2. "Copilot sugirió la función de actualización periódica de datos
climáticos."

### Requisitos obligatorios:
- Usar herramientas de IA (ej: ChatGPT, GitHub Copilot, u otra) para generar código
repetitivo (ej: configuración de endpoints, manejo de requests HTTP). Documentar su uso
en el README.
- Entregar una API funcional que pueda ejecutarse localmente con Docker o instalación
manual.
- Base de Datos: Usar SQLite (para simplificar) o PostgreSQL (Docker opcional).
Implementar al menos 2 tablas relacionadas (ej: countries y cities).
- Incluir tests básicos (ej: un script de Python con `requests` o un `curl` command para
probar la API).
Entregable:
1. Código:
- `app.py` (FastAPI) o `server.rb` (Sinatra).
- `requirements.txt` (Python) o `Gemfile` (Ruby).
- `Dockerfile` (opcional pero deseable).
2. Documentación:
- `README.md` con:
- Cómo ejecutar:
```bash
# Opción 1: Sin Docker
pip install -r requirements.txt && uvicorn app:app --reload
# Opción 2: Con Docker
docker build -t api-exercise . && docker run -p 8000:8000 api-exercise
```
- Herramientas de IA usadas: Ejemplo:
"Usé GitHub Copilot para generar el endpoint de filtrado por región (prompt: 'FastAPI
endpoint to filter countries by region')."
- Endpoints disponibles:
- `GET /countries?region={region}` → Devuelve países filtrados.
- `GET /weather/{city}` → Devuelve promedio de temperatura (si usan OpenWeather).
3. Tests:
- Incluir en el README un ejemplo de cómo probar la API:
```bash
curl "http://localhost:8000/countries?region=Europe"
```
Ejemplo de estructura de carpetas:
```
candidato/
├── app.py # o server.rb
├── models.py # Modelos de DB
├── init_db.py # Script de inicialización
├── requirements.txt # o Gemfile
├── Dockerfile # Opcional (para PostgreSQL)
├── README.md
└── tests/
├── test_api.py # Tests de endpoints
└── test_db.py # Tests de DB
```
Testing
1. Tests de Endpoints (API)
Cobertura mínima:
Verificar que los endpoints devuelven el código HTTP correcto (200, 400, 404, etc.).
Validar el formato JSON de las respuestas (ej: schema con pydantic o jsonschema).
Incluir casos de error:
Región inexistente en /countries?region={region}.
Ciudad no encontrada en /weather/{city}.
2. Tests de Base de Datos
Requerimientos:
Verificar que los datos se persisten correctamente después de consumir la API externa.
Probar consultas complejas (ej: estadísticas agregadas).
Usar una DB en memoria (SQLite) para tests.

# Ejercicio 2:
Refactorización Avanzada Asistida por IA (Código Legacy
Complejo)
Objetivo:
Refactorizar un sistema legacy de procesamiento de datos (Python/Ruby) que presenta:
- Mala estructuración.
- Código espagueti.
- Problemas de performance.
- Zero tests.
Tarea:
1. Mejorar la arquitectura (modularización, patrones).
2. Optimizar partes críticas.
3. Documentar el uso de IA para acelerar el proceso.
Código Legacy (Python) - Sistema de Reportes de Ventas
# sales_system_legacy.py
import os
import json
import csv
from datetime import datetime
from collections import defaultdict
class SalesSystem:
def __init__(self):
self.data = []
self.reports = {}
self.user_prefs = {
'currency': 'USD',
'date_format': '%Y-%m-%d',
'output_type': 'json'
}
def load_data(self, *args):
for file_path in args:
try:
if file_path.endswith('.json'):
with open(file_path) as f:
new_data = json.load(f)
if isinstance(new_data, list):
self.data.extend(new_data)
else:
print(f"Invalid JSON format in {file_path}")
elif file_path.endswith('.csv'):
with open(file_path) as f:
reader = csv.DictReader(f)
self.data.extend(list(reader))
else:
print(f"Unsupported file format: {file_path}")
except Exception as e:
print(f"Error loading {file_path}: {str(e)}")
def process_user(self, user_id):
user_sales = [s for s in self.data if str(s.get('user_id')) == str(user_id)]
if not user_sales:
print(f"No sales found for user {user_id}")
return False
monthly = defaultdict(lambda: {'total': 0, 'count': 0, 'items': []})
yearly = defaultdict(lambda: {'total': 0, 'count': 0})
for sale in user_sales:
try:
date = datetime.strptime(sale['date'], '%Y-%m-%d')
month_key = date.strftime('%Y-%m')
year_key = date.strftime('%Y')
price = float(sale['price'])
quantity = int(sale['quantity'])
total = price * quantity
monthly[month_key]['total'] += total
monthly[month_key]['count'] += 1
monthly[month_key]['items'].append(sale)
yearly[year_key]['total'] += total
yearly[year_key]['count'] += 1
except (KeyError, ValueError) as e:
print(f"Invalid sale record: {sale}. Error: {e}")
continue
## Calculate averages
for period in [monthly, yearly]:
for key in period:
if period[key]['count'] > 0:
period[key]['average'] = period[key]['total'] / period[key]['count']
else:
period[key]['average'] = 0
self.reports[user_id] = {
'monthly': dict(monthly),
'yearly': dict(yearly),
'user_id': user_id,
'generated_at': datetime.now().isoformat()
}
return True
def generate_reports(self, output_dir, users=None):
if not os.path.exists(output_dir):
os.makedirs(output_dir)
users_to_process = users if users else [uid for uid in self.reports.keys()]
for user_id in users_to_process:
if user_id not in self.reports:
if not self.process_user(user_id):
continue
report = self.reports[user_id]
filename = f"sales_report_{user_id}.{self.user_prefs['output_type']}"
filepath = os.path.join(output_dir, filename)
try:
if self.user_prefs['output_type'] == 'json':
with open(filepath, 'w') as f:
json.dump(report, f, indent=2)
elif self.user_prefs['output_type'] == 'csv':
self._generate_csv_report(report, filepath)
else:
print(f"Unsupported output format: {self.user_prefs['output_type']}")
continue
print(f"Generated report: {filepath}")
except IOError as e:
print(f"Failed to write report for user {user_id}: {e}")
def _generate_csv_report(self, report, filepath):
with open(filepath, 'w', newline='') as f:
writer = csv.writer(f)
writer.writerow(['Period', 'Total Sales', 'Average Sale', 'Number of Sales'])
for period in ['monthly', 'yearly']:
for period_name, data in report[period].items():
writer.writerow([
period_name,
data['total'],
data.get('average', 0),
data['count']
])
def set_preferences(self, **prefs):
for key, value in prefs.items():
if key in self.user_prefs:
self.user_prefs[key] = value
else:
print(f"Ignoring unknown preference: {key}")
## Example usage:
if __name__ == "__main__":
system = SalesSystem()
system.load_data('sales.json', 'sales.csv')
system.set_preferences(output_type='json', currency='EUR')
system.process_user(42)
system.process_user(101)
system.generate_reports('reports', users=[42, 101])
Problemas clave a resolver:
1. Acoplamiento alto: Todo en una función gigante.
2. Manejo de errores débil: No hay excepciones para JSON corrupto o permisos.
3. Performance: Cálculo del promedio ineficiente (podría usarse `statistics`).
4. Testabilidad: Código no modularizado → difícil de testear.
Requisitos obligatorios:
1. Refactorizar en módulos/CLASES:
- Separar en: `DataLoader`, `SalesAnalyzer`, `ReportGenerator`.
2. Optimizar:
- Usar `pandas` o `numpy` para cálculos si es necesario.
- Implementar logging en lugar de `print`.
3. Agregar tests:
- Unit tests (pytest) con >80% coverage.
4. IA Asistida:
- Usar Copilot/ChatGPT para:
- Generar la estructura de clases.
- Escribir tests automatizados.
- Justificar optimizaciones (ej: "IA sugirió usar `@lru_cache` para X").
Entregable:
```
deliverable/
├── src/
│ ├── __init__.py
│ ├── data_loader.py
│ ├── sales_analyzer.py
│ └── report_generator.py
├── tests/
│ ├── test_data_loader.py
│ ├── test_sales_analyzer.py
│ └── test_report_generator.py
├── requirements.txt
├── Dockerfile
└── README.md
```
README.md debe incluir:
1. Uso de IA:
El candidato debe documentar explícitamente su proceso de trabajo con IA, incluyendo:
a) Prompt Engineering:
i) Listado de prompts exactos utilizados.
b) Iteraciones y Ajustes:
i) Cómo evolucionaron los prompts para mejorar resultados.
c) Validación de Sugerencias:
i) Qué sugerencias de IA fueron descartadas y por qué.
d) Fragmentos de Diálogo Relevantes:
i) Capturas de pantalla o citas textuales de las conversaciones más útiles.
2. Cómo ejecutar:
```bash
# Instalar dependencias
pip install -r requirements.txt
# Ejecutar tests
pytest tests/ -v
# Ejecutar sistema refactorizado
python -m src.main
```
3. Diff de cambios: Tabla comparativa:
| Problema Original | Solución Implementada | Herramienta IA Usada |
|-------------------|-----------------------|-----------------------|
| Función monolítica | Arquitectura por clases | Copilot |
| Promedio ineficiente | Uso de `statistics.mean()` | ChatGPT |

# Ejercicio 3 Frontend:
Dashboard de Analytics para E-Commerce + Herramienta de QA
Objetivo:
Desarrollar dos aplicaciones frontend interconectadas usando React + TypeScript:
1. Dashboard para el cliente (visualización de datos).
2. Herramienta de QA (para detectar y corregir problemas en los datos).
Input Provisto
El candidato recibirá:
1. Dataset dummy (`sales_data.json`) con problemas intencionales:
```json
{
"sales": [
{
"id": 1,
"date": "2023-01-15",
"product": "Laptop",
"quantity": 2,
"price": 1200,
"rating": 4.5
},
{
"id": 2,
"date": "2023-01-15",
"product": "Mouse",
"quantity": -3, // Error: cantidad negativa
"price": 25,
"rating": 3.8
},
{
"id": 3,
"date": "2023-01-16",
"product": null, // Error: producto nulo
"quantity": 1,
"price": 300,
"rating": 5.0
}
]
}
```
2. Requisitos técnicos:
- Stack: React + TypeScript + MUI/Tailwind.
- Testing: Jest + React Testing Library (para QA).
Tarea:
1. Dashboard para el Cliente
- Funcionalidades:
- Mostrar métricas clave:
- Ventas totales (suma de `price * quantity`).
- Producto más vendido.
- Rating promedio (excluyendo datos corruptos).
- Gráficos interactivos (ej: ventas por día).
- Filtros: Por rango de fechas y productos.
- Requisitos:
- Manejar datos corruptos (ej: ignorar registros con `quantity < 0` o `product === null`).
- Usar Chart.js o D3.js para visualizaciones.
2. Herramienta de QA
- Funcionalidades:
- Tabla que liste todos los registros con errores (ej: `quantity < 0`, `product === null`).
- Opción para "corregir" datos (ej: cambiar `quantity` negativa a positiva).
- Botón para exportar datos limpios en JSON.
- Requisitos:
- Tests E2E con Cypress (ej: validar que el botón "Corregir" funciona).
Entregable:
Ejemplo de entregable del candidato (no es necesario que sea la misma arquitectura):
```
deliverables/
├── client-dashboard/ # App para el cliente
│ ├── src/
│ │ ├── components/ # Gráficos, filtros
│ │ ├── hooks/ # useSalesData, useFilters
│ │ └── types/ # Interfaces TypeScript
│ ├── public/sales_data.json
│ ├── README.md
│ └── package.json
│
├── qa-tool/ # App para QA
│ ├── src/
│ │ ├── components/ # Tabla, formularios
│ │ ├── utils/ # Funciones de limpieza
│ │ └── tests/ # Tests E2E
│ ├── README.md
│ └── package.json
│
└── instructions.md # Cómo levantar ambos proyectos
```
Instrucciones extras:
Uso de IA:
- El README.md debe documentar como se corre la aplicacion.
- El archivo manual_informe.txt debe contener:
* Explicación en primera persona del proceso de desarrollo
* Prompts exactos utilizados con las herramientas de IA
* Fragmentos de código generados por IA y cómo se adaptaron manualmente
* Decisiones tomadas independientemente de las sugerencias de IA
- IMPORTANTE: Estos archivos deben ser escritos completamente por el candidato, sin
uso de IA.
Bonus (Opcional)
- Dockerizar ambas apps para facilitar el despliegue.
- Añadir autenticación simulada (ej: login de QA vs. Cliente).

# Ejercicio extra:
Procesamiento y limpieza de datos con generación de informe
automatizado
Objetivo:
Demostrar habilidades de limpieza de datos, análisis básico y automatización utilizando
Python y herramientas de IA.
Tarea:
1. Descargar el dataset [COVID-19 World Vaccination
Progress](https://www.kaggle.com/gpreda/covid-world-vaccination-progress).
2. Limpiar y procesar los datos:
- Manejar valores nulos/duplicados.
- Filtrar registros relevantes (ej: países con >1M de vacunados).
- Calcular métricas básicas (ej: promedio de vacunación por región).
3. Generar un informe en PDF que incluya:
- Gráficos (ej: evolución de vacunación por país usando Seaborn/Matplotlib).
- Breve análisis (3-5 líneas) de hallazgos.
Requisitos obligatorios:
- Usar herramientas de IA (ej: ChatGPT, GitHub Copilot) para acelerar tareas repetitivas (ej:
generación de código de gráficos). Documentar su uso en el README.
- Entregar un script ejecutable (`main.py`) que, al correrse, genere el PDF automáticamente.
- Dockerizar la solución (incluir `Dockerfile` y `requirements.txt`) o asegurarse de que
funcione con un `pip install -r requirements.txt`.
Entregable:
1. Código:
- `main.py` (script principal).
- Carpeta `data/` con el dataset (o instrucciones para descargarlo).
2. Documentación:
- `README.md` con:
- Cómo ejecutar: Pasos para correr el script localmente o con Docker.
- Herramientas de IA usadas: Ejemplo:
"Usé ChatGPT para generar el código de los gráficos de Seaborn (prompt: 'How to plot
a time-series bar chart in Seaborn?')".
- Decisiones técnicas: Explicación breve de cómo se manejaron los datos (ej:
"Reemplacé nulos con la mediana porque...").
- `requirements.txt` o `Dockerfile`.
3. Output:
- `informe.pdf` (generado al ejecutar el script).
Ejemplo de estructura de carpetas:
```
candidato/
├── data/
│ └── vaccinations.csv
├── main.py
├── requirements.txt
├── Dockerfile
├── README.md
└── informe.pdf
```
Notas adicionales:
- Dificultad ajustable: Pueden simplificar el dataset o pedir menos gráficos si el tiempo es
limitado.
- Evaluación clave:
- ¿El PDF se genera sin errores?
- ¿El README permite replicar el proceso fácilmente?
- ¿Queda claro qué parte se resolvió con IA y qué parte manualmente?