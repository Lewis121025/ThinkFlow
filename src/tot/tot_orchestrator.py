from openai import OpenAI
import json
import os
from dotenv import load_dotenv

from src.prompts import GENERATOR_SYSTEM_PROMPT, EVALUATOR_SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

print("--- '协调器' (Orchestrator) 已启动 ---")
print("已成功加载 '生成者' 和 '批评家' 的Prompts。")


def generate_thoughts(problem_description, k):
    """
    指挥 "生成者Agent" 进行发散思维，生成 k 个不同的思考步骤。
    """
    print(f"\n--- 正在调用 '生成者Agent' 生成 {k} 个思想 ---")
    
    user_prompt = f"""
[原始问题]:
{problem_description}

[需要生成的思想数量]:
{k}
"""

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-nano-12b-v2-vl:free",
            messages=[
                {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["thoughts"]

    except Exception as e:
        print(f"调用 '生成者Agent' 时出错: {e}")
        return []


def evaluate_thought(problem_description, thought_step):
    """
    指挥 "批评家Agent" 进行收敛思维，评估单个思想的价值。
    """
    print(f"--- 正在调用 '批评家Agent' 评估: '{thought_step}' ---")
    
    user_prompt = f"""
[原始问题]:
{problem_description}

[提议的思考步骤]:
{thought_step}
"""

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-nano-12b-v2-vl:free",
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"调用 '批评家Agent' 时出错: {e}")
        return {"score": 0, "reason": f"评估失败: {e}"}


def run_tot_orchestrator(problem: str, k: int = 6):
    """
    运行Tree of Thought协调器版本
    """
    print(f"--- 启动ToT单步循环 (k={k}) ---")
    print(f"问题: {problem}\n")

    # 1. --- 发散 (Diverge) ---
    try:
        generated_thoughts = generate_thoughts(problem, k)
    except Exception as e:
        print(f"主循环中 '生成' 步骤失败: {e}")
        generated_thoughts = []

    # 2. --- 收敛 (Converge) ---
    evaluated_thoughts = []
    
    if generated_thoughts:
        print("\n--- '协调器' 正在将任务分发给 '批评家' ---")
        
        for thought in generated_thoughts:
            evaluation = evaluate_thought(problem, thought)
            
            evaluated_thoughts.append({
                "thought": thought,
                "score": evaluation.get("score", 0),
                "reason": evaluation.get("reason", "N/A")
            })

        print("\n--- 所有思想已评估完毕 ---")
        print(json.dumps(evaluated_thoughts, indent=2, ensure_ascii=False))
    else:
        print("--- '生成者' 未能产生任何思想 ---")

    # --- 4. 剪枝与选择 (Prune & Select) ---
    if evaluated_thoughts:
        best_thought_data = max(evaluated_thoughts, key=lambda x: x["score"])

        print("\n" + "="*30)
        print("--- 最终选择 (Best Thought) ---")
        print(f"最佳思考路径 (分数: {best_thought_data['score']}/10):")
        print(f"  思想: {best_thought_data['thought']}")
        print(f"  理由: {best_thought_data['reason']}")
        print("="*30)
        
        return best_thought_data
    else:
        print("\n--- 最终选择 ---")
        print("没有可供选择的思想。")
        return None


if __name__ == "__main__":
    problem = "我需要为一个5人的团队规划一次为期3天的技术静修会，预算是5000美元。"
    run_tot_orchestrator(problem, k=6)

