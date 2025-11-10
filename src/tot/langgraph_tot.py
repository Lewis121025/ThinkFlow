from typing import List, TypedDict
import json
from openai import OpenAI
import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from src.prompts import GENERATOR_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


# --- 1. 定义"状态" (State) ---
class ToTState(TypedDict):
    """
    ToTState (思维树状态)
    这是我们Agent团队的"共享内存"或"接力棒"。
    """
    # 必需的输入
    problem: str
    
    # "生成者"的输出
    generated_thoughts: List[str]
    
    # "批评家"的输出
    evaluated_thoughts: List[dict]
    
    # "选择"步骤的输出
    best_thought: dict
    
    # 循环次数限制
    retries: int


def generate(state: ToTState):
    """
    (节点 1) 指挥 "生成者Agent" 生成 K 个思想。
    """
    print(f"--- 节点: 'generate' (生成者) ---")
    problem = state["problem"]
    retries = state["retries"]
    
    user_prompt = f"[原始问题]:\n{problem}\n\n[需要生成的思想数量]:\n{6}"
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite-preview-09-2025",
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    print(f"    (第 {retries + 1} 次尝试...)")

    result = json.loads(response.choices[0].message.content)
    return {
        "generated_thoughts": result["thoughts"],
        "retries": retries + 1
    }


def evaluate(state: ToTState):
    """
    (节点 2) 指挥 "批评家Agent" 评估所有 K 个思想。
    """
    print(f"--- 节点: 'evaluate' (批评家) ---")
    problem = state["problem"]
    thoughts = state["generated_thoughts"]
    
    evaluations = []
    for thought in thoughts:
        user_prompt = f"[原始问题]:\n{problem}\n\n[提议的思考步骤]:\n{thought}"
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash-lite-preview-09-2025",
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        eval_result = json.loads(response.choices[0].message.content)
        eval_result["thought"] = thought
        evaluations.append(eval_result)
        
    return {"evaluated_thoughts": evaluations}


def select_best(state: ToTState):
    """
    (节点 3) "剪枝"：从评估中选出最好的一个。
    这是一个*非LLM*的"工具节点"(Tool Node)。
    """
    print(f"--- 节点: 'select_best' (选择者) ---")
    evaluations = state["evaluated_thoughts"]
    
    best_thought = max(evaluations, key=lambda x: x["score"])
    
    return {"best_thought": best_thought}


MIN_QUALITY_SCORE = 7
MAX_RETRIES = 3


def decide_next_step(state: ToTState):
    """
    (决策者 - "扳道工")
    这不是一个"节点",它是一个"路由函数"。
    它检查"评估"节点的分数,并决定下一步是"返工"还是"通过"。
    """
    print(f"--- 决策者 (Router): 检查品控 ---")
    
    evaluations = state["evaluated_thoughts"]
    retries = state["retries"]
    
    best_score = max(evaluation["score"] for evaluation in evaluations)
    print(f"    最高分: {best_score}/10 (阈值: {MIN_QUALITY_SCORE})")
    print(f"    重试次数: {retries}/{MAX_RETRIES}")

    if best_score < MIN_QUALITY_SCORE and state["retries"] < MAX_RETRIES:
        print(f"--- 决策: 质量不佳 (最高分 {best_score} < 7)，正在返工... ---")
        return "generate"

    else:
        if state["retries"] >= MAX_RETRIES:
            print(f"--- 决策: 已达最大返工次数 {MAX_RETRIES}。---")
        print("--- 决策: 质量达标 (或已放弃)，进入最终选择... ---")
        return "select"


def create_tot_workflow():
    """
    创建并编译Tree of Thought工作流
    """
    print("\n--- 正在构建工作流 (Graph) ---")

    workflow = StateGraph(ToTState)

    workflow.add_node("generate", generate)
    workflow.add_node("evaluate", evaluate)
    workflow.add_node("select_best", select_best)

    workflow.set_entry_point("generate")

    workflow.add_edge("generate", "evaluate")
    
    workflow.add_conditional_edges(
        "evaluate",
        decide_next_step,
        {
            "generate": "generate",
            "select": "select_best"
        }
    )

    workflow.add_edge("select_best", END)

    app = workflow.compile()

    print("--- 工作流已编译! ---")
    return app


def run_tot(problem: str):
    """
    运行Tree of Thought流程
    """
    app = create_tot_workflow()
    
    print("\n--- 启动 LangGraph 流程... ---")
    
    initial_input = {
        "problem": problem,
        "retries": 0
    }
    
    final_state = None
    
    for s in app.stream(initial_input):
        print(f"\n--- 状态更新 (来自节点: {list(s.keys())[0]}) ---")
        print(s[list(s.keys())[0]])
        
        final_state = s[list(s.keys())[0]]

    print("\n" + "="*30)
    print("--- 流程执行完毕 (END) ---")
    
    print("最终的 'State' 内容:")
    print(final_state)
    
    best_thought = final_state.get("best_thought", {})
    
    print("\n--- 最终选择的思考 (来自 'best_thought') ---")
    print(best_thought)
    
    return final_state


if __name__ == "__main__":
    problem = "我需要为一个5人的团队规划一次为期3天的技术静修会，预算是5000美元。"
    run_tot(problem)

