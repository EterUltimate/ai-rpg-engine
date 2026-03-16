#!/bin/bash

# 开发启动脚本 - 同时启动所有服务

set -e

echo "🚀 启动 AI-RPG Engine 开发环境"
echo "=================================="

# 函数: 启动服务并在后台运行
start_service() {
    local name=$1
    local command=$2
    local color=$3
    
    echo "启动 $name..."
    gnome-terminal --tab --title="$name" -- bash -c "$command; exec bash" 2>/dev/null || \
    xterm -T "$name" -e "$command" 2>/dev/null || \
    konsole --new-tab -e bash -c "$command; exec bash" 2>/dev/null || \
    {
        echo "无法在新终端启动 $name, 在当前终端运行..."
        eval "$command &"
    }
}

# 检查是否安装了必要的工具
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装"
    exit 1
fi

if ! command -v go &> /dev/null; then
    echo "❌ Go 未安装"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 启动服务
echo ""
start_service "游戏引擎服务" \
    "cd backend/services/game-engine && source venv/bin/activate && python main.py" \
    "蓝色"

start_service "AI引擎服务" \
    "cd backend/services/ai-engine && source venv/bin/activate && python main.py" \
    "绿色"

start_service "Go API网关" \
    "cd backend/gateway && go run cmd/main.go" \
    "黄色"

sleep 2

start_service "前端开发服务器" \
    "cd frontend && npm run dev" \
    "紫色"

echo ""
echo "✅ 所有服务已启动!"
echo ""
echo "📍 访问地址:"
echo "   - 前端: http://localhost:5173"
echo "   - API网关: http://localhost:8000"
echo "   - 游戏引擎: http://localhost:8001"
echo "   - AI引擎: http://localhost:8002"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
wait
