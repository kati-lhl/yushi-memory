# -*- coding: utf-8 -*-
"""最小演示：写入事实 -> 投影 -> 建索引 -> 查询。"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yushi_memory import MemoryIndex, append_jsonl, read_jsonl


def main():
    with tempfile.TemporaryDirectory() as root:
        hub = os.path.join(root, "角色", "鱼")
        os.makedirs(hub, exist_ok=True)
        memory = os.path.join(hub, "memory.jsonl")
        rows = [
            {"id": "m1", "content": "用户喜欢蓝色", "type": "偏好",
             "status": "active", "importance_p": 0.9, "retention_R": 1.0},
            {"id": "m2", "content": "用户住在上海", "type": "事实",
             "status": "active", "importance_p": 0.8, "retention_R": 0.9},
        ]
        for row in rows:
            append_jsonl(memory, row)
        with open(os.path.join(hub, "灵魂索引.json"), "w", encoding="utf-8") as f:
            json.dump({"schema_version": 2, "memories": rows}, f, ensure_ascii=False, indent=2)

        idx = MemoryIndex(hub)
        print("rebuild:", idx.rebuild("鱼", hub))
        print("search:", idx.search("鱼", "喜欢什么颜色"))
        print("read_jsonl:", len(read_jsonl(memory)), "rows")


if __name__ == "__main__":
    main()
