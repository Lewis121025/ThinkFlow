#!/usr/bin/env python3
"""
ThinkFlow - 统一入口点
基于Tree of Thought思维树的多模态智能代理框架
"""

import argparse
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tot import run_tot, run_tot_orchestrator
from src.agent import run_multi_modal_agent, run_planner_agent


def main():
    parser = argparse.ArgumentParser(
        description="ThinkFlow - 基于思维树的多模态智能代理框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # Tree of Thought (LangGraph版本)
  python main.py tot --problem "我需要为一个5人的团队规划一次为期3天的技术静修会，预算是5000美元。"
  
  # Tree of Thought (协调器版本)
  python main.py tot-orchestrator --problem "我需要为一个5人的团队规划一次为期3天的技术静修会，预算是5000美元。"
  
  # 多模态Agent
  python main.py multi-modal --input "这张图里是什么？" --image-url "https://example.com/image.jpg"
  
  # 规划Agent
  python main.py planner --problem "为期3天，从加州奥克兰出发，规划一次预算友好的东京之旅。"
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='运行模式')
    
    # Tree of Thought (LangGraph)
    tot_parser = subparsers.add_parser('tot', help='运行Tree of Thought (LangGraph版本)')
    tot_parser.add_argument('--problem', type=str, required=True, help='要解决的问题')
    
    # Tree of Thought (Orchestrator)
    tot_orch_parser = subparsers.add_parser('tot-orchestrator', help='运行Tree of Thought (协调器版本)')
    tot_orch_parser.add_argument('--problem', type=str, required=True, help='要解决的问题')
    tot_orch_parser.add_argument('--k', type=int, default=6, help='生成的思想数量 (默认: 6)')
    
    # Multi-Modal Agent
    mm_parser = subparsers.add_parser('multi-modal', help='运行多模态Agent')
    mm_parser.add_argument('--input', type=str, required=True, help='用户输入')
    mm_parser.add_argument('--image-url', type=str, default='', help='图片URL (可选)')
    
    # Planner Agent
    planner_parser = subparsers.add_parser('planner', help='运行规划Agent')
    planner_parser.add_argument('--problem', type=str, required=True, help='要规划的任务')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
    
    print("="*60)
    print("ThinkFlow - 基于思维树的多模态智能代理框架")
    print("="*60)
    print()
    
    try:
        if args.mode == 'tot':
            print(f"运行模式: Tree of Thought (LangGraph)")
            print(f"问题: {args.problem}")
            print()
            run_tot(args.problem)
            
        elif args.mode == 'tot-orchestrator':
            print(f"运行模式: Tree of Thought (协调器)")
            print(f"问题: {args.problem}")
            print(f"生成思想数量: {args.k}")
            print()
            run_tot_orchestrator(args.problem, args.k)
            
        elif args.mode == 'multi-modal':
            print(f"运行模式: 多模态Agent")
            print(f"输入: {args.input}")
            if args.image_url:
                print(f"图片URL: {args.image_url}")
            print()
            result = run_multi_modal_agent(args.input, args.image_url)
            print(f"\n结果: {result}")
            
        elif args.mode == 'planner':
            print(f"运行模式: 规划Agent")
            print(f"任务: {args.problem}")
            print()
            run_planner_agent(args.problem)
            
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

