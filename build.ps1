# ThinkFlow - 本地构建脚本 (PowerShell)

Write-Host "🚀 ThinkFlow - 本地构建脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker
Write-Host "📦 检查 Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker 未安装或未运行" -ForegroundColor Red
    Write-Host "请先启动 Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# 检查 Docker 是否运行
Write-Host "🔍 检查 Docker 服务状态..." -ForegroundColor Yellow
try {
    docker ps 2>&1 | Out-Null
    Write-Host "✓ Docker 服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker 服务未运行" -ForegroundColor Red
    Write-Host "请启动 Docker Desktop 后重试" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "启动方法:" -ForegroundColor Cyan
    Write-Host "1. 打开 Docker Desktop 应用程序" -ForegroundColor White
    Write-Host "2. 等待 Docker 完全启动（系统托盘图标不再闪烁）" -ForegroundColor White
    Write-Host "3. 重新运行此脚本" -ForegroundColor White
    exit 1
}

# 构建镜像
Write-Host ""
Write-Host "🔨 开始构建 Docker 镜像..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间..." -ForegroundColor Gray

try {
    docker build -t thinkflow:latest .
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 构建成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 使用示例:" -ForegroundColor Cyan
        Write-Host "  docker run --rm thinkflow:latest --help" -ForegroundColor White
        Write-Host "  docker run --rm -v `$PWD/.env:/app/.env:ro thinkflow:latest tot --problem `"你的问题`"" -ForegroundColor White
    } else {
        Write-Host "✗ 构建失败" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 构建过程中出错: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 完成！" -ForegroundColor Green

