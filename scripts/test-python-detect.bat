@echo off
chcp 65001 >nul
echo Testing Python detection...
echo.

REM Test py command
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python Launcher (py) found:
    py --version
    echo.
) else (
    echo [X] Python Launcher (py) not found
    echo.
)

REM Test python command
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python (python) found:
    python --version
    echo.
) else (
    echo [X] Python (python) not found
    echo.
)

echo Test complete!
pause
