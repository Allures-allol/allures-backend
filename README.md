
# Allures&Allol Marketplace Backend

Allures&Allol — модульная система backend для маркетплейса, построенная на FastAPI с архитектурой микросервисов. Используется PostgreSQL (Supabase), Docker и современный Python-стек.

## Структура проекта

```
├── services/
│   ├── product_service/        # Управление товарами и категориями
│   ├── sales_service/          # Продажи и аналитика
│   ├── review_service/         # Отзывы и рекомендации (AI, NLP)
│   ├── auth_service/           # Регистрация, авторизация, токены
│   ├── profile_service/        # Профили пользователей и компаний
│   ├── payment_service/        # Платежи и Webhook NowPayments
│   ├── discount_service/       # Скидки, промокоды, валидаторы
│   ├── subscription_service/   # Подписки: free / plus / premium
│   ├── dashboard_service/      # Кабинет пользователя и аналитика
│   └── admin_service/          # Администрирование
├── common/                     # Общие модели, enum, схемы, utils
├── .env                        # Настройки окружения
├── docker-compose.yml          # Подключение всех сервисов
├── start.sh / manage.py        # Скрипты управления
```

## Быстрый запуск

```bash
docker-compose up --build -d
```

> Убедитесь, что в `.env` указаны корректные строки подключения к PostgreSQL или Supabase и адреса сервисов.

## Swagger UI

| Сервис         | Swagger URL                |
|----------------|-----------------------------|
| Product        | http://localhost:8000/docs  |
| Sales          | http://localhost:8001/docs  |
| Review         | http://localhost:8002/docs  |
| Auth           | http://localhost:8003/docs  |
| Profile        | http://localhost:8004/docs  |
| Payment        | http://localhost:8005/docs  |
| Discount       | http://localhost:8006/docs  |
| Dashboard      | http://localhost:8007/docs  |
| Admin          | http://localhost:8010/docs  |
| Subscription   | http://localhost:8011/docs  |

## Примеры эндпоинтов

### Auth Service

| Метод | URL                      | Описание                        |
|-------|--------------------------|----------------------------------|
| POST  | `/auth/register`         | Регистрация пользователя         |
| POST  | `/auth/login`            | Вход и JWT-токен                 |
| POST  | `/auth/forgot-password`  | Запрос на сброс пароля           |
| POST  | `/auth/reset-password`   | Новый пароль                     |
| GET   | `/auth/users`            | Список всех пользователей        |

### Discount Service

| Метод | URL         | Описание                       |
|-------|-------------|--------------------------------|
| GET   | `/discount/` | Получить список активных скидок |
| POST  | `/discount/` | Создать новую скидку            |

Пример POST-запроса:

```json
{
  "code": "NEWYEAR2026",
  "percentage": 18.0,
  "valid_until": "2026-01-01T00:00:00"
}
```

## Review & Recommendation

- Анализ тональности отзывов (NLTK)
- AI-модуль рекомендаций на основе ключевых слов
- Поддержка расширенного GPT-анализатора

## Subscription Service

- Free: базовый функционал, ограниченный доступ
- Plus: расширенные возможности
- Premium: полная версия без ограничений

## Используемые технологии

- FastAPI, Pydantic
- SQLAlchemy, PostgreSQL (Supabase)
- Docker, Docker Compose
- Uvicorn, Gunicorn, Nginx
- Pytest, dotenv
- OpenAI, NLTK, Tesseract

## Рекомендации по доработке

- Планировщик очистки неактивных скидок
- Графики и статистика в dashboard_service
- WebSocket API для уведомлений и чатов
- Расширенные тесты (unit + integration)
- Интеграция с Stripe / PayPal / Mono

## License

Проект распространяется под лицензией MIT.


---

# Allures&Allol Marketplace Backend (EN)

Allures&Allol is a modular backend system for a marketplace platform, powered by FastAPI and PostgreSQL (Supabase), with microservice architecture and Docker containerization.

## Project Structure

```
├── services/
│   ├── product_service/        # Product and category management
│   ├── sales_service/          # Sales and analytics
│   ├── review_service/         # Reviews and AI-based recommendations
│   ├── auth_service/           # Authentication, registration, JWT
│   ├── profile_service/        # User and company profiles
│   ├── payment_service/        # Payments and NowPayments webhook
│   ├── discount_service/       # Discounts, coupons, validation
│   ├── subscription_service/   # Subscription plans: free / plus / premium
│   ├── dashboard_service/      # User dashboard and analytics
│   └── admin_service/          # Admin management
├── common/                     # Shared models, enums, schemas, utilities
├── .env                        # Environment variables
├── docker-compose.yml          # Service orchestration
├── start.sh / manage.py        # Management scripts
```

## Quick Start

```bash
docker-compose up --build -d
```

## API Docs (Swagger UI)

Access each service's Swagger UI:

- Product:       http://localhost:8000/docs
- Sales:         http://localhost:8001/docs
- Review:        http://localhost:8002/docs
- Auth:          http://localhost:8003/docs
- Profile:       http://localhost:8004/docs
- Payment:       http://localhost:8005/docs
- Discount:      http://localhost:8006/docs
- Dashboard:     http://localhost:8007/docs
- Admin:         http://localhost:8010/docs
- Subscription:  http://localhost:8011/docs

## Example Endpoints

### Auth Service

| Method | Endpoint                 | Description                 |
|--------|--------------------------|-----------------------------|
| POST   | `/auth/register`         | Register new user           |
| POST   | `/auth/login`            | Login with JWT token        |
| POST   | `/auth/forgot-password`  | Request password reset link |
| POST   | `/auth/reset-password`   | Reset password              |
| GET    | `/auth/users`            | List all users              |

### Discount Service

| Method | Endpoint     | Description                  |
|--------|--------------|------------------------------|
| GET    | `/discount/` | Get list of active discounts |
| POST   | `/discount/` | Create a new discount        |

Example POST body:

```json
{
  "code": "NEWYEAR2026",
  "percentage": 18.0,
  "valid_until": "2026-01-01T00:00:00"
}
```

## Features

- Review sentiment analysis with NLTK
- Recommendation engine based on keywords
- GPT-based advanced recommendations
- Flexible subscription system

## Stack

- FastAPI + Pydantic
- SQLAlchemy + PostgreSQL
- Docker & Docker Compose
- Nginx + Gunicorn + Uvicorn
- dotenv, Pytest, OpenAI, Tesseract

## Improvements Roadmap

- Auto-expire discounts with a scheduler
- Admin dashboard with full analytics
- Add Stripe/PayPal integration
- Real-time updates with WebSocket
- Full test coverage

## License

MIT License.
