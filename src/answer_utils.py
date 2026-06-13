def make_answer(conclusion: str, evidence: str, suggestion: str, supplement: str = "暫無相關紀錄") -> str:
    """Return a standardized multi-line answer block.

    Fields: 結論 / 依據 / 建議 / 補充
    """
    return "\n".join([
        f"結論：{conclusion}",
        f"依據：{evidence}",
        f"建議：{suggestion}",
        f"補充：{supplement}",
    ])
