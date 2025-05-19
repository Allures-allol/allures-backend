# Используем официальный образ Python 3.10 (slim)
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Устанавливаем MSSQL-драйвер ODBC и зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
        apt-transport-https \
        ca-certificates && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 --allow-downgrades --allow-remove-essential --allow-change-held-packages && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем весь проект
COPY . .

# Устанавливаем PYTHONPATH для корректного импорта общих модулей
ENV PYTHONPATH=/app:/app/common

# Запуск FastAPI приложения
CMD ["uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

