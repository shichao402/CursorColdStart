package commands

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cursor-cold-start/cursor-cold-start/internal/initializer"
	"github.com/cursor-cold-start/cursor-cold-start/pkg/utils"
)

// Executor 命令执行器
type Executor struct {
	toolRoot    string
	templateDir string
	init        *initializer.ProjectInitializer
}

// NewExecutor 创建命令执行器
func NewExecutor(toolRoot string) *Executor {
	return &Executor{
		toolRoot:    toolRoot,
		templateDir: filepath.Join(toolRoot, "rules_template"),
	}
}

// Init 初始化项目
func (e *Executor) Init(targetDir string) error {
	absTarget, err := filepath.Abs(targetDir)
	if err != nil {
		return fmt.Errorf("无法解析目标目录: %w", err)
	}

	// 创建初始化器
	e.init, err = initializer.New(e.toolRoot)
	if err != nil {
		return err
	}

	fmt.Println("==================================================")
	fmt.Println("  CursorColdStart - 项目初始化")
	fmt.Println("==================================================")
	fmt.Println()
	fmt.Printf("目标目录: %s\n", absTarget)
	fmt.Println()

	// 检查配置目录是否存在
	configDir := filepath.Join(absTarget, ".cursor-cold-start", "config")
	isFirstInit := !utils.DirExists(configDir)

	if isFirstInit {
		return e.firstInit(absTarget)
	}
	return e.updateInit(absTarget)
}

// firstInit 首次初始化 - 生成空配置 + 通用规则
func (e *Executor) firstInit(targetDir string) error {
	fmt.Println("📦 首次初始化...")
	fmt.Println()

	// 创建目录结构
	configDir := filepath.Join(targetDir, ".cursor-cold-start", "config")
	modulesDir := filepath.Join(targetDir, ".cursor-cold-start", "modules")

	for _, dir := range []string{configDir, modulesDir} {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("无法创建目录 %s: %w", dir, err)
		}
	}

	// 生成空配置文件
	configs := map[string]interface{}{
		"project.json": map[string]interface{}{
			"$schema":     "项目基本信息配置",
			"name":        "",
			"description": "",
			"version":     "1.0.0",
			"ides":        []string{"cursor"},
		},
		"technology.json": map[string]interface{}{
			"$schema":   "技术栈配置 - 运行 coldstart list 查看可用选项",
			"language":  "",
			"framework": "",
			"platforms": []string{},
		},
		"packs.json": map[string]interface{}{
			"$schema": "功能包配置 - 运行 coldstart list packs 查看可用功能包",
			"logging": map[string]interface{}{
				"enabled": true,
				"config": map[string]interface{}{
					"serviceClass": "LogService",
					"filePath":     "logs/app.log",
				},
			},
			"version-management": map[string]interface{}{
				"enabled": false,
				"config": map[string]interface{}{
					"sourceFile": "VERSION.yaml",
				},
			},
			"github-actions": map[string]interface{}{
				"enabled": false,
			},
			"documentation": map[string]interface{}{
				"enabled": true,
			},
			"cursortoolset": map[string]interface{}{
				"enabled": false,
				"config": map[string]interface{}{
					"packageName": "",
				},
			},
			"update-module": map[string]interface{}{
				"enabled": false,
				"config": map[string]interface{}{
					"moduleName": "",
					"modulePath": "",
				},
			},
		},
	}

	for filename, content := range configs {
		filePath := filepath.Join(configDir, filename)
		data, _ := json.MarshalIndent(content, "", "  ")
		if err := os.WriteFile(filePath, data, 0644); err != nil {
			return fmt.Errorf("无法写入 %s: %w", filename, err)
		}
		fmt.Printf("  ✅ 已创建 .cursor-cold-start/config/%s\n", filename)
	}

	// 生成 README
	readme := `# CursorColdStart 配置目录

此目录由 CursorColdStart 工具管理。

## 目录结构

` + "```" + `
.cursor-cold-start/
├── config/
│   ├── project.json      # 项目基本信息
│   ├── technology.json   # 技术栈配置
│   └── packs.json        # 功能包配置
└── modules/              # 已注入的模块配置
` + "```" + `

## 使用方法

1. **填写配置文件** - 让 AI 帮助填写 config/ 下的配置文件
2. **再次运行初始化** - ` + "`coldstart init .`" + ` 生成定制规则

## 配置说明

### project.json
- name: 项目名称（必填）
- description: 项目描述
- version: 项目版本
- ides: 目标 AI IDE 列表（可选，默认 ["cursor"]）
  - 支持: cursor, codebuddy, windsurf, trae

### technology.json
- language: 编程语言（必填）- dart/typescript/python/kotlin/swift
- framework: 框架 - flutter/react/vue/django/fastapi/android/ios
- platforms: 目标平台 - android/ios/web/macos/windows/linux

### packs.json
功能包配置，每个功能包可以独立启用/禁用：
- logging: 日志系统
- version-management: 版本管理
- github-actions: GitHub Actions CI/CD
- documentation: 文档管理
- cursortoolset: CursorToolset 包管理
- update-module: 应用更新模块

注意：安全规范、调试规范、脚本规范已内置在核心规则中，无需单独配置。

运行 ` + "`coldstart list packs`" + ` 查看所有可用功能包。
`
	readmePath := filepath.Join(targetDir, ".cursor-cold-start", "README.md")
	if err := os.WriteFile(readmePath, []byte(readme), 0644); err != nil {
		return fmt.Errorf("无法写入 README: %w", err)
	}
	fmt.Println("  ✅ 已创建 .cursor-cold-start/README.md")
	fmt.Println()

	// 复制通用规则（默认只注入 cursor）
	fmt.Println("📋 注入通用规则...")
	defaultIDEs := []string{"cursor"}
	
	// 使用 RuleGeneratorFacade 统一处理（仅核心规则模式）
	generator := NewRuleGeneratorFacade(e.templateDir, e.init)
	minimalConfig := make(map[string]interface{}) // 空配置，仅生成核心规则
	if err := generator.GenerateWithMode(targetDir, minimalConfig, defaultIDEs, true); err != nil {
		return err
	}

	fmt.Println()
	fmt.Println("==================================================")
	fmt.Println("  ✅ 首次初始化完成！")
	fmt.Println("==================================================")
	fmt.Println()
	fmt.Println("📝 下一步操作：")
	fmt.Println()
	fmt.Println("  1. 让 AI 帮助填写配置文件：")
	fmt.Println("     .cursor-cold-start/config/project.json")
	fmt.Println("     .cursor-cold-start/config/technology.json")
	fmt.Println("     .cursor-cold-start/config/packs.json")
	fmt.Println()
	fmt.Println("  2. 配置完成后，再次运行：")
	fmt.Printf("     coldstart init %s\n", targetDir)
	fmt.Println()

	return nil
}

// updateInit 更新初始化 - 检查配置 + 生成定制规则
func (e *Executor) updateInit(targetDir string) error {
	fmt.Println("🔄 检查配置并更新规则...")
	fmt.Println()

	// 读取并检查配置
	configDir := filepath.Join(targetDir, ".cursor-cold-start", "config")

	// 检查 project.json
	fmt.Println("📋 配置检查：")
	projectConfig, projectOk, projectMsg := e.checkProjectConfig(configDir)
	fmt.Printf("  %s project.json - %s\n", statusIcon(projectOk), projectMsg)

	// 检查 technology.json
	techConfig, techOk, techMsg := e.checkTechnologyConfig(configDir)
	fmt.Printf("  %s technology.json - %s\n", statusIcon(techOk), techMsg)

	// 检查 packs.json
	packsConfig, packsOk, packsMsg := e.checkPacksConfig(configDir)
	fmt.Printf("  %s packs.json - %s\n", statusIcon(packsOk), packsMsg)

	fmt.Println()

	// 如果必填配置不完整，提示并退出
	if !projectOk || !techOk {
		fmt.Println("❌ 配置不完整，请补充必填字段后重试")
		fmt.Println()
		fmt.Println("提示：让 AI 帮助填写配置文件")
		return nil
	}

	// 合并配置
	config := e.mergeConfigs(projectConfig, techConfig, packsConfig)

	// 获取 IDE 列表
	ides := getSliceValue(projectConfig, "ides")
	if len(ides) == 0 {
		ides = []string{"cursor"} // 默认只生成 cursor
	}

	// 生成规则
	fmt.Println("📋 生成规则文件...")
	fmt.Printf("  目标 IDE: %v\n", ides)
	if err := e.generateRules(targetDir, config, ides); err != nil {
		return err
	}

	fmt.Println()
	fmt.Println("==================================================")
	fmt.Println("  ✅ 规则生成完成！")
	fmt.Println("==================================================")
	fmt.Println()

	return nil
}

// checkProjectConfig 检查项目配置
func (e *Executor) checkProjectConfig(configDir string) (map[string]interface{}, bool, string) {
	filePath := filepath.Join(configDir, "project.json")
	config, err := readJSONFile(filePath)
	if err != nil {
		return nil, false, "文件不存在"
	}

	name := getStringValue(config, "name")
	if name == "" {
		return config, false, "缺少必填字段: name"
	}

	return config, true, fmt.Sprintf("完整 (%s)", name)
}

// checkTechnologyConfig 检查技术栈配置
func (e *Executor) checkTechnologyConfig(configDir string) (map[string]interface{}, bool, string) {
	filePath := filepath.Join(configDir, "technology.json")
	config, err := readJSONFile(filePath)
	if err != nil {
		return nil, false, "文件不存在"
	}

	language := getStringValue(config, "language")
	if language == "" {
		return config, false, "缺少必填字段: language"
	}

	framework := getStringValue(config, "framework")
	if framework != "" {
		return config, true, fmt.Sprintf("完整 (%s + %s)", language, framework)
	}

	return config, true, fmt.Sprintf("完整 (%s)", language)
}

// checkPacksConfig 检查功能包配置
func (e *Executor) checkPacksConfig(configDir string) (map[string]interface{}, bool, string) {
	filePath := filepath.Join(configDir, "packs.json")
	config, err := readJSONFile(filePath)
	if err != nil {
		return nil, true, "使用默认配置"
	}

	return config, true, "完整"
}

// mergeConfigs 合并配置
func (e *Executor) mergeConfigs(project, tech, packs map[string]interface{}) map[string]interface{} {
	config := make(map[string]interface{})

	// 项目信息
	if project != nil {
		config["projectName"] = getStringValue(project, "name")
		config["projectDescription"] = getStringValue(project, "description")
		config["projectVersion"] = getStringValue(project, "version")
	}

	// 技术栈
	if tech != nil {
		config["language"] = getStringValue(tech, "language")
		config["framework"] = getStringValue(tech, "framework")
		config["platforms"] = getSliceValue(tech, "platforms")

		// 根据语言设置额外信息
		lang := getStringValue(tech, "language")
		config["languageName"] = e.getLanguageName(lang)
		config["codeLanguage"] = e.getCodeLanguage(lang)
	}

	// 功能包配置
	config["packs"] = packs

	return config
}

// copyCommonRules 已废弃，使用 RuleGeneratorFacade.GenerateWithMode 替代
// 保留此函数仅用于向后兼容（如果其他地方有调用）
func (e *Executor) copyCommonRules(targetDir string, ides []string) error {
	generator := NewRuleGeneratorFacade(e.templateDir, e.init)
	minimalConfig := make(map[string]interface{})
	return generator.GenerateWithMode(targetDir, minimalConfig, ides, true)
}

// getIDERulesDir 获取 IDE 规则目录路径
func getIDERulesDir(ide string) string {
	switch ide {
	case "cursor":
		return ".cursor/rules"
	case "codebuddy":
		return ".codebuddy/rules"
	case "windsurf":
		return ".windsurf/rules"
	case "trae":
		return ".trae/rules"
	default:
		return fmt.Sprintf(".%s/rules", ide)
	}
}

// getIDEDirName 获取 IDE 目录名称（用于显示）
func getIDEDirName(ide string) string {
	switch ide {
	case "cursor":
		return ".cursor"
	case "codebuddy":
		return ".codebuddy"
	case "windsurf":
		return ".windsurf"
	case "trae":
		return ".trae"
	default:
		return fmt.Sprintf(".%s", ide)
	}
}

// generateRules 根据配置生成规则
// 使用门面模式：通过 RuleGeneratorFacade 统一管理规则生成流程
func (e *Executor) generateRules(targetDir string, config map[string]interface{}, ides []string) error {
	// 创建规则生成门面
	generator := NewRuleGeneratorFacade(e.templateDir, e.init)

	// 通过门面生成规则
	return generator.Generate(targetDir, config, ides)
}


// List 列出可用选项
func (e *Executor) List(listType string) error {
	optionsFile := filepath.Join(e.templateDir, "options.json")
	data, err := os.ReadFile(optionsFile)
	if err != nil {
		return fmt.Errorf("无法读取选项配置: %w", err)
	}

	var options map[string]interface{}
	if err := json.Unmarshal(data, &options); err != nil {
		return fmt.Errorf("无法解析选项配置: %w", err)
	}

	switch listType {
	case "languages", "lang":
		e.listLanguages(options)
	case "frameworks", "fw":
		e.listFrameworks(options)
	case "platforms", "plat":
		e.listPlatforms(options)
	case "packs", "pack":
		e.listPacks()
	case "ides", "ide":
		e.listIDEs()
	default:
		// 列出所有
		fmt.Println("可用选项：")
		fmt.Println()
		e.listLanguages(options)
		fmt.Println()
		e.listPlatforms(options)
		fmt.Println()
		e.listIDEs()
		fmt.Println()
		e.listPacks()
		fmt.Println()
		fmt.Println("提示：运行 'coldstart list languages' 查看语言对应的框架")
	}

	return nil
}

func (e *Executor) listLanguages(options map[string]interface{}) {
	fmt.Println("📝 支持的语言：")
	languages, _ := options["languages"].([]interface{})
	for _, lang := range languages {
		langMap, _ := lang.(map[string]interface{})
		id := getStringValue(langMap, "id")
		name := getStringValue(langMap, "name")
		fmt.Printf("  - %s (%s)\n", id, name)

		// 显示框架
		frameworks, _ := langMap["frameworks"].([]interface{})
		if len(frameworks) > 0 {
			fmt.Print("    框架: ")
			fwNames := []string{}
			for _, fw := range frameworks {
				fwMap, _ := fw.(map[string]interface{})
				fwNames = append(fwNames, getStringValue(fwMap, "id"))
			}
			fmt.Println(strings.Join(fwNames, ", "))
		}
	}
}

func (e *Executor) listFrameworks(options map[string]interface{}) {
	fmt.Println("📦 支持的框架：")
	languages, _ := options["languages"].([]interface{})
	for _, lang := range languages {
		langMap, _ := lang.(map[string]interface{})
		langName := getStringValue(langMap, "name")
		frameworks, _ := langMap["frameworks"].([]interface{})
		if len(frameworks) > 0 {
			fmt.Printf("  %s:\n", langName)
			for _, fw := range frameworks {
				fwMap, _ := fw.(map[string]interface{})
				id := getStringValue(fwMap, "id")
				name := getStringValue(fwMap, "name")
				fmt.Printf("    - %s (%s)\n", id, name)
			}
		}
	}
}

func (e *Executor) listPlatforms(options map[string]interface{}) {
	fmt.Println("🖥️  支持的平台：")
	platforms, _ := options["platforms"].([]interface{})
	for _, plat := range platforms {
		platMap, _ := plat.(map[string]interface{})
		id := getStringValue(platMap, "id")
		name := getStringValue(platMap, "name")
		fmt.Printf("  - %s (%s)\n", id, name)
	}
}

func (e *Executor) listIDEs() {
	fmt.Println("🤖 支持的 AI IDE：")
	ides := []struct {
		id   string
		name string
		dir  string
	}{
		{"cursor", "Cursor", ".cursor/rules"},
		{"codebuddy", "CodeBuddy", ".codebuddy/rules"},
		{"windsurf", "Windsurf", ".windsurf/rules"},
		{"trae", "Trae", ".trae/rules"},
	}
	for _, ide := range ides {
		fmt.Printf("  - %s (%s) -> %s\n", ide.id, ide.name, ide.dir)
	}
}

func (e *Executor) listPacks() {
	fmt.Println("📦 可用功能包：")
	packsDir := filepath.Join(e.templateDir, "templates", "packs")
	entries, err := os.ReadDir(packsDir)
	if err != nil {
		fmt.Println("  (暂无可用功能包)")
		return
	}

	for _, entry := range entries {
		if entry.IsDir() {
			configFile := filepath.Join(packsDir, entry.Name(), "pack.config.json")
			if utils.FileExists(configFile) {
				config, err := readJSONFile(configFile)
				if err == nil {
					name := getStringValue(config, "name")
					desc := getStringValue(config, "description")
					category := getStringValue(config, "category")
					fmt.Printf("  - %s: %s [%s]\n", entry.Name(), name, category)
					if desc != "" {
						fmt.Printf("    %s\n", desc)
					}
				}
			}
		}
	}
}

// 辅助函数
func (e *Executor) getLanguageName(lang string) string {
	names := map[string]string{
		"dart":       "Dart",
		"typescript": "TypeScript",
		"javascript": "JavaScript",
		"python":     "Python",
		"kotlin":     "Kotlin",
		"java":       "Java",
		"swift":      "Swift",
		"go":         "Go",
	}
	if name, ok := names[lang]; ok {
		return name
	}
	return lang
}

func (e *Executor) getCodeLanguage(lang string) string {
	codes := map[string]string{
		"dart":       "dart",
		"typescript": "typescript",
		"javascript": "javascript",
		"python":     "python",
		"kotlin":     "kotlin",
		"java":       "java",
		"swift":      "swift",
		"go":         "go",
	}
	if code, ok := codes[lang]; ok {
		return code
	}
	return lang
}

func statusIcon(ok bool) string {
	if ok {
		return "✅"
	}
	return "⚠️ "
}

// toUpperSnakeCase 将 camelCase 转换为 UPPER_SNAKE_CASE
func toUpperSnakeCase(s string) string {
	var result strings.Builder
	for i, r := range s {
		if i > 0 && r >= 'A' && r <= 'Z' {
			result.WriteRune('_')
		}
		result.WriteRune(r)
	}
	return strings.ToUpper(result.String())
}

func readJSONFile(filePath string) (map[string]interface{}, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}
	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		return nil, err
	}
	return result, nil
}

func getStringValue(m map[string]interface{}, key string) string {
	if m == nil {
		return ""
	}
	if v, ok := m[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

func getBoolValue(m map[string]interface{}, key string) bool {
	if m == nil {
		return false
	}
	if v, ok := m[key]; ok {
		if b, ok := v.(bool); ok {
			return b
		}
	}
	return false
}

func getSliceValue(m map[string]interface{}, key string) []string {
	if m == nil {
		return []string{}
	}
	if v, ok := m[key]; ok {
		return getStringSliceFromInterface(v)
	}
	return []string{}
}

func getStringSliceFromInterface(v interface{}) []string {
	if v == nil {
		return []string{}
	}
	if arr, ok := v.([]interface{}); ok {
		result := make([]string, 0, len(arr))
		for _, item := range arr {
			if s, ok := item.(string); ok {
				result = append(result, s)
			}
		}
		return result
	}
	if arr, ok := v.([]string); ok {
		return arr
	}
	return []string{}
}

func getFloatValue(m map[string]interface{}, key string) float64 {
	if m == nil {
		return 0
	}
	if v, ok := m[key]; ok {
		if f, ok := v.(float64); ok {
			return f
		}
		if i, ok := v.(int); ok {
			return float64(i)
		}
	}
	return 0
}
