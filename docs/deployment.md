# 部署指南

## 系统要求

### 最低配置
- **Mac**: M2/M3/M4 芯片，64GB 统一内存
- **PC**: 双 RTX 3090/4090 (24GB×2)
- **存储**: 50GB 可用空间（模型 ~40GB + 运行缓存）

### 推荐配置
- **Mac**: M4 Pro/Max，128GB 统一内存
- **PC**: 4× RTX 4090 (24GB×4) 或 A100 80GB

## 快速部署

### 方法一：Python 脚本（推荐）

```bash
# 1. 安装依赖
pip install llama-cpp-python

# 2. 下载模型
# 从 HuggingFace 下载：https://huggingface.co/luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit
# 或使用 huggingface-cli：
huggingface-cli download luoyike2003/LongShuGameDev-Qwen3.5-122B-REAP-Architect-MLX-4bit --local-dir ./models

# 3. 运行
python inference/run_longshu.py --model-path ./models/LongShuGameDev-MLX-4bit
```

### 方法二：Shell 脚本（自动检测硬件）

```bash
chmod +x inference/run_longshu.sh
./inference/run_longshu.sh
```

此脚本会自动检测你的硬件（Apple Silicon / NVIDIA GPU / CPU）并设置最优参数。

### 方法三：Docker

```bash
# 构建镜像
docker build -t longshu:latest .

# 运行
docker run -it --gpus all \
    -v ./models:/models \
    -v ./prompts:/app/prompts \
    longshu:latest \
    --model-path /models/LongShuGameDev-MLX-4bit \
    --prompt "帮我设计一个MMO游戏的公会系统"
```

## 参数调优

### Mac (Apple Silicon)

```bash
python inference/run_longshu.py \
    --model-path ./model.gguf \
    --n-gpu-layers -1 \      # 全部层使用 Metal GPU
    --threads 10 \           # CPU 线程数（M4 Pro 推荐 10-12）
    --batch-size 512 \       # 批处理大小
    --n-ctx 8192             # 上下文窗口
```

### 双 GPU (NVIDIA)

```bash
python inference/run_longshu.py \
    --model-path ./model.gguf \
    --n-gpu-layers 60 \       # 全部层 offload 到 GPU
    --tensor-split 1,1 \      # 两张卡平均分配
    --batch-size 1024 \
    --threads 16
```

### 单 GPU (NVIDIA 24GB)

由于模型 ~40GB，单张 24GB 显卡无法全部加载。部分层将回退到 CPU：

```bash
python inference/run_longshu.py \
    --model-path ./model.gguf \
    --n-gpu-layers 30 \       # 约一半的层在 GPU
    --batch-size 256 \
    --threads 16
```

> 速度会显著下降（~1 token/s），建议双卡或以上。

### CPU Only

```bash
python inference/run_longshu.py \
    --model-path ./model.gguf \
    --n-gpu-layers 0 \
    --batch-size 256 \
    --threads $(nproc)
```

> 仅用于测试，推理速度会非常慢（<0.5 token/s）。

## 生产环境部署

### API 服务模式

```bash
# 使用 llama-cpp-python 的 server 模式
python -m llama_cpp.server \
    --model ./model.gguf \
    --n_gpu_layers -1 \
    --host 0.0.0.0 \
    --port 8080 \
    --n_ctx 8192

# 然后通过 HTTP API 调用
curl http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "messages": [{"role": "user", "content": "帮我设计一个背包系统"}],
        "max_tokens": 2048
    }'
```

### Docker Compose (多实例)

```yaml
version: '3.8'
services:
  longshu-1:
    image: longshu:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    volumes:
      - ./models:/models
    ports:
      - "8081:8080"
    command: --model-path /models/model.gguf --n-gpu-layers -1

  longshu-2:
    image: longshu:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
              capabilities: [gpu]
    volumes:
      - ./models:/models
    ports:
      - "8082:8080"
    command: --model-path /models/model.gguf --n-gpu-layers -1
```

## 常见问题

### 1. 内存不足 (OOM)

- Mac: 关闭不必要的应用，确保有 50GB+ 可用内存
- GPU: 减少 `--n-gpu-layers` 或 `--batch-size`
- 使用 `--mlock` 防止内存交换

### 2. 推理速度慢

- 确认 GPU 层 offload 正确（`--n-gpu-layers -1` 为全 offload）
- 增加 `--batch-size`（但不超过可用内存）
- Mac 上确保使用 Metal 后端（llama-cpp-python 编译时需启用 Metal）

### 3. 输出质量差

- 降低 `--temperature`（建议 0.3-0.7）
- 增加 `--repeat-penalty`（建议 1.1-1.2）
- 确保使用了正确的 System Prompt

### 4. llama-cpp-python 编译失败

```bash
# macOS (Metal)
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --no-cache-dir

# Linux (CUDA)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --no-cache-dir
```
