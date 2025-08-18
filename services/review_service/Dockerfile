FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY common /app/common
WORKDIR /app
COPY services/review_service/requirements.txt /app/requirements.txt
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt
COPY services/review_service /app/services/review_service
ENV PYTHONPATH=/app
ENV NLTK_DATA=/app/services/review_service/sentiment/nltk_data
RUN python -c "import os; os.makedirs('', exist_ok=True); import nltk; nltk.download('punkt', download_dir=''); nltk.download('wordnet', download_dir='')"
EXPOSE 8000
CMD ["uvicorn", "services.review_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
