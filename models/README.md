# AI 模型配置指南

本文档说明如何下载和配置AI-RPG Engine所需的模型。

---

## 📥 模型下载

### 1. 嵌入模型 (自动下载)

运行 `scripts\download-models.bat` 将自动下载:

```bash
# 嵌入模型 (~90MB)
all-MiniLM-L6-v2
```

**用途**: 将文本转换为向量,用于RAG检索

**位置**: `models/embeddings/all-MiniLM-L6-v2/`

---

### 2. 重排序模型 (自动下载)

运行 `scripts\download-models.bat` 将自动下载:

```bash
# 重排序模型 (~80MB)
cross-encoder/ms-marco-MiniLM-L-6-v2
```

**用途**: 对检索结果进行智能重排序,提高准确率

**位置**: `models/rerankers/ms-marco-MiniLM-L-6-v2/`

---

### 3. LLM模型 (手动下载)

LLM模型较大,需要手动下载。根据您的硬件配置选择:

#### 推荐模型

| 模型 | 大小 | 内存需求 | 质量 | 下载链接 |
|------|------|----------|------|----------|
| **Qwen2.5-7B-Instruct** | ~14GB | 16GB+ | ⭐⭐⭐⭐⭐ | [HuggingFace](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) |
| **Mistral-7B-Instruct-v0.3** | ~14GB | 16GB+ | ⭐⭐⭐⭐⭐ | [HuggingFace](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) |
| **Llama-3.1-8B-Instruct** | ~16GB | 20GB+ | ⭐⭐⭐⭐⭐ | [HuggingFace](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) |
| **Qwen2.5-3B-Instruct** | ~6GB | 8GB+ | ⭐⭐⭐⭐ | [HuggingFace](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) |
| **Phi-3-mini-4k-instruct** | ~2.3GB | 4GB+ | ⭐⭐⭐⭐ | [HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) |

#### 下载方法

**方法1: 使用HuggingFace CLI**
```bash
# 安装工具
pip install huggingface-hub

# 下载模型 (示例: Qwen2.5-7B)
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir models/llm/Qwen2.5-7B-Instruct
```

**方法2: 使用Python**
```python
from huggingface_hub import snapshot_download

# 下载模型
snapshot_download(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    local_dir="models/llm/Qwen2.5-7B-Instruct"
)
```

**方法3: Git LFS**
```bash
# 安装Git LFS
git lfs install

# 克隆模型仓库
cd models/llm
git clone https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
```

#### 模型格式转换 (可选)

如果使用llama.cpp推理,需要转换为GGUF格式:

```bash
# 安装llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# 转换模型
python convert-hf-to-gguf.py ../models/llm/Qwen2.5-7B-Instruct --outfile qwen-7b.gguf --outtype q4_k_m
```

---

## ⚙️ 配置模型路径

编辑 `.env` 文件:

```env
# LLM模型配置
LLM_MODEL_PATH=models/llm/Qwen2.5-7B-Instruct
LLM_MODEL_TYPE=transformers  # 或 llama.cpp

# 嵌入模型配置
EMBEDDING_MODEL_PATH=models/embeddings/all-MiniLM-L6-v2

# 重排序模型配置
RERANKER_MODEL_PATH=models/rerankers/ms-marco-MiniLM-L-6-v2
```

---

## 🖥️ 硬件要求

### 最小配置
- CPU: 4核心
- RAM: 8GB
- 存储: 20GB
- 适合: Phi-3-mini (2.3GB)

### 推荐配置
- CPU: 8核心
- RAM: 16GB
- 存储: 50GB SSD
- 适合: Qwen2.5-7B / Mistral-7B

### 理想配置
- CPU: 12核心+
- RAM: 32GB
- GPU: RTX 3060+ (12GB显存)
- 存储: 100GB SSD
- 适合: Llama-3.1-8B + GPU加速

---

## 🚀 性能优化

### 1. 量化模型

使用量化模型减少内存占用:

```python
# 4-bit量化 (推荐)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    load_in_4bit=True,
    device_map="auto"
)

# 8-bit量化
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    load_in_8bit=True,
    device_map="auto"
)
```

### 2. 使用GGUF格式

GGUF模型加载更快,内存占用更少:

```bash
# 下载预量化GGUF模型
wget https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf
```

### 3. GPU加速

如果有NVIDIA GPU:

```python
# 启用CUDA
device_map = {
    "": "cuda:0"  # 使用第一块GPU
}

# 或自动分配
device_map = "auto"
```

---

## 📊 模型性能对比

| 模型 | 参数量 | 速度 | 质量评分 | 适用场景 |
|------|--------|------|----------|----------|
| Phi-3-mini | 3.8B | ⚡⚡⚡⚡⚡ | 7.5/10 | 轻量部署,快速响应 |
| Qwen2.5-3B | 3B | ⚡⚡⚡⚡⚡ | 8.0/10 | 平衡性能与速度 |
| Qwen2.5-7B | 7B | ⚡⚡⚡ | 8.8/10 | 最佳性价比 |
| Mistral-7B | 7B | ⚡⚡⚡ | 8.5/10 | 高质量对话 |
| Llama-3.1-8B | 8B | ⚡⚡ | 9.0/10 | 最高质量 |

---

## 🔧 使用API配置模型

如果不想本地运行模型,可以使用API:

### OpenAI API
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4-turbo-preview
```

### Claude API
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 国内模型API

**通义千问**
```env
LLM_PROVIDER=qwen
DASHSCOPE_API_KEY=sk-your-api-key
```

**智谱AI**
```env
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=your-api-key
```

---

## ✅ 验证安装

运行测试验证模型是否正确安装:

```bash
cd backend/services/ai-engine
python -c "
from llama_engine import LlamaEngine
engine = LlamaEngine()
print(engine.generate('测试', max_tokens=10))
"
```

---

## 🆘 常见问题

### 1. 内存不足
**问题**: OOM (Out of Memory)

**解决**: 使用量化模型或更小的模型

### 2. 下载速度慢
**问题**: HuggingFace下载慢

**解决**: 使用镜像站
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 3. 模型加载失败
**问题**: 加载时报错

**解决**: 检查模型文件完整性
```bash
# 验证文件
ls -lh models/llm/Qwen2.5-7B-Instruct/
```

---

## 📚 更多资源

- [HuggingFace模型库](https://huggingface.co/models)
- [llama.cpp文档](https://github.com/ggerganov/llama.cpp)
- [模型量化指南](https://huggingface.co/docs/transformers/quantization)

---

**模型配置完成后,运行 `scripts\dev.bat` 启动游戏! 🎮**
