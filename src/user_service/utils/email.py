from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from jinja2 import Environment, select_autoescape, PackageLoader

from core.config import settings

# # 邮件配置
# conf = ConnectionConfig(
#     MAIL_USERNAME=settings.MAIL_USERNAME,
#     MAIL_PASSWORD=settings.MAIL_PASSWORD,
#     MAIL_FROM=settings.MAIL_FROM,
#     MAIL_PORT=settings.MAIL_PORT,
#     MAIL_SERVER=settings.MAIL_SERVER,
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True,
#     TEMPLATE_FOLDER='user_service/templates/email'
# )

# # 创建Jinja2环境
# env = Environment(
#     loader=PackageLoader('user_service', 'templates/email'),
#     autoescape=select_autoescape(['html', 'xml'])
# )

# async def send_verification_email(email: EmailStr, verification_code: str):
#     """发送验证邮件"""
#     template = env.get_template('verification.html')
#     html = template.render(
#         verification_url=f"{settings.FRONTEND_URL}/verify-email?code={verification_code}",
#         support_email=settings.SUPPORT_EMAIL
#     )
    
#     message = MessageSchema(
#         subject="验证您的邮箱地址",
#         recipients=[email],
#         body=html,
#         subtype="html"
#     )
    
#     fm = FastMail(conf)
#     try:
#         await fm.send_message(message)
#     except Exception as e:
#         print(f"发送验证邮件失败: {str(e)}")
#         raise

# async def send_reset_password_email(email: EmailStr, reset_token: str):
#     """发送密码重置邮件"""
#     template = env.get_template('reset_password.html')
#     html = template.render(
#         reset_url=f"{settings.FRONTEND_URL}/reset-password?token={reset_token}",
#         support_email=settings.SUPPORT_EMAIL
#     )
    
#     message = MessageSchema(
#         subject="重置您的密码",
#         recipients=[email],
#         body=html,
#         subtype="html"
#     )
    
#     fm = FastMail(conf)
#     try:
#         await fm.send_message(message)
#     except Exception as e:
#         print(f"发送重置密码邮件失败: {str(e)}")
#         raise


### 模拟发送
async def send_verification_email(email: str, verification_code: str):
    """模拟发送验证邮件"""
    print(f"模拟发送验证邮件到 {email}，验证码：{verification_code}")
    return True

async def send_reset_password_email(email: str, reset_token: str):
    """模拟发送密码重置邮件"""
    print(f"模拟发送密码重置邮件到 {email}，重置令牌：{reset_token}")
    return True