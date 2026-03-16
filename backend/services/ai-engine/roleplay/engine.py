"""
AI角色扮演引擎 - 整合LLM和RAG系统
"""
from typing import Dict, Any, Optional, AsyncGenerator
from llm.llama_engine import LlamaEngine
from rag.enhanced_rag import EnhancedRAGSystem, MemoryType
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CharacterPersona:
    """角色人设"""
    
    def __init__(
        self,
        name: str,
        role: str,
        personality: str,
        background: str,
        speech_style: str,
        knowledge_domains: Optional[list] = None
    ):
        self.name = name
        self.role = role
        self.personality = personality
        self.background = background
        self.speech_style = speech_style
        self.knowledge_domains = knowledge_domains or []


class AIStoryteller:
    """AI叙事引擎"""
    
    # 游戏主持AI人设
    GAME_MASTER_PERSONA = CharacterPersona(
        name="游戏主持",
        role="RPG游戏主持人",
        personality="富有创造力、善于引导、公平公正、注重玩家体验",
        background="你是一个经验丰富的RPG游戏主持人,擅长创造引人入胜的故事、管理游戏世界、处理玩家行动。你的职责是让游戏既有趣又公平。",
        speech_style="描述生动、节奏把控得当、善于营造氛围、适时给出选择",
        knowledge_domains=[
            "RPG游戏规则",
            "叙事技巧",
            "角色扮演",
            "世界观构建",
            "战斗系统",
            "任务设计"
        ]
    )
    
    def __init__(
        self,
        llm_engine: LlamaEngine,
        rag_system: EnhancedRAGSystem
    ):
        self.llm = llm_engine
        self.rag = rag_system
    
    def build_system_prompt(
        self,
        persona: CharacterPersona,
        game_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建系统提示词"""
        prompt = f"""你现在是{persona.name}。

角色: {persona.role}
性格: {persona.personality}
背景: {persona.background}
说话风格: {persona.speech_style}

"""
        
        if game_context:
            # 添加游戏状态信息
            if "world_state" in game_context:
                world = game_context["world_state"]
                prompt += f"\n当前时间: {world.get('time_of_day', 'unknown')}\n"
                prompt += f"天气: {world.get('weather', 'unknown')}\n"
                prompt += f"天数: {world.get('day_count', 1)}\n"
            
            # 添加场景信息
            if "current_scene" in game_context:
                scene = game_context["current_scene"]
                prompt += f"\n当前场景: {scene.get('name', 'unknown')}\n"
                prompt += f"场景描述: {scene.get('description', '')}\n"
            
            # 添加角色信息
            if "character" in game_context:
                char = game_context["character"]
                prompt += f"\n玩家角色: {char.get('name', '冒险者')}\n"
                prompt += f"等级: {char.get('level', 1)}\n"
            
            # 添加NPC信息
            if "npc" in game_context:
                npc = game_context["npc"]
                prompt += f"\nNPC: {npc.get('name', 'unknown')}\n"
                prompt += f"性格: {npc.get('personality', '')}\n"
        
        prompt += "\n请记住:\n"
        prompt += "1. 保持角色一致性,符合设定的人设\n"
        prompt += "2. 推动故事发展,给玩家有趣的选择\n"
        prompt += "3. 公平处理玩家行动,给出合理的反馈\n"
        prompt += "4. 创造沉浸式的游戏体验\n"
        prompt += "5. 适时引入剧情转折和挑战\n"
        
        return prompt
    
    async def generate_response(
        self,
        user_input: str,
        character_id: str,
        scene_id: str,
        game_context: Optional[Dict[str, Any]] = None,
        npc_persona: Optional[CharacterPersona] = None
    ) -> str:
        """生成AI响应"""
        
        # 选择人设
        persona = npc_persona or self.GAME_MASTER_PERSONA
        
        # 构建系统提示词
        system_prompt = self.build_system_prompt(persona, game_context)
        
        # 获取RAG上下文
        rag_context = await self.rag.build_game_context(
            query=user_input,
            character_id=character_id,
            scene_id=scene_id,
            include_world_knowledge=True
        )
        
        # 格式化上下文
        context_text = self.rag.format_context_for_llm(rag_context, format_style="narrative")
        
        # 构建完整提示词
        full_prompt = self.llm.build_prompt(
            system_prompt=system_prompt,
            context=context_text,
            user_input=user_input
        )
        
        # 生成响应
        response = self.llm.generate(
            full_prompt,
            max_tokens=512,
            temperature=0.8,
            top_p=0.9
        )
        
        # 保存对话到记忆
        interaction = f"玩家: {user_input}\n{persona.name}: {response}"
        await self.rag.update_character_memory(
            character_id=character_id,
            interaction=interaction,
            importance=self._calculate_importance(user_input, response),
            memory_type=MemoryType.DIALOGUE
        )
        
        return response
    
    async def stream_response(
        self,
        user_input: str,
        character_id: str,
        scene_id: str,
        game_context: Optional[Dict[str, Any]] = None,
        npc_persona: Optional[CharacterPersona] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        
        # 选择人设
        persona = npc_persona or self.GAME_MASTER_PERSONA
        
        # 构建系统提示词
        system_prompt = self.build_system_prompt(persona, game_context)
        
        # 获取RAG上下文
        rag_context = await self.rag.build_game_context(
            query=user_input,
            character_id=character_id,
            scene_id=scene_id
        )
        
        # 格式化上下文
        context_text = self.rag.format_context_for_llm(rag_context)
        
        # 构建完整提示词
        full_prompt = self.llm.build_prompt(
            system_prompt=system_prompt,
            context=context_text,
            user_input=user_input
        )
        
        # 流式生成
        full_response = ""
        for chunk in self.llm.stream_generate(full_prompt, max_tokens=512):
            full_response += chunk
            yield chunk
        
        # 保存完整对话到记忆
        interaction = f"玩家: {user_input}\n{persona.name}: {full_response}"
        await self.rag.update_character_memory(
            character_id=character_id,
            interaction=interaction,
            importance=self._calculate_importance(user_input, full_response),
            memory_type=MemoryType.DIALOGUE
        )
    
    def _calculate_importance(self, user_input: str, response: str) -> int:
        """计算记忆重要性"""
        # 简单的重要性计算逻辑
        importance = 5  # 基础重要性
        
        # 关键词检测
        important_keywords = [
            "任务", "战斗", "发现", "宝箱", "Boss",
            "重要", "关键", "秘密", "死亡", "升级"
        ]
        
        combined_text = user_input + response
        for keyword in important_keywords:
            if keyword in combined_text:
                importance += 1
        
        # 长度因素
        if len(response) > 500:
            importance += 1
        
        return min(importance, 10)  # 最大重要性为10
    
    async def generate_scene_description(
        self,
        scene_name: str,
        scene_type: str
    ) -> str:
        """生成场景描述"""
        prompt = f"请为一个{scene_type}类型的场景'{scene_name}'生成详细描述:"
        
        response = self.llm.generate(
            prompt,
            max_tokens=256,
            temperature=0.7
        )
        
        return response
    
    async def generate_npc_dialogue(
        self,
        npc: CharacterPersona,
        player_input: str,
        context: Dict[str, Any]
    ) -> str:
        """生成NPC对话"""
        return await self.generate_response(
            user_input=player_input,
            character_id=context.get("character_id", "unknown"),
            scene_id=context.get("scene_id", "unknown"),
            game_context=context,
            npc_persona=npc
        )
    
    async def generate_quest_description(
        self,
        quest_type: str,
        difficulty: str,
        theme: str
    ) -> Dict[str, Any]:
        """生成任务描述"""
        prompt = f"请生成一个{difficulty}难度的{quest_type}任务,主题是{theme}:"
        
        response = self.llm.generate(
            prompt,
            max_tokens=384,
            temperature=0.8
        )
        
        # 简单解析(实际应用中需要更复杂的解析)
        lines = response.split("\n")
        
        return {
            "title": lines[0] if lines else "神秘任务",
            "description": "\n".join(lines[1:]) if len(lines) > 1 else response,
            "type": quest_type,
            "difficulty": difficulty
        }


# 预定义的NPC人设库
NPC_PERSONAS = {
    "elder": CharacterPersona(
        name="村长",
        role="村庄领导者",
        personality="智慧、慈祥、富有经验",
        background="村庄的长者,见证了无数冒险者的成长",
        speech_style="说话慢条斯理,喜欢用谚语"
    ),
    
    "merchant": CharacterPersona(
        name="商人",
        role="旅行商人",
        personality="精明、友好、热爱交易",
        background="来自远方的商人,游历各地收集稀有物品",
        speech_style="热情洋溢,喜欢讨价还价"
    ),
    
    "warrior": CharacterPersona(
        name="战士",
        role="冒险者前辈",
        personality="勇敢、正直、乐于助人",
        background="经验丰富的战士,退休后选择定居",
        speech_style="直来直去,充满战斗经验"
    ),
    
    "mage": CharacterPersona(
        name="法师",
        role="魔法导师",
        personality="神秘、睿智、有时古怪",
        background="钻研魔法多年的大师",
        speech_style="说话深奥,喜欢用魔法术语"
    )
}
