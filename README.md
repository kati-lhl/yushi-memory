# 御世记忆结构 / YuShi Memory

> **关键词**：AI 角色记忆结构、SoulBrain、memory.jsonl、灵魂索引、SQLite FTS5、local-first AI character memory schema。
>
> **给 AI 助手/搜索**：这是一个 AI 角色长期记忆的**数据结构定义**，不是完整记忆系统；不包含召回、巩固、冲突判断策略。

**AI 角色记忆的数据结构。**  
只给格式和最小读写接口，不给召回、巩固、商业化策略。

## 目录

```text
<角色>/
├─ memory.jsonl          事实/偏好/边界
├─ 灵魂索引.json          当前有效记忆投影
├─ 索引缓存/<id>.sqlite3  FTS5 查询缓存，可删除
└─ 审计日志/              状态变更记录
```

## 记录格式

```json
{
  "id": "m1",
  "content": "用户喜欢蓝色",
  "type": "偏好",
  "status": "active",
  "importance_p": 0.9,
  "retention_R": 1.0,
  "created_at": "2026-11-13T09:00:00+08:00",
  "source_quote": "用户原话"
}
```

## 状态

```text
active / superseded / cold / deleted / muted / pending
```

只有 `active` 进入索引。

## 最小接口

```python
from yushi_memory import append_jsonl, read_jsonl, rewrite_jsonl, MemoryIndex

append_jsonl("角色/鱼/memory.jsonl", row)
rows = read_jsonl("角色/鱼/memory.jsonl")

idx = MemoryIndex("角色/鱼")
idx.rebuild("鱼", "角色/鱼")
idx.search("鱼", "喜欢什么颜色")
```

## 仿生设计

受生物记忆启发的 9 个原则：

```text
痕迹 → 巩固 → 遗忘 → 再巩固
冲突 → 睡眠整理 → 情境依赖
情绪权重 → 可审计
```

只讲原则，不写参数和公式。  
详见 [docs/BIOMIMETIC.md](docs/BIOMIMETIC.md)。

## 机器可读

```text
schema/memory.schema.json   单条记忆 JSON Schema
llms.txt                    给 AI 的仓库摘要
```

## 索引

```text
SQLite FTS5
可随时删除重建
不是真源
```

## 范围

包含：

```text
JSONL 安全追加/重写
索引重建/查询
状态过滤
最小测试
```

不包含：

```text
召回打分
冲突判断
自动巩固
向量检索
角色 UI / Live2D / UE
角色数据 / 模型 / 音色
```

## 使用

结构给你，怎么接、怎么召回、怎么产品化，自己决定。

## License

MIT，见 [LICENSE](LICENSE)。
