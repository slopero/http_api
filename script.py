import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import get_current_weather as current_weather
from routers import insert_city_in_db
from routers import get_list_cities
from routers import get_weather_by_time
from routers import register_user
from services.work_with_db import get_all_cities, update_weather, init_db
from services.weather_api import get_current_weather
from config import METHOD_CURRENT_PARAMS

# Обновление погоды каждые 15 минут для всех городов в базе данных
async def update_weather_data():
    while True:
        cities = get_all_cities()
        for city, latitude, longitude in cities:
            try:
                params = METHOD_CURRENT_PARAMS
                type_query = "current"
                data = get_current_weather(latitude, longitude, params, type_query)
                update_weather(city, float(data["Температура"]), float(data["Скорость ветра"]), float(data["Атмосферное давление"]))
            except Exception as e:
                print(f"Ошибка обновления : {e}")
        await asyncio.sleep(15*60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(update_weather_data())
    yield
    task.cancel()

app = FastAPI(title="Weather API Server", lifespan=lifespan)

app.include_router(current_weather.router, prefix="/weather", tags=["weather"])
app.include_router(insert_city_in_db.router, prefix="/weather", tags=["weather"])
app.include_router(get_weather_by_time.router, prefix="/weather", tags=["weather"])
app.include_router(get_list_cities.router, prefix="/cities", tags=["cities"])
app.include_router(register_user.router, prefix="/users", tags=["users"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)