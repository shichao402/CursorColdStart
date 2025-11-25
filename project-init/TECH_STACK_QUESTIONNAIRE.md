# 技术选型问答模板

> **用途：** AI助手使用此模板收集项目的技术选型信息。

## 问答流程

AI助手将按照以下顺序询问用户，并记录答案。

### 1. 编程语言

**问题：** 项目使用什么编程语言？

**选项：**
- Dart
- JavaScript/TypeScript
- Python
- Java/Kotlin
- Swift
- Go
- Rust
- 其他（请说明）

**记录字段：** `programming_language`

---

### 2. 框架/平台

**问题：** 项目使用什么框架或平台？

**根据编程语言显示不同选项：**

**如果选择 Dart：**
- Flutter（移动端/桌面端）
- Dart（纯Dart项目）

**如果选择 JavaScript/TypeScript：**
- React
- Vue
- Angular
- Node.js（后端）
- Next.js
- 其他（请说明）

**如果选择 Python：**
- Django
- Flask
- FastAPI
- 其他（请说明）

**记录字段：** `framework`

---

### 3. 目标平台

**问题：** 项目需要支持哪些平台？（可多选）

**选项：**
- Android
- iOS
- macOS
- Windows
- Linux
- Web
- 其他（请说明）

**记录字段：** `target_platforms`（数组）

---

### 4. 构建工具

**问题：** 项目使用什么构建工具？

**根据框架显示不同选项：**

**如果选择 Flutter：**
- Flutter CLI（默认）

**如果选择 Node.js：**
- npm
- yarn
- pnpm

**如果选择 Android：**
- Gradle

**如果选择 iOS/macOS：**
- Xcode

**记录字段：** `build_tool`

---

### 5. 项目结构

**问题：** 项目是否有多个模块？（如客户端+服务端）

**选项：**
- 单一模块
- 多模块（请说明模块名称和用途）

**如果多模块：**
- 模块1名称：[填写]
- 模块1用途：[填写]
- 模块2名称：[填写]
- 模块2用途：[填写]
- ...

**记录字段：** `project_structure`（对象）

---

### 6. 日志需求

**问题：** 项目需要什么样的日志系统？

**选项：**
- [ ] 需要独立的日志文件
- [ ] 需要日志收集脚本
- [ ] 需要日志轮转策略
- [ ] 需要多平台日志收集（移动端+桌面端）
- [ ] 其他需求：[填写]

**记录字段：** `logging_requirements`（数组）

---

### 7. 部署需求

**问题：** 项目需要什么样的部署方式？

**选项：**
- [ ] 需要自动化部署脚本
- [ ] 需要多平台部署支持
- [ ] 需要CI/CD集成
- [ ] 需要开发环境快速部署
- [ ] 其他需求：[填写]

**记录字段：** `deployment_requirements`（数组）

---

### 8. 日志文件路径

**问题：** 日志文件应该存储在什么位置？

**根据平台显示不同选项：**

**Android：**
- `/data/data/[包名]/files/logs/`（默认）
- 自定义路径：[填写]

**macOS：**
- `~/Library/Application Support/[应用名]/logs/`（默认）
- 自定义路径：[填写]

**Windows：**
- `%APPDATA%/[应用名]/logs/`（默认）
- 自定义路径：[填写]

**记录字段：** `log_paths`（对象，按平台）

---

### 9. 包名/应用名

**问题：** 项目的包名或应用名是什么？

**格式要求：**
- Android：`com.example.appname`
- iOS/macOS：`com.example.appname`
- 其他平台：[说明格式]

**记录字段：** `package_name` 或 `app_name`

---

### 10. 其他特殊需求

**问题：** 项目是否有其他特殊需求或约束？

**记录字段：** `special_requirements`（文本）

---

## 答案记录格式

AI助手应该将答案记录为JSON格式：

```json
{
  "programming_language": "Dart",
  "framework": "Flutter",
  "target_platforms": ["Android", "macOS", "Windows"],
  "build_tool": "Flutter CLI",
  "project_structure": {
    "type": "multi-module",
    "modules": [
      {
        "name": "client",
        "purpose": "客户端应用",
        "platforms": ["macOS", "Windows"]
      },
      {
        "name": "server",
        "purpose": "服务端应用",
        "platforms": ["Android"]
      }
    ]
  },
  "logging_requirements": [
    "独立日志文件",
    "日志收集脚本",
    "日志轮转策略",
    "多平台日志收集"
  ],
  "deployment_requirements": [
    "自动化部署脚本",
    "多平台部署支持"
  ],
  "log_paths": {
    "android": "/data/data/com.example.app/files/logs/",
    "macos": "~/Library/Application Support/com.example.app/logs/",
    "windows": "%APPDATA%/com.example.app/logs/"
  },
  "package_name": "com.example.app",
  "special_requirements": "无"
}
```

## 使用说明

1. **AI读取项目计划文档** - 从 `.cold-start/project-init/ProjectPlan.md` 中提取初步信息
2. **生成问题** - 根据项目计划文档，生成需要确认的问题
3. **逐个询问** - 按照模板顺序询问用户
4. **记录答案** - 将答案记录为JSON格式
5. **生成确认清单** - 生成技术选型确认清单供用户确认

## 确认流程

询问完成后，AI应该：

1. **生成确认清单** - 将所有答案整理为易读的格式
2. **请求确认** - 询问用户是否确认所有技术选型
3. **保存答案** - 将答案保存为 `tech_stack.json` 文件
4. **继续下一步** - 确认后继续执行初始化计划

