from fastapi import FastAPI
from .controllers.users_controller import user_router

def create_app():
    """
    Membuat daftar endpoint yang akan digunakan oleh aplikasi FastAPI.
    """
    
    app = FastAPI()

    app.include_router(user_router, prefix="/users", tags=["users"])

    return app