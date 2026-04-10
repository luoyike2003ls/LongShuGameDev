# 性能调优指南

## 推理速度优化

### 1. GPU Offload（最重要）

尽可能多地将层 offload 到 GPU：

```bash
# Mac — 全部 Metal offload
--n-gpu-layers -1

# NVIDIA — 全部 CUDA offload
--n-gpu-layers -1

# 多 GPU 分摊
--n-gpu-layers 60 --tensor-split 1,1
```

### 2. Batch Size

- **推理阶段**（单条输入）：`--batch-size 512` 足够
- **并发阶段**（多条输入）：增加到 `--batch-size 2048` 或更高
- 更大的 batch size = 更高的吞吐量，但需要更多 VRAM

### 3. Context Window

- 默认 8192 已覆盖大部分场景
- 需要长文档理解时增加到 `--n-ctx 32768` 或 `--n-ctx 65536`
- 更大的 context = 更多内存占用

### 4. Thread Count（CPU 辅助）

```bash
# Mac M4 Pro — 10-12 线程
--threads 10

# Intel/AMD — 物理核心数
--threads $(nproc)
```

线程数过多反而会因为上下文切换降低性能。

## 输出质量优化

### Temperature

| Temperature | 适用场景 |
|------------|---------|
| 0.1-0.3 | 代码生成、JSON 输出、确定性任务 |
| 0.4-0.6 | 架构设计、方案推荐 |
| 0.7-0.9 | 创意发散、头脑风暴 |

### Repeat Penalty

- 默认 `1.1` 适用于大部分场景
- 如果输出出现重复循环，增加到 `1.2-1.3`
- 如果输出过于保守，降低到 `1.05`

### Top-P

- 默认 `0.9` 平衡质量和多样性
- 需要更精确输出时降低到 `0.8`

## 内存优化

### Mac

```bash
# 锁定内存防止交换
export LLAMA_NO_METAL=0
python run_longshu.py --model-path ./model.gguf --mlock
```

### Linux / NVIDIA

```bash
# 使用 mmap 减少初始加载内存
python run_longshu.py --model-path ./model.gguf --mmap

# 限制内存使用
export OMP_NUM_THREADS=10
```

## Benchmark 优化

跑 benchmark 时使用更低温度以保证输出稳定性：

```bash
python benchmark/game_swe_bench.py \
    --model-path ./model.gguf \
    --max-tokens 1024 \
    --temperature 0.3 \
    --top-p 0.8
```
