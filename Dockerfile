# ThinkFlow - Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目文件（排除不需要的文件）
COPY src/ ./src/
COPY main.py .
COPY requirements.txt .

# 验证关键文件
RUN test -f main.py && test -d src && echo "✓ Files copied successfully"

# 创建非root用户（可选，提高安全性）
RUN useradd -m -u 1000 thinkflow && \
    chown -R thinkflow:thinkflow /app

# 切换到非root用户
USER thinkflow

# 验证 Python 环境
RUN python --version && python -c "import sys; print(f'Python path: {sys.executable}')"

# 暴露端口（如果需要）
# EXPOSE 8000

# 设置入口点
ENTRYPOINT ["python", "main.py"]

# 默认命令
CMD ["--help"]

