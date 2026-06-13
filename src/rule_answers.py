from article_rules import try_build_article_answer
from boundary_rules import try_build_boundary_answer
from principle_rules import try_build_principle_answer
from source_formatting import extract_article_label
from answer_utils import make_answer


def build_rule_based_answer(question: str, results) -> str | None:
    question_text = question.replace(" ", "")
    article_docs = []
    for doc in results or []:
        label = extract_article_label(doc.page_content)
        if label:
            article_docs.append((label.replace("第", "").replace("條", ""), doc))

    article_map = {article_number: doc for article_number, doc in article_docs}

    for builder in (try_build_boundary_answer, try_build_article_answer, try_build_principle_answer):
        answer = builder(question_text, article_map)
        if answer:
            return answer

    return None