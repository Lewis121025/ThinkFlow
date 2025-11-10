# 构建指南

## 本地 Docker 构建

由于 GitHub Actions 需要计费账户，建议使用本地 Docker 构建。

### 1. 构建镜像

```bash
docker build -t thinkflow:latest .
```

### 2. 验证构建

```bash
# 测试镜像
docker run --rm thinkflow:latest --help

# 运行思维树
docker run --rm -v ${PWD}/.env:/app/.env:ro thinkflow:latest tot --problem "你的问题"
```

### 3. 使用 docker-compose

```bash
# 构建
docker-compose build

# 运行
docker-compose run --rm thinkflow tot --problem "你的问题"
```

## GitHub Actions 说明

GitHub Actions 需要：
- 公共仓库：免费（有限制）
- 私有仓库：需要 GitHub Pro/Team/Enterprise 账户

如果遇到计费问题：
1. 检查 GitHub 账户设置
2. 使用本地 Docker 构建（推荐）
3. 或使用其他 CI/CD 服务（如 GitLab CI, CircleCI 等）

## 替代 CI/CD 方案

### GitLab CI

创建 `.gitlab-ci.yml`:

```yaml
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t thinkflow:latest .
    - docker run --rm thinkflow:latest --help
```

### 本地构建脚本

使用 `build.sh` 或 `build.ps1` 进行本地构建和测试。

