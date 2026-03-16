from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from rag.context_manager import ContextManager
from llm.llama_engine import LlamaEngine
from routers import ai

# 初始化全局组件
context_manager = ContextManager(
    chromadb_path=os.getenv("CHROMADB_PATH", "./database/chromadb"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
)

llm_engine = LlamaEngine(
    model_path=os.getenv("LLM_MODEL_PATH", "./models/llm/model.gguf"),
    n_ctx=2048,
    n_gpu_layers=0  # CPU模式
)

app = FastAPI(
    title="AI-RPG AI Engine",
    description="AI推理服务 - RAG系统、LLM推理、角色扮演引擎",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("✅ AI Engine Service Started")
    print(f"📚 ChromaDB路径: {context_manager.chromadb_path}")
    print(f"🤖 LLM模型路径: {llm_engine.model_path}")


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "service": "ai-engine",
        "components": {
            "context_manager": "initialized",
            "llm_engine": "initialized"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
