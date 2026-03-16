# 🎮 AI-RPG Engine 快速启动指南

欢迎使用 AI-RPG Engine!本指南将帮助您快速启动项目。

---

## ⚡ 5分钟快速开始

### 第1步: 环境准备 (2分钟)

确保已安装以下软件:
- ✅ **Node.js 18+**: [下载地址](https://nodejs.org/)
- ✅ **Python 3.10+**: [下载地址](https://www.python.org/)
- ✅ **Go 1.22+**: [下载地址](https://golang.org/)

### 第2步: 运行安装脚本 (2分钟)

**Windows用户**:
```cmd
cd ai-rpg-engine
scripts\setup.bat
```

**Linux/macOS用户**:
```bash
cd ai-rpg-engine
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 第3步: 启动服务 (1分钟)

打开**4个终端窗口**,分别运行:

**终端1 - 前端**:
```bash
cd frontend
npm run dev
```

**终端2 - 游戏引擎**:
```bash
cd backend/services/game-engine
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
python main.py
```

**终端3 - AI引擎**:
```bash
cd backend/services/ai-engine
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
python main.py
```

**终端4 - Go网关**:
```bash
cd backend/gateway
go run cmd/main.go
```

### 第4步: 开始游戏

打开浏览器访问: **http://localhost:5173**

🎉 恭喜!您已成功启动AI-RPG Engine!

---

## 📋 详细说明

### 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 5173 | React开发服务器 |
| API网关 | 8000 | Go API网关 |
| 游戏引擎 | 8001 | Python游戏服务 |
| AI引擎 | 8002 | Python AI服务 |

### 首次运行

首次运行时,AI引擎会自动下载嵌入模型(sentence-transformers),大约100-500MB。

### 游戏操作

- **方向键**: 移动角色
- **空格键**: 打开AI对话界面
- **接近NPC**: 自动触发对话

---

## 🔧 常见问题

### Q1: 端口被占用怎么办?

**Windows**:
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/macOS**:
```bash
lsof -i :8000
kill -9 <PID>
```

### Q2: Python依赖安装失败?

尝试升级pip:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Q3: Go依赖下载慢?

设置国内代理:
```bash
go env -w GOPROXY=https://goproxy.cn,direct
go mod download
```

### Q4: AI对话不工作?

检查以下内容:
1. AI引擎服务是否正常启动
2. 查看终端错误日志
3. 确认模型配置正确

---

## 🚀 下一步

### 添加游戏资源

当前项目使用占位符,您需要添加实际游戏资源:

1. **精灵图**: 放入 `frontend/public/assets/sprites/`
2. **地图瓦片**: 放入 `frontend/public/assets/tiles/`
3. **地图数据**: 放入 `frontend/public/assets/maps/`

推荐资源网站:
- [OpenGameArt](https://opengameart.org/)
- [itch.io](https://itch.io/game-assets/free)
- [Kenney Assets](https://kenney.nl/assets)

### 下载AI模型

运行模型下载脚本:
```bash
./scripts/download-models.sh
```

选择合适的LLM模型(推荐Llama-3-8B-Instruct Q4_K_M)

### 自定义游戏内容

修改以下文件定制游戏:
- `backend/services/game-engine/app/models/models.py` - 数据模型
- `frontend/src/game/scenes/MainScene.tsx` - 游戏场景
- `backend/services/ai-engine/main.py` - AI系统提示词

---

## 📚 更多文档

- [完整架构文档](./docs/architecture.md)
- [API接口文档](./docs/api-spec.md)
- [部署指南](./docs/deployment.md)
- [贡献指南](./CONTRIBUTING.md)

---

## 💡 提示

### 开发模式

- 前端支持热更新,修改代码自动刷新
- 后端修改需要重启服务
- 查看浏览器控制台调试前端
- 查看终端输出调试后端

### 生产部署

建议使用Docker:
```bash
docker-compose up --build
```

详见 [部署指南](./docs/deployment.md)

---

## 🆘 获取帮助

遇到问题?

1. 查看 [FAQ](./docs/FAQ.md)
2. 提交 [GitHub Issue](https://github.com/your-repo/issues)
3. 查看 [文档](./docs/)

---

**祝您游戏开发愉快! 🎮✨**
