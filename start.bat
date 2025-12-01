@echo off
REM 项目初始化系统启动脚本（Windows）
REM 使用 pipenv 自动管理虚拟环境，无需手动激活

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set START_PY=%SCRIPT_DIR%coldstart.py
set PIPFILE=%SCRIPT_DIR%Pipfile

REM 检查 Pipfile 是否存在
if not exist "%PIPFILE%" (
    echo ❌ 错误：找不到 Pipfile: %PIPFILE%
    echo.
    echo 请先运行安装脚本：
    echo   python install.py
    echo   或
    echo   install.bat
    exit /b 1
)

REM 检查 pipenv 是否安装
where pipenv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误：pipenv 未安装
    echo.
    echo 请先安装 pipenv：
    echo   python -m pip install --user pipenv
    echo.
    echo 如果 pipenv 命令不可用，请将用户 Scripts 目录添加到 PATH
    exit /b 1
)

REM 检查虚拟环境是否存在，如果不存在则创建
pipenv --venv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  虚拟环境不存在，正在创建...
    cd /d "%SCRIPT_DIR%"
    pipenv install
)

REM 检查 coldstart.py 是否存在
if not exist "%START_PY%" (
    echo ❌ 错误：找不到 coldstart.py: %START_PY%
    exit /b 1
)

REM 使用 pipenv 运行 coldstart.py，并传递所有参数
cd /d "%SCRIPT_DIR%"
pipenv run python "%START_PY%" %*

endlocal
