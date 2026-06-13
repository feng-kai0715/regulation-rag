# ============================================================================
# 模型配置參數
# ============================================================================

MODEL_NAME = "gemma4:e4b"
KEEP_ALIVE = "30m"

# 上下文截斷設置
CONTEXT_TRUNCATE_CHARS = 2000  # 提高至 2000，避免重要信息丟失

# LLM 生成參數
TEMPERATURE = 0.3          # 保持低溫度確保答案一致性
MAX_TOKENS = 512           # 提高至 512，允許更完整的答案
TOP_P = 0.85
FREQUENCY_PENALTY = 0.0
PRESENCE_PENALTY = 0.0


# ============================================================================
# 提示詞範本
# ============================================================================

SYSTEM_PROMPT = """你是一位資深的法律顧問和 AI 基本法專家。

你的職責：
1. 根據提供的法規內容，準確回答用戶的法律問題
2. 必須遵守固定的回答格式
3. 優先依據提供的法規內容
4. 如果資料不足，明確說明

回答格式（必須遵守）：
結論：[提供清晰的法律結論或判斷]
依據：[引用相關法條編號]
建議：[給出具體的建議或行動方案]
補充：[補充說明或相關資訊]

重要提示：
- 每個部分必須有內容，不得空白
- 嚴禁捏造法條或虛假內容
- 如果資料不足，請明確說「資料不足，無法判斷」
"""

GENERATION_PROMPT_TEMPLATE = """根據以下法規內容，回答用戶的問題。

法規內容：
{context}

用戶問題：{question}

請按照系統提示中的格式回答，確保每個部分都有內容。"""


# ============================================================================
# 配置構建函數
# ============================================================================

def build_options() -> dict[str, object]:
    """
    構建 LLM 生成選項
    
    Returns:
        LLM 參數字典
    """
    return {
        "temperature": TEMPERATURE,
        "num_predict": MAX_TOKENS,
        "top_p": TOP_P,
        "frequency_penalty": FREQUENCY_PENALTY,
        "presence_penalty": PRESENCE_PENALTY,
    }


def build_context_note(context: str) -> str:
    """
    根據上下文長度生成提示信息
    
    Args:
        context: 法規上下文
        
    Returns:
        適當的提示信息
    """
    if context and len(context.strip()) > 50:
        return "以下參考資料與問題高度相關，可進行跨法規整合回答。"
    else:
        return "資料庫中未找到足夠相關的法規條文，請回覆「資料不足」。"


def build_prompt(question: str, context: str, source_hint: str = "") -> str:
    """
    構建查詢提示詞
    
    Args:
        question: 用戶問題
        context: 法規上下文
        source_hint: 來源提示（可選）
        
    Returns:
        格式化的提示詞
    """
    prompt = GENERATION_PROMPT_TEMPLATE.format(
        context=context[:CONTEXT_TRUNCATE_CHARS],  # 截斷過長的上下文
        question=question
    )
    
    if source_hint:
        prompt += f"\n\n參考來源：{source_hint}"
    
    return prompt


def build_chat_kwargs(
    question: str,
    context: str,
    *,
    stream: bool = False,
    source_hint: str = ""
) -> dict[str, object]:
    """
    構建 Chat API 調用參數
    
    Args:
        question: 用戶問題
        context: 法規上下文
        stream: 是否使用流式輸出
        source_hint: 來源提示
        
    Returns:
        Chat API 參數字典
    """
    kwargs: dict[str, object] = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question, context, source_hint)},
        ],
        "options": build_options(),
        "keep_alive": KEEP_ALIVE,
    }
    
    if stream:
        kwargs["stream"] = True
    
    return kwargs


# ============================================================================
# 調試/配置修改函數
# ============================================================================

def set_temperature(temp: float) -> None:
    """調整溫度參數（0.0-1.0）"""
    global TEMPERATURE
    TEMPERATURE = max(0.0, min(1.0, temp))


def set_max_tokens(tokens: int) -> None:
    """調整最大 token 數"""
    global MAX_TOKENS
    MAX_TOKENS = max(10, tokens)


def get_config() -> dict[str, object]:
    """
    獲取當前配置（用於調試）
    
    Returns:
        配置字典
    """
    return {
        "model": MODEL_NAME,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": TOP_P,
        "context_truncate": CONTEXT_TRUNCATE_CHARS,
    }
