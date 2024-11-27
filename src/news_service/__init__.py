from fastapi import FastAPI
from .routers import articles

def init_app(app: FastAPI) -> None:
    """初始化新闻服务"""
    app.include_router(articles.router)