# 集成测试指南

## 快速测试

### Windows
```bash
cd ai-rpg-engine
tests\integration_test.bat
```

### Linux/macOS
```bash
cd ai-rpg-engine
chmod +x tests/integration_test.sh
./tests/integration_test.sh
```

## 手动测试步骤

### 1. 启动所有服务

#### 终端1 - 前端
```bash
cd frontend
npm run dev
```
访问: http://localhost:5173

#### 终端2 - 游戏引擎
```bash
cd backend/services/game-engine
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```
访问: http://localhost:8001/health

#### 终端3 - AI引擎
```bash
cd backend/services/ai-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
访问: http://localhost:8002/health

#### 终端4 - Go网关
```bash
cd backend/gateway
go mod download
go run cmd/main.go
```
访问: http://localhost:8000/health

### 2. 测试API端点

#### 使用curl测试
```bash
# 健康检查
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# 创建角色
curl -X POST http://localhost:8000/api/v1/character/create \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"测试角色\"}"

# 获取游戏状态
curl http://localhost:8000/api/v1/game/state/{character_id}

# AI对话
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"你好\",\"character_id\":\"test\",\"scene_id\":\"village_001\"}"
```

#### 使用Python测试脚本
```bash
cd tests
python integration_test.py
```

### 3. 前端测试

1. 打开浏览器访问 http://localhost:5173
2. 创建新角色
3. 测试移动、对话等功能
4. 测试AI对话界面
5. 检查控制台是否有错误

## 测试清单

### ✅ 服务启动测试
- [ ] 前端服务启动 (5173端口)
- [ ] Go网关启动 (8000端口)
- [ ] 游戏引擎启动 (8001端口)
- [ ] AI引擎启动 (8002端口)

### ✅ API功能测试
- [ ] 健康检查接口
- [ ] 角色创建接口
- [ ] 游戏状态查询
- [ ] 动作执行
- [ ] AI对话
- [ ] 游戏保存/加载

### ✅ 前端功能测试
- [ ] 角色创建界面
- [ ] 游戏主界面
- [ ] HUD显示
- [ ] AI对话界面
- [ ] 背包系统
- [ ] 任务系统

### ✅ 集成测试
- [ ] 完整游戏流程
- [ ] 多次对话记忆
- [ ] 任务接受和完成
- [ ] 场景切换
- [ ] 数据持久化

## 常见问题

### Q1: 服务启动失败
**解决**: 检查端口是否被占用
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Q2: 数据库错误
**解决**: 删除数据库文件重新初始化
```bash
rm database/sqlite/game.db
```

### Q3: 模型加载失败
**解决**: 检查模型路径配置
- 修改 `.env` 文件中的 `LLM_MODEL_PATH`
- 或先不加载模型,测试基础功能

### Q4: 前端无法连接后端
**解决**: 
1. 检查后端服务是否启动
2. 检查CORS配置
3. 检查API URL配置

## 性能基准

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| API响应时间 | < 100ms | curl计时 |
| 前端首屏 | < 3s | Chrome DevTools |
| AI生成速度 | > 20 tokens/s | 计时统计 |
| 内存占用 | < 500MB | 任务管理器 |

## 测试报告

测试完成后,会生成测试报告文件:
- `test_report.txt` - 文本格式报告
- 测试日志输出

---

**提示**: 首次测试建议按顺序执行,确保每步都成功再进行下一步。
