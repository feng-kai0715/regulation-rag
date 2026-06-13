/**
 * Regulation_RAG 前端 API 客户端
 * 用于在网页中与 FastAPI 后端通信
 */

class RAGClient {
  constructor(apiBaseUrl = "http://localhost:8000") {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * 发送查询请求（非流式）
   * @param {string} question - 查询问题
   * @returns {Promise<{answer: string, source: string, duration: number}>}
   */
  async query(question) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`API 错误: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("查询失败:", error);
      throw error;
    }
  }

  /**
   * 发送流式查询请求
   * @param {string} question - 查询问题
   * @param {Function} onChunk - 接收每个流块时的回调
   * @param {Function} onComplete - 完成时的回调
   */
  async streamQuery(question, onChunk, onComplete) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/stream_query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`API 错误: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          if (buffer.trim()) {
            try {
              const event = JSON.parse(buffer);
              onChunk(event);
            } catch (e) {
              console.warn("无法解析最后一个事件:", e);
            }
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // 处理 SSE 消息
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const event = JSON.parse(line.substring(6));
              onChunk(event);

              // 处理完成事件
              if (event.event === "done") {
                if (onComplete) {
                  onComplete({
                    duration: event.duration,
                    source: event.source,
                  });
                }
              }
            } catch (e) {
              console.warn("无法解析事件:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("流式查询失败:", error);
      throw error;
    }
  }
}

// ===== 使用示例 =====

// 创建客户端实例
const client = new RAGClient("http://localhost:8000");

// 例1: 非流式查询
async function exampleBasicQuery() {
  try {
    const question = "臺灣 AI 基本法的目的是什麼?";
    console.log("正在查询:", question);

    const result = await client.query(question);

    console.log("回答:", result.answer);
    console.log("相關條文:", result.source);
    console.log("耗時:", result.duration, "秒");
  } catch (error) {
    console.error("查询失败:", error);
  }
}

// 例2: 流式查询（逐字显示）
async function exampleStreamQuery() {
  try {
    const question = "AI 模型的監管要求是什麼?";
    console.log("正在查询:", question);

    let fullAnswer = "";

    await client.streamQuery(
      question,
      (event) => {
        if (event.text) {
          process.stdout.write(event.text); // 逐字输出
          fullAnswer += event.text;
        }
        if (event.error) {
          console.error("错误:", event.error);
        }
        if (event.event === "start") {
          console.log("開始生成回答...");
        }
      },
      (metadata) => {
        console.log("\n\n完成！");
        console.log("耗時:", metadata.duration, "秒");
        console.log("相關條文:", metadata.source);
      }
    );
  } catch (error) {
    console.error("流式查询失败:", error);
  }
}

// ===== 前端 HTML 集成示例 =====

// 在 HTML 中使用（examples/index.html）
const htmlExample = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Regulation_RAG 查詢介面</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .query-box { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; cursor: pointer; }
        .result { 
            border: 1px solid #ccc; 
            padding: 15px; 
            margin-top: 20px;
            border-radius: 5px;
        }
        .source { color: #666; font-size: 12px; margin-top: 10px; }
        .loading { color: #0066cc; font-weight: bold; }
    </style>
</head>
<body>
    <h1>臺灣 AI 基本法 RAG 查詢系統</h1>
    
    <div class="query-box">
        <input 
            type="text" 
            id="questionInput" 
            placeholder="輸入您的問題..."
            onkeypress="if(event.key==='Enter') submitQuery()"
        >
        <button onclick="submitQuery()">查詢</button>
        <button onclick="streamQuery()">串流查詢</button>
    </div>

    <div id="result"></div>

    <script src="rag-client.js"></script>
    <script>
        const client = new RAGClient("http://localhost:8000");

        async function submitQuery() {
            const question = document.getElementById("questionInput").value.trim();
            if (!question) return;

            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = '<p class="loading">正在查詢...</p>';

            try {
                const result = await client.query(question);
                resultDiv.innerHTML = \`
                    <div class="result">
                        <h3>回答:</h3>
                        <p>\${result.answer}</p>
                        <div class="source">
                            <strong>相關條文:</strong>
                            <p>\${result.source}</p>
                            <p>耗時: \${result.duration}秒</p>
                        </div>
                    </div>
                \`;
            } catch (error) {
                resultDiv.innerHTML = \`<p style="color: red;">查詢失敗: \${error.message}</p>\`;
            }
        }

        async function streamQuery() {
            const question = document.getElementById("questionInput").value.trim();
            if (!question) return;

            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = '<p class="loading">正在生成回答...</p>';

            let fullAnswer = "";
            try {
                await client.streamQuery(
                    question,
                    (event) => {
                        if (event.text) {
                            fullAnswer += event.text;
                            resultDiv.innerHTML = \`
                                <div class="result">
                                    <h3>回答:</h3>
                                    <p>\${fullAnswer}</p>
                                </div>
                            \`;
                        }
                    },
                    (metadata) => {
                        resultDiv.innerHTML = \`
                            <div class="result">
                                <h3>回答:</h3>
                                <p>\${fullAnswer}</p>
                                <div class="source">
                                    <strong>相關條文:</strong>
                                    <p>\${metadata.source}</p>
                                    <p>耗時: \${metadata.duration}秒</p>
                                </div>
                            </div>
                        \`;
                    }
                );
            } catch (error) {
                resultDiv.innerHTML = \`<p style="color: red;">查詢失敗: \${error.message}</p>\`;
            }
        }
    </script>
</body>
</html>
`;
