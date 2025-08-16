FROM python:3.10-slim

WORKDIR /app

# 1. Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
        libpq-dev \
        apt-transport-https \
        ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Копируем requirements.txt
COPY requirements.txt .

# 3. Устанавливаем Python-зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# 4. Копируем и устанавливаем общий пакет common
COPY ../../common ./common
RUN pip install -e ./common

# 5. Копируем код самого сервиса
COPY . .

# 6. Настройка PYTHONPATH
ENV PYTHONPATH=/app

# 7. Запуск uvicorn
CMD ["uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]


