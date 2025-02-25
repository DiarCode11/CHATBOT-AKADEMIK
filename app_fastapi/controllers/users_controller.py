from fastapi import APIRouter

user_router = APIRouter()

@user_router.get("/")
async def get_users():
    return {"message": "List of users"}

@user_router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"User with ID {user_id}"}
