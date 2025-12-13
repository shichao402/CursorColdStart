# 代码审查 - 发现的问题

## 问题 1: `copyCommonRules` 违反单一职责原则

### 问题描述

`copyCommonRules` 函数在 `firstInit` 中使用，但它直接实现了规则注入逻辑，与 `RuleInjector` 有重复代码。

**位置**：`internal/commands/commands.go:351-394`

**问题**：
- 直接实现了规则注入逻辑（与 `RuleInjector` 重复）
- 没有使用统一的 `RuleGeneratorFacade`
- 违反了单一职责原则

### 改进方案

应该使用 `RuleGeneratorFacade` 来统一处理，但需要支持"仅核心规则"的模式（首次初始化时配置不完整）。

## 问题 2: 工具函数位置

### 问题描述

`getIDERulesDir` 和 `getIDEDirName` 是工具函数，放在 `commands.go` 中不够清晰。

**位置**：`internal/commands/commands.go:396-426`

**改进方案**：
- 可以考虑提取到独立的工具文件
- 或者保留在当前文件（如果只在这个包内使用）

## 问题 3: 首次初始化时的规则注入逻辑

### 问题描述

`copyCommonRules` 和 `generateRules` 都在做规则注入，但实现方式不同：
- `copyCommonRules`：只处理核心规则，使用最小化的占位符值
- `generateRules`：处理所有规则，使用完整的配置值

**改进方案**：
- 统一使用 `RuleGeneratorFacade`
- 支持"仅核心规则"模式（首次初始化）

