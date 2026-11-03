from langchain_openai import ChatOpenAI
from app.core.config import settings

llm = ChatOpenAI(model=settings.LLM_MODEL,
                 api_key=settings.LLM_API_KEY,
                 base_url=settings.LLM_BASE_URL,
                 temperature=0.4)

SYSTEM_PROMPT = """你是医药检测实验室预约助手，名字叫小检。
你可以帮检测员解答检测室预约规则、生物安全与仪器使用要求，查询检测室和设备，并协助预约。
回答简洁，使用中文；涉及具体数据时，不确定就如实说不知道。不要编造检测结果或样本信息。"""
