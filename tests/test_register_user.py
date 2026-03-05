import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from script import app

client = TestClient(app)


class TestRegisterUser:

    # Мокаем функции
    @patch("routers.register_user.user_exists")
    @patch("routers.register_user.get_user_id")
    # Тест успешной регистрации пользователя
    def test_register_user_success(self, mock_get_user_id, mock_user_exists):
        mock_get_user_id.return_value = 1
        mock_user_exists.return_value = True

        response = client.post("/users/id_user?login=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_id"] == 1

        mock_get_user_id.assert_called_once_with("test_user")

    @patch("routers.register_user.user_exists")
    @patch("routers.register_user.get_user_id")
    # Тест получения ID существующего пользователя
    def test_register_user_returns_existing_id(self, mock_get_user_id, mock_user_exists):
        mock_get_user_id.return_value = 5
        mock_user_exists.return_value = True

        response = client.post("/users/id_user?login=existing_user")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 5

    # Тест без параметра login
    def test_register_user_missing_login(self):
        response = client.post("/users/id_user")

        assert response.status_code == 422

    @patch("routers.register_user.get_user_id")
    @patch("routers.register_user.user_exists")
    # Тест ошибки при работе с БД
    def test_register_user_db_error(self, mock_user_exists, mock_get_user_id):
        mock_get_user_id.side_effect = Exception("Database connection failed")

        response = client.post("/users/id_user?login=test_user")

        assert response.status_code == 500
        assert "Ошибка" in response.json()["detail"]

