"""
游戏管理器 - 整合所有游戏系统
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.game_logic.world_manager import WorldManager
from app.game_logic.action_handler import ActionHandler, ActionType
from app.database import AsyncSessionLocal
from app.models.models import Character, SaveSlot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json


class GameManager:
    """游戏管理器 - 统一管理所有游戏系统"""
    
    def __init__(self):
        self.world = WorldManager()
        self.action_handler = None
        self.active_games: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self, db: AsyncSession):
        """初始化游戏管理器"""
        self.action_handler = ActionHandler(self.world, self)
    
    async def create_character(
        self,
        name: str,
        attributes: Optional[Dict[str, int]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """创建新角色"""
        # 默认属性
        default_attributes = {
            "strength": 10,
            "agility": 10,
            "intelligence": 10,
            "charisma": 10
        }
        
        if attributes:
            default_attributes.update(attributes)
        
        # 创建角色数据
        character_data = {
            "name": name,
            "level": 1,
            "attributes": default_attributes,
            "status": {
                "hp": 100,
                "max_hp": 100,
                "mp": 50,
                "max_mp": 50,
                "stamina": 100,
                "max_stamina": 100
            },
            "inventory": ["health_potion"],
            "skills": [],
            "equipment": {},
            "scene_id": "village_001"  # 起始位置
        }
        
        if db:
            # 保存到数据库
            character = Character(**character_data)
            db.add(character)
            await db.commit()
            await db.refresh(character)
            character_data["id"] = character.id
        
        return character_data
    
    async def get_character(
        self,
        character_id: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[Dict[str, Any]]:
        """获取角色信息"""
        if db:
            result = await db.execute(
                select(Character).where(Character.id == character_id)
            )
            character = result.scalar_one_or_none()
            
            if character:
                return {
                    "id": character.id,
                    "name": character.name,
                    "level": character.level,
                    "attributes": character.attributes,
                    "status": character.status,
                    "inventory": character.inventory,
                    "skills": character.skills,
                    "equipment": character.equipment,
                    "scene_id": getattr(character, "scene_id", "village_001"),
                    "created_at": character.created_at.isoformat()
                }
        
        return None
    
    async def update_character(
        self,
        character_id: str,
        updates: Dict[str, Any],
        db: Optional[AsyncSession] = None
    ) -> bool:
        """更新角色信息"""
        if db:
            result = await db.execute(
                select(Character).where(Character.id == character_id)
            )
            character = result.scalar_one_or_none()
            
            if character:
                for key, value in updates.items():
                    if hasattr(character, key):
                        setattr(character, key, value)
                
                await db.commit()
                return True
        
        return False
    
    async def perform_action(
        self,
        character_id: str,
        action_type: str,
        target: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """执行游戏动作"""
        if not self.action_handler:
            return {
                "success": False,
                "message": "游戏系统未初始化"
            }
        
        # 获取角色信息
        character = await self.get_character(character_id, db)
        if not character:
            return {
                "success": False,
                "message": "角色不存在"
            }
        
        # 执行动作（把 db 注入 parameters，供 action_handler 内部使用）
        params = dict(parameters or {})
        params["_db"] = db
        result = await self.action_handler.handle_action(
            action_type=action_type,
            character_id=character_id,
            target=target,
            parameters=params
        )
        
        # 应用状态变化
        if result.success and result.state_changes:
            await self._apply_state_changes(character_id, result.state_changes, db)
        
        return result.to_dict()
    
    async def _apply_state_changes(
        self,
        character_id: str,
        changes: Dict[str, Any],
        db: Optional[AsyncSession]
    ):
        """应用状态变化"""
        character = await self.get_character(character_id, db)
        if not character:
            return
        
        updates = {}
        
        if "character_location" in changes:
            updates["scene_id"] = changes["character_location"]
        
        if updates:
            await self.update_character(character_id, updates, db)
    
    async def get_game_state(
        self,
        character_id: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """获取完整游戏状态"""
        character = await self.get_character(character_id, db)
        if not character:
            return {"error": "角色不存在"}
        
        scene_id = character.get("scene_id", "village_001")
        scene = self.world.get_scene(scene_id)
        
        return {
            "character": character,
            "scene": scene.to_dict() if scene else None,
            "world_state": self.world.get_world_state(),
            "available_quests": [
                q.to_dict() for q in self.world.get_available_quests(character_id)
            ]
        }
    
    async def save_game(
        self,
        character_id: str,
        save_name: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """保存游戏"""
        if not db:
            return {"error": "数据库未连接"}
        
        # 获取当前状态
        game_state = await self.get_game_state(character_id, db)
        
        # 创建存档
        save = SaveSlot(
            character_id=character_id,
            scene_id=game_state["character"]["scene_id"],
            quest_progress={},  # TODO: 实现任务进度
            world_state=game_state["world_state"],
            character_snapshot=game_state["character"]
        )
        
        db.add(save)
        await db.commit()
        await db.refresh(save)
        
        return {
            "success": True,
            "save_id": save.id,
            "saved_at": save.saved_at.isoformat(),
            "scene": save.scene_id
        }
    
    async def load_game(
        self,
        save_id: str,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """加载游戏"""
        if not db:
            return {"error": "数据库未连接"}
        
        result = await db.execute(
            select(SaveSlot).where(SaveSlot.id == save_id)
        )
        save = result.scalar_one_or_none()
        
        if not save:
            return {"error": "存档不存在"}
        
        # 恢复世界状态
        if save.world_state:
            # TODO: 实现世界状态恢复
            pass
        
        # 恢复角色状态
        if save.character_snapshot:
            await self.update_character(
                save.character_id,
                save.character_snapshot,
                db
            )
        
        return {
            "success": True,
            "character_id": save.character_id,
            "scene_id": save.scene_id,
            "quest_progress": save.quest_progress,
            "world_state": save.world_state
        }
    
    def get_scene_description(
        self,
        scene_id: str,
        character_id: str
    ) -> Dict[str, Any]:
        """获取场景描述"""
        scene = self.world.get_scene(scene_id)
        if not scene:
            return {"error": "场景不存在"}
        
        npcs = self.world.get_npcs_in_scene(scene_id)
        connections = self.world.get_connected_scenes(scene_id)
        
        is_first_visit = character_id not in scene.visited_by
        
        return {
            "scene": scene.to_dict(),
            "npcs": [npc.to_dict() for npc in npcs],
            "connections": connections,
            "is_first_visit": is_first_visit
        }
    
    def get_available_actions(
        self,
        scene_id: str,
        character_id: str
    ) -> list:
        """获取可用动作列表"""
        actions = []
        scene = self.world.get_scene(scene_id)
        
        if not scene:
            return actions
        
        # 移动选项
        for conn_id in scene.connections:
            conn_scene = self.world.get_scene(conn_id)
            if conn_scene:
                actions.append({
                    "type": ActionType.MOVE.value,
                    "target": conn_id,
                    "label": f"前往{conn_scene.name}"
                })
        
        # NPC交互
        for npc_id in scene.npcs:
            npc = self.world.get_npc(npc_id)
            if npc:
                actions.append({
                    "type": ActionType.TALK.value,
                    "target": npc_id,
                    "label": f"与{npc.name}交谈"
                })
        
        # 物品拾取
        for item_id in scene.items:
            actions.append({
                "type": ActionType.PICK_UP.value,
                "target": item_id,
                "label": f"拾取{item_id}"
            })
        
        # 通用动作
        actions.extend([
            {"type": ActionType.INVESTIGATE.value, "label": "调查周围"},
            {"type": ActionType.REST.value, "label": "休息"}
        ])
        
        return actions
    
    async def initialize_world_data(self):
        """初始化世界数据到RAG系统"""
        # 添加世界知识
        world_lore = [
            "这个世界被称为艾尔德兰大陆,是一个充满魔法和奇迹的地方。",
            "大陆上分布着多个王国和城邦,居民包括人类、精灵、矮人等多个种族。",
            "神秘的古老遗迹散落在大陆各处,传说中隐藏着强大的宝藏和魔法。",
            "近年来,黑暗势力开始复苏,各地出现奇怪的生物袭击事件。"
        ]
        
        for lore in world_lore:
            await self.world.add_world_knowledge(lore, "history")
        
        # 添加场景信息
        scenes_info = {
            "village_001": "起始村庄是一个宁静的小村庄,是许多冒险者的起点。村中央有一口古井,据说有神秘的力量。",
            "forest_001": "神秘森林位于村庄北边,树木高大茂密,光线昏暗。传说深处有一个古老的洞穴。",
        }
        
        for scene_id, description in scenes_info.items():
            await self.world.add_scene_context(scene_id, description, "location")


# 全局游戏管理器实例
game_manager = GameManager()
