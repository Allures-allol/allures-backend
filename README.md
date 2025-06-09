# 🛍️ Allures&Allol Marketplace Backend

Welcome to the backend system for **Allures&Allol** — a FastAPI-based modular marketplace platform built on microservices, powered by MSSQL, and containerized with Docker.

## 🧱 Project Structure

- `services/`
  - `product_service/` – управление товарами и категориями
  - `sales_service/` – управление продажами и аналитикой
  - `review_service/` – управление отзывами и рекомендациями
  - `auth_service/` – регистрация, авторизация, управление доступом
  - `discount_service/` – управление скидками и акциями
  - `payment_service/` – создание и обработка платежей (включая Webhook)
  - `profile_service/` – профили пользователей, компании и расширенная информация
- `common/` – общие модули, модели, enum-категории, сессии БД
- `.env.example` – переменные окружения (без секретов)
- `docker-compose*.yml` – сборка и запуск сервисов

## 🚀 Быстрый запуск

```bash
docker-compose up --build -d
```

📦 Swagger-документация API:

- [Product Service](http://localhost:8000/docs)
- [Sales Service](http://localhost:8001/docs)
- [Review Service](http://localhost:8002/docs)
- [Authorization Service](http://localhost:8003/docs)
- [Profile Service](http://localhost:8004/docs)
- [Payment Service](http://localhost:8005/docs)
- [Discount Service](http://localhost:8006/docs)

## 🔐 Authorization Service Endpoints

| Метод | URL             | Описание                                  |
|-------|------------------|-------------------------------------------|
| POST  | `/auth/register` | Регистрация пользователя                 |
| POST  | `/auth/login`    | Вход пользователя                        |
| POST  | `/auth/forgot-password` | Запрос на сброс пароля         |
| POST  | `/auth/reset-password` | Установка нового пароля          |
| GET   | `/auth/users`    | Получение списка всех пользователей      |

## 🏷️ Discount Service

Управление акциями и скидками.

| Метод | URL         | Описание                       |
|-------|-------------|--------------------------------|
| GET   | `/discount/` | Получить список активных скидок |
| POST  | `/discount/` | Создать новую скидку            |

Пример тела запроса:
```json
{
  "code": "NEWYEAR2026",
  "percentage": 18.0,
  "valid_until": "2026-01-01T00:00:00"
}
```

## 📦 Используемые технологии

- FastAPI & Pydantic
- MSSQL + SQLAlchemy
- Docker & Docker Compose
- Uvicorn
- dotenv

## 💡 Рекомендации

- Добавить автоматическую деактивацию скидок с истекшим сроком.
- Привязка скидок к пользователям и заказам.
- Добавить проверку промокодов.
- Интеграция с системой оплаты и подписок.

## 📚 License

MIT License.