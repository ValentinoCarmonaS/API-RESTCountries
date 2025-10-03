# API-RESTCountries

Esta es una API desarrollada en FastAPI que consume datos de la API pública [RESTCountries](https://restcountries.com/), los persiste en una base de datos local SQLite y permite realizar consultas sobre ellos.

## Cómo Ejecutar

1. Para Construir la Imagen de Docker
Desde la raíz de tu proyecto (donde está el Dockerfile), ejecuta el siguiente comando. Esto creará una imagen llamada api-countries.
```bash
docker build -t api-countries .
```

2. Para Levantar el Servidor de la API
Una vez construida la imagen, puedes iniciar un contenedor para levantar el servidor:
```bash
docker run -p 8000:8000 api-countries
```
Lu API estará corriendo y accesible en http://localhost:8000. 

3. Para Ejecutar los Tests
Puedes usar la misma imagen para ejecutar tu suite de tests en un entorno limpio y aislado. Para ello utilizaremos el siguiente comando:
```bash
docker run api-countries pytest
```
Esto iniciará un contenedor, correrá todos los tests dentro de él y luego se detendrá, mostrándote el resultado.

## Endpoints Disponibles

### Raíz

*   `GET /`
    *   **Descripción:** Muestra un mensaje de bienvenida y la versión de la API.

### Países

*   `GET /countries`
    *   **Descripción:** Devuelve una lista de todos los países almacenados en la base de datos.
    *   **Parámetros (Query):**
        *   `region` (opcional): Filtra los países por la región especificada.
    *   **Ejemplo de Uso:**
        ```bash
        curl "http://localhost:8000/countries?region=Europe"
        ```

*   `GET /countries/stats`
    *   **Descripción:** Devuelve estadísticas calculadas sobre los países.
    *   **Parámetros (Query):**
        *   `metric` (obligatorio): La métrica a calcular. Valores posibles: `population`, `area`, `countries_per_region`.
        *   `region` (opcional): Filtra los datos para el cálculo de la estadística a una región específica.
    *   **Ejemplo de Uso:**
        ```bash
        curl "http://localhost:8000/countries/stats?metric=population&region=Americas"
        ```

## Uso de Inteligencia Artificial

Durante el desarrollo utilicé varias herramientas de IA (ChatGPT, Gemini Code Assist, Claude) para guiarme en la implementación de la API del Ejercicio 1.

### Ejemplos de interacciones relevantes

1. **Estructura de Entrega y Archivos**
   - **Mi prompt**:  
     > "init_db.py debe utilizar models.py?"  
   - **Respuesta de la IA**:  
     > "Sí, en el Ejercicio 1 es necesario que init_db.py importe las definiciones de la base de datos de models.py para crear físicamente las tablas."

2. **Persistencia de Datos de RESTCountries**
   - **Mi prompt**:  
     > "La llamada a la API RESTCountries debe estar en init_db.py?"  
   - **Respuesta de la IA**:  
     > "No. init_db.py solo debe crear la estructura. El consumo de RESTCountries y la persistencia corresponde a la lógica de negocio en app.py."

3. **Comportamiento de init_db.py**
   - **Mi prompt inicial**:  
     > "¿La llamada a la API RESTCountries debe estar en init_db.py?"  
   - **Respuesta de la IA (primera)**:  
     > "No, init_db.py solo debe crear la estructura. El consumo de RESTCountries corresponde a la lógica en app.py."  

   - **Iteración posterior**:  
     Volví a preguntar qué debía ocurrir si la base ya tenía datos. La IA me respondió:  
     > "init_db.py debería verificar si hay datos y, si no existen, consumir la API RESTCountries y guardarlos en la base."  

   - **Conclusión propia**:  
     Decidí implementar esta segunda opción: `init_db.py` crea las tablas y, si detecta que la base está vacía, consume la API RESTCountries y persiste los datos útiles (nombre, región, población, área, etc.). De esta manera, al levantar el servidor por primera vez la base ya está lista para ser consultada.

4. **Tests Automatizados**
   - **Mi prompt**:  
     > "Crear los test de test_api.py para que prueben los endpoints de la API."  
   - **Respuesta de la IA**:  
     > "Se generaron pruebas que validan los endpoints `/countries` y `/countries/stats`, incluyendo casos de éxito y error. También se corrigió un bug en app.py agregando `return` a las funciones de estadísticas."

5. **Dockerización**
   - **Mi prompt**:  
     > "Generar un archivo Dockerfile para levantar el servidor o ejecutar los tests."  
   - **Respuesta de la IA**:  
     > "Se propuso un Dockerfile con base en `python:3.11-slim`, que permite tanto correr el servidor (`docker run -p 8000:8000 api-countries`) como ejecutar los tests (`docker run api-countries pytest`)."

### Reflexiones
- La IA me ayudó a comprender conceptos (ej. diferencia de responsabilidades entre `init_db.py` y `models.py`).  
- Me aceleró tareas repetitivas (crear modelos, endpoints y tests).  
- No todas las respuestas fueron correctas, algunos casos en donde tuve que corregir manualmente: 
    - Algunos imports en los tests dieron error.  
    - Algunas partes del codigo no seguian buenas practicas. 
    - Algunos test fueron incoherentes con la API. 

