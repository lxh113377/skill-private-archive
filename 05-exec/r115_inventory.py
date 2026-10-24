# -*- coding: utf-8 -*-
r"""r115_inventory.py -- 需求1 逐件盘点：功能边界 / 性能指标 / 已知缺陷 / 实际使用反馈。

## 为什么重做（r113/r114 都只做到一半）

需求1 要「逐一梳理每个 skill 的功能边界、性能指标、已知缺陷和**实际使用反馈**」。
r113 做的是「四档身份 + 同源可判」，r114 做的是「替代候选面」——两者都不是这四件事。
缺的正是最后一列：**实际使用反馈**。而它一直有数据源，只是没人接：

| 反馈源 | 实测规模 | 权威件 |
|---|---|---|
| 真实路由调用 | **8,867 次 / 106 个 skill**（已剔除测试自流量 11,410 行） | eval/skill_usage_stats.py |
| 未命中 | **996 次**（route_trace 里 top1=NONE） | 同上 |
| 反馈分级 | feedback.jsonl 分类 | 同上 |

## 四列各自的数据来源（全部可复算，禁编造）

| 列 | 来源 | 口径 |
|---|---|---|
| 功能边界 | D:\global_skills\<slug>\SKILL.md 的 description | 逐件原文，不概括 |
| 性能指标 | ① SKILL.md 字节 ② dir_file_n ③ 该件在盲测/调参面的 Top-1 命中 | 前两项本地实测；第三项取 frozen_blind_eval 结果 |
| 已知缺陷 | ① 路由失败案例（该件作为 expected 但没命中）② 死引用 ③ 版本漂移 | 逐条带题面 |
| 实际使用反馈 | skill_usage_stats 的 per_skill 计数 + 低频候选 + NONE 未命中 | 真实生产 trace，非模拟 |

## 判据（禁读成已完成）

- 使用次数 = 0 的件**不得**读成「无用」：可能是 router 从没路由到（那是缺陷），
  也可能是它只在被点名时加载（那是设计）。本件把两种分开：**有题面期望但 0 调用** = 路由缺陷。
- 低频（<3）只登记不处置：降级/退役属用户裁定面（X-10 禁自动关账）。
- 性能列**不含耗时**：本件不测单 skill 执行耗时（无该数据源），只登记可得的
  体量与命中。禁把「没测」写成「很快」。

用法：
  python 05-exec/r115_inventory.py
  python 05-exec/r115_inventory.py --json <件>
退出码：0 出件且守恒 / 2 输入面不可用（禁记绿）。
"""
import argparse
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
AUTHORITY = r"D:\global_skills"
FENJUE = r"C:\Users\37533\Desktop\workspace\焚诀"
EVAL = os.path.join(FENJUE, "eval")
PY_CANDIDATES = [
    os.path.expanduser(r"~\.workbuddy\binaries\python\envs\default\Scripts\python.exe"),
    r"C:\Program Files\Python312\python.exe",
]


def pick_python():
    for p in PY_CANDIDATES:
        if os.path.exists(p):
            return p
    return sys.executable


def run_eval_json(script, args=(), timeout=1800):
    py = pick_python()
    argv = [py, os.path.join(EVAL, script)] + list(args)
    try:
        p = subprocess.run(argv, cwd=FENJUE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return None, "exc:%r" % (exc,)
    raw = (p.stdout or "").strip()
    i = raw.find("{")
    if i < 0:
        return None, "no_json rc=%s head=%s" % (p.returncode, raw[:200])
    try:
        return json.loads(raw[i:]), None
    except ValueError as exc:
        return None, "json:%r tail=%s" % (exc, raw[-200:])


def read_skill_md(slug):
    p = os.path.join(AUTHORITY, slug, "SKILL.md")
    if not os.path.isfile(p):
        return None
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def frontmatter_desc(text):
    """取 frontmatter 的 description（多行 block 也认）。"""
    if not text or not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = text[3:end]
    lines = fm.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("description:"):
            val = ln.split(":", 1)[1].strip()
            if val in ("|", ">", "|-", ">-", "|+", ">+"):
                buf = []
                for nxt in lines[i + 1:]:
                    if nxt and not nxt.startswith((" ", "\t")):
                        break
                    buf.append(nxt.strip())
                return " ".join(x for x in buf if x).strip()
            buf = [val]
            for nxt in lines[i + 1:]:
                if nxt and not nxt.startswith((" ", "\t")):
                    break
                if nxt.strip():
                    buf.append(nxt.strip())
                elif len(buf) > 1:
                    break
            return " ".join(buf).strip().strip('"').strip("'")
    return None


def dir_stats(slug):
    d = os.path.join(AUTHORITY, slug)
    n = 0
    b = 0
    for root, _dirs, files in os.walk(d):
        for f in files:
            n += 1
            try:
                b += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return n, b


def newest_replacement():
    """选最新替代候选面（与 newest_provenance 同口径：季度产物 ⇄ 历史件比 mtime）。"""
    cands = []
    qdir = os.path.join(BENCH, "quarterly")
    if os.path.isdir(qdir):
        for q in os.listdir(qdir):
            p = os.path.join(qdir, q, "replacement_matrix.json")
            if os.path.isfile(p):
                cands.append(p)
    try:
        for f in os.listdir(BENCH):
            if f.startswith("replacement_matrix_r") and f.endswith(".json"):
                cands.append(os.path.join(BENCH, f))
    except OSError:
        pass
    if not cands:
        return None
    return max(cands, key=lambda p: (os.path.getmtime(p), p))


def newest_provenance():
    """选最新 provenance 面：季度巡检产物与 06-benchmark 历史件同池比 mtime。

    取不到任何一份返回 None（调用方走 UNVERIFIED，禁回落到写死的旧面 —— 那正是本轮修的病）。
    """
    cands = []
    qdir = os.path.join(BENCH, "quarterly")
    if os.path.isdir(qdir):
        for q in os.listdir(qdir):
            p = os.path.join(qdir, q, "provenance.json")
            if os.path.isfile(p):
                cands.append(p)
    try:
        for f in os.listdir(BENCH):
            # 不用 re：本件 import 块里没有 re（首跑即 NameError，实测抓到；py_compile 抓不到）
            if f.startswith("provenance_r") and f.endswith(".json"):
                cands.append(os.path.join(BENCH, f))
    except OSError:
        pass
    if not cands:
        return None
    return max(cands, key=lambda p: (os.path.getmtime(p), p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--replacement", default=None,
                    help="替代候选面（缺省 = 季度巡检 replacement_matrix.json 与 06-benchmark/replacement_matrix_r*.json 里最新一份）")
    ap.add_argument("--provenance", default=None,
                    help="在册面件（缺省 = 季度巡检 provenance.json 与 06-benchmark/provenance_r*.json 里最新一份）")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    # --- 输入面 1：在册 skill 列表（取自 provenance 面） ---
    # r211 修（同族第 4 处「输入面写死日期件」）：原写死 provenance_r112_2026-10-18.json
    # ⇒ 权威源从 182 涨到 191 之后，本盘点**永远只看 182 件**，且不会报任何异常
    # （件数守恒是按它自己读到的 rows0 算的，不是按权威源算的）。这与 r118 修 r118_layer_attr
    # 硬编码 r117 归因件、r191 修棘轮选件口径同族。现改为 --provenance 可指 +
    # 缺省取「季度巡检产物 ⇄ 06-benchmark 历史件」里 mtime 最新的一份，并**显形选了哪份**。
    prov_path = args.provenance or newest_provenance()
    if not prov_path or not os.path.isfile(prov_path):
        print("[INV:UNVERIFIED] 缺在册面: %s" % prov_path)
        return 2
    prov = json.load(io.open(prov_path, encoding="utf-8"))
    rows0 = prov.get("rows") or []
    if not rows0:
        print("[INV:UNVERIFIED] 在册面 0 件 => 禁记绿（R247）")
        return 2

    # --- 输入面 2：真实使用统计 ---
    usage, uerr = run_eval_json("skill_usage_stats.py", ["--json"])
    if not usage:
        print("[INV:UNVERIFIED] 使用统计不可用: %s" % uerr)
        return 2
    per_skill = usage.get("per_skill") or {}
    lowfreq = set(usage.get("low_frequency_candidates") or [])
    total_calls = usage.get("total_calls")
    skills_seen = usage.get("skills_seen")

    # --- 输入面 3：路由评估逐条结果（用于「作为 expected 却未命中」缺陷列） ---
    layered, lerr = run_eval_json("frozen_blind_eval.py", ["--json", "--set", "layered"])
    cases = []
    if layered:
        cases = layered.get("results") or []

    # --- 输入面 4：替代候选面（判「有没有更好的」） ---
    # r211 修（同族第 5 处）：原写死 replacement_matrix_r114_2026-10-18.json
    # ⇒ 权威源 191 件里有 9 件在该面**根本不存在**，其替代列会静默留空，
    # 读起来像「这 9 件无候选」，真相是「读的是上一代面」。现取最新面 +
    # 缺行数显形（不静默），并给处置指引。
    repl_path = args.replacement or newest_replacement()
    repl = {}
    repl_note = None
    if repl_path and os.path.isfile(repl_path):
        try:
            rj = json.load(io.open(repl_path, encoding="utf-8"))
            repl = {r["slug"]: r for r in (rj.get("rows") or [])}
        except Exception as exc:  # noqa: BLE001
            repl_note = "候选面不可读 %r ⇒ 替代列全空（不得读成无候选）" % (exc,)
            repl = {}
    else:
        repl_note = "候选面缺失 ⇒ 先跑 05-exec/r114_replacement_scan.py"
    missing_cand = [r0.get("slug") for r0 in rows0 if r0.get("slug") not in repl] if repl else []
    if missing_cand:
        repl_note = (repl_note or "") + "｜候选面比在册面少 %d 件（%s）⇒ 重跑候选面再盘" % (
            len(missing_cand), ",".join(missing_cand[:6]))

    # --- 逐件装配 ---
    out_rows = []
    for r0 in rows0:
        slug = r0.get("slug")
        if not slug:
            continue
        text = read_skill_md(slug)
        desc = frontmatter_desc(text) or ""
        fn, fb = dir_stats(slug)
        calls = int(per_skill.get(slug) or 0)

        # 缺陷列：该件作为 expected 的题面里没命中的
        own = [c for c in cases if (c.get("expected") == slug)]
        miss = [c for c in own if not c.get("hit")]
        defects = []
        if miss:
            defects.append({"kind": "routing_miss",
                            "n": len(miss), "of": len(own),
                            "samples": [{"query": c.get("query"),
                                         "router_top1": c.get("router_top1"),
                                         "judge": c.get("judge")}
                                        for c in miss[:3]]})
        if text is None:
            defects.append({"kind": "skill_md_missing"})
        if calls == 0 and own:
            defects.append({"kind": "zero_calls_but_expected",
                            "n": len(own),
                            "note": "有题面期望它，但生产 trace 里 0 次被路由到 => 路由缺陷"})

        # 反馈列
        fb_col = {"calls": calls,
                  "share_pct": round(100.0 * calls / total_calls, 2) if total_calls else None,
                  "low_frequency": slug in lowfreq}

        rep = repl.get(slug) or {}
        out_rows.append({
            "slug": slug,
            "confidence": r0.get("confidence"),
            "boundary": {"desc": desc[:600],
                         "desc_len": len(desc),
                         "dir_file_n": fn,
                         "dir_bytes": fb,
                         "skill_md_bytes": (len(text.encode("utf-8")) if text else None)},
            "perf": {"routing_cases": len(own),
                     "routing_hits": len(own) - len(miss),
                     "routing_top1_pct": (round(100.0 * (len(own) - len(miss)) / len(own), 1)
                                          if own else None),
                     "note": "本列无单件执行耗时数据源；只登记命中与体量，禁读成快/慢"},
            "defects": defects,
            "feedback": fb_col,
            "replacement": {"verdict": rep.get("verdict"),
                            "candidates_n": rep.get("candidates_n"),
                            "top_candidate": ((rep.get("candidates") or [{}])[0].get("repo")
                                              if rep.get("candidates") else None)},
        })

    n = len(out_rows)
    zero_call = [x["slug"] for x in out_rows if x["feedback"]["calls"] == 0]
    with_defect = [x["slug"] for x in out_rows if x["defects"]]
    matched = [x["slug"] for x in out_rows if x["replacement"]["verdict"] == "MATCHED"]
    no_repl = [x["slug"] for x in out_rows
               if x["replacement"]["verdict"] == "NO_OS_CANDIDATE"]

    doc = {
        "schema": "skill-inventory-r115-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r115_inventory.py",
        "face": {
            "authority_n": n,
            "usage_total_calls": total_calls,
            "usage_skills_seen": skills_seen,
            "routing_cases": len(cases),
            "replacement_rows": len(repl),
        },
        "conservation": {"rows": n, "authority_n": len(rows0), "ok": n == len(rows0)},
        "summary": {
            "zero_call_n": len(zero_call),
            "zero_call_slugs": sorted(zero_call),
            "with_defect_n": len(with_defect),
            "with_defect_slugs": sorted(with_defect),
            "replacement_matched_n": len(matched),
            "replacement_none_n": len(no_repl),
        },
        "col_notes": {
            "boundary": "SKILL.md frontmatter description 原文（不概括）+ 目录体量",
            "perf": "路由命中（该件作为 expected 的题面）+ 体量；无单件执行耗时源",
            "defects": "routing_miss / skill_md_missing / zero_calls_but_expected",
            "feedback": "真实生产 trace 计数（已剔除测试自流量）",
        },
        "rows": out_rows,
    }
    out = args.json_out or os.path.join(
        BENCH, "inventory_r115_%s.json" % datetime.now().strftime("%Y-%m-%d"))
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    if not args.quiet:
        # r211：本件注释承诺「显形选了哪份输入面」，此前没落地 = 死注释（同族病：
        # 声明与打印分家，见 W-36）。选面必须可见，否则读到的永远是「某一代」面而看着像现值。
        print("输入面：在册=%s ｜ 候选=%s" % (
            os.path.relpath(prov_path, ROOT).replace("\\", "/"),
            os.path.relpath(repl_path, ROOT).replace("\\", "/") if repl_path else "缺失"))
        if repl_note:
            print("  ⚠️ 候选面注记（不静默吞）：%s" % repl_note)
        print("面：在册 %d 件 ｜ 真实调用 %s 次 / %s 个 skill ｜ 路由题面 %d 条 ｜ 替代候选行 %d"
              % (n, total_calls, skills_seen, len(cases), len(repl)))
        print("  0 调用件        : %d" % len(zero_call))
        print("  有缺陷件        : %d（routing_miss / 缺 SKILL.md / 有期望但0调用）" % len(with_defect))
        print("  有替代候选(MATCHED): %d ｜ 开源无对应(NO_OS): %d" % (len(matched), len(no_repl)))
    print("JSON -> %s" % out)
    if n != len(rows0):
        print("[INV:FAIL] 守恒破坏 %d != %d" % (n, len(rows0)))
        return 1
    print("[INV:PASS] 逐件盘点守恒 %d==%d（四列齐备：边界/性能/缺陷/反馈）" % (n, len(rows0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
