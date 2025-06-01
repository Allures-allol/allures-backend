import pytest
from fastapi.testclient import TestClient
from services.auth_service.main import app

client = TestClient(app)

def test_register_and_login():
    # Регистрация нового пользователя
    response = client.post("/auth/register", json={"login": "testuser@example.com", "password": "TestPassword123"})
    assert response.status_code == 200
    assert response.json()["login"] == "testuser@example.com"

    # Попытка логина с правильными данными
    response = client.post("/auth/login", data={"username": "testuser@example.com", "password": "TestPassword123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Попытка логина с неверным паролем
    response = client.post("/auth/login", data={"username": "testuser@example.com", "password": "WrongPassword"})
    assert response.status_code == 400

def test_forgot_password():
    # Отправка запроса на сброс пароля
    response = client.post("/auth/forgot-password", json={"email": "testuser@example.com"})
    assert response.status_code == 200
    assert "Password reset link sent" in response.json()["message"]

def test_reset_password():
    # Установка нового пароля
    response = client.post("/auth/reset-password", json={"email": "testuser@example.com", "new_password": "NewPassword456"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"

    # Логин с новым паролем
    response = client.post("/auth/login", data={"username": "testuser@example.com", "password": "NewPassword456"})
    assert response.status_code == 200
    assert "access_token" in response.json()
