from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator

from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 自动处理断开的连接
    pool_size=5,         # 连接池大小
    max_overflow=10,     # 最大溢出连接数
    pool_recycle=3600,   # 连接回收时间（秒）
    echo=False           # 是否打印SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """数据库会话上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 导出所需的组件
__all__ = ['engine', 'SessionLocal', 'Base', 'get_db', 'db_session']