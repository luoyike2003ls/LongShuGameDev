# Game-SWE-Bench

游戏开发专属基准测试 — 评估大模型在游戏工程领域的真实能力。

## 四个评测维度

| 维度 | 任务数 | 说明 |
|------|--------|------|
| API Understanding | 4 | 引擎 API 正确理解，无幻觉 |
| Architecture Design | 3 | 游戏系统架构设计能力 |
| Bug Diagnosis | 2 | Bug 根因分析与修复建议 |
| Agent Scheduling | 2 | 多智能体任务拆解与调度 |

## 使用方法

```bash
# 完整测试
python game_swe_bench.py --model-path ../models/LongShuGameDev-MLX-4bit

# 只测 API 理解
python game_swe_bench.py --model-path ../models/LongShuGameDev-MLX-4bit --dimension api

# 自定义输出路径
python game_swe_bench.py --model-path ../models/LongShuGameDev-MLX-4bit --output my_results.json
```

## 评测方法

基于关键词匹配 + 反关键词惩罚的自动化评分：

- **关键词匹配**：响应中必须包含领域核心术语
- **反关键词惩罚**：出现错误做法（如 Unity 中用 `Resources.Load` 替代 Addressables）会扣分
- **分数范围**：0% — 100%

## 扩展

在 `game_swe_bench.py` 中添加新的 `BenchmarkTask` 即可扩展测试集。欢迎贡献更多游戏开发领域的测试题目！
