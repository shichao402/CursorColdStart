#!/bin/bash

# 跨平台依赖安装脚本（Mac/Linux）
# 自动创建虚拟环境并安装依赖
# Windows用户请使用 install.bat 或 install.py

set -e

echo "=================================================="
echo "  项目初始化系统 - 依赖安装"
echo "=================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# 检查Python
echo "[1/4] 检查Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo "✅ 找到: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo "✅ 找到: $PYTHON_VERSION"
else
    echo "❌ 错误：未找到Python"
    echo ""
    echo "请安装Python 3.6或更高版本："
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION_NUM=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$(echo "$PYTHON_VERSION_NUM < 3.6" | bc 2>/dev/null || echo 0)" = "1" ]; then
    echo "❌ 错误：需要Python 3.6或更高版本"
    echo "当前版本: $PYTHON_VERSION_NUM"
    exit 1
fi
echo ""

# 检查venv模块
echo "[2/4] 检查venv模块..."
if $PYTHON_CMD -m venv --help &> /dev/null; then
    echo "✅ venv模块可用"
else
    echo "❌ venv模块不可用"
    echo ""
    echo "请安装python3-venv："
    echo "  Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3-venv"
    exit 1
fi
echo ""

# 创建虚拟环境
echo "[3/4] 创建虚拟环境..."
if [ -d "$VENV_DIR" ]; then
    echo "✅ 虚拟环境已存在: $VENV_DIR"
else
    echo "创建虚拟环境: $VENV_DIR"
    $PYTHON_CMD -m venv "$VENV_DIR" || {
        echo "❌ 创建虚拟环境失败"
        exit 1
    }
    echo "✅ 虚拟环境创建成功"
fi
echo ""

# 安装依赖
echo "[4/4] 安装依赖..."
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ 错误：找不到 requirements.txt: $REQUIREMENTS_FILE"
    exit 1
fi

VENV_PIP="$VENV_DIR/bin/pip"
if [ ! -f "$VENV_PIP" ]; then
    echo "❌ 错误：虚拟环境中找不到pip: $VENV_PIP"
    exit 1
fi

echo "执行: $VENV_PIP install -r $REQUIREMENTS_FILE"
echo ""

$VENV_PIP install -r "$REQUIREMENTS_FILE" || {
    echo ""
    echo "❌ 安装失败"
    echo ""
    echo "提示："
    echo "1. 检查网络连接"
    echo "2. 检查requirements.txt文件格式"
    exit 1
}

echo ""
echo "=================================================="
echo "  ✅ 安装完成！"
echo "=================================================="
echo ""
echo "虚拟环境位置："
echo "  $VENV_DIR"
echo ""
echo "激活虚拟环境："
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "使用虚拟环境运行："
echo "  $VENV_DIR/bin/python start.py init [目标项目目录]"
echo ""
echo "或者激活虚拟环境后直接运行："
echo "  python start.py init [目标项目目录]"
echo ""

