FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# общий код
COPY common /app/common

# зависимости сервиса
COPY services/profile_service/requirements.txt /app/requirements.txt

ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# код сервиса
COPY services/profile_service /app/services/profile_service

# видеть /app и /app/common
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "services.profile_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

