@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 构建脚本 - 构建所有组件

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 项目构建               ║
echo ╚════════════════════════════════════════╝
echo.
echo [开始时间: %date% %time%]
echo.

REM 检查是否在正确的目录
if not exist "frontend\package.json" (
    echo     [✗] 未找到 frontend\package.json
    echo     请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

set TOTAL_STEPS=3
set CURRENT_STEP=0

REM ============================================
REM 步骤1: 构建前端
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 构建前端             │
echo └─────────────────────────────────────────┘
echo.

cd frontend

REM 检查node_modules
if not exist "node_modules" (
    echo [!CURRENT_STEP!/!TOTAL_STEPS!] node_modules不存在,先安装依赖...
    echo     这可能需要几分钟...
    echo.
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo     [✗] 依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    echo     [✓] 依赖安装完成
    echo.
)

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 执行前端构建...
echo     运行: npm run build
echo.
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo     [✗] 前端构建失败
    cd ..
    pause
    exit /b 1
)

cd ..
echo.
echo     [✓] 前端构建完成
echo     输出目录: frontend\dist
echo.

REM ============================================
REM 步骤2: 构建Go网关
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 构建Go网关           │
echo └─────────────────────────────────────────┘
echo.

if not exist "backend\gateway\go.mod" (
    echo [!CURRENT_STEP!/!TOTAL_STEPS!] Go模块不存在,跳过
    echo     [!] 未找到 backend\gateway\go.mod
    echo.
) else (
    cd backend\gateway
    
    echo [!CURRENT_STEP!/!TOTAL_STEPS!] 检查Go依赖...
    if not exist "go.sum" (
        echo     [!] go.sum不存在,运行 go mod tidy
        go mod tidy
        if %ERRORLEVEL% NEQ 0 (
            echo     [✗] Go依赖整理失败
            cd ..\..
            pause
            exit /b 1
        )
        echo     [✓] go.sum生成完成
    )
    
    echo [!CURRENT_STEP!/!TOTAL_STEPS!] 编译Go程序...
    echo     运行: go build -o gateway.exe cmd\main.go
    echo.
    go build -o gateway.exe cmd\main.go
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo     [✗] Go网关构建失败
        cd ..\..
        pause
        exit /b 1
    )
    
    cd ..\..
    echo.
    echo     [✓] Go网关构建完成
    echo     输出文件: backend\gateway\gateway.exe
    echo.
)

REM ============================================
REM 步骤3: 创建发布包
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [步骤 !CURRENT_STEP!/!TOTAL_STEPS!] 创建发布包           │
echo └─────────────────────────────────────────┘
echo.

REM 生成发布目录名
set RELEASE_DIR=release\ai-rpg-engine-%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set RELEASE_DIR=%RELEASE_DIR: =0%

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 创建发布目录...
echo     路径: %RELEASE_DIR%
mkdir %RELEASE_DIR% 2>nul
echo     [✓] 目录创建完成
echo.

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 复制文件...

REM 复制前端
if exist "frontend\dist" (
    echo     [1/6] 复制前端构建文件...
    xcopy /E /I /Q frontend\dist %RELEASE_DIR%\frontend >nul
    echo     [✓] 前端文件复制完成
) else (
    echo     [!] 前端构建文件不存在,跳过
)

REM 复制后端
if exist "backend" (
    echo     [2/6] 复制后端服务文件...
    xcopy /E /I /Q backend %RELEASE_DIR%\backend >nul
    echo     [✓] 后端文件复制完成
) else (
    echo     [!] 后端文件不存在,跳过
)

REM 复制数据库
if exist "database" (
    echo     [3/6] 复制数据库文件...
    xcopy /E /I /Q database %RELEASE_DIR%\database >nul
    echo     [✓] 数据库文件复制完成
) else (
    echo     [!] 数据库文件不存在,跳过
)

REM 复制模型
if exist "models" (
    echo     [4/6] 复制模型文件...
    xcopy /E /I /Q models %RELEASE_DIR%\models >nul
    echo     [✓] 模型文件复制完成
) else (
    echo     [!] 模型文件不存在,跳过
)

REM 复制配置文件
echo     [5/6] 复制配置文件...
if exist "docker-compose.yml" (
    copy docker-compose.yml %RELEASE_DIR%\ >nul
    echo     [✓] docker-compose.yml 复制完成
)
if exist "README.md" (
    copy README.md %RELEASE_DIR%\ >nul
    echo     [✓] README.md 复制完成
)
if exist ".env.example" (
    copy .env.example %RELEASE_DIR%\.env >nul
    echo     [✓] .env 配置模板复制完成
)

REM 创建启动脚本
echo     [6/6] 创建启动脚本...
(
    echo @echo off
    echo echo 启动AI-RPG Engine...
    echo cd backend\gateway
    echo start gateway.exe
    echo cd ..\..\frontend
    echo echo 请使用Web服务器托管此目录
    echo echo 或运行: npx serve .
    echo pause
) > %RELEASE_DIR%\start.bat
echo     [✓] start.bat 创建完成

echo.

REM ============================================
REM 完成
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║         构建完成!                      ║
echo ╚════════════════════════════════════════╝
echo.
echo [完成时间: %date% %time%]
echo.

echo ┌─────────────────────────────────────────┐
echo │ 构建统计:                               │
echo └─────────────────────────────────────────┘
echo.

REM 统计文件数量
set FILE_COUNT=0
for /r %RELEASE_DIR% %%f in (*) do set /a FILE_COUNT+=1

echo   发布目录: %RELEASE_DIR%
echo   文件总数: !FILE_COUNT! 个
echo.

echo ┌─────────────────────────────────────────┐
echo │ 下一步:                                 │
echo └─────────────────────────────────────────┘
echo.
echo   1. 进入发布目录
echo      cd %RELEASE_DIR%
echo.
echo   2. 配置环境变量
echo      编辑 .env 文件设置必要参数
echo.
echo   3. 启动服务
echo      运行 start.bat
echo.
echo   4. 托管前端
echo      cd frontend ^&^& npx serve .
echo      或使用其他Web服务器
echo.

pause
