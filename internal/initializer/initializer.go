package initializer

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// ProjectInitializer 项目初始化器
type ProjectInitializer struct {
	ProjectRoot    string
	ProjectInitDir string
	StagingDir     string
	ConfigFile     string
}

// New 创建新的项目初始化器
func New(projectRoot string) (*ProjectInitializer, error) {
	absRoot, err := filepath.Abs(projectRoot)
	if err != nil {
		return nil, fmt.Errorf("无法解析项目根目录: %w", err)
	}

	init := &ProjectInitializer{
		ProjectRoot:    absRoot,
		ProjectInitDir: filepath.Join(absRoot, "rules_template"),
		StagingDir:     filepath.Join(absRoot, ".cold-start-staging"),
		ConfigFile:     filepath.Join(absRoot, ".cold-start-staging", "config.json"),
	}

	// 检查 rules_template 目录
	if _, err := os.Stat(init.ProjectInitDir); os.IsNotExist(err) {
		return nil, fmt.Errorf("找不到 rules_template 目录: %s", init.ProjectInitDir)
	}

	return init, nil
}

// LoadOptions 加载选项配置文件
func (p *ProjectInitializer) LoadOptions() (map[string]interface{}, error) {
	optionsFile := filepath.Join(p.ProjectInitDir, "options.json")
	data, err := os.ReadFile(optionsFile)
	if err != nil {
		return nil, fmt.Errorf("无法读取选项配置文件: %w", err)
	}

	var options map[string]interface{}
	if err := json.Unmarshal(data, &options); err != nil {
		return nil, fmt.Errorf("无法解析选项配置文件: %w", err)
	}

	return options, nil
}

// LoadConfig 加载项目配置文件
func (p *ProjectInitializer) LoadConfig() (map[string]interface{}, error) {
	data, err := os.ReadFile(p.ConfigFile)
	if err != nil {
		return nil, fmt.Errorf("配置文件不存在: %w", err)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("无法解析配置文件: %w", err)
	}

	return config, nil
}

// SaveConfig 保存项目配置文件
func (p *ProjectInitializer) SaveConfig(config map[string]interface{}) error {
	if err := os.MkdirAll(filepath.Dir(p.ConfigFile), 0755); err != nil {
		return fmt.Errorf("无法创建配置目录: %w", err)
	}

	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("无法序列化配置: %w", err)
	}

	if err := os.WriteFile(p.ConfigFile, data, 0644); err != nil {
		return fmt.Errorf("无法写入配置文件: %w", err)
	}

	return nil
}

// GetPlaceholderValues 生成所有占位符的值
func (p *ProjectInitializer) GetPlaceholderValues(config map[string]interface{}) map[string]interface{} {
	lang := getString(config, "language", "dart")
	framework := getString(config, "framework", "flutter")
	buildTool := getString(config, "buildTool", "Flutter CLI")

	platforms := getStringSlice(config, "platforms")
	targetPlatforms := ""
	if len(platforms) > 0 {
		targetPlatforms = platforms[0]
		for i := 1; i < len(platforms); i++ {
			targetPlatforms += ", " + platforms[i]
		}
	} else {
		targetPlatforms = "web"
	}

	values := map[string]interface{}{
		"PROJECT_NAME":            getString(config, "projectName", "未命名项目"),
		"PROGRAMMING_LANGUAGE":    getString(config, "languageName", "Dart"),
		"FRAMEWORK":               framework,
		"BUILD_TOOL":              buildTool,
		"CODE_LANGUAGE":           getString(config, "codeLanguage", lang),
		"TARGET_PLATFORMS":        targetPlatforms,
		"MODULE_NAME":             "应用",
		"MODULE_PATH":             "**",
		"GENERATION_DATE":         time.Now().Format("2006-01-02 15:04:05"),
		"ENABLE_GITHUB_ACTION":    getBool(config, "enableGitHubAction", false),
		"LOGGER_SERVICE_CLASS":    "Logger",
		"LOG_FILE_PATH":           "logs/app.log",
		"LOG_COLLECT_SCRIPT_PATH": "scripts/collect_logs.sh",
		"LOG_COLLECT_COMMAND":     "./scripts/collect_logs.sh",
	}

	// 根据语言设置额外的API方法
	if lang == "typescript" || lang == "javascript" {
		values["ADDITIONAL_API_METHODS"] = "- 警告日志：`logger.warn('警告', tag: 'TAG')`"
	} else {
		values["ADDITIONAL_API_METHODS"] = ""
	}

	// 根据框架生成部署相关占位符
	deployTemplates := p.getDeployTemplates(framework)
	for k, v := range deployTemplates {
		values[k] = v
	}

	return values
}

// getDeployTemplates 根据框架获取部署模板
func (p *ProjectInitializer) getDeployTemplates(framework string) map[string]string {
	templates := map[string]map[string]string{
		"flutter": {
			"DEPLOY_SCRIPTS_DESCRIPTION":  "**部署脚本：** `scripts/deploy.sh`\n\n此脚本用于部署Flutter应用到目标平台。AI必须使用此脚本进行部署，不得手动执行flutter命令。\n\n**脚本功能：**\n- 自动检测连接的设备\n- 构建应用\n- 安装到设备\n- 启动应用",
			"DEPLOY_STEPS_DESCRIPTION":    "1. **使用部署脚本部署应用**\n   - 执行：`./scripts/deploy.sh`\n   - 脚本会自动构建、安装并启动应用",
			"DEPLOY_COMMANDS_DESCRIPTION": "**部署命令：**\n\n```bash\n./scripts/deploy.sh\n```\n\n此脚本会：\n- 检查Flutter环境\n- 构建应用（`flutter build`）\n- 安装到设备（`flutter install`）\n- 启动应用（`flutter run`）",
		},
		"react": {
			"DEPLOY_SCRIPTS_DESCRIPTION":  "**部署脚本：** `scripts/deploy.sh`\n\n此脚本用于构建和部署Web应用。AI必须使用此脚本进行部署，不得手动执行npm/yarn命令。\n\n**脚本功能：**\n- 安装依赖\n- 构建应用\n- 启动开发服务器或部署到生产环境",
			"DEPLOY_STEPS_DESCRIPTION":    "1. **使用部署脚本部署应用**\n   - 执行：`./scripts/deploy.sh`\n   - 脚本会自动构建并启动应用",
			"DEPLOY_COMMANDS_DESCRIPTION": "**部署命令：**\n\n```bash\n./scripts/deploy.sh\n```\n\n此脚本会：\n- 安装依赖（`npm install` 或 `yarn install`）\n- 构建应用（`npm run build` 或 `yarn build`）\n- 启动开发服务器（`npm run dev` 或 `yarn dev`）",
		},
		"django": {
			"DEPLOY_SCRIPTS_DESCRIPTION":  "**部署脚本：** `scripts/deploy.sh`\n\n此脚本用于部署Python应用。AI必须使用此脚本进行部署，不得手动执行pip/python命令。\n\n**脚本功能：**\n- 安装依赖\n- 运行数据库迁移\n- 启动应用服务器",
			"DEPLOY_STEPS_DESCRIPTION":    "1. **使用部署脚本部署应用**\n   - 执行：`./scripts/deploy.sh`\n   - 脚本会自动安装依赖并启动应用",
			"DEPLOY_COMMANDS_DESCRIPTION": "**部署命令：**\n\n```bash\n./scripts/deploy.sh\n```\n\n此脚本会：\n- 安装依赖（`pip install -r requirements.txt`）\n- 运行数据库迁移（如适用）\n- 启动应用服务器（`python manage.py runserver` 或 `uvicorn app:app`）",
		},
	}

	// 默认模板
	defaultTemplates := map[string]string{
		"DEPLOY_SCRIPTS_DESCRIPTION":  "**部署脚本：** `scripts/deploy.sh`\n\n此脚本用于部署应用。AI必须使用此脚本进行部署，不得手动执行构建命令。\n\n**脚本功能：**\n- 构建应用\n- 部署到目标环境",
		"DEPLOY_STEPS_DESCRIPTION":    "1. **使用部署脚本部署应用**\n   - 执行：`./scripts/deploy.sh`\n   - 脚本会自动构建并部署应用",
		"DEPLOY_COMMANDS_DESCRIPTION": "**部署命令：**\n\n```bash\n./scripts/deploy.sh\n```\n\n此脚本会构建并部署应用。",
	}

	if fwTemplates, ok := templates[framework]; ok {
		return fwTemplates
	}
	return defaultTemplates
}

// 辅助函数
func getString(m map[string]interface{}, key, defaultValue string) string {
	if v, ok := m[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return defaultValue
}

func getBool(m map[string]interface{}, key string, defaultValue bool) bool {
	if v, ok := m[key]; ok {
		if b, ok := v.(bool); ok {
			return b
		}
	}
	return defaultValue
}

func getStringSlice(m map[string]interface{}, key string) []string {
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
	}
	return []string{}
}
