from answer_utils import make_answer


def try_build_boundary_answer(question_text: str, article_map) -> str | None:
    if "執照" in question_text or "許可證" in question_text or "認證" in question_text:
        return make_answer(
            "資料中未規定相關制度。",
            "人工智慧基本法第 1 條；人工智慧基本法第 18 條",
            "若需確認許可或制度要求，應另查相關子法或其他法律。",
        )

    article5 = article_map.get("5")
    if article5 and ("罰款" in question_text or "處罰" in question_text):
        return make_answer(
            "資料中未規定相關罰則或相關制度。",
            "人工智慧基本法第 1 條；人工智慧基本法第 18 條",
            "若需確認裁罰或許可要求，應另查相關子法或其他法律。",
        )

    return None