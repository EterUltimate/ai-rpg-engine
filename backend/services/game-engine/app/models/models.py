from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Character(Base):
    """角色模型"""
    __tablename__ = "characters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    
    # 属性 (JSON格式存储)
    attributes = Column(JSON, default={
        "strength": 10,
        "agility": 10,
        "intelligence": 10,
        "charisma": 10
    })
    
    # 状态
    status = Column(JSON, default={
        "hp": 100,
        "max_hp": 100,
        "mp": 50,
        "max_mp": 50,
        "stamina": 100,
        "max_stamina": 100
    })
    
    # 背包
    inventory = Column(JSON, default=[])
    
    # 技能
    skills = Column(JSON, default=[])
    
    # 装备
    equipment = Column(JSON, default={})
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SaveSlot(Base):
    """存档模型"""
    __tablename__ = "save_slots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, nullable=False)
    scene_id = Column(String, default="main")
    
    # 任务进度
    quest_progress = Column(JSON, default={})
    
    # 世界状态
    world_state = Column(JSON, default={})
    
    # 角色状态快照
    character_snapshot = Column(JSON, default={})
    
    saved_at = Column(DateTime, server_default=func.now())


class Quest(Base):
    """任务模型"""
    __tablename__ = "quests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    
    # 任务目标
    objectives = Column(JSON, default=[])
    
    # 奖励
    rewards = Column(JSON, default={})
    
    # 状态: active, completed, failed
    status = Column(String, default="active")
    
    # 任务类型: main, side, random
    quest_type = Column(String, default="side")
    
    created_at = Column(DateTime, server_default=func.now())
