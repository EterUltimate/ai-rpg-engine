# 集成测试计划

## 测试环境检查清单

### 1. 前端测试

#### 依赖检查
```bash
cd frontend
npm install
npm run build
```

#### 测试项
- [ ] React应用正常启动
- [ ] TypeScript编译无错误
- [ ] Vite构建成功
- [ ] Phaser游戏引擎初始化
- [ ] UI组件渲染正常

### 2. 后端测试

#### Go网关
```bash
cd backend/gateway
go mod download
go build -o gateway cmd/main.go
```

#### 测试项
- [ ] Go编译成功
- [ ] 服务启动正常
- [ ] API路由响应
- [ ] WebSocket连接

#### Python游戏引擎
```bash
cd backend/services/game-engine
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
python main.py
```

#### 测试项
- [ ] 虚拟环境创建
- [ ] 依赖安装成功
- [ ] 数据库初始化
- [ ] FastAPI服务启动
- [ ] API端点响应

#### Python AI引擎
```bash
cd backend/services/ai-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 测试项
- [ ] 依赖安装成功
- [ ] ChromaDB初始化
- [ ] 嵌入模型加载
- [ ] LLM模型加载(可选)
- [ ] API服务启动

### 3. 集成测试

#### API端点测试
- [ ] 健康检查: GET /health
- [ ] 角色创建: POST /api/v1/character/create
- [ ] 游戏状态: GET /api/v1/game/state/:id
- [ ] AI对话: POST /api/v1/ai/chat

#### 完整流程测试
1. [ ] 创建角色
2. [ ] 获取游戏状态
3. [ ] 执行移动动作
4. [ ] 与NPC对话
5. [ ] AI生成响应
6. [ ] 保存游戏
7. [ ] 加载游戏

### 4. 性能测试

- [ ] API响应时间 < 100ms
- [ ] 前端首屏加载 < 3s
- [ ] AI生成速度 > 20 tokens/s
- [ ] 内存占用合理

---

## 测试脚本

见 `tests/` 目录下的测试脚本
