#!/bin/bash

# 跨平台依赖安装脚本（Mac/Linux）
# 使用 pyenv 和 pipenv 管理 Python 版本和依赖
# Windows用户请使用 install.bat 或 install.py

set -e

echo "=================================================="
echo "  项目初始化系统 - 依赖安装"
echo "  使用 pyenv + pipenv"
echo "=================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPFILE="$SCRIPT_DIR/Pipfile"
PYTHON_VERSION_FILE="$SCRIPT_DIR/.python-version"

# 检查 pyenv
echo "[1/4] 检查 pyenv..."
if command -v pyenv &> /dev/null; then
    echo "✅ pyenv 已安装"
    PYENV_AVAILABLE=true
else
    echo "❌ pyenv 未安装"
    echo ""
    echo "请安装 pyenv："
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install pyenv"
        echo "  然后添加到 ~/.zshrc 或 ~/.bash_profile："
        echo '    export PYENV_ROOT="$HOME/.pyenv"'
        echo '    export PATH="$PYENV_ROOT/bin:$PATH"'
        echo '    eval "$(pyenv init -)"'
    else
        echo "  参考: https://github.com/pyenv/pyenv#installation"
    fi
    echo ""
    read -p "是否继续安装（将使用系统 Python）？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 1
    fi
    PYENV_AVAILABLE=false
fi
echo ""

# 检查 Python 版本
echo "[2/4] 检查 Python 版本..."
if [ -f "$PYTHON_VERSION_FILE" ]; then
    REQUIRED_VERSION=$(cat "$PYTHON_VERSION_FILE" | tr -d '[:space:]')
    echo "📋 项目要求的 Python 版本: $REQUIRED_VERSION"
    
    if [ "$PYENV_AVAILABLE" = true ]; then
        # 检查 pyenv 是否已安装该版本（支持精确匹配和主次版本匹配）
        INSTALLED_VERSIONS=$(pyenv versions --bare 2>/dev/null || echo "")
        VERSION_INSTALLED=false
        
        if [ -n "$INSTALLED_VERSIONS" ]; then
            while IFS= read -r ver; do
                if [ "$ver" = "$REQUIRED_VERSION" ] || [[ "$ver" == "$REQUIRED_VERSION"* ]]; then
                    VERSION_INSTALLED=true
                    break
                fi
            done <<< "$INSTALLED_VERSIONS"
        fi
        
        if [ "$VERSION_INSTALLED" = false ]; then
            echo "⚠️  Python $REQUIRED_VERSION 未安装"
            echo ""
            echo "正在使用 pyenv 安装 Python $REQUIRED_VERSION..."
            echo "（这可能需要几分钟时间）"
            echo ""
            pyenv install "$REQUIRED_VERSION" || {
                echo "❌ 安装失败"
                echo ""
                echo "请手动安装："
                echo "  pyenv install $REQUIRED_VERSION"
                exit 1
            }
            echo "✅ Python $REQUIRED_VERSION 安装成功"
        else
            echo "✅ Python $REQUIRED_VERSION 已安装"
        fi
        
        # 设置本地版本
        echo "设置本地 Python 版本..."
        cd "$SCRIPT_DIR"
        pyenv local "$REQUIRED_VERSION" || {
            echo "⚠️  设置本地版本失败，继续使用当前版本"
        }
        
        CURRENT_VERSION=$(pyenv version-name 2>/dev/null || echo "未知")
        echo "✅ 当前 Python 版本: $CURRENT_VERSION"
    else
        CURRENT_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        echo "当前 Python 版本: $CURRENT_VERSION"
        echo "⚠️  建议安装 pyenv 以使用指定版本"
    fi
else
    echo "⚠️  警告：未找到 .python-version 文件"
    CURRENT_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    echo "当前 Python 版本: $CURRENT_VERSION"
fi
echo ""

# 检查 pipenv
echo "[3/4] 检查 pipenv..."
if command -v pipenv &> /dev/null; then
    echo "✅ pipenv 已安装"
else
    echo "❌ pipenv 未安装"
    echo ""
    echo "正在安装 pipenv..."
    pip3 install --user pipenv || {
        echo "❌ pipenv 安装失败"
        echo ""
        echo "请手动安装："
        echo "  pip3 install --user pipenv"
        echo ""
        echo "如果 pipenv 命令不可用，请将 ~/.local/bin 添加到 PATH"
        exit 1
    }
    echo "✅ pipenv 安装成功"
    echo ""
    echo "⚠️  提示：如果 pipenv 命令不可用，请将 ~/.local/bin 添加到 PATH"
    echo "  添加到 ~/.zshrc 或 ~/.bash_profile："
    echo '    export PATH="$HOME/.local/bin:$PATH"'
fi
echo ""

# 检查 Pipfile
if [ ! -f "$PIPFILE" ]; then
    echo "❌ 错误：找不到 Pipfile: $PIPFILE"
    exit 1
fi

# 安装依赖
echo "[4/4] 安装依赖..."
echo "执行: pipenv install"
echo ""

cd "$SCRIPT_DIR"
pipenv install || {
    echo ""
    echo "❌ 安装失败"
    echo ""
    echo "提示："
    echo "1. 检查网络连接"
    echo "2. 检查 Pipfile 文件格式"
    echo "3. 确保 pyenv 已安装并配置正确"
    exit 1
}

echo ""
echo "=================================================="
echo "  ✅ 安装完成！"
echo "=================================================="
echo ""
echo "使用方式："
echo "  使用包装脚本（推荐）："
echo "    ./start [目标项目目录]"
echo ""
echo "  使用 pipenv 直接运行："
echo "    pipenv run python coldstart.py [目标项目目录]"
echo ""
echo "  激活虚拟环境："
echo "    pipenv shell"
echo ""
