# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest

from yushi_memory import append_jsonl, append_many, read_jsonl, rewrite_jsonl


class StoreTest(unittest.TestCase):
    def test_append_read_rewrite_and_truncated_line(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "memory.jsonl")
            append_jsonl(p, {"id": "1", "content": "喜欢蓝色"})
            append_many(p, [{"id": "2", "content": "住在上海"}])
            self.assertEqual(len(read_jsonl(p)), 2)

            with open(p, "a", encoding="utf-8") as f:
                f.write('{"id":"broken"')
            self.assertEqual(len(read_jsonl(p)), 2)

            rewrite_jsonl(p, [{"id": "1", "content": "改成绿色"}], backup=True)
            rows = read_jsonl(p)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["content"], "改成绿色")
            self.assertTrue(os.path.isfile(p + ".bak"))

    def test_rewrite_keeps_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.jsonl")
            append_jsonl(p, {"id": "1", "content": "a"})
            rewrite_jsonl(p, [{"id": "1", "content": "b"}])
            with open(p, encoding="utf-8") as f:
                self.assertEqual(json.loads(f.readline())["content"], "b")


if __name__ == "__main__":
    unittest.main()
