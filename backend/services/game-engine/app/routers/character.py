from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import Character
from pydantic import BaseModel
from typing import Dict, Optional

router = APIRouter()


class CreateCharacterRequest(BaseModel):
    name: str
    attributes: Optional[Dict[str, int]] = None


class UpdateCharacterRequest(BaseModel):
    name: Optional[str] = None
    attributes: Optional[Dict[str, int]] = None
    status: Optional[Dict[str, int]] = None


@router.get("/character/{character_id}")
async def get_character(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取角色信息"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "attributes": character.attributes,
        "status": character.status,
        "inventory": character.inventory,
        "skills": character.skills,
        "equipment": character.equipment,
        "created_at": character.created_at.isoformat()
    }


@router.post("/character/create")
async def create_character(
    request: CreateCharacterRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建新角色"""
    # 默认属性
    default_attributes = {
        "strength": 10,
        "agility": 10,
        "intelligence": 10,
        "charisma": 10
    }
    
    if request.attributes:
        default_attributes.update(request.attributes)
    
    character = Character(
        name=request.name,
        attributes=default_attributes
    )
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "attributes": character.attributes,
        "message": "Character created successfully"
    }


@router.put("/character/{character_id}")
async def update_character(
    character_id: str,
    request: UpdateCharacterRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新角色信息"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # 更新字段
    if request.name:
        character.name = request.name
    if request.attributes:
        character.attributes.update(request.attributes)
    if request.status:
        character.status.update(request.status)
    
    await db.commit()
    await db.refresh(character)
    
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "attributes": character.attributes,
        "status": character.status,
        "message": "Character updated successfully"
    }


@router.get("/character/{character_id}/inventory")
async def get_inventory(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取角色背包"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "character_id": character_id,
        "inventory": character.inventory,
        "equipment": character.equipment
    }
