from fastapi import FastAPI
from .routers import users

def init_app(app: FastAPI) -> None:
    """初始化用户服务"""
    app.include_router(users.router)