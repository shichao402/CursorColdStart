package commands

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/cursor-cold-start/cursor-cold-start/internal/template"
)

// RuleInjector 规则注入器 - 单一职责：将规则注入到单个 IDE
type RuleInjector struct {
	templateDir string
	processor   *template.Processor
	values      map[string]interface{}
	config      map[string]interface{}
}

// NewRuleInjector 创建规则注入器
func NewRuleInjector(templateDir string, processor *template.Processor, values map[string]interface{}, config map[string]interface{}) *RuleInjector {
	return &RuleInjector{
		templateDir: templateDir,
		processor:   processor,
		values:      values,
		config:      config,
	}
}

// Inject 将规则注入到指定 IDE
// 返回生成的文件名列表（用于后续清理）
func (ri *RuleInjector) Inject(targetDir string, ide string, rules []RuleFile) (map[string]bool, error) {
	expectedFiles := make(map[string]bool)
	rulesDir := filepath.Join(targetDir, getIDERulesDir(ide))

	// 创建规则目录
	if err := os.MkdirAll(rulesDir, 0755); err != nil {
		return nil, fmt.Errorf("无法创建目录 %s: %w", rulesDir, err)
	}

	// 1. 注入基础规则（核心、语言、框架、平台）
	for _, rule := range rules {
		expectedFiles[rule.OutputName] = true
		outputFile := filepath.Join(rulesDir, rule.OutputName)
		if err := ri.processor.RenderTemplateToFile(rule.TemplatePath, outputFile, ri.values); err != nil {
			fmt.Printf("  ⚠️  %s (跳过: %v)\n", rule.OutputName, err)
			continue
		}
		fmt.Printf("  ✅ %s\n", rule.OutputName)
	}

	// 2. 注入功能包规则
	packs, _ := ri.config["packs"].(map[string]interface{})
	// 统一通过 injectPackRules 处理（即使 packs 为 nil，也需要获取文件映射用于清理）
	packFiles, packFileMap := ri.injectPackRules(rulesDir, packs)
	for _, f := range packFiles {
		expectedFiles[f] = true
	}

	// 3. 清理不再需要的规则文件（包括禁用的 pack 文件）
	ri.cleanupObsoleteRules(rulesDir, expectedFiles, packs, packFileMap)

	// 4. 保存生成文件清单
	ri.saveGeneratedFilesList(rulesDir, expectedFiles)

	return expectedFiles, nil
}

// injectPackRules 注入功能包规则
// 即使 packs 为 nil，也会返回文件映射（用于清理）
func (ri *RuleInjector) injectPackRules(rulesDir string, packs map[string]interface{}) ([]string, map[string]string) {
	// 统一调用 generatePackRules（即使 packs 为 nil，也能获取文件映射）
	return generatePackRules(rulesDir, packs, ri.values, ri.processor, ri.templateDir)
}

// cleanupObsoleteRules 清理不再需要的规则文件
// 包括：之前生成但现在不需要的文件、禁用的 pack 文件、从配置中移除的 pack 文件
func (ri *RuleInjector) cleanupObsoleteRules(rulesDir string, expectedFiles map[string]bool, packs map[string]interface{}, packFileMap map[string]string) {
	previousFiles := loadGeneratedFilesList(rulesDir)
	
	// 检查禁用的 pack 文件
	for packID, fileName := range packFileMap {
		// 如果 pack 不在配置中，或者被禁用，且文件存在，则应该删除
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
				filePath := filepath.Join(rulesDir, fileName)
				if err := os.Remove(filePath); err != nil {
					if !os.IsNotExist(err) {
						fmt.Printf("  ⚠️  无法删除 %s: %v\n", fileName, err)
					}
				} else {
					fmt.Printf("  🗑️  已删除 %s (pack %s 已禁用或移除)\n", fileName, packID)
					// 从 expectedFiles 中移除，避免后续重复处理
					delete(expectedFiles, fileName)
				}
			}
		}
	}
	
	// 清理其他不再需要的文件（基于文件清单）
	if len(previousFiles) == 0 {
		return // 没有清单，跳过清理（首次运行或清单丢失）
	}

	for fileName := range previousFiles {
		// 如果之前生成的文件不在本次预期列表中，删除它
		if !expectedFiles[fileName] {
			filePath := filepath.Join(rulesDir, fileName)
			if err := os.Remove(filePath); err != nil {
				if !os.IsNotExist(err) {
					fmt.Printf("  ⚠️  无法删除 %s: %v\n", fileName, err)
				}
			} else {
				fmt.Printf("  🗑️  已删除 %s (不再需要)\n", fileName)
			}
		}
	}
}

// saveGeneratedFilesList 保存生成文件清单
func (ri *RuleInjector) saveGeneratedFilesList(rulesDir string, files map[string]bool) {
	saveGeneratedFilesListToFile(rulesDir, files)
}

