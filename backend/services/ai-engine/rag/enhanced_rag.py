"""
增强版RAG引擎 - 包含记忆管理、上下文构建和智能检索
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime
import json


class MemoryType:
    """记忆类型枚举"""
    DIALOGUE = "dialogue"          # 对话记忆
    EVENT = "event"                # 重要事件
    QUEST = "quest"                # 任务相关
    WORLD = "world"                # 世界知识
    CHARACTER = "character"        # 角色信息
    LOCATION = "location"          # 地点信息


class EnhancedRAGSystem:
    """增强版RAG系统"""
    
    def __init__(
        self,
        chromadb_path: str = "./database/chromadb",
        embedding_model: str = "all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        use_reranker: bool = True
    ):
        self.chromadb_path = chromadb_path
        self.embedding_model_name = embedding_model
        self.use_reranker = use_reranker
        
        # 初始化ChromaDB
        os.makedirs(chromadb_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=chromadb_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建集合
        self.collections = self._init_collections()
        
        # 加载嵌入模型
        print(f"🔧 Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # 加载重排模型(可选)
        if use_reranker:
            print(f"🔧 Loading reranker model: {reranker_model}")
            self.reranker = CrossEncoder(reranker_model)
        else:
            self.reranker = None
        
        print("✅ Enhanced RAG System initialized")
    
    def _init_collections(self) -> Dict[str, chromadb.Collection]:
        """初始化所有集合"""
        collections = {}
        
        # 角色记忆集合
        collections["character_memories"] = self.client.get_or_create_collection(
            name="character_memories",
            metadata={
                "description": "角色长期记忆和对话历史",
                "hnsw:space": "cosine"
            }
        )
        
        # 世界知识集合
        collections["world_knowledge"] = self.client.get_or_create_collection(
            name="world_knowledge",
            metadata={
                "description": "世界观、历史、规则等背景知识",
                "hnsw:space": "cosine"
            }
        )
        
        # 场景上下文集合
        collections["scene_contexts"] = self.client.get_or_create_collection(
            name="scene_contexts",
            metadata={
                "description": "场景描述、NPC、事件等",
                "hnsw:space": "cosine"
            }
        )
        
        # 任务历史集合
        collections["quest_history"] = self.client.get_or_create_collection(
            name="quest_history",
            metadata={
                "description": "任务历史和结果",
                "hnsw:space": "cosine"
            }
        )
        
        return collections
    
    def embed_text(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        return self.embedder.encode(text, convert_to_numpy=True).tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入向量"""
        return self.embedder.encode(texts, convert_to_numpy=True).tolist()
    
    async def add_memory(
        self,
        collection_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """添加记忆到向量库"""
        embedding = self.embed_text(content)
        
        if memory_id is None:
            memory_id = f"{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = datetime.now().isoformat()
        
        self.collections[collection_name].add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    async def search_memories(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """搜索记忆"""
        query_embedding = self.embed_text(query)
        
        results = self.collections[collection_name].query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            where_document=where_document
        )
        
        memories = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                memory = {
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                }
                memories.append(memory)
        
        return memories
    
    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """使用Cross-Encoder重排序结果"""
        if not self.reranker or not results:
            return results[:top_k]
        
        # 构建查询-文档对
        pairs = [(query, result["content"]) for result in results]
        
        # 计算相关性分数
        scores = self.reranker.predict(pairs)
        
        # 根据分数排序
        scored_results = list(zip(results, scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k结果
        reranked = []
        for result, score in scored_results[:top_k]:
            result["rerank_score"] = float(score)
            reranked.append(result)
        
        return reranked
    
    async def build_game_context(
        self,
        query: str,
        character_id: str,
        scene_id: str,
        include_world_knowledge: bool = True,
        max_context_length: int = 2000
    ) -> Dict[str, Any]:
        """构建游戏上下文"""
        context_parts = {}
        total_length = 0
        
        # 1. 检索角色记忆
        character_memories = await self.search_memories(
            "character_memories",
            query,
            n_results=5,
            where_filter={"character_id": character_id}
        )
        
        if character_memories:
            context_parts["character_memories"] = character_memories
            total_length += sum(len(m["content"]) for m in character_memories)
        
        # 2. 检索场景上下文
        if total_length < max_context_length:
            scene_contexts = await self.search_memories(
                "scene_contexts",
                scene_id,
                n_results=3,
                where_filter={"scene_id": scene_id}
            )
            
            if scene_contexts:
                context_parts["scene_contexts"] = scene_contexts
                total_length += sum(len(m["content"]) for m in scene_contexts)
        
        # 3. 检索世界知识
        if include_world_knowledge and total_length < max_context_length:
            world_knowledge = await self.search_memories(
                "world_knowledge",
                query,
                n_results=3
            )
            
            if world_knowledge:
                context_parts["world_knowledge"] = world_knowledge
                total_length += sum(len(m["content"]) for m in world_knowledge)
        
        # 4. 重排序所有结果
        all_memories = []
        for memories in context_parts.values():
            all_memories.extend(memories)
        
        if all_memories:
            reranked = self.rerank_results(query, all_memories, top_k=10)
            context_parts["reranked_memories"] = reranked
        
        return context_parts
    
    def format_context_for_llm(
        self,
        context: Dict[str, Any],
        format_style: str = "markdown"
    ) -> str:
        """格式化上下文为LLM提示词"""
        if format_style == "markdown":
            return self._format_markdown(context)
        elif format_style == "narrative":
            return self._format_narrative(context)
        else:
            return self._format_simple(context)
    
    def _format_markdown(self, context: Dict[str, Any]) -> str:
        """Markdown格式"""
        parts = []
        
        if "character_memories" in context:
            parts.append("## 角色记忆\n")
            for mem in context["character_memories"][:3]:
                parts.append(f"- {mem['content']}\n")
        
        if "scene_contexts" in context:
            parts.append("\n## 场景信息\n")
            for mem in context["scene_contexts"][:2]:
                parts.append(f"- {mem['content']}\n")
        
        if "world_knowledge" in context:
            parts.append("\n## 世界背景\n")
            for mem in context["world_knowledge"][:2]:
                parts.append(f"- {mem['content']}\n")
        
        return "\n".join(parts)
    
    def _format_narrative(self, context: Dict[str, Any]) -> str:
        """叙事格式"""
        parts = []
        
        if "scene_contexts" in context:
            scene_desc = context["scene_contexts"][0]["content"] if context["scene_contexts"] else ""
            parts.append(f"当前场景: {scene_desc}\n\n")
        
        if "character_memories" in context:
            parts.append("相关记忆: ")
            for mem in context["character_memories"][:2]:
                parts.append(f"{mem['content']} ")
            parts.append("\n")
        
        return "".join(parts)
    
    def _format_simple(self, context: Dict[str, Any]) -> str:
        """简单格式"""
        parts = []
        
        for key, memories in context.items():
            if isinstance(memories, list):
                for mem in memories[:2]:
                    parts.append(mem["content"])
        
        return " ".join(parts)
    
    async def update_character_memory(
        self,
        character_id: str,
        interaction: str,
        importance: int = 5,
        memory_type: str = MemoryType.DIALOGUE
    ):
        """更新角色记忆"""
        await self.add_memory(
            "character_memories",
            interaction,
            metadata={
                "character_id": character_id,
                "importance": importance,
                "type": memory_type,
                "source": "player_interaction"
            }
        )
    
    async def get_character_summary(self, character_id: str) -> Dict[str, Any]:
        """获取角色记忆摘要"""
        all_memories = await self.search_memories(
            "character_memories",
            "character history",
            n_results=20,
            where_filter={"character_id": character_id}
        )
        
        # 按重要性排序
        important_memories = sorted(
            all_memories,
            key=lambda m: m["metadata"].get("importance", 0),
            reverse=True
        )
        
        return {
            "total_memories": len(all_memories),
            "important_memories": important_memories[:5],
            "recent_memories": all_memories[:5]
        }
    
    def clear_collection(self, collection_name: str):
        """清空集合"""
        if collection_name in self.collections:
            # 删除并重新创建集合
            self.client.delete_collection(collection_name)
            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata=self.collections[collection_name].metadata
            )
    
    def get_collection_stats(self) -> Dict[str, int]:
        """获取集合统计信息"""
        stats = {}
        for name, collection in self.collections.items():
            count = collection.count()
            stats[name] = count
        return stats
