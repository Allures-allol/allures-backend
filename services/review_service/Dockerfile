# Используем официальный образ Python 3.10 (slim)
FROM python:3.10-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем requirements и ставим зависимости
COPY services/review_service/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Устанавливаем системные зависимости
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

# Копируем весь каталог конкретного сервиса
COPY services/review_service ./services/review_service

# Если есть общие модули
COPY common ./common

# Настраиваем PYTHONPATH для корректных импортов
ENV PYTHONPATH=/app:/app/common

# Экспорт порта
EXPOSE 8008

# Команда запуска
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8008"]

