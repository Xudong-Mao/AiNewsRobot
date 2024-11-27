"""
@auth xudongmao
@time 20241025011636
@description 获取信息源，然后将信息自动整理为相应的格式
@⚠️ 总结的信息存在emoji 需要修改数据库字符集 ALTER TABLE articles CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from core.database import get_db
from ..models import Article
from ..schemas import ArticleCreate
from .AiSumer import generate_summary

logger = logging.getLogger(__name__)

class NewsExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
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
            content_div = soup.find('div', class_='post-content')
            content = content_div.text.strip() if content_div else ""
            
            # 提取发布日期
            date_elem = soup.select_one('div.flex.flex-col > div.flex.flex-wrap > span:nth-child(6)')
            if date_elem:
                date_str = date_elem.text.strip()
                # 尝试多种日期格式
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',  # 2024-01-25 10:30:00
                    '%Y年%m月%d号 %H:%M',  # 2024年11月27号 13:56
                    '%Y年%m月%d日 %H:%M',  # 2024年11月27日 13:56
                    '%Y/%m/%d %H:%M:%S',  # 2024/01/25 10:30:00
                    '%Y/%m/%d %H:%M'      # 2024/01/25 10:30
                ]
                
                publication_date = None
                for date_format in date_formats:
                    try:
                        publication_date = datetime.strptime(date_str, date_format)
                        break
                    except ValueError:
                        continue
                
                if publication_date is None:
                    logger.warning(f"无法解析日期格式 '{date_str}'，使用当前时间")
                    publication_date = datetime.utcnow()
            else:
                logger.warning(f"未找到日期元素，使用当前时间")
                publication_date = datetime.utcnow()

            return {
                'title': title,
                'content': content,
                'publication_date': publication_date,
                'source_url': url
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

            try:
                # 生成摘要
                summary = await generate_summary(article_data['content'])
                if summary:
                    article_data['summary'] = summary
                else:
                    logger.warning(f"无法生成摘要，跳过文章: {url}")
                    continue

                # 创建文章
                new_article = Article(**article_data)
                db.add(new_article)
                new_articles.append(new_article)

                # 添加延迟避免请求过快
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"处理文章失败 {url}: {str(e)}")
                continue

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

# 测试代码
async def test_extractor():
    """测试文章提取"""
    extractor = NewsExtractor()
    url = "https://www.aibase.com/zh/news/13498"
    
    logger.info(f"开始测试文章提取: {url}")
    article = await extractor.extract_article(url)
    
    if article:
        logger.info("文章提取成功！")
        logger.info("文章信息:")
        print(f"标题: {article['title']}")
        print(f"发布时间: {article['publication_date']}")
        print(f"内容长度: {len(article['content'])}")
    else:
        logger.error("文章提取失败！")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    asyncio.run(test_extractor())

# 导出函数
__all__ = ['fetch_latest_news', 'get_db_context']