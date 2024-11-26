'''
    @auth xudongmao
    @time 20241025152120
    @description 文章相关的路由
'''

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from models import Article
from schemas import ArticleResponse, ArticleList
from database import SessionLocal
from GetNews2 import fetch_latest_news

router = APIRouter(prefix="/api/articles", tags=["articles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=ArticleList)
async def list_articles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取文章列表，支持分页和日期筛选"""
    query = db.query(Article)
    
    if date:
        query = query.filter(Article.publication_date.like(f"%{date}%"))
    
    total = query.count()
    articles = query.order_by(desc(Article.publication_date))\
                   .offset(skip)\
                   .limit(limit)\
                   .all()
    
    return ArticleList(total=total, items=articles)

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取单篇文章详情"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/fetch-latest", response_model=ArticleList)
async def fetch_new_articles(db: Session = Depends(get_db)):
    """手动触发获取最新文章"""
    try:
        new_articles = await fetch_latest_news()
        return ArticleList(
            total=len(new_articles),
            items=new_articles
        )
    except Exception as e:
        print(f"Error fetching new articles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch new articles: {str(e)}"
        )