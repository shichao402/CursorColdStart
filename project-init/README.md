# 项目初始化系统

> **用途：** 这是一个自动化的项目初始化系统，AI助手可以按照固化的计划逐步引导完成项目起步。

## 📁 文件说明

### 核心文件

1. **`00-PROJECT_INIT_RULE.mdc`** - 项目初始化规则（最重要）
   - AI助手必须遵循的规则文件
   - 定义了触发条件和执行流程
   - 必须复制到项目的 `.cursor/rules/` 目录

2. **`AI_EXECUTION_INSTRUCTIONS.md`** - AI助手执行指令
   - 详细的执行步骤说明
   - 每个步骤的具体操作和验证方法
   - AI助手必须严格按照此文档执行

3. **`PROJECT_INIT_PLAN.md`** - 项目初始化计划（参考文档）
   - 定义了完整的初始化流程
   - 包含所有步骤和AI操作说明
   - 供人类阅读和理解

4. **`ProjectPlan.md.template`** - 项目计划文档模板
   - 新项目应该基于此模板创建 `ProjectPlan.md`
   - 包含项目基本信息、技术选型、项目结构等

5. **`TECH_STACK_QUESTIONNAIRE.md`** - 技术选型问答模板
   - AI助手使用此模板收集技术选型信息
   - 包含所有问题和答案格式

6. **`TEMPLATE_PLACEHOLDERS.md`** - 模板占位符说明
   - 说明规则模板中使用的占位符及其替换规则
   - AI助手替换模板时参考此文档

### 工具脚本

- `start.sh [项目目录]` - 交互式启动脚本
  - 自动完成初始化系统设置
  - 交互式收集核心项目信息（项目名称、编程语言、框架、平台）
  - 生成 JSON 配置文件（project-config.json）
  - 设置AI助手规则文件
  - 验证设置完整性
  - 支持指定项目目录作为参数，或使用当前目录

- `finish.sh [项目目录]` - 清理脚本
  - 清理初始化过程中创建的临时文件
  - 交互式确认每个清理操作
  - 保留项目核心文件（规则、代码、脚本）
  - 支持指定项目目录作为参数，或使用当前目录

### 模板文件

#### 规则模板
- `templates/rules/*.mdc.template` - 规则模板文件
  - `00-core.mdc.template` - 核心规则模板
  - `01-logging.mdc.template` - 日志规则模板
  - `02-scripts.mdc.template` - 脚本规则模板
  - `03-debugging.mdc.template` - 调试规则模板
  - `04-development.mdc.template` - 开发规则模板

#### 计划模板
- `templates/plans/00-project-init-plan.mdc` - 项目初始化计划模板
  - AI助手根据 ProjectPlan.md 和技术选型生成
  - 保存到 `.cursor/plans/00-project-init-plan.mdc`
  - 用于跟踪初始化进度

#### 其他模板（可选，需要根据项目创建）
- `templates/logger_service_template.{language}` - 日志服务代码模板
- `templates/collect_logs_template.sh` - 日志收集脚本模板
- `templates/deploy_scripts_template/` - 部署脚本模板目录

## 🚀 使用流程

### 快速开始（推荐）

使用交互式脚本完成设置：

```bash
# 方法1：在当前项目目录运行（推荐）
# 1. 复制 project-init 目录到你的项目
cp -r /path/to/CursorColdStart/project-init /path/to/your-project/.cold-start/project-init

# 2. 在项目根目录运行启动脚本
cd /path/to/your-project
./.cold-start/project-init/start.sh

# 方法2：指定目标项目目录
# 从任何位置运行，指定项目目录
/path/to/CursorColdStart/project-init/start.sh /path/to/your-project

# 脚本会交互式地完成：
# - 复制初始化系统文件
# - 交互式收集核心项目信息（项目名称、编程语言、框架、平台）
# - 自动生成配置文件（.cold-start/project-init/project-config.json）
# - 设置AI助手规则文件
# - 创建计划目录
# - 验证设置

# 3. AI 助手会读取配置文件并继续初始化流程

# 4. 在 Cursor 中告诉 AI 助手：
# "请按照 PROJECT_INIT_PLAN.md 开始项目初始化"
# 或简单说："开始项目初始化"

# 5. 初始化完成后，清理临时文件（可选）
./.cold-start/project-init/finish.sh
# 或指定目录：
/path/to/CursorColdStart/project-init/finish.sh /path/to/your-project
```

### 手动设置流程

如果不使用脚本，可以手动完成：

#### 1. 复制初始化系统

```bash
# 复制整个 project-init 目录到新项目
cp -r /path/to/CursorColdStart/project-init /path/to/your-project/.cold-start/project-init
```

#### 2. 创建项目计划文档

在新项目根目录创建 `ProjectPlan.md`：

```bash
# 复制模板
# ProjectPlan.md 现在在 .cold-start/project-init/ 目录内，由 start.sh 自动创建

# 编辑填写项目信息
# ...
```

#### 3. 设置AI助手规则

```bash
# 创建规则目录
mkdir -p .cursor/rules

# 复制初始化规则文件
cp .cold-start/project-init/00-PROJECT_INIT_RULE.mdc .cursor/rules/
```

#### 4. 启动初始化流程

告诉AI助手开始初始化：

```
请按照 PROJECT_INIT_PLAN.md 开始项目初始化
```

### AI助手执行流程

AI助手将：

1. **读取项目配置文件** - 从 `.cold-start/project-init/project-config.json` 获取核心信息
2. **生成项目初始化计划** - 根据配置文件生成 `.cursor/plans/00-project-init-plan.mdc`
3. **技术选型确认** - 根据配置文件信息，询问用户确认或补充细节
4. **逐步实施** - 按照计划文件中的步骤执行：
   - 每步执行前读取计划文件了解当前步骤
   - 执行步骤操作
   - 更新计划文件中的状态和进度
5. **验证完成** - 确保所有步骤完成，生成报告

### 完成初始化

初始化完成后：
- AI助手会生成 `PROJECT_INIT_REPORT.md` 报告
- 可以使用 `finish.sh` 脚本清理临时文件（可选）

## 📋 初始化步骤概览

### 阶段1：项目理解和技术选型
- ✅ 阅读项目计划文档
- ✅ 技术选型确认（问答）

### 阶段2：日志系统初始化
- ✅ 创建统一日志服务
- ✅ 创建日志收集脚本
- ✅ 更新日志规则模板
- ✅ 应用日志规则

### 阶段3：脚本系统初始化
- ✅ 创建部署脚本
- ✅ 更新脚本规则模板
- ✅ 应用脚本规则

### 阶段4：调试规则初始化
- ✅ 更新调试规则模板
- ✅ 应用调试规则

### 阶段5：核心规则初始化
- ✅ 更新核心规则模板
- ✅ 应用核心规则

### 阶段6：开发规则初始化（可选）
- ✅ 更新开发规则模板
- ✅ 应用开发规则

### 阶段7：验证和完成
- ✅ 验证规则文件
- ✅ 验证代码文件
- ✅ 生成初始化报告

## 🎯 成功标准

项目初始化成功的标准：
- ✅ 所有规则文件已创建并应用
- ✅ 日志服务已实现并可用
- ✅ 日志收集脚本已创建
- ✅ 部署脚本已创建
- ✅ 所有规则文件格式正确
- ✅ 项目可以开始正常开发

## 📝 注意事项

1. **项目配置文件必须存在** - AI助手需要先读取 `.cold-start/project-init/project-config.json`（由 start.sh 自动生成）
2. **技术选型需要用户确认** - 问答环节需要用户参与
3. **模板文件需要准备** - 规则模板和代码模板需要提前准备
4. **逐步执行** - AI助手会逐步执行，每步完成后报告进度
5. **使用脚本简化流程** - 推荐使用 `start.sh` 和 `finish.sh` 脚本自动化设置和清理

## 🔧 自定义

如果需要自定义初始化流程：

1. **修改计划** - 编辑 `PROJECT_INIT_PLAN.md`
2. **添加步骤** - 在计划中添加新的步骤
3. **修改模板** - 更新规则模板或代码模板
4. **调整流程** - 根据项目特点调整执行顺序

## 📚 相关文档

### 核心文档
- `00-PROJECT_INIT_RULE.mdc` - 项目初始化规则（AI规则文件，最重要）
- `AI_EXECUTION_INSTRUCTIONS.md` - AI助手执行指令（AI必须遵循）
- `PROJECT_INIT_PLAN.md` - 详细的初始化计划（人类阅读参考）

### 模板和示例
- `ProjectPlan.md.template` - 项目计划文档模板
- `TECH_STACK_QUESTIONNAIRE.md` - 技术选型问答模板
- `TEMPLATE_PLACEHOLDERS.md` - 模板占位符说明
- `templates/plans/00-project-init-plan.mdc` - 计划文件模板

## 🔧 如何让AI助手识别此系统

### 方法1：复制规则文件到项目（推荐）

将 `00-PROJECT_INIT_RULE.mdc` 复制到项目的 `.cursor/rules/` 目录：

```bash
# 在新项目中
mkdir -p .cursor/rules
cp .cold-start/project-init/00-PROJECT_INIT_RULE.mdc .cursor/rules/
```

这样AI助手就能识别项目初始化系统。

### 方法2：在项目规则中引用

在项目的 `.cursor/rules/00-core.mdc` 中添加：

```markdown
## 项目初始化系统

如果用户要求"开始项目初始化"或"按照 PROJECT_INIT_PLAN.md 开始项目初始化"，
AI助手必须：
1. 读取 `.cold-start/project-init/00-PROJECT_INIT_RULE.mdc`
2. 按照规则执行项目初始化流程
```

## 📋 计划系统

### 计划文件的作用

项目初始化系统使用 `.cursor/plans/` 目录来管理初始化计划：

1. **生成计划文件** - AI助手根据 .cold-start/project-init/project-config.json 生成 `.cursor/plans/00-project-init-plan.mdc`
2. **跟踪进度** - 计划文件中每个步骤都有状态标记（⏳ 待执行 / ✅ 已完成）
3. **执行依据** - AI助手按照计划文件中的步骤执行
4. **更新状态** - 每完成一个步骤，AI助手更新计划文件中的状态和进度

### 计划文件结构

```
.cursor/plans/
└── 00-project-init-plan.mdc
    ├── 项目信息（从 .cold-start/project-init/project-config.json 读取）
    ├── 初始化目标
    ├── 执行步骤（每个步骤有状态标记）
    ├── 进度跟踪（完成率统计）
    └── 执行日志
```

计划系统的详细说明已包含在 `AI_EXECUTION_INSTRUCTIONS.md` 和 `PROJECT_INIT_PLAN.md` 中。

---

**提示：** 这是一个自动化系统，AI助手会按照计划逐步执行，用户只需要在技术选型环节提供信息即可。

**重要：** 确保AI助手能够访问 `00-PROJECT_INIT_RULE.mdc` 规则文件，这样AI助手才能识别并执行项目初始化系统。

