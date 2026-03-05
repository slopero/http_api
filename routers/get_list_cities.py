from fastapi import APIRouter, Query, HTTPException
from services.work_with_db import get_user_cities, user_exists
from typing import List

router = APIRouter()

# Получение списка всех городов, для которых отслеживается погода
@router.get("/city")
def all_cities(
    id_user: int = Query(..., description="ID пользователя")
) -> List:
    user_exist = user_exists(id_user)
    if not user_exist:
        raise HTTPException(404, f"Пользователь с id_user = {id_user} не найден")
    list_cities = []
    try:
        data = get_user_cities(id_user)
        if not data:
            list_cities.append("Нет отслеживаемых городов")
        else:
            for city in data:
                list_cities.append(city[0])
        return list_cities
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))