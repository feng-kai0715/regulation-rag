#!/bin/bash

# Regulation_RAG 环境诊断脚本
# 用法: chmod +x diagnose.sh && ./diagnose.sh

echo "=========================================="
echo "Regulation_RAG 环境诊断工具"
echo "=========================================="
echo ""

# 检查系统信息
echo "[系统信息]"
echo "操作系统: $(uname -s)"
echo "系统版本: $(uname -r)"
echo ""

# 1. Python
echo "[1] Python"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✓ $PYTHON_VERSION"
    PYTHON_PATH=$(which python3)
    echo "  位置: $PYTHON_PATH"
else
    echo "❌ Python 未找到"
    exit 1
fi
echo ""

# 2. pip
echo "[2] pip (包管理器)"
if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version)
    echo "✓ $PIP_VERSION"
else
    echo "❌ pip 未找到，请运行: python3 -m ensurepip"
    exit 1
fi
echo ""

# 3. 虚拟环境
echo "[3] 虚拟环境"
VENV_PATH=".venv"
if [ -d "$VENV_PATH" ]; then
    echo "✓ 虚拟环境已存在: $VENV_PATH"
    if [ -f "$VENV_PATH/bin/python" ]; then
        VENV_PYTHON=$("$VENV_PATH/bin/python" --version 2>&1)
        echo "  Python 版本: $VENV_PYTHON"
    fi
else
    echo "⚠ 虚拟环境不存在（运行脚本时自动创建）"
fi
echo ""

# 4. 依赖检查（如虚拟环境已激活）
echo "[4] Python 依赖包"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    
    PACKAGES=(
        "fastapi"
        "uvicorn"
        "langchain"
        "langchain_chroma"
        "chromadb"
        "sentence_transformers"
        "pydantic"
    )
    
    for pkg in "${PACKAGES[@]}"; do
        if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            echo "✓ $pkg"
        else
            echo "❌ $pkg 未安装"
        fi
    done
    deactivate
else
    echo "⚠ 虚拟环境未创建，跳过依赖检查"
fi
echo ""

# 5. Chroma 数据库
echo "[5] ChromaDB"
CHROMA_DB="chroma_db"
if [ -d "$CHROMA_DB" ]; then
    echo "✓ ChromaDB 已存在: $CHROMA_DB"
    SIZE=$(du -sh "$CHROMA_DB" 2>/dev/null | cut -f1)
    echo "  大小: $SIZE"
    if [ -f "$CHROMA_DB/chroma.sqlite3" ]; then
        echo "✓ SQLite 数据库文件存在"
    fi
else
    echo "⚠ ChromaDB 不存在，运行时会自动初始化"
fi
echo ""

# 6. 法规文档
echo "[6] 法规文档"
DOCS_DIR="documents"
if [ -d "$DOCS_DIR" ]; then
    echo "✓ 文档目录存在: $DOCS_DIR"
    FILE_COUNT=$(find "$DOCS_DIR" -type f | wc -l)
    echo "  文件数: $FILE_COUNT"
    find "$DOCS_DIR" -type f -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}'
else
    echo "⚠ 文档目录不存在"
fi
echo ""

# 7. Ollama（可选）
echo "[7] Ollama（LLM 本地推理）"
if command -v ollama &> /dev/null; then
    echo "✓ Ollama 已安装"
    OLLAMA_VERSION=$(ollama --version 2>&1)
    echo "  版本: $OLLAMA_VERSION"
    
    # 检查 Ollama 服务是否运行
    if curl -s http://localhost:11434/api/version &> /dev/null; then
        echo "✓ Ollama 服务正在运行（http://localhost:11434）"
        
        # 列出可用模型
        echo "  已加载的模型:"
        MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o '"name":"[^"]*' | cut -d'"' -f4)
        if [ -z "$MODELS" ]; then
            echo "    无"
        else
            echo "$MODELS" | sed 's/^/    /'
        fi
    else
        echo "⚠ Ollama 已安装但服务未运行"
        echo "  启动: ollama serve"
    fi
else
    echo "⚠ Ollama 未安装（可选）"
    echo "  如需使用本地 LLM，请访问: https://ollama.ai"
fi
echo ""

# 8. 端口检查
echo "[8] 端口可用性"
PORTS=(8000 11434)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠ 端口 $port 已被占用"
    else
        echo "✓ 端口 $port 可用"
    fi
done
echo ""

# 9. 环境变量
echo "[9] 环境变量"
if [ -f ".env" ]; then
    echo "✓ .env 文件存在"
    echo "  内容摘要:"
    grep -v '^#' .env | grep -v '^$' | sed 's/^/    /'
else
    echo "⚠ .env 文件不存在，使用默认配置"
fi
echo ""

# 10. 磁盘空间
echo "[10] 磁盘空间"
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
DISK_AVAILABLE=$(df -h . | tail -1 | awk '{print $4}')
echo "✓ 可用空间: $DISK_AVAILABLE"
echo "  已用比例: $DISK_USAGE"
echo ""

# 最终诊断总结
echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "后续步骤:"
echo "1. 如缺少依赖，运行: pip install -r requirements.txt"
echo "2. 启动 FastAPI 服务: ./start.sh"
echo "3. 访问 http://localhost:8000/docs 查看 API 文档"
echo ""
