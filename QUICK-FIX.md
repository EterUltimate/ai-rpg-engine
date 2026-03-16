# 🚨 快速修复指南

## 问题: 构建脚本报错 "Could not read package.json"

### 原因
脚本在错误的目录下运行,无法找到 `frontend/package.json` 文件。

### 解决方案 ✅

所有脚本已修复!现在可以从任何位置运行。

---

## 🔧 正确的使用方法

### 方法1: 从项目根目录运行 (推荐)
```cmd
cd c:\Users\zacza\WorkBuddy\20260315090337\ai-rpg-engine

REM 运行任何脚本
scripts\setup.bat
scripts\dev.bat
scripts\build.bat
```

### 方法2: 从scripts目录运行
```cmd
cd c:\Users\zacza\WorkBuddy\20260315090337\ai-rpg-engine\scripts

REM 脚本会自动切换到正确的目录
setup.bat
dev.bat
build.bat
```

### 方法3: 双击运行
直接在文件资源管理器中双击任何 `.bat` 文件,脚本会自动定位到项目根目录。

---

## 🚀 快速开始流程

### Step 1: 环境诊断 (可选)
```cmd
cd c:\Users\zacza\WorkBuddy\20260315090337\ai-rpg-engine
quick-test.bat
```
这将检查项目状态和依赖安装情况。

### Step 2: 安装依赖
```cmd
scripts\setup.bat
```
这将:
- 检查 Node.js, Python, Go 是否安装
- 创建项目目录结构
- 安装前端依赖 (npm install)
- 创建Python虚拟环境
- 安装后端依赖
- 下载Go模块

**预计时间**: 5-10分钟

### Step 3: 下载AI模型 (可选)
```cmd
scripts\download-models.bat
```
这将下载嵌入模型和重排序模型。

**注意**: LLM模型需要手动下载,参考 `models/README.md`

### Step 4: 启动服务
```cmd
scripts\dev.bat
```
这将启动4个服务窗口:
1. 游戏引擎 (端口8001)
2. AI引擎 (端口8002)
3. Go网关 (端口8000)
4. 前端开发服务器 (端口5173)

### Step 5: 访问游戏
打开浏览器: **http://localhost:5173**

---

## 📋 修复清单

- [x] 修复 `setup.bat` - 添加自动目录切换
- [x] 修复 `dev.bat` - 添加环境检查
- [x] 修复 `build.bat` - 添加文件存在性检查
- [x] 修复 `download-models.bat` - 添加错误处理
- [x] 修复 `integration_test.bat` - 确保正确路径
- [x] 创建 `quick-test.bat` - 快速诊断脚本

---

## ⚠️ 常见错误

### 错误1: "ENOENT: no such file or directory"
**原因**: 工作目录不正确

**解决**: 脚本已自动修复,或手动cd到项目根目录

### 错误2: "node_modules 不存在"
**原因**: 依赖未安装

**解决**: 运行 `scripts\setup.bat`

### 错误3: "venv 不存在"
**原因**: Python虚拟环境未创建

**解决**: 运行 `scripts\setup.bat`

### 错误4: "Go模块不存在"
**原因**: Go未安装或go.mod文件缺失

**解决**: 
1. 安装Go: https://golang.org/
2. 或跳过Go网关,直接使用Python服务

---

## 🎯 立即开始

```cmd
REM 1. 进入项目目录
cd c:\Users\zacza\WorkBuddy\20260315090337\ai-rpg-engine

REM 2. 运行环境诊断
quick-test.bat

REM 3. 如果依赖未安装,运行:
scripts\setup.bat

REM 4. 启动服务
scripts\dev.bat

REM 5. 打开浏览器
REM http://localhost:5173
```

---

## 💡 提示

1. **首次运行**: 必须先运行 `scripts\setup.bat` 安装依赖
2. **开发模式**: 使用 `scripts\dev.bat` 启动所有服务
3. **生产构建**: 使用 `scripts\build.bat` 构建发布版本
4. **遇到问题**: 运行 `quick-test.bat` 诊断

---

## 📞 还需要帮助?

如果仍有问题,请提供:
1. `quick-test.bat` 的完整输出
2. 具体的错误信息截图
3. 您的操作系统版本

---

**所有问题已修复! 现在可以正常使用了。** ✨
