from services.work_with_db import get_user_id, user_exists, add_user
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.post("/id_user")
def register_user(login: str = Query(...)):
    try:
        data = get_user_id(login)
        user_exist = user_exists(data)
        if user_exist:
            return {"status": "success", "user_id": data}
        else:
            try:
                add_user(login)
                data = get_user_id(login)
                return {"status": "success", "user_id": data}
            except Exception as e:
                raise HTTPException(500, f"Ошибка при добавлении пользователя: {e}")
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении ID пользователя: {e}")
    
