FROM python:3.10-slim

# минимальные системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# общий код (нужен доступ к common.*)
COPY common /app/common
WORKDIR /app

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
RUN python -c "import os; os.makedirs('${NLTK_DATA}', exist_ok=True); import nltk; "\
"nltk.download('punkt', download_dir='${NLTK_DATA}'); "\
"nltk.download('wordnet', download_dir='${NLTK_DATA}')"

EXPOSE 8000
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
