from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from core.config import settings
from ..utils.auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from ..utils.email import send_verification_email, send_reset_password_email
from ..models import User
from ..schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    EmailVerification,
    PasswordReset,
    PasswordResetConfirm
)
from core.database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    用户注册
    """
    # 检查用户名和邮箱
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=User.get_password_hash(user.password)
    )
    
    # 生成验证码
    verification_code = db_user.generate_verification_code()
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 异步发送验证邮件
        background_tasks.add_task(
            send_verification_email,
            db_user.email,
            verification_code
        )
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱未验证，请先验证邮箱"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 生成访问令牌
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer", 'expires_in':settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 }

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """
    验证邮箱
    """
    user = db.query(User).filter(
        User.verification_code == verification.code,
        User.verification_code_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效或已过期"
        )
    
    user.email_verified = True
    user.is_active = True
    user.verification_code = None
    user.verification_code_expires = None
    
    db.commit()
    return {"message": "邮箱验证成功"}

@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    忘记密码
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if user and user.email_verified:
        reset_token = user.generate_reset_token()
        db.commit()
        
        background_tasks.add_task(
            send_reset_password_email,
            user.email,
            reset_token
        )
    
    return {"message": "如果邮箱存在，您将收到重置密码的链接"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    重置密码
    """
    user = db.query(User).filter(
        User.reset_password_token == reset_data.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌无效或已过期"
        )
    
    user.hashed_password = User.get_password_hash(reset_data.new_password)
    user.reset_password_token = None
    user.reset_token_expires = None
    
    db.commit()
    return {"message": "密码重置成功"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return current_user