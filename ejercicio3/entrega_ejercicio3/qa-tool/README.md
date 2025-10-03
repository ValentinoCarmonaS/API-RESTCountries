# QA Tool - Limpieza de Datos

Esta aplicación es una herramienta de control de calidad (QA) diseñada para identificar, corregir y exportar datos de ventas limpios. Carga un archivo `sales_data.json`, detecta inconsistencias y permite al usuario corregirlas antes de exportar un conjunto de datos válido.

## Características

-   Detección automática de errores comunes (ej. valores nulos, cantidades negativas).
-   Interfaz para corregir errores de forma individual.
-   Seguimiento del progreso de corrección.
-   Exportación de los datos limpios (registros válidos originales + registros corregidos) a un archivo JSON.
-   Pruebas E2E con Cypress para garantizar la funcionalidad.

---

## Cómo Ejecutar la Aplicación

Puedes ejecutar este proyecto de dos maneras: directamente en tu máquina local o utilizando Docker.

### Requisitos Previos

-   **Para desarrollo local:**
    -   [Node.js](https://nodejs.org/) (v18 o superior)
    -   [npm](https://www.npmjs.com/) o [yarn](https://yarnpkg.com/)
-   **Para Docker:**
    -   [Docker](https://www.docker.com/products/docker-desktop/)
    -   [Docker Compose](https://docs.docker.com/compose/install/)

---

### Método 1: Ejecución Local (Sin Docker)

1.  **Navegar al directorio del proyecto:**
    ```bash
    cd qa-tool
    ```

2.  **Instalar dependencias:**
    ```bash
    npm install
    ```

3.  **Iniciar el servidor de desarrollo:**
    ```bash
    npm run dev
    ```

4.  Abre tu navegador y visita [http://localhost:5174](http://localhost:5174).

---

### Método 2: Ejecución con Docker

Este método utiliza el archivo `docker-compose.yml` ubicado en la carpeta raíz del ejercicio (`entrega_ejercicio3`) para levantar tanto el `client-dashboard` como el `qa-tool`.

1.  **Navegar a la carpeta raíz del ejercicio:**
    ```bash
    # Si estás en la carpeta 'qa-tool', sube un nivel
    cd .. 
    ```

2.  **Construir y levantar los contenedores:**
    ```bash
    docker-compose up
    ```

3.  Abre tu navegador y visita [http://localhost:5174](http://localhost:5174). La aplicación se ejecutará dentro de un contenedor Docker, con hot-reloading habilitado.

4. **Para detener ambos contenedores:**
    ```bash
    docker-compose down
    ```

---

## Como Ejecutar las Pruebas Unitarias con Doker

Puedes ejecutar las pruebas unitarias con Jest

1.  Asegúrate de que los contenedores estén **en ejecución** (usando `docker-compose up`).

2. Abre una nueva terminal y ejecuta el siguiente comando para iniciar las pruebas dentro del contenedor `qa-tool`:
    ```bash
    docker exec -it qa-tool-dev npm run test
    ```

---

## Cómo Ejecutar las Pruebas E2E

Las pruebas End-to-End se ejecutan con Cypress en modo *headless* en forma local, ya que en Docker ocurren problemas explicados y solucionados en esta [pagina](https://docs.cypress.io/app/get-started/install-cypress#Linux-Prerequisites) _(pero por falta de tiempo, no puedo dedicar el tiempo necesario para solucionarlo)_.

1.  Asegúrate de que los contenedores estén **en ejecución** o que la pagina este funcionando localmente.

2.  **Navegar al directorio del proyecto:**
    ```bash
    cd qa-tool
    ```

3.  Asegurate de tener las **dependencias instaladas:**
    ```bash
    npm install
    ```

4.  Abre una nueva terminal y ejecuta el siguiente comando para iniciar las pruebas de forma local:
    ```bash
    npm run test:e2e-headless
    ```
    - Tambien se pueden correr las pruebas con chrome:
        ```bash
        npm run test:e2e
       ```

---



## Scripts Disponibles

En el directorio de `qa-tool`, puedes ejecutar varios comandos:

-   `npm run dev`: Inicia la aplicación en modo de desarrollo.
-   `npm run build`: Compila la aplicación para producción en la carpeta `dist`.
-   `npm run test:e2e`: Ejecuta las pruebas E2E con Cypress en modo headless.
-   `npm run test`: Ejecuta las pruebas unitarias con Jest.