# Используем официальный образ Python 3.10 (slim)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

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

COPY . .

ENV PYTHONPATH=/app:/app/common

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


