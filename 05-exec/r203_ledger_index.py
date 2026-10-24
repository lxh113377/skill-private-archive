# -*- coding: utf-8 -*-
"""r203_ledger_index.py — 把本仓台账建成一个**派生** SQLite 索引（名册里的 SQLite 落地）。

为什么是 SQLite，以及不是为什么（r203 实测，非臆想）：
    本仓现状 942 个 .json + 4 本 .jsonl 台账（gate_runs 1.27MB / input_pins 1.33MB）。
    我实测五个高频问题的耗时：0.0028~0.0126 秒 —— 即 **SQLite 在这里不是查询提速手段**
    （1.2MB 全扫本来就毫秒级）。若我写「改用 SQLite 让门禁更快」，那是假优化。
    真实成本在另一处：每个新问题都要**写一个新脚本**。本轮我在 TEMP 里攒了 40 个一次性
    脚本件，全部不在仓内 ⇒ 无人可复算（本仓登记过的「临时自证 = 没有自证」同一形态）。
    SQLite 顶的是这个位置：把「按行扫 + 自己解析嵌套 JSON」换成一句 SQL，
    让跨快照的问题不必每次重写一个采集器。

权威边界（重要，防第二真相源）：
    · 真相源仍是 06-benchmark/*.jsonl 与 memory/07-next-steps.md，本件**只读它们**；
    · 索引落在 _temp/（.gitignore 已覆盖）⇒ 不入库、不成为提交物；
    · 每次 --build 全量重建（不做增量合并），因此永不存在「索引比源新」的状态；
    · --stale 比对源件内容指纹，漂移即 rc=1 判红 ⇒ 用它读数前可自证它没落伍；
    · --sql 只读（拒绝非 SELECT/WITH/PRAGMA），任何结论可回原 jsonl 复核。

用法：
    python 05-exec/r203_ledger_index.py --build
    python 05-exec/r203_ledger_index.py --stale
    python 05-exec/r203_ledger_index.py --sql "SELECT gate_id,state,COUNT(*) FROM gate_run GROUP BY 1,2"
退出码：0 正常 / 1 漂移或 SQL 报错 / 2 用法错或缺索引
"""

import argparse
import glob
import hashlib
import io
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BM = os.path.join(ROOT, "06-benchmark")
# 索引落 _temp（已 gitignore）⇒ 派生件，绝不成为第二真相源
DB = os.path.join(ROOT, "_temp", "gate_index.sqlite")
TOKEN = "[LEDGERIDX:PASS]"

JSONL_SOURCES = ["gate_runs.jsonl", "input_pins.jsonl", "debt_runs.jsonl",
                 "upstream_pins.jsonl"]
MEMORY_LEDGER = os.path.join(ROOT, "memory", "07-next-steps.md")
REPORT_GLOB = "全量对标报告_r*.md"


def _fp(path):
    """内容指纹（不用 mtime：并行会话可能同秒写盘，秒级 mtime 不足以辨漂移）。"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return None


def _rows(path):
    out = []
    if not os.path.isfile(path):
        return out
    for line in io.open(path, encoding="utf-8", errors="replace"):
        s = line.strip()
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except ValueError:
            out.append({"__broken__": s[:200]})
    return out


def build(conn):
    c = conn.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS src_fingerprint;
    DROP TABLE IF EXISTS gate_run;
    DROP TABLE IF EXISTS run_meta;
    DROP TABLE IF EXISTS debt_run;
    DROP TABLE IF EXISTS input_pin;
    DROP TABLE IF EXISTS report_section;
    DROP TABLE IF EXISTS ledger_item;
    CREATE TABLE src_fingerprint(
        path TEXT PRIMARY KEY, fp TEXT, bytes INTEGER, mtime INTEGER, rows INTEGER);
    CREATE TABLE run_meta(
        rid INTEGER PRIMARY KEY, ts TEXT, origin TEXT, mode TEXT,
        verdict TEXT, verdict_reason TEXT, gates_run INTEGER, total_ms INTEGER,
        generated_at TEXT, head TEXT, n_gates INTEGER, skipped INTEGER);
    -- 同一 runner 有**两种输出形态**（r203 亲测，别按印象构造）：
    --   06-benchmark/gate_runs.jsonl 的行用 per_gate = {gate_id: state}（仅状态）
    --   --json 快照件用 gates = [{id,state,rc,elapsed_ms,covers,...}]（含明细）
    -- 索引器必须两种都吃；我第一版只认 gates ⇒ gate_run 建成 0 行空表。
    -- gate_run：每次门禁 × 每门 = 一行。这是本索引的主要价值：原形态是嵌套数组，
    -- 问「ratchet_gate 历史上有几次 UNVERIFIED」就得写脚本解析。
    CREATE TABLE gate_run(
        id INTEGER PRIMARY KEY, rid INTEGER, ts TEXT, origin TEXT, mode TEXT,
        gate_id TEXT, state TEXT, rc INTEGER, elapsed_ms INTEGER,
        portable INTEGER, covers TEXT, why TEXT);
    CREATE INDEX idx_gr_gate ON gate_run(gate_id);
    CREATE INDEX idx_gr_ts ON gate_run(ts);
    CREATE INDEX idx_gr_state ON gate_run(state);
    CREATE TABLE debt_run(
        id INTEGER PRIMARY KEY, ts TEXT, round INTEGER, overdue INTEGER,
        deferred INTEGER, repeat INTEGER, decided INTEGER, undated INTEGER,
        active INTEGER, raw TEXT);
    CREATE TABLE input_pin(
        id INTEGER PRIMARY KEY, ts TEXT, schema TEXT, decl TEXT,
        face_root TEXT, face_state TEXT, face_head TEXT, face_dirty_n INTEGER,
        mirror_total INTEGER, mirror_ok INTEGER, raw TEXT);
    CREATE TABLE report_section(
        id INTEGER PRIMARY KEY, report TEXT, round INTEGER, heading TEXT,
        level INTEGER, line INTEGER, bytes INTEGER);
    CREATE TABLE ledger_item(
        id INTEGER PRIMARY KEY, volume TEXT, round INTEGER, key TEXT,
        open INTEGER, verdict TEXT, text TEXT);
    """)

    n_all = 0
    for name in JSONL_SOURCES:
        p = os.path.join(BM, name)
        rel = "06-benchmark/" + name
        rows = _rows(p)
        if os.path.isfile(p):
            st = os.stat(p)
            c.execute("INSERT OR REPLACE INTO src_fingerprint VALUES(?,?,?,?,?)",
                      (rel, _fp(p), st.st_size, int(st.st_mtime), len(rows)))
        n_all += len(rows)
        if name == "gate_runs.jsonl":
            for r in rows:
                if not isinstance(r, dict) or "__broken__" in r:
                    continue
                # 形态 A：--json 快照的 gates 数组（含 rc/耗时/covers）
                # 形态 B：台账 jsonl 的 per_gate 字典（仅状态，其余列留 NULL）
                gs = r.get("gates")
                flat = []
                shape = None
                if isinstance(gs, list) and gs:
                    shape = "gates[]"
                    for g in gs:
                        if isinstance(g, dict):
                            flat.append((g.get("id"), g.get("state"), g.get("rc"),
                                       g.get("elapsed_ms"), 1 if g.get("portable") else 0,
                                       json.dumps(g.get("covers"), ensure_ascii=False)
                                       if g.get("covers") is not None else None,
                                       g.get("why")))
                else:
                    pg = r.get("per_gate")
                    if isinstance(pg, dict) and pg:
                        shape = "per_gate{}"
                        for k, v in pg.items():
                            st = v if isinstance(v, str) else (
                                v.get("state") if isinstance(v, dict) else None)
                            flat.append((k, st, None, None, None, None, None))
                    elif isinstance(pg, list):
                        shape = "per_gate[]"
                        for g in pg:
                            if isinstance(g, dict):
                                flat.append((g.get("id") or g.get("gate"), g.get("state"),
                                             g.get("rc"), g.get("elapsed_ms"),
                                             1 if g.get("portable") else 0, None,
                                             g.get("why")))
                cur = c.execute(
                    "INSERT INTO run_meta(ts,origin,mode,verdict,verdict_reason,gates_run,"
                    "total_ms,generated_at,head,n_gates,skipped) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (r.get("ts"), r.get("origin"), r.get("mode"), r.get("verdict"),
                     r.get("verdict_reason"), r.get("gates_run"), r.get("total_ms"),
                     r.get("generated_at"), r.get("head"), len(flat), r.get("skipped")))
                rid = cur.lastrowid
                _ = shape
                for gid, st, rc_, el, por, cov, why in flat:
                    c.execute(
                        "INSERT INTO gate_run(rid,ts,origin,mode,gate_id,state,rc,"
                        "elapsed_ms,portable,covers,why) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (rid, r.get("ts"), r.get("origin"), r.get("mode"), gid, st,
                         rc_, el, por, cov, why))
        elif name == "debt_runs.jsonl":
            for r in rows:
                if not isinstance(r, dict):
                    continue
                c.execute(
                    "INSERT INTO debt_run(ts,round,overdue,deferred,repeat,decided,"
                    "undated,active,raw) VALUES(?,?,?,?,?,?,?,?,?)",
                    (r.get("ts"), r.get("round"), r.get("overdue"), r.get("deferred"),
                     r.get("repeat"), r.get("decided"), r.get("undated"),
                     r.get("active"), json.dumps(r, ensure_ascii=False)))
        elif name == "input_pins.jsonl":
            for r in rows:
                if not isinstance(r, dict):
                    continue
                faces = r.get("faces") or [{}]
                for f in faces:
                    if not isinstance(f, dict):
                        f = {}
                    c.execute(
                        "INSERT INTO input_pin(ts,schema,decl,face_root,face_state,"
                        "face_head,face_dirty_n,mirror_total,mirror_ok,raw) "
                        "VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (r.get("ts"), r.get("schema"), r.get("decl"), f.get("root"),
                         f.get("state"), f.get("head"), f.get("dirty_n"),
                         r.get("mirror_total"), r.get("mirror_ok"),
                         json.dumps(r, ensure_ascii=False)))

    RE_REP = re.compile(r"全量对标报告_r(\d{1,4})_")
    for f in sorted(glob.glob(os.path.join(BM, REPORT_GLOB))):
        m = RE_REP.search(os.path.basename(f))
        rnd = int(m.group(1)) if m else None
        rel = "06-benchmark/" + os.path.basename(f)
        st = os.stat(f)
        c.execute("INSERT OR REPLACE INTO src_fingerprint VALUES(?,?,?,?,?)",
                  (rel, _fp(f), st.st_size, int(st.st_mtime), None))
        line = 0
        for l in io.open(f, encoding="utf-8", errors="replace"):
            line += 1
            s = l.rstrip(chr(10))
            if s.startswith("#"):
                lv = len(s) - len(s.lstrip("#"))
                c.execute("INSERT INTO report_section(report,round,heading,level,line,"
                          "bytes) VALUES(?,?,?,?,?,?)",
                          (os.path.basename(f), rnd, s.lstrip("#").strip()[:180],
                           lv, line, len(s.encode("utf-8"))))

    if os.path.isfile(MEMORY_LEDGER):
        rel = "memory/07-next-steps.md"
        st = os.stat(MEMORY_LEDGER)
        c.execute("INSERT OR REPLACE INTO src_fingerprint VALUES(?,?,?,?,?)",
                  (rel, _fp(MEMORY_LEDGER), st.st_size, int(st.st_mtime), None))
        for i, l in enumerate(io.open(MEMORY_LEDGER, encoding="utf-8",
                                      errors="replace"), 1):
            s = l.rstrip(chr(10))
            if not s.startswith("- [ ]") and not s.startswith("- [x]"):
                continue
            mm = re.search(r"\[\s*(\d{1,3})\s*\]", s)
            key = re.search(r"\*\*(.{0,80}?)", s)
            vm = re.findall(r"【r\d{1,3}[^】]{0,300}】", s)
            c.execute("INSERT INTO ledger_item(volume,round,key,open,verdict,text) "
                      "VALUES(?,?,?,?,?,?)",
                      (rel, int(mm.group(1)) if mm else None,
                       key.group(1) if key else s[:60],
                       1 if s.startswith("- [ ]") else 0,
                       " | ".join(vm)[:400], s[:600]))
    conn.commit()
    counts = {}
    for t in ("run_meta", "gate_run", "debt_run", "input_pin", "report_section",
              "ledger_item"):
        counts[t] = c.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
    return counts, n_all


def stale(conn):
    c = conn.cursor()
    bad = []
    for path, fp, _b, _m, _r in c.execute(
            "SELECT path,fp,bytes,mtime,rows FROM src_fingerprint"):
        ap = os.path.join(ROOT, path.replace("/", os.sep))
        now = _fp(ap) if os.path.isfile(ap) else None
        if now != fp:
            bad.append((path, fp, now))
    return (not bad), bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="全量重建索引")
    ap.add_argument("--stale", action="store_true", help="比对源指纹判漂移")
    ap.add_argument("--sql", default="", help="对索引跑一条只读查询")
    ap.add_argument("--list", action="store_true", help="列表与行数")
    ap.add_argument("--json", default="", help="SQL 结果另存 JSON")
    args = ap.parse_args(argv)
    if not (args.build or args.stale or args.sql or args.list):
        print("[LEDGERIDX:UNVERIFIED] 必须给 --build/--stale/--sql/--list 之一")
        return 2
    if args.build:
        d = os.path.dirname(DB)
        if not os.path.isdir(d):
            os.makedirs(d)
        if os.path.isfile(DB):
            os.remove(DB)      # 全量重建，绝不做增量 ⇒ 不可能出现「索引比源新」
        conn = sqlite3.connect(DB)
        counts, n_rows = build(conn)
        print("=== 台账索引重建（派生件，落 _temp，不入库）===")
        print("  源 jsonl 行数合计 = %d" % n_rows)
        for t, n in counts.items():
            print("  %-16s %d 行" % (t, n))
        print("  索引件 = %s (%dB)" % (os.path.relpath(DB, ROOT),
                                       os.path.getsize(DB)))
        ok, bad = stale(conn)
        print("  建完即自证指纹：%s" % ("一致" if ok else "漂移 %s" % bad[:2]))
        conn.close()
        if not ok:
            return 1
    if not os.path.isfile(DB):
        print("[LEDGERIDX:UNVERIFIED] 索引不存在 ⇒ 先 --build（缺件不得当作「查无」）")
        return 2
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rc = 0
    if args.stale:
        ok, bad = stale(conn)
        n = conn.execute("SELECT COUNT(*) FROM src_fingerprint").fetchone()[0]
        if ok:
            print("  %s 索引与 %d 个源件内容指纹一致" % (TOKEN, n))
        else:
            print("  [LEDGERIDX:STALE] %d/%d 个源件已变更 ⇒ 索引落伍，读数前须 --build"
                  % (len(bad), n))
            for path, a, b in bad[:6]:
                print("     %-46s 索引=%s 现值=%s" % (path, a, b))
            rc = 1
    if args.list:
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' "
                              "ORDER BY name"):
            nm = r["name"]
            try:
                k = conn.execute("SELECT COUNT(*) FROM " + nm).fetchone()[0]
            except sqlite3.Error:
                k = -1
            print("  %-18s %8d 行" % (nm, k))
    if args.sql:
        q = args.sql.strip()
        if not q.lower().startswith(("select", "with", "pragma")):
            print("[LEDGERIDX:REFUSE] 只读接口：仅允许 SELECT/WITH/PRAGMA（防把索引当写入面）")
            return 2
        try:
            rows = [dict(x) for x in conn.execute(q)]
        except sqlite3.Error as e:
            print("[LEDGERIDX:SQLERR] %s" % e)
            return 1
        print("  返回 %d 行" % len(rows))
        for x in rows[:12]:
            print("   ", json.dumps(x, ensure_ascii=False)[:200])
        if len(rows) > 12:
            print("    ...（共 %d 行，--json 可全量落盘）" % len(rows))
        if args.json:
            with io.open(args.json, "w", encoding="utf-8") as fh:
                json.dump({"schema": "ledger-query-v1", "readonly": True,
                           "sql": q, "rows": rows,
                           "provenance_cmd":
                           "python 05-exec/r203_ledger_index.py --build && "
                           "python 05-exec/r203_ledger_index.py --sql <本条>"},
                          fh, ensure_ascii=False, indent=1)
            print("  JSON -> %s" % args.json)
    conn.close()
    return rc


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
