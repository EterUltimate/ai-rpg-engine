# 🚀 AI-RPG Engine 构建与启动指南

本文档提供详细的构建和启动步骤，帮助您快速运行 AI-RPG Engine。

---

## 📋 目录

- [环境要求](#环境要求)
- [快速启动（推荐）](#快速启动推荐)
- [手动安装](#手动安装)
- [启动服务](#启动服务)
- [常见问题](#常见问题)

---

## 🔧 环境要求

### 必需软件

| 软件 | 版本要求 | 用途 | 下载地址 |
|------|---------|------|---------|
| **Node.js** | 18+ | 前端应用 | [nodejs.org](https://nodejs.org/) |
| **Python** | 3.10+ | 后端服务 | [python.org](https://www.python.org/) |
| **Go** | 1.22+ | API 网关 | [golang.org](https://golang.org/) |

**Windows Python 安装注意事项**:
- 推荐从 [python.org](https://www.python.org/) 下载安装，会自动安装 Python Launcher (`py` 命令)
- 如果从 Microsoft Store 安装，可能需要手动添加到 PATH
- 脚本会自动检测 `py` 或 `python` 命令

### 可选软件

- **Git**: 用于克隆仓库和版本控制
- **Make**: 用于简化命令（Windows 用户可使用 Python 脚本）

### 硬件要求

- **内存**: 最少 8GB，推荐 16GB+
- **存储**: 10GB+ 可用空间（用于模型和数据）
- **CPU**: 4核+ 推荐

---

## ⚡ 快速启动（推荐）

### 方式一：使用自动化脚本

**Windows 用户**:
```cmd
# 1. 克隆仓库
git clone https://github.com/EterUltimate/ai-rpg-engine.git
cd ai-rpg-engine

# 2. 运行安装脚本
scripts\setup.bat

# 3. 下载模型（首次运行）
scripts\download-models.bat

# 4. 启动所有服务
scripts\dev-new.bat
```

**Linux/macOS 用户**:
```bash
# 1. 克隆仓库
git clone https://github.com/EterUltimate/ai-rpg-engine.git
cd ai-rpg-engine

# 2. 运行安装脚本
python scripts/setup.py

# 3. 下载模型（首次运行）
python scripts/download-models.py

# 4. 启动所有服务
python scripts/dev.py
```

### 方式二：使用 Makefile

```bash
# 安装依赖
make setup

# 下载模型
make download-models

# 启动服务
make dev
```

---

## 🔨 手动安装

如果自动脚本遇到问题，可以按照以下步骤手动安装。

### 1. 克隆仓库

```bash
git clone https://github.com/EterUltimate/ai-rpg-engine.git
cd ai-rpg-engine
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

**可能遇到的问题**:
- 如果 npm 安装慢，可以使用国内镜像：
  ```bash
  npm config set registry https://registry.npmmirror.com
  npm install
  ```

### 3. 安装游戏引擎依赖

```bash
cd backend/services/game-engine

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

cd ../../..
```

### 4. 安装 AI 引擎依赖

```bash
cd backend/services/ai-engine

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

cd ../../..
```

**可能遇到的问题**:
- 如果 pip 安装慢，可以使用国内镜像：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 5. 编译 Go 网关

```bash
cd backend/gateway

# 下载 Go 模块
go mod download

# 编译
# Windows:
go build -o gateway.exe cmd/main.go
# Linux/macOS:
go build -o gateway cmd/main.go

cd ../..
```

**可能遇到的问题**:
- 如果 Go 模块下载慢，可以设置代理：
  ```bash
  go env -w GOPROXY=https://goproxy.cn,direct
  go mod download
  ```

### 6. 创建必要的目录

```bash
# 创建数据库目录
mkdir -p database/sqlite
mkdir -p database/chromadb

# 创建模型目录
mkdir -p models/llm
mkdir -p models/embeddings
mkdir -p models/rerankers

# 创建日志目录
mkdir -p logs
```

### 7. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置模型路径等参数
```

---

## 🎮 启动服务

### 方式一：使用统一启动脚本（推荐）

```bash
# Python 方式
python scripts/dev.py

# 或使用 Makefile
make dev
```

这个脚本会：
1. 检查环境和依赖
2. 检查模型文件
3. 自动启动所有服务
4. 输出日志和访问地址

### 方式二：手动启动（需要 4 个终端）

**终端 1 - AI 引擎**:
```bash
cd backend/services/ai-engine
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
python main.py
```

**终端 2 - 游戏引擎**:
```bash
cd backend/services/game-engine
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
python main.py
```

**终端 3 - Go 网关**:
```bash
cd backend/gateway
# Windows:
.\gateway.exe
# Linux/macOS:
./gateway
```

**终端 4 - 前端**:
```bash
cd frontend
npm run dev
```

### 访问应用

打开浏览器访问: **http://localhost:5173**

### 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 5173 | React 开发服务器 |
| API 网关 | 8000 | Go API 网关 |
| 游戏引擎 | 8001 | Python 游戏服务 |
| AI 引擎 | 8002 | Python AI 服务 |

---

## 🤖 下载模型

首次运行需要下载 AI 模型。

### 使用自动下载脚本

```bash
python scripts/download-models.py
```

### 手动下载模型

#### LLM 模型（必需）

推荐模型：
- **Llama-3-8B-Instruct Q4_K_M** (约 5GB)
- **Qwen2-7B-Instruct Q4_K_M** (约 4GB)

下载地址：
- [Hugging Face](https://huggingface.co/models)
- [ModelScope](https://modelscope.cn/models)

下载后放入：
```
models/llm/<model-name>.gguf
```

#### Embedding 模型（自动下载）

首次运行时，AI 引擎会自动下载 `all-MiniLM-L6-v2` 模型（约 90MB）。

如需手动指定其他模型，编辑 `.env` 文件：
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

#### Lite 模式（低配置）

如果您的硬件配置较低，可以使用 Lite 模式：

```bash
# 复制 Lite 配置
cp .env.lite .env

# 启动服务
python scripts/dev.py
```

Lite 模式特点：
- 小型 embedding 模型
- 禁用 reranker
- 推荐小型 LLM（7B 参数）
- 内存需求：4-8GB

---

## 🔍 诊断工具

如果遇到问题，可以运行诊断工具：

```bash
# Python 方式
python scripts/doctor.py

# 或使用 Makefile
make doctor
```

诊断工具会检查：
- 基础环境（Node.js, Python, Go）
- 依赖状态
- 模型文件
- 端口占用
- 目录权限
- 配置一致性
- 服务健康状态

---

## ❓ 常见问题

### 1. 端口被占用

**问题**: 启动时提示端口被占用

**解决方案**:

Windows:
```cmd
# 查找占用进程
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <PID> /F
```

Linux/macOS:
```bash
# 查找占用进程
lsof -i :8000

# 结束进程
kill -9 <PID>
```

### 2. Python 依赖安装失败

**问题**: pip install 失败

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果某个包安装失败，可以单独安装
pip install <package-name> -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Go 模块下载慢

**问题**: go mod download 很慢

**解决方案**:
```bash
# 设置国内代理
go env -w GOPROXY=https://goproxy.cn,direct

# 重新下载
go mod download
```

### 4. Go 编译失败

**问题**: go build 失败

**解决方案**:
```bash
# 检查 Go 版本
go version  # 需要 1.22+

# 清理缓存
go clean -modcache

# 重新下载依赖
go mod download
go mod tidy

# 重新编译
go build -o gateway.exe cmd/main.go
```

### 5. npm install 慢或失败

**问题**: npm 安装依赖慢或失败

**解决方案**:
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 清理缓存
npm cache clean --force

# 重新安装
npm install
```

### 6. AI 对话不工作

**问题**: 游戏中无法与 NPC 对话

**解决方案**:
1. 检查 AI 引擎是否正常启动（终端输出是否有错误）
2. 检查模型文件是否存在
3. 查看浏览器控制台是否有错误
4. 运行诊断工具：`python scripts/doctor.py`

### 7. 数据库错误

**问题**: 启动时提示数据库错误

**解决方案**:
```bash
# 检查数据库目录是否存在
ls -la database/sqlite/

# 如果不存在，创建目录
mkdir -p database/sqlite

# 检查权限
chmod 755 database/sqlite/
```

### 8. 内存不足

**问题**: 运行时内存不足

**解决方案**:
1. 使用 Lite 模式：`cp .env.lite .env`
2. 使用更小的 LLM 模型（如 7B 而非 13B）
3. 减少量化参数（如 Q4_K_M 改为 Q2_K）
4. 关闭其他应用程序

---

## 🎯 下一步

安装完成后，您可以：

1. **开始游戏**: 访问 http://localhost:5173
2. **添加游戏资源**: 添加精灵图、地图瓦片等
3. **自定义内容**: 修改游戏数据、AI 提示词等
4. **查看文档**: 
   - [架构设计](./architecture.md)
   - [API 文档](./api-spec.md)
   - [部署指南](./deployment.md)

---

## 📚 相关文档

- [快速启动指南](../QUICKSTART.md)
- [架构设计](./architecture.md)
- [Docker 部署](./docker-deployment.md)
- [Lite 模式说明](./lite-mode.md)
- [API 文档](./api-spec.md)

---

## 💡 提示

- **开发模式**: 前端支持热更新，后端修改需要重启服务
- **调试**: 查看浏览器控制台和终端输出进行调试
- **生产部署**: 建议使用 Docker，详见 [Docker 部署文档](./docker-deployment.md)

---

**祝您使用愉快！🎮✨**
