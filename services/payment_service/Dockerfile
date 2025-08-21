FROM python:3.10-slim

# 1) Базовые утилиты (TLS-сертификаты для httpx/psycopg2 по SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Кладём общий пакет common (важно для импортов common.*)
COPY common /app/common

# 3) Копируем requirements сервиса (для кэширования слоёв)
COPY services/payment_service/requirements.txt /app/requirements.txt

# 4) Ставим зависимости
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) Копируем код сервиса (только payment_service)
COPY services/payment_service /app/services/payment_service

# 6) PYTHONPATH, чтобы видеть /app и /app/common
ENV PYTHONPATH=/app

EXPOSE 8000

# 7) Команда запуска (root_path="/payment" уже в приложении)
CMD ["uvicorn", "services.payment_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
