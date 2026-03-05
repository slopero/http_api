import requests
from typing import List, Dict

from config import (
    API_URL_WEATHER,
    ALL_WEATHER_PARAMS,
)

# Инициализация клиента
client = requests.Session()

class WeatherAPIError(Exception):
    pass

# Функция для поулчения данных с API
def fetch_weather(latitude: float, longitude: float, params: List[str], type_query: str):
    try:
        responses = client.get(API_URL_WEATHER, params={
            "latitude": latitude,
            "longitude": longitude,
            f"{type_query}": params
        })
        data = responses.json()
        return data
    except Exception as e:
        raise WeatherAPIError(f"Ошибка запроса к Open-Meteo: {e}")

# Функция для форматирования ответа
def format_response(response, params: List[str], method: str) -> Dict[str, str]:
    datas_weather = response.get(method)
    results = {}
    
    for param in params:
        value = datas_weather.get(param)
        label = ALL_WEATHER_PARAMS.get(param, param)

        if isinstance(value, list):
            value = value[0] if value else 0

        results[label] = f"{value:.2f}"
    
    return results

# Функция, которая будет вызываться из роутера для получения текущей погоды
def get_current_weather(latitude: float, longitude: float, params: List[str], type_query: str) -> Dict[str, str]:
    response = fetch_weather(latitude, longitude, params, type_query)
    return format_response(response, params, type_query)

# Функция для получения почасовой погоды на указанный час
def get_hourly_weather(latitude: float, longitude: float, params: List[str], hour: int) -> Dict[str, str]:
    try:
        responses = client.get(API_URL_WEATHER, params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": params,
            "forecast_days": 1
        })
        data = responses.json()
        
        hourly_data = data.get("hourly", {})
        results = {}
        
        for param in params:
            values = hourly_data.get(param)
            label = ALL_WEATHER_PARAMS.get(param, param)
            
            if values and len(values) > hour:
                value = values[hour]
                results[label] = f"{value:.2f}" if value is not None else "N/A"
            else:
                results[label] = "N/A"
        
        return results
    except Exception as e:
        raise WeatherAPIError(f"Ошибка запроса к Open-Meteo: {e}")