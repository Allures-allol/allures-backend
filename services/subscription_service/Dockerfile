FROM python:3.10-slim

# 1) Базовые утилиты (TLS и т.п.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Кладём общий пакет (если используется импорт common.*)
COPY common /app/common

# 3) Кэшируем зависимости
COPY services/subscription_service/requirements.txt /app/requirements.txt

# 4) Устанавливаем зависимости
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) Копируем код сервиса
COPY services/subscription_service /app/services/subscription_service

# 6) PYTHONPATH, чтобы видеть /app (а значит и /app/common как пакет)
ENV PYTHONPATH=/app

EXPOSE 8000

# 7) Запуск
CMD ["uvicorn", "services.subscription_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

