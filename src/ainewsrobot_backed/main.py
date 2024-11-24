from fastapi import FastAPI
from .database import engine, Base
from .routers import articles

# # 创建数据库表
# Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(articles.router)
