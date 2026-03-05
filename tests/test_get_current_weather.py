import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from script import app

client = TestClient(app)

class TestGetCurrentWeather:

    # Мокаем функцию
    @patch("routers.get_current_weather.get_current_weather")
    # Успешное получение погоды
    def test_current_weather_success(self, mock_get_weather):
        # Настраиваем мок — что вернёт функция
        mock_get_weather.return_value = {
            "Температура": "15.50",
            "Скорость ветра": "5.20",
            "Атмосферное давление": "1013.25"
        }
        
        # Выполняем запрос
        response = client.get("/weather/current?latitude=55.75&longitude=37.62")
        
        # Проверяем результат
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Температура" in data["data"]
        assert "Скорость ветра" in data["data"]
        assert "Атмосферное давление" in data["data"]
        
        mock_get_weather.assert_called_once()

    # Невалидная широта (больше 90)
    def test_current_weather_invalid_latitude(self):
        response = client.get("/weather/current?latitude=100&longitude=37.62")
        
        assert response.status_code == 422  # Validation Error

    # Тест с невалидной долготой (больше 180)
    def test_current_weather_invalid_longitude(self):
        response = client.get("/weather/current?latitude=55.75&longitude=200")
        
        assert response.status_code == 422

    # Тест без обязательных параметров
    def test_current_weather_missing_params(self):
        response = client.get("/weather/current")
        
        assert response.status_code == 422

    # Тест обработки ошибки от внешнего API
    @patch("routers.get_current_weather.get_current_weather")
    def test_current_weather_api_error(self, mock_get_weather):
        from services.weather_api import WeatherAPIError
        mock_get_weather.side_effect = WeatherAPIError("Connection timeout")
        
        response = client.get("/weather/current?latitude=55.75&longitude=37.62")
        
        assert response.status_code == 404
        assert "Ошибка" in response.json()["detail"]