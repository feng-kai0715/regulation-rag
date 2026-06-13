from answer_utils import make_answer


def try_build_principle_answer(question_text: str, article_map) -> str | None:
    if "高風險" in question_text and ("系統" in question_text or "公司" in question_text or "機器學習" in question_text):
        return make_answer(
            "系統是否為高風險應用，需依據目的事業主管機關訂定的風險分類框架判斷；若涉及政府使用，則應進行風險評估與規劃風險因應措施。",
            "各目的事業主管機關應視人工智慧風險等級訂定管理規範；人工智慧基本法第 5 條、第 16 條、第 17 條",
            "先確認系統用途、部署場景與風險分類，再依機關規範補足評估與標示。",
        )

    article4 = article_map.get("4")
    if article4 and "原則" in question_text:
        return make_answer(
            "政府推動人工智慧應遵循永續發展與福祉、人類自主、隱私保護與資料治理、資安與安全、透明與可解釋、公平與不歧視、問責等原則。",
            "人工智慧基本法第 4 條",
            "研發、應用與治理設計應逐一納入上述原則。",
        )

    return None