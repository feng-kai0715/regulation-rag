import os

# 禁用 ChromaDB telemetry
os.environ["CHROMA_TELEMETRY_DISABLED"] = "true"

# Optimize CPU usage on i5-12500 with 32GB RAM.
os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "6")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "6")
os.environ.setdefault("TORCH_CPU_THREADS", "6")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import asyncio
import json
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

# Cache & timeout configuration
CACHE_TTL_SECONDS = 1800  # 30 minutes
LLM_TIMEOUT_SECONDS = 3.0

# Content formatting limits
SOURCE_PREVIEW_LIMIT = 200
KEY_POINT_TRUNCATE = 120

# ============================================================================
# PATH SETUP
# ============================================================================

for path in (PROJECT_ROOT, BASE_DIR):
    resolved = str(path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)

# ============================================================================
# IMPORTS
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from embedding import get_embedding_model, preload_embedding
from generator import generate_answer, generate_stream, prewarm_model
from langchain_chroma import Chroma
from schema import QueryRequest, QueryResponse
from retrieval import build_cache_key, build_context, load_query_state
from rule_answers import build_rule_based_answer
from answer_utils import make_answer
from source_formatting import (
    build_source_preview,
    extract_article_label,
    extract_key_point,
    extract_source_path,
)

# ✨ 導入：Version 1 純文本格式化
from answer_normalizer import normalize_answer

# ============================================================================
# GLOBAL STATE
# ============================================================================

db = None
_CACHE: dict[str, dict[str, object]] = {}


# ============================================================================
# LIFECYCLE & APP SETUP
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context: initialize resources on startup."""
    _CACHE.clear()
    preload_embedding()
    _ensure_db()
    await asyncio.to_thread(prewarm_model)
    yield


app = FastAPI(lifespan=lifespan)

# CORS middleware for frontend HTML access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _ensure_db():
    """Initialize ChromaDB if not already loaded."""
    global db
    if db is None:
        db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=get_embedding_model(),
        )


def _get_cached_response(cache_key: str) -> QueryResponse | None:
    """Retrieve cached response if still valid."""
    cached = _CACHE.get(cache_key)
    if not cached:
        return None

    elapsed = time.time() - float(cached["ts"])
    if elapsed < CACHE_TTL_SECONDS:
        return QueryResponse(
            answer=str(cached["answer"]),
            source=str(cached["source"]),
            duration=float(cached["duration"]),
        )

    return None


def _cache_response(cache_key: str, response: QueryResponse):
    """Store response in cache with timestamp."""
    _CACHE[cache_key] = {
        "answer": response.answer,
        "source": response.source,
        "duration": response.duration,
        "ts": time.time(),
    }


def _build_generic_article_answer(results) -> str | None:
    """
    Generate a generic answer from top article retrieval result.
    Returns formatted answer with conclusion, evidence, and suggestion.
    Version 1 格式：純文本，無符號語法
    """
    if not results:
        return None

    top_doc = results[0]
    article_label = extract_article_label(top_doc.page_content)
    key_point = extract_key_point(top_doc.page_content)

    # Build conclusion based on article_label availability
    conclusion = (
        f"已檢索到{article_label}，請優先依該條文判斷。"
        if article_label
        else "已檢索到相關條文，請優先依檢索結果判斷。"
    )

    # Build evidence
    if article_label and key_point:
        evidence = f"{article_label}；{key_point}"
    elif article_label:
        evidence = article_label
    else:
        evidence = "相關法規"

    # Build suggestion based on key_point availability
    suggestion = (
        f"可先依條文重點：{key_point[:KEY_POINT_TRUNCATE]}。"
        if key_point
        else "建議直接查看原文條次與條號。"
    )

    answer = make_answer(conclusion, evidence, suggestion)
    
    # ✨ 正規化為 Version 1 純文本格式
    normalized = normalize_answer(answer)
    return normalized if normalized else None


async def _get_answer_with_fallback(request: QueryRequest, start_ts: float):
    """
    Unified answer retrieval logic: rule-based → generic article → LLM generation.
    ✨ 修復：添加防禦性檢查和詳細日誌
    Returns (answer_text, sources, results, cache_key, response_type, elapsed).
    """
    print(f"📋 [QUERY] {request.question}", file=sys.stderr)
    
    try:
        context, sources, results, law_hint, key = load_query_state(
            request.question, max_k=4
        )
        print(f"  📊 Context: {len(context) if context else 0} chars, Results: {len(results) if results else 0}", 
              file=sys.stderr)
    except Exception as e:
        print(f"  ❌ load_query_state error: {e}", file=sys.stderr)
        raise

    # Try rule-based answer
    try:
        rule_answer = build_rule_based_answer(request.question, results)
        if rule_answer:
            print(f"  ✅ Rule-based answer found", file=sys.stderr)
            normalized = normalize_answer(rule_answer)
            if normalized:
                return normalized, sources, results, key, "rule", time.time() - start_ts
    except Exception as e:
        print(f"  ❌ Rule-based error: {e}", file=sys.stderr)

    # Try generic article answer
    try:
        generic_answer = _build_generic_article_answer(results)
        if generic_answer:
            print(f"  ✅ Generic article answer found", file=sys.stderr)
            return generic_answer, sources, results, key, "generic", time.time() - start_ts
    except Exception as e:
        print(f"  ❌ Generic article error: {e}", file=sys.stderr)

    # No context available
    if not context:
        print(f"  ⚠️  No context, returning fallback", file=sys.stderr)
        fallback = "暫無相關紀錄"
        normalized = normalize_answer(fallback)
        return normalized, sources or "資料庫未找到相符法規", results, key, "empty", time.time() - start_ts

    # LLM generation needed
    print(f"  🤖 Calling LLM generation...", file=sys.stderr)
    try:
        answer = await asyncio.wait_for(
            generate_answer(request.question, context),
            timeout=LLM_TIMEOUT_SECONDS,
        )
        print(f"  ✅ LLM generation completed", file=sys.stderr)
        normalized = normalize_answer(answer)
        return normalized, sources, results, key, "llm", time.time() - start_ts
        
    except asyncio.TimeoutError:
        print(f"  ⏱️  LLM timeout (>{LLM_TIMEOUT_SECONDS}s)", file=sys.stderr)
        fallback = make_answer(
            "系統正在用較慢的模型整理答案，請稍後重試或改用更精準的條文關鍵字。",
            law_hint or "資料庫已找到相關法規，但模型回應超時",
            "若要在 10 秒內取得結果，建議先查條文或使用更明確的問題。",
        )
        normalized = normalize_answer(fallback)
        return normalized, sources, results, key, "llm_timeout", time.time() - start_ts
        
    except Exception as e:
        print(f"  ❌ LLM error: {type(e).__name__}: {e}", file=sys.stderr)
        fallback = f"系統生成錯誤：{type(e).__name__}"
        normalized = normalize_answer(fallback)
        return normalized, sources, results, key, "llm_error", time.time() - start_ts


def _sse_data(payload: dict[str, object]) -> str:
    """Format payload as Server-Sent Event data line."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _stream_answer_lines(
    answer_text: str, start_ts: float, sources, results
):
    """
    Common streaming generator for answer lines.
    Yields SSE events for each line and final completion.
    """
    if answer_text is None:
        answer_text = "暫無相關紀錄"
    
    if not isinstance(answer_text, str):
        answer_text = str(answer_text) if answer_text else "暫無相關紀錄"
    
    yield _sse_data({"event": "start"})

    for line in answer_text.splitlines():
        yield _sse_data({"text": line})

    duration = round(time.time() - start_ts, 3)
    yield _sse_data(
        {
            "event": "done",
            "duration": duration,
            "source": build_source_preview(sources, results),
        }
    )


# ============================================================================
# ROUTES
# ============================================================================


@app.get("/")
async def root_index():
    """Serve frontend index."""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Synchronous query endpoint.
    ✨ 修復：添加例外處理和 None 檢查
    Returns complete answer with sources and execution duration.
    """
    start_ts = time.time()
    
    try:
        answer, sources, results, cache_key, response_type, elapsed = (
            await _get_answer_with_fallback(request, start_ts)
        )
        
        # ✨ 防禦性檢查：確保 answer 不是 None
        if answer is None:
            print(f"⚠️  Warning: answer is None for query '{request.question}'", 
                  file=sys.stderr)
            answer = "暫無相關紀錄"
        
    except Exception as e:
        print(f"❌ Error in _get_answer_with_fallback: {str(e)}", 
              file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        answer = f"系統發生錯誤：{type(e).__name__}"
        sources = "未知"
        results = []
        cache_key = None
        response_type = "error"

    # Check cache for LLM-generated answers only
    if response_type == "llm":
        cached = _get_cached_response(cache_key)
        if cached:
            return cached

    source_preview = build_source_preview(sources, results)
    duration = round(time.time() - start_ts, 3)
    response = QueryResponse(answer=answer, source=source_preview, duration=duration)

    # Cache LLM-generated answers
    if response_type == "llm":
        _cache_response(cache_key, response)

    return response


@app.post("/stream_query")
async def stream_query(request: QueryRequest):
    """
    Streaming query endpoint.
    ✨ 修復：添加例外處理和 None 檢查
    Streams answer lines as Server-Sent Events for real-time display.
    """
    start_ts = time.time()
    
    try:
        answer, sources, results, _, _, _ = await _get_answer_with_fallback(
            request, start_ts
        )
        
        # ✨ 防禦性檢查：確保 answer 不是 None
        if answer is None:
            print(f"⚠️  Warning: answer is None for query '{request.question}'", 
                  file=sys.stderr)
            answer = "暫無相關紀錄"
        
    except Exception as e:
        print(f"❌ Error in _get_answer_with_fallback: {str(e)}", 
              file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        answer = f"系統發生錯誤：{type(e).__name__}"
        sources = "未知"
        results = []

    return StreamingResponse(
        _stream_answer_lines(answer, start_ts, sources, results),
        media_type="text/event-stream",
    )


# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================

@app.get("/config")
async def get_config():
    """
    返回當前系統配置（用於調試）
    """
    from generation_prompt import get_config
    
    return {
        "generation": get_config(),
        "cache": {
            "ttl_seconds": CACHE_TTL_SECONDS,
            "cached_keys": len(_CACHE),
        },
        "timeout_seconds": LLM_TIMEOUT_SECONDS,
        "format": "Version 1 - Pure Text (無符號語法)",
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
