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
git clone https://github.com/EterUltimate/ai-rpg-engine.git
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
├── LICENSE               # MIT License (仅针对代码)
├── DATA_LICENSE.md       # RAG数据专用协议
├── NOTICE_ADDENDUM.md    # 重要许可声明
├── frontend/             # React前端应用
├── backend/
│   ├── gateway/          # Go API网关
│   └── services/
│       ├── game-engine/  # 游戏引擎服务
│       └── ai-engine/    # AI推理服务
├── data-core/            # 🔒 受限制的RAG数据目录
│   ├── vectors/          # 向量索引文件
│   └── knowledge_base/   # 知识库文件
├── database/             # 数据库文件
├── models/               # AI模型文件
├── scripts/              # 构建和部署脚本
│   └── build_own_data.py # 构建自定义数据的脚本
└── docs/                 # 文档
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

---

## ⚠️ 重要许可声明与数据使用限制

### 1. 许可范围区分 (License Scope Separation)

本项目采用 **混合许可模式**：

| 组件类型 | 包含目录 | 许可协议 | 允许商用 | 允许二次分发 |
| :--- | :--- | :--- | :---: | :---: |
| **源代码** | `frontend/`, `backend/`, `gateway/`, `docs/`, `scripts/` | **AGPL-3.0** | ✅ 是 (需开源) | ✅ 是 (需开源) |
| **RAG 核心数据** | `data-core/`, `database/`, `models/`, `*.bin`, `*.sqlite`, `vectors/` | **NC-ND 学习许可** | 🛑 **否** | 🛑 **否** |

### 2. RAG 数据库特别条款

本项目中包含的 **RAG 数据库核心内容**（预置向量、嵌入模型权重、剧情知识库等）仅供**学习和研究使用**。

- ❌ **严禁**将预置的 RAG 数据文件用于任何商业产品或服务
- ❌ **严禁**将预置的 RAG 数据文件二次分发（包括修改后的版本）
- 💡 **建议**：如需商用，请使用本引擎代码架构，并自行采集、清洗和构建符合您业务需求的数据集

### 3. 合规使用指南

- **开发者**：您可以自由 Fork、修改和部署代码部分。在部署时，请确保移除或替换受限制的 `database/`、`models/` 和 `data-core/` 目录下的预置文件
- **研究者**：您可以在本地完整运行项目进行学术分析，但不得公开分享包含预置数据的完整构建包

> **法律声明**：任何忽略此声明并滥用 RAG 数据内容的行为，均视为对作者知识产权的侵犯，作者保留追究法律责任的权利。

### 4. 构建自己的数据

我们提供了 `scripts/build_own_data.py` 脚本，帮助您构建自己的 RAG 数据库，从而完全规避许可限制：

```bash
python scripts/build_own_data.py --input your_data/ --output data-core/
```

---

## 📄 许可证

### 源代码许可证

本项目源代码采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 许可证。

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**AGPL-3.0 主要特点：**

- ✅ 你可以自由使用、修改和分发本软件
- ✅ 任何修改版本必须以相同许可证开源
- ✅ 通过网络提供服务时，必须向用户提供源代码
- 📖 查看 [LICENSE](./LICENSE) 文件了解完整条款

### RAG 数据许可证

RAG 数据库核心内容采用 **非商业学习许可协议**。详见 [DATA_LICENSE.md](./DATA_LICENSE.md)。

---

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解详情。

**注意**：贡献的代码将采用 AGPL-3.0 许可证，但不得包含受限制的数据内容。

## 📞 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
