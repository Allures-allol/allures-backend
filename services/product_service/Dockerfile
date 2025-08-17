FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# зависимости только для product_service
COPY services/product_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# весь проект (нужен доступ к /common)
COPY . .

ENV PYTHONPATH=/app:/app/common

EXPOSE 8000

CMD ["uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
