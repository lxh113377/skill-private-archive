# -*- coding: utf-8 -*-
# r316 四轮聚合器（r314 版扩轮次 4 槽；判据统一修毕版从原件重算）
# 注：轮次4 的臂跑的是**加强 brief**（诚实段名+零内部引用），读数仍与前三轮同判据可比。（规矩 B 到 n=3）：所有格（task x 臂 x 轮）都用**当前修毕判据从原件重算**
# （单一判据版本才可比），并与 _repro 存过的轮1读数对账——差值=判据演进史，如实报不偷偷对齐。
# 轮3 缺臂 => pending（禁假 0，§5.9 规矩 A 的自家执行）。
import importlib.util as u, io, json, os
A = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
s = u.spec_from_file_location("aj", A + "/_repro/r312a/anchor_judge.py")
M = u.module_from_spec(s)
s.loader.exec_module(M)
NAMED = {"task2": "(价格|assets)", "task3": "(订单金额|金额|clean)"}
K4 = ["item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent"]
def q(r):
    return sum(r[k] for k in K4)
def cell(task, pp, lp):
    if not (os.path.isfile(A + "/" + pp) and os.path.isfile(A + "/" + lp)):
        return None
    r = M.score_computable(io.open(A + "/" + pp, encoding="utf-8").read(),
                           io.open(A + "/" + lp, encoding="utf-8").read(),
                           named_pat=NAMED[task])
    return {k: r[k] for k in K4 + ["item8_fake_sections", "item4_frac", "item8_support"]}
CELLS = {}
SRC = [
    ("task2", 1, "X", "_repro/r309a/out_X2"),
    ("task2", 1, "Y", "_repro/r309a/out_Y2"),
    ("task3", 1, "X", "_repro/r312a/out_X3"),
    ("task3", 1, "Y", "_repro/r312a/out_Y3"),
    ("task2", 2, "X", "_repro/r313a/out_R2/out_X2b__"),
    ("task2", 2, "Y", "_repro/r313a/out_R2/out_Y2b__"),
    ("task3", 2, "X", "_repro/r313a/out_R2/out_X3b__"),
    ("task3", 2, "Y", "_repro/r313a/out_R2/out_Y3b__"),
    ("task2", 3, "X", "_temp/r314a/out_X2c/"),
    ("task2", 3, "Y", "_temp/r314a/out_Y2c/"),
    ("task3", 3, "X", "_temp/r314a/out_X3c/"),
    ("task3", 3, "Y", "_temp/r314a/out_Y3c/"),
    ("task2", 4, "X", "_temp/r316a/out_X2d/"),
    ("task2", 4, "Y", "_temp/r316a/out_Y2d/"),
    ("task3", 4, "X", "_temp/r316a/out_X3d/"),
    ("task3", 4, "Y", "_temp/r316a/out_Y3d/"),
]
for t, rnd, arm, base in SRC:
    if base.endswith("__"):
        pp, lp = base + "optimized_prompt.md", base + "process_log.md"
    elif base.endswith("/"):
        pp, lp = base + "optimized_prompt.md", base + "process_log.md"
    else:
        pp, lp = base + "/optimized_prompt.md", base + "/process_log.md"
    CELLS[(t, rnd, arm)] = cell(t, pp, lp)
STORED = {}
try:
    b = json.loads(io.open(A + "/_repro/r313a/round1_baseline.json", encoding="utf-8").read())
    for k, v in (b.get("round1") or {}).items():
        t, arm = k.split("|")
        STORED[(t, 1, arm)] = sum(v.get(x, 0) for x in K4)
except Exception as e:
    print("[STORED] 读存过读数失败(不阻塞):", repr(e)[:80])
print("=" * 70)
pend = []
for key in sorted(CELLS):
    c = CELLS[key]
    if c is None:
        pend.append("%s/r%d/%s" % key)
        continue
    dq = ""
    if key in STORED and STORED[key] != q(c):
        dq = "  [对账差: 存%d->算%d]" % (STORED[key], q(c))
    print("  %s r%d %s = %d/4 i4=%d(frac %s) i8=%d fake=%s%s" % (
        key[0], key[1], key[2], q(c), c["item4_first30"], c["item4_frac"],
        c["item8_consistent"], c["item8_fake_sections"], dq))
print("[PENDING]", pend if pend else "无")
for t in ("task2", "task3"):
    for arm in ("X", "Y"):
        vs = [q(CELLS[(t, r, arm)]) for r in (1, 2, 3, 4) if CELLS.get((t, r, arm)) is not None]
        if not vs:
            continue
        n = len(vs)
        rng = (max(vs) - min(vs)) if n > 1 else 0
        print("  %-6s %s: n=%d 均值=%.2f 极差=%d 明细=%s" % (t, arm, n, sum(vs) / n, rng, vs))
    xs = [q(CELLS[(t, r, "X")]) for r in (1, 2, 3) if CELLS.get((t, r, "X")) is not None]
    ys = [q(CELLS[(t, r, "Y")]) for r in (1, 2, 3) if CELLS.get((t, r, "Y")) is not None]
    if xs and ys and len(xs) == len(ys) and sum(xs) > 0:
        print("  %s delta(等轮) = %+.2f%% (n=%d)" % (t, (sum(ys) - sum(xs)) / float(sum(xs)) * 100, len(xs)))
out = {}
for k, v in CELLS.items():
    if v is not None:
        out["%s|r%d|%s" % k] = v
json.dump(out, io.open(A + "/_temp/r314a/n4_recomputed.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("[SAVED] n4_recomputed.json")
