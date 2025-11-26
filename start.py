#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目初始化系统主脚本
支持跨平台（Windows/Mac/Linux）
"""

import json
import sys
import os
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from jinja2 import Template
except ImportError:
    print("错误：需要安装Jinja2模板引擎")
    print()
    print("请先运行安装脚本创建虚拟环境并安装依赖：")
    print("  python install.py")
    print()
    print("或者手动安装：")
    print("  pip install jinja2")
    sys.exit(1)


class ProjectInitializer:
    """项目初始化器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.project_init_dir = self.project_root / "project-init"
        self.staging_dir = self.project_root / ".cold-start-staging"
        self.config_file = self.staging_dir / "config.json"
        self.venv_dir = self.project_root / ".venv"
        
        # 检查project-init目录
        if not self.project_init_dir.exists():
            raise FileNotFoundError(f"找不到 project-init 目录: {self.project_init_dir}")
        
        # 检查虚拟环境（可选，如果不存在会提示）
        self._check_venv()
    
    def _check_venv(self):
        """检查虚拟环境是否存在（可选检查）"""
        if not self.venv_dir.exists():
            # 虚拟环境不存在不是致命错误，只是提示
            pass
    
    def load_options(self) -> Dict[str, Any]:
        """加载选项配置文件"""
        options_file = self.project_init_dir / "options.json"
        with open(options_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_config(self) -> Dict[str, Any]:
        """加载项目配置文件"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """保存项目配置文件"""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def read_project_description(self) -> str:
        """读取项目描述文档"""
        desc_file_path = self.config_file.parent / "plans" / "01-project-description.md"
        if desc_file_path.exists():
            with open(desc_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def get_placeholder_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成所有占位符的值"""
        lang = config.get('language', 'dart')
        framework = config.get('framework', 'flutter')
        build_tool = config.get('buildTool', 'Flutter CLI')
        
        values = {
            'PROJECT_NAME': config.get('projectName', '未命名项目'),
            'PROGRAMMING_LANGUAGE': config.get('languageName', 'Dart'),
            'FRAMEWORK': framework,
            'BUILD_TOOL': build_tool,
            'CODE_LANGUAGE': config.get('codeLanguage', lang),
            'TARGET_PLATFORMS': ', '.join(config.get('platforms', ['web'])),
            'MODULE_NAME': '应用',
            'MODULE_PATH': '**',
            'GENERATION_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # 日志相关
            'LOGGER_SERVICE_CLASS': 'Logger',
            'LOG_FILE_PATH': 'logs/app.log',
            'LOG_COLLECT_SCRIPT_PATH': 'scripts/collect_logs.sh',
            'LOG_COLLECT_COMMAND': './scripts/collect_logs.sh',
        }
        
        # 根据语言设置额外的API方法
        if lang in ['typescript', 'javascript']:
            values['ADDITIONAL_API_METHODS'] = '- 警告日志：`logger.warn(\'警告\', tag: \'TAG\')`'
        else:
            values['ADDITIONAL_API_METHODS'] = ''
        
        # 根据框架生成部署相关占位符
        deploy_templates = self._get_deploy_templates(framework)
        values.update(deploy_templates)
        
        return values
    
    def _get_deploy_templates(self, framework: str) -> Dict[str, str]:
        """根据框架获取部署模板"""
        templates = {
            'flutter': {
                'DEPLOY_SCRIPTS_DESCRIPTION': """**部署脚本：** `scripts/deploy.sh`

此脚本用于部署Flutter应用到目标平台。AI必须使用此脚本进行部署，不得手动执行flutter命令。

**脚本功能：**
- 自动检测连接的设备
- 构建应用
- 安装到设备
- 启动应用""",
                'DEPLOY_STEPS_DESCRIPTION': """1. **使用部署脚本部署应用**
   - 执行：`./scripts/deploy.sh`
   - 脚本会自动构建、安装并启动应用""",
                'DEPLOY_COMMANDS_DESCRIPTION': """**部署命令：**

```bash
./scripts/deploy.sh
```

此脚本会：
- 检查Flutter环境
- 构建应用（`flutter build`）
- 安装到设备（`flutter install`）
- 启动应用（`flutter run`）"""
            },
            'react': {
                'DEPLOY_SCRIPTS_DESCRIPTION': """**部署脚本：** `scripts/deploy.sh`

此脚本用于构建和部署Web应用。AI必须使用此脚本进行部署，不得手动执行npm/yarn命令。

**脚本功能：**
- 安装依赖
- 构建应用
- 启动开发服务器或部署到生产环境""",
                'DEPLOY_STEPS_DESCRIPTION': """1. **使用部署脚本部署应用**
   - 执行：`./scripts/deploy.sh`
   - 脚本会自动构建并启动应用""",
                'DEPLOY_COMMANDS_DESCRIPTION': """**部署命令：**

```bash
./scripts/deploy.sh
```

此脚本会：
- 安装依赖（`npm install` 或 `yarn install`）
- 构建应用（`npm run build` 或 `yarn build`）
- 启动开发服务器（`npm run dev` 或 `yarn dev`）"""
            },
            'django': {
                'DEPLOY_SCRIPTS_DESCRIPTION': """**部署脚本：** `scripts/deploy.sh`

此脚本用于部署Python应用。AI必须使用此脚本进行部署，不得手动执行pip/python命令。

**脚本功能：**
- 安装依赖
- 运行数据库迁移
- 启动应用服务器""",
                'DEPLOY_STEPS_DESCRIPTION': """1. **使用部署脚本部署应用**
   - 执行：`./scripts/deploy.sh`
   - 脚本会自动安装依赖并启动应用""",
                'DEPLOY_COMMANDS_DESCRIPTION': """**部署命令：**

```bash
./scripts/deploy.sh
```

此脚本会：
- 安装依赖（`pip install -r requirements.txt`）
- 运行数据库迁移（如适用）
- 启动应用服务器（`python manage.py runserver` 或 `uvicorn app:app`）"""
            }
        }
        
        # 默认模板
        default = {
            'DEPLOY_SCRIPTS_DESCRIPTION': """**部署脚本：** `scripts/deploy.sh`

此脚本用于部署应用。AI必须使用此脚本进行部署，不得手动执行构建命令。

**脚本功能：**
- 构建应用
- 部署到目标环境""",
            'DEPLOY_STEPS_DESCRIPTION': """1. **使用部署脚本部署应用**
   - 执行：`./scripts/deploy.sh`
   - 脚本会自动构建并部署应用""",
            'DEPLOY_COMMANDS_DESCRIPTION': """**部署命令：**

```bash
./scripts/deploy.sh
```

此脚本会构建并部署应用。"""
        }
        
        return templates.get(framework, default)
    
    def stage_init(self, target_dir: Optional[str] = None):
        """阶段1：初始化"""
        print("=" * 40)
        print("  阶段1：初始化")
        print("=" * 40)
        print()
        
        # 1.1 创建临时目录
        print("[1.1] 创建临时工作目录...")
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir(parents=True)
        print(f"✅ 临时目录: {self.staging_dir}")
        print()
        
        # 1.2 拷贝配置文件模板
        print("[1.2] 拷贝配置文件模板...")
        template_config = self.project_init_dir / "config.template.json"
        shutil.copy(template_config, self.config_file)
        print(f"✅ 配置文件: {self.config_file}")
        print()
        
        # 1.3 交互式收集信息
        print("[1.3] 交互式收集项目信息...")
        print()
        
        config = self.load_config()
        options = self.load_options()
        
        # 收集项目名称
        project_name = input("项目名称: ").strip() or "未命名项目"
        config['projectName'] = project_name
        
        # 拷贝项目描述模板
        print()
        print("[1.3.1] 拷贝项目描述模板文档...")
        desc_template = self.project_init_dir / "templates" / "plans" / "common" / "01-project-description.md"
        desc_output = self.staging_dir / "plans" / "01-project-description.md"
        desc_output.parent.mkdir(parents=True, exist_ok=True)
        if desc_template.exists():
            shutil.copy(desc_template, desc_output)
            print(f"✅ 项目描述模板已生成: plans/01-project-description.md")
            print("提示：请在阶段2之前编辑此文件，补充项目描述信息")
        print()
        
        # 收集编程语言
        print("编程语言：")
        languages = options.get('languages', [])
        for i, lang in enumerate(languages, 1):
            print(f"  {i}) {lang.get('name', lang.get('id', ''))}")
        
        lang_choice = input(f"请选择 (1-{len(languages)}，默认1): ").strip() or "1"
        try:
            lang_idx = int(lang_choice) - 1
            if 0 <= lang_idx < len(languages):
                selected_lang = languages[lang_idx]
            else:
                selected_lang = languages[0]
        except ValueError:
            selected_lang = languages[0]
        
        config['language'] = selected_lang['id']
        config['languageName'] = selected_lang['name']
        config['codeLanguage'] = selected_lang.get('codeLanguage', selected_lang['id'])
        
        # 收集框架
        print()
        print("框架/平台：")
        frameworks = selected_lang.get('frameworks', [])
        if len(frameworks) == 1:
            selected_fw = frameworks[0]
            print(f"  自动选择: {selected_fw['name']}")
        else:
            for i, fw in enumerate(frameworks, 1):
                print(f"  {i}) {fw['name']}")
            fw_choice = input(f"请选择 (1-{len(frameworks)}，默认1): ").strip() or "1"
            try:
                fw_idx = int(fw_choice) - 1
                if 0 <= fw_idx < len(frameworks):
                    selected_fw = frameworks[fw_idx]
                else:
                    selected_fw = frameworks[0]
            except ValueError:
                selected_fw = frameworks[0]
        
        config['framework'] = selected_fw['id']
        config['buildTool'] = selected_fw['buildTool']
        
        # 收集平台
        print()
        print("目标平台（可多选，用空格分隔，如：1 3 4）：")
        platforms_list = options.get('platforms', [])
        for i, platform in enumerate(platforms_list, 1):
            print(f"  {i}) {platform['name']}")
        
        platform_choices = input("请选择: ").strip().split()
        selected_platforms = []
        for choice in platform_choices:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(platforms_list):
                    selected_platforms.append(platforms_list[idx]['id'])
            except ValueError:
                pass
        
        if not selected_platforms:
            # 使用默认平台
            default_platform = next((p['id'] for p in platforms_list if p.get('default')), 'web')
            selected_platforms = [default_platform]
        
        config['platforms'] = selected_platforms
        self.save_config(config)
        
        print()
        print("✅ 项目信息收集完成")
        print()
        
        # 1.4 生成初始计划文件
        print("[1.4] 生成初始计划文件...")
        plan_template = self.project_init_dir / "templates" / "plans" / "common" / "00-project-init-plan.mdc"
        plan_output = self.staging_dir / "plans" / "00-project-init-plan.mdc"
        plan_output.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用Jinja2渲染模板
        with open(plan_template, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        values = self.get_placeholder_values(config)
        rendered = template.render(**values)
        
        with open(plan_output, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print("✅ 初始计划文件已生成: plans/00-project-init-plan.mdc")
        print()
        
        print("=" * 40)
        print("  ✅ 阶段1完成！")
        print("=" * 40)
        print()
        print("下一步操作：")
        print()
        print("1. 📝 审查和修改以下文件：")
        print(f"   - 配置文件: {self.config_file}")
        print(f"   - 计划文件: {self.staging_dir / 'plans' / '00-project-init-plan.mdc'}")
        print(f"   - 项目描述: {self.staging_dir / 'plans' / '01-project-description.md'}")
        print()
        print("2. ✏️  请编辑项目描述文档，补充详细的项目信息")
        print()
        print("3. ✅ 确认无误后，执行阶段2：")
        print("   python start.py process")
        print()
    
    def stage_process(self):
        """阶段2：处理"""
        if not self.config_file.exists():
            print("❌ 错误：配置文件不存在")
            print("请先运行阶段1：python start.py init")
            sys.exit(1)
        
        print("=" * 40)
        print("  阶段2：处理")
        print("=" * 40)
        print()
        
        # 2.1 读取配置
        print("[2.1] 读取配置文件...")
        config = self.load_config()
        values = self.get_placeholder_values(config)
        
        print("✅ 配置文件读取完成")
        print(f"  项目名称: {values['PROJECT_NAME']}")
        print(f"  语言: {values['PROGRAMMING_LANGUAGE']}")
        print(f"  框架: {values['FRAMEWORK']}")
        print(f"  平台: {values['TARGET_PLATFORMS']}")
        print()
        
        # 2.2 处理模板文件
        print("[2.2] 处理模板文件...")
        
        # 处理计划文件
        print("  处理计划文件...")
        plan_output = self.staging_dir / "plans" / "00-project-init-plan.mdc"
        if not plan_output.exists():
            plan_template = self.project_init_dir / "templates" / "plans" / "common" / "00-project-init-plan.mdc"
            shutil.copy(plan_template, plan_output)
        
        # 读取模板内容并使用Jinja2渲染
        plan_template_file = self.project_init_dir / "templates" / "plans" / "common" / "00-project-init-plan.mdc"
        with open(plan_template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        rendered = template.render(**values)
        with open(plan_output, 'w', encoding='utf-8') as f:
            f.write(rendered)
        print("    ✅ 计划文件已处理")
        
        # 确保项目描述文档存在
        desc_template = self.project_init_dir / "templates" / "plans" / "common" / "01-project-description.md"
        desc_output = self.staging_dir / "plans" / "01-project-description.md"
        if not desc_output.exists() and desc_template.exists():
            shutil.copy(desc_template, desc_output)
            print("    ✅ 项目描述文档已生成")
        
        # 处理规则文件
        print("  生成规则文件...")
        rules_dir = self.staging_dir / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rule_counter = 0
        files_to_render = []
        
        # 通用规则
        print("    处理通用规则...")
        common_dir = self.project_init_dir / "templates" / "rules" / "common"
        for template_file in common_dir.glob("*.template"):
            base_name = template_file.stem
            output_file = rules_dir / base_name
            files_to_render.append((template_file, output_file))
            rule_counter += 1
            print(f"      ✅ {base_name}")
        
        # 语言特定规则
        lang = config.get('language', 'dart')
        lang_template = self.project_init_dir / "templates" / "rules" / "languages" / f"{lang}.mdc.template"
        if lang_template.exists():
            print(f"    处理语言特定规则: {config.get('languageName', lang)}...")
            options = self.load_options()
            lang_priority = options.get('rulePriorities', {}).get('languages', 10)
            output_file = rules_dir / f"{lang_priority}-{lang}.mdc"
            files_to_render.append((lang_template, output_file))
            rule_counter += 1
            print(f"      ✅ {lang_priority}-{lang}.mdc")
        
        # 框架特定规则
        framework = config.get('framework', 'flutter')
        fw_template = self.project_init_dir / "templates" / "rules" / "frameworks" / f"{framework}.mdc.template"
        if fw_template.exists():
            print(f"    处理框架特定规则: {framework}...")
            options = self.load_options()
            fw_priority = options.get('rulePriorities', {}).get('frameworks', 20)
            output_file = rules_dir / f"{fw_priority}-{framework}.mdc"
            files_to_render.append((fw_template, output_file))
            rule_counter += 1
            print(f"      ✅ {fw_priority}-{framework}.mdc")
        
        # 平台特定规则
        print("    处理平台特定规则...")
        platforms = config.get('platforms', [])
        options = self.load_options()
        platform_priority = options.get('rulePriorities', {}).get('platforms', 30)
        platform_counter = platform_priority
        for platform in platforms:
            platform_template = self.project_init_dir / "templates" / "rules" / "platforms" / f"{platform}.mdc.template"
            if platform_template.exists():
                output_file = rules_dir / f"{platform_counter}-{platform}.mdc"
                files_to_render.append((platform_template, output_file))
                rule_counter += 1
                print(f"      ✅ {platform_counter}-{platform}.mdc")
                platform_counter += 1
        
        # 使用Jinja2渲染所有规则文件
        print("    替换占位符...")
        for template_file, output_file in files_to_render:
            # 读取模板内容
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 使用Jinja2渲染（模板中已使用 {% if %} 处理空值）
            template = Template(template_content)
            rendered = template.render(**values)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)
        
        print("✅ 模板处理完成")
        print()
        
        # 2.3 显示生成的文件
        print("[2.3] 生成的文件预览...")
        print()
        print("计划文件：")
        for plan_file in (self.staging_dir / "plans").glob("*.mdc"):
            print(f"  📋 {plan_file.name}")
        print()
        print(f"规则文件（共 {rule_counter} 个）：")
        for rule_file in rules_dir.glob("*.mdc"):
            print(f"  📋 {rule_file.name}")
        print()
        
        print("=" * 40)
        print("  ✅ 阶段2完成！")
        print("=" * 40)
        print()
        print("下一步操作：")
        print()
        print("1. 📝 审查临时目录中的文件：")
        print(f"   - 计划文件: {self.staging_dir / 'plans'}")
        print(f"   - 规则文件: {self.staging_dir / 'rules'}")
        print()
        print("2. ✅ 确认无误后，执行阶段3：")
        print("   python start.py export <目标项目目录>")
        print()
    
    def stage_export(self, target_dir: str):
        """阶段3：导出"""
        if not self.staging_dir.exists():
            print("❌ 错误：临时目录不存在")
            print("请先运行阶段1和阶段2")
            sys.exit(1)
        
        target_path = Path(target_dir).resolve()
        target_path.mkdir(parents=True, exist_ok=True)
        
        print("=" * 40)
        print("  阶段3：导出")
        print("=" * 40)
        print()
        print(f"目标目录：{target_path}")
        print()
        
        # 创建目标目录结构
        plans_dir = target_path / ".cursor" / "plans"
        rules_dir = target_path / ".cursor" / "rules"
        plans_dir.mkdir(parents=True, exist_ok=True)
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制计划文件
        staging_plans = self.staging_dir / "plans"
        if staging_plans.exists():
            for plan_file in staging_plans.glob("*.mdc"):
                shutil.copy(plan_file, plans_dir / plan_file.name)
            print("✅ 计划文件已复制")
        
        # 复制规则文件
        staging_rules = self.staging_dir / "rules"
        if staging_rules.exists():
            for rule_file in staging_rules.glob("*.mdc"):
                shutil.copy(rule_file, rules_dir / rule_file.name)
            print("✅ 规则文件已复制")
        
        # 显示生成的文件
        print()
        print("生成的文件：")
        for plan_file in plans_dir.glob("*.mdc"):
            print(f"  📋 {plan_file.name}")
        for rule_file in rules_dir.glob("*.mdc"):
            print(f"  📋 {rule_file.name}")
        
        print()
        print("=" * 40)
        print("  ✅ 阶段3完成！文件已导出到目标项目")
        print("=" * 40)
        print()
        print("下一步操作：")
        print()
        print("1. 🤖 在 Cursor 中告诉 AI 助手：")
        print("   开始项目初始化")
        print()
        
        # 清理临时目录
        cleanup = input("是否清理临时目录？(y/n): ").strip().lower()
        if cleanup == 'y':
            shutil.rmtree(self.staging_dir)
            print("✅ 临时目录已清理")
        else:
            print(f"临时目录保留在: {self.staging_dir}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='项目AI冷启动初始化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式：
  阶段1 - 初始化：  python start.py init [目标项目目录]
  阶段2 - 处理：    python start.py process
  阶段3 - 导出：    python start.py export <目标项目目录>
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # init命令
    init_parser = subparsers.add_parser('init', help='阶段1：初始化')
    init_parser.add_argument('target_dir', nargs='?', help='目标项目目录（可选）')
    
    # process命令
    subparsers.add_parser('process', help='阶段2：处理')
    
    # export命令
    export_parser = subparsers.add_parser('export', help='阶段3：导出')
    export_parser.add_argument('target_dir', help='目标项目目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 获取项目根目录（脚本所在目录）
    script_dir = Path(__file__).parent.resolve()
    initializer = ProjectInitializer(script_dir)
    
    try:
        if args.command == 'init':
            initializer.stage_init(args.target_dir)
        elif args.command == 'process':
            initializer.stage_process()
        elif args.command == 'export':
            if not args.target_dir:
                print("❌ 错误：必须指定目标项目目录")
                sys.exit(1)
            initializer.stage_export(args.target_dir)
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

