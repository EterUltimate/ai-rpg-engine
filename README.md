```md
# AI-RPG Engine

> 一个由大语言模型驱动的图形化 AI RPG 引擎 / 游戏原型。
> 基于 **LLM + RAG + Phaser 3**，实现动态剧情、对话、任务与记忆管理。

![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Status](https://img.shields.io/badge/status-MVP%20%2F%20Alpha-orange)

---

## 📌 项目状态

**当前阶段：MVP / Alpha**

本项目已经实现本地可运行的核心链路，包括：

- 图形化前端界面
- Go 网关 + Python 服务联调
- AI 对话与剧情生成
- 基于向量检索 + 重排的 RAG 记忆流程
- 本地模型推理接入

当前版本仍存在以下限制：

- 部署和依赖安装较复杂
- 首次运行需要一定命令行基础
- 模型、数据与环境配置需要手动准备
- 更适合开发者和研究者体验

---

## ✨ 特点

- **AI 驱动 RPG 体验**：动态生成剧情、对话和任务
- **RAG 记忆系统**：向量检索 + 重排序维护上下文
- **图形化游戏界面**：基于 Phaser 3 的 2D 场景
- **分层架构**：前端、网关、游戏引擎、AI 引擎解耦
- **本地推理支持**：基于 `llama.cpp`
- **支持自建数据**：可替换预置 RAG 数据

---

## 🏗️ 技术栈

**Frontend**
- React 18
- TypeScript
- Vite
- Phaser 3
- Tailwind CSS
- Zustand

**Backend**
- Go (Gin)
- Python (FastAPI)
- SQLite
- ChromaDB

**AI**
- llama.cpp
- sentence-transformers
- cross-encoder

---

## 🚀 快速开始

> 推荐先阅读 [QUICKSTART.md](./QUICKSTART.md)

### 环境要求

- Node.js 18+
- Python 3.10+
- Go 1.22+

### 安装

```bash
git clone https://github.com/EterUltimate/ai-rpg-engine.git
cd ai-rpg-engine

# 前端
cd frontend
npm install
cd ..

# 游戏引擎
cd backend/services/game-engine
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../../..

# AI 引擎
cd backend/services/ai-engine
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../../..

# Go 网关
cd backend/gateway
go mod download
go build -o gateway cmd/main.go
cd ../..
```

### 运行

分别打开 4 个终端：

```bash
# 终端 1
cd backend/services/ai-engine
python main.py
```

```bash
# 终端 2
cd backend/services/game-engine
python main.py
```

```bash
# 终端 3
cd backend/gateway
./gateway   # Windows: gateway.exe
```

```bash
# 终端 4
cd frontend
npm run dev
```

访问：

```text
http://localhost:5173
```

---

## 📁 项目结构

```text
ai-rpg-engine/
├── frontend/                # React + Phaser 前端
├── backend/
│   ├── gateway/             # Go API 网关
│   └── services/
│       ├── game-engine/     # Python 游戏引擎
│       └── ai-engine/       # Python AI / RAG 服务
├── data-core/               # 🔒 受限制的 RAG 数据目录
├── database/                # 数据库与本地存储
├── models/                  # 本地模型目录
├── scripts/                 # 安装、构建、诊断脚本
├── docs/                    # 项目文档
├── QUICKSTART.md
├── LICENSE
├── DATA_LICENSE.md
└── NOTICE_ADDENDUM.md
```

---

## 📚 文档

- [快速启动指南](./QUICKSTART.md)
- [架构设计](./docs/architecture.md)
- [API 文档](./docs/api-spec.md)
- [部署指南](./docs/deployment.md)
- [贡献指南](./CONTRIBUTING.md)

---

## ⚠️ 已知问题

当前版本主要问题集中在工程可用性，而不是核心功能：

- 安装链路较长
- 多服务启动步骤较多
- 模型与数据准备成本较高
- 跨平台脚本体验仍在持续优化

如果你遇到问题，欢迎提交 Issue。

---

## 🔒 许可说明

本项目采用 **混合许可模式**：

| 组件 | 范围 | 许可 |
| :-- | :-- | :-- |
| 源代码 | `frontend/`, `backend/`, `docs/`, `scripts/` 等 | **AGPL-3.0** |
| RAG 核心数据 | `data-core/`, `database/`, `models/` 等 | **非商业学习许可** |

### 说明
- ✅ 代码可在遵守 AGPL-3.0 的前提下使用、修改、分发
- ❌ 预置 RAG 数据不得用于商业用途
- ❌ 预置 RAG 数据不得二次分发
- 💡 如需商用，建议自行构建数据集

详见：
- [LICENSE](./LICENSE)
- [DATA_LICENSE.md](./DATA_LICENSE.md)
- [NOTICE_ADDENDUM.md](./NOTICE_ADDENDUM.md)

---

## 🤝 贡献

欢迎提交：

- Bug 反馈
- 文档修正
- 部署优化
- 脚本改进
- 性能优化建议

请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

> 注意：请不要提交受限制的数据内容。

---

## 🙏 说明

这是一个由个人开发者推进的实验性项目。
目前已具备可运行的 MVP，但仍在快速迭代与工程收敛中。

如果你愿意试用、提 Issue、补文档或帮忙优化部署体验，我会非常感谢。
```
