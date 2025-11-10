# Docker 使用指南

## 本地 Docker 构建

由于 GitHub Actions 需要计费账户，建议使用本地 Docker 构建。

### 使用构建脚本（推荐）

**Windows (PowerShell):**
```powershell
.\build.ps1
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

### 手动构建

```bash
# 基本构建
docker build -t thinkflow:latest .

# 使用 docker-compose
docker-compose build
```

## 运行容器

### 基本运行

```bash
# 显示帮助
docker run --rm thinkflow:latest --help

# 运行思维树
docker run --rm -v $(pwd)/.env:/app/.env:ro thinkflow:latest tot --problem "你的问题"

# 运行多模态Agent
docker run --rm -v $(pwd)/.env:/app/.env:ro thinkflow:latest multi-modal --input "问题" --image-url "图片URL"
```

### 使用 docker-compose

```bash
# 显示帮助
docker-compose run --rm thinkflow --help

# 运行思维树
docker-compose run --rm thinkflow tot --problem "你的问题"

# 运行多模态Agent
docker-compose run --rm thinkflow multi-modal --input "问题" --image-url "图片URL"

# 运行规划Agent
docker-compose run --rm thinkflow planner --problem "你的任务"
```

## 环境变量

确保 `.env` 文件存在并包含必要的配置：

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

## 挂载卷

如果需要使用本地知识库（RAG），可以挂载 `faiss_index` 目录：

```bash
docker run --rm \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/faiss_index:/app/faiss_index:ro \
  thinkflow:latest tot --problem "你的问题"
```

## 交互式使用

```bash
# 进入容器
docker run -it --rm thinkflow:latest /bin/bash

# 或使用 docker-compose
docker-compose run --rm thinkflow /bin/bash
```

## GitHub Actions 说明

GitHub Actions 需要：
- 公共仓库：免费（有限制）
- 私有仓库：需要 GitHub Pro/Team/Enterprise 账户

如果遇到计费问题：
1. 检查 GitHub 账户设置
2. 使用本地 Docker 构建（推荐）
3. 或使用其他 CI/CD 服务（如 GitLab CI, CircleCI 等）

