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
from AiSumer import get_news_summary

def extract_snumber_from_url(base_url: str) -> int:
    """获取最新文章ID"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(base_url, headers=headers)
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
        return 12700
    return 12700

async def extract_ai_news_article(url: str) -> List[Dict]:
    """获取单篇文章内容"""
    print(f"\n--- 正在获取文章: {url} ---")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找主容器
        main_container = soup.select_one('div.pb-32')
        if not main_container:
            return []
            
        # 提取标题
        title = main_container.select_one('h1')
        title = title.text.strip() if title else ''
        
        # 提取发布日期
        date_element = main_container.select_one('div.flex.flex-col > div.flex.flex-wrap > span:nth-child(6)')
        publication_date = date_element.text.strip() if date_element else ''
        
        # 提取内容
        content_element = main_container.select_one('div.post-content')
        content = content_element.text.strip() if content_element else ''
        
        if title and publication_date and content:
            extracted_data = [{
                'title': title,
                'publication_date': publication_date,
                'content': content
            }]
            print(f"成功提取文章数据: {url}")
            return extracted_data
        return []
            
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

# 测试获取新闻
async def test_crawler():
    url = "https://www.aibase.com/zh/news/12700"  # 使用一个确定存在的文章URL
    result = await extract_ai_news_article(url)
    print(result)

# 在命令行中运行测试
if __name__ == "__main__":
    asyncio.run(test_crawler())