import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from script import app

client = TestClient(app)

class TestGetListCities:

    # Мокаем функции
    @patch("routers.get_list_cities.user_exists")
    @patch("routers.get_list_cities.get_user_cities")
    # Тест успешного получения списка городов
    def test_all_cities_success(self, mock_get_list, mock_user_exists):
        mock_user_exists.return_value = True
        mock_get_list.return_value = [
            ("Moscow",),
            ("Tomsk",)
        ]

        response = client.get("/cities/city?id_user=1")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        mock_get_list.assert_called_once_with(1)

    # Тест без параметра id_user
    def test_all_cities_missing_id_user(self):
        response = client.get("/weather/city")

        assert response.status_code == 422

    # Тест с несуществующим id_user
    @patch("routers.get_list_cities.user_exists")
    def test_all_cities_nonexist_id_user(self, mock_user_exists):
        mock_user_exists.return_value = False

        response = client.get("/cities/city?id_user=999")

        assert response.status_code == 404
        mock_user_exists.assert_called_once_with(999)

    # Тест ошибка записи в БД
    @patch("routers.get_list_cities.user_exists")
    @patch("routers.get_list_cities.get_user_cities")
    def test_all_cities_db_error(self, mock_get_list, mock_user_exists):
        mock_user_exists.return_value = True
        mock_get_list.side_effect = Exception("Ошибка доступа к базе данных")

        response = client.get("/cities/city?id_user=1")

        assert response.status_code == 404
        data = response.json()
        assert "Ошибка" in data["detail"]

        mock_get_list.assert_called_once_with(1)