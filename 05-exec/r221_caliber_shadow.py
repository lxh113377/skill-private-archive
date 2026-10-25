# -*- coding: utf-8 -*-
r"""r221_caliber_shadow.py — 把「切到严格口径会不会改变下游结论」交给真实下游判据判（只读派生，不连网）。

存在理由（r221 一手，一条自我推翻的实例）：
  我上一轮把 r220_caliber_flip 的判据从「候选级翻转」改成「行级 any 候选为正」并据此打出
  [FLIP:READY]，理由是「该件另有两条 strict 阳性候选在位」。**这个理由比下游真实口径宽**：
  r125 的 C1 只看 ranked 前 3（按 score_total），ComposioHQ(864) 排在 top3 之外
  ⇒ 影子复判显示 A-java-problem 真的从 NEED_C2_HUMAN 变成 KEEP/C1。
  即我自己发明的「行级影响」指标把一次真实回归判成「无影响」。本件因此不再用自造指标，
  而是复跑真实下游判据（r125_c16_machine）两次并逐 slug 比对 verdict。

三态（禁静默）：
  SHADOW:IDENTICAL   两次判据的逐 slug verdict 完全一致 ⇒ 切换不改变任何下游结论
  SHADOW:DIVERGENT   有 slug 的 verdict 变化 ⇒ 逐个具名（从什么变成什么）
  SHADOW:UNVERIFIED 矩阵件不可读 / 下游判据跑不出 / 产物缺 rows ⇒ rc=2，禁读成「无影响」

口径红线：
  · 不重写上游判据、不改其阈值：影子件只把 skill_md_n 覆盖为 skill_md_exact_n，其余字段原样；
  · 两次判据用**同一份代码同一参数**（subprocess 直调 r125_c16_machine.py）；
  · 只比较 verdict 与 blocked_by（下游对外结论），不比较内部分数；
  · 影子件落 06-benchmark（可复核），不落 _temp —— _temp 会被清场，那会让判据退化成一次性（R211-7 同型）。

用法：python 05-exec/r221_caliber_shadow.py [--matrix 件] [--json 件] [--quiet]
退出码：0 IDENTICAL / 1 DIVERGENT / 2 UNVERIFIED。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
PY = sys.executable
TOK_SAME = "[SHADOW:IDENTICAL]"
TOK_DIFF = "[SHADOW:DIVERGENT]"
TOK_UNV = "[SHADOW:UNVERIFIED]"
SUFFIX = "_shadowstrict.json"


def read_json(path):
    try:
        return json.loads(io.open(path, encoding="utf-8-sig", errors="replace").read())
    except (OSError, ValueError):
        return None


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def default_matrix():
    """优先季度产物；跳过自己造的影子件与补测件，防自反馈。"""
    cands = []
    for rel in ("quarterly/*/replacement_matrix.json", "replacement_matrix_*.json"):
        d = os.path.join(BENCH, os.path.dirname(rel))
        if not os.path.isdir(d):
            continue
        rx = re.compile("^" + re.escape(os.path.basename(rel)).replace(r"\*", ".*") + "$")
        for f in sorted(os.listdir(d)):
            if rx.match(f):
                cands.append(os.path.join(d, f))
    best = None
    for p in cands:
        base = os.path.basename(p)
        if base.endswith(SUFFIX) or base.endswith("_fill.json"):
            continue
        m = re.search(r"(20\d\d-\d\d-\d\d)", base)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            mt = 0.0
        key = (1 if base == "replacement_matrix.json" else 0, m.group(1) if m else "", mt)
        if best is None or key > best[0]:
            best = (key, p)
    return best[1] if best else None


def build_shadow(doc):
    """影子件 = 原件的 skill_md_n 被 skill_md_exact_n 覆盖（其余一字不改）。返回改写条数。"""
    rows = (doc or {}).get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    n = 0
    for r in rows:
        for c in (r.get("candidates") or []):
            if is_int(c.get("skill_md_exact_n")):
                c["skill_md_n"] = c["skill_md_exact_n"]
                n += 1
    return n


def run_c16(matrix, out_path):
    cmd = [PY, os.path.join(HERE, "r125_c16_machine.py"),
           "--matrix", matrix, "--json", out_path, "--force"]
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
    except Exception as exc:  # noqa: BLE001
        return None, repr(exc)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout or "")[-300:]
    return read_json(out_path), None


def verdicts(doc):
    rows = doc.get("rows") if isinstance(doc, dict) else None
    if rows is None and isinstance(doc, dict):
        rows = doc.get("results")
    out = {}
    for r in rows or []:
        out[r.get("slug")] = (r.get("verdict") or "") + "|" + (r.get("blocked_by") or "")
    return out


def selftest():
    ok = True

    def chk(name, cond, got=""):
        if cond:
            print("  [OK  ] " + name)
        else:
            print("  [FAIL] " + name + "  <-- " + str(got))
        return bool(cond)

    d = {"rows": [{"slug": "a", "candidates": [{"repo": "R", "skill_md_n": 1, "skill_md_exact_n": 0}]}]}
    n = build_shadow(d)
    c = d["rows"][0]["candidates"][0]
    ok &= chk("影子件只覆盖 skill_md_n（其余字段不动）",
              n == 1 and c["skill_md_n"] == 0 and c["skill_md_exact_n"] == 0 and c["repo"] == "R", c)
    ok &= chk("无 exact 字段 ⇒ 不改写（返回 0）",
              build_shadow({"rows": [{"slug": "a", "candidates": [{"repo": "R", "skill_md_n": 3}]}]}) == 0)
    ok &= chk("空 rows ⇒ 不判（None）", build_shadow({"rows": []}) is None)
    ok &= chk("verdict 比对带 blocked_by",
              verdicts({"rows": [{"slug": "s", "verdict": "KEEP", "blocked_by": "C1"}]})["s"] == "KEEP|C1")
    ok &= chk("results 形态也收",
              verdicts({"results": [{"slug": "s", "verdict": "NEED_C2_HUMAN"}]})["s"] == "NEED_C2_HUMAN|")
    ok &= chk("无 rows/results ⇒ 空判据集（不猜）", verdicts({"other": 1}) == {})
    print("[SHADOW:SELFTEST-" + ("PASS" if ok else "FAIL") + "]")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="切换严格口径的下游结论影响（复跑 r125 两次比对）")
    ap.add_argument("--matrix", default=None)
    ap.add_argument("--json", dest="out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if args.selftest:
        return selftest()
    path = args.matrix or default_matrix()
    if not path or not os.path.isfile(path):
        print(TOK_UNV + " 矩阵件不可得（" + str(path) + "）⇒ 不判，禁读成「无影响」")
        return 2
    doc = read_json(path)
    if not isinstance(doc, dict):
        print(TOK_UNV + " 矩阵件不可读 ⇒ 不判")
        return 2
    n_shadow = build_shadow(doc)
    if n_shadow is None:
        print(TOK_UNV + " 矩阵件无 rows/candidates ⇒ 零输入不判（R247）")
        return 2
    shad_matrix = os.path.join(BENCH, os.path.basename(path).replace(".json", "") + SUFFIX)
    tmp = shad_matrix + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, shad_matrix)
    base_out = os.path.join(ROOT, "_temp", "shadow_base_r221.json")
    shad_out = os.path.join(ROOT, "_temp", "shadow_strict_r221.json")
    base, err_b = run_c16(path, base_out)
    shad, err_s = run_c16(shad_matrix, shad_out)
    if base is None or shad is None:
        print(TOK_UNV + " 下游判据跑不出（base=" + str(err_b) + " strict=" + str(err_s) + "）⇒ 不判")
        return 2
    vb, vs = verdicts(base), verdicts(shad)
    diffs = []
    for k in sorted(vb):
        if vb.get(k) != vs.get(k):
            diffs.append({"slug": k, "baseline": vb[k], "strict": vs.get(k)})
    state = "IDENTICAL" if not diffs else "DIVERGENT"
    out = {
        "schema": "caliber-shadow-r221-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r221_caliber_shadow.py",
        "inputs": {"matrix": os.path.relpath(path, ROOT).replace(os.sep, "/"),
                   "shadow_matrix": os.path.relpath(shad_matrix, ROOT).replace(os.sep, "/"),
                   "downstream": "05-exec/r125_c16_machine.py（同一代码同一参数跑两次）",
                   "shadow_rewrites": n_shadow},
        "state": state, "slugs_total": len(vb), "verdict_diffs": diffs,
        "stats_baseline": base.get("stats") if isinstance(base, dict) else None,
        "stats_strict": shad.get("stats") if isinstance(shad, dict) else None,
        "caveat": "本件只判「切换是否改变下游 verdict」；是否切换另按 r220 裁据（候选级翻转=0 且无未决行）。",
    }
    if not args.quiet:
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        print("严格口径的下游结论影响（矩阵件 = " + rel + "）")
        print("  影子改写条目 " + str(n_shadow) + " ｜slug 总数 " + str(len(vb))
              + " ｜verdict 变化 " + str(len(diffs)))
        for d in diffs:
            print("  变化：" + str(d["slug"]) + " " + str(d["baseline"]) + " -> " + str(d["strict"]))
        if out["stats_baseline"]:
            print("  stats 基线 " + json.dumps(out["stats_baseline"], ensure_ascii=False))
        if out["stats_strict"]:
            print("  stats 严格 " + json.dumps(out["stats_strict"], ensure_ascii=False))
    if args.out:
        tmp2 = args.out + ".tmp"
        with io.open(tmp2, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        os.replace(tmp2, args.out)
        print("JSON -> " + os.path.relpath(args.out, ROOT))
    if diffs:
        print(TOK_DIFF + " " + str(len(diffs)) + " 个 slug 的下游结论会变 ⇒ 切换会改变既有判定，须逐条读")
        return 1
    print(TOK_SAME + " 两次判据逐 slug verdict 完全一致 ⇒ 切换不改变下游结论")
    return 0


if __name__ == "__main__":
    sys.exit(main())
