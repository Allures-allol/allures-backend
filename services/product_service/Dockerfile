FROM python:3.10-slim

# 1) Базовые утилиты (TLS для httpx/psycopg2 через SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Кладём общий пакет common (важно для импортов common.*)
COPY common /app/common

# 3) Копируем только requirements сервиса (для кэширования слоёв)
COPY services/product_service/requirements.txt /app/requirements.txt

# 4) Ставим зависимости
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) Копируем код сервиса (только product_service)
COPY services/product_service /app/services/product_service

# 6) PYTHONPATH, чтобы видеть /app и /app/common
ENV PYTHONPATH=/app

EXPOSE 8000

# 7) Команда запуска
CMD ["uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
