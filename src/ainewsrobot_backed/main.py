from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import articles

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI News API",
    description="AI新闻获取和展示API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(articles.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=65535, reload=True)