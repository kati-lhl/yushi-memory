# -*- coding: utf-8 -*-
from .store import append_jsonl, append_many, read_jsonl, rewrite_jsonl
from .index import MemoryIndex

__version__ = "0.1.0"
__all__ = ["append_jsonl", "append_many", "read_jsonl", "rewrite_jsonl", "MemoryIndex"]
