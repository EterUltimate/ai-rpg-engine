# Lite 模式指南

Lite 模式是为低配置环境优化的运行模式，让 AI-RPG Engine 可以在资源有限的环境中运行。

## 📊 资源需求对比

| 配置项 | 标准模式 | Lite 模式 | 节省 |
|--------|---------|----------|------|
| **内存需求** | 12-16 GB | 4-6 GB | ~60% |
| **LLM 模型** | 7-13B (4-8GB) | 1.8-2.7B (1-2GB) | ~75% |
| **嵌入模型** | bge-large (1.3GB) | MiniLM (80MB) | ~94% |
| **重排序器** | bge-reranker (1.3GB) | 禁用 | 100% |
| **磁盘空间** | 10GB+ | 3GB+ | ~70% |
| **GPU显存** | 8GB+ | 2GB+ 或 CPU | ~75% |

## 🚀 快速启用

### 方式 1: 使用 .env.lite 配置文件

```bash
# 复制 Lite 配置
cp .env.lite .env

# 启动服务
python scripts/dev.py
```

### 方式 2: 环境变量

```bash
# Linux/macOS
export LITE_MODE=true
export DISABLE_RERANKER=true
python scripts/dev.py

# Windows PowerShell
$env:LITE_MODE="true"
$env:DISABLE_RERANKER="true"
python scripts/dev.py
```

### 方式 3: Docker

```bash
# 使用演示配置（已启用 Lite 模式）
docker-compose -f docker-compose.demo.yml up -d
```

## ⚙️ Lite 模式优化项

### 1. LLM 模型优化

推荐使用小型但性能优秀的模型：

| 模型 | 大小 | 性能 | 推荐场景 |
|------|------|------|----------|
| **Qwen-1.8B-Chat** | ~1GB | ★★★☆☆ | 中文对话 |
| **Phi-2** | ~1.6GB | ★★★★☆ | 英文通用 |
| **TinyLlama-1.1B** | ~0.6GB | ★★☆☆☆ | 极限配置 |
| **Qwen-2.7B-Chat** | ~1.8GB | ★★★★☆ | 平衡性能 |

下载模型：

```bash
# Qwen-1.8B (推荐中文)
wget -O models/llm/qwen-1.8b-chat-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen-1_8B-Chat-GGUF/resolve/main/qwen1_8b-chat-q4_k_m.gguf

# Phi-2 (推荐英文)
wget -O models/llm/phi-2-q4_k_m.gguf \
  https://huggingface.co/microsoft/phi-2/resolve/main/phi-2-q4_k_m.gguf
```

### 2. 嵌入模型优化

使用小型但高效的嵌入模型：

- **all-MiniLM-L6-v2**: 80MB，384维，速度快
- **all-MiniLM-L12-v2**: 120MB，384维，稍慢但更准确
- **paraphrase-multilingual-MiniLM-L12-v2**: 120MB，支持多语言

Lite 模式默认使用 `all-MiniLM-L6-v2`。

### 3. 重排序器禁用

重排序器在标准模式下提供更好的检索质量，但占用较多资源。

Lite 模式默认禁用重排序器：

```bash
DISABLE_RERANKER=true
```

如果需要启用，使用轻量级模型：

```bash
DISABLE_RERANKER=false
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

### 4. RAG 参数优化

```bash
# 减少检索数量
RAG_TOP_K=3          # 默认 5-10

# 更小的文本块
CHUNK_SIZE=256       # 默认 512
CHUNK_OVERLAP=50     # 默认 100

# 禁用重排序结果
RAG_RERANK_TOP_K=0   # 默认 3-5
```

### 5. 推理参数优化

```bash
# 减少 token 生成数量
LLM_MAX_TOKENS=512   # 默认 1024-2048

# 减少上下文窗口
LLM_N_CTX=2048       # 默认 4096

# 禁用 GPU 加速（使用 CPU）
LLM_N_GPU_LAYERS=0   # 默认 32-35
```

## 📈 性能调优

### CPU 优化

如果使用 CPU 推理：

```bash
# 设置线程数（建议物理核心数）
LLM_N_THREADS=4

# 启用批处理
BATCH_INFERENCE=true
MAX_BATCH_SIZE=8
```

### 内存优化

```bash
# 启用内存优化模式
ENABLE_MEMORY_OPTIMIZATION=true

# 限制最大内存使用
MAX_MEMORY_USAGE_GB=4

# 启用模型缓存
ENABLE_MODEL_CACHE=true
```

### 磁盘优化

```bash
# 使用内存盘存储临时文件（Linux）
export TMPDIR=/dev/shm

# 启用向量数据库压缩
CHROMADB_COMPRESSION=true
```

## 🔄 混合模式

如果部分资源充足，可以混合使用：

### 有 GPU 但内存不足

```bash
# 启用 GPU 加速 LLM
LLM_N_GPU_LAYERS=20

# 但禁用重排序器节省内存
DISABLE_RERANKER=true

# 使用小型嵌入模型
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 有内存但无 GPU

```bash
# 使用稍大的 LLM 模型
LLM_MODEL_PATH=./models/llm/qwen-7b-chat-q4_k_m.gguf

# CPU 推理
LLM_N_GPU_LAYERS=0
LLM_N_THREADS=8

# 启用重排序器
DISABLE_RERANKER=false
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

## 🌐 外部 API 替代

如果本地资源实在不足，可以使用外部 API：

```bash
# 使用 OpenAI API
USE_OPENAI_API=true
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-3.5-turbo

# 或使用其他兼容 API
USE_OLLAMA_API=true
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## ⚠️ Lite 模式限制

相比标准模式，Lite 模式有以下限制：

1. **检索质量**: 更少的检索结果和较小的嵌入模型可能影响检索准确性
2. **生成质量**: 小型 LLM 模型的生成质量和理解能力较弱
3. **上下文长度**: 更短的上下文窗口限制了对话历史长度
4. **功能限制**: 重排序器禁用可能影响复杂查询的效果

## 💡 最佳实践

### 开发测试

```bash
# Lite 模式适合开发测试
python scripts/dev.py --lite
```

### 生产部署

如果资源充足，建议：

```bash
# 前端和网关使用标准配置
# AI 引擎使用 Lite 模式
# 这样可以平衡性能和资源使用
```

### 性能监控

```bash
# 监控资源使用
python scripts/doctor.py

# 查看实时日志
tail -f logs/ai-engine.log
```

## 📚 相关文档

- [Docker 部署指南](./docker-deployment.md)
- [开发环境搭建](./development.md)
- [性能优化指南](./performance-tuning.md)
