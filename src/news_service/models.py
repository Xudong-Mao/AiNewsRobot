"""
    @auth xudongmao
    @time 20241025014613
    @description 新闻
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    source_url = Column(String(500))
    publication_date = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 文章状态
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    
    # 分类和标签
    category = Column(String(50))
    tags = Column(String(200))  # 以逗号分隔的标签

    def __repr__(self):
        return f"<Article {self.title}>"

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "publication_date": self.publication_date,
            "view_count": self.view_count,
            "category": self.category,
            "tags": self.tags.split(",") if self.tags else []
        }