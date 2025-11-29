# 规则整合日志

记录从目标项目中提取并整合的规则。

## 格式说明

- **日期：** 整合日期
- **来源项目：** 提取规则的项目
- **规则文件：** 整合到的模板文件
- **规则内容：** 简要描述
- **优先级：** 高/中/低

---

## 2024-11-26

### Android平台规则 - adb截图自动化

- **来源项目：** [项目名称]
- **规则文件：** `templates/rules/platforms/android.mdc.template`
- **规则内容：** 
  - 禁止要求用户提供截图
  - 必须使用adb自动截图
  - 自动执行截图命令
- **优先级：** 高
- **效果：** 提高调试效率，减少用户操作

### Android平台规则 - logcat日志收集

- **来源项目：** [项目名称]
- **规则文件：** `templates/rules/platforms/android.mdc.template`
- **规则内容：**
  - 优先使用应用统一日志
  - 辅助使用adb logcat收集系统日志
  - 日志收集优先级说明
- **优先级：** 高
- **效果：** 更全面的日志收集策略

---

## 2024-12-19

### 文档管理规则 - 统一文档管理规范

- **来源项目：** 通用规则（用户需求）
- **规则文件：** `templates/rules/common/08-documentation.mdc.template`
- **规则内容：**
  - 所有文档统一管理在 `Documents/` 目录下
  - 过程性文档放在 `Documents/temp/` 并添加到 `.gitignore`
  - 文档分门别类，使用清晰的目录结构
  - 文档命名规范（kebab-case）
  - 文档头部标准格式
  - 文档索引维护
  - 文档状态管理（draft/review/approved/archived）
- **优先级：** 最高
- **效果：** 统一文档管理方式，提高文档可维护性和可查找性，避免文档散乱

### 版本管理规则 - 通用版本管理实践

- **来源项目：** HelloKnightRemoteCam
- **规则文件：** `templates/rules/common/06-version-management.mdc.template`
- **规则内容：**
  - 使用 VERSION.yaml 作为单一数据源
  - 支持多组件独立版本号管理
  - 版本号格式：x.y.z+build（语义化版本号）
  - 自动同步版本号到项目配置文件
  - 版本兼容性检查机制
  - 构建号自动递增
  - 版本服务接口规范
- **优先级：** 高
- **效果：** 统一版本管理方式，适用于所有语言和框架，确保版本号一致性和可追溯性

### GitHub Actions CI/CD 规则 - 自动化发布流程

- **来源项目：** HelloKnightRemoteCam
- **规则文件：** `templates/rules/common/07-github-actions.mdc.template`
- **规则内容：**
  - 两阶段发布流程（构建 + 发布）
  - 构建标签格式：build{version}
  - 发布标签格式：v{version}
  - 构建号自动递增机制
  - 构建产物命名规则（使用 build 替代 + 避免 URL 特殊字符）
  - 更新配置文件自动生成和推送
  - 文件 Hash 计算（SHA256）
  - 固定的 UpdateConfig Release 管理
  - 多平台并行构建
- **优先级：** 高
- **效果：** 完全自动化的 CI/CD 流程，减少人工操作，提高发布效率和可靠性

---

## 待整合规则

### [规则名称]

- **来源项目：** [项目名称]
- **建议分类：** [common/languages/frameworks/platforms]
- **规则内容：** [描述]
- **优先级：** [高/中/低]
- **状态：** 待审查

