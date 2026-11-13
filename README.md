# 御世记忆底座 / YuShi Memory

**给 AI 角色用的本地优先、可审计记忆底座。**  
不是向量数据库，也不是聊天记录拼接。

> v0.1 只开源“数据层 + 索引层 + 设计约束”，不包含角色数据、UI、模型权重、商业逻辑。

## 为什么

大多数 AI 角色只有两种记忆：

```text
1. 把聊天记录全塞进上下文
2. 全部丢进向量库，召回不可解释
```

YuShi Memory 的取舍：

```text
memory.jsonl   事实真源，可读、可 diff、可审计
灵魂索引.json  对外投影，只放当前有效记忆
SQLite FTS5    可丢弃缓存，删了可重建
```

## 结构

```text
<角色>/
├─ memory.jsonl          事实/偏好/边界，追加写
├─ 灵魂索引.json          active 投影
├─ 索引缓存/<id>.sqlite3  FTS5，可删除
└─ 审计日志/              变更记录
```

```text
写入 → memory.jsonl
     → 灵魂索引投影
     → FTS 重建
```

## 状态

```text
active       当前有效
superseded   被新事实取代，保留历史
cold         长期不用，降权
deleted      软删除
muted        静音
pending      待确认
```

## 安装

```bash
pip install -e .
python examples/demo.py
python -m unittest discover -s tests -v
```

无第三方依赖，Python 3.10+。

## 最小用法

```python
from yushi_memory import append_jsonl, read_jsonl, MemoryIndex

append_jsonl("角色/鱼/memory.jsonl", {
    "id": "m1",
    "content": "用户喜欢蓝色",
    "type": "偏好",
    "status": "active",
    "importance_p": 0.9,
    "retention_R": 1.0,
})

rows = read_jsonl("角色/鱼/memory.jsonl")

idx = MemoryIndex("角色/鱼")
idx.rebuild("鱼", "角色/鱼")
print(idx.search("鱼", "喜欢什么颜色"))
```

## 设计约束

```text
1. 索引不是真源，删除后必须能重建
2. 任何状态变更必须留审计
3. 冲突不物理删除，只标 superseded
4. 召回失败不能影响事实层
5. 断电后最多丢最后一条未 fsync 的记录
```

## 已包含

```text
JSONL 安全追加 / 原子重写 / 截断容错
SQLite FTS5 索引
active/superseded/cold/deleted/muted/pending 过滤
索引签名与重建
最小测试与示例
```

## 未包含

```text
LLM 提取、冲突判断、自动巩固
召回打分策略
向量检索
角色 UI / Live2D / UE
角色数据、模型、音色
```

这些属于上层应用，后续按需拆。

## 路线

```text
v0.1  数据层 + 索引层
v0.2  召回打分 + 冲突扫描
v0.3  7 天模拟测试与基准
v1.0  完整可嵌入的 SoulBrain Core
```

## 适合谁

```text
做 AI 陪伴 / 虚拟角色 / 游戏 NPC 的开发者
不想把角色记忆交给云端黑盒的人
需要审计“她为什么记得这件事”的人
```

## License

MIT. 见 [LICENSE](LICENSE).

## 中文说明

如果你在做 AI 角色，欢迎提 Issue 说你的记忆结构；不要只发“求 star”。
