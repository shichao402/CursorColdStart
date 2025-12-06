package initializer

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/cursor-cold-start/cursor-cold-start/internal/template"
	"github.com/cursor-cold-start/cursor-cold-start/pkg/utils"
)

// StageInit 阶段1：初始化
func (p *ProjectInitializer) StageInit(targetDir string) error {
	fmt.Println("========================================")
	fmt.Println("  阶段1：初始化")
	fmt.Println("========================================")
	fmt.Println()

	// 1.1 创建临时目录
	fmt.Println("[1.1] 创建临时工作目录...")
	if utils.DirExists(p.StagingDir) {
		if err := utils.RemoveDir(p.StagingDir); err != nil {
			return fmt.Errorf("无法删除临时目录: %w", err)
		}
	}
	if err := os.MkdirAll(p.StagingDir, 0755); err != nil {
		return fmt.Errorf("无法创建临时目录: %w", err)
	}
	fmt.Printf("✅ 临时目录: %s\n", p.StagingDir)
	fmt.Println()

	// 1.2 拷贝配置文件模板
	fmt.Println("[1.2] 拷贝配置文件模板...")
	templateConfig := filepath.Join(p.ProjectInitDir, "config.template.json")
	if err := utils.CopyFile(templateConfig, p.ConfigFile); err != nil {
		return fmt.Errorf("无法拷贝配置文件模板: %w", err)
	}
	fmt.Printf("✅ 配置文件: %s\n", p.ConfigFile)
	fmt.Println()

	// 1.3 交互式收集信息
	fmt.Println("[1.3] 交互式收集项目信息...")
	fmt.Println()

	config, err := p.LoadConfig()
	if err != nil {
		return err
	}

	options, err := p.LoadOptions()
	if err != nil {
		return err
	}

	// 收集项目名称
	projectName := utils.ReadInputWithDefault("项目名称: ", "未命名项目")
	config["projectName"] = projectName

	// 拷贝项目描述模板
	fmt.Println()
	fmt.Println("[1.3.1] 拷贝项目描述模板文档...")
	descTemplate := filepath.Join(p.ProjectInitDir, "templates", "plans", "common", "01-project-description.md")
	descOutput := filepath.Join(p.StagingDir, "plans", "01-project-description.md")
	if utils.FileExists(descTemplate) {
		if err := utils.CopyFile(descTemplate, descOutput); err != nil {
			return fmt.Errorf("无法拷贝项目描述模板: %w", err)
		}
		fmt.Println("✅ 项目描述模板已生成: plans/01-project-description.md")
		fmt.Println("提示：请在阶段2之前编辑此文件，补充项目描述信息")
	}
	fmt.Println()

	// 收集编程语言
	fmt.Println("编程语言：")
	languages, _ := getSlice(options, "languages")
	for i, lang := range languages {
		langMap, _ := lang.(map[string]interface{})
		name := getString(langMap, "name", getString(langMap, "id", ""))
		fmt.Printf("  %d) %s\n", i+1, name)
	}

	langChoice := utils.ReadInputWithDefault(fmt.Sprintf("请选择 (1-%d，默认1): ", len(languages)), "1")
	langIdx := 0
	if idx, err := strconv.Atoi(langChoice); err == nil && idx > 0 && idx <= len(languages) {
		langIdx = idx - 1
	}

	selectedLang, _ := languages[langIdx].(map[string]interface{})
	config["language"] = getString(selectedLang, "id", "dart")
	config["languageName"] = getString(selectedLang, "name", "Dart")
	config["codeLanguage"] = getString(selectedLang, "codeLanguage", getString(selectedLang, "id", "dart"))

	// 收集框架
	fmt.Println()
	fmt.Println("框架/平台：")
	frameworks, _ := getSlice(selectedLang, "frameworks")
	if len(frameworks) == 1 {
		selectedFw, _ := frameworks[0].(map[string]interface{})
		fmt.Printf("  自动选择: %s\n", getString(selectedFw, "name", ""))
		config["framework"] = getString(selectedFw, "id", "")
		config["buildTool"] = getString(selectedFw, "buildTool", "CLI")
	} else {
		for i, fw := range frameworks {
			fwMap, _ := fw.(map[string]interface{})
			fmt.Printf("  %d) %s\n", i+1, getString(fwMap, "name", ""))
		}
		fwChoice := utils.ReadInputWithDefault(fmt.Sprintf("请选择 (1-%d，默认1): ", len(frameworks)), "1")
		fwIdx := 0
		if idx, err := strconv.Atoi(fwChoice); err == nil && idx > 0 && idx <= len(frameworks) {
			fwIdx = idx - 1
		}
		selectedFw, _ := frameworks[fwIdx].(map[string]interface{})
		config["framework"] = getString(selectedFw, "id", "")
		config["buildTool"] = getString(selectedFw, "buildTool", "CLI")
	}

	// 收集平台
	fmt.Println()
	fmt.Println("目标平台（可多选，用空格分隔，如：1 3 4）：")
	platformsList, _ := getSlice(options, "platforms")
	for i, platform := range platformsList {
		platformMap, _ := platform.(map[string]interface{})
		fmt.Printf("  %d) %s\n", i+1, getString(platformMap, "name", ""))
	}

	platformChoices := strings.Fields(utils.ReadInput("请选择: "))
	selectedPlatforms := []interface{}{}
	for _, choice := range platformChoices {
		if idx, err := strconv.Atoi(choice); err == nil && idx > 0 && idx <= len(platformsList) {
			platform, _ := platformsList[idx-1].(map[string]interface{})
			selectedPlatforms = append(selectedPlatforms, getString(platform, "id", ""))
		}
	}

	if len(selectedPlatforms) == 0 {
		// 使用默认平台
		for _, platform := range platformsList {
			platformMap, _ := platform.(map[string]interface{})
			if getBool(platformMap, "default", false) {
				selectedPlatforms = append(selectedPlatforms, getString(platformMap, "id", "web"))
				break
			}
		}
		if len(selectedPlatforms) == 0 {
			selectedPlatforms = append(selectedPlatforms, "web")
		}
	}

	config["platforms"] = selectedPlatforms

	// 收集是否启用 GitHub Action
	fmt.Println()
	githubActionInput := strings.ToLower(utils.ReadInputWithDefault("是否启用 GitHub Action？(y/n，默认n): ", "n"))
	config["enableGitHubAction"] = githubActionInput == "y" || githubActionInput == "yes"

	if err := p.SaveConfig(config); err != nil {
		return err
	}

	fmt.Println()
	fmt.Println("✅ 项目信息收集完成")
	fmt.Println()

	fmt.Println("========================================")
	fmt.Println("  ✅ 阶段1完成！")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Println("下一步操作：")
	fmt.Println()
	fmt.Printf("1. 📝 审查和修改以下文件：\n")
	fmt.Printf("   - 配置文件: %s\n", p.ConfigFile)
	fmt.Printf("   - 项目描述: %s\n", filepath.Join(p.StagingDir, "plans", "01-project-description.md"))
	fmt.Println()
	fmt.Println("2. ✏️  请编辑项目描述文档，补充详细的项目信息")
	fmt.Println()
	fmt.Println("3. ✅ 确认无误后，执行阶段2：")
	fmt.Println("   coldstart process")
	fmt.Println()

	return nil
}

// StageProcess 阶段2：处理
func (p *ProjectInitializer) StageProcess() error {
	if !utils.FileExists(p.ConfigFile) {
		return fmt.Errorf("配置文件不存在，请先运行阶段1：coldstart init")
	}

	fmt.Println("========================================")
	fmt.Println("  阶段2：处理")
	fmt.Println("========================================")
	fmt.Println()

	// 2.1 读取配置
	fmt.Println("[2.1] 读取配置文件...")
	config, err := p.LoadConfig()
	if err != nil {
		return err
	}
	values := p.GetPlaceholderValues(config)

	fmt.Println("✅ 配置文件读取完成")
	fmt.Printf("  项目名称: %v\n", values["PROJECT_NAME"])
	fmt.Printf("  语言: %v\n", values["PROGRAMMING_LANGUAGE"])
	fmt.Printf("  框架: %v\n", values["FRAMEWORK"])
	fmt.Printf("  平台: %v\n", values["TARGET_PLATFORMS"])
	fmt.Println()

	// 2.2 处理模板文件
	fmt.Println("[2.2] 处理模板文件...")

	// 确保项目描述文档存在
	descTemplate := filepath.Join(p.ProjectInitDir, "templates", "plans", "common", "01-project-description.md")
	descOutput := filepath.Join(p.StagingDir, "plans", "01-project-description.md")
	if !utils.FileExists(descOutput) && utils.FileExists(descTemplate) {
		if err := utils.CopyFile(descTemplate, descOutput); err != nil {
			return fmt.Errorf("无法拷贝项目描述模板: %w", err)
		}
		fmt.Println("    ✅ 项目描述文档已生成")
	}

	// 处理规则文件
	fmt.Println("  生成规则文件...")
	processor := template.NewProcessor()
	rulesDir := filepath.Join(p.StagingDir, "rules")
	if err := os.MkdirAll(rulesDir, 0755); err != nil {
		return fmt.Errorf("无法创建规则目录: %w", err)
	}

	ruleCounter := 0

	// 通用规则
	fmt.Println("    处理通用规则...")
	commonDir := filepath.Join(p.ProjectInitDir, "templates", "rules", "common")
	if utils.DirExists(commonDir) {
		entries, _ := os.ReadDir(commonDir)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".template") {
				templateFile := filepath.Join(commonDir, entry.Name())
				baseName := strings.TrimSuffix(entry.Name(), ".template")
				outputFile := filepath.Join(rulesDir, baseName)
				if err := processor.RenderTemplateToFile(templateFile, outputFile, values); err != nil {
					return fmt.Errorf("处理模板 %s 时出错: %w", templateFile, err)
				}
				ruleCounter++
				fmt.Printf("      ✅ %s\n", baseName)
			}
		}
	}

	// 语言特定规则
	lang := getString(config, "language", "dart")
	langRulesDir := filepath.Join(p.ProjectInitDir, "templates", "rules", "languages")
	langTemplate := ""
	for _, pattern := range []string{fmt.Sprintf("10-%s.mdc.template", lang), fmt.Sprintf("%s.mdc.template", lang)} {
		candidate := filepath.Join(langRulesDir, pattern)
		if utils.FileExists(candidate) {
			langTemplate = candidate
			break
		}
	}

	if langTemplate != "" {
		fmt.Printf("    处理语言特定规则: %s...\n", getString(config, "languageName", lang))
		options, _ := p.LoadOptions()
		rulePriorities, _ := options["rulePriorities"].(map[string]interface{})
		langPriority := int(getFloat64(rulePriorities, "languages", 10))
		outputFile := filepath.Join(rulesDir, fmt.Sprintf("%d-%s.mdc", langPriority, lang))
		if err := processor.RenderTemplateToFile(langTemplate, outputFile, values); err != nil {
			return fmt.Errorf("处理语言规则模板时出错: %w", err)
		}
		ruleCounter++
		fmt.Printf("      ✅ %d-%s.mdc\n", langPriority, lang)
	}

	// 框架特定规则
	framework := getString(config, "framework", "flutter")
	fwRulesDir := filepath.Join(p.ProjectInitDir, "templates", "rules", "frameworks")
	fwTemplate := ""
	for _, pattern := range []string{fmt.Sprintf("20-%s.mdc.template", framework), fmt.Sprintf("%s.mdc.template", framework)} {
		candidate := filepath.Join(fwRulesDir, pattern)
		if utils.FileExists(candidate) {
			fwTemplate = candidate
			break
		}
	}

	if fwTemplate != "" {
		fmt.Printf("    处理框架特定规则: %s...\n", framework)
		options, _ := p.LoadOptions()
		rulePriorities, _ := options["rulePriorities"].(map[string]interface{})
		fwPriority := int(getFloat64(rulePriorities, "frameworks", 20))
		outputFile := filepath.Join(rulesDir, fmt.Sprintf("%d-%s.mdc", fwPriority, framework))
		if err := processor.RenderTemplateToFile(fwTemplate, outputFile, values); err != nil {
			return fmt.Errorf("处理框架规则模板时出错: %w", err)
		}
		ruleCounter++
		fmt.Printf("      ✅ %d-%s.mdc\n", fwPriority, framework)
	}

	// 平台特定规则
	fmt.Println("    处理平台特定规则...")
	platforms := getStringSlice(config, "platforms")
	options, _ := p.LoadOptions()
	rulePriorities, _ := options["rulePriorities"].(map[string]interface{})
	platformPriority := int(getFloat64(rulePriorities, "platforms", 30))
	platformCounter := platformPriority

	for _, platform := range platforms {
		platformRulesDir := filepath.Join(p.ProjectInitDir, "templates", "rules", "platforms")
		platformTemplate := ""
		for _, pattern := range []string{fmt.Sprintf("30-%s.mdc.template", platform), fmt.Sprintf("%s.mdc.template", platform)} {
			candidate := filepath.Join(platformRulesDir, pattern)
			if utils.FileExists(candidate) {
				platformTemplate = candidate
				break
			}
		}

		if platformTemplate != "" {
			outputFile := filepath.Join(rulesDir, fmt.Sprintf("%d-%s.mdc", platformCounter, platform))
			if err := processor.RenderTemplateToFile(platformTemplate, outputFile, values); err != nil {
				return fmt.Errorf("处理平台规则模板时出错: %w", err)
			}
			ruleCounter++
			fmt.Printf("      ✅ %d-%s.mdc\n", platformCounter, platform)
			platformCounter++
		}
	}

	fmt.Println("✅ 模板处理完成")
	fmt.Println()

	// 2.3 显示生成的文件
	fmt.Println("[2.3] 生成的文件预览...")
	fmt.Println()
	fmt.Printf("规则文件（共 %d 个）：\n", ruleCounter)
	if utils.DirExists(rulesDir) {
		entries, _ := os.ReadDir(rulesDir)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".mdc") {
				fmt.Printf("  📋 %s\n", entry.Name())
			}
		}
	}
	fmt.Println()

	fmt.Println("========================================")
	fmt.Println("  ✅ 阶段2完成！")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Println("下一步操作：")
	fmt.Println()
	fmt.Printf("1. 📝 审查临时目录中的文件：\n")
	fmt.Printf("   - 项目描述: %s\n", filepath.Join(p.StagingDir, "plans"))
	fmt.Printf("   - 规则文件: %s\n", rulesDir)
	fmt.Println()
	fmt.Println("2. ✅ 确认无误后，执行阶段3：")
	fmt.Println("   coldstart export <目标项目目录>")
	fmt.Println()

	return nil
}

// StageExport 阶段3：导出
func (p *ProjectInitializer) StageExport(targetDir string) error {
	if !utils.DirExists(p.StagingDir) {
		return fmt.Errorf("临时目录不存在，请先运行阶段1和阶段2")
	}

	targetPath, err := filepath.Abs(targetDir)
	if err != nil {
		return fmt.Errorf("无法解析目标目录: %w", err)
	}
	if err := os.MkdirAll(targetPath, 0755); err != nil {
		return fmt.Errorf("无法创建目标目录: %w", err)
	}

	fmt.Println("========================================")
	fmt.Println("  阶段3：导出")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Printf("目标目录：%s\n", targetPath)
	fmt.Println()

	// 创建目标目录结构
	plansDir := filepath.Join(targetPath, ".cursor", "plans")
	rulesDir := filepath.Join(targetPath, ".cursor", "rules")
	if err := os.MkdirAll(plansDir, 0755); err != nil {
		return fmt.Errorf("无法创建计划目录: %w", err)
	}
	if err := os.MkdirAll(rulesDir, 0755); err != nil {
		return fmt.Errorf("无法创建规则目录: %w", err)
	}

	// 复制项目描述文档
	stagingPlans := filepath.Join(p.StagingDir, "plans")
	implementedPlans := []map[string]interface{}{}
	if utils.DirExists(stagingPlans) {
		entries, _ := os.ReadDir(stagingPlans)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".md") {
				src := filepath.Join(stagingPlans, entry.Name())
				dst := filepath.Join(plansDir, entry.Name())
				if err := utils.CopyFile(src, dst); err != nil {
					return fmt.Errorf("无法复制项目描述文档: %w", err)
				}
				implementedPlans = append(implementedPlans, map[string]interface{}{
					"name": entry.Name(),
					"path": filepath.Join(".cursor/plans", entry.Name()),
				})
			}
		}
		if len(implementedPlans) > 0 {
			fmt.Println("✅ 项目描述文档已复制")
		}
	}

	// 复制规则文件
	stagingRules := filepath.Join(p.StagingDir, "rules")
	implementedRules := []map[string]interface{}{}
	if utils.DirExists(stagingRules) {
		entries, _ := os.ReadDir(stagingRules)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".mdc") {
				src := filepath.Join(stagingRules, entry.Name())
				dst := filepath.Join(rulesDir, entry.Name())
				if err := utils.CopyFile(src, dst); err != nil {
					return fmt.Errorf("无法复制规则文件: %w", err)
				}
				implementedRules = append(implementedRules, map[string]interface{}{
					"name": entry.Name(),
					"path": filepath.Join(".cursor/rules", entry.Name()),
					"type": p.DetectRuleType(entry.Name()),
				})
			}
		}
		fmt.Println("✅ 规则文件已复制")
	}

	// 创建 .cold-start 目录
	coldStartDir := filepath.Join(targetPath, ".cold-start")
	if err := os.MkdirAll(coldStartDir, 0755); err != nil {
		return fmt.Errorf("无法创建配置目录: %w", err)
	}

	// 读取项目配置
	config, err := p.LoadConfig()
	if err != nil {
		return err
	}
	values := p.GetPlaceholderValues(config)

	// 准备模板渲染参数
	platforms := getStringSlice(config, "platforms")
	platformList := []map[string]interface{}{}
	for _, p := range platforms {
		platformList = append(platformList, map[string]interface{}{
			"id":   p,
			"name": utils.Capitalize(p),
		})
	}

	templateValues := map[string]interface{}{
		"GENERATION_DATE":         time.Now().Format(time.RFC3339),
		"PROJECT_NAME":            getString(config, "projectName", "未命名项目"),
		"PROJECT_DESCRIPTION":     getString(config, "projectDescription", ""),
		"LANGUAGE_ID":             getString(config, "language", "dart"),
		"PROGRAMMING_LANGUAGE":    getString(config, "languageName", "Dart"),
		"CODE_LANGUAGE":           getString(config, "codeLanguage", "dart"),
		"FRAMEWORK_ID":            getString(config, "framework", "flutter"),
		"FRAMEWORK":               values["FRAMEWORK"],
		"BUILD_TOOL":              getString(config, "buildTool", "Flutter CLI"),
		"PLATFORMS":               platformList,
		"INJECTED_MODULES":        []interface{}{},
		"IMPLEMENTED_PLANS":       implementedPlans,
		"IMPLEMENTED_RULES":       implementedRules,
		"ENABLE_GITHUB_ACTION":    getBool(config, "enableGitHubAction", false),
		"LOGGER_SERVICE_CLASS":    values["LOGGER_SERVICE_CLASS"],
		"LOG_FILE_PATH":           values["LOG_FILE_PATH"],
		"LOG_COLLECT_SCRIPT_PATH": values["LOG_COLLECT_SCRIPT_PATH"],
	}

	// 使用模板生成项目配置文件
	templateFile := filepath.Join(p.ProjectInitDir, "templates", "config", "project.json.template")
	configFile := filepath.Join(coldStartDir, "project.json")
	if utils.FileExists(templateFile) {
		processor := template.NewProcessor()
		if err := processor.RenderTemplateToFile(templateFile, configFile, templateValues); err != nil {
			// 如果模板渲染失败，使用默认方式
			return p.createDefaultProjectConfig(coldStartDir, templateValues, implementedPlans, implementedRules)
		}
		fmt.Println("✅ 项目配置文件已创建: .cold-start/project.json")
	} else {
		if err := p.createDefaultProjectConfig(coldStartDir, templateValues, implementedPlans, implementedRules); err != nil {
			return err
		}
	}

	// 创建 README 文件说明
	readmeFile := filepath.Join(coldStartDir, "README.md")
	readmeContent := fmt.Sprintf(`# ColdStart 项目配置

此目录由 CursorColdStart 脚手架自动创建和管理。

## 目录说明

- project.json - 项目完整配置信息
  - 项目基本信息
  - 技术方案（语言、框架、平台）
  - 已注入的模块列表
  - 已实施的文件列表

## 重要提示

⚠️ **请勿手动修改此目录中的文件**

此目录由 CursorColdStart 脚手架自动管理：
- 使用 inject 命令注入模块时，会自动更新此配置
- 使用 extract-rules 命令提取规则时，会读取此配置

如需修改项目配置，请使用 CursorColdStart 脚手架的命令。

## 项目信息

- **项目名称：** %v
- **技术栈：** %v + %v
- **目标平台：** %v
- **初始化时间：** %v
`, templateValues["PROJECT_NAME"], templateValues["PROGRAMMING_LANGUAGE"], templateValues["FRAMEWORK"],
		strings.Join(platforms, ", "), templateValues["GENERATION_DATE"])

	if err := os.WriteFile(readmeFile, []byte(readmeContent), 0644); err != nil {
		return fmt.Errorf("无法创建README文件: %w", err)
	}
	fmt.Println("✅ 说明文件已创建: .cold-start/README.md")

	// 显示生成的文件
	fmt.Println()
	fmt.Println("生成的文件：")
	if utils.DirExists(plansDir) {
		entries, _ := os.ReadDir(plansDir)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".mdc") {
				fmt.Printf("  📋 %s\n", entry.Name())
			}
		}
	}
	if utils.DirExists(rulesDir) {
		entries, _ := os.ReadDir(rulesDir)
		for _, entry := range entries {
			if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".mdc") {
				fmt.Printf("  📋 %s\n", entry.Name())
			}
		}
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ✅ 阶段3完成！文件已导出到目标项目")
	fmt.Println("========================================")
	fmt.Println()
	fmt.Println("下一步操作：")
	fmt.Println()
	fmt.Println("1. 🤖 在 Cursor 中告诉 AI 助手：")
	fmt.Println("   开始项目初始化")
	fmt.Println()

	// 清理临时目录
	fmt.Print("是否清理临时目录？(y/n): ")
	reader := bufio.NewReader(os.Stdin)
	cleanup, _ := reader.ReadString('\n')
	cleanup = strings.TrimSpace(strings.ToLower(cleanup))
	if cleanup == "y" {
		if err := utils.RemoveDir(p.StagingDir); err != nil {
			fmt.Printf("⚠️  无法清理临时目录: %v\n", err)
		} else {
			fmt.Println("✅ 临时目录已清理")
		}
	} else {
		fmt.Printf("临时目录保留在: %s\n", p.StagingDir)
	}
	fmt.Println()

	return nil
}

// createDefaultProjectConfig 创建默认项目配置
func (p *ProjectInitializer) createDefaultProjectConfig(coldStartDir string, templateValues map[string]interface{}, implementedPlans, implementedRules []map[string]interface{}) error {
	projectInfo := map[string]interface{}{
		"version":     "1.0.0",
		"generatedAt": templateValues["GENERATION_DATE"],
		"generatedBy": "CursorColdStart",
		"project": map[string]interface{}{
			"name":        templateValues["PROJECT_NAME"],
			"description": templateValues["PROJECT_DESCRIPTION"],
		},
		"technology": map[string]interface{}{
			"language": map[string]interface{}{
				"id":           templateValues["LANGUAGE_ID"],
				"name":         templateValues["PROGRAMMING_LANGUAGE"],
				"codeLanguage": templateValues["CODE_LANGUAGE"],
			},
			"framework": map[string]interface{}{
				"id":        templateValues["FRAMEWORK_ID"],
				"name":      templateValues["FRAMEWORK"],
				"buildTool": templateValues["BUILD_TOOL"],
			},
			"platforms": templateValues["PLATFORMS"],
		},
		"modules": map[string]interface{}{
			"injected":  []interface{}{},
			"available": []interface{}{},
		},
		"files": map[string]interface{}{
			"plans": implementedPlans,
			"rules": implementedRules,
		},
		"config": map[string]interface{}{
			"enableGitHubAction": templateValues["ENABLE_GITHUB_ACTION"],
			"logService": map[string]interface{}{
				"class":         templateValues["LOGGER_SERVICE_CLASS"],
				"filePath":      templateValues["LOG_FILE_PATH"],
				"collectScript": templateValues["LOG_COLLECT_SCRIPT_PATH"],
			},
		},
	}

	configFile := filepath.Join(coldStartDir, "project.json")
	data, err := json.MarshalIndent(projectInfo, "", "  ")
	if err != nil {
		return fmt.Errorf("无法序列化配置: %w", err)
	}

	if err := os.WriteFile(configFile, data, 0644); err != nil {
		return fmt.Errorf("无法写入配置文件: %w", err)
	}

	fmt.Println("✅ 项目配置文件已创建: .cold-start/project.json")
	return nil
}

// DetectRuleType 检测规则类型
func (p *ProjectInitializer) DetectRuleType(ruleFilename string) string {
	if strings.HasPrefix(ruleFilename, "00-") || strings.HasPrefix(ruleFilename, "0") && len(ruleFilename) > 2 && ruleFilename[2] >= '0' && ruleFilename[2] <= '9' {
		return "common"
	}
	if strings.HasPrefix(ruleFilename, "10-") {
		return "language"
	}
	if strings.HasPrefix(ruleFilename, "20-") {
		return "framework"
	}
	if strings.HasPrefix(ruleFilename, "30-") {
		return "platform"
	}
	if strings.HasPrefix(ruleFilename, "40-") {
		return "module"
	}
	return "unknown"
}

// 辅助函数
func getSlice(m map[string]interface{}, key string) ([]interface{}, bool) {
	if v, ok := m[key]; ok {
		if arr, ok := v.([]interface{}); ok {
			return arr, true
		}
	}
	return []interface{}{}, false
}

func getFloat64(m map[string]interface{}, key string, defaultValue float64) float64 {
	if v, ok := m[key]; ok {
		if f, ok := v.(float64); ok {
			return f
		}
		if i, ok := v.(int); ok {
			return float64(i)
		}
	}
	return defaultValue
}
