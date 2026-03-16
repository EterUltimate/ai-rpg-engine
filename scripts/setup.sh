#!/bin/bash

# AI-RPG Engine 环境搭建脚本
# 适用于 Linux/macOS

set -e

echo "🎮 AI-RPG Engine 开发环境搭建"
echo "================================"

# 检查必要的工具
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 未安装"
        return 1
    else
        echo "✅ $1 已安装: $(command -v $1)"
        return 0
    fi
}

# 检查依赖
echo ""
echo "📋 检查依赖..."
check_command "node" || echo "请安装 Node.js 18+: https://nodejs.org/"
check_command "python" || echo "请安装 Python 3.10+: https://www.python.org/"
check_command "go" || echo "请安装 Go 1.22+: https://golang.org/"

# 创建必要的目录
echo ""
echo "📁 创建目录结构..."
mkdir -p database/sqlite
mkdir -p database/chromadb
mkdir -p models/llm
mkdir -p models/embeddings
mkdir -p models/rerankers
mkdir -p frontend/public/assets/sprites
mkdir -p frontend/public/assets/maps
mkdir -p frontend/public/assets/tiles

# 前端设置
echo ""
echo "🎨 设置前端环境..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
else
    echo "前端依赖已安装"
fi
cd ..

# Python后端设置
echo ""
echo "🐍 设置Python环境..."

# 游戏引擎服务
cd backend/services/game-engine
if [ ! -d "venv" ]; then
    echo "创建游戏引擎虚拟环境..."
    python -m venv venv
fi

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "安装游戏引擎依赖..."
pip install -r requirements.txt
deactivate
cd ../../..

# AI引擎服务
cd backend/services/ai-engine
if [ ! -d "venv" ]; then
    echo "创建AI引擎虚拟环境..."
    python -m venv venv
fi

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "安装AI引擎依赖..."
pip install -r requirements.txt
deactivate
cd ../../..

# Go网关设置
echo ""
echo "🐹 设置Go网关..."
cd backend/gateway
if [ ! -f "go.sum" ]; then
    echo "下载Go依赖..."
    go mod download
else
    echo "Go依赖已下载"
fi
cd ../..

echo ""
echo "✅ 环境搭建完成!"
echo ""
echo "📝 下一步:"
echo "1. 下载AI模型(运行 ./scripts/download-models.sh)"
echo "2. 启动服务:"
echo "   - 前端: cd frontend && npm run dev"
echo "   - 游戏引擎: cd backend/services/game-engine && source venv/bin/activate && python main.py"
echo "   - AI引擎: cd backend/services/ai-engine && source venv/bin/activate && python main.py"
echo "   - Go网关: cd backend/gateway && go run cmd/main.go"
echo "3. 访问 http://localhost:5173 开始游戏"
