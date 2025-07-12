import pytest
from fastapi.testclient import TestClient
from services.auth_service.main import app

client = TestClient(app)

def test_register_and_login():
    # Регистрация нового пользователя
    register_data = {
        "login": "testuser@example.com",
        "password": "TestPassword123"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    assert response.json()["login"] == register_data["login"]

    # Попытка логина с правильными данными (теперь через JSON)
    login_data = {
        "login": "testuser@example.com",
        "password": "TestPassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Попытка логина с неверным паролем
    wrong_login = {
        "login": "testuser@example.com",
        "password": "WrongPassword"
    }
    response = client.post("/auth/login", json=wrong_login)
    assert response.status_code == 401 or response.status_code == 400

def test_forgot_password():
    # Отправка запроса на сброс пароля
    response = client.post("/auth/forgot-password", json={"email": "testuser@example.com"})
    assert response.status_code == 200
    assert "лист" in response.json()["message"].lower()  # Ukrainian: "Лист для скидання пароля..."

def test_reset_password():
    # Установка нового пароля
    response = client.post("/auth/reset-password", json={
        "email": "testuser@example.com",
        "new_password": "NewPassword456"
    })
    assert response.status_code == 200
    assert "успішно" in response.json()["message"].lower()

    # Логин с новым паролем
    login_data = {
        "login": "testuser@example.com",
        "password": "NewPassword456"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
