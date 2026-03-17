# AI-RPG Engine 系统架构文档

## 📐 整体架构

AI-RPG Engine 采用**微服务架构**，分为四个主要组件：

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│                  http://localhost:5173                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Go API Gateway (Port 8000)                  │
│  - 路由分发  - 请求聚合  - CORS处理  - 限流保护              │
└───────────┬─────────────────────────────┬───────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────────┐     ┌───────────────────────────────┐
│  Game Engine (8001)   │     │    AI Engine (8002)          │
│  - 游戏状态管理        │     │    - RAG 检索系统            │
│  - 角色属性系统        │◄────►│    - LLM 推理引擎           │
│  - 任务系统           │     │    - 上下文管理              │
│  - 世界状态           │     │    - 角色扮演引擎            │
└───────────┬───────────┘     └───────────┬───────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────────┐     ┌───────────────────────────────┐
│   SQLite Database     │     │     ChromaDB Vector Store     │
│   - 角色数据           │     │     - 剧情向量索引            │
│   - 游戏存档           │     │     - NPC 对话知识库          │
│   - 任务进度           │     │     - 世界观设定库            │
└───────────────────────┘     └───────────────────────────────┘
```

---

## 🎮 核心组件说明

### 1. Frontend (React + Phaser)

**技术栈**:
- React 18 + TypeScript + Vite
- Phaser 3 (WebGL 2D游戏引擎)
- Zustand (状态管理)
- Tailwind CSS (UI样式)

**主要模块**:
```
frontend/
├── src/
│   ├── game/              # Phaser 游戏引擎
│   │   ├── scenes/        # 游戏场景
│   │   ├── entities/      # 游戏实体
│   │   └── systems/       # 游戏系统
│   ├── ui/                # React UI组件
│   │   ├── components/    # 通用组件
│   │   ├── chat/          # AI对话界面
│   │   └── hud/           # 游戏HUD
│   ├── api/               # API客户端
│   ├── store/             # Zustand状态管理
│   └── types/             # TypeScript类型定义
```

**核心职责**:
- 渲染2D游戏画面
- 处理用户输入
- 显示AI对话界面
- 管理客户端状态

---

### 2. API Gateway (Go + Gin)

**技术栈**:
- Go 1.22+
- Gin Web Framework

**主要功能**:
```go
// 路由配置
api := r.Group("/api/v1")
{
    // 游戏引擎路由
    api.Any("/game/*path", proxyGameEngine)
    api.Any("/character/*path", proxyGameEngine)
    api.Any("/actions/*path", proxyGameEngine)
    
    // AI引擎路由
    api.Any("/ai/*path", proxyAIEngine)
}
```

**核心职责**:
- 请求路由和反向代理
- CORS跨域处理
- 请求限流保护
- 统一错误处理
- 健康检查

---

### 3. Game Engine Service (Python + FastAPI)

**技术栈**:
- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- SQLite + aiosqlite

**核心模块**:
```python
backend/services/game-engine/
├── app/
│   ├── main.py            # FastAPI应用入口
│   ├── database.py        # 数据库连接
│   ├── models/            # 数据模型
│   │   └── models.py      # SQLAlchemy模型
│   ├── routers/           # API路由
│   │   ├── game.py        # 游戏状态API
│   │   ├── character.py   # 角色管理API
│   │   └── actions.py     # 动作执行API
│   └── game_logic/        # 游戏逻辑
│       ├── game_manager.py    # 游戏管理器
│       ├── world_manager.py   # 世界管理器
│       └── action_handler.py  # 动作处理器
```

**API端点**:
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/game/state/:id` | GET | 获取游戏状态 |
| `/api/v1/game/save` | POST | 保存游戏 |
| `/api/v1/game/load/:id` | GET | 加载存档 |
| `/api/v1/character/create` | POST | 创建角色 |
| `/api/v1/character/:id` | GET | 获取角色信息 |
| `/api/v1/actions/perform` | POST | 执行游戏动作 |

---

### 4. AI Engine Service (Python + FastAPI)

**技术栈**:
- Python 3.10+
- FastAPI
- llama.cpp (LLM推理)
- sentence-transformers (嵌入模型)
- ChromaDB (向量数据库)
- cross-encoder (重排模型)

**核心模块**:
```python
backend/services/ai-engine/
├── main.py                # FastAPI应用入口
├── llm/
│   └── llama_engine.py    # LLM推理引擎
├── rag/
│   ├── enhanced_rag.py        # RAG系统实现
│   └── context_manager.py     # 上下文管理
├── roleplay/
│   └── engine.py          # 角色扮演引擎
└── routers/
    ├── ai.py              # 基础AI API
    └── enhanced_ai.py     # 增强AI API
```

**RAG系统架构**:
```
用户输入
    │
    ▼
文本嵌入 (sentence-transformers)
    │
    ▼
向量检索 (ChromaDB)
    │
    ▼
结果重排 (cross-encoder)
    │
    ▼
上下文构建
    │
    ▼
LLM生成 (llama.cpp)
    │
    ▼
AI响应
```

**API端点**:
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/ai/chat` | POST | AI对话 |
| `/api/v1/ai/chat/stream` | GET | 流式对话 (SSE) |
| `/api/v1/ai/generate` | POST | 生成游戏内容 |

---

## 🗄️ 数据存储架构

### 1. SQLite (关系型数据)

存储内容:
- 角色数据 (Character)
- 游戏存档 (GameSave)
- 任务进度 (QuestProgress)
- 物品栏 (Inventory)
- 世界状态快照 (WorldState)

**数据模型**:
```python
class Character(Base):
    __tablename__ = "characters"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    level: Mapped[int] = mapped_column(default=1)
    
    # 属性系统
    strength: Mapped[int] = mapped_column(default=10)
    agility: Mapped[int] = mapped_column(default=10)
    intelligence: Mapped[int] = mapped_column(default=10)
    charisma: Mapped[int] = mapped_column(default=10)
    
    # 状态系统
    hp: Mapped[int] = mapped_column(default=100)
    mp: Mapped[int] = mapped_column(default=50)
    
    # 位置
    scene_id: Mapped[str]
    x: Mapped[float]
    y: Mapped[float]
```

---

### 2. ChromaDB (向量数据库)

存储内容:
- 剧情向量索引
- NPC对话知识库
- 世界观设定库
- 任务模板库

**集合结构**:
```python
collections = {
    "story_events": "剧情事件向量",
    "npc_dialogues": "NPC对话模板",
    "world_knowledge": "世界观设定",
    "quest_templates": "任务模板",
    "item_descriptions": "物品描述"
}
```

---

## 🔄 数据流分析

### 1. AI对话流程

```
1. 用户输入对话
   ↓
2. 前端发送到 API Gateway
   ↓
3. Gateway 路由到 AI Engine
   ↓
4. AI Engine 处理:
   a. 文本嵌入
   b. 向量检索相关上下文
   c. 重排检索结果
   d. 构建完整提示词
   e. LLM生成响应
   ↓
5. 返回响应给前端
   ↓
6. 前端显示AI对话
```

### 2. 游戏动作流程

```
1. 用户触发动作 (如: 探索、战斗)
   ↓
2. 前端发送到 API Gateway
   ↓
3. Gateway 路由到 Game Engine
   ↓
4. Game Engine 处理:
   a. 验证动作合法性
   b. 计算动作结果
   c. 更新游戏状态
   d. 触发后续事件
   ↓
5. 返回结果给前端
   ↓
6. 前端更新游戏画面
```

---

## 🔐 安全架构

### 1. CORS配置

```python
# 各服务的CORS配置
allow_origins = [
    "http://localhost:5173",  # 前端开发服务器
    "http://localhost:8000",  # API网关
    "http://localhost:3000",  # 备用前端端口
]
```

### 2. API限流

```go
// Go Gateway 限流配置
rate.Limit(100, time.Minute) // 每分钟100个请求
```

### 3. 输入验证

- 所有API端点进行参数验证
- 防止SQL注入 (使用ORM参数化查询)
- 防止XSS攻击 (前端内容转义)

---

## 📦 部署架构

### 开发环境
```
本地机器:
├── Frontend (npm run dev)    → Port 5173
├── Game Engine (python)      → Port 8001
├── AI Engine (python)        → Port 8002
└── API Gateway (go run)      → Port 8000
```

### Docker环境
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
  
  gateway:
    build: ./backend/gateway
    ports: ["8000:8000"]
  
  game-engine:
    build: ./backend/services/game-engine
    ports: ["8001:8001"]
  
  ai-engine:
    build: ./backend/services/ai-engine
    ports: ["8002:8002"]
```

### 生产环境
```
Nginx (反向代理)
    │
    ├── Frontend (静态文件)
    │
    └── API Gateway (负载均衡)
            │
            ├── Game Engine (多实例)
            │
            └── AI Engine (多实例)
```

---

## 🎯 性能优化策略

### 1. 前端优化
- Vite自动代码分割
- 游戏资源懒加载
- React组件memo化
- Phaser场景预加载

### 2. 后端优化
- 数据库连接池
- 异步I/O (async/await)
- API响应缓存
- 向量索引优化 (HNSW)

### 3. AI优化
- LLM模型量化 (Q4_K_M)
- 向量检索批处理
- 上下文窗口管理
- GPU加速 (可选)

---

## 🔄 扩展性设计

### 1. 水平扩展
- 无状态服务设计
- 数据库读写分离
- 向量数据库分片
- 负载均衡支持

### 2. 模块化设计
- 微服务独立部署
- API版本管理
- 插件化游戏逻辑
- 可替换的LLM后端

### 3. 数据迁移
- SQLite → PostgreSQL
- ChromaDB → Milvus/Qdrant
- 本地存储 → 云存储

---

## 📚 相关文档

- [API接口文档](./api-spec.md)
- [部署指南](./deployment.md)
- [模型配置指南](../models/README.md)
- [构建自定义数据](../scripts/build_own_data.py)
