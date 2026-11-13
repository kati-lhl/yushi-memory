# Design Notes

## 原则

1. JSONL 是事实，索引是缓存。
2. 删除索引必须能重建。
3. 冲突不删，标 `superseded`。
4. 任何状态变更要可审计。
5. 断电最多丢最后一条未 fsync 记录。

## 数据流

```text
写入
  → memory.jsonl（追加）
  → 灵魂索引.json（active 投影）
  → SQLite FTS5（可重建）

读取
  → FTS 查询
  → 失败回退 LIKE
  → 返回 active 记录
```

## 状态

| 状态 | 含义 | 是否进入索引 |
|---|---|---|
| active | 当前有效 | 是 |
| superseded | 被取代 | 否 |
| cold | 长期不用 | 否 |
| deleted | 软删除 | 否 |
| muted | 静音 | 否 |
| pending | 待确认 | 否 |

## 不变量

```text
memory.jsonl 中每条 id 唯一
灵魂索引里的 id 必须能在 memory.jsonl 找到
索引 count 必须等于投影 active 数
索引 signature 必须等于投影签名
```

## 已知取舍

```text
v0.1 不做向量召回
v0.1 不做冲突判断
v0.1 不做自动巩固
```

这些需要上层策略，不应污染数据层。
