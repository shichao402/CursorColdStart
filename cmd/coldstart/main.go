package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/cursor-cold-start/cursor-cold-start/internal/commands"
)

const (
	version = "2.0.0"
	usage   = `CursorColdStart - 项目AI冷启动初始化系统

使用方式:
  coldstart <command> [options] [target-dir]

命令:
  init <target-dir>              初始化项目（生成配置文件和规则）
  list [type]                    列出可用选项（languages/frameworks/platforms/modules）
  version                        显示版本信息
  help                           显示帮助信息

示例:
  coldstart init ./my-project    # 初始化项目
  coldstart list languages       # 列出支持的语言
  coldstart list frameworks      # 列出支持的框架

工作流程:
  1. coldstart init ./project    # 首次：生成空配置 + 通用规则
  2. 让 AI 帮助填写配置文件       # .cursor-cold-start/config/*.json
  3. coldstart init ./project    # 再次：根据配置生成定制规则
`
)

func main() {
	if len(os.Args) < 2 {
		fmt.Print(usage)
		os.Exit(0)
	}

	cmd := os.Args[1]
	args := os.Args[2:]

	// 获取工具根目录（rules_template 所在目录）
	toolRoot, err := findToolRoot()
	if err != nil {
		fmt.Fprintf(os.Stderr, "❌ 错误: %v\n", err)
		os.Exit(1)
	}

	executor := commands.NewExecutor(toolRoot)

	switch cmd {
	case "init":
		if len(args) < 1 {
			fmt.Fprintln(os.Stderr, "❌ 错误: 缺少目标目录")
			fmt.Fprintln(os.Stderr, "使用方法: coldstart init <target-dir>")
			os.Exit(1)
		}
		if err := executor.Init(args[0]); err != nil {
			fmt.Fprintf(os.Stderr, "❌ 错误: %v\n", err)
			os.Exit(1)
		}

	case "list":
		listType := ""
		if len(args) > 0 {
			listType = args[0]
		}
		if err := executor.List(listType); err != nil {
			fmt.Fprintf(os.Stderr, "❌ 错误: %v\n", err)
			os.Exit(1)
		}

	case "version", "-v", "--version":
		fmt.Printf("coldstart version %s\n", version)

	case "help", "-h", "--help":
		fmt.Print(usage)

	default:
		fmt.Fprintf(os.Stderr, "❌ 错误: 未知命令 '%s'\n", cmd)
		fmt.Fprintln(os.Stderr, "运行 'coldstart help' 查看可用命令")
		os.Exit(1)
	}
}

// findToolRoot 查找工具根目录（rules_template 所在目录）
func findToolRoot() (string, error) {
	// 1. 优先检查当前工作目录
	cwd, err := os.Getwd()
	if err == nil {
		if _, err := os.Stat(filepath.Join(cwd, "rules_template")); err == nil {
			return cwd, nil
		}
	}

	// 2. 检查可执行文件所在目录
	execPath, err := os.Executable()
	if err != nil {
		return "", fmt.Errorf("找不到 rules_template 目录，请在 CursorColdStart 项目目录下运行")
	}

	// 解析符号链接，获取实际路径
	realPath, err := filepath.EvalSymlinks(execPath)
	if err != nil {
		realPath = execPath
	}

	execDir := filepath.Dir(realPath)
	if _, err := os.Stat(filepath.Join(execDir, "rules_template")); err == nil {
		return execDir, nil
	}

	// 3. 检查可执行文件的父目录（如 bin/coldstart）
	parentDir := filepath.Dir(execDir)
	if _, err := os.Stat(filepath.Join(parentDir, "rules_template")); err == nil {
		return parentDir, nil
	}

	return "", fmt.Errorf("找不到 rules_template 目录，请在 CursorColdStart 项目目录下运行")
}
