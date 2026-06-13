#!/bin/bash

# Regulation_RAG 启动脚本
# 用法: chmod +x start.sh && ./start.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
SRC_DIR="${PROJECT_ROOT}/src"

echo "=========================================="
echo "Regulation_RAG 启动配置"
echo "=========================================="
echo "项目路径: $PROJECT_ROOT"
echo ""

# 1. 检查 Python
echo "[1/6] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装 Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ 找到 $PYTHON_VERSION"
echo ""

# 2. 创建/激活虚拟环境
echo "[2/6] 设置虚拟环境..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "✓ 创建虚拟环境"
else
    echo "✓ 虚拟环境已存在"
fi
source "$VENV_PATH/bin/activate"
echo ""

# 3. 安装依赖
echo "[3/6] 安装依赖..."
pip install --upgrade pip setuptools wheel > /dev/null
pip install -r "${PROJECT_ROOT}/requirements.txt" > /dev/null
echo "✓ 依赖安装完成"
echo ""

# 4. 检查 Chroma 数据库
echo "[4/6] 检查 Chroma 数据库..."
CHROMA_DB="${PROJECT_ROOT}/chroma_db"
if [ -d "$CHROMA_DB" ]; then
    echo "✓ Chroma DB 已存在: $CHROMA_DB"
else
    echo "⚠ Chroma DB 不存在，运行时自动初始化"
fi
echo ""

# 5. 检查 Ollama（可选，用于本地 LLM）
echo "[5/6] 检查 Ollama（可选）..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama 已安装"
    echo "  提示: 请确保 Ollama 服务正在运行（ollama serve）"
else
    echo "⚠ Ollama 未安装（可选）"
    echo "  如需使用本地 LLM，请访问: https://ollama.ai"
fi
echo ""

# 6. 启动 FastAPI 服务
echo "[6/6] 启动 FastAPI 服务..."
echo "=========================================="
echo "✓ 配置完成，启动服务..."
echo ""
echo "服务信息:"
echo "  API: http://localhost:8000"
echo "  文档: http://localhost:8000/docs"
echo "  查询端点: POST /query"
echo "  流式端点: POST /stream_query"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

cd "$SRC_DIR"
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
