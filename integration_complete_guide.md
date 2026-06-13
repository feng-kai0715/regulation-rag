# Answer Normalizer 和 Generation Prompt 集成方案

## 📋 **問題分析**

### **原始 answer_normalizer.py 的問題**
```python
❌ 有兩個 normalize_answer() 函數定義（重複）
❌ 第一個函數未完成（中斷）
❌ 邏輯混亂，缺少關鍵部分
```

### **原始 generation_prompt.py 的問題**
```python
⚠️ MAX_TOKENS = 32 太小（只能生成短答案）
⚠️ build_context_note() 邏輯不對
⚠️ GENERATION_PROMPT 定義了但未被使用
⚠️ 缺少 SYSTEM_PROMPT
```

---

## ✅ **修復內容**

### **answer_normalizer_fixed.py**

✨ **改進：**
- 修復重複的函數定義
- 完成邏輯，確保四個部分都有內容
- 改進 `clean_line()` 函數邏輯
- 保留 `extract_content()` 以支持流式輸出

🎯 **功能：**
- 將任意格式的答案轉換為標準的「結論/依據/建議/補充」格式
- 處理異常情況（無相關紀錄）
- 移除 thinking 前綴和多餘空白

### **generation_prompt_improved.py**

✨ **改進：**
- 提高 `MAX_TOKENS` 從 32 → 512（允許更完整的答案）
- 提高 `CONTEXT_TRUNCATE_CHARS` 從 400 → 2000
- 新增完整的 `SYSTEM_PROMPT`（定義 AI 角色）
- 新增 `GENERATION_PROMPT_TEMPLATE`
- 修復 `build_context_note()` 邏輯
- 新增 `get_config()` 和調整函數

🎯 **功能：**
- 集中管理提示詞和模型參數
- 易於調整和實驗
- 支持系統提示詞和用戶提示詞分離

### **main_with_integration.py**

✨ **新增：**
```python
# 導入新模塊
from answer_normalizer import normalize_answer
from generation_prompt import build_chat_kwargs, build_context_note

# 在所有答案返回前進行正規化
answer = make_answer(...)
return normalize_answer(answer)  # ✨ 新增

# 新增調試端點
@app.get("/config")
async def get_config():
    """返回當前系統配置"""
```

---

## 🚀 **迁移步驟（3 步完成）**

### **Step 1：備份舊文件**

```bash
cd ~/Documents/pyhs/Regulation_RAG/src

# 備份現有文件
cp answer_normalizer.py answer_normalizer.py.backup
cp generation_prompt.py generation_prompt.py.backup
cp main.py main.py.backup
```

### **Step 2：複製新文件**

從 `/mnt/user-data/outputs/` 複製三個文件：

```bash
# 複製修復後的模塊
cp /mnt/user-data/outputs/answer_normalizer_fixed.py answer_normalizer.py
cp /mnt/user-data/outputs/generation_prompt_improved.py generation_prompt.py
cp /mnt/user-data/outputs/main_with_integration.py main.py
```

### **Step 3：驗證和測試**

```bash
cd ~/Documents/pyhs/Regulation_RAG
source .venv/bin/activate

# 檢查語法
python -m py_compile src/answer_normalizer.py src/generation_prompt.py src/main.py

# 啟動應用
python src/main.py &
sleep 5

# 測試 API
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "AI 基本法第 3 條是什麼？"}' | python -m json.tool

# 查看配置
curl http://localhost:8000/config | python -m json.tool

# 停止應用
kill %1
```

---

## 📊 **變更對比**

### **answer_normalizer.py**

| 項目 | 原始 | 修復後 |
|------|------|--------|
| 函數數 | 2（重複） | 2（修復） |
| 完整性 | ❌ 不完整 | ✅ 完整 |
| 邏輯清晰度 | 混亂 | 清晰 |
| 文檔 | 無 | 完整 |

### **generation_prompt.py**

| 項目 | 原始 | 改進後 |
|------|------|--------|
| MAX_TOKENS | 32 | **512** (+1500%) |
| CONTEXT_TRUNCATE | 400 | **2000** (+400%) |
| SYSTEM_PROMPT | ❌ 無 | ✅ 有 |
| 邏輯函數 | 4 | **6** |
| 文檔 | 少 | **完整** |

### **main.py**

| 項目 | 原始 | 整合後 |
|------|------|--------|
| answer_normalizer 使用 | ❌ 未使用 | ✅ 使用 |
| generation_prompt 使用 | ⚠️ 部分 | ✅ 完全 |
| 調試端點 | ❌ 無 | ✅ /config |
| 答案品質 | 基礎 | **優化** |

---

## 🎯 **預期改進**

### **立即可見的改進**

✅ **答案格式統一**
- 所有答案都遵循「結論/依據/建議/補充」格式
- 不會有格式不一致的情況

✅ **答案更完整**
- MAX_TOKENS 提高 16 倍，允許更詳細的答案
- 不再被截斷

✅ **提示詞更好**
- 系統提示詞清楚定義 AI 角色
- 更好的指導 LLM 行為

### **可測試的改進**

```bash
# 測試 1：驗證格式統一
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什麼是 AI 基本法？"}' \
  | jq '.answer'

# 預期：必定包含結論/依據/建議/補充四行

# 測試 2：檢查配置
curl http://localhost:8000/config | jq '.generation'

# 預期：max_tokens=512, temperature=0.3, 等等
```

---

## 💡 **論文價值**

這個集成對你的 IDSS 論文特別有意義：

✅ **第 4 章（系統設計）：**
- 可討論「答案正規化層」的設計
- 展示「提示詞工程」的重要性

✅ **第 5 章（實驗結果）：**
- 可比較「有/無正規化」的效果
- 可對比不同提示詞策略的結果

✅ **架構圖：**
```
Query Input
    ↓
Retrieval (retrieval.py)
    ↓
Answer Generation (generator.py + generation_prompt.py)
    ↓
Answer Normalization (answer_normalizer.py) ← 新增優化層
    ↓
Output
```

---

## ⚠️ **注意事項**

### **如果遇到 ImportError**

```bash
# 檢查 src 目錄結構
ls -la ~/Documents/pyhs/Regulation_RAG/src/*.py

# 確認所有模塊都存在：
# - answer_normalizer.py ✅
# - generation_prompt.py ✅
# - main.py ✅
# - embedding.py ✅
# - 等等...
```

### **如果遇到答案格式問題**

```bash
# 檢查 normalize_answer() 是否正確執行
python << 'EOF'
from src.answer_normalizer import normalize_answer

test_answer = "這是一個測試答案"
result = normalize_answer(test_answer)
print(result)
# 應該看到四行：結論、依據、建議、補充
EOF
```

---

## ✅ **完成檢查清單**

- [ ] Step 1：備份舊文件
- [ ] Step 2：複製新文件
- [ ] Step 3a：檢查語法（py_compile）
- [ ] Step 3b：啟動應用
- [ ] Step 3c：測試 /query 端點
- [ ] Step 3d：測試 /config 端點
- [ ] 觀察答案格式是否統一
- [ ] 觀察答案是否更完整

---

## 🎓 **下一步（可選）**

1. **調整提示詞：**
   ```python
   # 編輯 generation_prompt.py 中的 SYSTEM_PROMPT
   # 根據實驗結果優化
   ```

2. **實驗對比：**
   ```python
   # 在 generation_prompt.py 中設定多個提示詞版本
   # 記錄不同提示詞的效果
   ```

3. **收集數據：**
   ```bash
   # 記錄 /config 端點的輸出
   # 用於論文的「系統配置」章節
   ```

