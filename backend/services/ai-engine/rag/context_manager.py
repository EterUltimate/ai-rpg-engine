import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os


class ContextManager:
    """RAG上下文管理器"""
    
    def __init__(
        self,
        chromadb_path: str = "./database/chromadb",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.chromadb_path = chromadb_path
        self.embedding_model_name = embedding_model
        
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
        self.collections = {
            "character_memories": self.client.get_or_create_collection(
                name="character_memories",
                metadata={"description": "角色长期记忆"}
            ),
            "world_knowledge": self.client.get_or_create_collection(
                name="world_knowledge",
                metadata={"description": "世界背景知识"}
            ),
            "scene_contexts": self.client.get_or_create_collection(
                name="scene_contexts",
                metadata={"description": "场景上下文信息"}
            )
        }
        
        # 初始化嵌入模型
        print(f"🔧 Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        print("✅ Embedding model loaded")
    
    def embed_text(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        return self.embedder.encode(text).tolist()
    
    async def retrieve_memories(
        self,
        query: str,
        character_id: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """检索角色记忆"""
        query_embedding = self.embed_text(query)
        
        results = self.collections["character_memories"].query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"character_id": character_id}
        )
        
        memories = []
        for i, doc in enumerate(results["documents"][0]):
            memories.append({
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None
            })
        
        return memories
    
    async def get_scene_context(
        self,
        scene_id: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """获取场景上下文"""
        results = self.collections["scene_contexts"].query(
            query_texts=[scene_id],
            n_results=n_results,
            where={"scene_id": scene_id}
        )
        
        contexts = []
        for i, doc in enumerate(results["documents"][0] if results["documents"] else []):
            contexts.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
            })
        
        return contexts
    
    async def add_memory(
        self,
        character_id: str,
        content: str,
        importance: int = 5,
        memory_type: str = "event"
    ):
        """添加角色记忆"""
        embedding = self.embed_text(content)
        
        self.collections["character_memories"].add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "character_id": character_id,
                "importance": importance,
                "type": memory_type
            }],
            ids=[f"{character_id}_{len(self.collections['character_memories'].get()['ids'])}"]
        )
    
    async def build_context(
        self,
        query: str,
        character_id: str,
        scene_id: str
    ) -> str:
        """构建完整上下文"""
        # 检索相关记忆
        memories = await self.retrieve_memories(query, character_id)
        
        # 获取场景信息
        scene_contexts = await self.get_scene_context(scene_id)
        
        # 构建上下文字符串
        context_parts = []
        
        if memories:
            context_parts.append("### 相关记忆:")
            for mem in memories[:3]:  # 最多3条记忆
                context_parts.append(f"- {mem['content']}")
        
        if scene_contexts:
            context_parts.append("\n### 场景信息:")
            for ctx in scene_contexts:
                context_parts.append(f"- {ctx['content']}")
        
        return "\n".join(context_parts) if context_parts else ""
