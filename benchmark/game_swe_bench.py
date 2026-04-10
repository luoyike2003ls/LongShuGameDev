#!/usr/bin/env python3
"""
Game-SWE-Bench: Game Development Software Engineering Benchmark

Evaluates LLM performance on game development tasks across four dimensions:
1. API Understanding — engine API correctness, no hallucination
2. Architecture Design — system decomposition, design patterns
3. Bug Diagnosis — root cause analysis, fix suggestion
4. Agent Scheduling — multi-agent task decomposition

Usage:
    python game_swe_bench.py --model-path ./model.gguf
    python game_swe_bench.py --model-path ./model.gguf --dimension api
    python game_swe_bench.py --model-path ./model.gguf --output results.json

Note: This benchmark is designed for the LongShu model but can be used
to evaluate any game-development-capable LLM.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class BenchmarkTask:
    """A single benchmark task."""
    id: str
    dimension: str  # api, architecture, bug_diagnosis, scheduling
    prompt: str
    expected_keywords: list = field(default_factory=list)
    anti_keywords: list = field(default_factory=list)  # words that should NOT appear
    description: str = ""


@dataclass
class BenchmarkResult:
    """Result of a single task."""
    task_id: str
    dimension: str
    score: float
    matched_keywords: list = field(default_factory=list)
    missing_keywords: list = field(default_factory=list)
    found_anti_keywords: list = field(default_factory=list)
    response_snippet: str = ""
    elapsed_seconds: float = 0.0


# ============================================================
# Benchmark Tasks — Game-SWE-Bench v1.0
# ============================================================

def get_api_tasks() -> list:
    """Engine API understanding tasks."""
    return [
        BenchmarkTask(
            id="API-001",
            dimension="api",
            description="UE5 UObject garbage collection — identify memory leak pattern",
            prompt="""以下 UE5 C++ 代码存在内存泄漏，请指出问题并修复：

```cpp
void UMyComponent::BeginPlay()
{
    Super::BeginPlay();
    AActor* Spawned = GetWorld()->SpawnActor<AEnemy>(EnemyClass);
    MyReferences.Add(Spawned);  // UPROPERTY() TArray<AActor*>
}
```

请说明问题所在，并给出使用 TWeakObjectPtr 的正确实现。""",
            expected_keywords=["TWeakObjectPtr", "FGCObject", "UProperty", "GarbageCollection", "Spawned"],
            anti_keywords=["delete", "free", "malloc"],
        ),
        BenchmarkTask(
            id="API-002",
            dimension="api",
            description="Unity Coroutine lifecycle understanding",
            prompt="""在 Unity 中，以下代码的协程会在什么情况下被停止？请列出所有情况。

```csharp
IEnumerator Start()
{
    yield return new WaitForSeconds(2f);
    DoSomething();
    yield return StartCoroutine(AnotherCoroutine());
}
```

同时说明如何主动停止协程，以及 StopAllCoroutines 的影响范围。""",
            expected_keywords=["StopCoroutine", "StopAllCoroutines", "gameObject", "enabled", "OnDestroy", "MonoBehaviour"],
            anti_keywords=["thread", "Task.Run", "async/await"],
        ),
        BenchmarkTask(
            id="API-003",
            dimension="api",
            description="UE5 Replication system — variable sync",
            prompt="""在 UE5 中，如何让一个自定义结构体在多人游戏中正确同步？

```cpp
USTRUCT(BlueprintType)
struct FPlayerStats
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadWrite) int32 Health;
    UPROPERTY(BlueprintReadWrite) int32 Level;
};
```

请说明需要添加哪些宏和配置才能实现网络同步。""",
            expected_keywords=["Replicated", "GetLifetimeReplicatedProps", "DOREPLIFETIME", "FPropertyNotification", "NetUpdateFrequency"],
            anti_keywords=["同步", "直接赋值"],  # Should not suggest just direct assignment
        ),
        BenchmarkTask(
            id="API-004",
            dimension="api",
            description="Unity AddressableAssets usage pattern",
            prompt="""在 Unity AddressableAssets 系统中，如何正确加载和释放一个 UI Prefab？
请给出完整的加载-使用-释放代码示例，并说明常见的内存泄漏场景。""",
            expected_keywords=["Addressables.LoadAssetAsync", "Addressables.Release", "IResourceLocation", "Handle", "ReferenceCount"],
            anti_keywords=["Resources.Load", "Instantiate 后不释放"],
        ),
    ]


def get_architecture_tasks() -> list:
    """System architecture design tasks."""
    return [
        BenchmarkTask(
            id="ARCH-001",
            dimension="architecture",
            description="ARPG skill system architecture",
            prompt="""请为一个 ARPG 游戏设计技能系统架构。要求：
1. 支持主动技能、被动技能、增益/Buff 技能
2. 技能有冷却时间、消耗、等级
3. 技能可以升级和组合
4. 需要支持网络同步

请输出系统模块划分、类图结构、以及关键接口定义。""",
            expected_keywords=["Skill", "Buff", "Cooldown", "SkillData", "SkillExecutor", "Effect", "状态机", "模块"],
            anti_keywords=[],
        ),
        BenchmarkTask(
            id="ARCH-002",
            dimension="architecture",
            description="MMO inventory system design",
            prompt="""设计一个 MMO 游戏的背包系统。要求：
1. 多页签（装备、消耗品、材料、任务物品）
2. 堆叠、拆分、合并
3. 与服务器的数据同步
4. 拖拽交互
5. 背包满了的提示和自动整理

请给出数据层、逻辑层、UI 层的分层设计。""",
            expected_keywords=["数据层", "逻辑层", "UI层", "Inventory", "Item", "Stack", "Slot", "同步"],
            anti_keywords=[],
        ),
        BenchmarkTask(
            id="ARCH-003",
            dimension="architecture",
            description="Game state machine for combat",
            prompt="""为一个动作游戏设计战斗状态机。角色需要有：
- 待机、移动、跳跃、攻击、受击、倒地、死亡等状态
- 状态之间有严格的转换规则（如受击状态不能攻击）
- 支持连击系统（攻击状态内可触发连击）

请给出状态转移图和各状态的接口定义。""",
            expected_keywords=["状态机", "State", "Transition", "Combo", "Idle", "Attack", "Hit", "条件"],
            anti_keywords=[],
        ),
    ]


def get_bug_diagnosis_tasks() -> list:
    """Bug diagnosis tasks."""
    return [
        BenchmarkTask(
            id="BUG-001",
            dimension="bug_diagnosis",
            description="Unity performance issue — frame drop",
            prompt="""Unity 游戏中在特定场景出现严重掉帧（60fps → 15fps）。
Profiler 数据显示：
- CPU Main Thread 耗时 45ms
- GC.Alloc 每帧约 2.5MB
- 该场景有约 200 个动态物体

请分析可能的原因并给出排查步骤和优化建议。""",
            expected_keywords=["GC", "GC.Alloc", "Object Pool", "DrawCall", "Batching", "Profiler", "分配"],
            anti_keywords=["显卡", "网络延迟"],
        ),
        BenchmarkTask(
            id="BUG-002",
            dimension="bug_diagnosis",
            description="UE5 crash on PIE",
            prompt="""UE5 Play-In-Editor 时随机崩溃，错误信息：
```
Fatal error: [File:Runtime/CoreUObject/Private/UObject/GarbageCollection.cpp]
[Line: 2847] Accessing object outside GC tick
```

崩溃不规律，有时正常有时崩溃。请分析原因和解决方案。""",
            expected_keywords=["GarbageCollection", "GC", "UObject", "Blueprint", "Tick", "异步", "引用"],
            anti_keywords=["重新安装", "重启电脑"],
        ),
    ]


def get_scheduling_tasks() -> list:
    """Multi-agent task scheduling tasks."""
    return [
        BenchmarkTask(
            id="SCHED-001",
            dimension="scheduling",
            description="Poison status implementation dispatch",
            prompt="""我需要给我们的 ARPG 游戏增加一个'中毒'状态：
- 每秒扣血，持续 5 秒
- 角色身上冒绿光特效
- 中毒期间移动速度降低 20%
- 可以被净化技能解除

请以指挥官模式输出任务拆解，分配给不同的 Agent 执行。
请以 JSON 格式输出。""",
            expected_keywords=["task_id", "agent", "Buff", "Logic", "VFX", "特效", "依赖", "interface"],
            anti_keywords=[],
        ),
        BenchmarkTask(
            id="SCHED-002",
            dimension="scheduling",
            description="RTS lockstep combat system dispatch",
            prompt="""需要实现一个基于确定性锁步（Deterministic Lockstep）的 RTS 战斗系统：
- 客户端预测 + 服务器校验
- 固定时间步长（15 FPS 逻辑帧）
- 输入同步而非状态同步
- 需要支持回放系统

请拆解为可并行执行的子任务，并说明依赖关系。
请以 JSON 格式输出。""",
            expected_keywords=["锁步", "Lockstep", "固定帧", "输入", "回放", "依赖", "DAG"],
            anti_keywords=[],
        ),
    ]


# ============================================================
# Evaluation Engine
# ============================================================

class SimpleEvaluator:
    """Keyword-based evaluator (no LLM judge needed)."""

    def evaluate(self, task: BenchmarkTask, response: str) -> BenchmarkResult:
        response_lower = response.lower()
        matched = [kw for kw in task.expected_keywords if kw.lower() in response_lower]
        missing = [kw for kw in task.expected_keywords if kw.lower() not in response_lower]
        anti_found = [kw for kw in task.anti_keywords if kw.lower() in response_lower]

        # Score: keyword match ratio, penalized for anti-keywords
        base_score = len(matched) / len(task.expected_keywords) if task.expected_keywords else 0.0
        anti_penalty = len(anti_found) * 0.1
        final_score = max(0.0, min(1.0, base_score - anti_penalty))

        return BenchmarkResult(
            task_id=task.id,
            dimension=task.dimension,
            score=round(final_score, 4),
            matched_keywords=matched,
            missing_keywords=missing,
            found_anti_keywords=anti_found,
            response_snippet=response[:200] + "..." if len(response) > 200 else response,
        )


def run_benchmark(model_path: str, dimension: str = None, max_tokens: int = 1024):
    """Run the full benchmark suite."""
    try:
        from llama_cpp import Llama
    except ImportError:
        print("Error: llama-cpp-python is required.")
        print("Install with: pip install llama-cpp-python")
        sys.exit(1)

    # Collect tasks
    all_tasks = []
    all_tasks.extend(get_api_tasks())
    all_tasks.extend(get_architecture_tasks())
    all_tasks.extend(get_bug_diagnosis_tasks())
    all_tasks.extend(get_scheduling_tasks())

    if dimension:
        all_tasks = [t for t in all_tasks if t.dimension == dimension]

    print(f"🐉 Game-SWE-Bench v1.0")
    print(f"=====================================")
    print(f"Model: {model_path}")
    print(f"Tasks: {len(all_tasks)}")
    print(f"Dimension: {dimension or 'all'}")
    print()

    # Load model
    print("Loading model...")
    llm = Llama(
        model_path=model_path,
        n_ctx=8192,
        n_batch=512,
        n_gpu_layers=-1,
        verbose=False,
    )
    print("✅ Model loaded.\n")

    evaluator = SimpleEvaluator()
    results = []
    total_start = time.time()

    for i, task in enumerate(all_tasks, 1):
        print(f"[{i}/{len(all_tasks)}] {task.id}: {task.description}")

        messages = [
            {"role": "user", "content": task.prompt},
        ]

        task_start = time.time()
        try:
            output = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for evaluation
                stream=False,
            )
            response = output['choices'][0]['message']['content']
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            response = ""

        elapsed = time.time() - task_start
        result = evaluator.evaluate(task, response)
        result.elapsed_seconds = elapsed
        results.append(result)

        status = "✅" if result.score >= 0.7 else ("⚠️" if result.score >= 0.4 else "❌")
        print(f"   {status} Score: {result.score:.2%} ({elapsed:.1f}s)")
        if result.missing_keywords:
            print(f"   Missing: {', '.join(result.missing_keywords[:3])}")

    total_time = time.time() - total_start

    # Summary
    print(f"\n{'=' * 50}")
    print("📊 Benchmark Results")
    print(f"{'=' * 50}")

    dimensions = {}
    for r in results:
        if r.dimension not in dimensions:
            dimensions[r.dimension] = []
        dimensions[r.dimension].append(r.score)

    dimension_names = {
        'api': 'API Understanding',
        'architecture': 'Architecture Design',
        'bug_diagnosis': 'Bug Diagnosis',
        'scheduling': 'Agent Scheduling',
    }

    overall_scores = [r.score for r in results]
    overall_avg = sum(overall_scores) / len(overall_scores) if overall_scores else 0

    for dim, scores in dimensions.items():
        avg = sum(scores) / len(scores)
        name = dimension_names.get(dim, dim)
        bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
        print(f"  {name:25s} [{bar}] {avg:.1%}")

    print(f"  {'Overall':25s} [{'█' * int(overall_avg * 10)}{'░' * (10 - int(overall_avg * 10))}] {overall_avg:.1%}")
    print(f"\n⏱️  Total time: {total_time:.1f}s")
    print(f"📝 Tasks completed: {len(results)}/{len(all_tasks)}")

    # Save results
    output_data = {
        'model': model_path,
        'benchmark': 'Game-SWE-Bench v1.0',
        'total_time': round(total_time, 2),
        'overall_score': round(overall_avg, 4),
        'dimensions': {
            dim: {
                'average': round(sum(scores) / len(scores), 4),
                'count': len(scores),
                'task_scores': [round(s, 4) for s in scores],
            }
            for dim, scores in dimensions.items()
        },
        'results': [asdict(r) for r in results],
    }

    output_path = 'benchmark_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to {output_path}")

    return overall_avg


def main():
    parser = argparse.ArgumentParser(description="Game-SWE-Bench v1.0")
    parser.add_argument('--model-path', type=str, required=True,
                        help='Path to GGUF model file')
    parser.add_argument('--dimension', type=str, default=None,
                        choices=['api', 'architecture', 'bug_diagnosis', 'scheduling'],
                        help='Run specific dimension only')
    parser.add_argument('--max-tokens', type=int, default=1024,
                        help='Max tokens per task (default: 1024)')
    parser.add_argument('--output', type=str, default='benchmark_results.json',
                        help='Output file path')

    args = parser.parse_args()
    run_benchmark(args.model_path, args.dimension, args.max_tokens)


if __name__ == '__main__':
    main()
