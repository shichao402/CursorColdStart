package template

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"text/template"
)

// Processor 模板处理器
type Processor struct {
	funcMap template.FuncMap
}

// NewProcessor 创建新的模板处理器
func NewProcessor() *Processor {
	p := &Processor{
		funcMap: template.FuncMap{
			"upper": strings.ToUpper,
			"lower": strings.ToLower,
			"title": func(s string) string {
				// strings.Title 已废弃，使用替代实现
				if len(s) == 0 {
					return s
				}
				return strings.ToUpper(s[:1]) + strings.ToLower(s[1:])
			},
			"join": strings.Join,
		},
	}
	return p
}

// RenderTemplate 渲染模板文件
func (p *Processor) RenderTemplate(templatePath string, values map[string]interface{}) (string, error) {
	// 读取模板文件
	data, err := os.ReadFile(templatePath)
	if err != nil {
		return "", fmt.Errorf("无法读取模板文件: %w", err)
	}

	// 转换 Jinja2 语法到 Go template 语法
	content := convertJinja2ToGoTemplate(string(data))

	// 创建模板
	tmpl, err := template.New(filepath.Base(templatePath)).
		Funcs(p.funcMap).
		Parse(content)
	if err != nil {
		return "", fmt.Errorf("无法解析模板: %w", err)
	}

	// 渲染模板
	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, values); err != nil {
		return "", fmt.Errorf("无法渲染模板: %w", err)
	}

	return buf.String(), nil
}

// convertJinja2ToGoTemplate 将 Jinja2 语法转换为 Go template 语法
func convertJinja2ToGoTemplate(content string) string {
	// 先处理条件语句，避免与变量替换冲突
	// {% if VARIABLE %} -> {{ if .VARIABLE }}
	ifRe := regexp.MustCompile(`\{\%\s*if\s+([A-Z_][A-Z0-9_]*)\s*\%\}`)
	content = ifRe.ReplaceAllString(content, "{{ if .$1 }}")
	content = strings.ReplaceAll(content, "{% endif %}", "{{ end }}")

	// {% if not VARIABLE %} -> {{ if not .VARIABLE }}
	ifNotRe := regexp.MustCompile(`\{\%\s*if\s+not\s+([A-Z_][A-Z0-9_]*)\s*\%\}`)
	content = ifNotRe.ReplaceAllString(content, "{{ if not .$1 }}")

	// 转换循环: {% for item in items %} -> {{ range .items }}
	forRe := regexp.MustCompile(`\{\%\s*for\s+\w+\s+in\s+([A-Z_][A-Z0-9_]*)\s*\%\}`)
	content = forRe.ReplaceAllString(content, "{{ range .$1 }}")
	content = strings.ReplaceAll(content, "{% endfor %}", "{{ end }}")

	// 转换变量: {{ VARIABLE }} -> {{ .VARIABLE }}
	// 匹配 {{ VARIABLE }} 格式，但排除已经转换过的 {{ .VARIABLE }} 和 {{ if .VARIABLE }} 等
	varRe := regexp.MustCompile(`\{\{\s+([A-Z_][A-Z0-9_]*)\s+\}\}`)
	content = varRe.ReplaceAllStringFunc(content, func(match string) string {
		// 检查是否已经包含点号（已转换）
		if strings.Contains(match, "{{ .") {
			return match
		}
		// 提取变量名
		varName := regexp.MustCompile(`\{\{\s+([A-Z_][A-Z0-9_]*)\s+\}\}`).FindStringSubmatch(match)[1]
		return "{{ ." + varName + " }}"
	})

	return content
}

// RenderTemplateToFile 渲染模板并写入文件
func (p *Processor) RenderTemplateToFile(templatePath, outputPath string, values map[string]interface{}) error {
	// 渲染模板
	content, err := p.RenderTemplate(templatePath, values)
	if err != nil {
		return err
	}

	// 确保输出目录存在
	if err := os.MkdirAll(filepath.Dir(outputPath), 0755); err != nil {
		return fmt.Errorf("无法创建输出目录: %w", err)
	}

	// 写入文件
	if err := os.WriteFile(outputPath, []byte(content), 0644); err != nil {
		return fmt.Errorf("无法写入文件: %w", err)
	}

	return nil
}

// ProcessTemplates 批量处理模板文件
func (p *Processor) ProcessTemplates(templateDir, outputDir string, values map[string]interface{}, pattern string) error {
	// 查找所有模板文件
	matches, err := filepath.Glob(filepath.Join(templateDir, pattern))
	if err != nil {
		return fmt.Errorf("无法查找模板文件: %w", err)
	}

	for _, templatePath := range matches {
		// 计算输出路径
		relPath, err := filepath.Rel(templateDir, templatePath)
		if err != nil {
			return fmt.Errorf("无法计算相对路径: %w", err)
		}

		// 移除 .template 扩展名
		outputPath := filepath.Join(outputDir, strings.TrimSuffix(relPath, ".template"))

		// 渲染模板
		if err := p.RenderTemplateToFile(templatePath, outputPath, values); err != nil {
			return fmt.Errorf("处理模板 %s 时出错: %w", templatePath, err)
		}
	}

	return nil
}
