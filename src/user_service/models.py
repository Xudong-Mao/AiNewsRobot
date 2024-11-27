from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import secrets

from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    # 用户状态
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # 验证相关
    verification_code = Column(String(32))
    verification_code_expires = Column(DateTime(timezone=True))
    reset_password_token = Column(String(32))
    reset_token_expires = Column(DateTime(timezone=True))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.verify(password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return bcrypt.hash(password)
    
    def generate_verification_code(self) -> str:
        """生成邮箱验证码"""
        self.verification_code = secrets.token_hex(16)
        self.verification_code_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_code
    
    def generate_reset_token(self) -> str:
        """生成密码重置令牌"""
        self.reset_password_token = secrets.token_hex(16)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_password_token