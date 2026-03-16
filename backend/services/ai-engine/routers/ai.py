from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.context_manager import ContextManager
from llm.llama_engine import LlamaEngine
from main import context_manager, llm_engine

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    character_id: str
    scene_id: str
    stream: Optional[bool] = False


class GenerateRequest(BaseModel):
    type: str  # quest, npc, item, dialogue
    context: Optional[dict] = None


@router.post("/ai/chat")
async def chat(request: ChatRequest):
    """AI对话接口"""
    try:
        # 构建系统提示词
        system_prompt = """你是一个RPG游戏中的角色扮演AI。你的职责是:
1. 根据玩家的行动生成有趣的剧情和对话
2. 维护游戏世界的连贯性和沉浸感
3. 创造富有挑战性和趣味性的游戏体验
4. 根据玩家选择动态调整剧情走向

请用生动有趣的方式回应玩家的行动,保持角色一致性,并推动故事发展。"""

        # 获取上下文
        context = await context_manager.build_context(
            request.message,
            request.character_id,
            request.scene_id
        )
        
        # 构建完整提示词
        full_prompt = llm_engine.build_prompt(
            system_prompt,
            context,
            request.message
        )
        
        # 生成响应
        response = llm_engine.generate(
            full_prompt,
            max_tokens=512,
            temperature=0.8
        )
        
        # 保存对话到记忆
        await context_manager.add_memory(
            request.character_id,
            f"玩家: {request.message}\nAI: {response}",
            importance=5,
            memory_type="dialogue"
        )
        
        return {"response": response}
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/chat/stream")
async def chat_stream(
    message: str,
    character_id: str,
    scene_id: str
):
    """流式对话接口"""
    
    async def event_stream():
        try:
            # 构建提示词
            system_prompt = "你是一个RPG游戏AI助手。"
            context = await context_manager.build_context(
                message,
                character_id,
                scene_id
            )
            
            full_prompt = llm_engine.build_prompt(
                system_prompt,
                context,
                message
            )
            
            # 流式生成
            for chunk in llm_engine.stream_generate(full_prompt, max_tokens=256):
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
            prompt = "生成一个有趣的RPG任务:"
        elif request.type == "npc":
            prompt = "生成一个NPC角色的对话:"
        elif request.type == "item":
            prompt = "生成一个游戏物品的描述:"
        elif request.type == "dialogue":
            prompt = "生成一段NPC对话:"
        else:
            raise HTTPException(status_code=400, detail="Invalid type")
        
        if request.context:
            prompt += f"\n上下文: {request.context}"
        
        content = llm_engine.generate(prompt, max_tokens=256)
        
        return {
            "type": request.type,
            "content": content
        }
    
    except Exception as e:
        print(f"❌ Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/rag/add")
async def add_to_rag(
    collection: str,
    content: str,
    metadata: Optional[dict] = None
):
    """添加内容到RAG系统"""
    try:
        embedding = context_manager.embed_text(content)
        
        context_manager.collections[collection].add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}],
            ids=[f"{collection}_{len(context_manager.collections[collection].get()['ids'])}"]
        )
        
        return {"success": True, "message": "Content added to RAG system"}
    
    except Exception as e:
        print(f"❌ Add to RAG error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
