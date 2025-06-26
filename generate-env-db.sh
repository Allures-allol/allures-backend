#!/usr/bin/env bash

TEMPLATE_FILE="services/product_service/.env"
SERVICES=( "auth_service" "dashboard_service" "discount_service" "payment_service" "profile_service" "review_service" "sales_service")

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "❌ Шаблонный файл $TEMPLATE_FILE не найден. Сначала убедись, что он существует."
  exit 1
fi

for SERVICE in "${SERVICES[@]}"; do
  TARGET_FILE="services/${SERVICE}/.env"
  if [ -f "$TARGET_FILE" ]; then
    echo "✅ Уже существует: $TARGET_FILE"
  else
    cp "$TEMPLATE_FILE" "$TARGET_FILE"
    echo "📄 Создан: $TARGET_FILE"
  fi
done

echo "🚀 Все env-файлы готовы!"
