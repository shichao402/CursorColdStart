#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主入口模块
"""

import argparse
from pathlib import Path
from .initializer import ProjectInitializer
from .commands import InteractiveCommandSystem

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='项目AI冷启动初始化系统 - 交互式脚手架',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式：
  coldstart [命令] [目标项目目录]
  或
  python coldstart.py [命令] [目标项目目录]
  
示例：
  coldstart <目标项目目录>              # 启动交互式模式
  coldstart init-config <目标项目目录>  # 直接执行命令
  
启动后进入交互式命令模式，输入 'help' 查看可用命令。

命令结构：
  init          - 项目初始化流程
    process     - 阶段2：处理模板文件
    export      - 阶段3：导出到目标项目
  inject        - 模块化规则注入
  init-config   - 为现有项目补充配置信息
  add-module    - 快速创建新模块规则
  extract-rules - 从目标项目提取规则并反哺
  help          - 显示帮助信息
  exit          - 退出程序
        """
    )
    
    parser.add_argument('command_or_dir', nargs='?', help='命令名称或目标项目目录')
    parser.add_argument('target_dir', nargs='?', help='目标项目目录（当第一个参数是命令时）')
    
    args = parser.parse_args()
    
    # 获取项目根目录（coldstart.py 所在目录）
    # coldstart/main.py 的父目录的父目录就是项目根目录
    script_dir = Path(__file__).parent.parent.resolve()
    initializer = ProjectInitializer(script_dir)
    
    # 检查第一个参数是否是命令
    direct_commands = ['init-config', 'inject', 'extract-rules', 'add-module', 'update-rules']
    
    if args.command_or_dir in direct_commands:
        # 直接执行命令
        cmd_system = InteractiveCommandSystem(initializer, args.target_dir)
        # 直接执行命令，不进入交互式循环
        cmd_name = args.command_or_dir
        cmd_args = [args.target_dir] if args.target_dir else []
        
        print("=" * 50)
        print("  项目AI冷启动初始化系统 - 交互式脚手架")
        print("=" * 50)
        print()
        
        if args.target_dir:
            print(f"目标项目目录: {args.target_dir}")
        else:
            print("⚠️  警告：未指定目标项目目录")
            print("此命令需要目标项目目录")
            print()
            print("使用方法：")
            print(f"  python start.py {cmd_name} <目标项目目录>")
            return
        
        print()
        
        # 执行命令
        handler = cmd_system.commands['root'].get(cmd_name, {}).get('handler')
        if handler:
            try:
                handler(cmd_args)
            except Exception as e:
                print(f"❌ 执行命令时出错: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ 错误：找不到命令 '{cmd_name}' 的处理器")
    else:
        # 进入交互式模式
        target_dir = args.command_or_dir  # 第一个参数是目标目录
        cmd_system = InteractiveCommandSystem(initializer, target_dir)
        cmd_system.run()


if __name__ == '__main__':
    main()

