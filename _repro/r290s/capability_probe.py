# -*- coding: utf-8 -*-
"""capability_probe.py — 核台账 R261-7 那句「三项本地无」（只读受管根，不写任何东西）。

口径：漂移腿的本地面 = SKILL.md + references/ 全部 .md 合并（同 quarterly_skill_sweep.load_local_merged），
所以必须按合并面数命中，只数 SKILL.md 会漏。
"""
import io, os, re
SK = "D:/global_skills/security-audit"
NEEDLES = {
    "os_sandbox": [r"OS-enforced sandbox", r"\bsandbox\b", r"沙箱"],
    "write_isolation": [r"[Ww]rite isolation", r"隔离写", r"no-follow"],
    "coverage_ledger": [r"coverage-ledger", r"coverage ledger", r"\bledger\b", r"台账"],
}
files = [os.path.join(SK, "SKILL.md")] + sorted(
    os.path.join(SK, "references", f) for f in os.listdir(os.path.join(SK, "references")) if f.endswith(".md"))
merged = []
for p in files:
    for i, ln in enumerate(io.open(p, encoding="utf-8").read().splitlines(), 1):
        merged.append((os.path.basename(p), i, ln))
print("MERGED_FILES %s lines=%d" % ([os.path.basename(p) for p in files], len(merged)))
for name, pats in NEEDLES.items():
    hits = [(f, i, l[:70]) for (f, i, l) in merged for p in pats if re.search(p, l)]
    print("NEEDLE %-16s patterns=%d hits=%d detail=%s" % (name, len(pats), len(hits), hits[:6]))
print("[CAP-PROBE] done")
