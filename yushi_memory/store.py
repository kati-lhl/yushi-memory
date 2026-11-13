# -*- coding: utf-8 -*-
"""记忆数据层：只负责 JSONL 的安全追加/重写，不依赖应用逻辑。"""
import json
import os
import shutil
import threading

_LOCK = threading.RLock()


def _fsync(f):
    try:
        f.flush()
        os.fsync(f.fileno())
    except Exception:
        pass


def append_jsonl(path, row):
    """追加一行 JSON；同进程串行，追加后 fsync。"""
    with _LOCK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        line = json.dumps(row, ensure_ascii=False) + "\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
            _fsync(f)
    return True


def append_many(path, rows):
    with _LOCK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            _fsync(f)
    return True


def read_jsonl(path):
    out = []
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def rewrite_jsonl(path, rows, backup=False):
    """整文件重写：临时文件 + fsync + 原子替换。"""
    with _LOCK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp." + str(os.getpid()) + "." + str(threading.get_ident())
        with open(tmp, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            _fsync(f)
        if backup and os.path.isfile(path):
            try:
                shutil.copy2(path, path + ".bak")
            except Exception:
                pass
        os.replace(tmp, path)
    return True
