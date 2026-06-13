import re
from types import SimpleNamespace

from document_loading import load_document_texts


def extract_requested_article_number(question: str) -> str | None:
    match = re.search(r"第\s*(\d+)\s*條", question)
    return match.group(1) if match else None


def load_article_block(article_number: str):
    article_pattern = re.compile(rf"(?ms)^第\s*{re.escape(article_number)}\s*條\s*.*?(?=^第\s*\d+\s*條\s*|\Z)")

    for filename, text in load_document_texts():
        match = article_pattern.search(text)
        if match:
            return SimpleNamespace(
                page_content=match.group(0).strip(),
                metadata={"source": f"documents/{filename}"},
            )

    return None