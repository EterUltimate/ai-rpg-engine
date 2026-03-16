# API接口规范

## 概述

AI-RPG Engine 提供RESTful API和WebSocket接口,支持游戏状态管理、AI对话、角色管理等功能。

**基础URL**: `http://localhost:8000/api/v1`

---

## AI相关接口

### POST /ai/chat

AI对话接口,返回AI生成的回复。

**请求体**:
```json
{
  "message": "我想探索这个神秘的洞穴",
  "character_id": "char_123",
  "scene_id": "scene_forest_001"
}
```

**响应**:
```json
{
  "response": "你走进了一个昏暗的洞穴,火把的光芒在潮湿的墙壁上闪烁..."
}
```

### GET /ai/chat/stream

流式对话接口,使用Server-Sent Events (SSE) 实现实时响应。

**参数**:
- `message` (query): 用户消息
- `character_id` (query): 角色ID
- `scene_id` (query): 场景ID

**响应**: SSE流

### POST /ai/generate

生成游戏内容(任务、NPC对话、物品等)。

**请求体**:
```json
{
  "type": "quest",
  "context": {
    "player_level": 5,
    "location": "魔法森林"
  }
}
```

**响应**:
```json
{
  "type": "quest",
  "content": {
    "title": "失落的魔法水晶",
    "description": "在魔法森林深处找到失落的魔法水晶..."
  }
}
```

---

## 游戏相关接口

### GET /game/state/:character_id

获取游戏状态。

**响应**:
```json
{
  "character_id": "char_123",
  "name": "勇敢的冒险者",
  "level": 5,
  "attributes": {
    "strength": 15,
    "agility": 12,
    "intelligence": 10,
    "charisma": 8
  },
  "status": {
    "hp": 85,
    "max_hp": 100,
    "mp": 40,
    "max_mp": 50
  },
  "scene": "forest_entrance"
}
```

### POST /game/save

保存游戏进度。

**请求体**:
```json
{
  "character_id": "char_123",
  "state": {
    "quest_progress": {},
    "world_state": {},
    "character_snapshot": {}
  }
}
```

**响应**:
```json
{
  "success": true,
  "save_id": "save_456",
  "message": "Game saved successfully"
}
```

### GET /game/load/:save_id

加载游戏存档。

**响应**:
```json
{
  "save_id": "save_456",
  "character_id": "char_123",
  "scene_id": "forest_entrance",
  "quest_progress": {},
  "world_state": {},
  "saved_at": "2024-01-15T10:30:00"
}
```

### POST /game/action

执行游戏动作。

**请求体**:
```json
{
  "action": "attack",
  "target": "goblin_01"
}
```

**响应**:
```json
{
  "success": true,
  "result": "你攻击了哥布林,造成了15点伤害!"
}
```

---

## 角色相关接口

### GET /character/:character_id

获取角色信息。

### POST /character/create

创建新角色。

**请求体**:
```json
{
  "name": "艾莉丝",
  "attributes": {
    "strength": 12,
    "agility": 14,
    "intelligence": 16,
    "charisma": 10
  }
}
```

**响应**:
```json
{
  "id": "char_123",
  "name": "艾莉丝",
  "level": 1,
  "attributes": {...},
  "message": "Character created successfully"
}
```

### PUT /character/:character_id

更新角色信息。

---

## WebSocket接口

### 连接

```
ws://localhost:8000/ws
```

### 消息格式

```json
{
  "type": "chat",
  "data": {
    "message": "你好",
    "character_id": "char_123"
  }
}
```

---

## 错误响应

所有接口在出错时返回统一格式:

```json
{
  "error": "错误描述",
  "detail": "详细错误信息"
}
```

---

## 认证

当前版本暂无认证,未来将支持JWT Token认证。

---

## 限流

API网关实现了限流保护:
- 每分钟最多100个请求
- 超过限制返回 429 Too Many Requests

---

## CORS

允许的源:
- http://localhost:5173
- http://localhost:3000
