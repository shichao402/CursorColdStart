#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台依赖安装脚本
自动创建虚拟环境并安装所需的Python依赖
"""

import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("❌ 错误：需要Python 3.6或更高版本")
        print(f"当前版本：{sys.version}")
        sys.exit(1)
    print(f"✅ Python版本：{sys.version.split()[0]}")


def check_venv_module():
    """检查venv模块是否可用"""
    try:
        subprocess.run([sys.executable, "-m", "venv", "--help"], 
                      check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_venv(venv_dir: Path):
    """创建虚拟环境"""
    if venv_dir.exists():
        print(f"✅ 虚拟环境已存在: {venv_dir}")
        return True
    
    print(f"📦 创建虚拟环境: {venv_dir}")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], 
                      check=True)
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建虚拟环境失败，退出码: {e.returncode}")
        print()
        print("提示：")
        print("1. 确保Python版本 >= 3.6")
        print("2. 确保venv模块可用")
        sys.exit(1)


def get_venv_python(venv_dir: Path):
    """获取虚拟环境中的Python路径"""
    system = platform.system()
    if system == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def get_venv_pip(venv_dir: Path):
    """获取虚拟环境中的pip路径"""
    system = platform.system()
    if system == "Windows":
        return venv_dir / "Scripts" / "pip.exe"
    else:
        return venv_dir / "bin" / "pip"


def install_requirements(venv_dir: Path):
    """在虚拟环境中安装requirements.txt中的依赖"""
    script_dir = Path(__file__).parent.resolve()
    requirements_file = script_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ 错误：找不到 requirements.txt: {requirements_file}")
        sys.exit(1)
    
    venv_pip = get_venv_pip(venv_dir)
    if not venv_pip.exists():
        print(f"❌ 错误：虚拟环境中找不到pip: {venv_pip}")
        sys.exit(1)
    
    print(f"📦 安装依赖文件: {requirements_file}")
    print()
    
    cmd = [str(venv_pip), "install", "-r", str(requirements_file)]
    
    print(f"执行命令: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr and "WARNING" not in result.stderr:
            print(result.stderr, file=sys.stderr)
        print()
        print("✅ 依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ 安装失败，退出码: {e.returncode}")
        if e.stderr:
            print(e.stderr)
        if e.stdout:
            print(e.stdout)
        print()
        print("提示：")
        print("1. 检查网络连接")
        print("2. 检查requirements.txt文件格式")
        sys.exit(1)


def verify_installation(venv_dir: Path):
    """验证安装"""
    print()
    print("🔍 验证安装...")
    
    venv_python = get_venv_python(venv_dir)
    if not venv_python.exists():
        print(f"❌ 虚拟环境Python不存在: {venv_python}")
        return False
    
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "import jinja2; print(jinja2.__version__)"],
            check=True,
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        print(f"✅ Jinja2已安装，版本: {version}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Jinja2未正确安装")
        return False


def get_activate_script(venv_dir: Path):
    """获取激活脚本路径"""
    system = platform.system()
    if system == "Windows":
        return venv_dir / "Scripts" / "activate.bat"
    else:
        return venv_dir / "bin" / "activate"


def main():
    """主函数"""
    print("=" * 50)
    print("  项目初始化系统 - 依赖安装")
    print("=" * 50)
    print()
    
    # 显示平台信息
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"平台: {platform.platform()}")
    print()
    
    # 确定虚拟环境目录
    script_dir = Path(__file__).parent.resolve()
    venv_dir = script_dir / ".venv"
    
    # 检查Python版本
    print("[1/5] 检查Python版本...")
    check_python_version()
    print()
    
    # 检查venv模块
    print("[2/5] 检查venv模块...")
    if not check_venv_module():
        print("❌ venv模块不可用")
        print()
        print("请安装venv模块：")
        if system == "Windows":
            print("  python -m ensurepip --upgrade")
        else:
            print("  python3 -m ensurepip --upgrade")
            print("  或使用系统包管理器安装python3-venv")
        sys.exit(1)
    print("✅ venv模块可用")
    print()
    
    # 创建虚拟环境
    print("[3/5] 创建虚拟环境...")
    create_venv(venv_dir)
    print()
    
    # 安装依赖
    print("[4/5] 安装依赖...")
    install_requirements(venv_dir)
    print()
    
    # 验证安装
    print("[5/5] 验证安装...")
    if verify_installation(venv_dir):
        activate_script = get_activate_script(venv_dir)
        print()
        print("=" * 50)
        print("  ✅ 安装完成！")
        print("=" * 50)
        print()
        print("虚拟环境位置：")
        print(f"  {venv_dir}")
        print()
        print("激活虚拟环境：")
        if system == "Windows":
            print(f"  {activate_script}")
            print("  或: .venv\\Scripts\\activate")
        else:
            print(f"  source {activate_script}")
            print("  或: source .venv/bin/activate")
        print()
        print("使用虚拟环境运行：")
        venv_python = get_venv_python(venv_dir)
        print(f"  {venv_python} start.py init [目标项目目录]")
        print()
        print("或者激活虚拟环境后直接运行：")
        print("  python start.py init [目标项目目录]")
        print()
    else:
        print()
        print("=" * 50)
        print("  ⚠️  安装可能未完全成功")
        print("=" * 50)
        print()
        print("请手动验证：")
        venv_python = get_venv_python(venv_dir)
        print(f"  {venv_python} -c \"import jinja2; print(jinja2.__version__)\"")
        print()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

