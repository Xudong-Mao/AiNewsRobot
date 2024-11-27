import logging
from typing import Optional
from zhipuai import ZhipuAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.config import settings

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.base_url = settings.ZHIPU_BASE_URL
        self.model = settings.ZHIPU_MODEL
        self.client = ZhipuAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        self.system_prompt = """
#任务:生成文章摘要
输入:文章内容
输出:60-80字的连贯概要
#步骤:
1.确定主语和核心动作格式为"谁干了什么"
2.提取关键功能和用途，格式为"实现什么功能，达到什么效果"
3.概括亮点或创新点
4.强调主观意义和价值，格式为"对什么有重要意义"
#示例格式:
"猫眼娱乐推出"神笔马良"工具，实现智能分析、角色创作、分镜创作，节省创作者时间和精力，提升创作效率，对内容创新具重要推动作用。"
#要求:
-适当在每句话前面使用emoji
-语句通顺流畅
-用词精准合理
        """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def _generate_summary_sync(self, content: str) -> Optional[str]:
        """同步方式生成摘要"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"文章内容：{content}"}
                ],
                top_p=0.7,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content
            logger.info(f"成功生成摘要: {summary[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            if isinstance(e, (ConnectionError, TimeoutError)):
                raise  # 重试这些错误
            return None

    async def generate_summary(self, content: str) -> Optional[str]:
        """异步包装器，在线程池中执行同步API调用"""
        try:
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                self.executor, 
                self._generate_summary_sync,
                content
            )
            return summary
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            return None

    def __del__(self):
        """清理线程池"""
        self.executor.shutdown(wait=False)

# 创建单例实例
summarizer = AISummarizer()

async def generate_summary(content: str) -> Optional[str]:
    """便捷的摘要生成函数"""
    try:
        return await summarizer.generate_summary(content)
    except Exception as e:
        logger.error(f"生成摘要失败: {str(e)}")
        return None

# 测试代码
async def test_summary():
    """测试摘要生成"""
    test_content = """
    OpenAI发布了GPT-4 Turbo模型，具有更强大的性能和更低的价格。新模型支持128k上下文窗口，
    可以处理更长的对话和文档。同时，API调用成本降低了3倍，使其更加经济实惠。
    GPT-4 Turbo还具有更新的知识库，包含2023年4月之前的数据。
    """
    
    summary = await generate_summary(test_content)
    if summary:
        print("测试成功！生成的摘要：")
        print(summary)
    else:
        print("测试失败！")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_summary())