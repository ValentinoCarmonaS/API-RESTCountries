# Usar una imagen oficial de Node.js
FROM node:20-alpine

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de manifiesto del paquete e instalar dependencias
COPY package*.json ./
RUN npm install 

# Copiar el resto del código fuente de la aplicación
COPY . .

# Exponer el puerto en el que se ejecuta el servidor de desarrollo de Vite
EXPOSE 5173

# El comando para iniciar el servidor de desarrollo
CMD ["npm", "run", "dev"]