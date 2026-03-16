@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 开发启动脚本 - 同时启动所有服务

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 开发环境启动           ║
echo ╚════════════════════════════════════════╝
echo.
echo [启动时间: %date% %time%]
echo.

REM ============================================
REM 检查环境
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [步骤 1/2] 检查运行环境                │
echo └─────────────────────────────────────────┘
echo.

set STEP=1
set TOTAL=2
set SERVICES_STARTED=0

REM 检查前端依赖
echo [!STEP!/!TOTAL!] 检查前端依赖...
if not exist "frontend\node_modules" (
    echo     [✗] 前端依赖未安装
    echo.
    echo     请先运行 scripts\setup.bat 安装依赖
    pause
    exit /b 1
)
echo     [✓] 前端依赖已安装

REM 检查Python环境
echo [!STEP!/!TOTAL!] 检查Python环境...
if exist "backend\services\game-engine\venv" (
    echo     [✓] 游戏引擎虚拟环境已创建
) else (
    echo     [!] 游戏引擎虚拟环境未创建
    echo     建议运行 scripts\setup.bat
)

if exist "backend\services\ai-engine\venv" (
    echo     [✓] AI引擎虚拟环境已创建
) else (
    echo     [!] AI引擎虚拟环境未创建
    echo     建议运行 scripts\setup.bat
)

echo.
echo     ✓ 环境检查完成
echo.

REM ============================================
REM 启动服务
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 启动服务               │
echo └─────────────────────────────────────────┘
echo.

REM 启动游戏引擎服务
echo [!STEP!/!TOTAL! - 1/4] 启动游戏引擎服务...
if exist "backend\services\game-engine\venv\Scripts\activate.bat" (
    start "🎮 游戏引擎服务 - 端口8001" cmd /k "cd /d %cd%\backend\services\game-engine && venv\Scripts\activate && python main.py"
    echo     [✓] 游戏引擎服务启动命令已发送
    set /a SERVICES_STARTED+=1
    timeout /t 2 >nul
    echo     [✓] 等待服务初始化...
) else (
    echo     [!] 游戏引擎虚拟环境不存在,跳过
)
echo.

REM 启动AI引擎服务
echo [!STEP!/!TOTAL! - 2/4] 启动AI引擎服务...
if exist "backend\services\ai-engine\venv\Scripts\activate.bat" (
    start "🤖 AI引擎服务 - 端口8002" cmd /k "cd /d %cd%\backend\services\ai-engine && venv\Scripts\activate && python main.py"
    echo     [✓] AI引擎服务启动命令已发送
    set /a SERVICES_STARTED+=1
    timeout /t 2 >nul
    echo     [✓] 等待服务初始化...
) else (
    echo     [!] AI引擎虚拟环境不存在,跳过
)
echo.

REM 启动Go网关
echo [!STEP!/!TOTAL! - 3/4] 启动Go API网关...
if exist "backend\gateway\go.mod" (
    start "🌐 Go API网关 - 端口8000" cmd /k "cd /d %cd%\backend\gateway && go run cmd\main.go"
    echo     [✓] Go网关启动命令已发送
    set /a SERVICES_STARTED+=1
    timeout /t 2 >nul
    echo     [✓] 等待服务初始化...
) else (
    echo     [!] Go模块不存在,跳过
)
echo.

REM 启动前端开发服务器
echo [!STEP!/!TOTAL! - 4/4] 启动前端开发服务器...
if exist "frontend\package.json" (
    start "💻 前端开发服务器 - 端口5173" cmd /k "cd /d %cd%\frontend && npm run dev"
    echo     [✓] 前端服务器启动命令已发送
    set /a SERVICES_STARTED+=1
    timeout /t 3 >nul
    echo     [✓] 等待Vite启动...
) else (
    echo     [✗] 前端项目不存在
    pause
    exit /b 1
)
echo.

REM ============================================
REM 完成
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║        所有服务已启动!                 ║
echo ╚════════════════════════════════════════╝
echo.
echo [启动完成时间: %date% %time%]
echo.
echo ┌─────────────────────────────────────────┐
echo │ 已启动 !SERVICES_STARTED! 个服务窗口            │
echo └─────────────────────────────────────────┘
echo.

echo ┌─────────────────────────────────────────┐
echo │ 服务访问地址:                           │
echo └─────────────────────────────────────────┘
echo.
echo   🌐 前端界面
echo      http://localhost:5173
echo.
echo   🔌 API网关
echo      http://localhost:8000
echo      http://localhost:8000/health (健康检查)
echo.
echo   🎮 游戏引擎
echo      http://localhost:8001
echo      http://localhost:8001/health (健康检查)
echo.
echo   🤖 AI引擎
echo      http://localhost:8002
echo      http://localhost:8002/health (健康检查)
echo.

echo ┌─────────────────────────────────────────┐
echo │ 提示:                                   │
echo └─────────────────────────────────────────┘
echo.
echo   - 关闭各服务窗口即可停止服务
echo   - 首次启动AI引擎可能需要加载模型,请耐心等待
echo   - 如果端口被占用,请修改配置或关闭占用进程
echo.

echo ┌─────────────────────────────────────────┐
echo │ 测试服务状态:                           │
echo └─────────────────────────────────────────┘
echo.
echo   正在检查服务健康状态...
echo.

REM 等待服务启动
timeout /t 3 >nul

REM 检查Go网关
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [✓] Go网关 (端口8000) - 运行正常
) else (
    echo   [!] Go网关 (端口8000) - 未响应
)

REM 检查游戏引擎
curl -s http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [✓] 游戏引擎 (端口8001) - 运行正常
) else (
    echo   [!] 游戏引擎 (端口8001) - 未响应或正在启动
)

REM 检查AI引擎
curl -s http://localhost:8002/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [✓] AI引擎 (端口8002) - 运行正常
) else (
    echo   [!] AI引擎 (端口8002) - 未响应或正在启动
)

REM 检查前端
curl -s http://localhost:5173 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [✓] 前端服务器 (端口5173) - 运行正常
) else (
    echo   [!] 前端服务器 (端口5173) - 未响应或正在启动
)

echo.
echo ┌─────────────────────────────────────────┐
echo │ 准备就绪!                               │
echo └─────────────────────────────────────────┘
echo.
echo   🎮 打开浏览器访问: http://localhost:5173
echo.
pause
