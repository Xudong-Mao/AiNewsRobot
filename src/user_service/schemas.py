from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional, Annotated
from datetime import datetime

class UserBase(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=50)]
    email: EmailStr

class UserCreate(UserBase):
    password: Annotated[str, constr(min_length=8, max_length=50)]
    
    @validator('password')
    def password_complexity(cls, v):
        """验证密码复杂度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[Annotated[str, constr(min_length=8, max_length=50)]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    
class EmailVerification(BaseModel):
    code: Annotated[str, constr(min_length=32, max_length=32)]

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: Annotated[str, constr(min_length=32, max_length=32)]
    new_password: Annotated[str, constr(min_length=8, max_length=50)]
    
    @validator('new_password')
    def password_complexity(cls, v):
        """验证密码复杂度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v