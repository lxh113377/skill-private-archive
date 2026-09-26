# -*- coding: utf-8 -*-
r"""evidence_resolvability_measure.py — 「已闭环证据锚点到底可不可解析」的边界值测量（只读）。

为什么先测不先改：本仓 2026-09-22 有一次同类先例——为「记忆里的值是否陈旧」造判据，先在 8 个真实
项目上测出 **TP 恒 0、FP 1~3**，据 R236 补注③「区间重叠即不可作判据」当场否决，没有落。
本轮想把 `upgrade_footer_gate.py` 的 `RE_EVID`（只校验**形状**）升级为「**可解析**」（路径存在 +
锚点token在该文件里真找得到 + backup ID 可定位），必须先量：历史声明里有多少本来就解析得到。

输出四类：SHAPE_OK_AND_RESOLVABLE / SHAPE_OK_BUT_UNRESOLVABLE / SHAPE_BAD_BUT_RESOLVABLE /
SHAPE_BAD_AND_UNRESOLVABLE。前两类之比 = 升级判据的杀伤力与误伤率。
"""
import io
import json
import os
import re
import subprocess
import sys

LOG_DIR = r"D:\global_memory\memory"
ROOTS = [r"D:\global_skills", r"D:\global_memory", r"D:\global_memory_archive",
         r"C:\Users\37533\Desktop\workspace\焚诀", r"C:\Users\37533\Desktop\workspace\自建skill优化"]
BACKUP_DIR = r"D:\global_memory_archive\_trash\rule_backup"
RE_BLOCK = re.compile(r"^<!-- footer:begin session=(\S+) ts=(\S+) -->$")
RE_CLOSE = re.compile(r"状态=已闭环\(证据=(.+)\)")
RE_ANCHOR = re.compile(r"^(?P<path>.+?)#(?P<kind>版本行|backup):(?P<val>.+)$")


def read(p):
    try:
        return io.open(p, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def path_ok(p):
    p = p.strip().strip(chr(96))
    if os.path.isfile(p):
        return p
    for root in ROOTS:
        cand = os.path.join(root, p.replace("\\", os.sep).lstrip("ABCD:" + os.sep + "\\"))
        if os.path.isfile(cand):
            return cand
    return None


def shape_legal(v):
    return bool(re.match(r"^[A-Za-z]:[\\/].+?#(?:版本行:V\d+(?:\.\d+)*|backup:[\w.\-]+)$", v))


def git_has_rev(tok):
    for r in ROOTS:
        if os.path.isdir(os.path.join(r, ".git")):
            p = subprocess.run(["git", "-C", r, "cat-file", "-t", tok], capture_output=True)
            if p.returncode == 0:
                return r
    return None


def resolve(v):
    """返回 (resolvable, reason)。"""
    m = RE_ANCHOR.match(v)
    if not m:
        return False, "无 #kind:val 结构"
    p = path_ok(m.group("path"))
    if not p:
        return False, "路径不存在"
    val = m.group("val")
    if m.group("kind") == "版本行":
        t = read(p)
        bare = val[1:] if val[:1] == "V" else val          # SKILL.md 里写的是裸值 3.5.1
        for tok in {val, bare, "V" + bare}:
            if tok and tok in t:
                return True, "token 在文件内(%s)" % tok
        return False, "token 不在该文件内"
    if os.path.basename(p).endswith((".py", ".md", ".json")) and git_has_rev(val):
        return True, "git 对象存在"
    hit = [f for f in os.listdir(BACKUP_DIR) if val in f] if os.path.isdir(BACKUP_DIR) else []
    return (bool(hit), "回滚件存在" if hit else "backup ID 定位不到")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    days = sys.argv[1:] or ["2026-09-24", "2026-09-23", "2026-09-22"]
    rows, agg = [], {}
    for d in days:
        p = os.path.join(LOG_DIR, d + ".md")
        t = read(p)
        if not t:
            continue
        sess = None
        for ln in t.splitlines():
            mb = RE_BLOCK.match(ln)
            if mb:
                sess = mb.group(1)
            for mc in RE_CLOSE.finditer(ln):
                v = mc.group(1)
                legal = shape_legal(v)
                ok, why = resolve(v)
                key = ("SHAPE_OK_" if legal else "SHAPE_BAD_") + ("RESOLVABLE" if ok else "UNRESOLVABLE")
                agg[key] = agg.get(key, 0) + 1
                rows.append({"date": d, "session": sess, "kind": key, "why": why, "evidence": v[:150]})
    print("=== 已闭环证据锚点可解析性（近 %d 日 GM 日志，只读测量）===" % len(days))
    tot = sum(agg.values())
    for k in sorted(agg):
        print("  %-28s %3d  (%.1f%%)" % (k, agg[k], 100.0 * agg[k] / max(tot, 1)))
    print("  合计 %d 条" % tot)
    upg_hit = agg.get("SHAPE_OK_RESOLVABLE", 0)
    fp = agg.get("SHAPE_OK_UNRESOLVABLE", 0)
    rescue = agg.get("SHAPE_BAD_RESOLVABLE", 0)
    print("-" * 68)
    print("判定：形状合规且可解析=%d | 形状合规但解析不到=%d（%.1f%%，若追溯拦人即误伤面）| 形状不合规=%d"
          % (upg_hit, fp, 100.0 * fp / max(tot, 1), agg.get("SHAPE_BAD_UNRESOLVABLE", 0) + rescue))
    print("样例（每类最多 3 条）：")
    for k in sorted(agg):
        for r in [x for x in rows if x["kind"] == k][:3]:
            print("  %-28s %-14s %s | %s" % (k, r["why"], (r["session"] or "-")[:14], r["evidence"][:96]))
    out = os.path.join(os.getcwd(), "06-benchmark", "evidence_resolvability_measure.json")
    io.open(out, "w", encoding="utf-8").write(json.dumps(
        {"schema": "zijian-evidence-resolvability-v1", "days": days, "agg": agg, "rows": rows},
        ensure_ascii=False, indent=1))
    print("落盘:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
