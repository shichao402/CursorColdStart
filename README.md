# CursorColdStart

项目AI冷启动初始化系统 - 使用Python实现，支持跨平台（Windows/Mac/Linux）

## 🚀 快速开始

### 安装依赖（自动创建虚拟环境）

**方式1：使用Python脚本（推荐，跨平台）**
```bash
python install.py
```

**方式2：使用Shell脚本（Mac/Linux）**
```bash
./install.sh
```

**方式3：使用Batch脚本（Windows）**
```cmd
install.bat
```

安装脚本会自动：
- ✅ 检查Python版本（需要3.6+）
- ✅ 创建虚拟环境（`.venv/`目录）
- ✅ 在虚拟环境中安装依赖
- ✅ 验证安装是否成功

### 使用方式（推荐：使用包装脚本，无需激活虚拟环境）

**方式1：使用包装脚本（推荐，最简单）**
```bash
# Mac/Linux
./start [目标项目目录]

# Windows
start.bat [目标项目目录]
```

启动后进入**交互式命令模式**，输入命令进行操作。

包装脚本会自动使用虚拟环境，**无需手动激活**！

> **注意：** 脚手架已模块化重构，入口脚本从 `start.py` 重命名为 `coldstart.py`，但包装脚本（`start`/`start.bat`）保持不变，会自动调用新的入口脚本。

**方式2：直接使用Python脚本**
```bash
# Mac/Linux
.venv/bin/python coldstart.py [目标项目目录]

# Windows
.venv\Scripts\python.exe coldstart.py [目标项目目录]
```

**方式3：激活虚拟环境后使用（传统方式）**
```bash
# Mac/Linux
source .venv/bin/activate
python coldstart.py [目标项目目录]

# Windows
.venv\Scripts\activate.bat
python coldstart.py [目标项目目录]
```

### 交互式命令系统

启动后进入交互式命令模式，支持以下命令：

#### 根级别命令

- `init` - 项目初始化流程（分类命令）
- `inject` - 模块化规则注入
- `add-module` - 快速创建新模块规则
- `extract-rules` - 从目标项目提取规则并反哺
- `init-config` - 为现有项目补充配置信息
- `help` - 显示帮助信息
- `exit` - 退出程序

#### init 分类下的命令

进入 `init` 分类后，可以使用：

- `process` - 阶段2：处理模板文件
- `export` - 阶段3：导出到目标项目
- `help` - 显示init命令帮助
- `back` - 返回上一级

#### 使用示例

```bash
# 启动交互式脚手架
coldstart /path/to/target-project
# 或
python coldstart.py /path/to/target-project

# 进入交互式命令模式
[root] > help                    # 查看可用命令
[root] > init                    # 进入init分类
[init] > help                    # 查看init下的命令
[init] > process                 # 执行阶段2：处理
[init] > export                  # 执行阶段3：导出
[init] > back                    # 返回根级别
[root] > inject                  # 执行模块注入
[root] > add-module              # 创建新模块规则
[root] > extract-rules           # 从目标项目提取规则
[root] > init-config             # 为现有项目补充配置信息
[root] > exit                    # 退出程序
```

**提示：**
- 分类命令（如 `init`）可以直接执行，也可以进入分类后使用子命令
- 如果分类命令有handler且提供了参数，会直接执行
- 输入 `help` 可以随时查看当前级别的可用命令

## 📋 功能特性

- ✅ **跨平台支持** - Windows/Mac/Linux
- ✅ **Jinja2模板引擎** - 专业的模板处理
- ✅ **三阶段流程** - 初始化 → 处理 → 导出
- ✅ **组件化规则** - 根据项目配置自动选择规则
- ✅ **配置驱动** - 所有选项通过配置文件管理
- ✅ **模块化规则注入** - 在项目开发过程中动态注入模块化规则

## 📁 项目结构

```
CursorColdStart/
├── coldstart.py               # 主入口脚本（Python）
├── coldstart/                  # 模块化代码目录
│   ├── __init__.py            # 模块初始化
│   ├── initializer.py         # 项目初始化器
│   ├── commands.py             # 交互式命令系统
│   └── main.py                # 主入口函数
├── start                       # 启动脚本（Mac/Linux，自动使用虚拟环境）
├── start.bat                   # 启动脚本（Windows，自动使用虚拟环境）
├── install.py                  # 依赖安装脚本（Python，跨平台）
├── install.sh                  # 依赖安装脚本（Mac/Linux）
├── install.bat                 # 依赖安装脚本（Windows）
├── requirements.txt            # Python依赖
├── .venv/                      # Python虚拟环境（自动创建，已忽略）
├── project-init/
│   ├── templates/              # Jinja2模板
│   │   ├── plans/              # 计划模板
│   │   ├── rules/              # 规则模板
│   │   └── modules/            # 模块化规则模板
│   ├── options.json            # 选项配置
│   └── config.template.json    # 配置文件模板
└── .cold-start-staging/        # 临时工作目录（已忽略）
```

## 🔧 技术栈

- **Python 3** - 主编程语言
- **Jinja2** - 模板引擎
- **JSON** - 配置文件格式

## 🔌 模块化规则注入

### 功能说明

在项目开发过程中，你可以使用模块注入功能向现有项目添加新的模块化规则。例如，当你需要实现"更新模块"时，可以运行模块注入命令，脚手架会：

1. 读取目标项目的完整参数
2. 列出可用的模块化规则
3. 检查模块兼容性
4. 收集模块特定参数
5. 根据项目参数和模块参数定制规则
6. 将规则注入到目标项目

### 使用方式

```bash
# Mac/Linux
./start inject <目标项目目录>

# Windows
start.bat inject <目标项目目录>

# 或直接使用Python
coldstart inject <目标项目目录>
# 或
python coldstart.py inject <目标项目目录>
```

### 使用场景示例

假设你正在开发一个Flutter应用，到了某个阶段需要添加"更新模块"：

1. **运行模块注入命令**
   ```bash
   coldstart inject /path/to/your/flutter-project
   # 或
   python coldstart.py inject /path/to/your/flutter-project
   ```

2. **选择模块**
   - 脚手架会列出所有可用的模块（如：更新模块）
   - 选择"更新模块"

3. **配置模块参数**
   - 输入模块名称（如：AppUpdate）
   - 输入模块路径（如：lib/update）
   - 输入其他模块特定参数

4. **规则注入完成**
   - 脚手架会将定制后的规则注入到项目的 `.cursor/rules/` 目录
   - 规则会根据项目参数（Flutter、Dart等）和模块参数进行定制

5. **使用AI实现模块**
   - 切换到目标项目
   - 在Cursor中告诉AI："开始实现更新模块"
   - AI会根据注入的规则逐步完成模块的设计和编写

### 模块化规则结构

模块化规则存储在 `project-init/templates/modules/` 目录下，每个模块包含：

- `module.config.json` - 模块配置文件（定义参数、兼容性等）
- `*.mdc.template` - 模块规则模板（使用Jinja2语法）

### 快速创建新模块规则

在编码过程中需要新的通用模块时，使用 `add-module` 命令：

```bash
[root] > add-module
```

脚手架会交互式地收集：
- 模块基本信息（ID、名称、描述、类型）
- 兼容性信息（支持的语言和框架）
- 模块参数定义

创建完成后，你可以：
1. 编辑生成的模块规则模板，完善规则内容
2. 使用 `inject` 命令将模块注入到目标项目

### 为现有项目补充配置信息

如果目标项目缺少 `.cold-start/project.json` 配置文件，可以使用 `init-config` 命令补充：

```bash
[root] > init-config /path/to/your/project
```

脚手架会：
1. **自动检测项目信息**
   - 从规则文件检测技术栈（语言、框架）
   - 从项目文件检测平台（如 pubspec.yaml、package.json 等）
   - 扫描已实施的计划文件和规则文件

2. **交互式收集配置**
   - 项目名称和描述
   - 编程语言选择（带检测推荐）
   - 框架选择（带检测推荐）
   - 目标平台选择（可多选）
   - GitHub Actions 启用选项

3. **生成配置文件**
   - 创建 `.cold-start/project.json` 配置文件
   - 创建 `.cold-start/README.md` 说明文件
   - 记录已实施的文件列表

**使用场景：**
- 项目是通过其他方式创建的，缺少配置信息
- 配置文件被误删，需要重新生成
- 需要更新项目配置信息

### 从项目中提取规则并反哺

在编码过程中，AI帮你优化了规则，使用 `extract-rules` 命令反哺：

```bash
[root] > extract-rules /path/to/your/project
```

脚手架会：
1. 扫描目标项目的规则文件
2. 识别可提取的通用规则
3. 让你选择要提取的规则
4. 将规则保存到 `project-init/extract/rules/` 目录
5. 更新整合日志

提取后，你可以：
1. 审查提取的规则，确保通用性
2. 手动整合到对应的模板文件
3. 供其他项目使用

### 手动创建自定义模块

如果需要更精细的控制，也可以手动创建：

1. 在 `project-init/templates/modules/` 下创建模块目录
2. 创建 `module.config.json` 配置文件
3. 创建 `*.mdc.template` 规则模板文件
4. 使用Jinja2语法定义可定制的占位符

## 📝 详细文档

更多使用说明请参考：`project-init/README.md`

