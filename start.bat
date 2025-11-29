@echo off
REM 项目初始化系统启动脚本（Windows）
REM 自动使用虚拟环境，无需手动激活

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe
set START_PY=%SCRIPT_DIR%coldstart.py

REM 检查虚拟环境是否存在
if not exist "%VENV_DIR%" (
    echo 错误：虚拟环境不存在
    echo.
    echo 请先运行安装脚本创建虚拟环境：
    echo   python install.py
    echo   或
    echo   install.bat
    exit /b 1
)

REM 检查虚拟环境中的Python是否存在
if not exist "%VENV_PYTHON%" (
    echo 错误：虚拟环境中的Python不存在: %VENV_PYTHON%
    echo.
    echo 请重新运行安装脚本：
    echo   python install.py
    exit /b 1
)

REM 检查coldstart.py是否存在
if not exist "%START_PY%" (
    echo 错误：找不到 coldstart.py: %START_PY%
    exit /b 1
)

REM 使用虚拟环境的Python运行coldstart.py，并传递所有参数
"%VENV_PYTHON%" "%START_PY%" %*

endlocal

