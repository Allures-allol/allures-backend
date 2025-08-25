
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# общий код
COPY common /app/common

# зависимости сервиса
COPY services/product_service/requirements.txt /app/requirements.txt
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# код сервиса
COPY services/product_service /app/services/product_service

# PYTHONPATH видит и /app, и /app/common
ENV PYTHONPATH=/app:/app/common

CMD ["uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

