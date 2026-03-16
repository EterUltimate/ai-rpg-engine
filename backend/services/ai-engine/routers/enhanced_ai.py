"""
增强版AI路由 - 整合RAG和游戏逻辑
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.enhanced_rag import EnhancedRAGSystem
from llm.llama_engine import LlamaEngine
from roleplay.engine import AIStoryteller, NPC_PERSONAS

router = APIRouter()

# 初始化AI系统
rag_system = EnhancedRAGSystem(
    chromadb_path=os.getenv("CHROMADB_PATH", "./database/chromadb"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    use_reranker=True
)

llm_engine = LlamaEngine(
    model_path=os.getenv("LLM_MODEL_PATH", "./models/llm/model.gguf"),
    n_ctx=2048,
    n_gpu_layers=0
)

storyteller = AIStoryteller(llm_engine, rag_system)


class ChatRequest(BaseModel):
    message: str
    character_id: str
    scene_id: str
    npc_id: Optional[str] = None
    game_context: Optional[Dict[str, Any]] = None


class GenerateRequest(BaseModel):
    type: str
    context: Optional[Dict[str, Any]] = None


@router.post("/ai/chat")
async def chat(request: ChatRequest):
    """AI对话接口 - 支持RAG和角色扮演"""
    try:
        # 如果指定了NPC,使用NPC人设
        npc_persona = None
        if request.npc_id and request.npc_id in NPC_PERSONAS:
            npc_persona = NPC_PERSONAS[request.npc_id]
        
        # 生成响应
        response = await storyteller.generate_response(
            user_input=request.message,
            character_id=request.character_id,
            scene_id=request.scene_id,
            game_context=request.game_context,
            npc_persona=npc_persona
        )
        
        return {
            "response": response,
            "character_id": request.character_id,
            "scene_id": request.scene_id,
            "npc_id": request.npc_id
        }
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/chat/stream")
async def chat_stream(
    message: str,
    character_id: str,
    scene_id: str,
    npc_id: Optional[str] = None
):
    """流式对话接口"""
    
    async def event_stream():
        try:
            # 获取NPC人设
            npc_persona = None
            if npc_id and npc_id in NPC_PERSONAS:
                npc_persona = NPC_PERSONAS[npc_id]
            
            # 流式生成
            async for chunk in storyteller.stream_response(
                user_input=message,
                character_id=character_id,
                scene_id=scene_id,
                npc_persona=npc_persona
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


@router.post("/ai/generate")
async def generate_content(request: GenerateRequest):
    """生成游戏内容"""
    try:
        if request.type == "quest":
            result = await storyteller.generate_quest_description(
                quest_type=request.context.get("quest_type", "side"),
                difficulty=request.context.get("difficulty", "medium"),
                theme=request.context.get("theme", "adventure")
            )
            return result
        
        elif request.type == "scene":
            description = await storyteller.generate_scene_description(
                scene_name=request.context.get("name", "未知场景"),
                scene_type=request.context.get("type", "town")
            )
            return {"description": description}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")
    
    except Exception as e:
        print(f"❌ Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/memory/{character_id}")
async def get_character_memory(character_id: str):
    """获取角色记忆摘要"""
    try:
        summary = await rag_system.get_character_summary(character_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/memory/add")
async def add_memory(
    character_id: str,
    content: str,
    memory_type: str = "event",
    importance: int = 5
):
    """手动添加记忆"""
    try:
        memory_id = await rag_system.add_memory(
            collection_name="character_memories",
            content=content,
            metadata={
                "character_id": character_id,
                "type": memory_type,
                "importance": importance
            }
        )
        
        return {
            "success": True,
            "memory_id": memory_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/stats")
async def get_rag_stats():
    """获取RAG系统统计信息"""
    try:
        stats = rag_system.get_collection_stats()
        return {
            "collections": stats,
            "embedding_model": rag_system.embedding_model_name,
            "reranker_enabled": rag_system.use_reranker
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/world/add")
async def add_world_knowledge(
    content: str,
    category: str = "general"
):
    """添加世界知识"""
    try:
        memory_id = await rag_system.add_memory(
            collection_name="world_knowledge",
            content=content,
            metadata={
                "category": category,
                "source": "manual"
            }
        )
        
        return {
            "success": True,
            "memory_id": memory_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/scene/add")
async def add_scene_context(
    scene_id: str,
    content: str,
    scene_type: str = "location"
):
    """添加场景上下文"""
    try:
        memory_id = await rag_system.add_memory(
            collection_name="scene_contexts",
            content=content,
            metadata={
                "scene_id": scene_id,
                "type": scene_type
            }
        )
        
        return {
            "success": True,
            "memory_id": memory_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
