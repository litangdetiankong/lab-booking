import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")   # 2026-11-02 补：不设它，加载向量模型会直连
                                                                 # huggingface.co 超时重试一两分钟才回退缓存
import logging
logger = logging.getLogger("app.rag")
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

vectorstore = Chroma(persist_directory="../chroma_db",     # 相对 uvicorn 启动目录 server/ → 指向项目根的 chroma_db
                     embedding_function=HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5"))

MAX_DISTANCE = 1.2   # 距离阈值：Chroma 返回的是"距离"，越小越相似。超过它视为不相关（按实测调）

def retrieve(query: str, k: int = 3) -> list[str]:
    """检索 + 过滤：返回拼进 prompt 的片段列表"""
    # with_score 版本返回 (Document, 距离) 列表；距离越小 = 语义越接近
    pairs = vectorstore.similarity_search_with_score(query, k=k)
    hits = []
    for doc, distance in pairs:
        # 日志：亲眼看看每个问题命中了哪些片段、距离多少——调 RAG 必备
        logger.info("[RAG] distance=%.3f 片段=%s",
                     distance, doc.page_content[:40].replace("\n", " "))
        if distance <= MAX_DISTANCE:
            hits.append(doc.page_content)
        else:
            logger.info("[RAG] 距离超阈值，丢弃")   # 不相关片段硬塞进 prompt 反而带偏回答
    return hits