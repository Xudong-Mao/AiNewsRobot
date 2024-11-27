import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from core.database import get_db  # 从核心数据库模块导入
from ..models import Article
from ..schemas import ArticleCreate
from .AiSumer import generate_summary

logger = logging.getLogger(__name__)

class NewsExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_snumber_from_url(self, base_url: str) -> Optional[int]:
        """获取最新文章ID"""
        try:
            response = requests.get(base_url, headers=self.headers)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            for link in links:
                href = link.get('href')
                if href:
                    pattern = r'/zh/news/(\d+)'
                    match = re.search(pattern, href)
                    if match:
                        return int(match.group(1))
            return None
        except Exception as e:
            logger.error(f"获取最新文章ID失败: {str(e)}")
            return None

    async def extract_article(self, url: str) -> Optional[Dict]:
        """提取单篇文章内容"""
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取文章内容
            title = soup.find('h1').text.strip()
            content_div = soup.find('div', class_='article-content')
            content = content_div.text.strip() if content_div else ""
            
            # 提取发布日期
            date_str = soup.find('time').text.strip()
            publication_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

            # 提取分类和标签
            category = soup.find('span', class_='category').text.strip()
            tags = [tag.text.strip() for tag in soup.find_all('span', class_='tag')]

            return {
                'title': title,
                'content': content,
                'publication_date': publication_date,
                'source_url': url,
                'category': category,
                'tags': ','.join(tags)
            }
        except Exception as e:
            logger.error(f"提取文章失败 {url}: {str(e)}")
            return None

async def fetch_latest_news(db: Session) -> List[Article]:
    """获取最新新闻"""
    extractor = NewsExtractor()
    base_url = 'https://www.aibase.com/zh/news/'
    
    try:
        # 获取最新文章ID
        start_id = extractor.extract_snumber_from_url(base_url)
        if not start_id:
            raise Exception("无法获取最新文章ID")

        end_id = start_id - 10  # 每次获取10篇文章
        new_articles = []

        for article_id in range(start_id, end_id, -1):
            url = f"{base_url}{article_id}"
            logger.info(f"正在获取文章: {url}")
            
            # 检查文章是否已存在
            existing = db.query(Article).filter(
                Article.source_url == url
            ).first()
            if existing:
                continue

            # 提取文章
            article_data = await extractor.extract_article(url)
            if not article_data:
                continue

            # 生成摘要
            article_data['summary'] = await generate_summary(article_data['content'])

            # 创建文章
            new_article = Article(**article_data)
            db.add(new_article)
            new_articles.append(new_article)

        if new_articles:
            db.commit()
            logger.info(f"成功保存 {len(new_articles)} 篇新文章")

        return new_articles

    except Exception as e:
        db.rollback()
        logger.error(f"获取最新新闻失败: {str(e)}")
        raise

# 创建一个异步上下文管理器来处理数据库会话
async def get_db_context():
    """获取数据库会话的异步上下文管理器"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# 导出函数
__all__ = ['fetch_latest_news', 'get_db_context']


