@echo off
REM 跨平台依赖安装脚本（Windows）
REM 自动创建虚拟环境并安装依赖
REM Mac/Linux用户请使用 install.sh 或 install.py

setlocal enabledelayedexpansion

echo ==================================================
echo   项目初始化系统 - 依赖安装
echo ==================================================
echo.

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv
set REQUIREMENTS_FILE=%SCRIPT_DIR%requirements.txt

REM 检查Python
echo [1/4] 检查Python...
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ 找到: Python !PYTHON_VERSION!
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3
        for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
        echo ✅ 找到: Python !PYTHON_VERSION!
    ) else (
        echo ❌ 错误：未找到Python
        echo.
        echo 请安装Python 3.6或更高版本：
        echo   访问 https://www.python.org/downloads/
        echo   或使用包管理器：choco install python3
        exit /b 1
    )
)
echo.

REM 检查venv模块
echo [2/4] 检查venv模块...
%PYTHON_CMD% -m venv --help >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ venv模块可用
) else (
    echo ❌ venv模块不可用
    echo.
    echo 请确保Python版本 >= 3.6，venv模块应包含在标准库中
    exit /b 1
)
echo.

REM 创建虚拟环境
echo [3/4] 创建虚拟环境...
if exist "%VENV_DIR%" (
    echo ✅ 虚拟环境已存在: %VENV_DIR%
) else (
    echo 创建虚拟环境: %VENV_DIR%
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ 创建虚拟环境失败
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)
echo.

REM 安装依赖
echo [4/4] 安装依赖...
if not exist "%REQUIREMENTS_FILE%" (
    echo ❌ 错误：找不到 requirements.txt: %REQUIREMENTS_FILE%
    exit /b 1
)

set VENV_PIP=%VENV_DIR%\Scripts\pip.exe
if not exist "%VENV_PIP%" (
    echo ❌ 错误：虚拟环境中找不到pip: %VENV_PIP%
    exit /b 1
)

echo 执行: %VENV_PIP% install -r %REQUIREMENTS_FILE%
echo.

%VENV_PIP% install -r "%REQUIREMENTS_FILE%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 安装失败
    echo.
    echo 提示：
    echo 1. 检查网络连接
    echo 2. 检查requirements.txt文件格式
    exit /b 1
)

echo.
echo ==================================================
echo   ✅ 安装完成！
echo ==================================================
echo.
echo 虚拟环境位置：
echo   %VENV_DIR%
echo.
echo 激活虚拟环境：
echo   %VENV_DIR%\Scripts\activate.bat
echo.
echo 使用虚拟环境运行：
echo   %VENV_DIR%\Scripts\python.exe coldstart.py init [目标项目目录]
echo.
echo 或者激活虚拟环境后直接运行：
echo   python coldstart.py init [目标项目目录]
echo.

endlocal

