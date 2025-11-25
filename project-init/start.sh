#!/bin/bash

# 项目初始化系统启动脚本
# 用途：交互式地完成项目初始化设置

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
        echo -e "${YELLOW}⚠️  指定的目录不存在: $1${NC}"
        read -p "是否创建该目录？(y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p "$1"
            PROJECT_ROOT="$(cd "$1" && pwd)"
            echo -e "${GREEN}✅ 目录已创建: $PROJECT_ROOT${NC}"
        else
            echo -e "${RED}❌ 已取消${NC}"
            exit 1
        fi
    fi
else
    # 没有提供参数，使用当前目录
    PROJECT_ROOT="$(pwd)"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  项目AI冷启动初始化系统${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检测是否在模板项目本身中运行（且没有指定目标目录）
if [ -z "$1" ] && [ -d "$PROJECT_ROOT/project-init" ] && [ "$SCRIPT_DIR" = "$PROJECT_ROOT/project-init" ]; then
    echo -e "${RED}❌ 错误：检测到你在模板项目本身中运行此脚本${NC}"
    echo ""
    echo -e "${YELLOW}此脚本应该在新项目中使用，而不是在模板项目（CursorColdStart）中运行。${NC}"
    echo ""
    echo -e "${BLUE}正确的使用方法：${NC}"
    echo ""
    echo "方法1：指定目标项目目录"
    echo "   $0 /path/to/your-new-project"
    echo ""
    echo "方法2：在新项目中运行"
    echo "   1. 复制 project-init 目录到你的新项目："
    echo "      cp -r $PROJECT_ROOT/project-init /path/to/your-new-project/.cold-start/project-init"
    echo ""
    echo "   2. 在新项目根目录运行："
    echo "      cd /path/to/your-new-project"
    echo "      ./.cold-start/project-init/start.sh"
    echo ""
    exit 1
fi

# 检查是否在项目根目录（仅在未指定目录参数时检查）
if [ -z "$1" ] && [ ! -f "$PROJECT_ROOT/.git" ] && [ ! -f "$PROJECT_ROOT/.gitignore" ] && [ ! -d "$PROJECT_ROOT/.cursor" ] && [ ! -f "$PROJECT_ROOT/package.json" ] && [ ! -f "$PROJECT_ROOT/pubspec.yaml" ] && [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  警告：当前目录可能不是项目根目录${NC}"
    echo -e "${YELLOW}   建议在项目根目录运行此脚本${NC}"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 步骤1：复制初始化系统文件
echo -e "${GREEN}[步骤 1/4] 复制初始化系统文件...${NC}"
echo ""
INIT_DIR="$PROJECT_ROOT/.cold-start/project-init"

# 如果脚本就在目标目录中，不需要复制
if [ "$SCRIPT_DIR" = "$INIT_DIR" ]; then
    echo -e "${GREEN}✅ 脚本已在目标位置，跳过复制${NC}"
else
    if [ -d "$INIT_DIR" ]; then
        echo -e "${YELLOW}⚠️  目录已存在: $INIT_DIR${NC}"
        read -p "是否覆盖？(y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INIT_DIR"
        else
            echo -e "${YELLOW}跳过复制步骤${NC}"
        fi
    fi

    if [ ! -d "$INIT_DIR" ]; then
        mkdir -p "$(dirname "$INIT_DIR")"
        cp -r "$SCRIPT_DIR" "$INIT_DIR"
        echo -e "${GREEN}✅ 初始化系统文件已复制到: $INIT_DIR${NC}"
    else
        echo -e "${GREEN}✅ 使用现有初始化系统文件${NC}"
    fi
fi
echo ""

# 步骤2：交互式收集核心项目信息
echo -e "${GREEN}[步骤 2/4] 收集项目信息...${NC}"
mkdir -p "$INIT_DIR"
CONFIG_FILE="$INIT_DIR/project-config.json"

# 如果配置文件已存在，询问是否重新收集
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠️  配置文件已存在: $CONFIG_FILE${NC}"
    read -p "是否重新收集信息并覆盖？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 使用现有配置文件${NC}"
        SKIP_COLLECT=true
    fi
fi

if [ "$SKIP_COLLECT" != "true" ]; then
    echo ""
    echo -e "${BLUE}请回答以下核心问题：${NC}"
    echo ""
    
    # 收集项目名称
    read -p "项目名称: " PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-"未命名项目"}
    
    # 收集编程语言
    echo ""
    echo "编程语言："
    echo "  1) Dart"
    echo "  2) TypeScript/JavaScript"
    echo "  3) Python"
    echo "  4) Kotlin/Java"
    echo "  5) Swift"
    read -p "请选择 (1-5): " LANG_CHOICE
    case $LANG_CHOICE in
        1) LANG="dart"; LANG_NAME="Dart" ;;
        2) LANG="typescript"; LANG_NAME="TypeScript" ;;
        3) LANG="python"; LANG_NAME="Python" ;;
        4) LANG="kotlin"; LANG_NAME="Kotlin" ;;
        5) LANG="swift"; LANG_NAME="Swift" ;;
        *) LANG="dart"; LANG_NAME="Dart" ;;
    esac
    
    # 收集框架
    echo ""
    echo "框架/平台："
    case $LANG in
        dart)
            echo "  1) Flutter"
            echo "  2) 纯Dart"
            read -p "请选择 (1-2): " FW_CHOICE
            case $FW_CHOICE in
                1) FRAMEWORK="flutter" ;;
                2) FRAMEWORK="dart" ;;
                *) FRAMEWORK="flutter" ;;
            esac
            ;;
        typescript)
            echo "  1) React"
            echo "  2) Vue"
            echo "  3) Node.js"
            read -p "请选择 (1-3): " FW_CHOICE
            case $FW_CHOICE in
                1) FRAMEWORK="react" ;;
                2) FRAMEWORK="vue" ;;
                3) FRAMEWORK="nodejs" ;;
                *) FRAMEWORK="react" ;;
            esac
            ;;
        python)
            echo "  1) Django"
            echo "  2) FastAPI"
            echo "  3) 纯Python"
            read -p "请选择 (1-3): " FW_CHOICE
            case $FW_CHOICE in
                1) FRAMEWORK="django" ;;
                2) FRAMEWORK="fastapi" ;;
                3) FRAMEWORK="python" ;;
                *) FRAMEWORK="django" ;;
            esac
            ;;
        kotlin)
            echo "  1) Android"
            echo "  2) Spring Boot"
            read -p "请选择 (1-2): " FW_CHOICE
            case $FW_CHOICE in
                1) FRAMEWORK="android" ;;
                2) FRAMEWORK="spring" ;;
                *) FRAMEWORK="android" ;;
            esac
            ;;
        swift)
            FRAMEWORK="ios"
            ;;
        *)
            read -p "请输入框架名称: " FRAMEWORK
            ;;
    esac
    
    # 收集目标平台（多选）
    echo ""
    echo "目标平台（可多选，用空格分隔，如：1 3 4）："
    echo "  1) Android"
    echo "  2) iOS"
    echo "  3) macOS"
    echo "  4) Windows"
    echo "  5) Linux"
    echo "  6) Web"
    read -p "请选择: " PLATFORM_CHOICES
    PLATFORMS=()
    for choice in $PLATFORM_CHOICES; do
        case $choice in
            1) PLATFORMS+=("android") ;;
            2) PLATFORMS+=("ios") ;;
            3) PLATFORMS+=("macos") ;;
            4) PLATFORMS+=("windows") ;;
            5) PLATFORMS+=("linux") ;;
            6) PLATFORMS+=("web") ;;
        esac
    done
    if [ ${#PLATFORMS[@]} -eq 0 ]; then
        PLATFORMS=("web")
    fi
    
    # 生成 JSON 配置文件
    PLATFORMS_JSON="["
    for i in "${!PLATFORMS[@]}"; do
        if [ $i -gt 0 ]; then
            PLATFORMS_JSON="${PLATFORMS_JSON}, "
        fi
        PLATFORMS_JSON="${PLATFORMS_JSON}\"${PLATFORMS[$i]}\""
    done
    PLATFORMS_JSON="${PLATFORMS_JSON}]"
    
    cat > "$CONFIG_FILE" << EOF
{
  "projectName": "${PROJECT_NAME}",
  "language": "${LANG}",
  "languageName": "${LANG_NAME}",
  "framework": "${FRAMEWORK}",
  "platforms": ${PLATFORMS_JSON},
  "createdAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date "+%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    
    echo ""
    echo -e "${GREEN}✅ 配置文件已生成: $CONFIG_FILE${NC}"
fi
echo ""

# 步骤3：设置规则文件
echo -e "${GREEN}[步骤 3/4] 设置AI助手规则文件...${NC}"
RULES_DIR="$PROJECT_ROOT/.cursor/rules"

if [ ! -d "$RULES_DIR" ]; then
    mkdir -p "$RULES_DIR"
    echo -e "${GREEN}✅ 创建规则目录: $RULES_DIR${NC}"
fi

RULE_FILE="$RULES_DIR/00-PROJECT_INIT_RULE.mdc"
if [ -f "$RULE_FILE" ]; then
    echo -e "${YELLOW}⚠️  规则文件已存在: $RULE_FILE${NC}"
    read -p "是否覆盖？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}跳过复制规则文件${NC}"
    else
        cp "$SCRIPT_DIR/00-PROJECT_INIT_RULE.mdc" "$RULE_FILE"
        echo -e "${GREEN}✅ 规则文件已复制${NC}"
    fi
else
    cp "$SCRIPT_DIR/00-PROJECT_INIT_RULE.mdc" "$RULE_FILE"
    echo -e "${GREEN}✅ 规则文件已复制: $RULE_FILE${NC}"
fi
echo ""

# 步骤4：创建计划目录
echo -e "${GREEN}[步骤 4/4] 创建计划目录...${NC}"
PLANS_DIR="$PROJECT_ROOT/.cursor/plans"

if [ ! -d "$PLANS_DIR" ]; then
    mkdir -p "$PLANS_DIR"
    echo -e "${GREEN}✅ 创建计划目录: $PLANS_DIR${NC}"
else
    echo -e "${GREEN}✅ 计划目录已存在${NC}"
fi
echo ""

# 验证设置
echo -e "${GREEN}验证设置...${NC}"
echo ""

ERRORS=0

if [ ! -d "$INIT_DIR" ]; then
    echo -e "${RED}❌ 初始化系统目录不存在${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 初始化系统目录存在${NC}"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 配置文件存在${NC}"
fi

if [ ! -f "$RULE_FILE" ]; then
    echo -e "${RED}❌ AI规则文件不存在${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ AI规则文件存在${NC}"
fi

if [ ! -d "$PLANS_DIR" ]; then
    echo -e "${RED}❌ 计划目录不存在${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 计划目录存在${NC}"
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ 初始化设置完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}下一步操作：${NC}"
    echo ""
    echo "1. 🤖 在 Cursor 中告诉 AI 助手："
    echo "   请按照 PROJECT_INIT_PLAN.md 开始项目初始化"
    echo ""
    echo "   或者简单说："
    echo "   开始项目初始化"
    echo ""
    echo "2. 💬 AI 助手会读取配置文件并引导你完成后续步骤"
    echo ""
    echo -e "${YELLOW}提示：${NC}"
    echo "- 配置文件: $CONFIG_FILE"
    echo "- AI 助手会读取此配置文件获取项目信息"
    echo "- 如需修改配置，可直接编辑 JSON 文件"
    echo "- 初始化完成后，可以使用 finish.sh 清理临时文件"
    echo ""
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ❌ 设置验证失败，请检查上述错误${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
