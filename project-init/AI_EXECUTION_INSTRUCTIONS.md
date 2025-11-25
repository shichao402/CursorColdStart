# AI助手执行指令

> **重要：** 这是AI助手必须遵循的执行指令。当用户要求"按照PROJECT_INIT_PLAN.md开始项目初始化"时，AI助手必须按照此文档执行。

## 🎯 执行触发

### 触发条件

当用户说以下任何一句话时，AI助手应该开始执行项目初始化流程：

- "请按照 PROJECT_INIT_PLAN.md 开始项目初始化"
- "开始项目初始化"
- "执行项目初始化计划"
- "按照计划初始化项目"

### 执行前检查

AI助手必须首先检查：

1. ✅ **项目计划文档是否存在**
   ```bash
   # 检查 ProjectPlan.md 是否存在
   ls .cold-start/project-init/ProjectPlan.md
   ```
   - 如果不存在，提示用户先创建项目计划文档

2. ✅ **初始化计划文档是否存在**
   ```bash
   # 检查 PROJECT_INIT_PLAN.md 是否存在
   ls .cold-start/project-init/PROJECT_INIT_PLAN.md
   ```
   - 如果不存在，说明系统未正确安装

## 📋 执行流程

### 步骤1：读取项目计划文档

**AI操作：**
```bash
# 读取项目计划文档
cat .cold-start/project-init/ProjectPlan.md
```

**AI任务：**
1. 提取项目名称
2. 提取技术选型信息（初步）
3. 提取项目结构信息
4. 提取特殊需求

**输出：** 生成项目理解摘要，向用户展示

---

### 步骤1.5：生成项目初始化计划文件

**AI操作：**
1. **创建计划目录**
   ```bash
   mkdir -p .cursor/plans
   ```

2. **读取计划模板**
   ```bash
   cat .cold-start/project-init/templates/plans/00-project-init-plan.mdc
   ```

3. **替换占位符**
   - 从 .cold-start/project-init/ProjectPlan.md 读取项目信息
   - 根据项目结构生成文件路径
   - 替换所有占位符（参考 TEMPLATE_PLACEHOLDERS.md）

4. **保存计划文件**
   ```bash
   # 保存到 .cursor/plans/00-project-init-plan.mdc
   ```

**验证：**
- 检查计划文件是否存在
- 检查所有占位符是否已替换（除了技术选型相关的，因为还没确认）

**报告：**
```
AI: ✅ 项目初始化计划已生成：.cursor/plans/00-project-init-plan.mdc
```

---

### 步骤2：技术选型确认

**AI操作：**
1. 读取问答模板：`.cold-start/project-init/TECH_STACK_QUESTIONNAIRE.md`
2. 根据项目计划文档，生成需要确认的问题
3. **逐个询问用户**，记录答案
4. 生成技术选型确认清单

**问答格式：**
```
AI: 根据项目计划文档，我需要确认一些技术选型信息。

问题1：项目使用什么编程语言？
选项：
- Dart
- JavaScript/TypeScript
- Python
- 其他（请说明）

用户：[回答]

AI: 已记录。继续下一个问题...

问题2：项目使用什么框架？
...
```

**记录答案：**
- 创建 `tech_stack.json` 文件保存答案
- 格式参考 `TECH_STACK_QUESTIONNAIRE.md` 中的JSON格式

**确认流程：**
```
AI: 技术选型确认完成。以下是确认的技术选型：

- 编程语言：Dart
- 框架：Flutter
- 目标平台：Android, macOS, Windows
- ...

请确认以上信息是否正确？(是/否)

用户：[确认]

AI: 已确认。开始创建日志系统...
```

---

### 步骤3：创建日志服务

**AI操作：**
1. **读取计划文件**，找到当前步骤
   ```bash
   cat .cursor/plans/00-project-init-plan.mdc
   ```

2. 根据技术选型确定日志服务实现方式
3. 创建日志服务类文件
4. 实现日志文件写入功能
5. 实现日志轮转策略
6. 添加错误日志支持

**文件位置：**
- 根据项目结构确定（如 `lib/services/logger_service.dart`）

**验证：**
- 检查文件是否创建成功
- 检查代码语法是否正确

**更新计划文件：**
- 将步骤2.1的状态更新为 ✅
- 更新进度统计
- 添加执行日志

**报告：**
```
AI: ✅ 日志服务已创建：lib/services/logger_service.dart
AI: 📋 计划已更新：步骤2.1已完成
```

---

### 步骤4：创建日志收集脚本

**AI操作：**
1. 根据平台创建日志收集脚本
2. 配置日志文件路径（从tech_stack.json读取）
3. 实现自动查找最新日志文件
4. 实现日志内容显示

**文件位置：**
- `scripts/collect_all_logs.sh`

**验证：**
- 检查文件是否存在
- 检查是否有执行权限（如果没有，添加）

**报告：**
```
AI: ✅ 日志收集脚本已创建：scripts/collect_all_logs.sh
```

---

### 步骤5：更新日志规则模板

**AI操作：**
1. 读取模板：`.cold-start/project-init/templates/rules/01-logging.mdc.template`
2. 读取占位符说明：`.cold-start/project-init/TEMPLATE_PLACEHOLDERS.md`
3. 替换所有占位符：
   - `{PROJECT_NAME}` → 从.cold-start/project-init/ProjectPlan.md读取
   - `{LOGGER_SERVICE_CLASS}` → 从创建的代码读取
   - `{LOG_FILE_PATH}` → 从tech_stack.json读取
   - `{LOG_COLLECT_SCRIPT_PATH}` → scripts/collect_all_logs.sh
   - 等等...
4. 保存更新后的模板：`01-logging.mdc`（临时文件）

**验证：**
- 检查所有占位符是否已替换
- 检查路径限定语法是否正确

**报告：**
```
AI: ✅ 日志规则模板已更新
```

---

### 步骤6：应用日志规则

**AI操作：**
1. 创建 `.cursor/rules/` 目录（如果不存在）
2. 复制更新后的模板到 `.cursor/rules/01-logging.mdc`
3. 验证文件格式正确

**验证：**
- 检查文件是否存在
- 检查前置元数据 `alwaysApply: true` 是否存在

**报告：**
```
AI: ✅ 日志规则已应用到项目：.cursor/rules/01-logging.mdc
```

---

### 步骤7-12：重复步骤3-6

按照相同流程处理：
- 脚本规则（步骤7-8）
- 调试规则（步骤9-10）
- 核心规则（步骤11-12）
- 开发规则（步骤13-14，可选）

---

### 步骤15：验证和完成

**AI操作：**
1. 验证所有规则文件：
   ```bash
   ls .cursor/rules/*.mdc
   ```
   - 检查文件是否存在
   - 检查格式是否正确

2. 验证代码文件：
   - 日志服务文件是否存在
   - 脚本文件是否存在

3. 生成初始化报告：
   - 创建 `PROJECT_INIT_REPORT.md`
   - 列出所有创建的文件
   - 列出所有应用的规则
   - 提供下一步建议

**报告：**
```
AI: ✅ 项目初始化完成！

已创建的文件：
- lib/services/logger_service.dart
- scripts/collect_all_logs.sh
- scripts/deploy.sh
- .cursor/rules/00-core.mdc
- .cursor/rules/01-logging.mdc
- ...

已应用的规则：
- 日志规则
- 脚本规则
- 调试规则
- ...

下一步建议：
1. 测试日志服务是否正常工作
2. 测试部署脚本是否正常工作
3. 开始开发核心功能
```

## ⚠️ 错误处理

### 如果某个步骤失败

**AI应该：**
1. 报告错误信息
2. 提供修复建议
3. 询问用户：
   ```
   AI: ❌ 步骤X失败：[错误信息]
   
   建议修复方案：[修复建议]
   
   是否重试？(是/否) 或 是否跳过此步骤？(是/否)
   ```

### 如果用户中断

**AI应该：**
1. 保存当前进度
2. 记录已完成步骤
3. 询问用户是否继续

## 📝 执行检查清单

AI助手在执行过程中应该：

- [ ] **生成计划文件** - 在开始执行前，先生成 `.cursor/plans/00-project-init-plan.mdc`
- [ ] **读取计划文件** - 每步执行前，读取计划文件了解当前步骤
- [ ] **更新计划文件** - 每完成一个步骤，更新计划文件中的状态和进度
- [ ] 每完成一个步骤，向用户报告进度
- [ ] 需要用户输入时，明确说明需要什么信息
- [ ] 创建文件后，验证文件是否正确
- [ ] 替换模板后，验证占位符是否全部替换
- [ ] 应用规则后，验证规则文件格式是否正确
- [ ] 完成所有步骤后，生成完整的初始化报告

## 🎯 成功标准

项目初始化成功的标准：
- ✅ 所有规则文件已创建并应用（.cursor/rules/*.mdc）
- ✅ 日志服务已实现并可用
- ✅ 日志收集脚本已创建
- ✅ 部署脚本已创建（如果需要）
- ✅ 所有规则文件格式正确
- ✅ 项目可以开始正常开发

---

**重要提示：** AI助手必须严格按照此文档执行，不能跳过任何步骤。如果遇到问题，应该报告错误并询问用户如何处理。

