import sys
import asyncio
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import generator

SAMPLE_QUESTION = "台灣《人工智慧基本法》正式施行後的罰款金額是多少？"
SAMPLE_CONTEXT = "示範法規內容。" * 20
RUNS = 3


async def run_once(iteration: int) -> None:
    start = time.time()
    first_token_ts = None
    chunks = []

    async for chunk in generator.generate_stream(SAMPLE_QUESTION, SAMPLE_CONTEXT):
        if first_token_ts is None and "text" in chunk:
            first_token_ts = time.time()
        if "text" in chunk:
            chunks.append(chunk["text"])

    ans = "".join(chunks)
    duration = time.time() - start
    first_token = (first_token_ts - start) if first_token_ts is not None else None
    first_token_text = f", first_token={first_token:.3f}s" if first_token is not None else ", first_token=none"
    print(f"[run {iteration}] total={duration:.3f}s{first_token_text}, answer_preview={repr(ans)[:160]}")


async def main() -> None:
    try:
        print("預熱模型...")
        await asyncio.to_thread(generator.prewarm_model)
    except Exception as e:
        print(f"預熱失敗：{type(e).__name__}: {e}")

    for i in range(1, RUNS + 1):
        try:
            await run_once(i)
        except Exception as e:
            print(f"執行失敗（run {i}）：{type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
