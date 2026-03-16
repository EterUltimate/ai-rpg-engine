# 部署指南

## 本地开发部署

### 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最低8GB,推荐16GB+
- **磁盘**: 最低20GB可用空间
- **CPU**: 4核心以上

### 软件依赖

- **Node.js** 18.0 或更高版本
- **Python** 3.10 或更高版本
- **Go** 1.22 或更高版本

### 安装步骤

#### Windows

1. 运行环境搭建脚本:
```bash
scripts\setup.bat
```

2. 下载AI模型:
```bash
scripts\download-models.bat
```

3. 启动服务:
```bash
# 启动前端
cd frontend
npm run dev

# 启动游戏引擎 (新终端)
cd backend\services\game-engine
venv\Scripts\activate
python main.py

# 启动AI引擎 (新终端)
cd backend\services\ai-engine
venv\Scripts\activate
python main.py

# 启动Go网关 (新终端)
cd backend\gateway
go run cmd\main.go
```

#### Linux/macOS

1. 添加执行权限:
```bash
chmod +x scripts/*.sh
```

2. 运行环境搭建脚本:
```bash
./scripts/setup.sh
```

3. 下载AI模型:
```bash
./scripts/download-models.sh
```

4. 启动所有服务:
```bash
./scripts/dev.sh
```

或手动启动各服务:
```bash
# 前端
cd frontend && npm run dev

# 游戏引擎
cd backend/services/game-engine
source venv/bin/activate
python main.py

# AI引擎
cd backend/services/ai-engine
source venv/bin/activate
python main.py

# Go网关
cd backend/gateway
go run cmd/main.go
```

### 访问应用

打开浏览器访问: http://localhost:5173

---

## Docker部署

### 使用Docker Compose

1. 构建并启动所有服务:
```bash
docker-compose up --build
```

2. 后台运行:
```bash
docker-compose up -d
```

3. 停止服务:
```bash
docker-compose down
```

### 单独构建镜像

```bash
# 前端
docker build -t ai-rpg-frontend frontend/

# Go网关
docker build -t ai-rpg-gateway backend/gateway/

# 游戏引擎
docker build -t ai-rpg-game-engine backend/services/game-engine/

# AI引擎
docker build -t ai-rpg-ai-engine backend/services/ai-engine/
```

---

## 生产环境部署

### Web版本部署 (Nginx)

1. 构建前端:
```bash
cd frontend
npm run build
```

2. 配置Nginx:
```nginx
server {
    listen 80;
    server_name game.example.com;
    
    # 前端静态文件
    location / {
        root /var/www/ai-rpg/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket代理
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. 启动后端服务:
```bash
# 使用systemd管理服务
sudo systemctl start ai-rpg-game-engine
sudo systemctl start ai-rpg-ai-engine
sudo systemctl start ai-rpg-gateway
```

### 桌面版本打包 (Electron)

1. 安装Electron:
```bash
cd frontend
npm install --save-dev electron electron-builder
```

2. 添加Electron主进程:
```javascript
// electron/main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  
  win.loadFile(path.join(__dirname, '../dist/index.html'));
}

app.whenReady().then(createWindow);
```

3. 打包:
```bash
npm run build
npx electron-builder
```

### 移动版本打包 (Capacitor)

1. 安装Capacitor:
```bash
npm install @capacitor/core @capacitor/cli
npx cap init
```

2. 添加平台:
```bash
npx cap add android
npx cap add ios
```

3. 构建并同步:
```bash
npm run build
npx cap sync
```

4. 打开IDE:
```bash
npx cap open android  # Android Studio
npx cap open ios      # Xcode
```

---

## 性能优化建议

### 前端优化

1. **代码分割**: Vite已自动配置
2. **资源压缩**: 图片使用WebP格式
3. **CDN加速**: 静态资源使用CDN
4. **缓存策略**: 配置浏览器缓存

### 后端优化

1. **启用Gzip压缩**
2. **数据库索引优化**
3. **连接池配置**
4. **启用HTTP/2**

### AI服务优化

1. **模型量化**: 使用Q4_K_M量化
2. **批处理**: 合并多个请求
3. **缓存**: 常见查询缓存结果
4. **GPU加速**: 如有GPU,启用CUDA

---

## 监控和日志

### 日志管理

- 前端日志: 浏览器控制台
- 后端日志: 各服务stdout/stderr
- 建议使用ELK Stack或Loki进行日志收集

### 性能监控

- 使用Prometheus + Grafana监控系统指标
- 使用Jaeger进行分布式追踪

---

## 安全建议

1. **启用HTTPS**: 生产环境必须使用TLS
2. **API认证**: 实现JWT Token认证
3. **输入验证**: 严格验证所有用户输入
4. **SQL注入防护**: 使用ORM参数化查询
5. **XSS防护**: 前端内容转义
6. **CORS配置**: 限制允许的源

---

## 故障排查

### 常见问题

1. **端口占用**: 检查端口8000, 8001, 8002, 5173是否被占用
2. **模型加载失败**: 检查模型路径是否正确
3. **数据库错误**: 检查数据库文件权限
4. **依赖安装失败**: 尝试删除node_modules/venv重新安装

### 获取帮助

- 查看日志输出
- 检查配置文件
- 提交Issue到GitHub仓库
