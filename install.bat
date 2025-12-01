@echo off
REM 跨平台依赖安装脚本（Windows）
REM 使用 pyenv 和 pipenv 管理 Python 版本和依赖
REM Mac/Linux用户请使用 install.sh 或 install.py

setlocal enabledelayedexpansion

echo ==================================================
echo   项目初始化系统 - 依赖安装
echo   使用 pyenv + pipenv
echo ==================================================
echo.

set SCRIPT_DIR=%~dp0
set PIPFILE=%SCRIPT_DIR%Pipfile
set PYTHON_VERSION_FILE=%SCRIPT_DIR%.python-version

REM 检查 pyenv
echo [1/4] 检查 pyenv...
where pyenv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pyenv 已安装
    set PYENV_AVAILABLE=1
) else (
    echo ❌ pyenv 未安装
    echo.
    echo 请安装 pyenv-win: https://github.com/pyenv-win/pyenv-win
    echo.
    set /p CONTINUE="是否继续安装（将使用系统 Python）？(y/N): "
    if /i not "!CONTINUE!"=="y" if /i not "!CONTINUE!"=="yes" (
        echo 安装已取消
        exit /b 1
    )
    set PYENV_AVAILABLE=0
)
echo.

REM 检查 Python 版本
echo [2/4] 检查 Python 版本...
if exist "%PYTHON_VERSION_FILE%" (
    set /p REQUIRED_VERSION=<"%PYTHON_VERSION_FILE%"
    echo 📋 项目要求的 Python 版本: !REQUIRED_VERSION!
    
    if !PYENV_AVAILABLE! EQU 1 (
        REM 检查 pyenv 是否已安装该版本
        pyenv versions | findstr /C:"!REQUIRED_VERSION!" >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo ✅ Python !REQUIRED_VERSION! 已安装
        ) else (
            echo ⚠️  Python !REQUIRED_VERSION! 未安装
            echo.
            echo 正在安装 Python !REQUIRED_VERSION!...
            pyenv install !REQUIRED_VERSION!
            if !ERRORLEVEL! NEQ 0 (
                echo ❌ 安装失败
                exit /b 1
            )
        )
        
        REM 设置本地版本
        echo 设置本地 Python 版本...
        pyenv local !REQUIRED_VERSION!
        
        for /f "tokens=1" %%i in ('pyenv version-name') do set CURRENT_VERSION=%%i
        echo ✅ 当前 Python 版本: !CURRENT_VERSION!
    ) else (
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do set CURRENT_VERSION=%%i
        echo 当前 Python 版本: !CURRENT_VERSION!
        echo ⚠️  建议安装 pyenv-win 以使用指定版本
    )
) else (
    echo ⚠️  警告：未找到 .python-version 文件
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set CURRENT_VERSION=%%i
    echo 当前 Python 版本: !CURRENT_VERSION!
)
echo.

REM 检查 pipenv
echo [3/4] 检查 pipenv...
where pipenv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pipenv 已安装
) else (
    echo ❌ pipenv 未安装
    echo.
    echo 正在安装 pipenv...
    python -m pip install --user pipenv
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ pipenv 安装失败
        echo.
        echo 请手动安装：
        echo   python -m pip install --user pipenv
        echo.
        echo 如果 pipenv 命令不可用，请将用户 Scripts 目录添加到 PATH：
        echo   %%APPDATA%%\Python\Python{version}\Scripts
        exit /b 1
    )
    echo ✅ pipenv 安装成功
    echo.
    echo ⚠️  提示：如果 pipenv 命令不可用，请将用户 Scripts 目录添加到 PATH
)
echo.

REM 检查 Pipfile
if not exist "%PIPFILE%" (
    echo ❌ 错误：找不到 Pipfile: %PIPFILE%
    exit /b 1
)

REM 安装依赖
echo [4/4] 安装依赖...
echo 执行: pipenv install
echo.

cd /d "%SCRIPT_DIR%"
pipenv install
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 安装失败
    echo.
    echo 提示：
    echo 1. 检查网络连接
    echo 2. 检查 Pipfile 文件格式
    echo 3. 确保 pyenv-win 已安装并配置正确
    exit /b 1
)

echo.
echo ==================================================
echo   ✅ 安装完成！
echo ==================================================
echo.
echo 使用方式：
echo   使用包装脚本（推荐）：
echo     start.bat [目标项目目录]
echo.
echo   使用 pipenv 直接运行：
echo     pipenv run python coldstart.py [目标项目目录]
echo.
echo   激活虚拟环境：
echo     pipenv shell
echo.

endlocal
