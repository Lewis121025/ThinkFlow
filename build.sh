#!/bin/bash
# ThinkFlow - 本地构建脚本 (Bash)

echo "🚀 ThinkFlow - 本地构建脚本"
echo "================================"
echo ""

# 检查 Docker
echo "📦 检查 Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✓ Docker 已安装: $DOCKER_VERSION"
else
    echo "✗ Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker 是否运行
echo "🔍 检查 Docker 服务状态..."
if docker ps &> /dev/null; then
    echo "✓ Docker 服务正在运行"
else
    echo "✗ Docker 服务未运行"
    echo "请启动 Docker Desktop 后重试"
    exit 1
fi

# 构建镜像
echo ""
echo "🔨 开始构建 Docker 镜像..."
echo "这可能需要几分钟时间..."

if docker build -t thinkflow:latest .; then
    echo ""
    echo "✅ 构建成功！"
    echo ""
    echo "📝 使用示例:"
    echo "  docker run --rm thinkflow:latest --help"
    echo "  docker run --rm -v \$(pwd)/.env:/app/.env:ro thinkflow:latest tot --problem \"你的问题\""
else
    echo "✗ 构建失败"
    exit 1
fi

echo ""
echo "🎉 完成！"

