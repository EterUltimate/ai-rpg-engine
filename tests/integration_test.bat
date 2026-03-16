@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 集成测试启动脚本 - Windows版本

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 集成测试               ║
echo ╚════════════════════════════════════════╝
echo.
echo [测试时间: %date% %time%]
echo.

set TOTAL_STEPS=5
set CURRENT_STEP=0
set TESTS_PASSED=0
set TESTS_FAILED=0
set TESTS_WARNING=0

REM ============================================
REM 测试1: 检查服务状态
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [测试 !CURRENT_STEP!/!TOTAL_STEPS!] 服务状态检查         │
echo └─────────────────────────────────────────┘
echo.

echo [!CURRENT_STEP!/!TOTAL_STEPS!] 检查各服务运行状态...
echo.

REM 检查Go网关
echo     检查 Go网关 (端口8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [✓] Go网关运行正常
    set /a TESTS_PASSED+=1
) else (
    echo     [!] Go网关未运行
    set /a TESTS_WARNING+=1
)

REM 检查游戏引擎
echo     检查 游戏引擎 (端口8001)...
curl -s http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [✓] 游戏引擎运行正常
    set /a TESTS_PASSED+=1
) else (
    echo     [!] 游戏引擎未运行
    set /a TESTS_WARNING+=1
)

REM 检查AI引擎
echo     检查 AI引擎 (端口8002)...
curl -s http://localhost:8002/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [✓] AI引擎运行正常
    set /a TESTS_PASSED+=1
) else (
    echo     [!] AI引擎未运行
    set /a TESTS_WARNING+=1
)

REM 检查前端
echo     检查 前端服务器 (端口5173)...
curl -s http://localhost:5173 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     [✓] 前端服务器运行正常
    set /a TESTS_PASSED+=1
) else (
    echo     [!] 前端服务器未运行
    set /a TESTS_WARNING+=1
)

echo.
echo     测试1完成: !TESTS_PASSED! 通过, !TESTS_WARNING! 警告
echo.

REM ============================================
REM 测试2: 前端构建检查
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [测试 !CURRENT_STEP!/!TOTAL_STEPS!] 前端构建检查         │
echo └─────────────────────────────────────────┘
echo.

if not exist "frontend\package.json" (
    echo     [✗] 前端项目不存在
    set /a TESTS_FAILED+=1
    echo.
    goto test3
)

cd frontend

if exist "dist" (
    echo     [✓] 前端已构建 (dist目录存在)
    set /a TESTS_PASSED+=1
    
    REM 检查构建文件
    if exist "dist\index.html" (
        echo     [✓] index.html 存在
        set /a TESTS_PASSED+=1
    ) else (
        echo     [✗] index.html 不存在
        set /a TESTS_FAILED+=1
    )
) else (
    echo     [!] 前端未构建
    echo.
    echo     正在执行构建...
    if exist "node_modules" (
        call npm run build
        if %ERRORLEVEL% EQU 0 (
            echo     [✓] 前端构建成功
            set /a TESTS_PASSED+=1
        ) else (
            echo     [✗] 前端构建失败
            set /a TESTS_FAILED+=1
        )
    ) else (
        echo     [!] node_modules不存在,跳过构建
        set /a TESTS_WARNING+=1
    )
)

cd ..
echo.

REM ============================================
REM 测试3: Python集成测试
REM ============================================
:test3
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [测试 !CURRENT_STEP!/!TOTAL_STEPS!] Python集成测试        │
echo └─────────────────────────────────────────┘
echo.

if exist "tests\integration_test.py" (
    echo     [!CURRENT_STEP!/!TOTAL_STEPS!] 运行Python测试脚本...
    echo.
    python tests\integration_test.py
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo     [✓] Python测试通过
        set /a TESTS_PASSED+=1
    ) else (
        echo.
        echo     [✗] Python测试失败
        set /a TESTS_FAILED+=1
    )
) else (
    echo     [!] 未找到测试脚本: tests\integration_test.py
    set /a TESTS_WARNING+=1
)

echo.

REM ============================================
REM 测试4: 依赖安装检查
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [测试 !CURRENT_STEP!/!TOTAL_STEPS!] 依赖安装检查         │
echo └─────────────────────────────────────────┘
echo.

REM 检查前端依赖
echo     检查前端依赖...
if exist "frontend\node_modules" (
    echo     [✓] 前端依赖已安装
    set /a TESTS_PASSED+=1
) else (
    echo     [!] 前端依赖未安装
    set /a TESTS_WARNING+=1
)

REM 检查游戏引擎依赖
echo     检查游戏引擎Python依赖...
if exist "backend\services\game-engine\venv" (
    echo     [✓] 游戏引擎虚拟环境存在
    set /a TESTS_PASSED+=1
) else (
    echo     [!] 游戏引擎虚拟环境不存在
    set /a TESTS_WARNING+=1
)

REM 检查AI引擎依赖
echo     检查AI引擎Python依赖...
if exist "backend\services\ai-engine\venv" (
    echo     [✓] AI引擎虚拟环境存在
    set /a TESTS_PASSED+=1
) else (
    echo     [!] AI引擎虚拟环境不存在
    set /a TESTS_WARNING+=1
)

echo.

REM ============================================
REM 测试5: 生成测试报告
REM ============================================
set /a CURRENT_STEP+=1
echo ┌─────────────────────────────────────────┐
echo │ [测试 !CURRENT_STEP!/!TOTAL_STEPS!] 生成测试报告         │
echo └─────────────────────────────────────────┘
echo.

echo     正在生成测试报告...
echo.

(
    echo ╔════════════════════════════════════════╗
    echo ║   AI-RPG Engine 集成测试报告           ║
    echo ╚════════════════════════════════════════╝
    echo.
    echo 测试时间: %date% %time%
    echo.
    echo ┌─────────────────────────────────────────┐
    echo │ 测试统计:                               │
    echo └─────────────────────────────────────────┘
    echo.
    echo   通过: !TESTS_PASSED! 项
    echo   失败: !TESTS_FAILED! 项
    echo   警告: !TESTS_WARNING! 项
    echo.
    echo ┌─────────────────────────────────────────┐
    echo │ 测试项目:                               │
    echo └─────────────────────────────────────────┘
    echo.
    echo   [1] 服务状态检查 - 完成
    echo   [2] 前端构建检查 - 完成
    echo   [3] Python集成测试 - 完成
    echo   [4] 依赖安装检查 - 完成
    echo   [5] 测试报告生成 - 完成
    echo.
    echo ┌─────────────────────────────────────────┐
    echo │ 建议:                                   │
    echo └─────────────────────────────────────────┘
    echo.
    if !TESTS_FAILED! GTR 0 (
        echo   ❌ 测试未通过
        echo   请修复失败的测试项后重新运行
    ) else if !TESTS_WARNING! GTR 0 (
        echo   ⚠️  测试基本通过,但有警告
        echo   建议处理警告项以获得最佳体验
    ) else (
        echo   ✅ 所有测试通过
        echo   项目状态良好,可以正常使用
    )
    echo.
    echo 详细信息请查看上方输出
    echo.
) > test_report.txt

echo     [✓] 测试报告已生成: test_report.txt
set /a TESTS_PASSED+=1
echo.

REM ============================================
REM 测试总结
REM ============================================
echo ╔════════════════════════════════════════╗
echo ║         集成测试完成                   ║
echo ╚════════════════════════════════════════╝
echo.

echo ┌─────────────────────────────────────────┐
echo │ 测试结果总结:                           │
echo └─────────────────────────────────────────┘
echo.
echo     ✅ 通过: !TESTS_PASSED! 项
echo     ❌ 失败: !TESTS_FAILED! 项
echo     ⚠️  警告: !TESTS_WARNING! 项
echo.

if !TESTS_FAILED! GTR 0 (
    echo ┌─────────────────────────────────────────┐
    echo │ ❌ 测试未完全通过                      │
    echo └─────────────────────────────────────────┘
    echo.
    echo     请查看测试报告了解详情: test_report.txt
    echo.
    echo     建议:
    echo       1. 确保所有服务已启动 (scripts\dev.bat)
    echo       2. 确保依赖已安装 (scripts\setup.bat)
    echo       3. 查看具体错误信息进行修复
    echo.
) else if !TESTS_WARNING! GTR 0 (
    echo ┌─────────────────────────────────────────┐
    echo │ ⚠️  测试通过,但有警告项                 │
    echo └─────────────────────────────────────────┘
    echo.
    echo     测试报告: test_report.txt
    echo.
    echo     提示: 处理警告项可以获得更完整的功能
    echo.
) else (
    echo ┌─────────────────────────────────────────┐
    echo │ ✅ 所有测试通过!                       │
    echo └─────────────────────────────────────────┘
    echo.
    echo     测试报告: test_report.txt
    echo.
    echo     项目状态良好,可以正常使用!
    echo     启动服务: scripts\dev.bat
    echo     访问游戏: http://localhost:5173
    echo.
)

pause
