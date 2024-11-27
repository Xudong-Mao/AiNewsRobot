import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.database import Base
from main import app
from user_service.database import get_user_db

# 测试配置和测试用例