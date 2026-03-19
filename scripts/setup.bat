@echo off
chcp 65001 >nul
REM 项目设置脚本包装器 - 调用 Python 实现

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 项目设置               ║
echo ╚════════════════════════════════════════╝
echo.

REM 检测并调用 Python
REM 优先使用 Python Launcher (py)，如果不存在则尝试 python
where py >nul 2>&1
if %errorlevel% equ 0 (
    py scripts\setup.py %*
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        python scripts\setup.py %*
    ) else (
        echo [ERROR] Python not found!
        echo Please install Python 3.10+ from https://www.python.org/
        echo or Microsoft Store.
        pause
        exit /b 1
    )
)

pause
