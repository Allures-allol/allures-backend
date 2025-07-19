#!/bin/bash

echo "🔍 Тестируем подключения ко всем сервисам..."

SERVICES=(
  "review_service"
  "discount_service"
  "dashboard_service"
  "subscription_service"
  "admin_service"
)

for SERVICE in "${SERVICES[@]}"
do
  FILE="services/${SERVICE}/test_db_connection.py"
  if [ -f "$FILE" ]; then
    echo "➡️  Тест: $FILE"
    pytest "$FILE"
    echo "------------------------------------------------------"
  else
    echo "⚠️  Файл не найден: $FILE"
  fi
done

echo "✅ Тестирование завершено."
