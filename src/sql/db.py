import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.database import Base
from user_service.models import User
from news_service.models import Article

def init_db():
    """初始化数据库"""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建超级管理员
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                is_superuser=True,
                is_active=True
            )
            admin.set_password("admin123")  # 请修改为安全的密码
            db.add(admin)
            db.commit()
            click.echo("已创建超级管理员账户")
    except Exception as e:
        db.rollback()
        click.echo(f"创建超级管理员失败: {e}")
    finally:
        db.close()

@click.group()
def cli():
    """数据库管理命令"""
    pass

@cli.command()
def init():
    """初始化数据库"""
    click.echo("正在初始化数据库...")
    init_db()
    click.echo("数据库初始化完成！")

@cli.command()
def reset():
    """重置数据库（危险操作）"""
    if click.confirm('此操作将删除所有数据，确定继续吗？'):
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        click.echo("数据库已重置！")

if __name__ == '__main__':
    cli()