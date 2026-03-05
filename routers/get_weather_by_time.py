from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.weather_api import get_hourly_weather, WeatherAPIError
from services.work_with_db import get_city_coordinates
from services.work_with_db import user_exists
from config import METHOD_HOURLY_PARAMS

router = APIRouter()

@router.get("/time")
def weather_by_time(
    city: str = Query(..., description="Название города"),
    hour: int = Query(..., description="Час (0-23)", ge=0, le=23),
    temperature: Optional[bool] = Query(False, description="Включить температуру"),
    humidity: Optional[bool] = Query(False, description="Включить влажность"),
    wind_speed: Optional[bool] = Query(False, description="Включить скорость ветра"),
    precipitation: Optional[bool] = Query(False, description="Включить осадки"),
    id_user: int = Query(..., description="ID пользователя")
):
    user_exist = user_exists(id_user)
    if not user_exist:
        raise HTTPException(404, f"Пользователь с id_user = {id_user} не найден")
    # Получаем координаты города из БД (только если город привязан к пользователю)
    coordinates = get_city_coordinates(city, id_user)
    if coordinates is None: 
        raise HTTPException(404, f"Город '{city}' не найден в списке отслеживаемых городов пользователя")
    
    latitude, longitude = coordinates
    
    # Собираем запрошенные параметры
    params = []
    if temperature:
        params.append("temperature_2m")
    if humidity:
        params.append("relative_humidity_2m")
    if wind_speed:
        params.append("wind_speed_10m")
    if precipitation:
        params.append("precipitation")
    
    # Если ничего не выбрано - возвращаем все параметры
    if not params:
        params = list(METHOD_HOURLY_PARAMS)
    
    try:
        data = get_hourly_weather(latitude, longitude, params, hour)
        
    except WeatherAPIError as e:
        raise HTTPException(500, f"Ошибка получения погоды: {e}")
    
    return {
        "data": data
    }
