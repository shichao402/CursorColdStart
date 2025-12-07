#!/bin/bash
#
# CursorColdStart 集成测试脚本
# 基于 testProject 验证所有命令功能
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 计数器
PASS=0
FAIL=0

# 路径
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COLDSTART="$PROJECT_ROOT/bin/coldstart"
TEST_DIR="/tmp/coldstart-test-$$"

# 打印函数
header() { echo -e "\n${BLUE}══════════════════════════════════════════════════${NC}\n${BLUE}  $1${NC}\n${BLUE}══════════════════════════════════════════════════${NC}"; }
test_case() { echo -e "${YELLOW}▶ $1${NC}"; }
pass() { echo -e "${GREEN}  ✅ $1${NC}"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}  ❌ $1${NC}"; FAIL=$((FAIL + 1)); }
info() { echo -e "  ℹ️  $1"; }

# 清理
cleanup() {
    if [ $FAIL -eq 0 ]; then
        rm -rf "$TEST_DIR" 2>/dev/null || true
    else
        echo -e "  ℹ️  测试目录保留用于调试: $TEST_DIR"
    fi
}
trap cleanup EXIT

# ============================================================
# 前置检查
# ============================================================
header "前置检查"

# 切换到项目根目录（coldstart 需要在此目录运行以找到 rules_template）
cd "$PROJECT_ROOT"

test_case "检查 coldstart 可执行文件"
if [ -f "$COLDSTART" ]; then
    pass "coldstart 存在"
else
    fail "coldstart 不存在，请先运行 make build"
    exit 1
fi

test_case "检查 rules_template 目录"
if [ -d "$PROJECT_ROOT/rules_template" ]; then
    pass "rules_template 存在"
else
    fail "rules_template 不存在"
    exit 1
fi

mkdir -p "$TEST_DIR"

# ============================================================
# 测试 help/version 命令
# ============================================================
header "测试 help/version 命令"

test_case "coldstart help"
$COLDSTART help | grep -q "CursorColdStart" && pass "help 正常" || fail "help 异常"

test_case "coldstart -h"
$COLDSTART -h | grep -q "使用方式" && pass "-h 正常" || fail "-h 异常"

test_case "coldstart --help"
$COLDSTART --help | grep -q "命令" && pass "--help 正常" || fail "--help 异常"

test_case "coldstart version"
$COLDSTART version | grep -q "version" && pass "version 正常" || fail "version 异常"

test_case "coldstart -v"
$COLDSTART -v | grep -q "version" && pass "-v 正常" || fail "-v 异常"

test_case "coldstart --version"
$COLDSTART --version | grep -q "version" && pass "--version 正常" || fail "--version 异常"

# ============================================================
# 测试 list 命令
# ============================================================
header "测试 list 命令"

test_case "coldstart list"
$COLDSTART list 2>&1 | grep -qE "languages|frameworks|platforms|packs" && pass "list 正常" || fail "list 异常"

test_case "coldstart list languages"
$COLDSTART list languages 2>&1 | grep -qE "go|python|dart|typescript" && pass "list languages 正常" || fail "list languages 异常"

test_case "coldstart list frameworks"
$COLDSTART list frameworks 2>&1 | grep -qE "flutter|react|vue|gin" && pass "list frameworks 正常" || fail "list frameworks 异常"

test_case "coldstart list platforms"
$COLDSTART list platforms 2>&1 | grep -qE "ios|android|web|cli" && pass "list platforms 正常" || fail "list platforms 异常"

test_case "coldstart list packs"
$COLDSTART list packs 2>&1 | grep -qE "logging|documentation|github-actions" && pass "list packs 正常" || fail "list packs 异常"

# ============================================================
# 测试 init 命令 - 首次初始化
# ============================================================
header "测试 init 命令 - 首次初始化"

FIRST_INIT="$TEST_DIR/first-init"
mkdir -p "$FIRST_INIT"

test_case "coldstart init (首次)"
INIT_OUTPUT=$($COLDSTART init "$FIRST_INIT" 2>&1)
if echo "$INIT_OUTPUT" | grep -q "首次初始化"; then
    pass "首次初始化执行"
else
    fail "首次初始化失败"
    echo "$INIT_OUTPUT"
fi

test_case "检查 .cursor-cold-start/config 目录"
[ -d "$FIRST_INIT/.cursor-cold-start/config" ] && pass "config 目录存在" || fail "config 目录不存在"

test_case "检查 project.json"
[ -f "$FIRST_INIT/.cursor-cold-start/config/project.json" ] && pass "project.json 存在" || fail "project.json 不存在"

test_case "检查 technology.json"
[ -f "$FIRST_INIT/.cursor-cold-start/config/technology.json" ] && pass "technology.json 存在" || fail "technology.json 不存在"

test_case "检查 packs.json"
[ -f "$FIRST_INIT/.cursor-cold-start/config/packs.json" ] && pass "packs.json 存在" || fail "packs.json 不存在"

test_case "检查 .cursor/rules 目录"
[ -d "$FIRST_INIT/.cursor/rules" ] && pass "rules 目录存在" || fail "rules 目录不存在"

test_case "检查 00-principles.mdc (核心规则)"
[ -f "$FIRST_INIT/.cursor/rules/00-principles.mdc" ] && pass "00-principles.mdc 存在" || fail "00-principles.mdc 不存在"

# ============================================================
# 测试 init 命令 - 配置后再次初始化
# ============================================================
header "测试 init 命令 - 配置后再次初始化"

SECOND_INIT="$TEST_DIR/second-init"
mkdir -p "$SECOND_INIT/.cursor-cold-start/config"

# 创建配置文件 (模拟 testProject 的配置)
cat > "$SECOND_INIT/.cursor-cold-start/config/project.json" << 'EOF'
{
  "name": "TestProject",
  "description": "测试项目",
  "version": "1.0.0"
}
EOF

cat > "$SECOND_INIT/.cursor-cold-start/config/technology.json" << 'EOF'
{
  "language": "dart",
  "framework": "flutter",
  "platforms": ["android", "ios"]
}
EOF

cat > "$SECOND_INIT/.cursor-cold-start/config/packs.json" << 'EOF'
{
  "logging": {
    "enabled": true,
    "config": {
      "serviceClass": "AppLogger",
      "filePath": "logs/app.log"
    }
  },
  "documentation": {
    "enabled": true
  },
  "version-management": {
    "enabled": true
  },
  "update-module": {
    "enabled": true,
    "config": {
      "moduleName": "UpdateModule",
      "modulePath": "lib/modules/update"
    }
  }
}
EOF

test_case "coldstart init (再次初始化)"
INIT_OUTPUT=$($COLDSTART init "$SECOND_INIT" 2>&1)
if echo "$INIT_OUTPUT" | grep -q "生成规则文件"; then
    pass "再次初始化执行"
else
    fail "再次初始化失败"
    echo "$INIT_OUTPUT"
fi

test_case "检查语言规则 (dart)"
[ -f "$SECOND_INIT/.cursor/rules/10-dart.mdc" ] && pass "10-dart.mdc 存在" || fail "10-dart.mdc 不存在"

test_case "检查框架规则 (flutter)"
[ -f "$SECOND_INIT/.cursor/rules/20-flutter.mdc" ] && pass "20-flutter.mdc 存在" || fail "20-flutter.mdc 不存在"

test_case "检查平台规则 (android)"
[ -f "$SECOND_INIT/.cursor/rules/30-android.mdc" ] && pass "30-android.mdc 存在" || fail "30-android.mdc 不存在"

test_case "检查 pack 规则 (logging)"
[ -f "$SECOND_INIT/.cursor/rules/40-logging.mdc" ] && pass "40-logging.mdc 存在" || fail "40-logging.mdc 不存在"

test_case "检查 pack 规则 (documentation)"
[ -f "$SECOND_INIT/.cursor/rules/46-documentation.mdc" ] && pass "46-documentation.mdc 存在" || fail "46-documentation.mdc 不存在"

test_case "检查 pack 规则 (version-management)"
[ -f "$SECOND_INIT/.cursor/rules/44-version-management.mdc" ] && pass "44-version-management.mdc 存在" || fail "44-version-management.mdc 不存在"

test_case "检查 pack 规则 (update-module)"
[ -f "$SECOND_INIT/.cursor/rules/51-update-module.mdc" ] && pass "51-update-module.mdc 存在" || fail "51-update-module.mdc 不存在"

# ============================================================
# 测试不同技术栈组合
# ============================================================
header "测试不同技术栈组合"

# 注意：目前只支持 dart + flutter + android 技术栈
# 其他技术栈模板尚未实现

# Dart + Flutter + iOS (测试不同平台)
DART_IOS="$TEST_DIR/dart-ios-project"
mkdir -p "$DART_IOS/.cursor-cold-start/config"

cat > "$DART_IOS/.cursor-cold-start/config/project.json" << 'EOF'
{"name": "DartIOSProject", "description": "Dart iOS 项目", "version": "1.0.0"}
EOF

cat > "$DART_IOS/.cursor-cold-start/config/technology.json" << 'EOF'
{"language": "dart", "framework": "flutter", "platforms": ["ios"]}
EOF

cat > "$DART_IOS/.cursor-cold-start/config/packs.json" << 'EOF'
{"logging": {"enabled": false}}
EOF

test_case "Dart + Flutter + iOS 项目初始化"
$COLDSTART init "$DART_IOS" >/dev/null 2>&1 || true
[ -f "$DART_IOS/.cursor/rules/10-dart.mdc" ] && pass "10-dart.mdc 存在" || fail "10-dart.mdc 不存在"
[ -f "$DART_IOS/.cursor/rules/20-flutter.mdc" ] && pass "20-flutter.mdc 存在" || fail "20-flutter.mdc 不存在"

# 仅 Dart (无框架)
DART_ONLY="$TEST_DIR/dart-only-project"
mkdir -p "$DART_ONLY/.cursor-cold-start/config"

cat > "$DART_ONLY/.cursor-cold-start/config/project.json" << 'EOF'
{"name": "DartOnlyProject", "description": "纯 Dart 项目", "version": "1.0.0"}
EOF

cat > "$DART_ONLY/.cursor-cold-start/config/technology.json" << 'EOF'
{"language": "dart", "framework": "", "platforms": []}
EOF

cat > "$DART_ONLY/.cursor-cold-start/config/packs.json" << 'EOF'
{"logging": {"enabled": false}}
EOF

test_case "纯 Dart 项目初始化 (无框架)"
$COLDSTART init "$DART_ONLY" >/dev/null 2>&1 || true
[ -f "$DART_ONLY/.cursor/rules/10-dart.mdc" ] && pass "10-dart.mdc 存在" || fail "10-dart.mdc 不存在"
[ ! -f "$DART_ONLY/.cursor/rules/20-flutter.mdc" ] && pass "无 flutter 规则 (正确)" || fail "不应有 flutter 规则"

# ============================================================
# 测试错误处理
# ============================================================
header "测试错误处理"

test_case "coldstart init (无参数)"
if $COLDSTART init 2>&1 | grep -q "缺少目标目录"; then
    pass "正确提示缺少目标目录"
else
    fail "未提示缺少目标目录"
fi

test_case "coldstart unknown-command"
if $COLDSTART unknown-command 2>&1 | grep -q "未知命令"; then
    pass "正确提示未知命令"
else
    fail "未提示未知命令"
fi

# ============================================================
# 对比 testProject 输出
# ============================================================
header "对比 testProject 预期输出"

REFERENCE="$PROJECT_ROOT/testProject"

if [ -d "$REFERENCE/.cursor/rules" ]; then
    test_case "对比规则文件数量"
    REF_COUNT=$(ls -1 "$REFERENCE/.cursor/rules"/*.mdc 2>/dev/null | wc -l)
    GEN_COUNT=$(ls -1 "$SECOND_INIT/.cursor/rules"/*.mdc 2>/dev/null | wc -l)
    if [ "$REF_COUNT" -eq "$GEN_COUNT" ]; then
        pass "规则文件数量一致 ($REF_COUNT 个)"
    else
        fail "规则文件数量不一致 (预期: $REF_COUNT, 实际: $GEN_COUNT)"
    fi
    
    test_case "对比规则文件列表"
    REF_FILES=$(ls -1 "$REFERENCE/.cursor/rules"/*.mdc | xargs -n1 basename | sort)
    GEN_FILES=$(ls -1 "$SECOND_INIT/.cursor/rules"/*.mdc | xargs -n1 basename | sort)
    if [ "$REF_FILES" = "$GEN_FILES" ]; then
        pass "规则文件列表一致"
    else
        fail "规则文件列表不一致"
        info "预期: $REF_FILES"
        info "实际: $GEN_FILES"
    fi
else
    info "跳过 testProject 对比 (目录不存在)"
fi

# ============================================================
# 测试结果汇总
# ============================================================
header "测试结果汇总"

TOTAL=$((PASS + FAIL))
echo -e "总计: ${TOTAL} 个测试"
echo -e "${GREEN}通过: ${PASS} 个${NC}"
echo -e "${RED}失败: ${FAIL} 个${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "\n${RED}💥 有 ${FAIL} 个测试失败${NC}"
    exit 1
fi
