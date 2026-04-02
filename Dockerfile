# Imagen base liviana
FROM python:3.10-slim

# Evitar generación de archivos .pyc y habilitar salida de buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puertos para DigitalOcean
EXPOSE 8001
EXPOSE 8002

# El Worker corre en el módulo app.main
CMD ["python", "-m", "app.main"]
