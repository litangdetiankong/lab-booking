from langchain_openai import ChatOpenAI
from app.core.config import settings

llm = ChatOpenAI(model=settings.LLM_MODEL,
                 api_key=settings.LLM_API_KEY,
                 base_url=settings.LLM_BASE_URL,
                 temperature=0.4)

SYSTEM_PROMPT = """你是公司实验室预约助手，名字叫小实。
你可以帮员工解答实验室规则、查询实验室信息、协助预约。
回答简洁，使用中文；涉及具体数据时，不确定就如实说不知道。"""
