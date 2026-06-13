import asyncio
import textwrap

import anthropic

MODEL_NAME = "claude-opus-4-8"
TRUNCATE_CHARS = 800
MAX_CONCURRENCY = 2
MAX_TOKENS = 2048

_semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
_client = anthropic.Anthropic()


def _build_context_note(context: str) -> str:
    return (
        "以下參考資料與問題高度相關，可能同時包含多部法規或多個條文，請優先依據參考資料做跨法規整合回答，避免補充未出現在資料中的內容。"
        if context[:TRUNCATE_CHARS]
        else "目前資料庫中沒有找到足夠相關的法規條文，請先明確說明查無直接相符法條，再提供簡短的一般性回答。"
    )


def _build_prompt(question: str, context: str) -> str:
    return textwrap.dedent(
        f"""
        你是一個專業的法律助理，只根據提供的法規資料回答，必要時要把多部法規整合成完整建議。
        {_build_context_note(context)}

        【參考資料】：
        {context[:TRUNCATE_CHARS]}

        【使用者問題】：
        {question}

        請使用繁體中文，採用以下固定格式輸出：
        1. 結論：直接回答問題核心，判斷是否可行或有無規範。
        2. 依據：明確引用條文（格式：《法規名稱》第X條），若有多部法規請分別列出，最多 3 點。
        3. 建議：整合各法規給出具體可執行的建議。
        4. 補充：若參考資料與問題不直接相關，請說明「現行草案未明定此議題」。

        嚴格規則：
        - 不得編造條文、法規名稱或數字。
        - 若問題詢問「罰款金額」、「申請流程」、「特定技術規範（如量子運算）」等草案未規定之細節，必須回答「現行草案未規定此細節」，不得引用不相關條文。
        - 參考資料若來自多部法規，必須分別說明各法規的規範重點。
        - 回答需與問題直接相關，若條文與問題無關請勿引用。
        - 內容精簡，總長度控制在 200 字以內。
        """
    ).strip()


def _sync_generate(question: str, context: str) -> str:
    try:
        message = _client.messages.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": _build_prompt(question, context)}],
        )
        return message.content[0].text
    except Exception as e:
        return f"生成失敗：{type(e).__name__}: {e}"


async def generate_answer(question: str, context: str) -> str:
    async with _semaphore:
        return await asyncio.to_thread(_sync_generate, question, context)


async def generate_stream(question: str, context: str):
    async with _semaphore:
        try:
            with _client.messages.stream(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": _build_prompt(question, context)}],
            ) as stream:
                for text in stream.text_stream:
                    yield {"text": text}
        except Exception as e:
            yield {"error": f"{type(e).__name__}: {e}"}


def prewarm_model():
    # Claude API 不需要預熱
    pass
