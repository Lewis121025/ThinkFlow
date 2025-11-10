# ThinkFlow - GitHub 部署脚本 (PowerShell)

Write-Host "🚀 ThinkFlow - GitHub 部署脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否初始化
if (-not (Test-Path ".git")) {
    Write-Host "📦 初始化 Git 仓库..." -ForegroundColor Yellow
    git init
}

# 添加所有文件
Write-Host "📝 添加文件到 Git..." -ForegroundColor Yellow
git add .

# 提交
Write-Host "💾 提交更改..." -ForegroundColor Yellow
$commitMsg = Read-Host "请输入提交信息 (默认: Initial commit)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Initial commit"
}
git commit -m $commitMsg

# 检查远程仓库
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    Write-Host "🔗 添加远程仓库..." -ForegroundColor Yellow
    git remote add origin https://github.com/Lewis121025/ThinkFlow.git
}

# 推送
Write-Host "📤 推送到 GitHub..." -ForegroundColor Yellow
$branch = Read-Host "推送到哪个分支? (默认: main)"
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
}
git push -u origin $branch

Write-Host ""
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "🌐 查看仓库: https://github.com/Lewis121025/ThinkFlow" -ForegroundColor Cyan

