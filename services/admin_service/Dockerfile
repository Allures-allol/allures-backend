# services/admin_service/Dockerfile

FROM python:3.10-slim

# 1) базовые утилиты
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) общий пакет (для импортов common.*)
COPY common /app/common

# 3) только requirements (лучше кэш слоёв)
COPY services/admin_service/requirements.txt /app/requirements.txt

# 4) зависимости
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 5) код сервиса
COPY services/admin_service /app/services/admin_service

# 6) PYTHONPATH, чтобы импортировать общий пакет common.*
ENV PYTHONPATH=/app

# 7) Команда запуска
CMD ["uvicorn", "services.admin_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
