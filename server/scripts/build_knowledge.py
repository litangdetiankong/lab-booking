import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")   # 必须在加载 HF 相关库之前设置
import pathlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def main():
    docs = []
    for md in pathlib.Path("../docs").glob("*.md"):   # 相对 CWD：必须从 server/ 目录运行（../docs = 项目根/docs）
        docs += TextLoader(str(md), encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    Chroma.from_documents(chunks, embeddings, persist_directory="../chroma_db")
    print(f"入库完成：{len(chunks)} 个片段")

if __name__ == "__main__":     # 2026-10-30 修订：原骨架定义了 main() 却从没调用它，-m 运行会静默退出
    main()