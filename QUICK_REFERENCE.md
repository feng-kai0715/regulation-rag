# Regulation_RAG 启动配置包 - 快速参考

## 📦 生成的文件说明

### 核心文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `requirements.txt` | 依赖管理 | 所有 Python 包及版本 |
| `start.sh` | 启动脚本 | macOS/Linux 一键启动 |
| `start.bat` | 启动脚本 | Windows 一键启动 |
| `.env.example` | 环境配置示例 | 复制为 `.env` 后修改 |

### 参考与诊断

| 文件 | 用途 | 说明 |
|------|------|------|
| `STARTUP_GUIDE.md` | 完整指南 | 详细的启动和配置说明 |
| `diagnose.sh` | 诊断工具 | macOS/Linux 环境诊断 |
| `diagnose.bat` | 诊断工具 | Windows 环境诊断 |
| `frontend-client-example.js` | 前端集成 | JavaScript API 客户端 |

---

## 🚀 快速启动（3 步）

### 方案 A：自动启动（推荐）

**macOS / Linux：**
```bash
cd ~/文件/Regulation_RAG
chmod +x start.sh
./start.sh
```

**Windows：**
```cmd
cd %USERPROFILE%\...\Regulation_RAG
start.bat
```

### 方案 B：手动启动

```bash
# 1. 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 2. 启动 FastAPI
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## ✅ 启动检查清单

启动前确保：

- [ ] Python 3.8+ 已安装
- [ ] 项目目录在 `~/文件/Regulation_RAG`
- [ ] `requirements.txt` 在项目根目录
- [ ] Chroma 数据库在 `chroma_db/` 目录
- [ ] 法规文档在 `documents/` 目录
- [ ] (可选) Ollama 已安装并运行（`ollama serve`）

---

## 📊 诊断与故障排查

### 运行诊断工具

**macOS / Linux：**
```bash
chmod +x diagnose.sh
./diagnose.sh
```

**Windows：**
```cmd
diagnose.bat
```

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| `ModuleNotFoundError: No module named 'fastapi'` | 运行 `pip install -r requirements.txt` |
| `Connection refused: http://localhost:11434` | 启动 Ollama（`ollama serve`） 或改用 Claude API |
| `ChromaDB not found` | 运行 `python scripts/ingest.py` |
| 前端无法连接 API | 检查 CORS 配置，验证端口 8000 是否开放 |

---

## 🌐 前端集成

### 快速例子

```html
<!-- 在你的 HTML 中 -->
<script src="frontend-client-example.js"></script>

<input type="text" id="question" placeholder="输入问题...">
<button onclick="submitQuery()">查询</button>
<div id="result"></div>

<script>
  const client = new RAGClient("http://localhost:8000");
  
  async function submitQuery() {
    const q = document.getElementById("question").value;
    const res = await client.query(q);
    document.getElementById("result").innerHTML = `
      <p>${res.answer}</p>
      <p>相关条文: ${res.source}</p>
      <p>耗时: ${res.duration}秒</p>
    `;
  }
</script>
```

### API 端点

```bash
# 非流式查询
POST http://localhost:8000/query
Content-Type: application/json
{"question": "你的问题"}

# 流式查询
POST http://localhost:8000/stream_query
# 返回 Server-Sent Events (SSE)
```

---

## 🔧 环境变量配置

复制 `.env.example` 为 `.env`，然后根据需要修改：

```env
# LLM 选择
LLM_PROVIDER=ollama           # 或 anthropic

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:2b        # 或 qwen:7b, llama2:13b

# 或 Claude API
# ANTHROPIC_API_KEY=sk-ant-...

# 嵌入模型
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# 查询参数
RETRIEVAL_K=3
CACHE_TTL_SECONDS=300
```

---

## 📖 详细指南

完整的启动、配置和故障排查指南请参考 `STARTUP_GUIDE.md`

---

## 🎯 验证服务运行

### 打开 API 文档

访问浏览器：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 测试 API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"臺灣 AI 基本法的目的是什麼?"}'
```

---

## 📁 项目结构

```
Regulation_RAG/
├── src/
│   ├── main.py              # FastAPI 应用入口
│   ├── embedding.py         # 嵌入模型
│   ├── generator.py         # LLM 生成逻辑
│   ├── schema.py            # 数据模型
│   ├── ingest.py            # 数据摄入
│   └── static/              # 前端（HTML/CSS/JS）
├── chroma_db/               # 向量数据库
├── documents/               # 法规文档
├── scripts/                 # 工具脚本
├── requirements.txt         # 依赖清单
├── start.sh / start.bat     # 启动脚本
├── diagnose.sh / diagnose.bat # 诊断脚本
└── .env                     # 环境变量（复制自 .env.example）
```

---

## 💡 性能优化建议

### 使用更大的模型

```bash
# 下载更强大的模型
ollama pull qwen:14b
ollama pull llama2:13b

# 在 .env 中配置
OLLAMA_MODEL=qwen:14b
```

### 增加嵌入模型质量

```env
# 更高质量的多语言嵌入
EMBEDDING_MODEL=intfloat/multilingual-e5-large-instruct
```

### 提高查询精度

```env
# 增加检索文档数
RETRIEVAL_K=5

# 增加缓存时间
CACHE_TTL_SECONDS=600
```

---

## 🆘 获取帮助

### 查看日志

启动脚本运行时会显示详细日志，包括：
- 依赖加载情况
- 模型初始化状态
- API 请求/响应日志

### 检查常见问题

1. **Python 版本**：确保 >= 3.8
2. **网络连接**：检查 Ollama 或 Claude API 连接
3. **端口冲突**：运行诊断工具检查端口可用性
4. **磁盘空间**：确保有足够空间存储模型和数据库

---

## 📝 许可证和引用

Regulation_RAG 用于学术研究（IDSS 论文）。

主要依赖：
- FastAPI
- LangChain
- ChromaDB
- Sentence Transformers
- Ollama（本地 LLM）

---

**最后更新**: 2026-06-05
**维护者**: Kai（IDSS 论文项目）
