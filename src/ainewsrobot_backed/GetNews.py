'''
    @auth xudongmao
    @time 20241025011636
    @description 获取信息源，然后将信息自动整理为相应的格式
    @⚠️ 总结的信息存在emoji 需要修改数据库字符集         ALTER TABLE your_table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
'''
import json
import asyncio
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Article
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from AiSumer import get_news_summary

def extract_snumber_from_url(base_url: str) -> int:
    """获取最新文章ID"""
    try:
        response = requests.get(base_url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href:
                pattern = r'/zh/news/(\d+)' 
                match = re.search(pattern, href)
                if match:
                    snumber = int(match.group(1))
                    return snumber
    except Exception as e:
        print(f"error: {e}")
        return 12700  # 默认值
    return 12700

async def extract_ai_news_article(url: str) -> List[Dict]:
    """获取单篇文章内容"""
    print(f"\n--- 正在获取文章: {url} ---")
    
    schema = {
        "name": "AIbase News Article",
        "baseSelector": "div.pb-32",  # 主容器的 CSS 选择器
        "fields": [
            {
                "name": "title",
                "selector": "h1",
                "type": "text",
            },
            {
                "name": "publication_date",
                "selector": "div.flex.flex-col > div.flex.flex-wrap > span:nth-child(6)",
                "type": "text",
            },
            {
                "name": "content",
                "selector": "div.post-content",
                "type": "text",
            },
        ],
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    
    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                extraction_strategy=extraction_strategy,
                bypass_cache=True,
            )
            
            if not result.success:
                print(f"页面爬取失败: {url}")
                return []
            
            extracted_data = json.loads(result.extracted_content)
            print(f"成功提取文章数据: {url}")
            return extracted_data
            
    except Exception as e:
        print(f"Error extracting article from {url}: {str(e)}")
        return []

async def fetch_latest_news() -> List[Article]:
    """获取最新新闻并保存到数据库"""
    db = SessionLocal()
    new_articles = []
    
    try:
        base_url = 'https://www.aibase.com/zh/news/'
        start_id = extract_snumber_from_url(base_url)
        print(f"最新文章ID: {start_id}")
        
        # 获取数据库中最新的文章ID
        latest_db_article = db.query(Article).order_by(Article.id.desc()).first()
        end_id = latest_db_article.id if latest_db_article else start_id - 10
        
        # 限制一次最多获取10篇文章
        end_id = max(end_id, start_id - 10)
        
        for article_id in range(start_id, end_id - 1, -1):
            url = f"{base_url}{article_id}"
            
            # 检查文章是否已存在
            existing_article = db.query(Article).filter(
                Article.title.like(f"%{article_id}%")
            ).first()
            
            if existing_article:
                continue
                
            extracted_data = await extract_ai_news_article(url)
            
            if extracted_data and len(extracted_data) > 0:
                for article_data in extracted_data:
                    # 添加摘要
                    article_data['summary'] = get_news_summary(article_data['content'])
                    
                    # 创建新文章
                    new_article = Article(
                        title=article_data['title'],
                        content=article_data['content'],
                        publication_date=article_data['publication_date'],
                        summary=article_data['summary']
                    )
                    db.add(new_article)
                    new_articles.append(new_article)
        
        # 提交更改
        if new_articles:
            db.commit()
            print(f"成功保存 {len(new_articles)} 篇新文章")
            
            # 刷新对象以获取新的ID
            for article in new_articles:
                db.refresh(article)
        
        return new_articles
    
    except Exception as e:
        db.rollback()
        print(f"Error in fetch_latest_news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# # 测试获取新闻
# async def test_crawler():
#     url = "https://www.aibase.com/zh/news/12700"  # 使用一个确定存在的文章URL
#     result = await extract_ai_news_article(url)
#     print(result)

# # 在命令行中运行测试
# if __name__ == "__main__":
#     asyncio.run(test_crawler())