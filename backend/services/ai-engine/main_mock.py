"""
AI Engine - Mock 模式（可行性测试用）
跳过 llama.cpp / chromadb / sentence-transformers，仅用 fastapi + uvicorn 验证路由层。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncIterator
import uvicorn
import asyncio
import json
import os

app = FastAPI(
    title="AI-RPG AI Engine [MOCK]",
    description="Mock AI 推理服务 - 可行性测试专用",
    version="0.1.0-mock"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 请求/响应模型 ────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    character_id: Optional[str] = "1"
    scene_id: Optional[str] = "main"
    history: Optional[list] = []

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

# ── 健康检查 ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "mode": "mock",
        "components": {
            "context_manager": "mock",
            "llm_engine": "mock"
        }
    }

# ── AI 对话接口 ───────────────────────────────────────────

@app.post("/api/v1/ai/chat")
async def chat(req: ChatRequest):
    """同步对话 - Mock 响应"""
    return {
        "response": f"[MOCK] 我收到了你的消息：'{req.message}'。（这是可行性测试的 mock 回复，真实 LLM 尚未加载）",
        "character_id": req.character_id,
        "scene_id": req.scene_id,
        "tokens_used": 42,
        "model": "mock-llm"
    }

@app.post("/api/v1/ai/chat/stream")
async def chat_stream(req: ChatRequest):
    """流式对话 - Mock SSE 响应"""
    async def generate() -> AsyncIterator[str]:
        words = f"[MOCK] 我收到了：'{req.message}'，这是流式 mock 测试回复。".split()
        for word in words:
            chunk = {"delta": word + " ", "done": False}
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.05)
        yield f"data: {json.dumps({'delta': '', 'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/v1/ai/generate")
async def generate(req: GenerateRequest):
    """文本生成 - Mock 响应"""
    return {
        "text": f"[MOCK] 针对提示词 '{req.prompt[:30]}...' 的生成结果（mock）",
        "tokens_used": 64,
        "model": "mock-llm"
    }

# ── RAG 接口 ─────────────────────────────────────────────

@app.post("/api/v1/ai/rag/query")
async def rag_query(req: RAGQueryRequest):
    """RAG 检索 - Mock 响应"""
    return {
        "results": [
            {"content": f"Mock 检索结果 #{i+1}：与 '{req.query}' 相关的世界观片段", "score": 0.9 - i * 0.1}
            for i in range(min(req.top_k, 3))
        ],
        "query": req.query
    }

@app.post("/api/v1/ai/rag/add")
async def rag_add(payload: dict):
    return {"status": "ok", "message": "mock: document added", "id": "mock-doc-001"}

# ── 增强 AI 接口（enhanced_ai.py 的路由）────────────────

@app.post("/api/v1/ai/enhanced/chat")
async def enhanced_chat(req: ChatRequest):
    return {
        "response": f"[MOCK-ENHANCED] 增强对话回复：'{req.message}'",
        "context_used": True,
        "rag_hits": 2
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run("main_mock:app", host="0.0.0.0", port=port, reload=False)
