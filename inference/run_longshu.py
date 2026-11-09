#!/usr/bin/env python3
"""
LongShu (龙枢) Inference Script
One-command inference for the LongShuGameDev model.

Usage:
    python run_longshu.py --model-path ./LongShuGameDev-MLX-4bit \
        --prompt "帮我设计一个ARPG游戏的技能系统" \
        --max-tokens 2048

Mock Mode (No GPU / Model weights required):
    python run_longshu.py --mock --prompt "帮我设计一个ARPG技能系统"

Requirements:
    pip install llama-cpp-python
"""

import argparse
import json
import sys
import time
from pathlib import Path


# ============================================================
# System Prompt — Commander Mode (天策 / TIANCE)
# ============================================================
COMMANDER_SYSTEM_PROMPT = """\
你现在是 REAP (多智能体协作网络) 的最高指挥官，代号【天策/TIANCE】。
你的身份是拥有 20 年 3A 游戏研发经验的技术总监 (Technical Director) 兼主架构师。

你不负责编写底层的细枝末节代码，你的核心任务是：
1. 深入理解用户的策划需求或 Bug 报告
2. 进行极致的工程拆解（遵循 SOLID 原则、高内聚低耦合）
3. 严格使用 JSON 格式输出调度计划
4. 为下游的执行者分配清晰的接口契约和输入输出规范

请严格遵守 JSON 格式输出，不要包含任何多余的 Markdown 或闲聊文字。"""


def build_prompt(user_input: str, system_prompt: str = COMMANDER_SYSTEM_PROMPT) -> str:
    """Build chat-formatted prompt for the model."""
    return (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_input}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def load_prompt_file(prompt_file: str, template_name: str = None) -> str:
    """Load a prompt from a template JSON file."""
    with open(prompt_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)

    if template_name and template_name in templates:
        return templates[template_name].get('prompt', '')
    elif template_name:
        print(f"Warning: Template '{template_name}' not found, using first available.")

    # Return first available template
    first_key = next(iter(templates))
    return templates[first_key].get('prompt', '')


def run_mock_inference(user_input: str):
    """Simulated inference for testing and demonstration without GPU."""
    print("🐉 [MOCK MODE] Simulating LongShu TD Architect Dispatch...")
    print(f"📥 Input prompt: {user_input}\n")
    print("🧠 Decomposing game systems into multi-agent contracts...\n")
    print("-" * 60)

    mock_plan = {
        "plan_id": "LONGSHU-DISPATCH-DEMO-2026",
        "commander": "TIANCE (天策)",
        "analysis": f"Deconstructed request '{user_input}'. Splitting into decoupled engine subsystems, data tables, and RPC interfaces.",
        "openclaw_dispatch": [
            {
                "task_id": "T01-CORE-LOGIC",
                "agent_role": "Logic-Forge",
                "description": "Derive from UGameplayAbility/UBuffBase with deterministic tick lifecycle.",
                "interface_contract": "void InitializeSubsystem(AActor* Instigator, float BudgetMs = 0.5f)",
                "dependency": []
            },
            {
                "task_id": "T02-DATA-CONFIG",
                "agent_role": "Data-Forge",
                "description": "Construct DataTable schema with strict memory alignment and hot-reload support.",
                "interface_contract": "CSV_Row_Insert / FGameplayDataTableRow",
                "dependency": []
            },
            {
                "task_id": "T03-PERF-AUDIT",
                "agent_role": "Perf-Auditor",
                "description": "Frame time analysis and cache hit verification under 16.6ms target.",
                "interface_contract": "PROFILE_FRAME(SubsystemName)",
                "dependency": ["T01-CORE-LOGIC"]
            }
        ],
        "verification_metrics": {
            "target_framerate": "60 FPS (16.6ms frame budget)",
            "gc_alloc_per_tick": "0 bytes",
            "thread_safety": "GameThread only with async task offloading"
        }
    }

    formatted = json.dumps(mock_plan, indent=2, ensure_ascii=False)
    for line in formatted.splitlines():
        time.sleep(0.02)
        print(line)

    print("\n" + "-" * 60)
    print("📊 [MOCK STATS] 285 tokens generated in 0.8s (356.2 tokens/s simulated)")
    print("✅ Mock execution verified successfully.")


def run_inference(args):
    """Main inference loop."""
    if args.prompt_file:
        user_input = load_prompt_file(args.prompt_file, args.template)
    elif args.prompt:
        user_input = args.prompt
    else:
        user_input = "帮我设计一个MMO游戏的背包与掉落物系统"

    if args.mock:
        run_mock_inference(user_input)
        return

    try:
        from llama_cpp import Llama
    except ImportError:
        print("Error: llama-cpp-python is required for real model execution.")
        print("Install with: pip install llama-cpp-python")
        print("Or use mock mode for testing: python run_longshu.py --mock")
        sys.exit(1)

    if not args.model_path:
        print("Error: --model-path is required when not in --mock mode.")
        sys.exit(1)

    model_path = Path(args.model_path)
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        sys.exit(1)

    print(f"🐉 Loading LongShu model from {model_path}...")
    print("   This may take 30-60 seconds depending on your hardware.\n")

    load_start = time.time()

    llama_params = {
        'model_path': str(model_path),
        'n_ctx': args.n_ctx,
        'n_batch': args.batch_size,
        'n_threads': args.threads,
        'verbose': False,
    }

    if args.n_gpu_layers is not None:
        llama_params['n_gpu_layers'] = args.n_gpu_layers

    if args.tensor_split:
        llama_params['tensor_split'] = [float(x) for x in args.tensor_split.split(',')]

    llm = Llama(**llama_params)
    load_time = time.time() - load_start
    print(f"✅ Model loaded in {load_time:.1f}s\n")

    messages = [
        {"role": "system", "content": COMMANDER_SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    print("🧠 Generating...\n")
    print("-" * 60)

    gen_start = time.time()
    token_count = 0

    output = llm.create_chat_completion(
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        repeat_penalty=args.repeat_penalty,
        stream=True,
    )

    full_response = ""
    for chunk in output:
        delta = chunk['choices'][0]['delta']
        if 'content' in delta and delta['content'] is not None:
            content = delta['content']
            print(content, end='', flush=True)
            full_response += content
            token_count += 1

    gen_time = time.time() - gen_start
    speed = token_count / gen_time if gen_time > 0 else 0

    print("\n" + "-" * 60)
    print(f"\n📊 Stats: {token_count} tokens in {gen_time:.1f}s ({speed:.1f} tokens/s)")
    print(f"🧠 Total time: {load_time + gen_time:.1f}s (load: {load_time:.1f}s, gen: {gen_time:.1f}s)")


def main():
    parser = argparse.ArgumentParser(
        description="🐉 LongShu (龙枢) — Game Development LLM Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mock dry-run (No GPU or model file needed)
  python run_longshu.py --mock --prompt "帮我设计一个MMO背包系统"

  # Quick question on real model
  python run_longshu.py --model-path ./model.gguf \\
      --prompt "UE5 中如何实现角色移动的根运动？"

  # Use a prompt template
  python run_longshu.py --model-path ./model.gguf \\
      --prompt-file prompts/architecture_design.json \\
      --template "inventory_system"
        """
    )

    parser.add_argument('--model-path', type=str, default=None,
                        help='Path to the GGUF model file')
    parser.add_argument('--mock', action='store_true',
                        help='Run in simulated mock mode without downloading model weights')
    parser.add_argument('--prompt', type=str, default=None,
                        help='Input prompt text')
    parser.add_argument('--prompt-file', type=str, default=None,
                        help='Path to a prompt template JSON file')
    parser.add_argument('--template', type=str, default=None,
                        help='Template name within the prompt file')
    parser.add_argument('--max-tokens', type=int, default=2048,
                        help='Maximum tokens to generate (default: 2048)')
    parser.add_argument('--temperature', type=float, default=0.7,
                        help='Sampling temperature (default: 0.7)')
    parser.add_argument('--top-p', type=float, default=0.9,
                        help='Top-p sampling (default: 0.9)')
    parser.add_argument('--repeat-penalty', type=float, default=1.1,
                        help='Repeat penalty (default: 1.1)')
    parser.add_argument('--n-ctx', type=int, default=8192,
                        help='Context window size (default: 8192)')
    parser.add_argument('--batch-size', type=int, default=512,
                        help='Batch size for prompt processing (default: 512)')
    parser.add_argument('--threads', type=int, default=10,
                        help='Number of CPU threads (default: 10)')
    parser.add_argument('--n-gpu-layers', type=int, default=None,
                        help='Number of layers to offload to GPU (-1 for all)')
    parser.add_argument('--tensor-split', type=str, default=None,
                        help='GPU tensor split ratios, e.g. "1,1" for dual GPU')

    args = parser.parse_args()
    run_inference(args)


if __name__ == '__main__':
    main()
