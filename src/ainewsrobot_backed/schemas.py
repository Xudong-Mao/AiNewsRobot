'''
    @auth xudongmao
    @time 20241025152120
    @description Pydantic 模式, 用于请求和响应验证
'''

from pydantic import BaseModel
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    summary: str
    content: str

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    publication_date: datetime

    class Config:
        orm_mode = True
