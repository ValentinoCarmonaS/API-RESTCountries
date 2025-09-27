# Usar una imagen oficial de Python como imagen base
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
# --no-cache-dir: Deshabilita el caché de pip para reducir el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al directorio de trabajo
COPY . .

# Exponer el puerto en el que se ejecuta la aplicación
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación cuando se inicie el contenedor
# Esto levanta el servidor de FastAPI con Uvicorn.
# --host 0.0.0.0 es crucial para que el servidor sea accesible desde fuera del contenedor.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
