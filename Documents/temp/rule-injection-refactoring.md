# 规则注入逻辑重构报告

## 重构目标

将规则注入逻辑重构为**单一职责模式**和**门面模式**，避免后续修改时出现逻辑错漏。

## 问题分析

### 原有问题

在 `generateRules` 函数中，规则收集逻辑和 IDE 注入逻辑耦合在一起：

1. **违反单一职责原则**：
   - `generateRules` 函数同时负责：
     - 收集规则文件（核心、语言、框架、平台）
     - 为每个 IDE 生成规则
     - 生成功能包规则
     - 清理旧规则
     - 保存文件清单

2. **潜在风险**：
   - 修改规则收集逻辑需要修改 `generateRules`
   - 修改 IDE 注入逻辑也需要修改 `generateRules`
   - 添加新的规则类型需要修改 `generateRules`
   - 添加新的 IDE 需要修改 `generateRules`
   - 容易导致逻辑错漏

## 重构方案

### 架构设计

采用**单一职责模式**和**门面模式**：

```
RuleGeneratorFacade (门面)
    ├── RuleCollector (规则收集器)
    │   └── 单一职责：收集所有规则文件
    └── RuleInjector (规则注入器)
        └── 单一职责：将规则注入到单个 IDE
```

### 组件说明

#### 1. RuleCollector（规则收集器）

**职责**：收集所有规则文件

**方法**：
- `Collect(config)` - 收集所有规则文件
- `collectCoreRules()` - 收集核心规则
- `collectLanguageRules(config)` - 收集语言规则
- `collectFrameworkRules(config)` - 收集框架规则
- `collectPlatformRules(config)` - 收集平台规则

**文件**：`internal/commands/rule_collector.go`

#### 2. RuleInjector（规则注入器）

**职责**：将规则注入到单个 IDE

**方法**：
- `Inject(targetDir, ide, rules)` - 注入规则到指定 IDE
- `injectPackRules(rulesDir, packs)` - 注入功能包规则
- `cleanupObsoleteRules(rulesDir, expectedFiles)` - 清理旧规则
- `saveGeneratedFilesList(rulesDir, files)` - 保存文件清单

**文件**：`internal/commands/rule_injector.go`

#### 3. RuleGeneratorFacade（规则生成门面）

**职责**：统一管理规则生成流程

**方法**：
- `Generate(targetDir, config, ides)` - 生成规则（门面方法）

**流程**：
1. 创建规则收集器
2. 收集所有规则文件
3. 为每个 IDE 创建规则注入器并注入规则

**文件**：`internal/commands/rule_generator.go`

#### 4. 辅助函数

**文件**：`internal/commands/rule_helpers.go`

包含共享的辅助函数：
- `generatePackRules()` - 生成功能包规则
- `loadGeneratedFilesList()` - 加载文件清单
- `saveGeneratedFilesListToFile()` - 保存文件清单

## 重构效果

### 单一职责原则

- ✅ **RuleCollector**：只负责收集规则文件
- ✅ **RuleInjector**：只负责将规则注入到单个 IDE
- ✅ **RuleGeneratorFacade**：只负责协调整个流程

### 门面模式

- ✅ **RuleGeneratorFacade** 提供统一的入口
- ✅ 隐藏了规则收集和注入的复杂性
- ✅ 客户端代码（`generateRules`）只需要调用门面方法

### 可维护性提升

1. **修改规则收集逻辑**：
   - 只需修改 `RuleCollector`
   - 不影响 IDE 注入逻辑

2. **修改 IDE 注入逻辑**：
   - 只需修改 `RuleInjector`
   - 不影响规则收集逻辑

3. **添加新的规则类型**：
   - 在 `RuleCollector` 中添加新的收集方法
   - 不影响其他组件

4. **添加新的 IDE**：
   - 只需在 `RuleGeneratorFacade` 中循环调用 `RuleInjector`
   - 不需要修改规则收集逻辑

### 代码对比

#### 重构前

```go
func (e *Executor) generateRules(...) error {
    // 1. 收集规则（444-498行）
    // 2. 为每个 IDE 生成规则（500-532行）
    // 3. 功能包规则、清理、保存（518-531行）
}
```

**问题**：所有逻辑混在一起，难以维护

#### 重构后

```go
// 门面方法
func (rg *RuleGeneratorFacade) Generate(...) error {
    collector := NewRuleCollector(rg.templateDir)
    rules := collector.Collect(config)
    
    for _, ide := range ides {
        injector := NewRuleInjector(...)
        injector.Inject(targetDir, ide, rules)
    }
}

// Executor 中的调用
func (e *Executor) generateRules(...) error {
    generator := NewRuleGeneratorFacade(e.templateDir, e.init)
    return generator.Generate(targetDir, config, ides)
}
```

**优势**：
- 职责清晰
- 易于测试
- 易于扩展

## 文件结构

```
internal/commands/
├── commands.go              # Executor（使用门面）
├── rule_collector.go        # RuleCollector（规则收集器）
├── rule_injector.go         # RuleInjector（规则注入器）
├── rule_generator.go        # RuleGeneratorFacade（门面）
└── rule_helpers.go          # 辅助函数
```

## 测试建议

1. **单元测试**：
   - 测试 `RuleCollector` 的各个收集方法
   - 测试 `RuleInjector` 的注入方法
   - 测试 `RuleGeneratorFacade` 的生成流程

2. **集成测试**：
   - 测试完整的规则生成流程
   - 测试多 IDE 场景（cursor + codebuddy）

## 总结

通过重构，我们实现了：

1. ✅ **单一职责原则**：每个组件只负责一个明确的职责
2. ✅ **门面模式**：提供统一的入口，隐藏复杂性
3. ✅ **高内聚低耦合**：组件间通过接口通信，不直接依赖实现
4. ✅ **易于维护**：修改某个功能时，只需修改对应的组件
5. ✅ **易于扩展**：添加新功能时，只需添加新的组件或方法

这样的架构设计能够有效避免后续修改时出现逻辑错漏的情况。

