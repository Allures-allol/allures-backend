# services/admin_service/Dockerfile
FROM python:3.10-slim

# 1) Минимум системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Общий пакет common (для импортов common.*)
COPY common /app/common

# 3) Только requirements сервиса (лучше кэш слоёв)
COPY services/admin_service/requirements.txt /app/requirements.txt

# 4) Зависимости
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) Код сервиса
COPY services/admin_service /app/services/admin_service

# 6) PYTHONPATH, чтобы видеть /app и /app/common
ENV PYTHONPATH=/app

# (опционально) EXPOSE — для документации
EXPOSE 8000

# 7) Команда запуска
CMD ["uvicorn", "services.admin_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
