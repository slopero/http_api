import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from script import app

client = TestClient(app)

class TestGetWeatherTime:

    @patch("routers.get_weather_by_time.get_hourly_weather")
    @patch("routers.get_weather_by_time.get_city_coordinates")
    # Тест успешного получения погоды по времени
    def test_weather_by_time(self, mock_get_coordinates, mock_get_hourly):
        mock_get_coordinates.return_value = (55.75, 37.62)
        mock_get_hourly.return_value = {
            "temperature_2m": "15.50",
            "relative_humidity_2m": "60",
            "wind_speed_10m": "5.20",
            "precipitation": "0.00"
        }

        response = client.get("/weather/time?city=Moscow&hour=14&temperature=true&humidity=true&wind_speed=true&precipitation=true&id_user=1")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["temperature_2m"] == "15.50"
        assert data["data"]["relative_humidity_2m"] == "60"
        assert data["data"]["wind_speed_10m"] == "5.20"
        assert data["data"]["precipitation"] == "0.00"
        mock_get_coordinates.assert_called_once_with("Moscow", 1)

    @patch("routers.get_weather_by_time.get_city_coordinates")
    # Тест когда город не найден в БД пользователя
    def test_weather_by_time_city_not_found(self, mock_get_coords):
        mock_get_coords.return_value = None

        response = client.get(
            "/weather/time?city=НесуществующийГород&hour=12&id_user=1"
        )

        assert response.status_code == 404
        assert "не найден" in response.json()["detail"]

    # Тест с невалидным часом (больше 23)
    def test_weather_by_time_invalid_hour_too_high(self):
        response = client.get(
            "/weather/time?city=Москва&hour=25&id_user=1"
        )

        assert response.status_code == 422

    # Тест с отрицательным часом
    def test_weather_by_time_invalid_hour_negative(self):
        response = client.get(
            "/weather/time?city=Москва&hour=-1&id_user=1"
        )

        assert response.status_code == 422

    # Тест без параметра city
    def test_weather_by_time_missing_city(self):
        response = client.get(
            "/weather/time?hour=12&id_user=1"
        )

        assert response.status_code == 422

    # Тест без параметра hour
    def test_weather_by_time_missing_hour(self):
        response = client.get(
            "/weather/time?city=Москва&id_user=1"
        )

        assert response.status_code == 422

    # Тест без параметра id_user
    def test_weather_by_time_missing_id_user(self):
        response = client.get(
            "/weather/time?city=Москва&hour=12"
        )

        assert response.status_code == 422

    @patch("routers.get_weather_by_time.get_hourly_weather")
    @patch("routers.get_weather_by_time.get_city_coordinates")
    # Тест ошибки при запросе к API погоды
    def test_weather_by_time_api_error(self, mock_get_coords, mock_get_weather):
        from services.weather_api import WeatherAPIError
        mock_get_coords.return_value = (55.75, 37.62)
        mock_get_weather.side_effect = WeatherAPIError("API недоступен")

        response = client.get(
            "/weather/time?city=Москва&hour=12&id_user=1"
        )

        assert response.status_code == 500
        assert "Ошибка" in response.json()["detail"]

    @patch("routers.get_weather_by_time.get_hourly_weather")
    @patch("routers.get_weather_by_time.get_city_coordinates")
    # Тест без выбора параметров (должны вернуться все)
    def test_weather_by_time_default_params(self, mock_get_coords, mock_get_weather):
        mock_get_coords.return_value = (55.75, 37.62)
        mock_get_weather.return_value = {
            "Температура": "15.50",
            "Влажность": "65.00"
        }

        response = client.get(
            "/weather/time?city=Москва&hour=12&id_user=1"
        )

        assert response.status_code == 200
        # Проверяем что вызов был с параметрами из METHOD_HOURLY_PARAMS
        mock_get_weather.assert_called_once()