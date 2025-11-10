# ThinkFlow

基于Tree of Thought思维树的多模态智能代理框架，支持复杂问题推理、多模态处理和任务规划。

## 📁 项目结构

```
AI_Agent_Learning/
├── src/                          # 源代码
│   ├── tot/                      # 思维树模块
│   │   ├── langgraph_tot.py      # LangGraph版本
│   │   └── tot_orchestrator.py   # 协调器版本
│   ├── agent/                    # Agent模块
│   │   ├── multi_modal_agent.py  # 多模态代理
│   │   └── planner_agent.py      # 规划代理
│   ├── tools/                    # 工具集
│   │   └── tools.py              # 搜索、计算、RAG、图像分析等
│   └── prompts/                  # 提示词
│       └── tot_prompts.py
├── main.py                       # 统一入口点
└── requirements.txt
```

## 🚀 快速开始

### 方式1: Docker（推荐）

#### 前置要求

确保 Docker Desktop 已安装并正在运行。

**Windows:**
- 启动 Docker Desktop 应用程序
- 等待系统托盘图标显示 Docker 已运行

#### 1. 构建镜像

**使用构建脚本（推荐）:**

**Windows (PowerShell):**
```powershell
.\build.ps1
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

**或手动构建:**
```bash
docker build -t thinkflow:latest .
```

**或使用 docker-compose:**
```bash
docker-compose build
```

#### 2. 配置环境变量

创建 `.env` 文件（见下方配置说明）

#### 3. 运行

```bash
# 使用 Docker
docker run --rm -v $(pwd)/.env:/app/.env:ro thinkflow:latest tot --problem "你的问题"

# 使用 docker-compose
docker-compose run --rm thinkflow tot --problem "你的问题"
```

### 方式2: 本地安装

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

创建 `.env` 文件：

```env
# 必需
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# 可选（用于搜索功能）
Custom_Google_Search_API=your_google_search_api_key
GOOGLE_CSE_ID=your_cse_id

# 可选（用于RAG）
EMBED_MODEL=BAAI/bge-small-zh-v1.5
```

#### 3. 运行

```bash
# 思维树 (LangGraph)
python main.py tot --problem "你的问题"

# 思维树 (协调器)
python main.py tot-orchestrator --problem "你的问题" --k 6

# 多模态Agent
python main.py multi-modal --input "问题" --image-url "图片URL"

# 规划Agent
python main.py planner --problem "你的任务"
```

#### 直接运行模块

```bash
python -m src.tot.langgraph_tot
python -m src.agent.multi_modal_agent
```

## 📚 功能模块

### 1. Tree of Thought (思维树)

通过生成→评估→选择→优化的流程解决复杂问题。

**两种实现：**
- `langgraph_tot.py` - LangGraph工作流（支持自动重试）
- `tot_orchestrator.py` - 协调器模式（简化版）

### 2. Multi-Modal Agent (多模态代理)

处理文本和图像，支持对话记忆。

### 3. Planner Agent (规划代理)

将复杂任务自动分解为可执行的子任务。

### 4. Tools (工具集)

- `deep_think` - 深度思考推理
- `simple_calculator` - 计算器
- `real_search` - 网络搜索（需Google API）
- `query_local_knowledge` - 本地知识库查询（RAG）
- `image_analyzer` - 图像分析

## 💻 代码示例

### Python调用

```python
# 思维树
from src.tot import run_tot
result = run_tot("你的问题")

# 多模态Agent
from src.agent import run_multi_modal_agent
response = run_multi_modal_agent("问题", "图片URL")

# 规划Agent
from src.agent import run_planner_agent
run_planner_agent("你的任务")
```

## 🐳 Docker 使用

详细的 Docker 使用说明请查看 [DOCKER.md](DOCKER.md)

**注意**: GitHub Actions 需要计费账户。如果遇到计费问题，请使用本地 Docker 构建（见 [DOCKER.md](DOCKER.md)）

## ⚠️ 常见问题

**Q: 导入错误 `ModuleNotFoundError: No module named 'src'`**  
A: 确保在项目根目录运行，或使用 `python -m` 方式。

**Q: API密钥错误**  
A: 检查 `.env` 文件是否存在且配置正确。

**Q: 模型不可用**  
A: 修改代码中的模型名称，使用可用的模型。

**Q: Docker 容器无法访问 .env 文件**  
A: 确保使用 `-v $(pwd)/.env:/app/.env:ro` 挂载环境变量文件。

---

## 📦 部署到 GitHub

### 方式1: 使用部署脚本（推荐）

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 方式2: 手动部署

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Lewis121025/ThinkFlow.git
git push -u origin main
```

---

**祝学习愉快！** 🎉

Created with ❤️ by Lewis
