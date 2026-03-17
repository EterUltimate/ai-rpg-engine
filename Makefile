# AI-RPG Engine Makefile
# 统一命令入口，支持跨平台使用

.PHONY: help setup dev doctor build clean test docker-dev docker-demo download-models

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
help:
	@echo "AI-RPG Engine 命令参考"
	@echo ""
	@echo "环境设置:"
	@echo "  make setup           # 安装所有依赖"
	@echo "  make download-models # 下载AI模型"
	@echo "  make doctor          # 运行系统诊断"
	@echo ""
	@echo "开发:"
	@echo "  make dev             # 启动开发环境"
	@echo "  make test            # 运行测试"
	@echo "  make build           # 构建生产版本"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-dev      # 启动开发容器"
	@echo "  make docker-demo     # 启动演示容器"
	@echo "  make docker-stop     # 停止所有容器"
	@echo ""
	@echo "清理:"
	@echo "  make clean           # 清理构建文件"
	@echo "  make clean-all       # 清理所有生成文件"
	@echo ""

# 环境设置
setup:
	@echo "📦 安装依赖..."
	python scripts/setup.py

download-models:
	@echo "📥 下载模型..."
	python scripts/download-models.py

download-models-lite:
	@echo "📥 下载 Lite 模式模型..."
	python scripts/download-models.py --lite

download-models-llm:
	@echo "📥 下载模型（包含 LLM）..."
	python scripts/download-models.py --llm

doctor:
	@echo "🔍 运行系统诊断..."
	python scripts/doctor.py

doctor-verbose:
	@echo "🔍 运行详细诊断..."
	python scripts/doctor.py --verbose

# 开发
dev:
	@echo "🚀 启动开发环境..."
	python scripts/dev.py

dev-skip-checks:
	@echo "🚀 启动开发环境（跳过检查）..."
	python scripts/dev.py --skip-checks

test:
	@echo "🧪 运行测试..."
	python -m pytest tests/

test-integration:
	@echo "🧪 运行集成测试..."
	python tests/integration_test.py

# 构建
build:
	@echo "🏗️  构建生产版本..."
	cd frontend && npm run build
	cd backend/gateway && go build -o gateway cmd/main.go

build-frontend:
	@echo "🏗️  构建前端..."
	cd frontend && npm run build

build-backend:
	@echo "🏗️  构建后端..."
	cd backend/gateway && go build -o gateway cmd/main.go

# Docker
docker-dev:
	@echo "🐳 启动开发容器..."
	docker-compose -f docker-compose.dev.yml up -d

docker-demo:
	@echo "🐳 启动演示容器..."
	docker-compose -f docker-compose.demo.yml up -d

docker-stop:
	@echo "🛑 停止所有容器..."
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.demo.yml down

docker-logs:
	@echo "📄 查看容器日志..."
	docker-compose logs -f

docker-clean:
	@echo "🧹 清理 Docker 资源..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.demo.yml down -v

# 清理
clean:
	@echo "🧹 清理构建文件..."
	rm -rf frontend/dist
	rm -rf backend/gateway/gateway
	rm -rf backend/services/*/venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all:
	@echo "🧹 清理所有生成文件..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	rm -rf backend/gateway/gateway
	rm -rf backend/services/*/venv
	rm -rf logs
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 快捷命令
status:
	@echo "📊 检查服务状态..."
	@curl -s http://localhost:8000/health || echo "API网关: 未运行"
	@curl -s http://localhost:8001/health || echo "游戏引擎: 未运行"
	@curl -s http://localhost:8002/health || echo "AI引擎: 未运行"
	@curl -s http://localhost:5173 > /dev/null && echo "前端: 运行中" || echo "前端: 未运行"

open:
	@echo "🌐 打开浏览器..."
	@if command -v xdg-open >/dev/null; then \
		xdg-open http://localhost:5173; \
	elif command -v open >/dev/null; then \
		open http://localhost:5173; \
	else \
		echo "请手动打开: http://localhost:5173"; \
	fi
