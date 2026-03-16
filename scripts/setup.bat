@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 错误处理 - 确保窗口不会自动关闭
if "%1"=="SILENT" goto :main
cmd /c "%~f0 SILENT"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo 脚本执行出错，错误代码: %ERRORLEVEL%
    echo ============================================
    pause
)
exit /b %ERRORLEVEL%

:main
REM AI-RPG Engine 环境搭建脚本 (Windows)

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 开发环境搭建           ║
echo ╚════════════════════════════════════════╝
echo.
echo [开始时间: %date% %time%]
echo.

REM ============================================
REM 步骤1: 检查必要的工具
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [步骤 1/6] 检查开发环境                │
echo └─────────────────────────────────────────┘
echo.

set STEP=1
set TOTAL=6

REM 检查Node.js
echo [!STEP!/!TOTAL!] 检查 Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     [X] Node.js 未安装
    echo.
    echo     请从 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo     [OK] Node.js 已安装 !NODE_VER!

REM 检查Python
echo [!STEP!/!TOTAL!] 检查 Python...

REM 首先尝试 py 启动器 (Windows Python Launcher)
set PYTHON_INSTALLED=0
set PYTHON_CMD=

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('py --version 2^>^&1') do set PYTHON_VER=%%i
    echo     [OK] Python 已安装 !PYTHON_VER!
    set PYTHON_CMD=py
    set PYTHON_INSTALLED=1
)

if "%PYTHON_INSTALLED%"=="0" (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        python --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
            echo     [OK] Python 已安装 !PYTHON_VER!
            set PYTHON_CMD=python
            set PYTHON_INSTALLED=1
        )
    )
)

if "%PYTHON_INSTALLED%"=="0" (
    echo     [!] Python 未安装或未正确配置
    echo     [!] 如需使用AI功能,请安装Python
)

REM 检查Go
echo [!STEP!/!TOTAL!] 检查 Go...
where go >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     [!] Go 未安装 (可选)
    echo     请从 https://golang.org/ 下载安装
) else (
    for /f "tokens=*" %%i in ('go version') do set GO_VER=%%i
    echo     [OK] Go 已安装 !GO_VER!
)

echo.
echo     OK 环境检查完成
echo.

REM ============================================
REM 步骤2: 创建目录结构
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 创建项目目录            │
echo └─────────────────────────────────────────┘
echo.

echo [!STEP!/!TOTAL!] 创建数据库目录...
if not exist "database\sqlite" (mkdir database\sqlite && echo     [OK] 创建 database\sqlite) else (echo     [OK] database\sqlite 已存在)
if not exist "database\chromadb" (mkdir database\chromadb && echo     [OK] 创建 database\chromadb) else (echo     [OK] database\chromadb 已存在)

echo [!STEP!/!TOTAL!] 创建模型目录...
if not exist "models\llm" (mkdir models\llm && echo     [OK] 创建 models\llm) else (echo     [OK] models\llm 已存在)
if not exist "models\embeddings" (mkdir models\embeddings && echo     [OK] 创建 models\embeddings) else (echo     [OK] models\embeddings 已存在)
if not exist "models\rerankers" (mkdir models\rerankers && echo     [OK] 创建 models\rerankers) else (echo     [OK] models\rerankers 已存在)

echo [!STEP!/!TOTAL!] 创建资源目录...
if not exist "frontend\public\assets\sprites" (mkdir frontend\public\assets\sprites && echo     [OK] 创建 assets\sprites) else (echo     [OK] assets\sprites 已存在)
if not exist "frontend\public\assets\maps" (mkdir frontend\public\assets\maps && echo     [OK] 创建 assets\maps) else (echo     [OK] assets\maps 已存在)
if not exist "frontend\public\assets\tiles" (mkdir frontend\public\assets\tiles && echo     [OK] 创建 assets\tiles) else (echo     [OK] assets\tiles 已存在)

echo.
echo     OK 目录创建完成
echo.

REM ============================================
REM 步骤3: 安装前端依赖
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 设置前端环境            │
echo └─────────────────────────────────────────┘
echo.

if not exist "frontend\package.json" (
    echo     [X] 未找到 frontend\package.json
    echo     请确保项目结构完整
    pause
    exit /b 1
)

cd frontend

if not exist "node_modules" (
    echo [!STEP!/!TOTAL!] 安装前端依赖...
    echo     这可能需要几分钟,请耐心等待...
    echo.
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo     [X] 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    echo.
    echo     [OK] 前端依赖安装完成
) else (
    echo [!STEP!/!TOTAL!] 前端依赖已安装
    echo     [OK] node_modules 已存在,跳过安装
)

cd ..
echo.
echo     OK 前端环境设置完成
echo.

REM ============================================
REM 步骤4: 设置游戏引擎服务
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 设置游戏引擎服务        │
echo └─────────────────────────────────────────┘
echo.

if "%PYTHON_INSTALLED%"=="0" (
    echo     [!] Python未安装,跳过游戏引擎设置
    echo     [!] 如需使用AI功能,请安装Python后重新运行
    echo.
    goto :skip_game_engine
)

if not exist "backend\services\game-engine\requirements.txt" (
    echo     [!] 未找到游戏引擎requirements.txt,跳过
    echo.
    goto :skip_game_engine
)

cd backend\services\game-engine

REM 创建虚拟环境
if not exist "venv" (
    echo [!STEP!/!TOTAL!] 创建Python虚拟环境...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo     [X] 虚拟环境创建失败
        cd ..\..\..
        pause
        exit /b 1
    )
    echo     [OK] 虚拟环境创建完成
) else (
    echo [!STEP!/!TOTAL!] Python虚拟环境已存在
    echo     [OK] venv 已存在,跳过创建
)

REM 激活虚拟环境并安装依赖
echo [!STEP!/!TOTAL!] 安装游戏引擎依赖...
echo     这可能需要几分钟,请耐心等待...
echo     使用国内镜像源加速下载...
echo.
call venv\Scripts\activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo     [!] 游戏引擎依赖安装失败 (可能是网络问题)
    echo     [!] 你可以稍后手动安装: venv\Scripts\pip install -r requirements.txt
)
deactivate
cd ..\..\..

echo.
echo     OK 游戏引擎环境设置完成
echo.

:skip_game_engine

REM ============================================
REM 步骤5: 设置AI引擎服务
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 设置AI引擎服务          │
echo └─────────────────────────────────────────┘
echo.

if "%PYTHON_INSTALLED%"=="0" (
    echo     [!] Python未安装,跳过AI引擎设置
    echo     [!] 如需使用AI功能,请安装Python后重新运行
    echo.
    goto :skip_ai_engine
)

if not exist "backend\services\ai-engine\requirements.txt" (
    echo     [!] 未找到AI引擎requirements.txt,跳过
    echo.
    goto :skip_ai_engine
)

cd backend\services\ai-engine

REM 创建虚拟环境
if not exist "venv" (
    echo [!STEP!/!TOTAL!] 创建Python虚拟环境...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo     [X] 虚拟环境创建失败
        cd ..\..\..
        pause
        exit /b 1
    )
    echo     [OK] 虚拟环境创建完成
) else (
    echo [!STEP!/!TOTAL!] Python虚拟环境已存在
    echo     [OK] venv 已存在,跳过创建
)

REM 激活虚拟环境并安装依赖
echo [!STEP!/!TOTAL!] 安装AI引擎依赖...
echo     这可能需要几分钟,请耐心等待...
echo     (包含PyTorch等大型库,请耐心等待)
echo     使用国内镜像源加速下载...
echo.
call venv\Scripts\activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo     [!] AI引擎依赖安装失败 (可能是网络问题)
    echo     [!] 你可以稍后手动安装: venv\Scripts\pip install -r requirements.txt
)
deactivate
cd ..\..\..

echo.
echo     OK AI引擎环境设置完成
echo.

:skip_ai_engine

REM ============================================
REM 步骤6: 设置Go网关
REM ============================================
set /a STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !STEP!/!TOTAL!] 设置Go API网关         │
echo └─────────────────────────────────────────┘
echo.

if not exist "backend\gateway\go.mod" (
    echo     [!] 未找到Go模块,跳过
    echo     如果不使用Go网关,可以忽略此警告
    echo.
) else (
    cd backend\gateway
    
    if not exist "go.sum" (
        echo [!STEP!/!TOTAL!] 下载Go依赖...
        echo     这可能需要几分钟,请耐心等待...
        echo.
        go mod download
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo     [X] Go依赖下载失败
            cd ..\..
            pause
            exit /b 1
        )
        echo.
        echo     [OK] Go依赖下载完成
    ) else (
        echo [!STEP!/!TOTAL!] Go依赖已下载
        echo     [OK] go.sum 已存在,跳过下载
    )
    
    cd ..\..
    echo.
    echo     OK Go网关环境设置完成
    echo.
)

REM ============================================
REM 完成
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║         环境搭建完成!                  ║
echo ╚════════════════════════════════════════╝
echo.
echo [完成时间: %date% %time%]
echo.
echo ┌─────────────────────────────────────────┐
echo │ 下一步操作:                             │
echo └─────────────────────────────────────────┘
echo.
echo   1. 下载AI模型 (可选)
echo      运行: scripts\download-models.bat
echo.
echo   2. 启动服务
echo      方式1: 运行 scripts\dev.bat (自动启动所有服务)
echo      方式2: 手动启动各服务
echo.
echo   3. 访问游戏
echo      浏览器打开: http://localhost:5173
echo.
echo ┌─────────────────────────────────────────┐
echo │ 提示:                                   │
echo └─────────────────────────────────────────┘
echo.
echo   - 运行 quick-test.bat 可以检查环境状态
echo   - 查看 START_HERE.md 获取详细帮助
echo.

echo ============================================
echo 脚本执行完毕，按任意键退出...
echo ============================================
pause >nul
