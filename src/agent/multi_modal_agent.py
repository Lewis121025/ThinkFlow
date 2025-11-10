import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from src.tools import image_analyzer

load_dotenv()


def create_multi_modal_agent():
    """
    创建多模态Agent
    """
    print(">>> 正在创建视觉Agent...")

    tools = [image_analyzer]

    llm = ChatOpenAI(
        model="meta-llama/llama-4-maverick:free",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base=os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个乐于助人的、强大的AI助手。你能调用工具来分析图片。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "图片URL: {image_url}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input"
    )

    agent = create_openai_tools_agent(llm, tools, prompt_template)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )

    print(">>> 视觉Agent执行器 (AgentExecutor) 已创建。准备就绪。")
    return agent_executor


def run_multi_modal_agent(input_text: str, image_url: str = ""):
    """
    运行多模态Agent
    """
    agent_executor = create_multi_modal_agent()
    
    response = agent_executor.invoke({
        "input": input_text,
        "image_url": image_url
    })
    
    return response['output']


if __name__ == "__main__":
    print("\n--- [综合挑战开始] ---")

    print("\n--- 测试1: 纯文本 (测试基础对话能力) ---")
    response1 = run_multi_modal_agent("你好，我叫Lewis。", "")
    print(f"回答1: {response1}\n")

    print("--- 测试2: 多模态问题 (测试工具调用) ---")
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Eiffel_Tower_from_immediately_beside_it%2C_Paris_May_2008.jpg/800px-Eiffel_Tower_from_immediately_beside_it%2C_Paris_May2008.jpg"
    question = f"这张图里是什么？它在哪个城市？ {image_url}"

    response2 = run_multi_modal_agent(question, image_url)
    print(f"回答2: {response2}\n")

    print("--- 测试3: 记忆 + 纯文本 (测试记忆模块) ---")
    response3 = run_multi_modal_agent("我叫什么名字？", "")
    print(f"回答3: {response3}\n")

    print("--- [综合挑战结束] ---")

