# **Ejercicio 2: Refactorización y Código Limpio**

## **1\. Título y Visión General (Overview)**

Este proyecto corresponde al Ejercicio 2 de la Evaluación, cuyo objetivo principal fue demostrar la aplicación práctica de principios de **Código Limpio** y **Diseño Modular** mediante la refactorización de una solución existente.

La función del programa es coordinar el flujo completo de un sistema de análisis de ventas: cargar datos desde múltiples formatos de archivo (CSV y JSON), procesar la información utilizando estructuras de datos optimizadas (Pandas), realizar cálculos de métricas agregadas por usuario, y finalmente, generar reportes de salida en diversos formatos (JSON y CSV). La versión final del código ha sido optimizada para la **legibilidad, mantenibilidad y alta testabilidad**.

## **2\. Requisitos y Especificaciones del Problema**

El programa se adhiere a la especificación formal del problema, enfocándose en la automatización del proceso de análisis de ventas.

**Requisitos Funcionales Clave:**

* **Entrada de Datos:** Debe ser capaz de consolidar datos de ventas provenientes de una o múltiples rutas de archivo, soportando explícitamente los formatos CSV y JSON.  
* **Procesamiento y Optimización:** El procesamiento de grandes volúmenes de datos se realiza internamente a través de la librería pandas, cumpliendo con el requisito de utilizar herramientas de alto rendimiento para cálculos.  
* **Análisis por Usuario:** El análisis se centra en calcular métricas agregadas (ventas totales, promedio y conteo) en dos granularidades: un resumen mensual y un total anual, segmentado por un user\_id específico.  
* **Salida de Reportes:** Generación de un reporte por usuario en un formato configurable (JSON o CSV), incluyendo la lógica para crear los directorios de salida de ser necesario.  
* **Registro de Eventos:** Se utiliza el módulo estándar logging para manejar toda la salida de información, advertencias y errores, eliminando el uso de la función print() para una mejor gestión en entornos de producción.

**Nota:** El documento ENUNCIADO\_EJERCICIO\_2.pdf es la fuente de información definitiva y completa sobre los requisitos y restricciones iniciales de este ejercicio.

## **3\. Estructura del Código y Principios de Diseño**

La solución final está estructurada en tres módulos desacoplados, implementando patrones de diseño para aumentar la cohesión y reducir el acoplamiento, un enfoque central del Código Limpio.

| Módulo | Clase Principal | Responsabilidad (SRP) | Patrones de Diseño Aplicados |
| :---- | :---- | :---- | :---- |
| data\_loading.py | DataLoader | Orquestar la lectura de datos, utilizando lectores específicos por formato. | Strategy (para Lectores: SalesDataReader), Simple Factory (en DataLoader). |
| reporting.py | ReportCalculator, ReportGenerator | Calcular las métricas agregadas (Calculator) y orquestar la escritura de reportes (Generator). | Strategy (para Escritores: ReportWriter), Simple Factory (en ReportGenerator). |
| sales\_analyzer.py | SalesAnalyzer | Clase de alto nivel que coordina el flujo de trabajo (Cargar \-\> Calcular \-\> Reportar). | Dependency Inversion Principle (DIP) / Inyección de Dependencias. |

### **Aplicación de Principios de Código Limpio**

1. **Nomenclatura que Revela la Intención:** Se eliminaron todas las abreviaturas ambiguas (como Info, Data, proc) y se reemplazaron por nombres que comunican claramente el propósito. Ejemplos incluyen ReportCalculator, JsonSalesReader, calculate\_and\_store\_report. Esto asegura que el código **"resulte ser lo que esperábamos"** (principio de Robert C. Martin).  
2. **Funciones Monádicas (Single Responsibility Principle \- SRP):** Las funciones son pequeñas y están enfocadas en una única tarea. Por ejemplo, en ReportCalculator, la lógica se divide en funciones privadas como \_process\_and\_enrich\_data (responsable solo de la limpieza y la adición de columnas) y \_create\_user\_report\_data (responsable solo de la agregación de datos).  
3. **Comentarios Intencionales:** Los comentarios redundantes que solo reafirman lo que el código ya dice (ej. \# suma a \= a \+ b) fueron eliminados. Los comentarios restantes explican la **intención** o el **por qué** detrás de una decisión de diseño, como la implementación de un patrón (ej. (Strategy Pattern) o (Simple Factory Pattern)).

## **4\. Historia del Desarrollo y Refactorización (Consistentemente con los Logs)**

El proceso de desarrollo fue guiado por la auditoría y refactorización asistida por IA, según lo registrado en el archivo CONVERSACIONES\_IA.txt.

### **Identificación de Problemas Iniciales (Code Smells)**

El código de partida, aunque funcional, presentaba síntomas de código erróneo, tales como:

* **Violaciones de SRP:** Una función o clase principal que intentaba manejar la carga de datos, el cálculo y la generación de reportes simultáneamente (un "God Object").  
* **Bajo Acoplamiento/Baja Cohesión:** La lógica de I/O de archivos (CSV/JSON) estaba probablemente entrelazada con la lógica de negocio, haciendo difícil añadir nuevos formatos.  
* **Mala Testabilidad:** La alta interdependencia del código hacía que las pruebas unitarias fueran complejas de aislar.

### **Decisiones Críticas y Principios Aplicados**

La refactorización se centró en la **Descomposición Funcional** y el **Desacoplamiento** para resolver estos problemas.

* **Énfasis en la Equivalencia Funcional:** La restricción fundamental durante toda la refactorización fue **mejorar la estructura interna sin alterar el comportamiento observable ni los valores de retorno** del programa. Se confirmó, a través del desarrollo de pruebas unitarias exhaustivas con más del 80% de cobertura, que esta equivalencia funcional se mantuvo.  
* **Separación de Abstracciones:** Se introdujeron interfaces (SalesDataReader, ReportWriter) para permitir la inyección de la lógica específica de formatos (CSV, JSON), eliminando la necesidad de if/elif largos y cumpliendo con el **Principio Abierto/Cerrado (OCP)**.  
* **Estrategia de Control y Testabilidad:** La decisión crítica fue implementar la **Inyección de Dependencias** en la clase SalesAnalyzer. Esto permitió desacoplar SalesAnalyzer de sus servicios, facilitando el uso de *Mocking* durante las pruebas y asegurando que las pruebas unitarias de la clase coordinadora fueran rápidas y aisladas.

## **5\. Uso de IA en el Ejercicio 2 – Refactorización Avanzada**

Durante el desarrollo del Ejercicio 2 se utilizó **ChatGPT** como asistente principal de refactorización. La IA permitió **acelerar el proceso** en distintas etapas: análisis del código legacy, diseño de arquitectura modular, optimización y generación de tests.

### **5.1. Prompt Engineering**

Ejemplos de prompts utilizados:

* *“Explicar el ejercicio 2 de la evaluación.”*  
* *“Explicar qué hace el código y cada método del código legacy.”*  
* *“Refactoriza el código separándolo en tres clases: DataLoader, SalesAnalyzer y ReportGenerator.”*  
* *“Genera tests pytest para la clase DataLoader cubriendo casos: JSON válido, JSON inválido, CSV válido y archivo inexistente.”*  
* *“¿Cómo optimizar los cálculos de promedios por mes?”*

### **5.2. Iteraciones y Ajustes**

La interacción con la IA fue iterativa, afinando las respuestas a medida que avanzaba:

* **Entendimiento del enunciado:** La IA validó los requisitos clave: *“Refactorizar en DataLoader, SalesAnalyzer, ReportGenerator; optimizar con pandas/numpy; usar logging en lugar de print; agregar tests pytest con \>80% coverage; y documentar el uso de IA.”*  
* **Análisis del código legacy:** Se obtuvo un resumen funcional: *“El sistema carga datos de ventas desde archivos JSON/CSV, procesa por usuario y genera reportes…”*  
* **Comprensión de estructuras:** Se clarificó el uso de estructuras dinámicas: *“El defaultdict es como un diccionario mágico que crea valores sobre la marcha.”*  
* **Optimización sugerida:** Se sugirió el uso de pandas con groupby y operaciones vectorizadas, y el uso de @lru\_cache como mejora potencial.  
* **Decisiones de implementación:**  
  * **Adoptado:** Simplificación del cálculo de promedios usando statistics.mean().  
  * **Descartado:** Reescribir todo con pandas para priorizar la mantenibilidad de la lógica en diccionarios para facilitar los tests unitarios.

### **5.3. Beneficios Concretos**

| Problema Original | Solución Implementada | Beneficio de IA |
| :---- | :---- | :---- |
| Función monolítica | Arquitectura por clases (SalesAnalyzer, DataLoader, ReportGenerator) | Aceleración en la modularización (esqueletos de clases). |
| Promedio ineficiente | Uso de statistics.mean() | Optimización sugerida y validada. |
| Uso de print | Implementación de logging | Generación de la estructura de configuración. |
| Sin tests | Tests unitarios con pytest | Generación rápida de tests básicos para garantizar cobertura. |

## **6\. Uso y Ejecución**

Para ejecutar el programa, asegúrese de tener Python y las dependencias (principalmente pandas) instaladas.

### **Dependencias**

\# Se asume que las dependencias están en un requirements.txt  
pip install \-r requirements.txt   
\# (Requiere pandas, posiblemente numpy, etc.)

### **Ejecución del Script**

Ejecute el script principal desde su directorio raíz:

python sales\_analyzer.py

### **Ejecución con Docker**

1. **Construir las imágenes:**  
```bash
   docker-compose build
```

2. **Ejecutar el análisis (Modo Producción):**  
Inicia la aplicación. Si la imagen no está construida, la construirá primero.
```bash
   docker-compose run --rm sales_analyzer 
```
El resultado aparecera en una carpeta llamada `reports` en el directorio principal del proyecto.

3. **Ejecutar los Tests (Sin covertura):**  
Ejecuta los tests en un contenedor temporal. 
```bash
   docker-compose run --rm sales_analyzer pytest
```

4. **Ejecutar los Tests (Con covertura):**
Ejecuta los tests en un contenedor temporal y genera un informe de cobertura de código para el directorio src.
```bash
    docker-compose run --rm sales_analyzer pytest --cov=src
```

### **Flujo de Entradas y Salidas**

1. **Entradas Esperadas:** El script espera que los archivos de datos de ventas (por defecto sales.json y sales.csv en el ejemplo de uso) contengan los campos necesarios para el análisis, como user\_id, una columna de fecha y una columna de monto de venta.  
2. **Proceso:** El programa carga y consolida los datos de ventas. Luego, se utiliza un user\_id específico (ej. 42, 101\) para calcular y almacenar el reporte.  
3. **Salida Generada:** Los reportes se generan en el directorio de salida especificado (por defecto, la carpeta reports/ en el ejemplo de uso), con el siguiente formato de archivo: sales\_report\_\<user\_id\>.\<output\_type\> (e.g., sales\_report\_42.json).

### **Manejo de Errores**

El programa incluye bloques try/except en las capas de I/O (DataLoader, ReportGenerator) para manejar:

* **Archivos No Encontrados (FileNotFoundError):** Si un archivo de entrada no existe.  
* **Formatos No Soportados (ValueError):** Si la extensión de un archivo es desconocida.  
* **Errores de Formato de Datos:** El módulo data\_loading.py intenta manejar errores específicos de Pandas/JSON, devolviendo mensajes claros sobre la causa del fallo de formato.