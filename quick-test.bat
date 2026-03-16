@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 快速诊断脚本 - 检查项目环境

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 环境诊断               ║
echo ╚════════════════════════════════════════╝
echo.
echo [诊断时间: %date% %time%]
echo.

set TOTAL_CHECKS=15
set PASSED=0
set FAILED=0
set WARNINGS=0

REM ============================================
REM 检查1: 当前目录
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 1/!TOTAL_CHECKS!] 项目位置              │
echo └─────────────────────────────────────────┘
echo.
echo     当前目录:
echo     %cd%
echo.

REM ============================================
REM 检查2-5: 项目结构
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 2-5/!TOTAL_CHECKS!] 项目结构            │
echo └─────────────────────────────────────────┘
echo.

if exist "frontend\package.json" (
    echo     [✓] 前端项目存在
    set /a PASSED+=1
) else (
    echo     [✗] 前端项目不存在
    set /a FAILED+=1
)

if exist "backend\gateway\go.mod" (
    echo     [✓] Go网关项目存在
    set /a PASSED+=1
) else (
    echo     [!] Go网关项目不存在 (可选)
    set /a WARNINGS+=1
)

if exist "backend\services\game-engine\requirements.txt" (
    echo     [✓] 游戏引擎项目存在
    set /a PASSED+=1
) else (
    echo     [✗] 游戏引擎项目不存在
    set /a FAILED+=1
)

if exist "backend\services\ai-engine\requirements.txt" (
    echo     [✓] AI引擎项目存在
    set /a PASSED+=1
) else (
    echo     [✗] AI引擎项目不存在
    set /a FAILED+=1
)

echo.

REM ============================================
REM 检查6-8: 依赖安装状态
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 6-8/!TOTAL_CHECKS!] 依赖安装状态        │
echo └─────────────────────────────────────────┘
echo.

if exist "frontend\node_modules" (
    echo     [✓] 前端依赖已安装 (node_modules存在)
    set /a PASSED+=1
) else (
    echo     [!] 前端依赖未安装 - 运行 scripts\setup.bat
    set /a WARNINGS+=1
)

if exist "backend\services\game-engine\venv" (
    echo     [✓] 游戏引擎虚拟环境已创建
    set /a PASSED+=1
) else (
    echo     [!] 游戏引擎虚拟环境未创建 - 运行 scripts\setup.bat
    set /a WARNINGS+=1
)

if exist "backend\services\ai-engine\venv" (
    echo     [✓] AI引擎虚拟环境已创建
    set /a PASSED+=1
) else (
    echo     [!] AI引擎虚拟环境未创建 - 运行 scripts\setup.bat
    set /a WARNINGS+=1
)

echo.

REM ============================================
REM 检查9-11: 开发工具
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 9-11/!TOTAL_CHECKS!] 开发工具            │
echo └─────────────────────────────────────────┘
echo.

where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
    echo     [✓] Node.js 已安装 !NODE_VER!
    set /a PASSED+=1
) else (
    echo     [✗] Node.js 未安装
    set /a FAILED+=1
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo     [✓] Python 已安装 !PYTHON_VER!
    set /a PASSED+=1
) else (
    echo     [✗] Python 未安装
    set /a FAILED+=1
)

where go >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('go version') do set GO_VER=%%i
    echo     [✓] Go 已安装 !GO_VER!
    set /a PASSED+=1
) else (
    echo     [!] Go 未安装 (可选)
    set /a WARNINGS+=1
)

echo.

REM ============================================
REM 检查12-14: 模型目录
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 12-14/!TOTAL_CHECKS!] 模型目录          │
echo └─────────────────────────────────────────┘
echo.

if exist "models\embeddings" (
    echo     [✓] 嵌入模型目录存在
    set /a PASSED+=1
) else (
    echo     [!] 嵌入模型目录不存在 - 运行 scripts\download-models.bat
    set /a WARNINGS+=1
)

if exist "models\rerankers" (
    echo     [✓] 重排序模型目录存在
    set /a PASSED+=1
) else (
    echo     [!] 重排序模型目录不存在 - 运行 scripts\download-models.bat
    set /a WARNINGS+=1
)

if exist "models\llm" (
    echo     [✓] LLM模型目录存在
    set /a PASSED+=1
) else (
    echo     [!] LLM模型目录不存在
    set /a WARNINGS+=1
)

echo.

REM ============================================
REM 检查15: 数据库目录
REM ============================================
echo ┌─────────────────────────────────────────┐
echo │ [检查 15/!TOTAL_CHECKS!] 数据库目录           │
echo └─────────────────────────────────────────┘
echo.

if exist "database\sqlite" (
    echo     [✓] SQLite数据库目录存在
    set /a PASSED+=1
) else (
    echo     [!] SQLite数据库目录不存在 - 运行 scripts\setup.bat
    set /a WARNINGS+=1
)

if exist "database\chromadb" (
    echo     [✓] ChromaDB目录存在
) else (
    echo     [!] ChromaDB目录不存在 - 运行 scripts\setup.bat
)

echo.

REM ============================================
REM 诊断总结
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║         诊断完成                       ║
echo ╚════════════════════════════════════════╝
echo.

echo ┌─────────────────────────────────────────┐
echo │ 诊断结果:                               │
echo └─────────────────────────────────────────┘
echo.
echo     通过: !PASSED! / !TOTAL_CHECKS!
echo     失败: !FAILED! / !TOTAL_CHECKS!
echo     警告: !WARNINGS! / !TOTAL_CHECKS!
echo.

if !FAILED! GTR 0 (
    echo ┌─────────────────────────────────────────┐
    echo │ ❌ 项目环境不完整                      │
    echo └─────────────────────────────────────────┘
    echo.
    echo     建议操作:
    echo       1. 运行 scripts\setup.bat 安装依赖
    echo       2. 运行 scripts\download-models.bat 下载模型
    echo.
) else if !WARNINGS! GTR 0 (
    echo ┌─────────────────────────────────────────┐
    echo │ ⚠️  项目环境基本完整,但部分功能缺失     │
    echo └─────────────────────────────────────────┘
    echo.
    echo     建议操作:
    echo       1. 如果依赖未安装: scripts\setup.bat
    echo       2. 如果模型未下载: scripts\download-models.bat
    echo       3. 启动服务测试: scripts\dev.bat
    echo.
) else (
    echo ┌─────────────────────────────────────────┐
    echo │ ✅ 项目环境完整,可以正常使用           │
    echo └─────────────────────────────────────────┘
    echo.
    echo     下一步:
    echo       1. 启动服务: scripts\dev.bat
    echo       2. 访问游戏: http://localhost:5173
    echo.
)

echo ┌─────────────────────────────────────────┐
echo │ 快速命令参考:                           │
echo └─────────────────────────────────────────┘
echo.
echo   scripts\setup.bat          # 安装所有依赖
echo   scripts\download-models.bat   # 下载AI模型
echo   scripts\dev.bat            # 启动开发服务
echo   scripts\build.bat          # 构建生产版本
echo   tests\integration_test.bat # 运行集成测试
echo.

pause
