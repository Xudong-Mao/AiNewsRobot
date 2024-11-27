'''
    @auth xudongmao
    @time 20241025152120
    @description 文章相关的路由
'''

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from core.config import settings  
from user_service.utils.auth import get_current_user, get_current_active_superuser
from ..database import NewsDB, get_news_db
from ..schemas import ArticleCreate, ArticleUpdate, ArticleInDB, ArticleList, ArticleSearchParams
from ..utils.GetNews import fetch_latest_news
from ..utils.AiSumer import generate_summary

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=ArticleList)
async def get_articles(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 10,
    news_db: NewsDB = Depends(get_news_db)
):
    """获取文章列表"""
    search_params = ArticleSearchParams(
        keyword=keyword,
        category=category,
        tags=tags,
        start_date=start_date,
        end_date=end_date
    )
    
    articles = news_db.get_articles(skip=skip, limit=limit, search_params=search_params)
    total = news_db.get_total_count(search_params)
    
    return ArticleList(total=total, items=articles)

@router.get("/{article_id}", response_model=ArticleInDB)
async def get_article(
    article_id: int,
    news_db: NewsDB = Depends(get_news_db)
):
    """获取单个文章"""
    article = news_db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览次数
    news_db.increment_view_count(article_id)
    return article

@router.post("/fetch-latest")
async def fetch_new_articles(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """获取最新文章"""
    try:
        background_tasks.add_task(fetch_latest_news, db)
        return {"message": "正在后台获取最新文章"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=ArticleInDB)
async def create_article(
    article: ArticleCreate,
    current_user = Depends(get_current_active_superuser),
    news_db: NewsDB = Depends(get_news_db)
):
    """创建新文章"""
    # 生成摘要
    if not article.summary and article.content:
        article.summary = generate_summary(article.content)
    
    try:
        return news_db.create_article(article)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{article_id}", response_model=ArticleInDB)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    current_user = Depends(get_current_active_superuser),
    news_db: NewsDB = Depends(get_news_db)
):
    """更新文章"""
    # 如果内容更新了，重新生成摘要
    if article_update.content:
        article_update.summary = generate_summary(article_update.content)
    
    updated_article = news_db.update_article(article_id, article_update)
    if not updated_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return updated_article

@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user = Depends(get_current_active_superuser),
    news_db: NewsDB = Depends(get_news_db)
):
    """删除文章"""
    if not news_db.delete_article(article_id):
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return {"message": "文章已删除"}