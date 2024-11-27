'''
    @auth xudongmao
    @time 20241025152120
    @description Pydantic 模式, 用于请求和响应验证
'''

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    category: Optional[str] = None
    tags: Optional[str] = None

class ArticleCreate(ArticleBase):
    publication_date: Optional[datetime] = None

class ArticleUpdate(ArticleBase):
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None

class ArticleInDB(ArticleBase):
    id: int
    publication_date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    is_published: bool
    view_count: int

    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    total: int
    items: List[ArticleInDB]

class ArticleSearchParams(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None