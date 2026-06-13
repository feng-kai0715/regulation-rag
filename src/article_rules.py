import re

from retrieval import load_article_block
from answer_utils import make_answer


def try_build_article_answer(question_text: str, article_map) -> str | None:
    article2 = article_map.get("2") or load_article_block("2")
    if article2 and "主管機關" in question_text:
        article_text = article2.page_content
        central_match = re.search(r"在中央為([^；;\n]+)", article_text)
        local_match = re.search(r"在地方為([^；;\n]+)", article_text)
        central = central_match.group(1).strip() if central_match else "國家科學及技術委員會"
        local = local_match.group(1).strip() if local_match else "直轄市、縣（市）政府"

        if "地方" in question_text:
            return make_answer(
                f"地方主管機關為{local}。",
                "人工智慧基本法第 2 條",
                "涉及各目的事業主管機關職掌者，仍由各目的事業主管機關辦理。",
            )
        return make_answer(
            f"中央主管機關為{central}。",
            "人工智慧基本法第 2 條",
            "辦理本法所定事項時，應以第 2 條所定中央與地方權責分工為準。",
        )

    article3 = article_map.get("3")
    if article3 and "定義" in question_text:
        article_text = article3.page_content
        definition_match = re.search(r"本法所稱人工智慧，指(.+?)(?:。|\n)", article_text)
        definition = definition_match.group(1).strip() if definition_match else article_text.strip()
        return make_answer(
            f"人工智慧是{definition}。",
            "人工智慧基本法第 3 條",
            "可據此判斷系統是否屬於本法所稱人工智慧。",
        )

    article4 = article_map.get("4")
    if article4 and "原則" in question_text:
        return make_answer(
            "政府推動人工智慧應遵循永續發展與福祉、人類自主、隱私保護與資料治理、資安與安全、透明與可解釋、公平與不歧視、問責等原則。",
            "人工智慧基本法第 4 條",
            "研發、應用與治理設計應逐一納入上述原則。",
        )

    article5 = article_map.get("5")
    article16 = article_map.get("16")
    if article5 and article16 and ("高風險" in question_text or "標示" in question_text or "認定" in question_text):
        return make_answer(
            "高風險AI由中央目的事業主管機關會商數位發展部認定，並應明確標示注意事項或警語；各目的事業主管機關應依風險分類框架訂定管理規範。",
            "人工智慧基本法第 5 條；人工智慧基本法第 16 條",
            "實務上應先確認風險分類，再依認定機關與標示要求進行合規設計。",
        )

    article14 = article_map.get("14")
    if article14 and "個人資料" in question_text:
        return make_answer(
            "在人工智慧研發及應用過程中，應避免不必要的個人資料蒐集、處理或利用，並將個資保護納入預設及設計措施。",
            "人工智慧基本法第 14 條",
            "應先採取資料最小化與預設保護設計。",
        )

    article15 = article_map.get("15")
    if article15 and ("失業" in question_text or "勞工" in question_text):
        return make_answer(
            "政府應透過教育及培訓、縮小技能落差、保障勞動參與與經濟安全，並對失業者依其工作能力輔導就業。",
            "人工智慧基本法第 15 條",
            "可依勞動能力與技能缺口提供轉職、訓練與就業輔導。",
        )

    article18 = article_map.get("18")
    if article18 and ("修正期限" in question_text or "多久" in question_text):
        return make_answer(
            "自本法施行後二年內，應完成法規的制定、修正或廢止，以及行政措施的改進。",
            "人工智慧基本法第 18 條",
            "相關主管機關應及早完成配套修法。",
        )

    article20 = article_map.get("20")
    if article20 and ("施行" in question_text or "日期" in question_text):
        return make_answer(
            "本法自公布之日起施行；公布日期為民國 115 年 01 月 14 日。",
            "人工智慧基本法第 20 條；人工智慧基本法公布日期為民國 115 年 01 月 14 日",
            "施行時點以公布日為準。",
        )

    return None