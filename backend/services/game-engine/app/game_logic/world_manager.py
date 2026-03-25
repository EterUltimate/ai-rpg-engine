"""
游戏世界管理系统 - 管理场景、NPC、事件等
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import random


class WorldState:
    """世界状态"""
    
    def __init__(self):
        self.time_of_day: str = "morning"  # morning, afternoon, evening, night
        self.weather: str = "clear"         # clear, cloudy, rainy, stormy
        self.day_count: int = 1
        self.global_events: List[str] = []
        self.world_flags: Dict[str, bool] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_of_day": self.time_of_day,
            "weather": self.weather,
            "day_count": self.day_count,
            "global_events": self.global_events,
            "world_flags": self.world_flags
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.time_of_day = data.get("time_of_day", "morning")
        self.weather = data.get("weather", "clear")
        self.day_count = data.get("day_count", 1)
        self.global_events = data.get("global_events", [])
        self.world_flags = data.get("world_flags", {})


class NPC:
    """NPC数据结构"""
    
    def __init__(
        self,
        npc_id: str,
        name: str,
        npc_type: str,
        personality: str,
        dialogue_style: str,
        location: str,
        schedule: Optional[Dict[str, str]] = None
    ):
        self.npc_id = npc_id
        self.name = name
        self.npc_type = npc_type  # merchant, quest_giver, enemy, neutral
        self.personality = personality
        self.dialogue_style = dialogue_style
        self.location = location
        self.schedule = schedule or {}
        self.relationships: Dict[str, int] = {}  # character_id -> relationship_score
        self.flags: Dict[str, bool] = {}
        self.inventory: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "npc_type": self.npc_type,
            "personality": self.personality,
            "dialogue_style": self.dialogue_style,
            "location": self.location,
            "schedule": self.schedule,
            "relationships": self.relationships,
            "flags": self.flags,
            "inventory": self.inventory
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NPC":
        npc = cls(
            npc_id=data["npc_id"],
            name=data["name"],
            npc_type=data["npc_type"],
            personality=data["personality"],
            dialogue_style=data["dialogue_style"],
            location=data["location"],
            schedule=data.get("schedule")
        )
        npc.relationships = data.get("relationships", {})
        npc.flags = data.get("flags", {})
        npc.inventory = data.get("inventory", [])
        return npc


class Scene:
    """场景数据结构"""
    
    def __init__(
        self,
        scene_id: str,
        name: str,
        description: str,
        scene_type: str,
        connections: List[str],
        npcs: List[str],
        items: List[str],
        events: List[str]
    ):
        self.scene_id = scene_id
        self.name = name
        self.description = description
        self.scene_type = scene_type  # town, forest, dungeon, building
        self.connections = connections  # 连接的场景ID
        self.npcs = npcs
        self.items = items
        self.events = events
        self.flags: Dict[str, bool] = {}
        self.visited_by: List[str] = []  # 访问过的角色ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "description": self.description,
            "scene_type": self.scene_type,
            "connections": self.connections,
            "npcs": self.npcs,
            "items": self.items,
            "events": self.events,
            "flags": self.flags,
            "visited_by": self.visited_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        scene = cls(
            scene_id=data["scene_id"],
            name=data["name"],
            description=data["description"],
            scene_type=data["scene_type"],
            connections=data["connections"],
            npcs=data["npcs"],
            items=data["items"],
            events=data["events"]
        )
        scene.flags = data.get("flags", {})
        scene.visited_by = data.get("visited_by", [])
        return scene


class Quest:
    """任务数据结构"""
    
    def __init__(
        self,
        quest_id: str,
        title: str,
        description: str,
        quest_type: str,
        objectives: List[Dict[str, Any]],
        rewards: Dict[str, Any],
        prerequisites: Optional[List[str]] = None
    ):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.quest_type = quest_type  # main, side, random
        self.objectives = objectives
        self.rewards = rewards
        self.prerequisites = prerequisites or []
        self.status = "available"  # available, active, completed, failed
        self.assigned_to: Optional[str] = None
        self.progress: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "quest_type": self.quest_type,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        quest = cls(
            quest_id=data["quest_id"],
            title=data["title"],
            description=data["description"],
            quest_type=data["quest_type"],
            objectives=data["objectives"],
            rewards=data["rewards"],
            prerequisites=data.get("prerequisites")
        )
        quest.status = data.get("status", "available")
        quest.assigned_to = data.get("assigned_to")
        quest.progress = data.get("progress", {})
        return quest
    
    def check_completion(self) -> bool:
        """检查任务是否完成"""
        for objective in self.objectives:
            obj_id = objective["id"]
            required = objective.get("required", 1)
            current = self.progress.get(obj_id, 0)
            if current < required:
                return False
        return True


class WorldManager:
    """世界管理器"""
    
    def __init__(self):
        self.world_state = WorldState()
        self.scenes: Dict[str, Scene] = {}
        self.npcs: Dict[str, NPC] = {}
        self.quests: Dict[str, Quest] = {}
        self.active_events: List[Dict[str, Any]] = []
        
        # 初始化默认世界
        self._init_default_world()
    
    def _init_default_world(self):
        """初始化默认游戏世界"""
        # 创建起始村庄场景
        village = Scene(
            scene_id="village_001",
            name="起始村庄",
            description="一个宁静的小村庄,是冒险者的起点。村庄中央有一口古老的井,周围散布着几间房屋。",
            scene_type="town",
            connections=["forest_001", "shop_001"],
            npcs=["npc_elder", "npc_merchant"],
            items=[],
            events=["village_welcome"]
        )
        self.scenes[village.scene_id] = village
        
        # 创建森林场景
        forest = Scene(
            scene_id="forest_001",
            name="神秘森林",
            description="村庄北边的古老森林,树木高大茂密,光线昏暗。传说深处隐藏着宝藏。",
            scene_type="forest",
            connections=["village_001", "cave_001"],
            npcs=["npc_hunter"],
            items=["herb_001", "wood_001"],
            events=["forest_explore"]
        )
        self.scenes[forest.scene_id] = forest
        
        # 创建NPC
        elder = NPC(
            npc_id="npc_elder",
            name="村长",
            npc_type="quest_giver",
            personality="智慧、慈祥、富有经验的老者",
            dialogue_style="说话慢条斯理,喜欢用谚语,充满智慧",
            location="village_001"
        )
        self.npcs[elder.npc_id] = elder
        
        merchant = NPC(
            npc_id="npc_merchant",
            name="商人",
            npc_type="merchant",
            personality="精明、友好、热爱交易的商人",
            dialogue_style="热情洋溢,喜欢讨价还价,总是微笑",
            location="village_001"
        )
        self.npcs[merchant.npc_id] = merchant
        
        # 创建初始任务
        main_quest = Quest(
            quest_id="quest_001",
            title="村庄的困境",
            description="村长说村庄最近受到奇怪生物的骚扰,希望你能调查森林深处的洞穴。",
            quest_type="main",
            objectives=[
                {"id": "obj_1", "description": "与村长交谈", "type": "talk", "target": "npc_elder", "required": 1},
                {"id": "obj_2", "description": "前往神秘森林", "type": "visit", "target": "forest_001", "required": 1},
                {"id": "obj_3", "description": "调查洞穴", "type": "explore", "target": "cave_001", "required": 1}
            ],
            rewards={
                "gold": 100,
                "experience": 50,
                "items": ["sword_001"]
            }
        )
        self.quests[main_quest.quest_id] = main_quest
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取场景"""
        return self.scenes.get(scene_id)
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """获取NPC"""
        return self.npcs.get(npc_id)
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """获取任务"""
        return self.quests.get(quest_id)
    
    def get_available_quests(self, character_id: str) -> List[Quest]:
        """获取可用任务"""
        available = []
        for quest in self.quests.values():
            if quest.status == "available":
                # 检查前置任务
                if all(
                    (q := self.quests.get(pre_id)) is not None and q.status == "completed"
                    for pre_id in quest.prerequisites
                ):
                    available.append(quest)
        return available
    
    def accept_quest(self, quest_id: str, character_id: str) -> bool:
        """接受任务"""
        quest = self.quests.get(quest_id)
        if quest and quest.status == "available":
            quest.status = "active"
            quest.assigned_to = character_id
            quest.progress = {}
            return True
        return False
    
    def update_quest_progress(
        self,
        quest_id: str,
        objective_id: str,
        amount: int = 1
    ) -> Dict[str, Any]:
        """更新任务进度"""
        quest = self.quests.get(quest_id)
        if not quest or quest.status != "active":
            return {"success": False, "message": "任务不存在或未激活"}
        
        # 更新进度
        current = quest.progress.get(objective_id, 0)
        quest.progress[objective_id] = current + amount
        
        # 检查是否完成
        if quest.check_completion():
            quest.status = "completed"
            return {
                "success": True,
                "message": "任务完成!",
                "rewards": quest.rewards
            }
        
        return {
            "success": True,
            "message": f"任务进度更新: {quest.progress[objective_id]}"
        }
    
    def get_npcs_in_scene(self, scene_id: str) -> List[NPC]:
        """获取场景中的NPC"""
        scene = self.scenes.get(scene_id)
        if not scene:
            return []
        
        return [
            self.npcs[npc_id]
            for npc_id in scene.npcs
            if npc_id in self.npcs
        ]
    
    def get_connected_scenes(self, scene_id: str) -> List[str]:
        """获取连接的场景"""
        scene = self.scenes.get(scene_id)
        return scene.connections if scene else []
    
    def update_npc_relationship(
        self,
        npc_id: str,
        character_id: str,
        delta: int
    ):
        """更新NPC关系值"""
        npc = self.npcs.get(npc_id)
        if npc:
            current = npc.relationships.get(character_id, 0)
            npc.relationships[character_id] = current + delta
    
    def advance_time(self):
        """推进时间"""
        time_order = ["morning", "afternoon", "evening", "night"]
        current_idx = time_order.index(self.world_state.time_of_day)
        
        if current_idx == len(time_order) - 1:
            self.world_state.time_of_day = time_order[0]
            self.world_state.day_count += 1
        else:
            self.world_state.time_of_day = time_order[current_idx + 1]
    
    def add_global_event(self, event: str):
        """添加全局事件"""
        self.world_state.global_events.append(event)
    
    def set_world_flag(self, flag_name: str, value: bool):
        """设置世界标志"""
        self.world_state.world_flags[flag_name] = value
    
    def get_world_state(self) -> Dict[str, Any]:
        """获取世界状态"""
        return self.world_state.to_dict()
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "world_state": self.world_state.to_dict(),
            "scenes": {sid: scene.to_dict() for sid, scene in self.scenes.items()},
            "npcs": {nid: npc.to_dict() for nid, npc in self.npcs.items()},
            "quests": {qid: quest.to_dict() for qid, quest in self.quests.items()},
            "active_events": self.active_events
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldManager":
        """从字典反序列化"""
        manager = cls()
        manager.world_state.from_dict(data["world_state"])
        
        manager.scenes = {
            sid: Scene.from_dict(sdata)
            for sid, sdata in data.get("scenes", {}).items()
        }
        
        manager.npcs = {
            nid: NPC.from_dict(ndata)
            for nid, ndata in data.get("npcs", {}).items()
        }
        
        manager.quests = {
            qid: Quest.from_dict(qdata)
            for qid, qdata in data.get("quests", {}).items()
        }
        
        manager.active_events = data.get("active_events", [])
        
        return manager
