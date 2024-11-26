"""
    @auth xudongmao
    @time 20241025014613
    @description 将获取的文章进行总结
"""
from zhipuai import ZhipuAI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os, asyncio
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Article
from sqlalchemy import Column, Text

# 加载环境变量
load_dotenv(find_dotenv())
database_url = os.getenv("DATABASE_URL")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 创建数据库引擎
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_news_summary(data):
    API_KEY = openai_api_key
    BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

    client = ZhipuAI(api_key=API_KEY, base_url=BASE_URL)

    system_prompt = """
#任务:生成文章摘要
输入:文章内容
输出:60-80字的连贯概要
#步骤:
1.确定主语和核心动作格式为"谁干了什么"
2.提取关键功能和用途，格式为"实现什么功能，达到什么效果"
3.概括亮点或创新点
4.强调主观意义和价值，格式为"对什么有重要意义”
#示例格式:
"猫眼娱乐推出"神笔马良"工具，实现智能分析、角色创作、分镜创作，节省创作者时间和精力，提升创作效率，对内容创新具重要推动作用。
#要求:
-适当在每句话前面使用emoji
-语句通顺流畅
-用词精准合理
    """

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文章内容：{data}"}
            ],
            top_p=0.7,
            temperature=0.1,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"error: {e}")
        return None

async def summarize_and_update_db(date):
    # 创建数据库会话
    session = SessionLocal()

    # 将查询日期格式化为与数据库中一致的格式
    date = (datetime.now() - timedelta(days=1)).strftime("%Y年%m月%d号")

    # 打印出查询的日期以进行调试
    print(f"查询日期: {date}")

    # 检查数据库中是否有匹配的记录
    articles = session.query(Article).filter(Article.publication_date.like(f"{date}%")).all()

    if not articles:
        print("没有找到匹配的文章")
    else:
        for article in articles:
            print(f"找到文章ID: {article.id}, 日期: {article.publication_date}")
    
    # 更新数据库中的文章摘要
    for article in articles:
        summary = get_news_summary(article.content)
        print(f"文章ID: {article.id} 的总结:\n{summary}")
        article.summary = summary
        session.add(article)
    
    # 提交事务以保存更改
    session.commit()

    # 关闭会话
    session.close()

async def main():
    # 获取当天的日期
    date = datetime.now().strftime("%Y-%m-%d")
    await summarize_and_update_db(date)

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(main())
