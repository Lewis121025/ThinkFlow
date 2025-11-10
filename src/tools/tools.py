# 文件名: tools.py
import operator
import re
import json
import os
from openai import OpenAI
from googleapiclient.discovery import build
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.pop("LANGCHAIN_API_KEY", None)
os.environ.pop("LANGSMITH_ENDPOINT", None)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# --- "图书馆"会员卡  ---
Custom_Google_Search_API = os.environ.get("Custom_Google_Search_API")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")

DEEP_THINK_SYSTEM_PROMPT = """
你是一个纯粹的、高度集中的逻辑推理器。你模拟xAI的"Deep Think" API。
你的任务是接收一个复杂的逻辑问题、谜题或战略分析请求，并提供一个深入的、一步一步的、链式思考(Chain-of-Thought)的回答。
你绝不能使用任何外部工具（如搜索）。你的所有回答都必须基于你自己的内部知识和推理能力。

首先，陈述你的思考过程，然后给出最终答案。
"""


@tool
def deep_think(query: str) -> str:
    """
    一个专业的逻辑推理工具，模拟Grok 5的"Deep Think"链式推理API。
    当你需要解决一个复杂的逻辑谜题、伦理困境、战略问题，
    或者任何不需要实时搜索、但需要深度思考才能回答的问题时，
    你必须使用此工具。
    """
    print("--- 正在调用 'Deep Thinker' 工具... ---")
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",
            messages=[
                {"role": "system", "content": DEEP_THINK_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用Deep Think API时出错: {e}"


@tool
def simple_calculator(expression: str) -> str:
    """
    一个安全的计算器。只能用于简单的二元运算，例如 '10 + 5' 或 '20 * 3'。
    (A safe calculator. Use for simple math operations like '10 + 5' or '20 * 3'.)
    """
    print(f"--- [Tool]: 正在调用 'simple_calculator'，表达式: {expression} ---")

    ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }
    pattern = r"^\s*([\d\.]+)\s*([+\-*/])\s*([\d\.]+)\s*$"
    match = re.match(pattern, expression)
    if not match:
        return f"Error: 表达式格式无效。请输入如 '10 + 5' 的简单运算。"
    try:
        num1_str, op_str, num2_str = match.groups()
        num1 = float(num1_str)
        num2 = float(num2_str)
        op_func = ops[op_str]
        result = op_func(num1, num2)
        return str(result)
    except ZeroDivisionError:
        return "Error: 不能除以零。"
    except Exception as e:
        return f"Error: 计算时出错: {e}"


@tool
def real_search(query: str, num_results: int = 3) -> str:
    """
    一个实时互联网搜索引擎。
    用于查询当前天气、体育赛事结果、新闻、或你不认识的人或事物的最新信息。
    (A real-time internet search engine. Use for current events like weather, sports, news, etc.)
    """
    print(f"--- [Tool]: 正在调用 'real_search'，查询: {query} ---")

    if not Custom_Google_Search_API or not GOOGLE_CSE_ID:
        return "Error: Google Search API key or CSE ID not configured."
    try:
        service = build("customsearch", "v1", developerKey=Custom_Google_Search_API)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()
        snippets = []
        if "items" in res:
            for i, item in enumerate(res["items"]):
                snippets.append(f"[{i + 1}] {item['title']}: {item['snippet']}")
        if not snippets:
            return "No relevant search results found."
        return "\n".join(snippets)
    except Exception as e:
        return f"Error during Google Search: {e}"


@tool
def query_local_knowledge(question: str) -> str:
    """
    查询本地知识库（RAG）。
    用于问项目内部信息、秘密代号、规则、文档内容等。
    """
    print(f"--- [Tool]: 正在调用 'query_local_knowledge'，问题: {question} ---")
    try:
        if not os.path.exists("faiss_index"):
            return "Error: 本地知识库未构建！请先运行 build_rag_hf.py 重建索引（见下方脚本）。"

        embed_model_name = os.environ.get("EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
        embeddings = HuggingFaceEmbeddings(
            model_name=embed_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        db = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True
        )

        docs = db.similarity_search(question, k=2)
        if not docs:
            return "本地知识库中未找到相关信息。"
        context = "\n\n".join([doc.page_content.strip() for doc in docs])
        return f"【本地知识库】\n{context}"

    except Exception as e:
        return f"Error: 查询知识库失败: {e}"


def ask_about_image(image_url: str, question: str) -> str:
    """
    向多模态模型发送一张图片和一个问题。
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用API时出错: {e}"


@tool
def image_analyzer(question: str, image_url: str) -> str:
    """
    一个视觉分析工具。当用户的提问中"同时"包含"问题"和"图片URL"时，
    你必须调用此工具来分析图片内容并回答问题。
    'question' 参数是用户关于图片的问题。
    'image_url' 参数是图片在互联网上的链接(URL)地址。
    """
    print(f"--- [工具被调用：image_analyzer] ---")
    print(f"   问题: {question}")
    print(f"   URL: {image_url}")
    print(f"---------------------------------")
    return ask_about_image(image_url, question)

