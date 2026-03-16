#!/bin/bash

# AI模型下载脚本
# 下载所需的LLM、嵌入和重排模型

set -e

echo "🤖 AI-RPG Engine 模型下载"
echo "============================"

# 模型保存路径
MODELS_DIR="./models"
mkdir -p $MODELS_DIR/llm
mkdir -p $MODELS_DIR/embeddings
mkdir -p $MODELS_DIR/rerankers

echo ""
echo "⚠️  注意: 模型文件较大,请确保有足够的磁盘空间"
echo "   - LLM模型: 约4-8GB"
echo "   - 嵌入模型: 约100-500MB"
echo "   - 重排模型: 约100-500MB"
echo ""

read -p "是否继续下载? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消下载"
    exit 1
fi

# 下载LLM模型 (使用llama.cpp的GGUF格式)
echo ""
echo "📥 下载LLM模型..."
echo "选择要下载的模型:"
echo "1. Llama-3-8B-Instruct (Q4_K_M量化, 约4.7GB) - 推荐"
echo "2. Mistral-7B-Instruct (Q4_K_M量化, 约4.1GB)"
echo "3. Qwen-7B-Chat (Q4_K_M量化, 约4.3GB)"
echo "4. 跳过LLM模型下载"
echo ""
read -p "请选择 (1-4): " llm_choice

case $llm_choice in
    1)
        echo "下载 Llama-3-8B-Instruct..."
        wget -O $MODELS_DIR/llm/llama-3-8b-instruct.q4_k_m.gguf \
            https://huggingface.co/MaziyarPanahi/Llama-3-8B-Instruct-GGUF/resolve/main/Llama-3-8B-Instruct.Q4_K_M.gguf
        ;;
    2)
        echo "下载 Mistral-7B-Instruct..."
        wget -O $MODELS_DIR/llm/mistral-7b-instruct.q4_k_m.gguf \
            https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
        ;;
    3)
        echo "下载 Qwen-7B-Chat..."
        wget -O $MODELS_DIR/llm/qwen-7b-chat.q4_k_m.gguf \
            https://huggingface.co/Qwen/Qwen-7B-Chat-GGUF/resolve/main/qwen-7b-chat.Q4_K_M.gguf
        ;;
    4)
        echo "跳过LLM模型下载"
        ;;
    *)
        echo "无效选择,跳过LLM模型下载"
        ;;
esac

# 嵌入模型 (首次运行时自动下载)
echo ""
echo "📥 嵌入模型信息..."
echo "嵌入模型 'all-MiniLM-L6-v2' 将在首次运行时自动下载到:"
echo "  - Linux/Mac: ~/.cache/huggingface/hub/"
echo "  - Windows: C:\Users\<用户名>\.cache\huggingface\hub/"
echo ""
echo "如需使用其他嵌入模型,请修改 backend/services/ai-engine/main.py"

# 重排模型 (首次运行时自动下载)
echo ""
echo "📥 重排模型信息..."
echo "重排模型将在首次运行时自动下载到相同位置"

# 创建模型配置文件
echo ""
echo "📝 创建模型配置..."
cat > .env.model <<EOF
# AI模型配置
# 请根据下载的模型修改路径

# LLM模型路径
LLM_MODEL_PATH=./models/llm/llama-3-8b-instruct.q4_k_m.gguf

# 嵌入模型 (HuggingFace模型名称)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB路径
CHROMADB_PATH=./database/chromadb

# 数据库路径
DATABASE_URL=sqlite+aiosqlite:///./database/sqlite/game.db
EOF

echo ""
echo "✅ 模型下载完成!"
echo ""
echo "📝 配置文件已创建: .env.model"
echo "   请根据实际下载的模型修改配置"
echo ""
echo "下一步: 运行 ./scripts/setup.sh 完成环境搭建"
