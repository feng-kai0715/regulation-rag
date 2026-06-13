import re


def extract_content(chunk) -> str | None:
    """從不同格式的 chunk 中提取文本內容"""
    if isinstance(chunk, dict):
        message = chunk.get("message")
        if isinstance(message, dict):
            content = message.get("content") or message.get("thinking")
            if content:
                return content
        content = chunk.get("delta") or chunk.get("content")
        if content:
            return content
        return None

    message = getattr(chunk, "message", None)
    if isinstance(message, dict):
        content = message.get("content") or message.get("thinking")
        if content:
            return content
    elif message is not None:
        content = getattr(message, "content", "") or getattr(message, "thinking", "")
        if content:
            return content

    return None


def clean_line(line: str) -> str:
    """清理單行：移除列表符號、編號、冒號等"""
    line = line.strip()
    line = re.sub(r"^[\-*•]+\s*", "", line)  # 移除列表符號
    line = re.sub(r"^\d+\.\s*", "", line)    # 移除數字編號
    line = re.sub(r"^\s*[:：]\s*", "", line)  # 移除冒號
    return line.strip()


def normalize_answer(raw_answer: str) -> str:
    """
    正規化答案格式為標準結構：結論/依據/建議/補充
    """
    text = (raw_answer or "").strip()
    
    # 特殊情況：無相關紀錄
    if not text or ("暫無相關紀錄" in text and len(text) <= 30):
        return _format_text_v1({
            "結論": "暫無相關紀錄",
            "依據": "無",
            "建議": "無",
            "補充": "無",
        })
    
    # 策略：先嘗試標準解析，若失敗則強制分割
    sections = _parse_sections_standard(text)
    
    if not any(sections.values()):
        sections = _parse_sections_force(text)
    
    # 若仍然為空，強制進行基本格式化
    if not any(sections.values()):
        return _format_text_v1({
            "結論": text[:200] if text else "暫無結論",
            "依據": "無相關法條",
            "建議": "無特別建議",
            "補充": "無補充說明",
        })
    
    # 填充空部分
    if not sections["結論"]:
        sections["結論"] = "暫無結論"
    if not sections["依據"]:
        sections["依據"] = "無相關法條"
    if not sections["建議"]:
        sections["建議"] = "無特別建議"
    if not sections["補充"]:
        sections["補充"] = "無補充說明"
    
    return _format_text_v1(sections)


def _parse_sections_standard(text: str) -> dict:
    """
    標準解析：逐行識別標題和內容
    支援「結論：」「依據：」等格式
    """
    sections = {
        "結論": [],
        "依據": [],
        "建議": [],
        "補充": [],
    }
    
    current_section = None
    
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        
        # 匹配「結論：」「結論:」或「結論」等格式
        section_match = re.match(
            r"^(結論|依據|建議|補充)[:：]?\s*(.*)$",
            line
        )
        
        if section_match:
            section_name = section_match.group(1)
            content = section_match.group(2).strip()
            current_section = section_name
            
            if content:
                sections[current_section].append(content)
            continue
        
        # 若在某個部分內，將內容添加到該部分
        if current_section and line:
            sections[current_section].append(line)
    
    # 合併各部分的內容
    result = {
        "結論": " ".join(sections["結論"]).strip(),
        "依據": "；".join(part for part in sections["依據"] if part).strip(),
        "建議": " ".join(sections["建議"]).strip(),
        "補充": " ".join(sections["補充"]).strip(),
    }
    
    return result


def _parse_sections_force(text: str) -> dict:
    """
    強制分割：當標準解析失敗時使用
    根據關鍵詞（結論、依據、建議、補充）位置分割
    
    例：「結論xxx依據xxx建議xxx補充xxx」
    """
    sections = {
        "結論": "",
        "依據": "",
        "建議": "",
        "補充": "",
    }
    
    # 找出所有標題的位置
    section_keywords = ["結論", "依據", "建議", "補充"]
    positions = {}
    
    for keyword in section_keywords:
        pos = text.find(keyword)
        if pos != -1:
            positions[keyword] = pos
    
    # 若找不到任何標題，返回空字典
    if not positions:
        return sections
    
    # 按位置排序
    sorted_keywords = sorted(positions.keys(), key=lambda k: positions[k])
    
    # 從每個標題開始，到下一個標題前結束
    for i, keyword in enumerate(sorted_keywords):
        start = positions[keyword] + len(keyword)
        
        # 跳過冒號（如果有）
        if start < len(text) and text[start] in "：:":
            start += 1
        
        # 找出內容的結束位置
        if i + 1 < len(sorted_keywords):
            end = positions[sorted_keywords[i + 1]]
        else:
            end = len(text)
        
        # 提取內容
        content = text[start:end].strip()
        content = re.sub(r"^[:：\s]+", "", content).strip()
        
        sections[keyword] = content
    
    return sections


def _format_text_v1(sections_dict: dict) -> str:
    """
    Version 1 純文本格式：標題獨立一行，內容接下一行，區段用空行分隔
    
    ✨ 關鍵：確保輸出中含有換行符 \n，讓前端正確顯示
    
    結論
    內容...
    
    依據
    內容...
    
    建議
    內容...
    
    補充
    內容...
    """
    lines = []
    
    for key, value in sections_dict.items():
        lines.append(key)        # 標題單獨一行
        
        # 確保內容非空
        if value:
            lines.append(value)  # 內容接下一行
        else:
            lines.append("無")   # 若無內容，寫「無」
        
        lines.append("")         # 區段間加空行（重要！）
    
    # ✨ 關鍵：用 \n 連接，確保換行符存在
    result = "\n".join(lines).strip()
    return result

# 測試
if __name__ == "__main__":
    test = "結論系統是否為高風險應用，需依據目的事業主管機關訂定的風險分類框架判斷；若涉及政府使用，則應進行風險評估與規劃風險因應措施。依據各目的事業主管機關應視人工智慧風險等級訂定管理規範；人工智慧基本法第 5 條、第 16 條、第 17 條建議先確認系統用途、部署場景與風險分類，再依機關規範補足評估與標示。補充暫無相關紀錄"
    result = normalize_answer(test)
    print("=" * 50)
    print(result)
    print("=" * 50)
    print(repr(result))  # 看換行符

