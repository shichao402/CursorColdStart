#!/bin/bash

# 项目初始化系统清理脚本
# 用途：清理冷启动过程中创建的临时文件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录（project-init目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 处理参数：如果提供了目录参数，使用该目录；否则使用当前目录
if [ -n "$1" ]; then
    # 提供了目录参数
    if [ -d "$1" ]; then
        PROJECT_ROOT="$(cd "$1" && pwd)"
        echo -e "${BLUE}使用指定目录: $PROJECT_ROOT${NC}"
    else
        echo -e "${RED}❌ 错误：指定的目录不存在: $1${NC}"
        echo -e "${YELLOW}清理脚本需要指定一个已存在的项目目录${NC}"
        exit 1
    fi
else
    # 没有提供参数，使用当前目录
    PROJECT_ROOT="$(pwd)"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  项目AI冷启动清理工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  此脚本将清理项目初始化过程中创建的临时文件${NC}"
echo ""

# 检测是否在模板项目本身中运行（且没有指定目标目录）
if [ -z "$1" ] && [ -d "$PROJECT_ROOT/project-init" ] && [ "$SCRIPT_DIR" = "$PROJECT_ROOT/project-init" ]; then
    echo -e "${YELLOW}⚠️  警告：检测到你在模板项目本身中运行此脚本${NC}"
    echo ""
    echo -e "${YELLOW}此脚本主要用于清理新项目中的初始化文件。${NC}"
    echo ""
    echo -e "${BLUE}使用方法：${NC}"
    echo "   $0 [项目目录路径]"
    echo ""
    echo -e "${YELLOW}如果你确实想在模板项目中清理测试文件，可以继续。${NC}"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 检查是否在项目根目录
if [ ! -f "$PROJECT_ROOT/.git" ] && [ ! -f "$PROJECT_ROOT/.gitignore" ] && [ ! -d "$PROJECT_ROOT/.cursor" ] && [ ! -f "$PROJECT_ROOT/package.json" ] && [ ! -f "$PROJECT_ROOT/pubspec.yaml" ] && [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  警告：当前目录可能不是项目根目录${NC}"
    echo -e "${YELLOW}   建议在项目根目录运行此脚本${NC}"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 定义要清理的文件和目录
INIT_DIR="$PROJECT_ROOT/.cold-start/project-init"
PROJECT_PLAN="$INIT_DIR/ProjectPlan.md"
PLANS_DIR="$PROJECT_ROOT/.cursor/plans"
TECH_STACK_JSON="$PROJECT_ROOT/tech_stack.json"
INIT_REPORT="$PROJECT_ROOT/PROJECT_INIT_REPORT.md"
RULE_FILE="$PROJECT_ROOT/.cursor/rules/00-PROJECT_INIT_RULE.mdc"

# 显示将要清理的文件
echo -e "${BLUE}以下文件/目录将被清理：${NC}"
echo ""

FILES_TO_CLEAN=()

if [ -d "$INIT_DIR" ]; then
    echo -e "  📁 $INIT_DIR"
    FILES_TO_CLEAN+=("$INIT_DIR")
fi

if [ -f "$PROJECT_PLAN" ]; then
    echo -e "  📄 $PROJECT_PLAN"
    FILES_TO_CLEAN+=("$PROJECT_PLAN")
fi

if [ -d "$PLANS_DIR" ] && [ "$(ls -A $PLANS_DIR 2>/dev/null)" ]; then
    echo -e "  📁 $PLANS_DIR/*"
    FILES_TO_CLEAN+=("$PLANS_DIR")
fi

if [ -f "$TECH_STACK_JSON" ]; then
    echo -e "  📄 $TECH_STACK_JSON"
    FILES_TO_CLEAN+=("$TECH_STACK_JSON")
fi

if [ -f "$INIT_REPORT" ]; then
    echo -e "  📄 $INIT_REPORT"
    FILES_TO_CLEAN+=("$INIT_REPORT")
fi

if [ -f "$RULE_FILE" ]; then
    echo -e "  📄 $RULE_FILE"
    FILES_TO_CLEAN+=("$RULE_FILE")
fi

if [ ${#FILES_TO_CLEAN[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ 没有找到需要清理的文件${NC}"
    echo ""
    exit 0
fi

echo ""
read -p "是否继续清理？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消清理${NC}"
    exit 0
fi

echo ""

# 逐个询问清理
CLEANED_COUNT=0

# 1. 清理初始化系统目录
if [ -d "$INIT_DIR" ]; then
    echo -e "${BLUE}清理初始化系统目录...${NC}"
    read -p "删除 $INIT_DIR？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INIT_DIR"
        echo -e "${GREEN}✅ 已删除${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
        
        # 如果 .cold-start 目录为空，也删除
        if [ -d "$PROJECT_ROOT/.cold-start" ] && [ -z "$(ls -A $PROJECT_ROOT/.cold-start 2>/dev/null)" ]; then
            rmdir "$PROJECT_ROOT/.cold-start"
            echo -e "${GREEN}✅ 已删除空目录: .cold-start${NC}"
        fi
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 2. 清理项目计划文档（在冷启动目录内）
if [ -f "$PROJECT_PLAN" ]; then
    echo -e "${BLUE}清理项目计划文档...${NC}"
    read -p "删除 $PROJECT_PLAN？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$PROJECT_PLAN"
        echo -e "${GREEN}✅ 已删除${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 3. 清理计划目录
if [ -d "$PLANS_DIR" ] && [ "$(ls -A $PLANS_DIR 2>/dev/null)" ]; then
    echo -e "${BLUE}清理计划目录...${NC}"
    read -p "删除 $PLANS_DIR 中的所有文件？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PLANS_DIR"/*
        echo -e "${GREEN}✅ 已清理${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 4. 清理技术选型记录
if [ -f "$TECH_STACK_JSON" ]; then
    echo -e "${BLUE}清理技术选型记录...${NC}"
    read -p "删除 $TECH_STACK_JSON？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$TECH_STACK_JSON"
        echo -e "${GREEN}✅ 已删除${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 5. 清理初始化报告
if [ -f "$INIT_REPORT" ]; then
    echo -e "${BLUE}清理初始化报告...${NC}"
    read -p "删除 $INIT_REPORT？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$INIT_REPORT"
        echo -e "${GREEN}✅ 已删除${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 6. 清理初始化规则文件
if [ -f "$RULE_FILE" ]; then
    echo -e "${BLUE}清理初始化规则文件...${NC}"
    echo -e "${YELLOW}⚠️  注意：删除此文件后，AI助手将无法识别项目初始化系统${NC}"
    read -p "删除 $RULE_FILE？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$RULE_FILE"
        echo -e "${GREEN}✅ 已删除${NC}"
        CLEANED_COUNT=$((CLEANED_COUNT + 1))
    else
        echo -e "${YELLOW}跳过${NC}"
    fi
    echo ""
fi

# 总结
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 清理完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "已清理 ${CLEANED_COUNT} 个项目"
echo ""

# 检查是否还有残留文件
REMAINING_FILES=()

if [ -d "$INIT_DIR" ]; then
    REMAINING_FILES+=("$INIT_DIR")
fi

if [ -f "$PROJECT_PLAN" ]; then
    REMAINING_FILES+=("$PROJECT_PLAN")
fi

if [ -f "$TECH_STACK_JSON" ]; then
    REMAINING_FILES+=("$TECH_STACK_JSON")
fi

if [ -f "$INIT_REPORT" ]; then
    REMAINING_FILES+=("$INIT_REPORT")
fi

if [ ${#REMAINING_FILES[@]} -gt 0 ]; then
    echo -e "${YELLOW}以下文件/目录被保留：${NC}"
    for file in "${REMAINING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
fi

echo -e "${BLUE}提示：${NC}"
echo "- 项目初始化规则文件（.cursor/rules/*.mdc）已保留"
echo "- 日志服务和脚本文件已保留"
echo "- 如需完全清理，请手动删除相关文件"
echo ""

