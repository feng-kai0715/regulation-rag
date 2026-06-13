from pathlib import Path
import re
import os

from langchain_chroma import Chroma
import uuid

# Some environments may not have langchain.schema available; use a minimal Document-like class
class SimpleDoc:
    def __init__(self, page_content: str, metadata: dict[str, object]):
        self.page_content = page_content
        self.metadata = metadata
        self.id = str(uuid.uuid4())

from embedding import get_embedding_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


def split_into_articles(text: str):
    # 捕捉每個「第 N 條」起始到下一個條次前的區塊（包含標題與前置欄位）
    pattern = re.compile(r"(?ms)(^第\s*\d+\s*條[\s\S]*?)(?=^第\s*\d+\s*條|\Z)")
    matches = list(pattern.finditer(text))
    if not matches:
        # fallback: whole text as single document
        return [(None, text)]

    articles = []
    # 若檔案開頭包含標題與前置說明（在第1條之前），把它附到第1條前方
    for m in matches:
        articles.append(m.group(1).strip())
    return articles


def ingest_file(source_file: Path) -> list:
    print(f"讀取：{source_file.name}")
    try:
        raw = source_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = source_file.read_text(encoding="utf-8-sig")
    except Exception as e:
        print(f"  讀取失敗：{type(e).__name__}: {e}")
        return []

    article_texts = split_into_articles(raw)
    docs = []
    for i, art in enumerate(article_texts):
        if not art or not art.strip():
            continue
        m = re.search(r"第\s*(\d+)\s*條", art)
        label = f"第 {m.group(1)} 條" if m else f"chunk_{i+1}"
        docs.append(SimpleDoc(
            page_content=art,
            metadata={"source": f"documents/{source_file.name}", "article": label}
        ))
    print(f"  解析完成：{len(docs)} 條")
    return docs


def ingest_docs():
    txt_files = sorted(DOCUMENTS_DIR.glob("*.txt"))
    if not txt_files:
        print(f"找不到任何 .txt 法規檔案：{DOCUMENTS_DIR}")
        return

    all_docs = []
    for f in txt_files:
        all_docs.extend(ingest_file(f))

    if not all_docs:
        print("無可匯入的文件")
        return

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR") or str(CHROMA_DIR)
    print(f"\n寫入 ChromaDB 至：{persist_dir} （共 {len(all_docs)} 條）")
    try:
        Chroma.from_documents(
            documents=all_docs,
            embedding=get_embedding_model(),
            persist_directory=str(persist_dir),
        )
    except Exception as e:
        print(f"寫入 ChromaDB 失敗：{type(e).__name__}: {e}")
        return

    print("匯入完成")


if __name__ == "__main__":
    ingest_docs()