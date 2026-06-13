from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"


@lru_cache(maxsize=1)
def load_document_texts() -> tuple[tuple[str, str], ...]:
    if not DOCUMENTS_DIR.exists():
        return ()

    texts: list[tuple[str, str]] = []
    for txt_path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        try:
            text = txt_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = txt_path.read_text(encoding="utf-8-sig")
        texts.append((txt_path.name, text))
    return tuple(texts)