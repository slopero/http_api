import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Data/weather_data.db")

API_URL_WEATHER = "https://api.open-meteo.com/v1/forecast"

ALL_WEATHER_PARAMS = {
    "temperature_2m" : "Температура", 
    "wind_speed_10m" : "Скорость ветра", 
    "surface_pressure" : "Атмосферное давление", 
    "precipitation" : "Осадки", 
    "relative_humidity_2m" : "Влажность"
}

# Параметры для методов 1 и 4
METHOD_CURRENT_PARAMS = {"temperature_2m", "wind_speed_10m", "surface_pressure"}

METHOD_HOURLY_PARAMS = {"temperature_2m", "wind_speed_10m", "precipitation", "relative_humidity_2m"}