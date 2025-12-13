package commands

import (
	"fmt"

	"github.com/cursor-cold-start/cursor-cold-start/internal/initializer"
	"github.com/cursor-cold-start/cursor-cold-start/internal/template"
)

// RuleGeneratorFacade 规则生成门面 - 门面模式：统一管理规则生成流程
type RuleGeneratorFacade struct {
	templateDir string
	init        *initializer.ProjectInitializer
}

// NewRuleGeneratorFacade 创建规则生成门面
func NewRuleGeneratorFacade(templateDir string, init *initializer.ProjectInitializer) *RuleGeneratorFacade {
	return &RuleGeneratorFacade{
		templateDir: templateDir,
		init:        init,
	}
}

// Generate 生成规则（门面方法）
// 统一管理规则收集、注入到多个 IDE 的整个流程
func (rg *RuleGeneratorFacade) Generate(targetDir string, config map[string]interface{}, ides []string) error {
	return rg.GenerateWithMode(targetDir, config, ides, false)
}

// GenerateWithMode 生成规则（支持仅核心规则模式）
// onlyCore: true 表示只生成核心规则（用于首次初始化）
func (rg *RuleGeneratorFacade) GenerateWithMode(targetDir string, config map[string]interface{}, ides []string, onlyCore bool) error {
	// 1. 创建规则收集器
	collector := NewRuleCollector(rg.templateDir)

	// 2. 收集规则文件
	var rules []RuleFile
	if onlyCore {
		// 仅核心规则模式（首次初始化）
		rules = collector.CollectCoreRules()
	} else {
		// 完整模式（更新初始化）
		rules = collector.Collect(config)
	}

	// 3. 准备模板处理器和占位符值
	processor := template.NewProcessor()
	var values map[string]interface{}
	if onlyCore {
		// 使用最小化的占位符值
		values = rg.getMinimalPlaceholderValues()
	} else {
		// 使用完整的占位符值
		values = rg.init.GetPlaceholderValues(config)
	}

	// 4. 为每个 IDE 注入规则
	for _, ide := range ides {
		// 创建规则注入器
		injector := NewRuleInjector(rg.templateDir, processor, values, config)

		// 注入规则
		_, err := injector.Inject(targetDir, ide, rules)
		if err != nil {
			return fmt.Errorf("为 IDE %s 注入规则失败: %w", ide, err)
		}
	}

	return nil
}

// getMinimalPlaceholderValues 获取最小化的占位符值（用于首次初始化）
func (rg *RuleGeneratorFacade) getMinimalPlaceholderValues() map[string]interface{} {
	return map[string]interface{}{
		"PROJECT_NAME":           "项目",
		"PROGRAMMING_LANGUAGE":   "待配置",
		"FRAMEWORK":              "待配置",
		"BUILD_TOOL":             "待配置",
		"CODE_LANGUAGE":          "text",
		"TARGET_PLATFORMS":       "待配置",
		"LOGGER_SERVICE_CLASS":   "LogService",
	}
}

