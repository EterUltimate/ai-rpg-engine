from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import SaveSlot, Character
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()


class SaveGameRequest(BaseModel):
    character_id: str
    state: Dict[str, Any]


class ActionRequest(BaseModel):
    action: str
    target: Optional[str] = None


@router.get("/game/state/{character_id}")
async def get_game_state(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取游戏状态"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "character_id": character_id,
        "name": character.name,
        "level": character.level,
        "attributes": character.attributes,
        "status": character.status,
        "scene": "main"
    }


@router.post("/game/save")
async def save_game(
    request: SaveGameRequest,
    db: AsyncSession = Depends(get_db)
):
    """保存游戏"""
    # 创建新存档
    save = SaveSlot(
        character_id=request.character_id,
        world_state=request.state.get("world_state", {}),
        quest_progress=request.state.get("quest_progress", {}),
        character_snapshot=request.state.get("character_snapshot", {})
    )
    
    db.add(save)
    await db.commit()
    await db.refresh(save)
    
    return {
        "success": True,
        "save_id": save.id,
        "message": "Game saved successfully"
    }


@router.get("/game/load/{save_id}")
async def load_game(
    save_id: str,
    db: AsyncSession = Depends(get_db)
):
    """加载游戏"""
    result = await db.execute(
        select(SaveSlot).where(SaveSlot.id == save_id)
    )
    save = result.scalar_one_or_none()
    
    if not save:
        raise HTTPException(status_code=404, detail="Save not found")
    
    return {
        "save_id": save.id,
        "character_id": save.character_id,
        "scene_id": save.scene_id,
        "quest_progress": save.quest_progress,
        "world_state": save.world_state,
        "character_snapshot": save.character_snapshot,
        "saved_at": save.saved_at.isoformat()
    }


@router.post("/game/action")
async def perform_action(request: ActionRequest):
    """执行游戏动作"""
    # TODO: 实现动作处理逻辑
    # 这里应该与AI引擎交互,处理动作结果
    
    return {
        "success": True,
        "action": request.action,
        "target": request.target,
        "result": f"Action '{request.action}' executed successfully"
    }
