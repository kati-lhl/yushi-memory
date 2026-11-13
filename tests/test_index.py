# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from yushi_memory import MemoryIndex


def write_hub(hub):
    os.makedirs(hub, exist_ok=True)
    data = {
        "schema_version": 2,
        "memories": [
            {"id": "1", "content": "用户喜欢蓝色", "type": "偏好", "status": "active",
             "importance_p": 0.9, "retention_R": 1.0},
            {"id": "2", "content": "用户住在杭州", "type": "事实", "status": "active",
             "importance_p": 0.8, "retention_R": 0.9},
            {"id": "3", "content": "用户以前喜欢红色", "type": "偏好", "status": "superseded",
             "importance_p": 0.7, "retention_R": 1.0},
        ],
    }
    with open(os.path.join(hub, "灵魂索引.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


class IndexTest(unittest.TestCase):
    def test_rebuild_search_and_drop_cache(self):
        with tempfile.TemporaryDirectory() as d:
            hub = os.path.join(d, "角色", "鱼")
            write_hub(hub)
            idx = MemoryIndex(hub)
            r = idx.rebuild("鱼", hub)
            self.assertTrue(r["ok"])
            self.assertEqual(r["count"], 2)

            hit = idx.search("鱼", "喜欢什么颜色")
            self.assertTrue(hit["ok"])
            self.assertTrue(any("蓝色" in x["content"] for x in hit["items"]))
            self.assertFalse(any("红色" in x["content"] for x in hit["items"]))

            os.remove(idx.path("鱼"))
            self.assertFalse(idx.status("鱼")["exists"])
            self.assertTrue(idx.rebuild("鱼", hub)["ok"])

    def test_signature_changes_when_content_changes(self):
        with tempfile.TemporaryDirectory() as d:
            hub = os.path.join(d, "角色", "鱼")
            write_hub(hub)
            idx = MemoryIndex(hub)
            s1 = idx.signature(hub)
            data = json.load(open(os.path.join(hub, "灵魂索引.json"), encoding="utf-8"))
            data["memories"][0]["content"] = "用户喜欢绿色"
            json.dump(data, open(os.path.join(hub, "灵魂索引.json"), "w", encoding="utf-8"),
                      ensure_ascii=False)
            self.assertNotEqual(s1, idx.signature(hub))


if __name__ == "__main__":
    unittest.main()
