# AI-RPG Engine

🤖 一个由大语言模型驱动的、嵌入和重排模型维护RAG的AI角色扮演RPG游戏

## 🎮 项目特点

- **AI驱动的RPG体验**: 大语言模型实时生成剧情、对话和任务
- **RAG记忆系统**: 向量检索+重排序,实现智能上下文管理
- **图形化游戏界面**: 基于Phaser 3的2D游戏引擎
- **一次构建,多端运行**: 支持Web、桌面(Windows/macOS/Linux)和移动端

## 🏗️ 技术栈

### 前端
- **React 18** + TypeScript + Vite
- **Phaser 3** - WebGL 2D游戏引擎
- **Tailwind CSS** - UI样式
- **Zustand** - 状态管理

### 后端
- **Go (Gin)** - API网关和高性能路由
- **Python (FastAPI)** - 游戏引擎和AI服务
- **SQLite + ChromaDB** - 数据存储

### AI
- **llama.cpp** - 本地LLM推理
- **sentence-transformers** - 嵌入模型
- **cross-encoder** - 重排模型

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Go 1.22+

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd ai-rpg-engine

# 安装前端依赖
cd frontend
npm install

# 安装后端依赖
cd ../backend/services/game-engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd ../ai-engine
pip install -r requirements.txt

# 编译Go网关
cd ../../gateway
go mod download
go build -o gateway cmd/main.go
```

### 运行

```bash
# 启动AI服务
cd backend/services/ai-engine
python main.py

# 启动游戏引擎
cd ../game-engine
python main.py

# 启动API网关
cd ../../gateway
./gateway

# 启动前端开发服务器
cd ../../../frontend
npm run dev
```

访问 http://localhost:5173 开始游戏!

## 📁 项目结构

```
ai-rpg-engine/
├── frontend/          # React前端应用
├── backend/
│   ├── gateway/       # Go API网关
│   └── services/
│       ├── game-engine/  # 游戏引擎服务
│       └── ai-engine/    # AI推理服务
├── database/          # 数据库文件
├── models/            # AI模型文件
└── docs/              # 文档
```

## 📖 文档

- [架构设计](./docs/architecture.md)
- [API文档](./docs/api-spec.md)
- [部署指南](./docs/deployment.md)

## 📝 开发路线图

- [x] 项目架构设计
- [ ] 项目脚手架搭建
- [ ] 前端游戏界面
- [ ] 后端游戏引擎
- [ ] RAG系统实现
- [ ] LLM集成
- [ ] 多端打包

## 📄 许可证

MIT License
