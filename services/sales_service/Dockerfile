FROM python:3.10-slim

WORKDIR /app

# Установим системные зависимости сразу
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        unixodbc \
        unixodbc-dev \
        curl \
        gnupg2 \
        apt-transport-https \
        ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app:/app/common

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
