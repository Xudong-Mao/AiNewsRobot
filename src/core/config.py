from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI News Robot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI新闻获取和用户管理系统"
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 65535
    RELOAD: bool = True
    WORKERS: int = 4
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@127.0.0.1:3306/ai_news_db?charset=utf8mb4")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 邮件配置 - 设置默认值或标记为可选
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER", "")
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VERIFY_SSL: bool = True
    
    # 前端配置
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # 支持邮箱
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@example.com")
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"
    ]
    
    # # OpenAI配置
    # OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    # OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # ZhipuAI配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_BASE_URL: str = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    
    # Redis配置
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

settings = get_settings()