#!/bin/bash

echo "=========================================="
echo "Regulation_RAG 快速測試"
echo "=========================================="
echo ""

API_URL="http://localhost:8000"

# 檢查 API 是否運行
echo "[1/3] 檢查 API 連線..."
if ! curl -s "$API_URL/docs" > /dev/null 2>&1; then
    echo "❌ API 未運行"
    echo "   請先執行: ./start.sh"
    exit 1
fi
echo "✅ API 運行中"
echo ""

# 測試查詢
echo "[2/3] 測試查詢..."
RESPONSE=$(curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"臺灣 AI 基本法的目的是什麼?"}')

if echo "$RESPONSE" | grep -q '"answer"'; then
    echo "✅ 查詢成功"
    echo ""
    echo "回答示例:"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo "❌ 查詢失敗"
    echo "回應: $RESPONSE"
    exit 1
fi
echo ""

# 測試快取
echo "[3/3] 測試快取功能..."
QUERY='{"question":"測試快取"}'

START1=$(date +%s%N)
curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d "$QUERY" > /dev/null
TIME1=$(( ($(date +%s%N) - START1) / 1000000 ))

START2=$(date +%s%N)
curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d "$QUERY" > /dev/null
TIME2=$(( ($(date +%s%N) - START2) / 1000000 ))

echo "第一次: ${TIME1}ms"
echo "第二次: ${TIME2}ms"

if [ $TIME2 -lt $((TIME1 / 2)) ]; then
    echo "✅ 快取工作正常"
else
    echo "⚠️  快取速度差異不明顯"
fi
echo ""

echo "=========================================="
echo "✅ 測試完成！系統已準備就緒"
echo "=========================================="
