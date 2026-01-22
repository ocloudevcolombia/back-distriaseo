FROM python:3.11-slim

# Evitar archivos .pyc y forzar logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Para que "from app import ..." funcione
ENV PYTHONPATH=/app/app

# Copiar primero requirements para cachear instalación
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto interno (el que usará Uvicorn)
EXPOSE 9002

# Arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9002"]
