from news_service.utils.GetNews import fetch_latest_news

async def main():
    async with get_db_context() as db:
        articles = await fetch_latest_news(db)
        print(f"获取到 {len(articles)} 篇新文章")

if __name__ == "__main__":
    asyncio.run(main())