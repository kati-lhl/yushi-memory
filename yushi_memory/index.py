# -*- coding: utf-8 -*-
"""可丢弃的本地记忆索引：SQLite FTS5。

记忆本体永远是 memory.jsonl / 灵魂索引.json。
这个文件只负责查询，删除后可重建，绝不进入记忆胶囊。
"""
import hashlib
import json
import os
import re
import sqlite3


def _safe_id(cid):
    return re.sub(r"[^0-9a-zA-Z_-]", "_", str(cid or "unknown"))[:80] or "unknown"


class MemoryIndex:
    def __init__(self, cache_root):
        self.cache_root = os.path.join(cache_root, "索引缓存")
        os.makedirs(self.cache_root, exist_ok=True)

    def path(self, character_id):
        return os.path.join(self.cache_root, _safe_id(character_id) + ".sqlite3")

    def _conn(self, character_id):
        p = self.path(character_id)
        c = sqlite3.connect(p, timeout=8)
        c.execute("""CREATE TABLE IF NOT EXISTS memories(
            id TEXT PRIMARY KEY, content TEXT, importance REAL, retention REAL,
            source TEXT, type TEXT, status TEXT, created_at TEXT, source_quote TEXT)""")
        c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(id UNINDEXED, content, tokenize='trigram')""")
        c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
        return c

    @staticmethod
    def _records(hub_dir):
        rows, seen, seen_text = [], set(), set()

        def add(item):
            if not isinstance(item, dict):
                return
            text = str(item.get("content") or "").strip()
            if not text:
                return
            if str(item.get("status") or "active") in ("superseded", "deleted", "inactive", "cold", "muted"):
                return
            key = str(item.get("id") or "") or text
            if key in seen or text in seen_text:
                return
            seen.add(key)
            seen_text.add(text)
            rows.append({
                "id": str(item.get("id") or key)[:80],
                "content": text,
                "importance": float(item.get("importance_p") or 0.6),
                "retention": float(item.get("retention_R") or 1.0),
                "source": str(item.get("source") or "unknown")[:40],
                "type": str(item.get("type") or "记忆")[:30],
                "status": str(item.get("status") or "active")[:20],
                "created_at": str(item.get("created_at") or "")[:40],
                "source_quote": str(item.get("source_quote") or "")[:1000],
            })

        try:
            data = json.load(open(os.path.join(hub_dir, "灵魂索引.json"), encoding="utf-8"))
            for x in data.get("memories", []) if isinstance(data, dict) else []:
                add(x)
        except Exception:
            pass
        try:
            for line in open(os.path.join(hub_dir, "memory.jsonl"), encoding="utf-8"):
                line = line.strip()
                if line:
                    try:
                        add(json.loads(line))
                    except Exception:
                        pass
        except Exception:
            pass
        return rows

    @staticmethod
    def signature(hub_dir):
        rows = MemoryIndex._records(hub_dir)
        raw = "\n".join(str(r.get("id")) + "|" + str(r.get("content")) + "|" + str(r.get("status")) for r in rows)
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def rebuild(self, character_id, hub_dir):
        rows = self._records(hub_dir)
        c = self._conn(character_id)
        try:
            c.execute("BEGIN")
            c.execute("DELETE FROM memories")
            c.execute("DELETE FROM memories_fts")
            for r in rows:
                c.execute("INSERT OR REPLACE INTO memories VALUES(?,?,?,?,?,?,?,?,?)",
                          (r["id"], r["content"], r["importance"], r["retention"],
                           r["source"], r["type"], r["status"], r["created_at"], r["source_quote"]))
                c.execute("INSERT INTO memories_fts(id, content) VALUES(?,?)", (r["id"], r["content"]))
            c.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('signature',?)", (self.signature(hub_dir),))
            c.commit()
            return {"ok": True, "count": len(rows), "path": self.path(character_id)}
        except Exception as e:
            c.rollback()
            return {"ok": False, "error": str(e)[:200]}
        finally:
            c.close()

    def search(self, character_id, query, limit=5):
        q = str(query or "").strip()
        if not q:
            return {"ok": True, "items": []}
        c = self._conn(character_id)
        try:
            if len(q) < 3:
                rows = c.execute("SELECT id,content,importance,retention,source,type,status,created_at,source_quote FROM memories WHERE content LIKE ? LIMIT ?", ("%" + q + "%", int(limit))).fetchall()
            else:
                safe = q.replace('"', '""')
                rows = c.execute("""SELECT m.id,m.content,m.importance,m.retention,m.source,m.type,m.status,m.created_at,m.source_quote
                    FROM memories_fts f JOIN memories m ON m.id=f.id
                    WHERE memories_fts MATCH ? ORDER BY bm25(memories_fts) LIMIT ?""", ('"' + safe + '"', int(limit))).fetchall()
            if not rows:
                toks = []
                for seq in re.findall(r"[\u4e00-\u9fa5]{2,}", q):
                    toks.extend(seq[i:i + 2] for i in range(len(seq) - 1))
                toks.extend(re.findall(r"[a-zA-Z0-9_]{2,}", q))
                toks = list(dict.fromkeys(toks))[:8]
                if toks:
                    cond = " OR ".join(["content LIKE ?"] * len(toks))
                    rows = c.execute("SELECT id,content,importance,retention,source,type,status,created_at,source_quote FROM memories WHERE " + cond + " ORDER BY importance DESC LIMIT ?",
                                     tuple("%" + t + "%" for t in toks) + (int(limit),)).fetchall()
            items = [{"id": r[0], "content": r[1], "importance": r[2], "retention": r[3],
                      "source": r[4], "type": r[5], "status": r[6], "created_at": r[7],
                      "source_quote": r[8]} for r in rows]
            return {"ok": True, "items": items}
        except Exception as e:
            return {"ok": False, "items": [], "error": str(e)[:200]}
        finally:
            c.close()

    def status(self, character_id):
        p = self.path(character_id)
        if not os.path.isfile(p):
            return {"exists": False, "count": 0, "size": 0, "path": p}
        try:
            c = self._conn(character_id)
            count = c.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            sig = c.execute("SELECT v FROM meta WHERE k='signature'").fetchone()
            c.close()
            return {"exists": True, "count": int(count), "size": os.path.getsize(p), "path": p,
                    "signature": sig[0] if sig else ""}
        except Exception as e:
            return {"exists": True, "count": 0, "size": os.path.getsize(p), "path": p, "error": str(e)[:160]}
