# CursorColdStart

项目 AI 冷启动初始化系统 - 使用 Go 实现，支持跨平台（Windows/Mac/Linux）

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/shichao402/CursorColdStart.git
cd CursorColdStart

# 构建
make build
```

### 使用方式

```bash
# 初始化项目（首次）
./bin/coldstart init ./my-project

# 查看可用选项
./bin/coldstart list

# 查看帮助
./bin/coldstart help
```

## 📋 工作流程

### 1. 首次初始化

```bash
./bin/coldstart init ./my-project
```

生成：
- `.cursor-cold-start/config/project.json` - 项目信息（空）
- `.cursor-cold-start/config/technology.json` - 技术栈配置（空）
- `.cursor-cold-start/config/features.json` - 功能特性配置
- `.cursor/rules/00-core.mdc` - 通用规则

### 2. 填写配置

让 AI 帮助填写配置文件：

**project.json**
```json
{
  "name": "MyApp",
  "description": "我的应用",
  "version": "1.0.0"
}
```

**technology.json**
```json
{
  "language": "dart",
  "framework": "flutter",
  "platforms": ["android", "ios"]
}
```

### 3. 生成定制规则

```bash
./bin/coldstart init ./my-project
```

根据配置生成：
- `10-dart.mdc` - 语言规则
- `20-flutter.mdc` - 框架规则
- `30-android.mdc` - 平台规则
- 等等...

## 📁 生成的目录结构

```
my-project/
├── .cursor-cold-start/          # CursorColdStart 管理目录
│   ├── config/
│   │   ├── project.json         # 项目信息
│   │   ├── technology.json      # 技术栈配置
│   │   └── features.json        # 功能特性
│   ├── modules/                 # 已注入的模块配置
│   └── README.md
└── .cursor/
    └── rules/                   # Cursor AI 规则
        ├── 00-core.mdc          # 通用规则
        ├── 01-logging.mdc       # 日志规则
        ├── 10-dart.mdc          # 语言规则
        ├── 20-flutter.mdc       # 框架规则
        └── 30-android.mdc       # 平台规则
```

## 🔧 命令参考

| 命令 | 说明 |
|------|------|
| `init <dir>` | 初始化项目（首次生成空配置，再次生成定制规则） |
| `list` | 列出所有可用选项 |
| `list languages` | 列出支持的语言 |
| `list frameworks` | 列出支持的框架 |
| `list platforms` | 列出支持的平台 |
| `list modules` | 列出可用模块 |
| `version` | 显示版本 |
| `help` | 显示帮助 |

## 📝 支持的技术栈

### 语言
- **dart** - Dart (Flutter, 纯 Dart)
- **typescript** - TypeScript/JavaScript (React, Vue, Node.js)
- **python** - Python (Django, FastAPI)
- **kotlin** - Kotlin/Java (Android, Spring)
- **swift** - Swift (iOS)

### 框架
- Flutter, React, Vue, Node.js
- Django, FastAPI
- Android, iOS, Spring

### 平台
- Android, iOS, macOS, Windows, Linux, Web

## 🛠️ 开发

### 项目结构

```
CursorColdStart/
├── cmd/coldstart/           # 主程序入口
├── internal/
│   ├── commands/           # 命令执行器
│   ├── initializer/        # 项目初始化器
│   └── template/           # 模板处理器
├── pkg/utils/               # 工具函数
├── rules_template/          # 规则模板（核心资产）
│   ├── templates/
│   │   ├── rules/          # 规则模板
│   │   └── modules/        # 模块模板
│   └── options.json        # 选项配置
├── Makefile
└── go.mod
```

### 构建命令

```bash
make build        # 构建当前平台
make build-all    # 构建所有平台
make fmt          # 格式化代码
make vet          # 代码检查
make test         # 运行测试
make check        # 全部检查
```

## 📄 License

MIT
