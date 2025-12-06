.PHONY: build clean install test run

# 项目信息
BINARY_NAME=coldstart
CMD_PATH=./cmd/coldstart
BUILD_DIR=./bin
VERSION?=1.0.0
BUILD_TIME=$(shell date +%Y-%m-%dT%H:%M:%S)
GIT_COMMIT=$(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# 构建标志
LDFLAGS=-ldflags "-X main.version=$(VERSION) -X 'main.buildTime=$(BUILD_TIME)' -X main.gitCommit=$(GIT_COMMIT)"

# 默认目标
all: build

# 构建
build:
	@echo "构建 $(BINARY_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) $(CMD_PATH)
	@echo "✅ 构建完成: $(BUILD_DIR)/$(BINARY_NAME)"

# 构建所有平台
build-all: build-darwin build-linux build-windows

build-darwin:
	@echo "构建 macOS (amd64)..."
	@GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 $(CMD_PATH)
	@echo "构建 macOS (arm64)..."
	@GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64 $(CMD_PATH)

build-linux:
	@echo "构建 Linux (amd64)..."
	@GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 $(CMD_PATH)
	@echo "构建 Linux (arm64)..."
	@GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-arm64 $(CMD_PATH)

build-windows:
	@echo "构建 Windows (amd64)..."
	@GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-windows-amd64.exe $(CMD_PATH)
	@echo "构建 Windows (arm64)..."
	@GOOS=windows GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-windows-arm64.exe $(CMD_PATH)

# 安装到本地
install: build
	@echo "安装 $(BINARY_NAME)..."
	@cp $(BUILD_DIR)/$(BINARY_NAME) /usr/local/bin/$(BINARY_NAME) || \
	 cp $(BUILD_DIR)/$(BINARY_NAME) ~/bin/$(BINARY_NAME) || \
	 echo "请手动将 $(BUILD_DIR)/$(BINARY_NAME) 添加到 PATH"
	@echo "✅ 安装完成"

# 运行
run:
	@go run $(CMD_PATH) $(ARGS)

# 测试
test:
	@echo "运行测试..."
	@go test -v ./...

# 清理
clean:
	@echo "清理构建文件..."
	@rm -rf $(BUILD_DIR)
	@go clean
	@echo "✅ 清理完成"

# 格式化代码
fmt:
	@echo "格式化代码..."
	@go fmt ./...
	@echo "✅ 格式化完成"

# 检查代码
vet:
	@echo "检查代码..."
	@go vet ./...
	@echo "✅ 检查完成"

# 代码检查（包含格式化、vet、测试）
check: fmt vet test

# 帮助信息
help:
	@echo "可用命令:"
	@echo "  make build        - 构建当前平台"
	@echo "  make build-all    - 构建所有平台"
	@echo "  make install      - 安装到本地"
	@echo "  make run          - 运行程序 (使用 ARGS='...' 传递参数)"
	@echo "  make test         - 运行测试"
	@echo "  make clean        - 清理构建文件"
	@echo "  make fmt          - 格式化代码"
	@echo "  make vet          - 检查代码"
	@echo "  make check        - 运行所有检查（fmt + vet + test）"
	@echo "  make help         - 显示此帮助信息"

