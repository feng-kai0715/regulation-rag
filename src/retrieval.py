import hashlib
from pathlib import Path

from article_lookup import extract_requested_article_number, load_article_block
from embedding import get_embedding_model
from langchain_chroma import Chroma
from source_formatting import (
    build_law_hint,
    build_source_preview,
    extract_article_label,
    extract_key_point,
    extract_source_path,
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

db = None


def ensure_db():
    global db
    if db is None:
        db = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=get_embedding_model())


def build_context(question: str, max_k: int = 3):
    ensure_db()
    if db is None:
        raise RuntimeError("Vector database is not ready. Wait for startup to finish.")

    results = db.similarity_search(question, k=max_k)
    requested_article_number = extract_requested_article_number(question)
    direct_article_doc = load_article_block(requested_article_number) if requested_article_number else None

    if direct_article_doc:
        deduped_results = [direct_article_doc]
        for doc in results:
            if doc.page_content.strip() != direct_article_doc.page_content.strip():
                deduped_results.append(doc)
        results = deduped_results[:max_k]

    context = "\n".join(doc.page_content for doc in results)
    sources = " | ".join(sorted({doc.metadata.get("source", "未知來源") for doc in results}))

    return context, sources, results


def build_cache_key(question: str, context: str) -> str:
    return hashlib.sha256(f"{question}::{context}".encode("utf-8")).hexdigest()


def load_query_state(question: str, max_k: int = 3):
    context, sources, results = build_context(question, max_k=max_k)
    law_hint = build_law_hint(results)
    return context, sources, results, law_hint, build_cache_key(question, context)