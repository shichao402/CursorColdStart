package commands

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cursor-cold-start/cursor-cold-start/internal/initializer"
	"github.com/cursor-cold-start/cursor-cold-start/internal/template"
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
	rulesDir := filepath.Join(targetDir, ".cursor", "rules")

	for _, dir := range []string{configDir, modulesDir, rulesDir} {
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
		},
		"technology.json": map[string]interface{}{
			"$schema":   "技术栈配置 - 运行 coldstart list 查看可用选项",
			"language":  "",
			"framework": "",
			"platforms": []string{},
		},
		"features.json": map[string]interface{}{
			"$schema": "功能特性配置",
			"logging": map[string]interface{}{
				"enabled":      true,
				"serviceClass": "LogService",
				"filePath":     "logs/app.log",
			},
			"githubAction": map[string]interface{}{
				"enabled": false,
			},
			"documentation": map[string]interface{}{
				"enabled": true,
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
│   └── features.json     # 功能特性配置
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

### technology.json
- language: 编程语言（必填）- dart/typescript/python/kotlin/swift
- framework: 框架 - flutter/react/vue/django/fastapi/android/ios
- platforms: 目标平台 - android/ios/web/macos/windows/linux

### features.json
- logging: 日志配置
- githubAction: GitHub Action 配置
- documentation: 文档配置

运行 ` + "`coldstart list`" + ` 查看所有可用选项。
`
	readmePath := filepath.Join(targetDir, ".cursor-cold-start", "README.md")
	if err := os.WriteFile(readmePath, []byte(readme), 0644); err != nil {
		return fmt.Errorf("无法写入 README: %w", err)
	}
	fmt.Println("  ✅ 已创建 .cursor-cold-start/README.md")
	fmt.Println()

	// 复制通用规则
	fmt.Println("📋 注入通用规则...")
	if err := e.copyCommonRules(targetDir); err != nil {
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
	fmt.Println("     .cursor-cold-start/config/features.json")
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

	// 检查 features.json
	featuresConfig, featuresOk, featuresMsg := e.checkFeaturesConfig(configDir)
	fmt.Printf("  %s features.json - %s\n", statusIcon(featuresOk), featuresMsg)

	fmt.Println()

	// 如果必填配置不完整，提示并退出
	if !projectOk || !techOk {
		fmt.Println("❌ 配置不完整，请补充必填字段后重试")
		fmt.Println()
		fmt.Println("提示：让 AI 帮助填写配置文件")
		return nil
	}

	// 合并配置
	config := e.mergeConfigs(projectConfig, techConfig, featuresConfig)

	// 生成规则
	fmt.Println("📋 生成规则文件...")
	if err := e.generateRules(targetDir, config); err != nil {
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

// checkFeaturesConfig 检查功能特性配置
func (e *Executor) checkFeaturesConfig(configDir string) (map[string]interface{}, bool, string) {
	filePath := filepath.Join(configDir, "features.json")
	config, err := readJSONFile(filePath)
	if err != nil {
		return nil, true, "使用默认配置"
	}

	return config, true, "完整"
}

// mergeConfigs 合并配置
func (e *Executor) mergeConfigs(project, tech, features map[string]interface{}) map[string]interface{} {
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

	// 功能特性
	if features != nil {
		if logging, ok := features["logging"].(map[string]interface{}); ok {
			config["enableLogging"] = getBoolValue(logging, "enabled")
			config["loggerServiceClass"] = getStringValue(logging, "serviceClass")
			config["logFilePath"] = getStringValue(logging, "filePath")
		}
		if githubAction, ok := features["githubAction"].(map[string]interface{}); ok {
			config["enableGitHubAction"] = getBoolValue(githubAction, "enabled")
		}
		if doc, ok := features["documentation"].(map[string]interface{}); ok {
			config["enableDocumentation"] = getBoolValue(doc, "enabled")
		}
	}

	return config
}

// copyCommonRules 复制通用规则
func (e *Executor) copyCommonRules(targetDir string) error {
	rulesDir := filepath.Join(targetDir, ".cursor", "rules")
	commonDir := filepath.Join(e.templateDir, "templates", "rules", "common")

	// 只复制 00-core.mdc（通用规则）
	coreTemplate := filepath.Join(commonDir, "00-core.mdc.template")
	if utils.FileExists(coreTemplate) {
		processor := template.NewProcessor()
		outputFile := filepath.Join(rulesDir, "00-core.mdc")

		// 使用最小化的占位符值
		values := map[string]interface{}{
			"PROJECT_NAME":         "项目",
			"PROGRAMMING_LANGUAGE": "待配置",
			"FRAMEWORK":            "待配置",
			"BUILD_TOOL":           "待配置",
			"CODE_LANGUAGE":        "text",
			"TARGET_PLATFORMS":     "待配置",
		}

		if err := processor.RenderTemplateToFile(coreTemplate, outputFile, values); err != nil {
			return fmt.Errorf("无法生成 00-core.mdc: %w", err)
		}
		fmt.Println("  ✅ .cursor/rules/00-core.mdc")
	}

	return nil
}

// generateRules 根据配置生成规则
func (e *Executor) generateRules(targetDir string, config map[string]interface{}) error {
	rulesDir := filepath.Join(targetDir, ".cursor", "rules")
	processor := template.NewProcessor()
	values := e.init.GetPlaceholderValues(config)

	// 1. 通用规则
	commonDir := filepath.Join(e.templateDir, "templates", "rules", "common")
	if utils.DirExists(commonDir) {
		entries, _ := os.ReadDir(commonDir)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".template") {
				templateFile := filepath.Join(commonDir, entry.Name())
				baseName := strings.TrimSuffix(entry.Name(), ".template")
				outputFile := filepath.Join(rulesDir, baseName)

				if err := processor.RenderTemplateToFile(templateFile, outputFile, values); err != nil {
					fmt.Printf("  ⚠️  %s (跳过: %v)\n", baseName, err)
					continue
				}
				fmt.Printf("  ✅ %s\n", baseName)
			}
		}
	}

	// 2. 语言规则
	lang := getStringValue(config, "language")
	if lang != "" {
		langDir := filepath.Join(e.templateDir, "templates", "rules", "languages")
		langTemplate := filepath.Join(langDir, fmt.Sprintf("10-%s.mdc.template", lang))
		if utils.FileExists(langTemplate) {
			outputFile := filepath.Join(rulesDir, fmt.Sprintf("10-%s.mdc", lang))
			if err := processor.RenderTemplateToFile(langTemplate, outputFile, values); err == nil {
				fmt.Printf("  ✅ 10-%s.mdc\n", lang)
			}
		}
	}

	// 3. 框架规则
	framework := getStringValue(config, "framework")
	if framework != "" {
		fwDir := filepath.Join(e.templateDir, "templates", "rules", "frameworks")
		fwTemplate := filepath.Join(fwDir, fmt.Sprintf("20-%s.mdc.template", framework))
		if utils.FileExists(fwTemplate) {
			outputFile := filepath.Join(rulesDir, fmt.Sprintf("20-%s.mdc", framework))
			if err := processor.RenderTemplateToFile(fwTemplate, outputFile, values); err == nil {
				fmt.Printf("  ✅ 20-%s.mdc\n", framework)
			}
		}
	}

	// 4. 平台规则
	platforms := getSliceValue(config, "platforms")
	platformPriority := 30
	for _, platform := range platforms {
		platformDir := filepath.Join(e.templateDir, "templates", "rules", "platforms")
		platformTemplate := filepath.Join(platformDir, fmt.Sprintf("30-%s.mdc.template", platform))
		if utils.FileExists(platformTemplate) {
			outputFile := filepath.Join(rulesDir, fmt.Sprintf("%d-%s.mdc", platformPriority, platform))
			if err := processor.RenderTemplateToFile(platformTemplate, outputFile, values); err == nil {
				fmt.Printf("  ✅ %d-%s.mdc\n", platformPriority, platform)
			}
			platformPriority++
		}
	}

	return nil
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
	case "modules", "mod":
		e.listModules()
	default:
		// 列出所有
		fmt.Println("可用选项：")
		fmt.Println()
		e.listLanguages(options)
		fmt.Println()
		e.listPlatforms(options)
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

func (e *Executor) listModules() {
	fmt.Println("📦 可用模块：")
	modulesDir := filepath.Join(e.templateDir, "templates", "modules")
	entries, err := os.ReadDir(modulesDir)
	if err != nil {
		fmt.Println("  (暂无可用模块)")
		return
	}

	for _, entry := range entries {
		if entry.IsDir() {
			configFile := filepath.Join(modulesDir, entry.Name(), "module.config.json")
			if utils.FileExists(configFile) {
				config, err := readJSONFile(configFile)
				if err == nil {
					name := getStringValue(config, "moduleName")
					desc := getStringValue(config, "moduleDescription")
					fmt.Printf("  - %s: %s\n", entry.Name(), name)
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
	}
	return []string{}
}
