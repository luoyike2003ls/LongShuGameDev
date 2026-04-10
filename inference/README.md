# 推理工具

## 文件说明

| 文件 | 用途 |
|------|------|
| `run_longshu.py` | Python 推理脚本，支持完整参数控制 |
| `run_longshu.sh` | Shell 一键启动脚本，自动检测硬件并设置最优参数 |

## Python 脚本

### 基本用法

```bash
# 交互式对话
python run_longshu.py --model-path ./model.gguf

# 单次提问
python run_longshu.py --model-path ./model.gguf \
    --prompt "UE5 如何实现角色移动的根运动？"

# 使用 Prompt 模板
python run_longshu.py --model-path ./model.gguf \
    --prompt-file ../prompts/architecture_design.json \
    --template "inventory_system"
```

### 完整参数

```
--model-path      GGUF 模型文件路径（必填）
--prompt          输入文本
--prompt-file     Prompt 模板 JSON 文件路径
--template        模板名称（配合 --prompt-file 使用）
--max-tokens      最大生成 token 数（默认 2048）
--temperature     采样温度（默认 0.7）
--top-p           Top-p 采样（默认 0.9）
--repeat-penalty  重复惩罚（默认 1.1）
--n-ctx           上下文窗口大小（默认 8192）
--batch-size      批处理大小（默认 512）
--threads         CPU 线程数（默认 10）
--n-gpu-layers    GPU offload 层数（-1 为全部）
--tensor-split    多 GPU 分配比例，如 "1,1"
```

## Shell 脚本

```bash
chmod +x run_longshu.sh

# 自动检测硬件并启动
./run_longshu.sh

# 指定模型路径
./run_longshu.sh /path/to/model.gguf

# 指定模型 + 问题
./run_longshu.sh /path/to/model.gguf "帮我设计一个技能系统"
```

Shell 脚本会自动检测：
- macOS Apple Silicon → 全 Metal offload
- 双 GPU → tensor split 均衡分配
- 单 GPU → 部分 offload + CPU 辅助
- 无 GPU → 纯 CPU 模式（仅测试）
