from typing import Optional, List
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from core.database import Base, get_db
from .models import User
from .schemas import UserCreate, UserUpdate

class UserDB:
    """用户数据库操作类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_verification_code(self, code: str) -> Optional[User]:
        """通过验证码获取用户"""
        return self.db.query(User).filter(
            User.verification_code == code,
            User.verification_code_expires > datetime.utcnow()
        ).first()
    
    def get_user_by_reset_token(self, token: str) -> Optional[User]:
        """通过重置令牌获取用户"""
        return self.db.query(User).filter(
            User.reset_password_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """获取用户列表"""
        query = self.db.query(User)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def create_user(self, user: UserCreate) -> User:
        """创建新用户"""
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=User.get_password_hash(user.password)
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
            
        update_data = user_update.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = User.get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
            
        try:
            self.db.delete(db_user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def verify_email(self, user: User) -> bool:
        """验证用户邮箱"""
        try:
            user.email_verified = True
            user.is_active = True
            user.verification_code = None
            user.verification_code_expires = None
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_last_login(self, user: User) -> None:
        """更新最后登录时间"""
        try:
            user.last_login = datetime.utcnow()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def change_password(self, user: User, new_password: str) -> bool:
        """修改用户密码"""
        try:
            user.hashed_password = User.get_password_hash(new_password)
            user.reset_password_token = None
            user.reset_token_expires = None
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

# 创建数据库操作依赖
def get_user_db(db: Session = Depends(get_db)) -> UserDB:
    """获取用户数据库操作实例"""
    return UserDB(db)