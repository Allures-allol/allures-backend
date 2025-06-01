
# 🛍️ Allures&Allol Marketplace Backend

Welcome to the backend system for **Allures&Allol** — a FastAPI-based modular marketplace platform built on microservices, powered by MSSQL, and containerized with Docker.

## 🧱 Project Structure

- `services/`
  - `product_service/` – управление товарами и категориями
  - `sales_service/` – управление продажами и аналитикой
  - `review_service/` – управление отзывами и рекомендациями
  - `auth_service/` – регистрация, авторизация, управление доступом
- `common/` – общие модули, модели, enum-категории, сессии БД
- `.env` – конфигурация подключения к базе
- `docker-compose.yml` – полный запуск всех сервисов
- `docker-compose-*.yml` – индивидуальные сборки

## 🚀 Быстрый запуск

```bash
docker-compose up --build -d
```

📦 Документация API:

- [Product Service Swagger UI](http://localhost:8000/docs)
- [Sales Service Swagger UI](http://localhost:8001/docs)
- [Review Service Swagger UI](http://localhost:8002/docs)
- [Authorization Service Swagger UI](http://localhost:8003/docs)

## ⚙️ Настройки среды

### `.env.review`

```env
# Отдельная БД для отзывов (если требуется)
LOCAL_DB_URL=mssql+pyodbc://sa:${MSSQL_SA_PASSWORD}@mssql-db:1433/ReviewDb?driver=ODBC+Driver+17+for+SQL+Server
```

### `.env`

```env
# Основная база
ALLURES_DB_URL=mssql+pyodbc://sa:${MSSQL_SA_PASSWORD}@mssql-db:1433/AlluresDb?driver=ODBC+Driver+17+for+SQL+Server
```

### `.env.example`

```env
# MSSQL connection
MSSQL_SA_PASSWORD=YourStrongPasswordHere
MSSQL_HOST=mssql-db
MSSQL_PORT=1433

# Основная база
ALLURES_DB_URL=mssql+pyodbc://sa:${MSSQL_SA_PASSWORD}@mssql-db:1433/AlluresDb?driver=ODBC+Driver+17+for+SQL+Server

# Отдельная БД для отзывов (если требуется)
LOCAL_DB_URL=mssql+pyodbc://sa:${MSSQL_SA_PASSWORD}@mssql-db:1433/ReviewDb?driver=ODBC+Driver+17+for+SQL+Server
```

## 🔒 Authorization Service Endpoints

| Метод | URL             | Описание                                  | Тело запроса                |
|-------|------------------|-------------------------------------------|-----------------------------|
| POST  | `/auth/register` | Регистрация пользователя                 | `{ login, password }`       |
| POST  | `/auth/login`    | Вход пользователя                        | `username`, `password` (x-www-form-urlencoded) |
| POST  | `/auth/forgot-password` | Запрос на сброс пароля         | `{ email }`                 |
| POST  | `/auth/reset-password` | Установка нового пароля          | `{ email, new_password }`   |
| GET   | `/auth/users`    | Получение списка всех пользователей      | -                           |

## 🔧 Возможности расширения

- Сервис скидок и акций
- Авторизация и управление правами доступа (auth_service)
- Мультиязычность (i18n)
- Модуль прогнозной аналитики

## 📦 Используемые технологии

- FastAPI
- MSSQL + SQLAlchemy
- Docker & Docker Compose
- pyodbc
- Pydantic
- Uvicorn
- dotenv

## 📚 Лицензия

Проект распространяется под лицензией [MIT](./LICENSE).
