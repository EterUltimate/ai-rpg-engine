"""
游戏动作路由
"""
from fastapi import APIRouter, Depends, HTTPException
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
