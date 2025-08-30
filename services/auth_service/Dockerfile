FROM python:3.10-slim

# 1) Базовые системные утилиты (минимум)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    openssl \
 && rm -rf /var/lib/apt/lists/*

RUN find /app -name "*.pyc" -delete

WORKDIR /app

# 2) Кладём общий пакет common в образ (из корня репо)
#    Build context у тебя — корень, поэтому путь просто "common"
COPY common /app/common

# 3) Копируем только requirements сервиса (для кэша слоёв)
#    Файл лежит рядом с этим Dockerfile: services/auth_service/requirements.txt
COPY services/auth_service/requirements.txt /app/requirements.txt

# 4) Ставим зависимости сервиса
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) Копируем код сервиса (только auth_service)
COPY services/auth_service /app/services/auth_service

# 6) PYTHONPATH, чтобы импортировать общий пакет common.*
ENV PYTHONPATH=/app

# 7) Команда запуска
CMD ["uvicorn", "services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

