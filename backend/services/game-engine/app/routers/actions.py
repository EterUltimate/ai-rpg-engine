"""
游戏动作路由
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.game_logic.game_manager import game_manager
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


class ActionRequest(BaseModel):
    character_id: str
    action_type: str
    target: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


@router.post("/actions/perform")
async def perform_action(
    request: ActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """执行游戏动作"""
    result = await game_manager.perform_action(
        character_id=request.character_id,
        action_type=request.action_type,
        target=request.target,
        parameters=request.parameters,
        db=db
    )
    
    return result


@router.get("/actions/available/{character_id}")
async def get_available_actions(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取可用动作列表"""
    # 获取角色当前场景
    character = await game_manager.get_character(character_id, db)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    scene_id = character.get("scene_id", "village_001")
    
    # 获取可用动作
    actions = game_manager.get_available_actions(scene_id, character_id)
    
    return {
        "character_id": character_id,
        "scene_id": scene_id,
        "available_actions": actions
    }


@router.post("/actions/move")
async def move_character(
    character_id: str,
    target_scene: str,
    db: AsyncSession = Depends(get_db)
):
    """移动角色到新场景"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="move",
        target=target_scene,
        db=db
    )
    
    return result


@router.post("/actions/talk")
async def talk_to_npc(
    character_id: str,
    npc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """与NPC交谈"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="talk",
        target=npc_id,
        db=db
    )
    
    return result


@router.post("/actions/investigate")
async def investigate_scene(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """调查当前场景"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="investigate",
        db=db
    )
    
    return result


@router.post("/actions/rest")
async def rest_character(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """休息恢复"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="rest",
        db=db
    )
    
    return result


@router.post("/actions/quest/accept")
async def accept_quest(
    character_id: str,
    quest_id: str,
    db: AsyncSession = Depends(get_db)
):
    """接受任务"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="accept_quest",
        target=quest_id,
        db=db
    )
    
    return result


@router.post("/actions/quest/complete")
async def complete_quest(
    character_id: str,
    quest_id: str,
    db: AsyncSession = Depends(get_db)
):
    """完成任务"""
    result = await game_manager.perform_action(
        character_id=character_id,
        action_type="complete_quest",
        target=quest_id,
        db=db
    )
    
    return result


# ── AI 对话专用路由 ─────────────────────────────────────────────────────────

class TalkAIRequest(BaseModel):
    """AI 对话请求体"""
    character_id: str
    npc_id: Optional[str] = None          # 与 NPC 对话时必填；省略则走"叙述者"模式
    message: str                           # 玩家输入的文字
    scene_id: Optional[str] = None        # 可选，留空时从角色当前位置推断


@router.post("/actions/talk-ai")
async def talk_ai(
    request: TalkAIRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI 驱动的 NPC 对话（同步版）。

    - 若提供 npc_id，走 game_manager.perform_action(action_type="talk")，
      action_handler 内部会调用 ai-engine 获取 NPC 角色回复。
    - 若不提供 npc_id，直接调用 ai-engine /chat，以叙述者模式生成场景描述。

    响应额外携带 ai_used / fallback 标志，方便前端做状态提示。
    """
    if request.npc_id:
        # 走标准 talk action（已集成 AI）
        result = await game_manager.perform_action(
            character_id=request.character_id,
            action_type="talk",
            target=request.npc_id,
            parameters={"message": request.message},
            db=db,
        )
        return result
    else:
        # 叙述者模式：直接调用 ai_client
        from app.ai_client import chat as ai_chat

        character = await game_manager.get_character(request.character_id, db)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        scene_id = request.scene_id or character.get("scene_id", "village_001")
        scene = game_manager.world.get_scene(scene_id)
        scene_name = scene.name if scene else scene_id
        world_state = game_manager.world.get_world_state()
        world_time = world_state.get("time_of_day", "白天")

        ai_result = await ai_chat(
            message=request.message,
            character_id=request.character_id,
            scene_id=scene_id,
            scene_name=scene_name,
            world_time=world_time,
        )

        return {
            "success": True,
            "message": ai_result["response"],
            "effects": {
                "mode": "narrator",
                "scene_id": scene_id,
                "ai_used": ai_result.get("ai_used", False),
                "fallback": ai_result.get("fallback", False),
            },
            "state_changes": {},
        }


@router.post("/actions/talk-ai/stream")
async def talk_ai_stream(
    request: TalkAIRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI 驱动的 NPC 对话（流式 SSE 版）。
    每条 SSE 数据格式：data: {"delta": "...", "done": false}
    最终帧：data: {"delta": "", "done": true}
    """
    from app.ai_client import chat_stream as ai_stream

    character = await game_manager.get_character(request.character_id, db)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    scene_id = request.scene_id or character.get("scene_id", "village_001")
    scene = game_manager.world.get_scene(scene_id)
    scene_name = scene.name if scene else scene_id
    world_state = game_manager.world.get_world_state()
    world_time = world_state.get("time_of_day", "白天")

    npc_dict = None
    if request.npc_id:
        npc = game_manager.world.get_npc(request.npc_id)
        if npc:
            npc_dict = npc.to_dict()

    async def event_generator():
        async for chunk in ai_stream(
            message=request.message,
            character_id=request.character_id,
            scene_id=scene_id,
            npc=npc_dict,
            scene_name=scene_name,
            world_time=world_time,
        ):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")
