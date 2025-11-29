#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目初始化器模块
负责项目初始化的核心逻辑
"""

import json
import sys
import shutil
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
        # 通用规则：00- 到 09- 开头，或包含 'core'
        if (any(rule_filename.startswith(f'{i:02d}-') for i in range(10)) or 
            'core' in rule_filename.lower()):
            return 'common'
        # 语言特定规则：10- 到 19- 开头，或文件名是语言名（如 dart.mdc.template）
        elif (any(rule_filename.startswith(f'{i:02d}-') for i in range(10, 20)) or
              any(lang in rule_filename.lower() for lang in ['dart', 'typescript', 'python', 'kotlin', 'swift', 'javascript', 'java', 'go', 'rust'])):
            return 'language'
        # 框架特定规则：20- 到 29- 开头，或文件名是框架名（如 flutter.mdc.template）
        elif (any(rule_filename.startswith(f'{i:02d}-') for i in range(20, 30)) or
              any(fw in rule_filename.lower() for fw in ['flutter', 'react', 'vue', 'angular', 'django', 'fastapi', 'spring', 'express'])):
            return 'framework'
        # 平台特定规则：30- 到 39- 开头，或文件名是平台名（如 android.mdc.template）
        elif (any(rule_filename.startswith(f'{i:02d}-') for i in range(30, 40)) or
              any(platform in rule_filename.lower() for platform in ['android', 'ios', 'web', 'windows', 'macos', 'linux'])):
            return 'platform'
        # 模块化规则：40- 到 49- 开头
        elif any(rule_filename.startswith(f'{i:02d}-') for i in range(40, 50)):
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
        print("   coldstart process")
        print()
    
    def stage_process(self):
        """阶段2：处理"""
        if not self.config_file.exists():
            print("❌ 错误：配置文件不存在")
            print("请先运行阶段1：coldstart init")
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
        lang_rules_dir = self.project_init_dir / "templates" / "rules" / "languages"
        # 尝试查找带前缀的文件（如 10-dart.mdc.template）或不带前缀的文件（如 dart.mdc.template）
        lang_template = None
        for pattern in [f"10-{lang}.mdc.template", f"{lang}.mdc.template"]:
            candidate = lang_rules_dir / pattern
            if candidate.exists():
                lang_template = candidate
                break
        
        if lang_template:
            print(f"    处理语言特定规则: {config.get('languageName', lang)}...")
            options = self.load_options()
            lang_priority = options.get('rulePriorities', {}).get('languages', 10)
            output_file = rules_dir / f"{lang_priority}-{lang}.mdc"
            files_to_render.append((lang_template, output_file))
            rule_counter += 1
            print(f"      ✅ {lang_priority}-{lang}.mdc")
        
        # 框架特定规则
        framework = config.get('framework', 'flutter')
        fw_rules_dir = self.project_init_dir / "templates" / "rules" / "frameworks"
        # 尝试查找带前缀的文件（如 20-flutter.mdc.template）或不带前缀的文件（如 flutter.mdc.template）
        fw_template = None
        for pattern in [f"20-{framework}.mdc.template", f"{framework}.mdc.template"]:
            candidate = fw_rules_dir / pattern
            if candidate.exists():
                fw_template = candidate
                break
        
        if fw_template:
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
            platform_rules_dir = self.project_init_dir / "templates" / "rules" / "platforms"
            # 尝试查找带前缀的文件（如 30-android.mdc.template）或不带前缀的文件（如 android.mdc.template）
            platform_template = None
            for pattern in [f"30-{platform}.mdc.template", f"{platform}.mdc.template"]:
                candidate = platform_rules_dir / pattern
                if candidate.exists():
                    platform_template = candidate
                    break
            
            if platform_template:
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
        print("   coldstart export <目标项目目录>")
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
        
        # 准备模板渲染参数
        template_values = {
            'GENERATION_DATE': datetime.now().isoformat(),
            'PROJECT_NAME': config.get('projectName', '未命名项目'),
            'PROJECT_DESCRIPTION': config.get('projectDescription', ''),
            'LANGUAGE_ID': config.get('language', 'dart'),
            'PROGRAMMING_LANGUAGE': config.get('languageName', 'Dart'),
            'CODE_LANGUAGE': config.get('codeLanguage', 'dart'),
            'FRAMEWORK_ID': config.get('framework', 'flutter'),
            'FRAMEWORK': values.get('FRAMEWORK', 'Flutter'),
            'BUILD_TOOL': config.get('buildTool', 'Flutter CLI'),
            'PLATFORMS': [
                {'id': p, 'name': p.capitalize()} 
                for p in config.get('platforms', ['web'])
            ],
            'INJECTED_MODULES': [],
            'IMPLEMENTED_PLANS': implemented_plans,
            'IMPLEMENTED_RULES': implemented_rules,
            'ENABLE_GITHUB_ACTION': config.get('enableGitHubAction', False),
            'LOGGER_SERVICE_CLASS': values.get('LOGGER_SERVICE_CLASS', 'Logger'),
            'LOG_FILE_PATH': values.get('LOG_FILE_PATH', 'logs/app.log'),
            'LOG_COLLECT_SCRIPT_PATH': values.get('LOG_COLLECT_SCRIPT_PATH', 'scripts/collect_logs.sh')
        }
        
        # 使用模板生成项目配置文件
        template_file = self.project_init_dir / "templates" / "config" / "project.json.template"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            rendered_content = template.render(**template_values)
            
            config_file = cold_start_dir / "project.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            print("✅ 项目配置文件已创建: .cold-start/project.json")
        else:
            # 如果模板不存在，使用旧方式（向后兼容）
            project_info = {
                'version': '1.0.0',
                'generatedAt': template_values['GENERATION_DATE'],
                'generatedBy': 'CursorColdStart',
                'project': {
                    'name': template_values['PROJECT_NAME'],
                    'description': template_values['PROJECT_DESCRIPTION']
                },
                'technology': {
                    'language': {
                        'id': template_values['LANGUAGE_ID'],
                        'name': template_values['PROGRAMMING_LANGUAGE'],
                        'codeLanguage': template_values['CODE_LANGUAGE']
                    },
                    'framework': {
                        'id': template_values['FRAMEWORK_ID'],
                        'name': template_values['FRAMEWORK'],
                        'buildTool': template_values['BUILD_TOOL']
                    },
                    'platforms': template_values['PLATFORMS']
                },
                'modules': {
                    'injected': [],
                    'available': []
                },
                'files': {
                    'plans': template_values['IMPLEMENTED_PLANS'],
                    'rules': template_values['IMPLEMENTED_RULES']
                },
                'config': {
                    'enableGitHubAction': template_values['ENABLE_GITHUB_ACTION'] == 'true',
                    'logService': {
                        'class': template_values['LOGGER_SERVICE_CLASS'],
                        'filePath': template_values['LOG_FILE_PATH'],
                        'collectScript': template_values['LOG_COLLECT_SCRIPT_PATH']
                    }
                }
            }
            
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

- **项目名称：** {template_values['PROJECT_NAME']}
- **技术栈：** {template_values['PROGRAMMING_LANGUAGE']} + {template_values['FRAMEWORK']}
- **目标平台：** {', '.join([p['name'] for p in template_values['PLATFORMS']])}
- **初始化时间：** {template_values['GENERATION_DATE']}
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
                        'name': old_config.get('projectName', '未命名项目')
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
                            'name': project_config.get('PROJECT_NAME', '未命名项目')
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
                code_lang = tech.get('language', {}).get('codeLanguage') or tech.get('language', {}).get('id', 'dart')
                params[param_name] = code_lang
                print(f"  {param_name}: {params[param_name]} (使用项目配置)")
                continue
            elif param_name == 'CODE_LANGUAGE_EXT':
                code_lang = tech.get('language', {}).get('codeLanguage') or tech.get('language', {}).get('id', 'dart')
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
        code_lang = tech.get('language', {}).get('codeLanguage') or tech.get('language', {}).get('id', 'dart')
        render_params = {
            'PROJECT_NAME': project_info.get('project', {}).get('name', '未命名项目'),
            'PROGRAMMING_LANGUAGE': tech.get('language', {}).get('name', '未知'),
            'CODE_LANGUAGE': code_lang,
            'CODE_LANGUAGE_EXT': self._get_language_ext(code_lang),
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

