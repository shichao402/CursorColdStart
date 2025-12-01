#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台依赖安装脚本
使用 pyenv 和 pipenv 管理 Python 版本和依赖
"""

import sys
import subprocess
import platform
import shutil
from pathlib import Path


def check_command(cmd: str) -> bool:
    """检查命令是否可用"""
    return shutil.which(cmd) is not None


def check_pyenv():
    """检查并安装 pyenv"""
    if check_command("pyenv"):
        print("✅ pyenv 已安装")
        return True
    
    print("❌ pyenv 未安装")
    print()
    print("请安装 pyenv：")
    system = platform.system()
    if system == "Darwin":  # macOS
        print("  brew install pyenv")
        print("  然后添加到 ~/.zshrc 或 ~/.bash_profile：")
        print('    export PYENV_ROOT="$HOME/.pyenv"')
        print('    export PATH="$PYENV_ROOT/bin:$PATH"')
        print('    eval "$(pyenv init -)"')
    elif system == "Linux":
        print("  参考: https://github.com/pyenv/pyenv#installation")
    elif system == "Windows":
        print("  安装 pyenv-win: https://github.com/pyenv-win/pyenv-win")
    print()
    return False


def get_pipenv_command():
    """获取 pipenv 命令（优先使用命令，否则使用 python -m pipenv）"""
    if check_command("pipenv"):
        return ["pipenv"]
    # 尝试使用 python -m pipenv
    try:
        subprocess.run([sys.executable, "-m", "pipenv", "--version"], 
                      capture_output=True, check=True)
        return [sys.executable, "-m", "pipenv"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def check_pipenv():
    """检查并安装 pipenv"""
    pipenv_cmd = get_pipenv_command()
    if pipenv_cmd:
        print("✅ pipenv 已安装")
        return True
    
    print("❌ pipenv 未安装")
    print()
    print("正在安装 pipenv...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "pipenv"], 
                      check=True)
        print("✅ pipenv 安装成功")
        print()
        # 再次检查是否可用
        pipenv_cmd = get_pipenv_command()
        if not pipenv_cmd:
            print("⚠️  提示：pipenv 命令可能不在 PATH 中")
            print("  脚本将使用 'python -m pipenv' 方式运行")
            print("  或手动将用户 bin 目录添加到 PATH：")
            print("  macOS/Linux: ~/.local/bin 或 ~/Library/Python/3.9/bin")
            print("  Windows: %APPDATA%\\Python\\Python{version}\\Scripts")
        return True
    except subprocess.CalledProcessError:
        print("❌ pipenv 安装失败")
        print()
        print("请手动安装：")
        print("  pip install --user pipenv")
        return False


def check_python_version(script_dir: Path):
    """检查 Python 版本，使用 pyenv 确保版本匹配"""
    python_version_file = script_dir / ".python-version"
    
    if not python_version_file.exists():
        print("⚠️  警告：未找到 .python-version 文件")
        print("   当前 Python 版本:", sys.version.split()[0])
        return
    
    required_version = python_version_file.read_text().strip()
    print(f"📋 项目要求的 Python 版本: {required_version}")
    
    # 检查 pyenv 是否可用
    if not check_command("pyenv"):
        print("⚠️  警告：pyenv 未安装，无法自动切换 Python 版本")
        print(f"   当前 Python 版本: {sys.version.split()[0]}")
        print(f"   要求版本: {required_version}")
        print()
        print("建议：")
        print("  1. 安装 pyenv（见上方提示）")
        print(f"  2. 运行: pyenv install {required_version}")
        print(f"  3. 运行: pyenv local {required_version}")
        return
    
    # 检查 pyenv 是否已安装指定版本
    try:
        # 列出所有已安装的版本
        result = subprocess.run(
            ["pyenv", "versions", "--bare"],
            capture_output=True,
            text=True,
            check=True
        )
        installed_versions = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # 检查是否已安装所需版本（支持精确匹配和主次版本匹配）
        version_installed = False
        for ver in installed_versions:
            if ver == required_version or ver.startswith(required_version + '.'):
                version_installed = True
                break
        
        if not version_installed:
            print(f"⚠️  Python {required_version} 未安装")
            print()
            print(f"正在使用 pyenv 安装 Python {required_version}...")
            print("（这可能需要几分钟时间）")
            print()
            try:
                subprocess.run(
                    ["pyenv", "install", required_version],
                    check=True
                )
                print(f"✅ Python {required_version} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ Python {required_version} 安装失败")
                print(f"   退出码: {e.returncode}")
                print()
                print("请手动安装：")
                print(f"  pyenv install {required_version}")
                return
        
        # 设置本地版本
        print("设置本地 Python 版本...")
        try:
            subprocess.run(
                ["pyenv", "local", required_version],
                check=True,
                cwd=str(script_dir)
            )
            print(f"✅ 已设置本地 Python 版本为 {required_version}")
        except subprocess.CalledProcessError:
            print("⚠️  设置本地版本失败，继续使用当前版本")
        
        # 显示当前版本
        try:
            result = subprocess.run(
                ["pyenv", "version-name"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(script_dir)
            )
            current_version = result.stdout.strip()
            print(f"✅ 当前 Python 版本: {current_version}")
        except subprocess.CalledProcessError:
            pass
            
    except subprocess.CalledProcessError as e:
        print("⚠️  无法检查 pyenv 版本")
        print(f"   错误: {e}")
    except FileNotFoundError:
        print("⚠️  pyenv 命令不可用")


def install_with_pipenv(script_dir: Path):
    """使用 pipenv 安装依赖"""
    pipfile = script_dir / "Pipfile"
    
    if not pipfile.exists():
        print(f"❌ 错误：找不到 Pipfile: {pipfile}")
        sys.exit(1)
    
    # 获取 pipenv 命令
    pipenv_cmd = get_pipenv_command()
    if not pipenv_cmd:
        print("❌ 错误：无法找到 pipenv 命令")
        print()
        print("请确保 pipenv 已安装：")
        print("  pip install --user pipenv")
        print()
        print("或使用 python -m pipenv：")
        print(f"  {sys.executable} -m pipenv install")
        sys.exit(1)
    
    print("📦 使用 pipenv 安装依赖...")
    print()
    
    # 检查是否已有虚拟环境
    try:
        result = subprocess.run(
            pipenv_cmd + ["--venv"],
            capture_output=True,
            text=True,
            cwd=str(script_dir)
        )
        if result.returncode == 0:
            venv_path = result.stdout.strip()
            print(f"✅ 虚拟环境已存在: {venv_path}")
    except FileNotFoundError:
        pass
    
    # 安装依赖
    try:
        cmd_str = " ".join(pipenv_cmd + ["install"])
        print(f"执行: {cmd_str}")
        print()
        subprocess.run(
            pipenv_cmd + ["install"],
            cwd=str(script_dir),
            check=True
        )
        print()
        print("✅ 依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ 安装失败，退出码: {e.returncode}")
        print()
        print("提示：")
        print("1. 检查网络连接")
        print("2. 检查 Pipfile 文件格式")
        print("3. 确保 pyenv 已安装并配置正确")
        sys.exit(1)


def verify_installation(script_dir: Path):
    """验证安装"""
    print()
    print("🔍 验证安装...")
    
    pipenv_cmd = get_pipenv_command()
    if not pipenv_cmd:
        print("⚠️  无法验证安装（pipenv 命令不可用）")
        return False
    
    try:
        result = subprocess.run(
            pipenv_cmd + ["run", "python", "-c", "import jinja2; print(jinja2.__version__)"],
            capture_output=True,
            text=True,
            cwd=str(script_dir),
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ Jinja2 已安装，版本: {version}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Jinja2 未正确安装")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("  项目初始化系统 - 依赖安装")
    print("  使用 pyenv + pipenv")
    print("=" * 50)
    print()
    
    # 显示平台信息
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"平台: {platform.platform()}")
    print()
    
    script_dir = Path(__file__).parent.resolve()
    
    # 检查 pyenv
    print("[1/4] 检查 pyenv...")
    pyenv_installed = check_pyenv()
    if not pyenv_installed:
        print()
        response = input("是否继续安装（将使用系统 Python）？(y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("安装已取消")
            sys.exit(1)
    print()
    
    # 检查 Python 版本
    print("[2/4] 检查 Python 版本...")
    check_python_version(script_dir)
    print()
    
    # 检查 pipenv
    print("[3/4] 检查 pipenv...")
    if not check_pipenv():
        print("❌ pipenv 安装失败，无法继续")
        sys.exit(1)
    print()
    
    # 安装依赖
    print("[4/4] 安装依赖...")
    install_with_pipenv(script_dir)
    print()
    
    # 验证安装
    if verify_installation(script_dir):
        print()
        print("=" * 50)
        print("  ✅ 安装完成！")
        print("=" * 50)
        print()
        print("使用方式：")
        print("  使用包装脚本（推荐）：")
        print("    ./start [目标项目目录]")
        print("    或")
        print("    start.bat [目标项目目录]")
        print()
        print("  使用 pipenv 直接运行：")
        print("    pipenv run python coldstart.py [目标项目目录]")
        print()
        print("  激活虚拟环境：")
        print("    pipenv shell")
        print()
    else:
        print()
        print("=" * 50)
        print("  ⚠️  安装可能未完全成功")
        print("=" * 50)
        print()
        print("请手动验证：")
        print("  pipenv run python -c \"import jinja2; print(jinja2.__version__)\"")
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
