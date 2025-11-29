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
from typing import Dict, Any, List, Optional, Callable
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
            
            # GitHub Action 相关
            'ENABLE_GITHUB_ACTION': config.get('enableGitHubAction', False),
            
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
    
    def _detect_rule_type(self, rule_filename: str) -> str:
        """检测规则类型"""
        if rule_filename.startswith('00-') or 'core' in rule_filename.lower():
            return 'common'
        elif any(x in rule_filename for x in ['10-', '11-', '12-', '13-', '14-', '15-']):
            return 'language'
        elif any(x in rule_filename for x in ['20-', '21-', '22-', '23-', '24-', '25-']):
            return 'framework'
        elif any(x in rule_filename for x in ['30-', '31-', '32-', '33-', '34-', '35-']):
            return 'platform'
        elif any(x in rule_filename for x in ['40-', '41-', '42-', '43-', '44-', '45-']):
            return 'module'
        else:
            return 'unknown'
    
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
        
        # 收集是否启用 GitHub Action
        print()
        github_action_input = input("是否启用 GitHub Action？(y/n，默认n): ").strip().lower()
        config['enableGitHubAction'] = github_action_input == 'y' or github_action_input == 'yes'
        
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
        implemented_rules = []
        if staging_rules.exists():
            for rule_file in staging_rules.glob("*.mdc"):
                shutil.copy(rule_file, rules_dir / rule_file.name)
                implemented_rules.append({
                    'name': rule_file.name,
                    'path': f".cursor/rules/{rule_file.name}",
                    'type': self._detect_rule_type(rule_file.name)
                })
            print("✅ 规则文件已复制")
        
        # 记录已实施的计划文件
        implemented_plans = []
        if staging_plans.exists():
            for plan_file in staging_plans.glob("*.mdc"):
                implemented_plans.append({
                    'name': plan_file.name,
                    'path': f".cursor/plans/{plan_file.name}"
                })
        
        # 创建 .cold-start 目录
        cold_start_dir = target_path / ".cold-start"
        cold_start_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取项目配置
        config = self.load_config()
        values = self.get_placeholder_values(config)
        
        # 创建完整的项目配置文件
        project_info = {
            'version': '1.0.0',
            'generatedAt': datetime.now().isoformat(),
            'generatedBy': 'CursorColdStart',
            'project': {
                'name': config.get('projectName', '未命名项目'),
                'description': config.get('projectDescription', ''),
                'rootPath': str(target_path)
            },
            'technology': {
                'language': {
                    'id': config.get('language', 'dart'),
                    'name': config.get('languageName', 'Dart'),
                    'codeLanguage': config.get('codeLanguage', 'dart')
                },
                'framework': {
                    'id': config.get('framework', 'flutter'),
                    'name': values.get('FRAMEWORK', 'Flutter'),
                    'buildTool': config.get('buildTool', 'Flutter CLI')
                },
                'platforms': [
                    {'id': p, 'name': p.capitalize()} 
                    for p in config.get('platforms', ['web'])
                ]
            },
            'modules': {
                'injected': [],
                'available': []
            },
            'files': {
                'plans': implemented_plans,
                'rules': implemented_rules
            },
            'config': {
                'enableGitHubAction': config.get('enableGitHubAction', False),
                'logService': {
                    'class': values.get('LOGGER_SERVICE_CLASS', 'Logger'),
                    'filePath': values.get('LOG_FILE_PATH', 'logs/app.log'),
                    'collectScript': values.get('LOG_COLLECT_SCRIPT_PATH', 'scripts/collect_logs.sh')
                }
            }
        }
        
        # 保存项目配置文件
        config_file = cold_start_dir / "project.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        print("✅ 项目配置文件已创建: .cold-start/project.json")
        
        # 创建 README 文件说明
        readme_file = cold_start_dir / "README.md"
        readme_content = f"""# ColdStart 项目配置

此目录由 CursorColdStart 脚手架自动创建和管理。

## 目录说明

- `project.json` - 项目完整配置信息
  - 项目基本信息
  - 技术方案（语言、框架、平台）
  - 已注入的模块列表
  - 已实施的文件列表

## 重要提示

⚠️ **请勿手动修改此目录中的文件**

此目录由 CursorColdStart 脚手架自动管理：
- 使用 `inject` 命令注入模块时，会自动更新此配置
- 使用 `extract-rules` 命令提取规则时，会读取此配置

如需修改项目配置，请使用 CursorColdStart 脚手架的命令。

## 项目信息

- **项目名称：** {project_info['project']['name']}
- **技术栈：** {project_info['technology']['language']['name']} + {project_info['technology']['framework']['name']}
- **目标平台：** {', '.join([p['name'] for p in project_info['technology']['platforms']])}
- **初始化时间：** {project_info['generatedAt']}
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ 说明文件已创建: .cold-start/README.md")
        
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
    
    def stage_inject(self, target_dir: str):
        """模块注入：向现有项目注入模块化规则"""
        target_path = Path(target_dir).resolve()
        
        if not target_path.exists():
            print(f"❌ 错误：目标项目目录不存在: {target_path}")
            sys.exit(1)
        
        print("=" * 40)
        print("  模块化规则注入")
        print("=" * 40)
        print()
        print(f"目标项目：{target_path}")
        print()
        
        # 1. 读取目标项目配置
        print("[1] 读取目标项目配置...")
        project_config_file = target_path / ".cold-start" / "project.json"
        project_info = None
        
        if project_config_file.exists():
            with open(project_config_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
            print("✅ 项目配置读取完成")
            print(f"  项目名称: {project_info.get('project', {}).get('name', '未知')}")
            print(f"  语言: {project_info.get('technology', {}).get('language', {}).get('name', '未知')}")
            print(f"  框架: {project_info.get('technology', {}).get('framework', {}).get('name', '未知')}")
        else:
            # 尝试从旧配置读取
            old_config_file = target_path / ".cold-start-config.json"
            if old_config_file.exists():
                with open(old_config_file, 'r', encoding='utf-8') as f:
                    old_config = json.load(f)
                # 转换为新格式
                values = self.get_placeholder_values(old_config)
                project_info = {
                    'version': '1.0.0',
                    'generatedAt': datetime.now().isoformat(),
                    'generatedBy': 'CursorColdStart',
                    'project': {
                        'name': old_config.get('projectName', '未命名项目'),
                        'rootPath': str(target_path)
                    },
                    'technology': {
                        'language': {
                            'id': old_config.get('language', 'dart'),
                            'name': old_config.get('languageName', 'Dart'),
                            'codeLanguage': old_config.get('codeLanguage', 'dart')
                        },
                        'framework': {
                            'id': old_config.get('framework', 'flutter'),
                            'name': values.get('FRAMEWORK', 'Flutter'),
                            'buildTool': old_config.get('buildTool', 'Flutter CLI')
                        },
                        'platforms': [
                            {'id': p, 'name': p.capitalize()} 
                            for p in old_config.get('platforms', ['web'])
                        ]
                    },
                    'modules': {'injected': [], 'available': []},
                    'files': {'plans': [], 'rules': []},
                    'config': old_config
                }
                print("✅ 从旧配置转换完成")
            else:
                # 尝试从规则文件读取
                project_config = self._read_project_config(target_path)
                if project_config:
                    project_info = {
                        'version': '1.0.0',
                        'generatedAt': datetime.now().isoformat(),
                        'generatedBy': 'CursorColdStart',
                        'project': {
                            'name': project_config.get('PROJECT_NAME', '未命名项目'),
                            'rootPath': str(target_path)
                        },
                        'technology': {
                            'language': {
                                'id': project_config.get('CODE_LANGUAGE', 'dart'),
                                'name': project_config.get('PROGRAMMING_LANGUAGE', 'Dart'),
                                'codeLanguage': project_config.get('CODE_LANGUAGE', 'dart')
                            },
                            'framework': {
                                'id': project_config.get('FRAMEWORK', 'flutter').lower(),
                                'name': project_config.get('FRAMEWORK', 'Flutter'),
                                'buildTool': 'Unknown'
                            },
                            'platforms': []
                        },
                        'modules': {'injected': [], 'available': []},
                        'files': {'plans': [], 'rules': []},
                        'config': {}
                    }
                    print("✅ 从规则文件读取完成")
                else:
                    print("❌ 错误：无法读取项目配置")
                    print("提示：目标项目必须是通过本脚手架创建的项目")
                    sys.exit(1)
        
        print()
        
        # 2. 列出可用模块
        print("[2] 列出可用模块...")
        modules_dir = self.project_init_dir / "templates" / "modules"
        available_modules = self._list_available_modules(modules_dir)
        
        if not available_modules:
            print("❌ 错误：没有找到可用的模块")
            sys.exit(1)
        
        print("可用模块：")
        for i, module_info in enumerate(available_modules, 1):
            print(f"  {i}) {module_info['name']} - {module_info['description']}")
        print()
        
        # 3. 选择模块
        module_choice = input(f"请选择要注入的模块 (1-{len(available_modules)}): ").strip()
        try:
            module_idx = int(module_choice) - 1
            if 0 <= module_idx < len(available_modules):
                selected_module = available_modules[module_idx]
            else:
                print("❌ 错误：无效的选择")
                sys.exit(1)
        except ValueError:
            print("❌ 错误：请输入数字")
            sys.exit(1)
        
        print(f"✅ 已选择模块: {selected_module['name']}")
        print()
        
        # 4. 检查模块兼容性
        print("[3] 检查模块兼容性...")
        module_config = self._load_module_config(selected_module['path'])
        if not self._check_module_compatibility(module_config, project_info):
            print("❌ 错误：模块与项目不兼容")
            sys.exit(1)
        print("✅ 模块兼容性检查通过")
        print()
        
        # 5. 收集模块参数
        print("[4] 收集模块参数...")
        module_params = self._collect_module_parameters(module_config, project_info)
        print("✅ 模块参数收集完成")
        print()
        
        # 6. 渲染并注入模块规则
        print("[5] 渲染并注入模块规则...")
        injected_files = self._inject_module_rules(target_path, selected_module, module_config, project_info, module_params)
        print("✅ 模块规则注入完成")
        print()
        
        # 7. 更新项目配置文件
        print("[6] 更新项目配置文件...")
        self._update_project_config(target_path, project_info, selected_module, module_config, injected_files)
        print("✅ 项目配置已更新")
        print()
        
        print("=" * 40)
        print("  ✅ 模块注入完成！")
        print("=" * 40)
        print()
        print("下一步操作：")
        print()
        print("1. 🤖 切换到目标项目，在 Cursor 中告诉 AI 助手：")
        print(f"   开始实现 {selected_module['name']} 模块")
        print()
        print("2. 📋 AI 将根据注入的规则逐步完成模块的实现")
        print()
    
    def _read_project_config(self, target_path: Path) -> Optional[Dict[str, Any]]:
        """从目标项目读取配置参数（兼容旧版本）"""
        # 先尝试读取新的配置文件
        project_config_file = target_path / ".cold-start" / "project.json"
        if project_config_file.exists():
            with open(project_config_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
                return {
                    'PROJECT_NAME': project_info.get('project', {}).get('name', '未命名项目'),
                    'PROGRAMMING_LANGUAGE': project_info.get('technology', {}).get('language', {}).get('name', '未知'),
                    'CODE_LANGUAGE': project_info.get('technology', {}).get('language', {}).get('codeLanguage', 'unknown'),
                    'FRAMEWORK': project_info.get('technology', {}).get('framework', {}).get('name', '未知'),
                    'CODE_LANGUAGE_EXT': self._get_language_ext(project_info.get('technology', {}).get('language', {}).get('codeLanguage', 'unknown'))
                }
        
        # 尝试从旧配置读取
        old_config_file = target_path / ".cold-start-config.json"
        if old_config_file.exists():
            with open(old_config_file, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
                values = self.get_placeholder_values(old_config)
                return {
                    'PROJECT_NAME': old_config.get('projectName', '未命名项目'),
                    'PROGRAMMING_LANGUAGE': old_config.get('languageName', '未知'),
                    'CODE_LANGUAGE': old_config.get('codeLanguage', 'unknown'),
                    'FRAMEWORK': values.get('FRAMEWORK', '未知'),
                    'CODE_LANGUAGE_EXT': self._get_language_ext(old_config.get('codeLanguage', 'unknown'))
                }
        
        # 尝试从规则文件读取
        rules_dir = target_path / ".cursor" / "rules"
        if not rules_dir.exists():
            return None
        
        config = {}
        for rule_file in rules_dir.glob("*.mdc"):
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                project_name_match = re.search(r'#\s*([^\n]+)\s*项目核心规则', content)
                if project_name_match:
                    config['PROJECT_NAME'] = project_name_match.group(1).strip()
                
                if 'Dart' in content or 'dart' in rule_file.name:
                    config['PROGRAMMING_LANGUAGE'] = 'Dart'
                    config['CODE_LANGUAGE'] = 'dart'
                    config['CODE_LANGUAGE_EXT'] = 'dart'
                elif 'TypeScript' in content or 'typescript' in rule_file.name:
                    config['PROGRAMMING_LANGUAGE'] = 'TypeScript'
                    config['CODE_LANGUAGE'] = 'typescript'
                    config['CODE_LANGUAGE_EXT'] = 'ts'
                elif 'Python' in content or 'python' in rule_file.name:
                    config['PROGRAMMING_LANGUAGE'] = 'Python'
                    config['CODE_LANGUAGE'] = 'python'
                    config['CODE_LANGUAGE_EXT'] = 'py'
                
                if 'Flutter' in content or 'flutter' in rule_file.name:
                    config['FRAMEWORK'] = 'Flutter'
                elif 'React' in content or 'react' in rule_file.name:
                    config['FRAMEWORK'] = 'React'
        
        config.setdefault('PROJECT_NAME', '未命名项目')
        config.setdefault('PROGRAMMING_LANGUAGE', '未知')
        config.setdefault('CODE_LANGUAGE', 'unknown')
        config.setdefault('CODE_LANGUAGE_EXT', 'txt')
        config.setdefault('FRAMEWORK', '未知')
        
        return config
    
    def _get_language_ext(self, code_language: str) -> str:
        """获取语言文件扩展名"""
        ext_map = {
            'dart': 'dart',
            'typescript': 'ts',
            'javascript': 'js',
            'python': 'py',
            'kotlin': 'kt',
            'swift': 'swift'
        }
        return ext_map.get(code_language.lower(), 'txt')
    
    def _list_available_modules(self, modules_dir: Path) -> List[Dict[str, Any]]:
        """列出可用的模块"""
        modules = []
        if not modules_dir.exists():
            return modules
        
        for module_dir in modules_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            config_file = module_dir / "module.config.json"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    module_config = json.load(f)
                    modules.append({
                        'id': module_config.get('moduleId', module_dir.name),
                        'name': module_config.get('moduleName', module_dir.name),
                        'description': module_config.get('moduleDescription', ''),
                        'path': module_dir
                    })
            except Exception:
                continue
        
        return modules
    
    def _load_module_config(self, module_path: Path) -> Dict[str, Any]:
        """加载模块配置"""
        config_file = module_path / "module.config.json"
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _check_module_compatibility(self, module_config: Dict[str, Any], project_info: Dict[str, Any]) -> bool:
        """检查模块兼容性"""
        tech = project_info.get('technology', {})
        lang_id = tech.get('language', {}).get('id', '').lower()
        fw_id = tech.get('framework', {}).get('id', '').lower()
        
        compatible_languages = module_config.get('compatibleLanguages', [])
        if compatible_languages:
            if lang_id not in [lang.lower() for lang in compatible_languages]:
                print(f"  警告：项目语言 {tech.get('language', {}).get('name')} 不在模块兼容语言列表中")
        
        compatible_frameworks = module_config.get('compatibleFrameworks', [])
        if compatible_frameworks:
            if fw_id not in [fw.lower() for fw in compatible_frameworks]:
                print(f"  警告：项目框架 {tech.get('framework', {}).get('name')} 不在模块兼容框架列表中")
        
        return True
    
    def _collect_module_parameters(self, module_config: Dict[str, Any], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """收集模块参数"""
        params = {}
        parameters = module_config.get('parameters', {})
        
        tech = project_info.get('technology', {})
        project_name = project_info.get('project', {}).get('name', '未命名项目')
        
        for param_name, param_def in parameters.items():
            required = param_def.get('required', False)
            default = param_def.get('default', '')
            prompt = param_def.get('prompt', f'请输入 {param_name}')
            
            # 如果参数已经在项目配置中存在，使用项目配置的值
            if param_name == 'PROJECT_NAME':
                params[param_name] = project_name
                print(f"  {param_name}: {params[param_name]} (使用项目配置)")
                continue
            elif param_name == 'CODE_LANGUAGE':
                params[param_name] = tech.get('language', {}).get('codeLanguage', 'unknown')
                print(f"  {param_name}: {params[param_name]} (使用项目配置)")
                continue
            elif param_name == 'CODE_LANGUAGE_EXT':
                code_lang = tech.get('language', {}).get('codeLanguage', 'unknown')
                params[param_name] = self._get_language_ext(code_lang)
                print(f"  {param_name}: {params[param_name]} (使用项目配置)")
                continue
            
            # 交互式收集参数
            if default:
                user_input = input(f"{prompt} (默认: {default}): ").strip()
                params[param_name] = user_input if user_input else default
            else:
                user_input = input(f"{prompt}: ").strip()
                if not user_input and required:
                    print(f"❌ 错误：{param_name} 是必填参数")
                    sys.exit(1)
                params[param_name] = user_input
        
        return params
    
    def _inject_module_rules(self, target_path: Path, module_info: Dict[str, Any], 
                           module_config: Dict[str, Any], project_info: Dict[str, Any],
                           module_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """注入模块规则到目标项目"""
        # 查找模块规则模板文件
        module_dir = module_info['path']
        template_files = list(module_dir.glob("*.mdc.template"))
        
        if not template_files:
            print(f"❌ 错误：模块 {module_info['name']} 没有找到规则模板文件")
            sys.exit(1)
        
        # 准备渲染参数
        tech = project_info.get('technology', {})
        render_params = {
            'PROJECT_NAME': project_info.get('project', {}).get('name', '未命名项目'),
            'PROGRAMMING_LANGUAGE': tech.get('language', {}).get('name', '未知'),
            'CODE_LANGUAGE': tech.get('language', {}).get('codeLanguage', 'unknown'),
            'CODE_LANGUAGE_EXT': self._get_language_ext(tech.get('language', {}).get('codeLanguage', 'unknown')),
            'FRAMEWORK': tech.get('framework', {}).get('name', '未知'),
            'GENERATION_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        render_params.update(module_params)
        
        # 目标规则目录
        target_rules_dir = target_path / ".cursor" / "rules"
        target_rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 渲染并复制规则文件
        priority = module_config.get('priority', 40)
        injected_files = []
        
        for template_file in template_files:
            # 读取模板
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 使用Jinja2渲染
            template = Template(template_content)
            rendered = template.render(**render_params)
            
            # 生成输出文件名
            base_name = template_file.stem.replace('.template', '')
            output_file = target_rules_dir / f"{priority}-{base_name}.mdc"
            
            # 写入规则文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)
            
            injected_files.append({
                'name': output_file.name,
                'path': f".cursor/rules/{output_file.name}",
                'type': 'module'
            })
            
            print(f"  ✅ {output_file.name}")
        
        return injected_files
    
    def _update_project_config(self, target_path: Path, project_info: Dict[str, Any],
                              module_info: Dict[str, Any], module_config: Dict[str, Any],
                              injected_files: List[Dict[str, Any]]):
        """更新项目配置文件"""
        cold_start_dir = target_path / ".cold-start"
        cold_start_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = cold_start_dir / "project.json"
        
        # 更新模块列表
        if 'modules' not in project_info:
            project_info['modules'] = {'injected': [], 'available': []}
        
        # 添加新注入的模块
        module_entry = {
            'id': module_config.get('moduleId'),
            'name': module_config.get('moduleName'),
            'type': module_config.get('moduleType'),
            'injectedAt': datetime.now().isoformat(),
            'files': injected_files
        }
        
        # 检查是否已存在
        existing_modules = project_info['modules'].get('injected', [])
        module_ids = [m.get('id') for m in existing_modules]
        
        if module_entry['id'] in module_ids:
            # 更新现有模块
            for i, m in enumerate(existing_modules):
                if m.get('id') == module_entry['id']:
                    existing_modules[i] = module_entry
                    break
        else:
            # 添加新模块
            existing_modules.append(module_entry)
        
        project_info['modules']['injected'] = existing_modules
        
        # 更新文件列表
        if 'files' not in project_info:
            project_info['files'] = {'plans': [], 'rules': []}
        
        # 添加新注入的规则文件
        existing_rules = project_info['files'].get('rules', [])
        for injected_file in injected_files:
            if not any(r.get('name') == injected_file['name'] for r in existing_rules):
                existing_rules.append(injected_file)
        
        project_info['files']['rules'] = existing_rules
        project_info['lastUpdated'] = datetime.now().isoformat()
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)


class InteractiveCommandSystem:
    """交互式命令系统"""
    
    def __init__(self, initializer: ProjectInitializer, target_dir: Optional[str] = None):
        self.initializer = initializer
        self.target_dir = target_dir
        self.command_path = []  # 命令路径栈，用于跟踪当前所在的"目录"
        self.running = True
        
        # 定义命令结构
        self.commands = {
            'root': {
                'init': {
                    'type': 'category',
                    'description': '项目初始化流程（可直接执行：init [目标目录]）',
                    'handler': self._handle_init,  # 也可以直接执行
                    'commands': {
                        'process': {
                            'type': 'command',
                            'description': '阶段2：处理模板文件',
                            'handler': self._handle_init_process
                        },
                        'export': {
                            'type': 'command',
                            'description': '阶段3：导出到目标项目',
                            'handler': self._handle_init_export,
                            'requires_target': True
                        },
                        'help': {
                            'type': 'help',
                            'description': '显示init命令帮助'
                        },
                        'back': {
                            'type': 'nav',
                            'description': '返回上一级'
                        }
                    }
                },
                'inject': {
                    'type': 'category',
                    'description': '模块化规则注入',
                    'commands': {
                        'help': {
                            'type': 'help',
                            'description': '显示inject命令帮助'
                        },
                        'back': {
                            'type': 'nav',
                            'description': '返回上一级'
                        }
                    },
                    'handler': self._handle_inject,  # inject是直接执行的命令
                    'requires_target': True
                },
                'add-module': {
                    'type': 'command',
                    'description': '快速创建新模块规则',
                    'handler': self._handle_add_module
                },
                'extract-rules': {
                    'type': 'command',
                    'description': '从目标项目提取规则并反哺',
                    'handler': self._handle_extract_rules,
                    'requires_target': True
                },
                'init-config': {
                    'type': 'command',
                    'description': '为现有项目补充配置信息',
                    'handler': self._handle_init_config,
                    'requires_target': True
                },
                'update-rules': {
                    'type': 'command',
                    'description': '自动更新目标项目的规则文件',
                    'handler': self._handle_update_rules,
                    'requires_target': True
                },
                'help': {
                    'type': 'help',
                    'description': '显示帮助信息'
                },
                'exit': {
                    'type': 'exit',
                    'description': '退出程序'
                }
            }
        }
    
    def _handle_init(self, args: List[str]):
        """处理 init 命令（阶段1：初始化）"""
        # 如果提供了参数，使用参数作为目标目录
        target_dir = args[0] if args else self.target_dir
        self.initializer.stage_init(target_dir)
    
    def _handle_init_process(self, args: List[str]):
        """处理 init process 命令"""
        self.initializer.stage_process()
    
    def _handle_init_export(self, args: List[str]):
        """处理 init export 命令"""
        # 如果提供了参数，使用参数作为目标目录
        target_dir = args[0] if args else self.target_dir
        if not target_dir:
            print("❌ 错误：必须指定目标项目目录")
            print("提示：启动时请提供目标项目目录参数，或在命令中指定")
            return
        self.initializer.stage_export(target_dir)
    
    def _handle_inject(self, args: List[str]):
        """处理 inject 命令"""
        # 如果提供了参数，使用参数作为目标目录
        target_dir = args[0] if args else self.target_dir
        if not target_dir:
            print("❌ 错误：必须指定目标项目目录")
            print("提示：启动时请提供目标项目目录参数，或在命令中指定")
            return
        self.initializer.stage_inject(target_dir)
    
    def _handle_add_module(self, args: List[str]):
        """处理 add-module 命令：快速创建新模块规则"""
        print("=" * 50)
        print("  创建新模块规则")
        print("=" * 50)
        print()
        
        # 1. 收集模块基本信息
        print("[1] 收集模块基本信息...")
        module_id = input("模块ID（英文，如：network-module）: ").strip()
        if not module_id:
            print("❌ 错误：模块ID不能为空")
            return
        
        module_name = input("模块名称（中文，如：网络模块）: ").strip() or module_id
        module_description = input("模块描述: ").strip() or f"提供{module_name}功能的模块化规则"
        
        print()
        print("模块类型：")
        print("  1) feature - 功能模块")
        print("  2) utility - 工具模块")
        print("  3) service - 服务模块")
        module_type_choice = input("请选择 (1-3，默认1): ").strip() or "1"
        module_type_map = {"1": "feature", "2": "utility", "3": "service"}
        module_type = module_type_map.get(module_type_choice, "feature")
        
        priority = input("规则优先级（数字，默认40）: ").strip() or "40"
        try:
            priority = int(priority)
        except ValueError:
            priority = 40
        
        print()
        
        # 2. 收集兼容性信息
        print("[2] 收集兼容性信息...")
        print("兼容的语言（用逗号分隔，如：dart,typescript,python）: ")
        compatible_languages_input = input().strip()
        compatible_languages = [lang.strip() for lang in compatible_languages_input.split(',') if lang.strip()] if compatible_languages_input else []
        
        print("兼容的框架（用逗号分隔，如：flutter,react,django）: ")
        compatible_frameworks_input = input().strip()
        compatible_frameworks = [fw.strip() for fw in compatible_frameworks_input.split(',') if fw.strip()] if compatible_frameworks_input else []
        
        print()
        
        # 3. 收集模块参数
        print("[3] 收集模块参数（可选）...")
        print("提示：按Enter跳过，输入'done'完成")
        parameters = {}
        while True:
            param_name = input("参数名称（如：MODULE_NAME，输入done完成）: ").strip()
            if not param_name or param_name.lower() == 'done':
                break
            
            param_desc = input(f"  参数描述: ").strip()
            param_required = input(f"  是否必填 (y/n，默认n): ").strip().lower() == 'y'
            param_default = input(f"  默认值: ").strip()
            param_prompt = input(f"  提示文本: ").strip() or f"请输入 {param_name}"
            
            parameters[param_name] = {
                "description": param_desc,
                "required": param_required,
                "default": param_default,
                "prompt": param_prompt
            }
        
        print()
        
        # 4. 创建模块目录和文件
        print("[4] 创建模块文件...")
        modules_dir = self.initializer.project_init_dir / "templates" / "modules"
        module_dir = modules_dir / module_id
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模块配置文件
        module_config = {
            "moduleId": module_id,
            "moduleName": module_name,
            "moduleDescription": module_description,
            "moduleType": module_type,
            "priority": priority,
            "dependencies": {
                "required": ["logging"],
                "optional": []
            },
            "parameters": parameters,
            "compatibleLanguages": compatible_languages if compatible_languages else ["dart", "typescript", "python"],
            "compatibleFrameworks": compatible_frameworks if compatible_frameworks else ["flutter", "react", "django"]
        }
        
        config_file = module_dir / "module.config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(module_config, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {config_file.name}")
        
        # 创建模块规则模板文件
        template_file = module_dir / f"{module_id}.mdc.template"
        template_content = f"""---
alwaysApply: true
---
# {{{{ MODULE_NAME }}}}{module_name}规则

## 模块信息

- **模块名称：** {{{{ MODULE_NAME }}}}
- **模块路径：** {{{{ MODULE_PATH }}}}
- **模块类型：** {module_type}
- **应用项目：** {{{{ PROJECT_NAME }}}}

## 核心约束（强制）

1. **模块必须实现统一接口**
2. **模块必须记录详细日志**
3. **模块必须提供错误处理**

## 模块设计原则

### 1. 统一接口

**原则：** 所有模块操作必须通过统一接口进行

**实践：**
```{{{{ CODE_LANGUAGE }}}}
// ✅ 好的做法 - 统一接口
class {{{{ MODULE_NAME }}}}Manager {{
  // 实现模块功能
}}

// ❌ 不好的做法 - 分散的逻辑
void doSomething() {{ ... }}
void doAnother() {{ ... }}
```

### 2. 详细日志记录

**原则：** 模块操作必须记录详细日志

**实践：**
```{{{{ CODE_LANGUAGE }}}}
// ✅ 好的做法 - 详细日志
logger.log('开始执行模块操作', tag: 'MODULE');
logger.logError('模块操作失败', error: e, stackTrace: stackTrace, tag: 'MODULE');
```

### 3. 错误处理

**原则：** 模块必须提供完善的错误处理

**实践：**
- 捕获所有异常
- 记录错误日志
- 提供错误恢复机制

## 禁止行为

- ❌ 不记录模块日志
- ❌ 不提供错误处理
- ❌ 不使用项目统一的日志服务

## 必须遵守

- ✅ 必须实现统一接口
- ✅ 必须记录详细日志
- ✅ 必须提供错误处理
- ✅ 必须使用项目统一的日志服务

## 模块文件结构

```
{{{{ MODULE_PATH }}}}/
├── {{{{ MODULE_NAME }}}}_manager.{{{{ CODE_LANGUAGE_EXT }}}}
├── {{{{ MODULE_NAME }}}}_service.{{{{ CODE_LANGUAGE_EXT }}}}
└── {{{{ MODULE_NAME }}}}_config.{{{{ CODE_LANGUAGE_EXT }}}}
```

## 日志标签

模块使用以下日志标签：
- `MODULE` - 模块操作日志
"""
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"  ✅ {template_file.name}")
        
        print()
        print("=" * 50)
        print("  ✅ 模块创建完成！")
        print("=" * 50)
        print()
        print(f"模块位置: {module_dir}")
        print()
        print("下一步操作：")
        print("1. 编辑模块规则模板文件，完善规则内容")
        print("2. 根据需要调整模块配置文件")
        print("3. 使用 'inject' 命令将模块注入到目标项目")
        print()
    
    def _handle_init_config(self, args: List[str]):
        """处理 init-config 命令：为现有项目补充配置信息"""
        target_dir = args[0] if args else self.target_dir
        if not target_dir:
            print("❌ 错误：必须指定目标项目目录")
            print("提示：启动时请提供目标项目目录参数，或在命令中指定")
            return
        
        target_path = Path(target_dir).resolve()
        if not target_path.exists():
            print(f"❌ 错误：目标项目目录不存在: {target_path}")
            return
        
        print("=" * 50)
        print("  补充项目配置信息")
        print("=" * 50)
        print()
        print(f"目标项目: {target_path}")
        print()
        
        # 1. 检查是否已有配置文件
        project_config_file = target_path / ".cold-start" / "project.json"
        if project_config_file.exists():
            print("⚠️  项目配置文件已存在")
            print(f"  位置: {project_config_file}")
            print()
            overwrite = input("是否覆盖现有配置？(y/n): ").strip().lower()
            if overwrite != 'y':
                print("操作已取消")
                return
            print()
        
        # 2. 自动检测项目信息
        print("[1] 自动检测项目信息...")
        detected_info = self._detect_project_info(target_path)
        print(f"  ✅ 检测完成")
        print()
        
        # 3. 交互式收集项目信息
        print("[2] 收集项目配置信息...")
        print()
        
        # 项目名称
        default_name = detected_info.get('project_name', target_path.name)
        project_name = input(f"项目名称 [{default_name}]: ").strip()
        if not project_name:
            project_name = default_name
        
        # 项目描述
        project_description = input("项目描述（可选）: ").strip()
        
        # 语言选择
        options = self.initializer.load_options()
        languages = options.get('languages', [])
        
        print()
        print("可用语言：")
        for i, lang in enumerate(languages, 1):
            default_marker = " (默认)" if lang.get('default') else ""
            print(f"  {i}. {lang['name']}{default_marker}")
        
        detected_lang_id = detected_info.get('language_id')
        if detected_lang_id:
            detected_lang = next((l for l in languages if l['id'] == detected_lang_id), None)
            if detected_lang:
                default_lang_idx = languages.index(detected_lang) + 1
                print(f"  检测到的语言: {detected_lang['name']} (推荐选择 {default_lang_idx})")
        
        lang_choice = input(f"选择语言 [1-{len(languages)}]: ").strip()
        if not lang_choice:
            lang_choice = "1"
        
        try:
            lang_idx = int(lang_choice) - 1
            if 0 <= lang_idx < len(languages):
                selected_lang = languages[lang_idx]
            else:
                selected_lang = languages[0]
        except ValueError:
            selected_lang = languages[0]
        
        # 框架选择
        frameworks = selected_lang.get('frameworks', [])
        if frameworks:
            print()
            print(f"可用框架（{selected_lang['name']}）：")
            for i, fw in enumerate(frameworks, 1):
                default_marker = " (默认)" if fw.get('default') else ""
                print(f"  {i}. {fw['name']}{default_marker}")
            
            detected_fw_id = detected_info.get('framework_id')
            if detected_fw_id:
                detected_fw = next((f for f in frameworks if f['id'] == detected_fw_id), None)
                if detected_fw:
                    default_fw_idx = frameworks.index(detected_fw) + 1
                    print(f"  检测到的框架: {detected_fw['name']} (推荐选择 {default_fw_idx})")
            
            fw_choice = input(f"选择框架 [1-{len(frameworks)}]: ").strip()
            if not fw_choice:
                fw_choice = "1"
            
            try:
                fw_idx = int(fw_choice) - 1
                if 0 <= fw_idx < len(frameworks):
                    selected_framework = frameworks[fw_idx]
                else:
                    selected_framework = frameworks[0]
            except ValueError:
                selected_framework = frameworks[0]
        else:
            selected_framework = {'id': selected_lang['id'], 'name': selected_lang['name'], 'buildTool': 'CLI'}
        
        # 平台选择
        available_platforms = options.get('platforms', [])
        print()
        print("可用平台（可多选，用逗号分隔）：")
        for i, platform in enumerate(available_platforms, 1):
            default_marker = " (默认)" if platform.get('default') else ""
            print(f"  {i}. {platform['name']}{default_marker}")
        
        detected_platforms = detected_info.get('platforms', [])
        if detected_platforms:
            print(f"  检测到的平台: {', '.join(detected_platforms)}")
        
        platform_choice = input("选择平台（留空使用默认）: ").strip()
        if platform_choice:
            try:
                platform_indices = [int(x.strip()) - 1 for x in platform_choice.split(',')]
                selected_platforms = [available_platforms[i] for i in platform_indices if 0 <= i < len(available_platforms)]
            except ValueError:
                selected_platforms = [p for p in available_platforms if p.get('default')]
        else:
            selected_platforms = [p for p in available_platforms if p.get('default')] or [available_platforms[0]]
        
        # GitHub Action
        print()
        enable_github_action = input("启用 GitHub Actions？(y/n) [n]: ").strip().lower()
        enable_github_action = enable_github_action == 'y'
        
        print()
        
        # 4. 扫描已实施的文件
        print("[3] 扫描已实施的文件...")
        implemented_plans = []
        implemented_rules = []
        
        plans_dir = target_path / ".cursor" / "plans"
        if plans_dir.exists():
            for plan_file in plans_dir.glob("*.mdc"):
                implemented_plans.append({
                    'name': plan_file.name,
                    'path': f".cursor/plans/{plan_file.name}"
                })
        
        rules_dir = target_path / ".cursor" / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.mdc"):
                implemented_rules.append({
                    'name': rule_file.name,
                    'path': f".cursor/rules/{rule_file.name}",
                    'type': self.initializer._detect_rule_type(rule_file.name)
                })
        
        print(f"  ✅ 发现 {len(implemented_plans)} 个计划文件，{len(implemented_rules)} 个规则文件")
        print()
        
        # 5. 生成项目配置
        print("[4] 生成项目配置文件...")
        
        # 创建 .cold-start 目录
        cold_start_dir = target_path / ".cold-start"
        cold_start_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建项目配置
        project_info = {
            'version': '1.0.0',
            'generatedAt': datetime.now().isoformat(),
            'generatedBy': 'CursorColdStart',
            'project': {
                'name': project_name,
                'description': project_description,
                'rootPath': str(target_path)
            },
            'technology': {
                'language': {
                    'id': selected_lang['id'],
                    'name': selected_lang['name'],
                    'codeLanguage': selected_lang.get('codeLanguage', selected_lang['id'])
                },
                'framework': {
                    'id': selected_framework['id'],
                    'name': selected_framework['name'],
                    'buildTool': selected_framework.get('buildTool', 'CLI')
                },
                'platforms': [
                    {'id': p['id'], 'name': p['name']} 
                    for p in selected_platforms
                ]
            },
            'modules': {
                'injected': [],
                'available': []
            },
            'files': {
                'plans': implemented_plans,
                'rules': implemented_rules
            },
            'config': {
                'enableGitHubAction': enable_github_action,
                'logService': {
                    'class': 'Logger',
                    'filePath': 'logs/app.log',
                    'collectScript': 'scripts/collect_logs.sh'
                }
            }
        }
        
        # 保存配置文件
        with open(project_config_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 配置文件已创建: {project_config_file}")
        print()
        
        # 创建 README 文件
        readme_file = cold_start_dir / "README.md"
        readme_content = f"""# ColdStart 项目配置

此目录由 CursorColdStart 脚手架自动创建和管理。

## 目录说明

- `project.json` - 项目完整配置信息
  - 项目基本信息
  - 技术方案（语言、框架、平台）
  - 已注入的模块列表
  - 已实施的文件列表

## 重要提示

⚠️ **请勿手动修改此目录中的文件**

此目录由 CursorColdStart 脚手架自动管理：
- 使用 `inject` 命令注入模块时，会自动更新此配置
- 使用 `extract-rules` 命令提取规则时，会读取此配置

如需修改项目配置，请使用 CursorColdStart 脚手架的命令。

## 项目信息

- **项目名称：** {project_info['project']['name']}
- **技术栈：** {project_info['technology']['language']['name']} + {project_info['technology']['framework']['name']}
- **目标平台：** {', '.join([p['name'] for p in project_info['technology']['platforms']])}
- **初始化时间：** {project_info['generatedAt']}
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("=" * 50)
        print("  ✅ 项目配置补充完成！")
        print("=" * 50)
        print()
        print("配置信息：")
        print(f"  项目名称: {project_name}")
        print(f"  语言: {selected_lang['name']}")
        print(f"  框架: {selected_framework['name']}")
        print(f"  平台: {', '.join([p['name'] for p in selected_platforms])}")
        print(f"  GitHub Actions: {'启用' if enable_github_action else '禁用'}")
        print()
        print("下一步操作：")
        print("1. 使用 'inject' 命令注入模块规则")
        print("2. 使用 'extract-rules' 命令提取规则并反哺")
        print("3. 使用 'update-rules' 命令更新规则文件")
        print()
    
    def _handle_update_rules(self, args: List[str]):
        """处理 update-rules 命令：自动更新目标项目的规则文件"""
        target_dir = args[0] if args else self.target_dir
        if not target_dir:
            print("❌ 错误：必须指定目标项目目录")
            print("提示：启动时请提供目标项目目录参数，或在命令中指定")
            return
        
        target_path = Path(target_dir).resolve()
        if not target_path.exists():
            print(f"❌ 错误：目标项目目录不存在: {target_path}")
            return
        
        print("=" * 50)
        print("  自动更新项目规则")
        print("=" * 50)
        print()
        print(f"目标项目: {target_path}")
        print()
        
        # 1. 读取项目配置
        print("[1] 读取项目配置...")
        project_config_file = target_path / ".cold-start" / "project.json"
        if not project_config_file.exists():
            print("❌ 错误：项目配置文件不存在")
            print("提示：请先运行 'init-config' 命令补充项目配置")
            return
        
        with open(project_config_file, 'r', encoding='utf-8') as f:
            project_info = json.load(f)
        
        print(f"✅ 项目配置读取完成")
        print(f"  项目名称: {project_info.get('project', {}).get('name', '未知')}")
        tech = project_info.get('technology', {})
        print(f"  技术栈: {tech.get('language', {}).get('name', '未知')} + {tech.get('framework', {}).get('name', '未知')}")
        print()
        
        # 2. 确定需要应用的规则模板
        print("[2] 确定需要应用的规则模板...")
        language_id = tech.get('language', {}).get('id', 'dart')
        framework_id = tech.get('framework', {}).get('id', 'flutter')
        platforms = [p.get('id') for p in tech.get('platforms', [])]
        
        # 构建配置用于模板渲染
        config = {
            'projectName': project_info.get('project', {}).get('name', '未命名项目'),
            'projectDescription': project_info.get('project', {}).get('description', ''),
            'language': language_id,
            'languageName': tech.get('language', {}).get('name', 'Dart'),
            'codeLanguage': tech.get('language', {}).get('codeLanguage', language_id),
            'framework': framework_id,
            'buildTool': tech.get('framework', {}).get('buildTool', 'CLI'),
            'platforms': platforms,
            'enableGitHubAction': project_info.get('config', {}).get('enableGitHubAction', False)
        }
        
        values = self.initializer.get_placeholder_values(config)
        
        # 确定需要应用的规则模板
        rule_templates = []
        
        # 通用规则（所有项目都需要）
        common_rules_dir = self.initializer.project_init_dir / "templates" / "rules" / "common"
        if common_rules_dir.exists():
            for template_file in sorted(common_rules_dir.glob("*.template")):
                rule_templates.append({
                    'type': 'common',
                    'template_path': template_file,
                    'output_name': template_file.stem.replace('.mdc', '') + '.mdc'
                })
        
        # 语言特定规则
        if language_id:
            lang_rules_dir = self.initializer.project_init_dir / "templates" / "rules" / "languages"
            if lang_rules_dir.exists():
                lang_template = lang_rules_dir / f"{language_id}.mdc.template"
                if lang_template.exists():
                    rule_templates.append({
                        'type': 'language',
                        'template_path': lang_template,
                        'output_name': f"10-{language_id}.mdc"
                    })
        
        # 框架特定规则
        if framework_id:
            fw_rules_dir = self.initializer.project_init_dir / "templates" / "rules" / "frameworks"
            if fw_rules_dir.exists():
                fw_template = fw_rules_dir / f"{framework_id}.mdc.template"
                if fw_template.exists():
                    rule_templates.append({
                        'type': 'framework',
                        'template_path': fw_template,
                        'output_name': f"20-{framework_id}.mdc"
                    })
        
        # 平台特定规则
        for platform_id in platforms:
            platform_rules_dir = self.initializer.project_init_dir / "templates" / "rules" / "platforms"
            if platform_rules_dir.exists():
                platform_template = platform_rules_dir / f"{platform_id}.mdc.template"
                if platform_template.exists():
                    rule_templates.append({
                        'type': 'platform',
                        'template_path': platform_template,
                        'output_name': f"30-{platform_id}.mdc"
                    })
        
        print(f"  ✅ 找到 {len(rule_templates)} 个规则模板")
        print()
        
        # 3. 渲染并更新规则文件
        print("[3] 渲染并更新规则文件...")
        rules_dir = target_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        updated_files = []
        created_files = []
        
        for rule_template in rule_templates:
            template_path = rule_template['template_path']
            output_name = rule_template['output_name']
            output_path = rules_dir / output_name
            
            # 读取模板
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 渲染模板
            template = Template(template_content)
            rendered_content = template.render(**values)
            
            # 检查文件是否存在
            file_exists = output_path.exists()
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            if file_exists:
                updated_files.append(output_name)
                print(f"  ✅ 更新: {output_name}")
            else:
                created_files.append(output_name)
                print(f"  ✅ 创建: {output_name}")
        
        print()
        print(f"  ✅ 共更新 {len(updated_files)} 个文件，创建 {len(created_files)} 个文件")
        print()
        
        # 4. 更新项目配置文件
        print("[4] 更新项目配置文件...")
        
        # 更新规则文件列表
        implemented_rules = []
        for rule_template in rule_templates:
            output_name = rule_template['output_name']
            rule_type = self.initializer._detect_rule_type(output_name)
            implemented_rules.append({
                'name': output_name,
                'path': f".cursor/rules/{output_name}",
                'type': rule_type
            })
        
        project_info['files']['rules'] = implemented_rules
        project_info['lastUpdated'] = datetime.now().isoformat()
        
        with open(project_config_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)
        
        print("  ✅ 项目配置已更新")
        print()
        
        print("=" * 50)
        print("  ✅ 规则更新完成！")
        print("=" * 50)
        print()
        print("更新的规则文件：")
        for rule_template in rule_templates:
            print(f"  - {rule_template['output_name']}")
        print()
        print("下一步操作：")
        print("1. 在 Cursor 中重新加载规则文件")
        print("2. 检查规则是否正确应用")
        print()
    
    def _detect_project_info(self, target_path: Path) -> Dict[str, Any]:
        """自动检测项目信息"""
        info = {
            'project_name': target_path.name,
            'language_id': None,
            'framework_id': None,
            'platforms': []
        }
        
        # 1. 从规则文件检测
        rules_dir = target_path / ".cursor" / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.mdc"):
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测语言
                if 'dart' in rule_file.name.lower() or 'Dart' in content:
                    info['language_id'] = 'dart'
                elif 'typescript' in rule_file.name.lower() or 'TypeScript' in content:
                    info['language_id'] = 'typescript'
                elif 'python' in rule_file.name.lower() or 'Python' in content:
                    info['language_id'] = 'python'
                elif 'kotlin' in rule_file.name.lower() or 'Kotlin' in content:
                    info['language_id'] = 'kotlin'
                elif 'swift' in rule_file.name.lower() or 'Swift' in content:
                    info['language_id'] = 'swift'
                
                # 检测框架
                if 'flutter' in rule_file.name.lower() or 'Flutter' in content:
                    info['framework_id'] = 'flutter'
                elif 'react' in rule_file.name.lower() or 'React' in content:
                    info['framework_id'] = 'react'
                elif 'vue' in rule_file.name.lower() or 'Vue' in content:
                    info['framework_id'] = 'vue'
                elif 'django' in rule_file.name.lower() or 'Django' in content:
                    info['framework_id'] = 'django'
                elif 'fastapi' in rule_file.name.lower() or 'FastAPI' in content:
                    info['framework_id'] = 'fastapi'
                elif 'android' in rule_file.name.lower() or 'Android' in content:
                    info['framework_id'] = 'android'
                elif 'ios' in rule_file.name.lower() or 'iOS' in content:
                    info['framework_id'] = 'ios'
        
        # 2. 从项目文件检测
        # 检测 pubspec.yaml (Flutter/Dart)
        if (target_path / "pubspec.yaml").exists():
            info['language_id'] = 'dart'
            info['framework_id'] = 'flutter'
        
        # 检测 package.json (Node.js/TypeScript)
        package_json = target_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    deps = package_data.get('dependencies', {})
                    if 'react' in deps:
                        info['framework_id'] = 'react'
                    elif 'vue' in deps:
                        info['framework_id'] = 'vue'
                    info['language_id'] = 'typescript'
            except:
                pass
        
        # 检测 requirements.txt 或 pyproject.toml (Python)
        if (target_path / "requirements.txt").exists() or (target_path / "pyproject.toml").exists():
            info['language_id'] = 'python'
        
        # 检测 build.gradle (Android/Kotlin)
        if (target_path / "build.gradle").exists() or (target_path / "android" / "build.gradle").exists():
            info['language_id'] = 'kotlin'
            info['framework_id'] = 'android'
            info['platforms'].append('android')
        
        # 检测 Xcode 项目 (iOS/Swift)
        xcodeproj_files = list(target_path.glob("*.xcodeproj"))
        ios_xcodeproj_files = list((target_path / "ios").glob("*.xcodeproj")) if (target_path / "ios").exists() else []
        if xcodeproj_files or ios_xcodeproj_files:
            info['language_id'] = 'swift'
            info['framework_id'] = 'ios'
            info['platforms'].append('ios')
        
        return info
    
    def _handle_extract_rules(self, args: List[str]):
        """处理 extract-rules 命令：从目标项目提取规则并反哺"""
        target_dir = args[0] if args else self.target_dir
        if not target_dir:
            print("❌ 错误：必须指定目标项目目录")
            print("提示：启动时请提供目标项目目录参数，或在命令中指定")
            return
        
        target_path = Path(target_dir).resolve()
        if not target_path.exists():
            print(f"❌ 错误：目标项目目录不存在: {target_path}")
            return
        
        print("=" * 50)
        print("  从目标项目提取规则")
        print("=" * 50)
        print()
        print(f"目标项目: {target_path}")
        print()
        
        # 1. 读取项目配置信息
        print("[1] 读取项目配置信息...")
        project_config_file = target_path / ".cold-start" / "project.json"
        project_info = None
        project_name = target_path.name
        
        if project_config_file.exists():
            with open(project_config_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
                project_name = project_info.get('project', {}).get('name', target_path.name)
            print(f"✅ 项目配置读取完成")
            print(f"  项目名称: {project_name}")
            tech = project_info.get('technology', {})
            print(f"  技术栈: {tech.get('language', {}).get('name', '未知')} + {tech.get('framework', {}).get('name', '未知')}")
        else:
            print("⚠️  未找到项目配置文件，使用默认信息")
        
        print()
        
        # 2. 检查目标项目的规则文件
        rules_dir = target_path / ".cursor" / "rules"
        if not rules_dir.exists():
            print("❌ 错误：目标项目没有规则文件目录")
            print("提示：目标项目必须是通过本脚手架创建的项目")
            return
        
        rule_files = list(rules_dir.glob("*.mdc"))
        if not rule_files:
            print("❌ 错误：目标项目没有规则文件")
            return
        
        print(f"[2] 发现 {len(rule_files)} 个规则文件")
        print()
        
        # 3. 分析规则文件，识别可提取的规则
        print("[3] 分析规则文件...")
        extractable_rules = []
        
        # 如果项目配置存在，获取项目名称用于过滤
        project_name_pattern = project_name if project_info else None
        
        for rule_file in rule_files:
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否是项目特定的规则
            is_project_specific = False
            if project_name_pattern and project_name_pattern in content:
                is_project_specific = True
            if '{{ PROJECT_NAME }}' in content or '项目核心规则' in content:
                is_project_specific = True
            
            if not is_project_specific:
                # 可能是通用的规则
                extractable_rules.append({
                    'file': rule_file,
                    'name': rule_file.stem,
                    'content': content,
                    'size': len(content)
                })
        
        if not extractable_rules:
            print("  ⚠️  未发现可提取的通用规则")
            print("  提示：规则可能包含项目特定信息，需要手动审查")
            return
        
        print(f"  ✅ 发现 {len(extractable_rules)} 个可能可提取的规则")
        print()
        
        # 4. 交互式选择要提取的规则
        print("[4] 选择要提取的规则...")
        print()
        for i, rule in enumerate(extractable_rules, 1):
            print(f"{i}) {rule['name']} ({rule['size']} 字符)")
        
        print()
        selected_input = input("请选择要提取的规则（用逗号分隔，如：1,3,5，或输入all选择全部）: ").strip()
        
        selected_rules = []
        if selected_input.lower() == 'all':
            selected_rules = extractable_rules
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selected_input.split(',')]
                selected_rules = [extractable_rules[i] for i in indices if 0 <= i < len(extractable_rules)]
            except ValueError:
                print("❌ 错误：无效的选择")
                return
        
        if not selected_rules:
            print("❌ 错误：未选择任何规则")
            return
        
        print()
        
        # 5. 确定规则分类和整合位置
        print("[5] 确定规则分类...")
        print()
        print("规则分类：")
        print("  1) common - 通用规则")
        print("  2) languages - 语言特定规则")
        print("  3) frameworks - 框架特定规则")
        print("  4) platforms - 平台特定规则")
        print("  5) modules - 模块化规则")
        
        category_choice = input("请选择分类 (1-5，默认1): ").strip() or "1"
        category_map = {
            "1": "common",
            "2": "languages",
            "3": "frameworks",
            "4": "platforms",
            "5": "modules"
        }
        category = category_map.get(category_choice, "common")
        
        print()
        
        # 6. 整合规则
        print("[6] 整合规则...")
        extract_dir = self.initializer.project_init_dir / "extract" / "rules" / category
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        integration_log = self.initializer.project_init_dir / "extract" / "integration" / "integration-log.md"
        integration_log.parent.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        project_name = target_path.name
        
        for rule in selected_rules:
            # 保存提取的规则
            extract_file = extract_dir / f"{rule['name']}.md"
            with open(extract_file, 'w', encoding='utf-8') as f:
                f.write(f"# 提取的规则：{rule['name']}\n\n")
                f.write(f"**来源项目：** {project_name}\n")
                f.write(f"**提取时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**原始文件：** {rule['file']}\n\n")
                f.write("---\n\n")
                f.write(rule['content'])
            print(f"  ✅ {extract_file.name}")
        
        # 更新整合日志
        log_entry = f"""
## {today}

"""
        for rule in selected_rules:
            log_entry += f"""### {rule['name']}

- **来源项目：** {project_name}
- **规则文件：** `extract/rules/{category}/{rule['name']}.md`
- **规则内容：** {rule['name']}
- **优先级：** 待评估
- **状态：** 待审查和整合

"""
        
        # 读取现有日志
        existing_log = ""
        if integration_log.exists():
            with open(integration_log, 'r', encoding='utf-8') as f:
                existing_log = f.read()
        
        # 如果今天已经有日志，追加到今天的部分
        if f"## {today}" in existing_log:
            # 在今天的部分后面追加
            lines = existing_log.split('\n')
            insert_index = -1
            for i, line in enumerate(lines):
                if line == f"## {today}":
                    # 找到下一个##的位置
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith('## ') and lines[j] != f"## {today}":
                            insert_index = j
                            break
                    if insert_index == -1:
                        insert_index = len(lines)
                    break
            
            lines.insert(insert_index, log_entry.strip())
            new_log = '\n'.join(lines)
        else:
            # 在文件开头添加今天的日志
            new_log = log_entry.strip() + '\n\n---\n\n' + existing_log
        
        with open(integration_log, 'w', encoding='utf-8') as f:
            f.write(new_log)
        
        print()
        print("=" * 50)
        print("  ✅ 规则提取完成！")
        print("=" * 50)
        print()
        print(f"提取的规则保存在: {extract_dir}")
        print(f"整合日志已更新: {integration_log}")
        print()
        print("下一步操作：")
        print("1. 审查提取的规则文件，确保规则通用性")
        print("2. 根据规则内容，决定整合到哪个模板文件")
        print("3. 手动整合规则到对应的模板文件")
        print("4. 更新整合日志，标记规则已整合")
        print()
    
    def _get_current_commands(self) -> Dict[str, Any]:
        """获取当前命令路径下的可用命令"""
        current = self.commands['root']
        for path_item in self.command_path:
            if path_item in current and current[path_item].get('type') == 'category':
                current = current[path_item].get('commands', {})
            else:
                return {}
        return current
    
    def _show_help(self, context: Optional[str] = None):
        """显示帮助信息"""
        commands = self._get_current_commands()
        
        if self.command_path:
            print(f"\n当前路径: {' > '.join(self.command_path)}")
        else:
            print("\n可用命令：")
        
        print()
        
        # 分类显示命令
        categories = []
        commands_list = []
        nav_commands = []
        other_commands = []
        
        for cmd_name, cmd_info in commands.items():
            cmd_type = cmd_info.get('type', 'command')
            desc = cmd_info.get('description', '')
            
            if cmd_type == 'category':
                categories.append((cmd_name, desc, cmd_info))
            elif cmd_type in ['nav', 'exit']:
                nav_commands.append((cmd_name, desc))
            elif cmd_type == 'help':
                other_commands.append((cmd_name, desc))
            else:
                commands_list.append((cmd_name, desc))
        
        # 显示分类命令
        if categories:
            print("分类命令：")
            for cmd_name, desc, cmd_info in categories:
                print(f"  {cmd_name:<12} - {desc}")
                # 显示子命令预览
                sub_commands = cmd_info.get('commands', {})
                if sub_commands:
                    sub_list = [name for name in sub_commands.keys() if sub_commands[name].get('type') not in ['nav', 'help']]
                    if sub_list:
                        print(f"             子命令: {', '.join(sub_list)}")
            print()
        
        # 显示普通命令
        if commands_list:
            print("命令：")
            for cmd_name, desc in commands_list:
                print(f"  {cmd_name:<12} - {desc}")
            print()
        
        # 显示导航和其他命令
        if nav_commands or other_commands:
            for cmd_name, desc in nav_commands + other_commands:
                print(f"  {cmd_name:<12} - {desc}")
        
        print()
        print("提示：")
        print("  - 输入分类命令名称进入该分类（如：init）")
        print("  - 分类命令可以带参数直接执行（如：init /path/to/project）")
        print("  - 输入 'back' 返回上一级")
        print("  - 输入 'exit' 退出程序")
    
    def _execute_command(self, cmd_name: str, args: List[str]):
        """执行命令"""
        commands = self._get_current_commands()
        
        if cmd_name not in commands:
            print(f"❌ 错误：未知命令 '{cmd_name}'")
            print("输入 'help' 查看可用命令")
            return
        
        cmd_info = commands[cmd_name]
        cmd_type = cmd_info.get('type', 'command')
        
        if cmd_type == 'category':
            # 检查是否有handler（可以直接执行）
            handler = cmd_info.get('handler')
            if handler and args:
                # 如果有参数，直接执行handler
                try:
                    handler(args)
                except Exception as e:
                    print(f"❌ 执行命令时出错: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # 没有参数，进入分类命令
                self.command_path.append(cmd_name)
                print(f"✅ 进入 {cmd_name} 命令空间")
                print("输入 'help' 查看可用命令，输入 'back' 返回上一级")
        elif cmd_type == 'command':
            # 执行命令
            handler = cmd_info.get('handler')
            if handler:
                try:
                    handler(args)
                except Exception as e:
                    print(f"❌ 执行命令时出错: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ 错误：命令 '{cmd_name}' 没有实现")
        elif cmd_type == 'help':
            # 显示帮助
            self._show_help()
        elif cmd_type == 'nav':
            # 导航命令（back）
            if cmd_name == 'back':
                if self.command_path:
                    self.command_path.pop()
                    print("✅ 已返回上一级")
                else:
                    print("❌ 错误：已经在根目录")
        elif cmd_type == 'exit':
            # 退出命令
            if cmd_name == 'exit':
                self.running = False
                print("👋 再见！")
        else:
            # 特殊处理：如果分类命令有handler，直接执行（如inject）
            handler = cmd_info.get('handler')
            if handler:
                try:
                    handler(args)
                except Exception as e:
                    print(f"❌ 执行命令时出错: {e}")
                    import traceback
                    traceback.print_exc()
    
    def run(self):
        """运行交互式命令系统"""
        print("=" * 50)
        print("  项目AI冷启动初始化系统 - 交互式脚手架")
        print("=" * 50)
        print()
        
        if self.target_dir:
            print(f"目标项目目录: {self.target_dir}")
        else:
            print("⚠️  警告：未指定目标项目目录")
            print("某些命令（如 export、inject）需要目标项目目录")
            print("提示：启动时请提供目标项目目录参数")
        
        print()
        print("输入 'help' 查看可用命令，输入 'exit' 退出")
        print()
        
        while self.running:
            try:
                # 显示命令提示符
                if self.command_path:
                    prompt = f"[{' > '.join(self.command_path)}] > "
                else:
                    prompt = "[root] > "
                
                # 读取用户输入
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # 解析命令和参数
                parts = user_input.split()
                cmd_name = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # 执行命令
                self._execute_command(cmd_name, args)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except EOFError:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                import traceback
                traceback.print_exc()
                print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='项目AI冷启动初始化系统 - 交互式脚手架',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式：
  python start.py [命令] [目标项目目录]
  
示例：
  python start.py <目标项目目录>              # 启动交互式模式
  python start.py init-config <目标项目目录>  # 直接执行命令
  
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
    
    # 获取项目根目录（脚本所在目录）
    script_dir = Path(__file__).parent.resolve()
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

