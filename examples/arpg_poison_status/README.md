# 实战案例：ARPG 中毒状态实现

本案例演示龙枢如何将一个简单需求拆解为可执行的开发任务。

## 需求

> 给 ARPG 游戏增加一个"中毒"状态：每秒扣血，持续 5 秒，角色身上冒绿光。

## 龙枢输出示例

```json
{
  "plan_id": "TASK-STATUS-POISON-001",
  "analysis": "中毒状态涉及逻辑层的状态机倒计时、数值层的属性扣减、表现层的特效挂载，以及可以被净化技能解除的交互接口。必须严格分离表现与逻辑。",
  "openclaw_dispatch": [
    {
      "task_id": "T01",
      "agent_role": "Logic-Forge",
      "description": "基于现有的 UBuffBase 类，派生 UPoisonBuff。实现 OnApply（启动计时器）、OnTick（每秒扣血）、OnRemove（清理状态）。使用 FTimerHandle 管理 5 秒生命周期。",
      "interface_contract": "UPoisonBuff(AActor* Target, float DamagePerTick, float Duration = 5.0f)",
      "dependency": []
    },
    {
      "task_id": "T02",
      "agent_role": "VFX-Artisan",
      "description": "在 Target 的 Socket 'Spine_02' 处 Spawn 绿色粒子特效 P_PoisonAura。监听 Buff 的 OnRemove 事件同步销毁特效。",
      "interface_contract": "void PlayPoisonVFX(AActor* Target)",
      "dependency": ["T01"]
    },
    {
      "task_id": "T03",
      "agent_role": "Data-Forge",
      "description": "在 Buff_DataTable.csv 中新增一行：ID=1001, Name=Poison, TickInterval=1.0, Duration=5.0, DamagePerTick=10, MovementSpeedModifier=-0.2。",
      "interface_contract": "CSV_Row_Insert",
      "dependency": []
    },
    {
      "task_id": "T04",
      "agent_role": "Logic-Forge",
      "description": "在净化技能（CleanseSkill）中添加对中毒状态的检测逻辑：遍历 Target 身上的 Buff 列表，找到 UPoisonBuff 实例并调用 Remove()。",
      "interface_contract": "void CleanseBuff(AActor* Target, EBuffType Type)",
      "dependency": ["T01"]
    }
  ]
}
```

## 任务依赖图

```
T01 (逻辑层 Buff) ──┬──> T02 (特效)
                     └──> T04 (净化)
T03 (数据配置)

T01 和 T03 可并行，T02 和 T04 依赖 T01。
```

## 关键设计决策

1. **继承现有 Buff 系统**：不重新造轮子，复用 UBuffBase 框架
2. **数据驱动**：所有数值（伤害、持续时间、减速比例）配置在 DataTable 中
3. **表现解耦**：特效和逻辑完全分离，通过事件通知
4. **可扩展**：新增其他 DoT 状态（燃烧、流血）只需派生新类

## 运行此案例

```bash
python inference/run_longshu.py \
    --model-path ./models/LongShuGameDev-MLX-4bit \
    --prompt-file prompts/multi_agent_dispatch.json \
    --template "agent_dispatch_arpg"
```
