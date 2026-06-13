from answer_utils import make_answer


# 邊界問題關鍵字：這類問題在草案中查無具體資料，應直接拒答
_NO_DATA_PATTERNS = [
    # 罰款/罰則類
    ("罰款", "施行後"),
    ("罰款金額",),
    ("罰緩",),
    ("罰則",),
    ("處罰金額",),
    # 認證/申請流程類
    ("認證", "申請"),
    ("合規認證",),
    ("許可證",),
    ("執照",),
    ("申請流程",),
    # 特定技術規範類（草案未明定）
    ("量子運算",),
    ("量子電腦",),
    ("區塊鏈", "AI"),
    ("元宇宙", "AI"),
]


def _matches_no_data(question_text: str) -> bool:
    for pattern in _NO_DATA_PATTERNS:
        if all(kw in question_text for kw in pattern):
            return True
    return False


def try_build_boundary_answer(question_text: str, article_map) -> str | None:
    # 優先判斷：完全查無資料的邊界問題
    if _matches_no_data(question_text):
        return make_answer(
            "暫無相關紀錄",
            "現行《人工智慧基本法》草案中未規定相關內容",
            "建議查閱施行細則、子法規或洽詢目的事業主管機關以取得最新資訊。",
        )

    # 既有認證/許可類
    if "許可" in question_text and "制度" in question_text:
        return make_answer(
            "資料中未規定相關制度。",
            "人工智慧基本法第 1 條；人工智慧基本法第 18 條",
            "若需確認許可或制度要求，應另查相關子法或其他法律。",
        )

    return None
