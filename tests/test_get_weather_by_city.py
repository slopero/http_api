import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from script import app

client = TestClient(app)

class TestWeatherByCity:
     
    # Мокаем функции
    @patch("routers.insert_city_in_db.add_city_user")
    @patch("routers.insert_city_in_db.add_weather_city")
    @patch("routers.insert_city_in_db.get_current_weather")
    @patch("routers.insert_city_in_db.user_exists")
    # Тест успешного получения погоды
    def test_weather_by_city_success(self, mock_user_exists, mock_get_weather, mock_add_weather, mock_add_city):
        mock_user_exists.return_value = True
        mock_get_weather.return_value = {
            "Температура": "15.50",
            "Скорость ветра": "5.20",
            "Атмосферное давление": "1013.25"
        }

        response = client.get("/weather/city?city=Moscow&latitude=55.75&longitude=37.62&id_user=1")

        # Проверка результата

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        mock_get_weather.assert_called_once()

        mock_add_weather.assert_called_once_with(
            "Moscow", 55.75, 37.62, "15.50", "5.20", "1013.25"
        )

        mock_add_city.assert_called_once_with(1, "Moscow")

    # Тест с пустым значением города
    def test_null_city(self):
        response = client.get("/weather/city?latitude=55.75&longitude=37.62&id_user=1")

        assert response.status_code == 422

    # Тест без параметра id_user
    def test_none_id_user(self):
        response = client.get(
            "/weather/city?city=Moscow&latitude=55.75&longitude=37.62"
        )

        assert response.status_code == 422

    @patch("routers.insert_city_in_db.add_city_user")
    @patch("routers.insert_city_in_db.add_weather_city")
    @patch("routers.insert_city_in_db.get_current_weather")
    @patch("routers.insert_city_in_db.user_exists")
    # Тест обработки ошибки от внешнего API
    def test_weather_by_city_api_error(self, mock_user_exists, mock_get_weather, mock_add_weather, mock_add_city_user):
        mock_user_exists.return_value = True
        mock_get_weather.side_effect = Exception("API недоступен")
        
        response = client.get(
            "/weather/city?city=Москва&latitude=55.75&longitude=37.62&id_user=1"
        )
        
        assert response.status_code == 404
        # Функции БД не должны вызываться при ошибке API
        mock_add_weather.assert_not_called()
        mock_add_city_user.assert_not_called()

    @patch("routers.insert_city_in_db.add_city_user")
    @patch("routers.insert_city_in_db.add_weather_city")
    @patch("routers.insert_city_in_db.get_current_weather")
    @patch("routers.insert_city_in_db.user_exists")
    # Тест ошибки при записи в БД
    def test_weather_by_city_db_error(self, mock_user_exists, mock_get_weather, mock_add_weather, mock_add_city_user):
        mock_user_exists.return_value = True
        mock_get_weather.return_value = {
            "Температура": "15.50",
            "Скорость ветра": "5.20",
            "Атмосферное давление": "1013.25"
        }
        mock_add_weather.side_effect = Exception("Ошибка БД")
        
        response = client.get(
            "/weather/city?city=Москва&latitude=55.75&longitude=37.62&id_user=1"
        )
        
        assert response.status_code == 404