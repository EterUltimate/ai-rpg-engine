# Docker 部署指南

本指南介绍如何使用 Docker 部署 AI-RPG Engine。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 8GB 可用内存（推荐 16GB）
- 至少 20GB 可用磁盘空间（用于模型和数据）
- （可选）NVIDIA GPU + nvidia-docker（用于 GPU 加速）

## 🚀 快速开始

### 1. 准备模型文件

Docker 镜像不包含模型文件，需要预先下载：

```bash
# 下载模型（需要较长时间）
python scripts/download-models.py

# 或手动下载：
# - LLM模型: GGUF 格式，放入 models/llm/ 目录
# - 嵌入模型: 自动下载（首次运行时）
# - 重排序模型: 自动下载（首次运行时）
```

### 2. 选择部署模式

#### 开发模式（推荐用于开发）

支持热重载、调试日志、源代码挂载：

```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

**开发模式特点：**
- ✓ 源代码热重载
- ✓ 详细的调试日志
- ✓ 本地数据库存储
- ✓ 支持实时开发

#### 演示模式（推荐用于展示）

优化性能、启用 Lite 模式、生产配置：

```bash
# 启动所有服务
docker-compose -f docker-compose.demo.yml up -d

# 查看日志
docker-compose -f docker-compose.demo.yml logs -f

# 停止服务
docker-compose -f docker-compose.demo.yml down
```

**演示模式特点：**
- ✓ 生产级优化
- ✓ Lite 模式（降低资源需求）
- ✓ 自动重启
- ✓ 健康检查

## 📁 数据和模型挂载

### 数据库挂载

数据库文件默认存储在 Docker volume 中。要使用本地目录：

```yaml
# 修改 docker-compose.yml
services:
  game-engine:
    volumes:
      - ./database:/app/database  # 使用本地目录
```

### 模型挂载

模型文件需要挂载到容器中：

```yaml
services:
  ai-engine:
    volumes:
      - ./models:/app/models:ro  # 只读挂载
```

### 数据库持久化

默认配置会创建持久化 volume：

```bash
# 查看 volumes
docker volume ls | grep ai-rpg

# 备份数据库
docker run --rm -v ai-rpg-database-demo:/data -v $(pwd):/backup \
  alpine tar czf /backup/database-backup.tar.gz /data

# 恢复数据库
docker run --rm -v ai-rpg-database-demo:/data -v $(pwd):/backup \
  alpine tar xzf /backup/database-backup.tar.gz -C /
```

## 🔧 配置选项

### 环境变量

在 `docker-compose.yml` 或 `.env` 文件中配置：

```bash
# .env 文件
DATABASE_URL=sqlite+aiosqlite:///app/database/sqlite/game.db
LLM_MODEL_PATH=/app/models/llm/model.gguf
CHROMADB_PATH=/app/database/chromadb
EMBEDDING_MODEL=all-MiniLM-L6-v2
LOG_LEVEL=INFO

# Lite模式
LITE_MODE=true
DISABLE_RERANKER=true
```

### Lite 模式

演示环境默认启用 Lite 模式，大幅降低资源需求：

- ❌ 禁用重排序器（节省 1-2GB 内存）
- ✓ 使用小型嵌入模型（all-MiniLM-L6-v2）
- ✓ 优化的批处理大小
- ✓ 降低模型精度

启用 Lite 模式：

```yaml
environment:
  - LITE_MODE=true
  - DISABLE_RERANKER=true
```

## 🔍 服务健康检查

所有服务都配置了健康检查：

```bash
# 检查服务状态
docker-compose ps

# 手动健康检查
curl http://localhost:8000/health  # API网关
curl http://localhost:8001/health  # 游戏引擎
curl http://localhost:8002/health  # AI引擎
curl http://localhost:80           # 前端（演示模式）
```

## 📊 监控和日志

### 查看日志

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f ai-engine

# 最近100行日志
docker-compose logs --tail=100 ai-engine
```

### 资源监控

```bash
# 实时资源使用
docker stats

# 查看容器详情
docker inspect ai-rpg-ai-engine-demo
```

## 🛠️ 常见问题

### 端口冲突

如果端口被占用，修改 `docker-compose.yml`：

```yaml
services:
  frontend:
    ports:
      - "3000:80"  # 改为其他端口
```

### 内存不足

启用 Lite 模式或增加 Docker 内存限制：

```yaml
services:
  ai-engine:
    deploy:
      resources:
        limits:
          memory: 4G
```

### GPU 加速

安装 nvidia-docker 并添加 GPU 配置：

```yaml
services:
  ai-engine:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 模型加载失败

检查模型文件是否存在：

```bash
ls -lh models/llm/
# 应该看到 GGUF 文件
```

## 🔄 更新和重建

```bash
# 拉取最新代码
git pull

# 重建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

## 🧹 清理

```bash
# 停止并删除容器
docker-compose down

# 删除 volumes（会删除数据库）
docker-compose down -v

# 删除镜像
docker rmi ai-rpg-frontend:demo ai-rpg-gateway:demo \
            ai-rpg-game-engine:demo ai-rpg-ai-engine:demo
```

## 📚 相关文档

- [开发环境搭建](./development.md)
- [API 文档](./api-spec.md)
- [架构设计](./architecture.md)
