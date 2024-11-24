"""
    @auth xudongmao
    @time 20241025014613
    @description 数据库模型
"""
from datetime import datetime
import os
from sqlalchemy import Boolean, DateTime, ForeignKey, create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .database import Base

# from dotenv import load_dotenv, find_dotenv
# load_dotenv()
# database_url = os.getenv("DATABASE_URL") 
# # 创建数据库引擎
# DATABASE_URL = database_url
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# 定义数据库模型
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    publication_date = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(255))

# 定义用户模型      
class Uer(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    create_at = Column(DateTime, nullable=False, default=datetime.now)
    update_at = Column(DateTime, nullable=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)

class ArticleCategory(Base):
    __tablename__ = 'article_categories'
    article_id = Column(Integer, ForeignKey('articles.id'), primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True, index=True)

class Comment(Base):
    __tablename__= 'comments'
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer,ForeignKey('articles.id'), index=True)
    user_id = Column(Integer,ForeignKey('users.id'), index=True)
    content = Column(Text,nullable=False)
    create_at = Column(DateTime, nullable=False, default=datetime.now)

class Like(Base):
    __tablename__= 'likes'
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('articles.id'), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    create_at = Column(DateTime, nullable=False, default=datetime.now)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

class ArticleTag(Base):
    __tablename__ = "article_tags"
    article_id = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)


# # 创建表格（如果表格不存在）
# Base.metadata.create_all(bind=engine)