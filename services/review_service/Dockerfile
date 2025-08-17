FROM python:3.10-slim

WORKDIR /app

# Копируем common
COPY common /app/common

# Копируем requirements и ставим зависимости
COPY services/review_service/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
        libpq-dev \
        apt-transport-https \
        ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем **только каталог review_service**, чтобы структура была как в других сервисах
COPY services/review_service /app/services/review_service

# PYTHONPATH
ENV PYTHONPATH=/app

# Порт и запуск
EXPOSE 8008
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8008"]

