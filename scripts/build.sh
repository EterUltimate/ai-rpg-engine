#!/bin/bash

# 构建脚本 - 构建所有组件

set -e

echo "🔨 AI-RPG Engine 构建脚本"
echo "============================"

# 构建前端
echo ""
echo "📦 构建前端..."
cd frontend
npm run build
cd ..

# 构建Go网关
echo ""
echo "📦 构建Go网关..."
cd backend/gateway
go build -o gateway cmd/main.go
cd ../..

# 创建发布目录
echo ""
echo "📁 创建发布包..."
RELEASE_DIR="release/ai-rpg-engine-$(date +%Y%m%d-%H%M%S)"
mkdir -p $RELEASE_DIR

# 复制文件
cp -r frontend/dist $RELEASE_DIR/frontend
cp -r backend $RELEASE_DIR/
cp -r database $RELEASE_DIR/
cp -r models $RELEASE_DIR/
cp docker-compose.yml $RELEASE_DIR/
cp README.md $RELEASE_DIR/
cp .env.example $RELEASE_DIR/.env

echo ""
echo "✅ 构建完成!"
echo "发布包位置: $RELEASE_DIR"
