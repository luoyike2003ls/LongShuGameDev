# Prompt 库 — 游戏开发专用模板

这套 Prompt 模板针对龙枢模型调优，覆盖游戏开发常见场景。

## 目录结构

| 文件 | 用途 |
|------|------|
| `architecture_design.json` | 游戏系统架构设计（背包、技能、战斗等） |
| `bug_diagnosis.json` | Bug 诊断与修复建议 |
| `code_review.json` | 代码审查（UE/Unity/Lua） |
| `gdd_to_tech_spec.json` | 策划案转技术方案 |
| `multi_agent_dispatch.json` | 多智能体任务调度 |

## 使用方法

### 通过推理脚本使用

```bash
# 使用模板运行
python inference/run_longshu.py \
    --model-path ./models/model.gguf \
    --prompt-file prompts/architecture_design.json \
    --template "inventory_system"
```

### 手动使用

打开对应的 JSON 文件，复制 `prompt` 字段的值作为输入即可。

## 贡献

欢迎提交更多游戏开发场景的 Prompt 模板！请遵循以下格式：

```json
{
  "template_name": {
    "name": "中文名称",
    "description": "模板描述",
    "system_prompt": "系统提示词（可选）",
    "prompt": "用户输入"
  }
}
```
