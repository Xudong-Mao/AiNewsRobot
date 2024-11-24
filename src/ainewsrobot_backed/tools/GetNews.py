'''
    @auth xudongmao
    @time 20241025011636
    @description 获取信息源，然后将信息自动整理为相应的格式
    @⚠️ 总结的信息存在emoji 需要修改数据库字符集         ALTER TABLE your_table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
'''
import json
import asyncio
import os
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

from Python.AINewsRobot.ainewsrobot_backed.src.ainewsrobot_backed.models import SessionLocal, Article
from AiSumer import get_news_summary

# 获取文章URL
import requests
from bs4 import BeautifulSoup
import re

# 获取首条文章的链接
def extract_snumber_from_url(base_url):
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
    return None

async def extract_ai_news_article(URL):
    print("\n--- 使用 JsonCssExtractionStrategy 提取 AIbase 新闻文章数据 ---")
    
    # 定义提取 schema
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
    
    # 创建提取策略
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    
    # 使用 AsyncWebCrawler 进行爬取
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url = URL,
            extraction_strategy=extraction_strategy,
            bypass_cache=True,  # 忽略缓存，确保获取最新内容
        )
        
        if not result.success:
            print("页面爬取失败")
            return
        
        # 解析提取的内容
        extracted_data = json.loads(result.extracted_content)
        print(f"成功提取 {len(extracted_data)} 条记录")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            
    return extracted_data


async def save_to_database(data):
    # 创建数据库会话
    session = SessionLocal()
    
    # 插入数据
    for article in data:
        db_article = Article(
            title=article['title'],
            publication_date=article['publication_date'],
            content=article['content'],
            summary = get_news_summary(article['content'])
        )
        session.add(db_article)
    
    # 提交事务并关闭会话
    session.commit()
    session.close()
    print("数据已成功写入数据库")


async def main():
    # 假设你想获取从12718到12710的文章
    base_url = 'https://www.aibase.com/zh/news/'
    start_id = extract_snumber_from_url(base_url)
    end_id = 12700
    print(start_id)
    for article_id in range(start_id, end_id - 1, -1):
        url = base_url + str(article_id)
        extracted_data = await extract_ai_news_article(url)
        if extracted_data:
            await save_to_database(extracted_data)

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(main())
