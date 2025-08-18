FROM python:3.10-slim

# минимальные системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# общий код (нужен доступ к common.*)
COPY common /app/common
WORKDIR /app

<<<<<<< Updated upstream
# Копируем common
COPY common /app/common

# Копируем requirements и ставим зависимости
COPY services/review_service/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
        libpq-dev \
        apt-transport-https \
        ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем **только каталог review_service**, чтобы структура была как в других сервисах
COPY services/review_service /app/services/review_service

# PYTHONPATH
ENV PYTHONPATH=/app

# Порт и запуск
EXPOSE 8008
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8008"]
=======
# зависимости сервиса (prod)
COPY services/review_service/requirements.txt /app/requirements.txt
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# код сервиса
COPY services/review_service /app/services/review_service

# NLTK датасеты в образ
ENV PYTHONPATH=/app
ENV NLTK_DATA=/app/services/review_service/sentiment/nltk_data
RUN python -c "import os; os.makedirs('${NLTK_DATA}', exist_ok=True); "\
"import nltk; nltk.download('punkt', download_dir='${NLTK_DATA}'); "\
"nltk.download('wordnet', download_dir='${NLTK_DATA}')"
>>>>>>> Stashed changes

EXPOSE 8000
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
