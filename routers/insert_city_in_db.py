from fastapi import APIRouter, HTTPException, Query
from services.weather_api import get_current_weather
from config import METHOD_CURRENT_PARAMS
from services.work_with_db import add_weather_city, add_city_user, user_exists

router = APIRouter()

@router.get("/city")
def insert_city(
    city: str = Query(..., description="Название города"),
    latitude: float = Query(..., description="Широта"),
    longitude: float = Query(..., description="Долгота"),
    id_user: int = Query(..., description="ID пользователя")
):
    try:
        user_exist = user_exists(id_user)
    except Exception as e:
        raise HTTPException(404, f"Ошибка {e}")
    if not user_exist:
        raise HTTPException(404, f"Пользователь с id_user = {id_user} не найден")
    try:
        params = METHOD_CURRENT_PARAMS
        type_query = "current"
        data = get_current_weather(latitude, longitude, params, type_query)
        data["Город"] = city
        add_weather_city(city, latitude, longitude, data["Температура"], data["Скорость ветра"], data["Атмосферное давление"])
        add_city_user(id_user, city)
    except Exception as e:
        raise HTTPException(404, f"Ошибка {e}")
    
    return {"status": "success"}