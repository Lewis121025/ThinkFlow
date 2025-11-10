#!/bin/bash
# ThinkFlow - GitHub 部署脚本

echo "🚀 ThinkFlow - GitHub 部署脚本"
echo "================================"
echo ""

# 检查 Git 是否初始化
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
fi

# 添加所有文件
echo "📝 添加文件到 Git..."
git add .

# 提交
echo "💾 提交更改..."
read -p "请输入提交信息 (默认: Initial commit): " commit_msg
commit_msg=${commit_msg:-"Initial commit"}
git commit -m "$commit_msg"

# 检查远程仓库
if ! git remote | grep -q "origin"; then
    echo "🔗 添加远程仓库..."
    git remote add origin https://github.com/Lewis121025/ThinkFlow.git
fi

# 推送
echo "📤 推送到 GitHub..."
read -p "推送到哪个分支? (默认: main): " branch
branch=${branch:-main}
git push -u origin $branch

echo ""
echo "✅ 部署完成！"
echo "🌐 查看仓库: https://github.com/Lewis121025/ThinkFlow"

