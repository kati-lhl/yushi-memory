# 字段说明

## 单条记忆

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | string | 是 | 唯一 ID |
| content | string | 是 | 事实/偏好/边界 |
| type | string | 否 | 身份/偏好/约定/边界/事实 |
| status | enum | 是 | active/superseded/cold/deleted/muted/pending |
| importance_p | number | 否 | 0–1 重要度 |
| retention_R | number | 否 | 0–1 留存强度 |
| created_at | string | 否 | ISO 时间 |
| valid_from | string | 否 | 生效时间 |
| last_seen | string | 否 | 最后一次出现 |
| source | string | 否 | chat/user/diary |
| source_quote | string | 否 | 原话证据 |
| topic | string | 否 | address/preference/location 等 |
| superseded_by | string | 否 | 被哪条新记忆取代 |

## 状态

```text
active      当前有效，进入索引
superseded  被取代，保留历史
cold        长期不用
deleted     软删除
muted       静音
pending     待确认
```

## 不变量

```text
memory.jsonl 的 id 唯一
索引只收 active
索引删除后可重建
索引不是真源
```

## 文件

```text
memory.jsonl
灵魂索引.json
索引缓存/<id>.sqlite3
审计日志/
```
