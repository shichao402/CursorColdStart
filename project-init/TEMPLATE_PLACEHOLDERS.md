# 模板占位符说明

> **用途：** 说明规则模板中使用的占位符及其替换规则。

## 占位符列表

### 项目基本信息

| 占位符 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{PROJECT_NAME}` | 项目名称 | .cold-start/project-init/ProjectPlan.md | HelloKnightRemoteCam |
| `{PROJECT_DESCRIPTION}` | 项目描述 | .cold-start/project-init/ProjectPlan.md | 远程相机控制系统 |

### 技术选型

| 占位符 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{PROGRAMMING_LANGUAGE}` | 编程语言 | tech_stack.json | Dart |
| `{FRAMEWORK}` | 框架/平台 | tech_stack.json | Flutter |
| `{BUILD_TOOL}` | 构建工具 | tech_stack.json | Flutter CLI |
| `{CODE_LANGUAGE}` | 代码语言（用于代码块） | tech_stack.json | dart |

### 项目结构

| 占位符 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{MODULE_NAME}` | 模块名称 | tech_stack.json | Client |
| `{MODULE_PATH}` | 模块路径（用于路径限定） | tech_stack.json | client/** |
| `{PACKAGE_NAME}` | 包名/应用名 | tech_stack.json | com.example.app |

### 日志系统

| 占位符 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{LOGGER_SERVICE_CLASS}` | 日志服务类名 | 代码生成 | LoggerService |
| `{LOG_FILE_PATH}` | 日志文件路径 | tech_stack.json | ~/Library/Application Support/com.example.app/logs/ |
| `{LOG_COLLECT_SCRIPT_PATH}` | 日志收集脚本路径 | 脚本生成 | scripts/collect_all_logs.sh |
| `{LOG_COLLECT_COMMAND}` | 日志收集命令 | 脚本生成 | ./scripts/collect_all_logs.sh |
| `{ADDITIONAL_API_METHODS}` | 额外的API方法 | 代码生成 | - 下载日志：`logger.logDownload(...)` |

### 部署脚本

| 占位符 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| `{DEPLOY_SCRIPTS_DESCRIPTION}` | 部署脚本描述 | 脚本生成 | ### 手机端部署... |
| `{DEPLOY_STEPS_DESCRIPTION}` | 部署步骤描述 | 脚本生成 | 1. 使用部署脚本... |
| `{DEPLOY_COMMANDS_DESCRIPTION}` | 部署命令描述 | 脚本生成 | **手机端部署：** `cd server && ./scripts/deploy.sh` |

## 替换规则

### AI助手替换流程

1. **读取模板文件** - 读取 `.mdc.template` 文件
2. **获取替换值** - 从以下来源获取值：
   - `.cold-start/project-init/ProjectPlan.md` - 项目基本信息
   - `tech_stack.json` - 技术选型信息
   - 代码生成结果 - 日志服务类名等
   - 脚本生成结果 - 脚本路径等
3. **替换占位符** - 使用实际值替换所有占位符
4. **保存更新后的模板** - 保存为 `.mdc` 文件

### 替换示例

**模板内容：**
```markdown
# {PROJECT_NAME} 项目核心规则

使用 `{LOGGER_SERVICE_CLASS}` 单例
```

**替换后：**
```markdown
# HelloKnightRemoteCam 项目核心规则

使用 `LoggerService` 单例
```

## 特殊占位符处理

### `{ADDITIONAL_API_METHODS}`

如果日志服务有额外的API方法（如下载日志、API日志等），应该替换为：

```markdown
- 下载日志：`logger.logDownload('操作', details: '详情')`
- API日志：`logger.logApiCall()` / `logger.logApiResponse()`
```

如果没有额外方法，应该替换为空字符串。

### `{DEPLOY_SCRIPTS_DESCRIPTION}`

根据项目结构生成部署脚本描述：

**单模块项目：**
```markdown
### 部署脚本（强制使用）

**路径：** `scripts/deploy.sh`

**使用方式：**
```bash
./scripts/deploy.sh --debug
```
```

**多模块项目：**
```markdown
### 手机端部署（强制使用）

**路径：** `server/scripts/deploy.sh`

**使用方式：**
```bash
cd server && ./scripts/deploy.sh --debug
```

### Mac客户端部署（强制使用）

**路径：** `client/scripts/deploy.sh`

**使用方式：**
```bash
cd client && ./scripts/deploy.sh --debug --macos
```
```

### `{MODULE_PATH}` 和路径限定

如果项目有多个模块，需要在 `01-logging.mdc` 中使用路径限定：

**模板：**
```markdown
### {MODULE_NAME}模块

[{MODULE_PATH}]
使用 `{LOGGER_SERVICE_CLASS}` 单例
```

**替换后（多模块）：**
```markdown
### 客户端（Client）

[client/**]
使用 `ClientLoggerService` 单例

### 手机端（Server）

[server/**]
使用 `LoggerService` 单例
```

**替换后（单模块）：**
```markdown
### 应用模块

[**]
使用 `LoggerService` 单例
```

## 验证占位符替换

替换完成后，AI应该验证：

1. ✅ 所有占位符都已替换（没有遗留的 `{...}`）
2. ✅ 路径限定语法正确（`[path/**]` 格式）
3. ✅ 代码块语言标记正确（`{CODE_LANGUAGE}` 已替换）
4. ✅ 脚本路径存在且正确
5. ✅ 日志路径格式正确

## 注意事项

1. **大小写敏感** - 占位符区分大小写
2. **完整替换** - 确保所有占位符都被替换
3. **格式保持** - 替换时保持Markdown格式
4. **路径格式** - 确保路径格式符合项目结构

