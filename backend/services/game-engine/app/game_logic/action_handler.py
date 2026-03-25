"""
游戏动作处理器 - 处理玩家各种行动
"""
from typing import Dict, Any, Optional
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """动作类型枚举"""
    MOVE = "move"
    TALK = "talk"
    ATTACK = "attack"
    USE_ITEM = "use_item"
    PICK_UP = "pick_up"
    DROP = "drop"
    INVESTIGATE = "investigate"
    REST = "rest"
    TRADE = "trade"
    ACCEPT_QUEST = "accept_quest"
    COMPLETE_QUEST = "complete_quest"


class ActionResult:
    """动作结果"""
    
    def __init__(
        self,
        success: bool,
        message: str,
        effects: Optional[Dict[str, Any]] = None,
        state_changes: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.message = message
        self.effects = effects or {}
        self.state_changes = state_changes or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "effects": self.effects,
            "state_changes": self.state_changes
        }


class ActionHandler:
    """动作处理器"""
    
    def __init__(self, world_manager, character_manager):
        self.world = world_manager
        self.characters = character_manager
    
    async def handle_action(
        self,
        action_type: str,
        character_id: str,
        target: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """处理游戏动作"""
        
        action_map = {
            ActionType.MOVE.value: self._handle_move,
            ActionType.TALK.value: self._handle_talk,
            ActionType.ATTACK.value: self._handle_attack,
            ActionType.USE_ITEM.value: self._handle_use_item,
            ActionType.PICK_UP.value: self._handle_pick_up,
            ActionType.DROP.value: self._handle_drop,
            ActionType.INVESTIGATE.value: self._handle_investigate,
            ActionType.REST.value: self._handle_rest,
            ActionType.TRADE.value: self._handle_trade,
            ActionType.ACCEPT_QUEST.value: self._handle_accept_quest,
            ActionType.COMPLETE_QUEST.value: self._handle_complete_quest,
        }
        
        handler = action_map.get(action_type)
        if not handler:
            return ActionResult(
                success=False,
                message=f"未知动作类型: {action_type}"
            )
        
        return await handler(character_id, target, parameters or {})
    
    async def _handle_move(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理移动动作"""
        # 获取角色当前场景
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        current_scene_id = character.get("scene_id", "village_001")
        current_scene = self.world.get_scene(current_scene_id)
        
        if not current_scene:
            return ActionResult(False, "当前场景不存在")
        
        # 检查目标场景是否可达
        if target not in current_scene.connections:
            return ActionResult(
                False,
                f"无法从{current_scene.name}到达目标地点"
            )
        
        # 获取目标场景
        target_scene = self.world.get_scene(target)
        if not target_scene:
            return ActionResult(False, "目标场景不存在")
        
        # 记录访问
        if character_id not in target_scene.visited_by:
            target_scene.visited_by.append(character_id)
            is_first_visit = True
        else:
            is_first_visit = False
        
        # 更新角色位置
        await self.characters.update_character(character_id, {
            "scene_id": target
        })
        
        # 生成场景描述
        description = f"你来到了{target_scene.name}。\n{target_scene.description}"
        
        # 获取场景中的NPC
        npcs = self.world.get_npcs_in_scene(target)
        if npcs:
            npc_names = [npc.name for npc in npcs]
            description += f"\n你看到: {', '.join(npc_names)}"
        
        return ActionResult(
            success=True,
            message=description,
            effects={
                "scene_change": target,
                "is_first_visit": is_first_visit,
                "npcs_present": [npc.npc_id for npc in npcs]
            },
            state_changes={
                "character_location": target
            }
        )
    
    async def _handle_talk(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """
        处理对话动作。
        流程：
          1. 基础校验（NPC 存在、在当前场景）
          2. 组装游戏上下文（关系值、可用任务）
          3. 调用 ai-engine 生成 NPC 对话
          4. 返回结果；ai-engine 不可用时自动降级到本地文本
        """
        # ── 1. 基础校验 ──────────────────────────────────────────
        npc = self.world.get_npc(target)
        if not npc:
            return ActionResult(False, "目标NPC不存在")

        # 从 parameters 取出 db session（由 GameManager.perform_action 注入）
        db = parameters.get("_db")

        character = await self.characters.get_character(character_id, db)
        if not character:
            return ActionResult(False, "角色不存在")

        current_scene_id = character.get("scene_id", "village_001")
        if npc.location != current_scene_id:
            return ActionResult(False, f"{npc.name}不在这里")

        # ── 2. 组装上下文 ─────────────────────────────────────────
        relationship = npc.relationships.get(character_id, 0)
        world_state = self.world.get_world_state()
        scene = self.world.get_scene(current_scene_id)
        scene_name = scene.name if scene else current_scene_id
        world_time = world_state.get("time_of_day", "白天")

        # 玩家本次说的话（可选，由前端通过 parameters["message"] 传入）
        player_message: str = parameters.get(
            "message",
            f"你好，{npc.name}。"
        )

        # 构造背景补充给 AI（附加到 player_message 末尾作为 context hint）
        context_hints: list[str] = []
        if relationship > 30:
            context_hints.append(f"（{npc.name}与玩家是老朋友，关系亲密）")
        elif relationship < -30:
            context_hints.append(f"（{npc.name}对玩家心存警惕）")

        # 检查可分配任务
        available_quests = [
            q for q in self.world.quests.values()
            if q.status == "available" and q.assigned_to != character_id
        ]
        if npc.npc_type == "quest_giver" and available_quests:
            quest_titles = "、".join(q.title for q in available_quests[:2])
            context_hints.append(f"（{npc.name}有任务想委托给玩家：{quest_titles}）")

        full_message = player_message
        if context_hints:
            full_message += " " + " ".join(context_hints)

        # ── 3. 调用 AI ────────────────────────────────────────────
        try:
            from app.ai_client import chat as ai_chat   # 延迟导入避免循环
            ai_result = await ai_chat(
                message=full_message,
                character_id=character_id,
                scene_id=current_scene_id,
                npc=npc.to_dict(),
                scene_name=scene_name,
                world_time=world_time,
            )
            npc_reply = ai_result["response"]
            ai_used = ai_result.get("ai_used", False)
            fallback = ai_result.get("fallback", False)
        except Exception as exc:   # noqa: BLE001
            logger.warning("AI chat call failed unexpectedly: %s", exc)
            npc_reply = f"{npc.name}沉默片刻，没有说话。"
            ai_used = False
            fallback = True

        # ── 4. 组装返回消息 ───────────────────────────────────────
        # 前缀行保留，供前端渲染角色名气泡
        display_message = f"**{npc.name}**：{npc_reply}"

        # 补充任务提示（仅在降级模式下才加，AI 模式让 LLM 自己提）
        if fallback and npc.npc_type == "quest_giver" and available_quests:
            display_message += f"\n\n{npc.name}似乎有任务要交给你。"

        return ActionResult(
            success=True,
            message=display_message,
            effects={
                "npc_id": target,
                "npc_name": npc.name,
                "relationship": relationship,
                "npc_type": npc.npc_type,
                "ai_used": ai_used,
                "fallback": fallback,
            }
        )
    
    async def _handle_attack(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理攻击动作"""
        # 简化的战斗系统
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        # 计算伤害
        strength = character.get("attributes", {}).get("strength", 10)
        base_damage = strength // 2 + random.randint(1, 6)
        
        message = f"你发起了攻击!造成{base_damage}点伤害。"
        
        return ActionResult(
            success=True,
            message=message,
            effects={
                "damage": base_damage,
                "target": target
            }
        )
    
    async def _handle_use_item(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理使用物品"""
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        inventory = character.get("inventory", [])
        if target not in inventory:
            return ActionResult(False, "你没有这个物品")
        
        # 简单的物品效果
        item_effects = {
            "health_potion": {"hp": 50, "message": "恢复了50点生命值"},
            "mana_potion": {"mp": 30, "message": "恢复了30点魔法值"},
        }
        
        effect = item_effects.get(target, {"message": f"使用了{target}"})
        
        # 从背包移除物品
        inventory.remove(target)
        await self.characters.update_character(character_id, {
            "inventory": inventory
        })
        
        return ActionResult(
            success=True,
            message=effect.get("message", "物品已使用"),
            effects=effect,
            state_changes={
                "inventory_change": -1,
                "item_used": target
            }
        )
    
    async def _handle_pick_up(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理拾取物品"""
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        current_scene_id = character.get("scene_id", "village_001")
        scene = self.world.get_scene(current_scene_id)
        
        if not scene or target not in scene.items:
            return ActionResult(False, "这里没有这个物品")
        
        # 添加到背包
        inventory = character.get("inventory", [])
        inventory.append(target)
        
        await self.characters.update_character(character_id, {
            "inventory": inventory
        })
        
        # 从场景移除
        scene.items.remove(target)
        
        return ActionResult(
            success=True,
            message=f"你拾取了{target}",
            effects={"item_added": target},
            state_changes={
                "inventory_change": 1
            }
        )
    
    async def _handle_drop(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理丢弃物品"""
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        inventory = character.get("inventory", [])
        if target not in inventory:
            return ActionResult(False, "你没有这个物品")
        
        # 从背包移除
        inventory.remove(target)
        await self.characters.update_character(character_id, {
            "inventory": inventory
        })
        
        # 添加到当前场景
        current_scene_id = character.get("scene_id", "village_001")
        scene = self.world.get_scene(current_scene_id)
        if scene:
            scene.items.append(target)
        
        return ActionResult(
            success=True,
            message=f"你丢弃了{target}",
            effects={"item_removed": target},
            state_changes={
                "inventory_change": -1
            }
        )
    
    async def _handle_investigate(
        self,
        character_id: str,
        target: Optional[str],
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理调查动作"""
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        current_scene_id = character.get("scene_id", "village_001")
        scene = self.world.get_scene(current_scene_id)
        
        if not scene:
            return ActionResult(False, "当前场景不存在")
        
        # 生成调查结果
        descriptions = [
            f"你仔细观察了周围环境。",
            scene.description,
            f"这里连接着: {', '.join(scene.connections)}"
        ]
        
        if scene.npcs:
            descriptions.append(f"你注意到: {', '.join(scene.npcs)}")
        
        if scene.items:
            descriptions.append(f"地上有: {', '.join(scene.items)}")
        
        # 随机发现隐藏物品或线索
        if random.random() < 0.3:
            descriptions.append("你发现了一些有趣的痕迹...")
        
        return ActionResult(
            success=True,
            message="\n".join(descriptions),
            effects={
                "investigated_scene": current_scene_id
            }
        )
    
    async def _handle_rest(
        self,
        character_id: str,
        target: Optional[str],
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理休息动作"""
        character = await self.characters.get_character(character_id)
        if not character:
            return ActionResult(False, "角色不存在")
        
        # 恢复生命和魔法
        status = character.get("status", {})
        max_hp = status.get("max_hp", 100)
        max_mp = status.get("max_mp", 50)
        
        status["hp"] = max_hp
        status["mp"] = max_mp
        
        await self.characters.update_character(character_id, {
            "status": status
        })
        
        # 推进时间
        self.world.advance_time()
        
        return ActionResult(
            success=True,
            message="你休息了一会,生命和魔法已完全恢复。",
            effects={
                "hp_restored": max_hp,
                "mp_restored": max_mp
            },
            state_changes={
                "time_advanced": True
            }
        )
    
    async def _handle_trade(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理交易动作"""
        npc = self.world.get_npc(target)
        if not npc or npc.npc_type != "merchant":
            return ActionResult(False, "这个NPC不进行交易")
        
        character = await self.characters.get_character(character_id)
        current_scene_id = character.get("scene_id", "village_001")
        
        if npc.location != current_scene_id:
            return ActionResult(False, f"{npc.name}不在这里")
        
        # 简单的交易系统
        message = f"{npc.name}打开了商店界面。\n"
        message += "可购买物品: 健康药水、魔法药水、武器、防具\n"
        message += "可出售物品: 你背包中的物品"
        
        return ActionResult(
            success=True,
            message=message,
            effects={
                "merchant_id": target,
                "merchant_name": npc.name
            }
        )
    
    async def _handle_accept_quest(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理接受任务"""
        success = self.world.accept_quest(target, character_id)
        
        if success:
            quest = self.world.get_quest(target)
            return ActionResult(
                success=True,
                message=f"你接受了任务: {quest.title}\n{quest.description}",
                effects={
                    "quest_accepted": target,
                    "quest_title": quest.title
                },
                state_changes={
                    "quest_status": "active"
                }
            )
        else:
            return ActionResult(
                success=False,
                message="无法接受这个任务"
            )
    
    async def _handle_complete_quest(
        self,
        character_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> ActionResult:
        """处理完成任务"""
        quest = self.world.get_quest(target)
        if not quest or quest.assigned_to != character_id:
            return ActionResult(False, "任务不存在或未分配给你")
        
        if not quest.check_completion():
            return ActionResult(False, "任务尚未完成")
        
        quest.status = "completed"
        
        # 发放奖励
        rewards = quest.rewards
        message = f"任务完成! {quest.title}\n获得奖励:\n"
        
        for key, value in rewards.items():
            message += f"- {key}: {value}\n"
        
        return ActionResult(
            success=True,
            message=message,
            effects={
                "quest_completed": target,
                "rewards": rewards
            },
            state_changes={
                "quest_status": "completed"
            }
        )
