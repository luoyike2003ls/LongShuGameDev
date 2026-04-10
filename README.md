# 🐉 LongShu (龙枢) — Game Development Large Language Model

<p align="center">
  <strong>专为游戏研发打造的 AI 指挥官</strong>
</p>

<p align="center">
  <a href="https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow" alt="HuggingFace"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue" alt="License"></a>
  <a href="#benchmark"><img src="https://img.shields.io/badge/Game--SWE--Bench-v1.0-green" alt="Benchmark"></a>
</p>

---

## Quick Start

```bash
# 安装依赖
pip install llama-cpp-python

# 下载模型（HuggingFace）
# https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit

# 一键运行
python inference/run_longshu.py --model-path ./LongShuGameDev-MLX-4bit \
    --prompt "帮我设计一个ARPG游戏的技能系统架构"
```

> **硬件要求**: Mac M2/M3/M4 (64GB) 或 双 RTX 3090/4090 (24GB×2)

---

## 模型简介

龙枢（LongShu）是基于 **Qwen3.5-122B-A10B-MoE** 架构深度优化的游戏研发专属大模型。通过领域特化微调 + 游戏引擎感知的混合量化压缩，在消费级硬件上实现 **3.5 tokens/s** 的推理速度，同时保留 **98.5%** 的核心推理能力。

它不是一个聊天机器人，而是一个**"技术总监 + 主架构师"**——能拆解复杂游戏系统需求、输出可执行的开发计划、调度下游 Agent 协同工作。

### 核心亮点

| 特性 | 说明 |
|------|------|
| **混合注意力架构** | 60 层网络中 Linear + Full Attention 以 3:1 交替，兼顾速度与精度 |
| **256K 超长上下文** | 原生支持 262,144 token，可一次性读取完整项目文档 |
| **极致 MoE 稀疏性** | 105 个专家，每次仅激活 10 个，推理效率极高 |
| **游戏引擎感知量化** | 核心 20 专家高精度保留，非核心 85 专家极限压缩 |
| **Agent 原生输出** | 稳定 JSON 格式输出，专为多智能体调度设计 |

### 训练数据

| 数据类型 | 规模 | 说明 |
|----------|------|------|
| 真实游戏项目 | 50+ | MMO、FPS、ARPG、Roguelike 等 |
| 核心源码 | 20亿+ Token | UE C++、Unity C#、Godot、Lua 热更 |
| 工程文档 | 30万+ 页 | GDD、系统拆解、数值策划逻辑 |
| 线上高质量数据 | 100亿+ | StackOverflow gamedev、GitHub Issues、图形学论文 |

---

## 快速上手

### 1. 安装依赖

```bash
pip install llama-cpp-python numpy
```

### 2. 下载模型

```bash
# 从 HuggingFace 下载 4bit MLX 量化版本
# 推荐使用 huggingface-cli
huggingface-cli download luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit --local-dir ./LongShuGameDev-MLX-4bit
```

### 3. 运行推理

```bash
python inference/run_longshu.py \
    --model-path ./LongShuGameDev-MLX-4bit \
    --prompt "帮我设计一个MMO游戏的背包系统" \
    --max-tokens 2048
```

### 4. Docker 一键部署

```bash
docker build -t longshu:latest .
docker run -it --gpus all -v ./models:/models longshu:latest \
    python inference/run_longshu.py --model-path /models/LongShuGameDev-MLX-4bit
```

### 性能调优参数

| 硬件 | 推荐参数 |
|------|----------|
| Mac M4 Pro 64GB | `--n-gpu-layers -1 --threads 10 --batch-size 512` |
| 双 RTX 4090 | `--n-gpu-layers 60 --tensor-split 1,1 --batch-size 1024` |
| 单 RTX 4090 24GB | `--n-gpu-layers 30 --tensor-split 1 --batch-size 256` |

---

## Benchmark: Game-SWE-Bench

我们构建了专门针对游戏开发领域的基准测试 **Game-SWE-Bench**，涵盖引擎 API 理解、系统架构设计、多智能体调度等维度。

### 评测结果

| 模型 | API 准确率 | 架构设计 | 调度能力 | 综合 |
|------|-----------|---------|---------|------|
| **LongShuGameDev-MLX-4bit** | **94.2%** | **91.5%** | **88.7%** | **91.5%** |
| Qwen3.5-122B-A10B | 87.3% | 84.1% | 79.2% | 83.5% |
| GPT-4o | 82.1% | 78.6% | 74.3% | 78.3% |
| Claude 3.5 Sonnet | 79.8% | 81.2% | 76.1% | 79.0% |

### 运行 Benchmark

```bash
cd benchmark
python game_swe_bench.py --model-path ../models/LongShuGameDev-MLX-4bit
```

详见 [benchmark/README.md](benchmark/README.md)

---

## Prompt 库

我们提供了一套精心调优的 Prompt 模板，覆盖游戏开发常见场景：

```bash
# 查看可用模板
ls prompts/

# 使用模板运行
python inference/run_longshu.py \
    --prompt-file prompts/architecture_design.json \
    --template "inventory_system"
```

| 模板 | 用途 |
|------|------|
| `architecture_design.json` | 游戏系统架构设计 |
| `bug_diagnosis.json` | Bug 诊断与修复建议 |
| `code_review.json` | 代码审查 |
| `gdd_to_tech_spec.json` | 策划案转技术方案 |
| `multi_agent_dispatch.json` | 多智能体任务调度 |

详见 [prompts/README.md](prompts/README.md)

---

## 仓库结构

```
longshu/
├── inference/          # 推理脚本 & 部署工具
├── benchmark/          # Game-SWE-Bench 基准测试
├── prompts/            # 游戏开发专用 Prompt 库
├── tutorials/          # Jupyter Notebook 教程
├── tools/              # 量化/压缩工具链
├── examples/           # 实战案例
├── docs/               # 文档
├── TECHNICAL_REPORT.md # 技术报告
└── Dockerfile          # Docker 部署
```

---

## 模型生态

龙枢是 REAP（游戏研发多智能体协作网络）的核心大脑：

| 角色 | 代号 | 定位 |
|------|------|------|
| 👑 **指挥官** | 天策 / TIANCE | 全局规划、任务拆解、智能体调度 |
| 🏗️ 架构师 | 玄构 / XUANGOU | 架构优化、技术债务识别（即将开源） |
| ⚒️ 执行者 | 墨行 / MOXING | 代码编写、Bug 修复（即将开源） |
| 🔭 守望者 | 烛照 / ZHUZHAO | 日志分析、异常检测（即将开源） |

---

## License

Apache 2.0

---

## 引用

如果你在工作中使用了龙枢模型，请引用：

```bibtex
@misc{longshu2026,
  title={LongShuGameDev: A Game Development Large Language Model},
  author={LongShu Team},
  year={2026},
  url={https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit},
  publisher={HuggingFace}
}
```

---

*龙 · 驱动游戏研发的未来*
