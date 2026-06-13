import re

SOURCE_PREVIEW_LIMIT = 200


def extract_article_label(text: str) -> str | None:
    match = re.search(r"第\s*\d+\s*條", text)
    return match.group(0).replace(" ", "") if match else None


def extract_key_point(text: str) -> str:
    content = re.sub(r"^第\s*\d+\s*條\s*", "", text).strip()
    if not content:
        return ""

    content = re.sub(r"^法規名稱：.*?(?:\n|$)", "", content)
    content = re.sub(r"^公布日期：.*?(?:\n|$)", "", content)
    content = content.strip()

    first_clause = re.split(r"[。；;]\s*", content, maxsplit=1)[0].strip()
    if not first_clause:
        first_clause = content

    return first_clause[:SOURCE_PREVIEW_LIMIT]


def extract_source_path(metadata: dict[str, object]) -> str:
    source = str(metadata.get("source", "")).strip()
    if source:
        return source.split("/")[-1] if source.startswith("documents/") else source
    return "未知來源"


def build_source_preview(sources: str, results) -> str:
    if not results:
        return sources or "資料庫未找到相符法規"

    previews = []
    seen = set()
    for doc in results:
        article_label = extract_article_label(doc.page_content)
        key_point = extract_key_point(doc.page_content)
        source_hint = extract_source_path(getattr(doc, "metadata", {}) or {})

        if article_label and key_point:
            summary = f"{article_label}：{key_point}"
        elif article_label:
            summary = article_label
        elif key_point:
            summary = f"{source_hint}：{key_point}"
        else:
            summary = source_hint

        if summary not in seen:
            seen.add(summary)
            previews.append(summary)

    if not previews:
        return sources or "資料庫未找到相符法規"

    return "\n".join(previews)


def build_law_hint(results) -> str:
    names = []
    for doc in results or []:
        match = re.search(r"法規名稱：([^\n]+)", doc.page_content)
        if match:
            law_name = match.group(1).strip()
            if law_name and law_name not in names:
                names.append(law_name)

    if names:
        return "、".join(names)

    source_names = []
    for doc in results or []:
        source_hint = extract_source_path(getattr(doc, "metadata", {}) or {})
        if source_hint and source_hint not in source_names:
            source_names.append(source_hint)

    return "、".join(source_names)