package commands

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cursor-cold-start/cursor-cold-start/pkg/utils"
)

// RuleFile 表示一个规则文件
type RuleFile struct {
	TemplatePath string // 模板文件路径
	OutputName   string // 输出文件名
}

// RuleCollector 规则收集器 - 单一职责：收集所有规则文件
type RuleCollector struct {
	templateDir string
}

// NewRuleCollector 创建规则收集器
func NewRuleCollector(templateDir string) *RuleCollector {
	return &RuleCollector{
		templateDir: templateDir,
	}
}

// Collect 收集所有规则文件
// 根据配置收集核心规则、语言规则、框架规则、平台规则
func (rc *RuleCollector) Collect(config map[string]interface{}) []RuleFile {
	var rules []RuleFile

	// 1. 收集核心规则
	rules = append(rules, rc.CollectCoreRules()...)

	// 2. 收集语言规则
	rules = append(rules, rc.collectLanguageRules(config)...)

	// 3. 收集框架规则
	rules = append(rules, rc.collectFrameworkRules(config)...)

	// 4. 收集平台规则
	rules = append(rules, rc.collectPlatformRules(config)...)

	return rules
}

// CollectCoreRules 仅收集核心规则（用于首次初始化）
func (rc *RuleCollector) CollectCoreRules() []RuleFile {
	return rc.collectCoreRules()
}

// collectCoreRules 收集核心规则
func (rc *RuleCollector) collectCoreRules() []RuleFile {
	var rules []RuleFile
	coreDir := filepath.Join(rc.templateDir, "templates", "core")
	if !utils.DirExists(coreDir) {
		return rules
	}

	entries, _ := os.ReadDir(coreDir)
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".template") {
			baseName := strings.TrimSuffix(entry.Name(), ".template")
			rules = append(rules, RuleFile{
				TemplatePath: filepath.Join(coreDir, entry.Name()),
				OutputName:   baseName,
			})
		}
	}

	return rules
}

// collectLanguageRules 收集语言规则
func (rc *RuleCollector) collectLanguageRules(config map[string]interface{}) []RuleFile {
	var rules []RuleFile
	lang := getStringValue(config, "language")
	if lang == "" {
		return rules
	}

	langDir := filepath.Join(rc.templateDir, "templates", "tech", "languages")
	langTemplate := filepath.Join(langDir, fmt.Sprintf("10-%s.mdc.template", lang))
	if utils.FileExists(langTemplate) {
		rules = append(rules, RuleFile{
			TemplatePath: langTemplate,
			OutputName:   fmt.Sprintf("10-%s.mdc", lang),
		})
	}

	return rules
}

// collectFrameworkRules 收集框架规则
func (rc *RuleCollector) collectFrameworkRules(config map[string]interface{}) []RuleFile {
	var rules []RuleFile
	framework := getStringValue(config, "framework")
	if framework == "" {
		return rules
	}

	fwDir := filepath.Join(rc.templateDir, "templates", "tech", "frameworks")
	fwTemplate := filepath.Join(fwDir, fmt.Sprintf("20-%s.mdc.template", framework))
	if utils.FileExists(fwTemplate) {
		rules = append(rules, RuleFile{
			TemplatePath: fwTemplate,
			OutputName:   fmt.Sprintf("20-%s.mdc", framework),
		})
	}

	return rules
}

// collectPlatformRules 收集平台规则
func (rc *RuleCollector) collectPlatformRules(config map[string]interface{}) []RuleFile {
	var rules []RuleFile
	platforms := getSliceValue(config, "platforms")
	if len(platforms) == 0 {
		return rules
	}

	platformPriority := 30
	platformDir := filepath.Join(rc.templateDir, "templates", "tech", "platforms")
	for _, platform := range platforms {
		platformTemplate := filepath.Join(platformDir, fmt.Sprintf("30-%s.mdc.template", platform))
		if utils.FileExists(platformTemplate) {
			rules = append(rules, RuleFile{
				TemplatePath: platformTemplate,
				OutputName:   fmt.Sprintf("%d-%s.mdc", platformPriority, platform),
			})
			platformPriority++
		}
	}

	return rules
}

