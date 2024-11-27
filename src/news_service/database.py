'''
    @auth xudongmao
    @time 20241025152120
    @description 数据库连接
'''
from typing import List, Optional, Generator
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta
from fastapi import Depends

from core.database import get_db  # 从核心数据库模块导入
from .models import Article
from .schemas import ArticleCreate, ArticleUpdate, ArticleSearchParams

class NewsDB:
    def __init__(self, db: Session):
        self.db = db

    def get_article(self, article_id: int) -> Optional[Article]:
        """获取单个文章"""
        return self.db.query(Article).filter(Article.id == article_id).first()

    def get_articles(
        self,
        skip: int = 0,
        limit: int = 10,
        search_params: Optional[ArticleSearchParams] = None
    ) -> List[Article]:
        """获取文章列表"""
        query = self.db.query(Article)

        if search_params:
            if search_params.keyword:
                query = query.filter(
                    or_(
                        Article.title.ilike(f"%{search_params.keyword}%"),
                        Article.content.ilike(f"%{search_params.keyword}%")
                    )
                )
            
            if search_params.category:
                query = query.filter(Article.category == search_params.category)
            
            if search_params.tags:
                for tag in search_params.tags:
                    query = query.filter(Article.tags.ilike(f"%{tag}%"))
            
            if search_params.start_date:
                query = query.filter(Article.publication_date >= search_params.start_date)
            
            if search_params.end_date:
                query = query.filter(Article.publication_date <= search_params.end_date)

        return query.order_by(desc(Article.publication_date)).offset(skip).limit(limit).all()

    def create_article(self, article: ArticleCreate) -> Article:
        """创建新文章"""
        db_article = Article(
            title=article.title,
            content=article.content,
            summary=article.summary,
            source_url=article.source_url,
            publication_date=article.publication_date or datetime.utcnow(),
            category=article.category,
            tags=article.tags
        )
        
        try:
            self.db.add(db_article)
            self.db.commit()
            self.db.refresh(db_article)
            return db_article
        except Exception as e:
            self.db.rollback()
            raise e

    def update_article(self, article_id: int, article_update: ArticleUpdate) -> Optional[Article]:
        """更新文章"""
        db_article = self.get_article(article_id)
        if not db_article:
            return None

        update_data = article_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_article, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_article)
            return db_article
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_article(self, article_id: int) -> bool:
        """删除文章"""
        db_article = self.get_article(article_id)
        if not db_article:
            return False

        try:
            self.db.delete(db_article)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def get_total_count(self, search_params: Optional[ArticleSearchParams] = None) -> int:
        """获取文章总数"""
        query = self.db.query(Article)
        
        if search_params:
            # 添加搜索条件...
            pass
            
        return query.count()

    def increment_view_count(self, article_id: int) -> bool:
        """增加文章浏览次数"""
        db_article = self.get_article(article_id)
        if not db_article:
            return False

        try:
            db_article.increment_view_count()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

def get_news_db(db: Session = Depends(get_db)) -> NewsDB:
    """获取新闻数据库操作实例"""
    return NewsDB(db)

# 导出所需的函数和类
__all__ = ['NewsDB', 'get_news_db']