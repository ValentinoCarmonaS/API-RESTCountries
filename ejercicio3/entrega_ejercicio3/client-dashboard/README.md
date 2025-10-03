# Client Dashboard

Este proyecto es un dashboard de visualización de datos de ventas construido con React, Vite y TypeScript. Muestra métricas clave y gráficos basados en un archivo de datos `sales_data.json`.

## Características

-   Visualización de ventas totales, promedio y por producto.
-   Gráficos interactivos para analizar tendencias.
-   Filtros dinámicos por producto y rango de fechas.
-   Interfaz moderna construida con Tailwind CSS.

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
    cd client-dashboard
    ```

2.  **Instalar dependencias:**
    ```bash
    npm install
    ```

3.  **Iniciar el servidor de desarrollo:**
    ```bash
    npm run dev
    ```

4.  Abre tu navegador y visita [http://localhost:5173](http://localhost:5173).

---

### Método 2: Ejecución con Docker

Este método utiliza el archivo `docker-compose.yml` ubicado en la carpeta raíz del ejercicio (`entrega_ejercicio3`) para levantar tanto el `client-dashboard` como el `qa-tool`.

1.  **Navegar a la carpeta raíz del ejercicio:**
    ```bash
    # Si estás en la carpeta 'client-dashboard', sube un nivel
    cd .. 
    ```

2.  **Construir y levantar los contenedores:**
    ```bash
    docker-compose up --build
    ```

3.  Abre tu navegador y visita [http://localhost:5173](http://localhost:5173). La aplicación se ejecutará dentro de un contenedor Docker, con hot-reloading habilitado.

---

## Scripts Disponibles

En el directorio de client-dashboard, puedes ejecutar varios comandos:

-   `npm run dev`: Inicia la aplicación en modo de desarrollo.
-   `npm run build`: Compila la aplicación para producción en la carpeta `dist`.
