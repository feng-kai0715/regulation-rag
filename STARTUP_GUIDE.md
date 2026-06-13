# Regulation_RAG 终端启动完整指南

## 项目概述

Regulation_RAG 是一个基于 FastAPI + ChromaDB + LangChain 的 RAG（检索增强生成）系统，用于查询和解释臺灣 AI 基本法相关的法规。

**项目结构：**
```
Regulation_RAG/
├── src/                  # 源代码
│   ├── main.py          # FastAPI 主应用
│   ├── embedding.py     # 嵌入模型管理
│   ├── generator.py     # LLM 生成逻辑
│   ├── schema.py        # 数据模型
│   ├── ingest.py        # 数据摄入
│   └── static/          # 前端静态文件
├── chroma_db/           # 向量数据库
├── documents/           # 法规文档（PDF/TXT）
├── scripts/             # 工具脚本
└── requirements.txt     # Python 依赖
```

---

## 1. 环境准备

### macOS

```bash
# 1.1 安装 Homebrew（如未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 1.2 安装 Python 3.11
brew install python@3.11
python3 --version  # 确认版本

# 1.3 安装 Ollama（可选，用于本地 LLM）
brew install ollama
# 或访问 https://ollama.ai 下载

# 1.4 克隆/进入项目
cd ~/文件/Regulation_RAG
```

### Windows

```cmd
# 1.1 检查是否已安装 Python
python --version

# 1.2 如未安装，从 https://python.org 下载并安装
# 安装时勾选 "Add Python to PATH"

# 1.3 安装 Ollama（可选）
# 访问 https://ollama.ai 下载 Windows 版本

# 1.4 进入项目目录
cd %USERPROFILE%\...\Regulation_RAG
```

### Linux (Ubuntu/Debian)

```bash
# 1.1 更新包管理器
sudo apt update

# 1.2 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# 1.3 安装 Ollama（可选）
curl -fsSL https://ollama.ai/install.sh | sh

# 1.4 进入项目
cd ~/Regulation_RAG
```

---

## 2. 快速启动

### 最简单的方法：运行启动脚本

**macOS / Linux：**
```bash
chmod +x start.sh
./start.sh
```

**Windows：**
```cmd
start.bat
```

启动脚本会自动：
- ✓ 检查 Python 版本
- ✓ 创建虚拟环境（`.venv`）
- ✓ 安装依赖（从 `requirements.txt`）
- ✓ 检查 ChromaDB 和 Ollama
- ✓ 启动 FastAPI 服务

---

## 3. 手动启动步骤

如果不想使用脚本，可以手动执行：

### 步骤 1：创建虚拟环境

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 步骤 2：安装依赖

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 步骤 3：配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，根据你的设置修改：
# - LLM_PROVIDER: ollama 或 anthropic
# - OLLAMA_MODEL: 使用的模型名称
# - CHROMA_DB_PATH: ChromaDB 路径
```

### 步骤 4：启动 Ollama（如使用本地 LLM）

```bash
# 在新的终端窗口运行
ollama serve

# 拉取所需模型（首次运行）
ollama pull gemma2:2b
# 或更大的模型：
# ollama pull qwen:7b
# ollama pull gemma4:e4b
```

### 步骤 5：启动 FastAPI 服务

```bash
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

成功启动后会看到：
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## 4. 验证服务运行

### 测试 API 是否运行

```bash
# 在另一个终端窗口测试
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"臺灣 AI 基本法的目的是什麼?"}'
```

### 访问交互式文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 5. 前端集成

### 选项 A：使用静态 HTML（推荐简单情况）

1. 将 `frontend-client-example.js` 复制到 `src/static/` 目录

2. 创建 `src/static/index.html`：
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="UTF-8">
       <title>Regulation_RAG</title>
   </head>
   <body>
       <h1>查詢臺灣 AI 基本法</h1>
       <input type="text" id="question" placeholder="输入问题...">
       <button onclick="queryAPI()">查询</button>
       <div id="result"></div>
       
       <script src="rag-client.js"></script>
       <script>
           const client = new RAGClient("http://localhost:8000");
           async function queryAPI() {
               const q = document.getElementById("question").value;
               const res = await client.query(q);
               document.getElementById("result").innerHTML = 
                   `<p>${res.answer}</p><p>来源: ${res.source}</p>`;
           }
       </script>
   </body>
   </html>
   ```

3. FastAPI 会自动在 `http://localhost:8000/` 提供 `index.html`

### 选项 B：使用 React/Vue 等现代框架

```javascript
// 在你的框架中导入客户端
import RAGClient from "./rag-client.js";

// 在组件中使用
const client = new RAGClient(process.env.REACT_APP_API_URL);

// 发送查询
const handleQuery = async (question) => {
  const result = await client.query(question);
  setResponse(result);
};
```

---

## 6. 常见问题排查

### ❌ "ModuleNotFoundError: No module named 'fastapi'"

**解决：**
```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### ❌ "Connection refused: http://localhost:11434"

**原因：** Ollama 服务未启动

**解决：**
```bash
# 在新终端启动 Ollama
ollama serve

# 或改用 Claude API（需要 API Key）
# 编辑 .env 设置 LLM_PROVIDER=anthropic
```

### ❌ "ChromaDB not found"

**解决：**
```bash
# 运行数据摄入脚本
cd scripts
python ingest.py

# 或检查路径
ls -la ../chroma_db/
```

### ❌ 前端无法连接到 API

**检查清单：**
- ✓ FastAPI 服务在运行吗？（http://localhost:8000/docs）
- ✓ 前端 API URL 是否正确？（应为 http://localhost:8000）
- ✓ 浏览器控制台是否有 CORS 错误？
  - FastAPI 已配置 CORS，应该可以跨域访问

**测试连接：**
```javascript
// 在浏览器控制台运行
fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: 'test' })
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e))
```

---

## 7. 性能优化

### 使用更好的嵌入模型

编辑 `.env`：
```env
EMBEDDING_MODEL=intfloat/multilingual-e5-large-instruct
```

### 使用更强大的本地 LLM

```bash
# 下载更大的模型（需要更多 VRAM）
ollama pull qwen:14b
ollama pull llama2:13b

# 编辑 .env
OLLAMA_MODEL=qwen:14b
```

### 调整查询参数

```env
# 增加检索的相关文档数
RETRIEVAL_K=5

# 增加缓存 TTL
CACHE_TTL_SECONDS=600
```

---

## 8. 部署到远程服务器

### 使用 Gunicorn + Nginx

```bash
# 安装生产服务器
pip install gunicorn

# 启动（后台）
nohup gunicorn -w 4 -b 0.0.0.0:8000 \
    --chdir src main:app > rag.log 2>&1 &

# 配置 Nginx 反向代理...
```

### 使用 Docker（推荐）

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t regulation-rag .
docker run -p 8000:8000 regulation-rag
```

---

## 9. 进一步学习

- **FastAPI 文档**: https://fastapi.tiangolo.com
- **LangChain 文档**: https://python.langchain.com
- **ChromaDB 文档**: https://docs.trychroma.com
- **Ollama 模型库**: https://ollama.ai/library

---

## 快速命令参考

```bash
# 启动服务
./start.sh                          # 自动启动（macOS/Linux）
start.bat                           # 自动启动（Windows）

# 手动启动
source .venv/bin/activate           # 激活虚拟环境
python -m uvicorn main:app \
  --host 127.0.0.1 --port 8000

# 测试 API
curl http://localhost:8000/docs     # 打开文档
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"你的问题"}'

# 停止服务
Ctrl+C                              # 在终端按 Ctrl+C

# 停用虚拟环境
deactivate                          # (bash/zsh)
.venv\Scripts\deactivate.bat        # (Windows)
```

---

祝你使用愉快！有问题可查看终端错误日志或检查 http://localhost:8000/docs 了解 API 细节。
