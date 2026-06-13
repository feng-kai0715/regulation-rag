from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embedding import get_embedding_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "documents" / "bank_regulations.txt"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


def ingest_docs():
    if not SOURCE_FILE.exists():
        print(f"找不到來源檔案：{SOURCE_FILE}")
        return

    print(f"讀取來源檔案：{SOURCE_FILE}")
    try:
        loader = TextLoader(str(SOURCE_FILE), encoding="utf-8")
        documents = loader.load()
    except Exception as e:
        print(f"讀取檔案失敗：{type(e).__name__}: {e}")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)

    print("寫入 ChromaDB...")
    Chroma.from_documents(
        documents=texts,
        embedding=get_embedding_model(),
        persist_directory=str(CHROMA_DIR),
    )
    print("匯入完成")

if __name__ == "__main__":
    ingest_docs()