# CursorToolset 包开发指南

本指南帮助你开发符合 CursorToolset 规范的工具集包。

---

## 目录结构

```
my-toolset/
├── toolset.json          # 包配置文件（必需）
├── .cursortoolset/       # AI 规则目录
│   └── rules/            # 规则文件
├── .github/
│   └── workflows/
│       └── release.yml   # 发布工作流（推荐）
├── .gitignore
└── README.md
```

---

## 注册表与发布规范

### 注册表格式

包在 CursorToolset 注册表中只需提供仓库地址：

```json
{
  "name": "my-toolset",
  "repository": "https://github.com/USERNAME/my-toolset"
}
```

管理工具会自动组装 URL 获取包信息：
- 最新版本：`https://github.com/{repo}/releases/latest/download/package.json`
- 特定版本：`https://github.com/{repo}/releases/download/v1.0.0/package.json`

### 发布产物结构

每次 Release 需要上传两个文件：

```
Release v1.0.0/
├── package.json                  # 包配置（从 toolset.json 生成）
├── my-toolset-1.0.0.tar.gz       # 打包产物
```

**重要**：`package.json` 中的 `dist.tarball` 使用**相对路径**：

```json
{
  "dist": {
    "tarball": "my-toolset-1.0.0.tar.gz",
    "sha256": "..."
  }
}
```

管理工具会根据 `package.json` 的 URL 自动解析 tarball 的完整下载地址。

---

## package.json 规范

这是发布时上传的包配置文件，定义包的元数据和下载信息。

```json
{
  "name": "my-toolset",
  "displayName": "My Toolset",
  "version": "1.0.0",
  "description": "包的简短描述",
  "author": "你的名字",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "repository": {
    "type": "git",
    "url": "https://github.com/USERNAME/my-toolset.git"
  },
  "dist": {
    "tarball": "my-toolset-1.0.0.tar.gz",
    "sha256": "SHA256校验和",
    "size": 12345
  },
  "cursortoolset": {
    "minVersion": "1.0.0"
  }
}
```

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| name | ✅ | 包名，小写字母、数字、连字符 |
| version | ✅ | 语义化版本号 (MAJOR.MINOR.PATCH) |
| displayName | ❌ | 显示名称 |
| description | ❌ | 包描述 |
| dist.tarball | ✅ | 下载文件名（相对路径） |
| dist.sha256 | ✅ | SHA256 校验和 |
| dist.size | ❌ | 文件大小（字节） |
| bin | ❌ | 可执行文件配置（见下文） |

---

## 可执行文件 (bin) 配置

如果你的包包含可执行文件（如 Go/Rust 编译的二进制），需要配置 `bin` 字段。

### 支持的平台标识

| 平台 | 标识 |
|------|------|
| macOS Intel | `darwin-amd64` |
| macOS Apple Silicon | `darwin-arm64` |
| Linux x64 | `linux-amd64` |
| Linux ARM64 | `linux-arm64` |
| Windows x64 | `windows-amd64` |
| Windows ARM64 | `windows-arm64` |

### 配置格式

```json
{
  "bin": {
    "命令名": {
      "平台标识": "tarball内的相对路径"
    }
  }
}
```

### 完整示例

```json
{
  "name": "github-action-toolset",
  "version": "1.0.5",
  "bin": {
    "gh-action-debug": {
      "darwin-amd64": "core/tools/go/dist/gh-action-debug-darwin-amd64",
      "darwin-arm64": "core/tools/go/dist/gh-action-debug-darwin-arm64",
      "linux-amd64": "core/tools/go/dist/gh-action-debug-linux-amd64",
      "linux-arm64": "core/tools/go/dist/gh-action-debug-linux-arm64",
      "windows-amd64": "core/tools/go/dist/gh-action-debug-windows-amd64.exe",
      "windows-arm64": "core/tools/go/dist/gh-action-debug-windows-arm64.exe"
    }
  },
  "dist": {
    "tarball": "github-action-toolset-1.0.5.tar.gz",
    "sha256": "8f107e5d303e9e8645c6714d73483b4d87317c10e6747523dbf02b8d035d103b",
    "size": 30461952
  }
}
```

### 目录结构建议

```
my-toolset/
├── core/
│   └── tools/
│       └── go/
│           ├── cmd/
│           │   └── my-command/
│           │       └── main.go
│           └── dist/                    # 构建产物目录
│               ├── my-command-darwin-amd64
│               ├── my-command-darwin-arm64
│               ├── my-command-linux-amd64
│               ├── my-command-linux-arm64
│               ├── my-command-windows-amd64.exe
│               └── my-command-windows-arm64.exe
├── toolset.json
└── .github/
    └── workflows/
        └── release.yml
```

### 构建配置（可选）

在 `toolset.json` 中添加 `build` 字段，供工具自动构建：

```json
{
  "build": {
    "type": "go",
    "entry": "core/tools/go/cmd/my-command",
    "output": "core/tools/go/dist",
    "platforms": [
      "darwin-amd64",
      "darwin-arm64", 
      "linux-amd64",
      "linux-arm64",
      "windows-amd64",
      "windows-arm64"
    ]
  }
}
```

---

## 版本号规范

遵循语义化版本 (SemVer)：

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

示例：`1.0.0`, `1.2.3`, `2.0.0`

---

## 发布流程

### 方式一：使用 GitHub Actions（推荐）

#### 1. 添加 Release Workflow

在 `.github/workflows/release.yml` 创建发布工作流：

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    
    steps:
      - uses: actions/checkout@v4
      
      # 如果有 Go 构建需求
      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'
      
      # 构建多平台二进制（如果需要）
      - name: Build binaries
        run: |
          cd core/tools/go
          mkdir -p dist
          GOOS=darwin GOARCH=amd64 go build -o dist/my-command-darwin-amd64 ./cmd/my-command
          GOOS=darwin GOARCH=arm64 go build -o dist/my-command-darwin-arm64 ./cmd/my-command
          GOOS=linux GOARCH=amd64 go build -o dist/my-command-linux-amd64 ./cmd/my-command
          GOOS=linux GOARCH=arm64 go build -o dist/my-command-linux-arm64 ./cmd/my-command
          GOOS=windows GOARCH=amd64 go build -o dist/my-command-windows-amd64.exe ./cmd/my-command
          GOOS=windows GOARCH=arm64 go build -o dist/my-command-windows-arm64.exe ./cmd/my-command
      
      # 获取版本号
      - name: Get version
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
      
      # 打包
      - name: Create tarball
        run: |
          mkdir -p /tmp/release
          tar -czvf /tmp/release/${{ github.event.repository.name }}-${{ steps.version.outputs.VERSION }}.tar.gz \
            --exclude='.git' \
            --exclude='.github' \
            --exclude='*.tar.gz' \
            --exclude='*.go' \
            --exclude='go.mod' \
            --exclude='go.sum' \
            .
      
      # 计算 SHA256 并生成 package.json
      - name: Generate package.json
        run: |
          TARBALL="${{ github.event.repository.name }}-${{ steps.version.outputs.VERSION }}.tar.gz"
          SHA256=$(shasum -a 256 /tmp/release/$TARBALL | cut -d' ' -f1)
          SIZE=$(stat -f%z /tmp/release/$TARBALL 2>/dev/null || stat -c%s /tmp/release/$TARBALL)
          
          # 从 toolset.json 生成 package.json，更新 dist 字段
          jq --arg tarball "$TARBALL" \
             --arg sha256 "$SHA256" \
             --arg size "$SIZE" \
             '.dist.tarball = $tarball | .dist.sha256 = $sha256 | .dist.size = ($size | tonumber)' \
             toolset.json > /tmp/release/package.json
      
      # 创建 Release
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            /tmp/release/package.json
            /tmp/release/${{ github.event.repository.name }}-${{ steps.version.outputs.VERSION }}.tar.gz
          generate_release_notes: true
```

#### 2. 发布新版本

```bash
# 更新 toolset.json 中的版本号
# 提交更改
git add .
git commit -m "chore: release v1.0.0"

# 创建并推送 tag
git tag v1.0.0
git push origin main --tags
```

GitHub Actions 会自动：
1. 构建二进制文件（如果配置了）
2. 打包 tarball
3. 计算 SHA256
4. 生成 package.json
5. 创建 Release 并上传文件

### 方式二：手动发布

#### 1. 更新版本号

编辑 `toolset.json`，更新 `version` 字段。

#### 2. 构建（如果有 bin）

```bash
# Go 项目示例
cd core/tools/go
mkdir -p dist
GOOS=darwin GOARCH=amd64 go build -o dist/my-command-darwin-amd64 ./cmd/my-command
GOOS=darwin GOARCH=arm64 go build -o dist/my-command-darwin-arm64 ./cmd/my-command
# ... 其他平台
```

#### 3. 打包

```bash
tar -czvf my-toolset-1.0.0.tar.gz \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='*.tar.gz' \
  --exclude='*.go' \
  --exclude='go.mod' \
  --exclude='go.sum' \
  .
```

#### 4. 计算 SHA256

```bash
shasum -a 256 my-toolset-1.0.0.tar.gz
```

#### 5. 生成 package.json

复制 `toolset.json` 为 `package.json`，更新 `dist` 字段：

```json
{
  "dist": {
    "tarball": "my-toolset-1.0.0.tar.gz",
    "sha256": "计算得到的SHA256",
    "size": 文件大小
  }
}
```

#### 6. 创建 GitHub Release

1. 在 GitHub 仓库创建 Release
2. Tag 选择 `v1.0.0`
3. 上传 `package.json` 和 `my-toolset-1.0.0.tar.gz`
4. 发布

---

## 本地验证（dry-run）

发布前可以本地验证打包内容：

```bash
# 预览发布内容（不实际发布）
cursortoolset release --dry-run

# 输出示例：
# ✓ 版本: 1.0.0
# ✓ 将包含的文件:
#   - toolset.json
#   - rules/
#   - core/tools/go/dist/
# ✗ 将排除的文件:
#   - .git/
#   - *.go
#   - go.mod
# ✓ bin 文件检查:
#   - gh-action-debug-darwin-arm64 ✓
#   - gh-action-debug-linux-amd64 ✓
```

---

## AI 规则编写

在 `.cursortoolset/rules/` 目录下创建 `.md` 文件作为 AI 规则。

### 规则文件示例

```markdown
# 项目开发规范

## 代码风格
- 使用 4 空格缩进
- 函数命名使用驼峰式

## 提交规范
- feat: 新功能
- fix: 修复
- docs: 文档
```

### 最佳实践

1. **清晰明确** - 规则应该具体、可执行
2. **分类组织** - 按主题拆分多个规则文件
3. **保持更新** - 随项目演进更新规则

---

## 常用命令

```bash
# 初始化新包
cursortoolset init my-toolset

# 打包
cursortoolset pack

# 本地发布预览
cursortoolset release --dry-run

# 本地安装测试
cursortoolset install ./my-toolset
```

---

## 常见问题

### Q: tarball 打包时出现 "file changed as we read it"

**原因**：tar 输出在当前目录，打包时包含了自己。

**解决**：输出到 `/tmp/release/` 或其他目录。

### Q: 排除规则把构建产物也排除了

**原因**：使用了 `--exclude='core/tools'` 这样的目录排除。

**解决**：精确排除源码文件：
```bash
--exclude='*.go' \
--exclude='go.mod' \
--exclude='go.sum'
```

### Q: 安装后 bin 命令找不到

**检查**：
1. `bin` 配置的路径是否正确
2. 平台标识是否匹配当前系统
3. 文件是否有执行权限

---

## 参考资源

- [CursorToolset 仓库](https://github.com/shichao402/CursorToolset)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [GitHub Releases 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)
