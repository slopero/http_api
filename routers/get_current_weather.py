from fastapi import APIRouter, HTTPException, Query
from services.weather_api import get_current_weather, WeatherAPIError
from config import METHOD_CURRENT_PARAMS

router = APIRouter()

@router.get("/current")
def current_weather(
    latitude: float = Query(..., description="Широта", ge=-90.0, le=90.0),
    longitude: float = Query(..., description="Долгота", ge=-180.0, le=180.0),
):
    method = "current"
    params = list(METHOD_CURRENT_PARAMS)
    try:
        data = get_current_weather(latitude, longitude, params, method)
    except WeatherAPIError as e:
        raise HTTPException(404, f"Ошибка {e}")
    
    return {"status": "success", "data": data}