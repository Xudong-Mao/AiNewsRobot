'''
    @auth xudongmao
    @time 20241025152120
    @description Pydantic 模式, 用于请求和响应验证
'''

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    content: str
    publication_date: str
    summary: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int

    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    total: int
    items: List[ArticleResponse]