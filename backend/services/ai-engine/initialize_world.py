"""
初始化脚本 - 初始化游戏世界数据
"""
import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.enhanced_rag import EnhancedRAGSystem


async def initialize_game_data():
    """初始化游戏数据到RAG系统"""
    print("🎮 初始化游戏世界数据...")
    
    # 初始化RAG系统
    rag = EnhancedRAGSystem(
        chromadb_path="./database/chromadb",
        embedding_model="all-MiniLM-L6-v2",
        use_reranker=True
    )
    
    # 添加世界背景知识
    print("📚 添加世界背景...")
    world_lore = [
        "艾尔德兰大陆是一个充满魔法和奇迹的世界,由多个王国和城邦组成。",
        "大陆的主要种族包括人类、精灵、矮人、兽人等,他们和平共处了数百年。",
        "古老的魔法遗迹散布在大陆各处,许多冒险者探索这些遗迹寻找宝藏和秘密。",
        "近年来,一股神秘的黑暗势力开始苏醒,各地频繁出现怪物袭击事件。",
        "冒险者公会是大陆上最大的组织,负责发布任务和协调冒险者。",
        "魔法师塔是研究魔法的主要场所,聚集了众多强大的法师。"
    ]
    
    for lore in world_lore:
        await rag.add_memory(
            "world_knowledge",
            lore,
            metadata={"category": "history", "source": "world_lore"}
        )
    
    # 添加场景信息
    print("🗺️  添加场景信息...")
    scenes = {
        "village_001": "起始村庄是一个宁静的小村庄,村中央有一口据说有神奇力量的古井。村庄周围是肥沃的农田,村民以务农为生。",
        "forest_001": "神秘森林位于村庄北边,古树参天,光线昏暗。传说森林深处有一个被遗忘的洞穴,藏有古代宝藏。",
        "shop_001": "村庄杂货店由一位名叫卡尔的商人经营,出售各种冒险必需品和稀有物品。",
        "cave_001": "黑暗洞穴隐藏在森林深处,据说曾经是古代法师的实验室,现在充满了危险的怪物。"
    }
    
    for scene_id, description in scenes.items():
        await rag.add_memory(
            "scene_contexts",
            description,
            metadata={
                "scene_id": scene_id,
                "type": "location"
            }
        )
    
    # 添加角色模板
    print("👥 添加角色模板...")
    character_templates = [
        "战士擅长近战攻击,高生命值和防御力,适合在前线作战。",
        "法师精通各种魔法,可以造成大量魔法伤害,但防御较弱。",
        "游侠擅长远程攻击和追踪,是优秀的探险者和猎人。",
        "牧师拥有治疗和辅助魔法,是队伍中不可或缺的支援角色。"
    ]
    
    for template in character_templates:
        await rag.add_memory(
            "world_knowledge",
            template,
            metadata={"category": "character_class", "source": "game_rules"}
        )
    
    # 添加战斗规则
    print("⚔️  添加游戏规则...")
    game_rules = [
        "战斗时,先攻值高的角色先行动。攻击检定需要掷骰子加上属性修正值。",
        "使用技能需要消耗魔法值或体力值。技能威力受角色等级和属性影响。",
        "装备可以提升角色的属性和能力。稀有装备通常有特殊效果。",
        "完成任务可以获得经验值、金币和物品奖励。经验值达到一定数量可以升级。"
    ]
    
    for rule in game_rules:
        await rag.add_memory(
            "world_knowledge",
            rule,
            metadata={"category": "game_rules", "source": "manual"}
        )
    
    # 获取统计信息
    stats = rag.get_collection_stats()
    
    print("\n✅ 初始化完成!")
    print("\n📊 数据统计:")
    for collection_name, count in stats.items():
        print(f"  - {collection_name}: {count} 条记录")
    
    print("\n💡 提示: 现在可以启动游戏服务并开始游戏了!")


if __name__ == "__main__":
    asyncio.run(initialize_game_data())
