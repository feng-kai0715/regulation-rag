#!/usr/bin/env python3
"""
自動修復 Regulation_RAG 中發現的所有問題
"""

import sys
from pathlib import Path

# ============================================================================
# 配置
# ============================================================================

PROJECT_ROOT = Path.home() / "Documents/pyhs/Regulation_RAG"
SRC_DIR = PROJECT_ROOT / "src"

# 需要修復的文件
FILES_TO_FIX = {
    "main.py": [
        {
            "name": "修復 evidence 的語法錯誤",
            "old": """    evidence = f"{article_label}\\n{key_point}" if article_label and key_point else article_label
# 結果：「第3條\\n本法所稱人工智慧，指...」✅""",
            "new": """    # Build evidence - 包含條文編號和完整內容
    if article_label and key_point:
        evidence = f"{article_label}；{key_point}"
    elif article_label:
        evidence = article_label
    else:
        evidence = "相關法規\"""",
        },
        {
            "name": "修復 generate_answer 的參數（第 1 處）",
            "old": """        answer = await asyncio.wait_for(
            generate_answer(request.question, context, law_hint),
            timeout=LLM_TIMEOUT_SECONDS,
        )""",
            "new": """        answer = await asyncio.wait_for(
            generate_answer(request.question, context),
            timeout=LLM_TIMEOUT_SECONDS,
        )""",
            "first_only": True,  # 只替換第一個出現
        },
    ],
    "rule_answers.py": [
        {
            "name": "修復 extract_article_label 的導入",
            "old": """from retrieval import extract_article_label""",
            "new": """from source_formatting import extract_article_label""",
        },
    ],
}

# ============================================================================
# 修復函數
# ============================================================================

def fix_file(file_path, fixes):
    """
    修復單個文件
    
    Args:
        file_path: 要修復的文件路徑
        fixes: 修復清單
        
    Returns:
        是否成功修復
    """
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return False
    
    print(f"\n📝 修復 {file_path.name}...")
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    
    for fix in fixes:
        fix_name = fix["name"]
        old_text = fix["old"]
        new_text = fix["new"]
        first_only = fix.get("first_only", False)
        
        if old_text in content:
            if first_only:
                # 只替換第一個出現
                content = content.replace(old_text, new_text, 1)
                print(f"  ✅ {fix_name}（第 1 處）")
            else:
                # 替換所有出現
                count = content.count(old_text)
                content = content.replace(old_text, new_text)
                print(f"  ✅ {fix_name}（共 {count} 處）")
        else:
            print(f"  ⚠️  {fix_name} - 未找到對應文本")
            print(f"     期望查找：{old_text[:100]}...")
    
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✅ {file_path.name} 已保存")
        return True
    else:
        print(f"  ℹ️  {file_path.name} 無需修改")
        return False


def verify_syntax(file_path):
    """
    驗證 Python 文件語法
    
    Args:
        file_path: 要檢查的文件
        
    Returns:
        是否語法正確
    """
    import py_compile
    try:
        py_compile.compile(str(file_path), doraise=True)
        print(f"  ✅ 語法檢查通過")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ❌ 語法錯誤：{e}")
        return False


def verify_imports(src_dir):
    """
    驗證模塊導入
    
    Args:
        src_dir: src 目錄
        
    Returns:
        是否導入成功
    """
    sys.path.insert(0, str(src_dir))
    
    print("\n🔍 驗證模塊導入...")
    
    modules = [
        ("main", "main.py"),
        ("rule_answers", "rule_answers.py"),
        ("retrieval", "retrieval.py"),
        ("answer_normalizer", "answer_normalizer.py"),
    ]
    
    all_ok = True
    for module_name, file_name in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {file_name} 導入成功")
        except Exception as e:
            print(f"  ❌ {file_name} 導入失敗：{e}")
            all_ok = False
    
    return all_ok


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主修復流程"""
    
    print("=" * 70)
    print("Regulation_RAG 自動修復工具")
    print("=" * 70)
    
    # 檢查項目路徑
    if not SRC_DIR.exists():
        print(f"\n❌ src 目錄不存在：{SRC_DIR}")
        print(f"請確保你在項目根目錄運行此腳本")
        return False
    
    print(f"\n📂 項目路徑：{PROJECT_ROOT}")
    print(f"📂 src 目錄：{SRC_DIR}")
    
    # 修復所有文件
    print("\n" + "=" * 70)
    print("開始修復...")
    print("=" * 70)
    
    fixed_files = []
    for file_name, fixes in FILES_TO_FIX.items():
        file_path = SRC_DIR / file_name
        if fix_file(file_path, fixes):
            fixed_files.append(file_name)
    
    # 語法驗證
    print("\n" + "=" * 70)
    print("語法驗證")
    print("=" * 70)
    
    syntax_ok = True
    for file_name in FILES_TO_FIX.keys():
        file_path = SRC_DIR / file_name
        print(f"\n檢查 {file_name}...")
        if not verify_syntax(file_path):
            syntax_ok = False
    
    # 導入驗證
    if syntax_ok:
        print("\n" + "=" * 70)
        imports_ok = verify_imports(SRC_DIR)
    else:
        imports_ok = False
    
    # 總結
    print("\n" + "=" * 70)
    print("修復總結")
    print("=" * 70)
    
    if fixed_files:
        print(f"\n✅ 已修復 {len(fixed_files)} 個文件：")
        for file_name in fixed_files:
            print(f"   - {file_name}")
    else:
        print("\nℹ️  無需修復的文件（已經是正確的）")
    
    if syntax_ok:
        print("\n✅ 語法驗證：全部通過")
    else:
        print("\n❌ 語法驗證：有錯誤")
        return False
    
    if imports_ok:
        print("✅ 導入驗證：全部通過")
    else:
        print("❌ 導入驗證：有錯誤")
        return False
    
    print("\n" + "=" * 70)
    print("✅ 修復完成！")
    print("=" * 70)
    
    print("\n下一步：")
    print("1. 啟動應用：python src/main.py")
    print("2. 測試查詢：curl -X POST http://localhost:8000/query ...")
    print("3. 查看配置：curl http://localhost:8000/config")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
