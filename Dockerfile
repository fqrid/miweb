# Imagen base oficial de Python 3.11
FROM python:3.11-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar requerimientos e instalar dependencias
COPY src/requirements.txt ./src/
RUN pip install --no-cache-dir -r src/requirements.txt

# Copiar el resto del código
COPY . .

# Comando por defecto (por ejemplo, ejecutar las pruebas)
CMD ["pytest", "src/tests.py"]
