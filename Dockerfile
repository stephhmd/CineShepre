# Imagen base
FROM python:3.12-slim

# Carpeta interna
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto
EXPOSE 8000

# Ejecutar servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]