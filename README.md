# 🐉 LongShu (龙枢) — Game Development Large Language Model

<p align="center">
  <strong>专为游戏研发打造的 AI 指挥官 / Game Development Large Language Model</strong>
</p>

<p align="center">
  <a href="https://github.com/luoyike2003ls/LongShuGameDev/actions/workflows/ci.yml"><img src="https://github.com/luoyike2003ls/LongShuGameDev/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow" alt="HuggingFace"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue" alt="License"></a>
  <a href="#benchmark"><img src="https://img.shields.io/badge/Game--SWE--Bench-v1.0-green" alt="Benchmark"></a>
</p>

---

## ⚡ Quick Start / 快速上手

### 0. 免显卡即时体验 (Mock Demo)

无需下载任何数十 GB 权重，无需显卡，直接在终端体验龙枢技术总监（TIANCE）的任务拆解与多智能体调度：

```bash
# 克隆仓库
git clone https://github.com/luoyike2003ls/LongShuGameDev.git
cd LongShuGameDev

# 一秒运行模拟调度
python inference/run_longshu.py --mock --prompt "帮我设计一个MMO游戏的背包与掉落物系统"
```

### 1. 生产环境模型部署 (Real Inference)

```bash
# 安装依赖
pip install -r requirements.txt

# 下载模型（HuggingFace 4-bit MLX/GGUF）
# https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit
huggingface-cli download luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit --local-dir ./LongShuGameDev-MLX-4bit

# 一键运行真实推理
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
LongShuGameDev/
├── .github/workflows/  # GitHub Actions CI 流水线
├── inference/          # 推理脚本 & 部署工具
├── benchmark/          # Game-SWE-Bench 基准测试
├── prompts/            # 游戏开发专用 Prompt 库
├── tools/              # 游戏感知混合量化工具链
├── examples/           # 实战案例（ARPG中毒状态等）
├── tests/              # 自动化测试用例
├── docs/               # 部署与调优文档
├── pyproject.toml      # 现代 Python 打包标准
├── requirements.txt    # 依赖说明
├── TECHNICAL_REPORT.md # 完整学术/工程技术报告
└── Dockerfile          # 容器化部署
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
