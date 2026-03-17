@echo off
chcp 65001 >nul
REM 系统诊断脚本包装器 - 调用 Python 实现

REM 切换到项目根目录
cd /d "%~dp0.."

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI-RPG Engine 系统诊断               ║
echo ╚════════════════════════════════════════╝
echo.

REM 调用 Python 脚本
python scripts\doctor.py %*

pause
