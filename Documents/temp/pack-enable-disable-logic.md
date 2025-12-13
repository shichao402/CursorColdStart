# Pack 启用/禁用逻辑改进

## 问题分析

### 原有问题

在 pack 启用/禁用时，原有的清理逻辑存在以下问题：

1. **pack 禁用时文件清理不完整**：
   - 当 pack 从 `enabled: true` 变为 `enabled: false` 时
   - `generatePackRules` 会跳过该 pack，不生成文件
   - 文件名不会被添加到 `expectedFiles`
   - 理论上 `cleanupObsoleteRules` 应该能清理，但依赖文件清单的完整性

2. **pack 从配置中移除时**：
   - 如果 pack 从配置中完全移除（`packs[packID]` 不存在）
   - `generatePackRules` 会跳过，不生成文件
   - 文件名不会被添加到 `expectedFiles`
   - 清理逻辑可能无法正确识别需要删除的文件

3. **清理逻辑不够健壮**：
   - 只基于文件清单进行清理
   - 没有主动检查 pack 配置状态
   - 可能导致某些文件无法被清理

## 改进方案

### 核心改进

1. **记录所有 pack 的文件名映射**：
   - `generatePackRules` 现在返回两个值：
     - `[]string`：实际生成的文件名列表
     - `map[string]string`：packID -> 文件名的映射（包括所有 pack，无论是否启用）

2. **增强的清理逻辑**：
   - `cleanupObsoleteRules` 现在接收 pack 配置和文件映射
   - 主动检查每个 pack 的状态：
     - 如果 pack 不在配置中 → 删除文件
     - 如果 pack 被禁用（`enabled: false`）→ 删除文件
     - 如果 pack 启用 → 保留文件

### 代码改进

#### 1. `generatePackRules` 函数签名变更

**改进前**：
```go
func generatePackRules(...) []string
```

**改进后**：
```go
func generatePackRules(...) ([]string, map[string]string)
```

返回两个值：
- `[]string`：实际生成的文件名列表（只包括启用的 pack）
- `map[string]string`：所有 pack 的文件名映射（用于清理）

#### 2. 记录所有 pack 的文件名

```go
// 获取 pack 可能生成的文件名（用于清理）
rulesPath := filepath.Join(packsDir, packID, "rules")
var ruleEntries []os.DirEntry
if utils.DirExists(rulesPath) {
    ruleEntries, _ = os.ReadDir(rulesPath)
    // 记录 pack 对应的文件名（用于清理）
    for _, ruleEntry := range ruleEntries {
        if ruleEntry.IsDir() || !strings.HasSuffix(ruleEntry.Name(), ".template") {
            continue
        }
        baseName := strings.TrimSuffix(ruleEntry.Name(), ".template")
        outputFileName := fmt.Sprintf("%d-%s", priority, baseName)
        packFileMap[packID] = outputFileName
    }
}
```

**关键点**：
- 无论 pack 是否启用，都会记录文件名
- 这样清理逻辑可以知道哪些文件属于哪个 pack

#### 3. 增强的清理逻辑

```go
func (ri *RuleInjector) cleanupObsoleteRules(
    rulesDir string, 
    expectedFiles map[string]bool, 
    packs map[string]interface{}, 
    packFileMap map[string]string,
) {
    // 检查禁用的 pack 文件
    for packID, fileName := range packFileMap {
        packConfig, exists := packs[packID].(map[string]interface{})
        shouldDelete := false
        
        if !exists {
            // pack 从配置中移除
            shouldDelete = true
        } else if !getBoolValue(packConfig, "enabled") {
            // pack 被禁用
            shouldDelete = true
        }
        
        if shouldDelete {
            // 检查文件是否在之前的清单中（说明之前生成过）
            if previousFiles != nil && previousFiles[fileName] {
                // 删除文件
                os.Remove(filePath)
                fmt.Printf("  🗑️  已删除 %s (pack %s 已禁用或移除)\n", fileName, packID)
            }
        }
    }
    
    // 清理其他不再需要的文件（基于文件清单）
    // ...
}
```

**关键点**：
- 主动检查每个 pack 的状态
- 如果 pack 被禁用或移除，且文件存在，则删除
- 提供清晰的日志输出

## 改进效果

### 场景 1：Pack 被禁用

**操作**：将 `logging` pack 的 `enabled` 从 `true` 改为 `false`

**改进前**：
- 不生成文件
- 依赖文件清单清理（可能不完整）

**改进后**：
- 不生成文件
- 主动检查 pack 状态
- 明确删除已禁用的 pack 文件
- 输出日志：`🗑️  已删除 40-logging.mdc (pack logging 已禁用或移除)`

### 场景 2：Pack 从配置中移除

**操作**：从 `packs.json` 中完全移除 `logging` pack

**改进前**：
- 不生成文件
- 依赖文件清单清理（可能不完整）

**改进后**：
- 不生成文件
- 主动检查 pack 是否在配置中
- 明确删除已移除的 pack 文件
- 输出日志：`🗑️  已删除 40-logging.mdc (pack logging 已禁用或移除)`

### 场景 3：Pack 被启用

**操作**：将 `logging` pack 的 `enabled` 从 `false` 改为 `true`

**改进前/后**：
- 生成文件
- 添加到 `expectedFiles`
- 正常工作

## 架构优势

### 单一职责原则

- **`generatePackRules`**：负责生成规则文件，同时记录所有 pack 的文件名映射
- **`cleanupObsoleteRules`**：负责清理不再需要的文件，包括禁用的 pack 文件

### 门面模式

- **`RuleInjector`**：统一管理规则注入和清理流程
- 客户端代码只需要调用 `Inject` 方法

### 可维护性

1. **清晰的逻辑**：
   - 生成逻辑和清理逻辑分离
   - 清理逻辑主动检查 pack 状态

2. **易于调试**：
   - 提供清晰的日志输出
   - 明确标识删除原因

3. **易于扩展**：
   - 如果需要添加新的清理规则，只需修改 `cleanupObsoleteRules`
   - 不影响生成逻辑

## 测试建议

1. **单元测试**：
   - 测试 pack 禁用时的清理逻辑
   - 测试 pack 从配置中移除时的清理逻辑
   - 测试 pack 启用时的生成逻辑

2. **集成测试**：
   - 测试完整的 pack 启用/禁用流程
   - 测试多 pack 场景

## 总结

通过改进 pack 启用/禁用逻辑，我们实现了：

1. ✅ **完整的文件清理**：pack 禁用或移除时，文件会被正确清理
2. ✅ **主动检查机制**：清理逻辑主动检查 pack 状态，不依赖文件清单
3. ✅ **清晰的日志输出**：明确标识删除原因
4. ✅ **单一职责原则**：生成逻辑和清理逻辑分离
5. ✅ **易于维护**：逻辑清晰，易于调试和扩展

这样的改进确保了 pack 启用/禁用时的逻辑正确性，避免了文件残留的问题。

