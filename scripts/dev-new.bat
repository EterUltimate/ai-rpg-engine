@echo off
chcp 65001 >nul
REM 开发启动脚本包装器 - 调用 Python 实现

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 开发环境启动           ║
echo ╚════════════════════════════════════════╝
echo.

REM 检测并调用 Python
where py >nul 2>&1
if %errorlevel% equ 0 (
    py scripts\dev.py %*
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        python scripts\dev.py %*
    ) else (
        echo [ERROR] Python not found!
        pause
        exit /b 1
    )
)

pause
