import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import time

from src.prompts import PLANNER_SYSTEM_PROMPT

load_dotenv()

os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.pop("LANGCHAIN_API_KEY", None)
os.environ.pop("LANGSMITH_ENDPOINT", None)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def generate_plan(problem: str) -> dict:
    """
    调用"规划师"Agent，为其分配一个复杂任务，
    并返回一个结构化的JSON计划。
    """
    print(f"--- [规划师] 接收到任务: {problem} ---")
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": problem}
            ],
            temperature=0.0
        )
        
        raw_response_content = response.choices[0].message.content
        
        start_index = raw_response_content.find('{')
        end_index = raw_response_content.rfind('}')
        
        if start_index == -1 or end_index == -1:
            print(f"--- [规划师] 错误: 在模型回复中找不到JSON的 '{{' 或 '}}' ---")
            print(f"--- 原始回复: {raw_response_content} ---")
            return {}
            
        clean_json_string = raw_response_content[start_index : end_index + 1]
        plan_dict = json.loads(clean_json_string)
        
        print(f"--- [规划师] 已生成蓝图 (JSON): ---")
        print(json.dumps(plan_dict, indent=2, ensure_ascii=False))
        
        return plan_dict

    except Exception as e:
        print(f"--- [规划师] 错误 (可能是JSON解析失败): {e} ---")
        return {}


class AgentState(TypedDict):
    problem: str
    plan: List[str]
    step: int
    result: str


def planner_node(state: AgentState):
    """
    "规划师"节点：只运行一次，生成"蓝图"。
    """
    print("--- [节点: 规划师] ---")
    problem = state["problem"]
    plan_dict = generate_plan(problem)
    
    return {
        "plan": plan_dict.get("plan", []),
        "step": 1
    }


def executor_node(state: AgentState):
    """
    "执行者"节点：在循环中运行，逐一执行任务。
    """
    print(f"--- [节点: 执行者 (第 {state['step']} 步)] ---")
    
    plan = state["plan"]
    step = state["step"]
    
    if not plan or step > len(plan):
        print("   错误：执行者在没有有效计划或步骤的情况下被调用。")
        return {"result": "执行错误"}

    task = plan[step - 1]
    print(f"   执行任务: {task}")
    
    time.sleep(1)
    result = f"成功完成了 '{task}'"
    
    return {
        "step": state["step"] + 1,
        "result": result
    }


def should_continue(state: AgentState):
    """
    "扳道工"：决定下一步是"继续执行"还是"结束"。
    """
    print("--- [节点: 路由 (扳道工)] ---")
    plan = state["plan"]
    step = state["step"]
    
    if step > len(plan):
        print("   决策：计划已完成。")
        return END
    else:
        print(f"   决策：继续执行第 {step} 步。")
        return "executor"


def create_planner_workflow():
    """
    创建并编译规划Agent工作流
    """
    print("\n--- [LangGraph 阶段] ---")

    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)

    workflow.set_entry_point("planner")

    workflow.add_edge("planner", "executor")

    workflow.add_conditional_edges(
        "executor",
        should_continue,
        {
            "executor": "executor",
            END: END
        }
    )

    app = workflow.compile()
    print(">>> (9) 工作流图已编译！`app` 已准备就绪。")
    
    return app


def run_planner_agent(problem: str):
    """
    运行规划Agent
    """
    app = create_planner_workflow()
    
    print("\n--- [运行规划Agent] ---")
    
    try:
        for s in app.stream({"problem": problem}):
            print("---")
            state_summary = {k: v for k, v in s.items() if k != 'problem'}
            print(state_summary)
    except Exception as e:
        print(f"\n--- 运行时错误 ---: {e}")


if __name__ == "__main__":
    complex_task = "为期3天，从加州奥克兰出发，规划一次预算友好的东京之旅。请先查机票，再查3家酒店，最后查3个免费景点。"
    run_planner_agent(complex_task)

