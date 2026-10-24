# -*- coding: utf-8 -*-
"""r214_tool_carrier_face.py — 名册工具↔skill 承载面对账（第 93 门，r214）。

存在理由：前 92 门量的是「工具能不能跑」(163)、「话术能不能召回」(208/213)、「分卷有没有指针」
(204)，但**没有任何门断言「每个名册工具至少被一个 skill 承载」** —— 那恰恰是目标
「把这些免费工具与相关 skill 合理搭配」最字面的可读形态。一个工具从全部 .md 里被删干净，
今天所有门照样绿。

本轮建门前先踩到该门的命门（已固化为 K2）：我第一版对账探针把模式表键写成「Cloudflare D1」
（空格），名册却是「Cloudflare-D1」（连字符）⇒ 四个工具静默算成 0 命中，差点被我当成
「这四个工具在 skill 里没人说何时用」写进报告。**分母键名不匹配 = 反向断言全缺位的典型**
（本仓 X-24/X-26 同族）。故本门强制「每个名册工具的归一化键必须在模式表里存在」，
缺任一 ⇒ UNVERIFIED（绝不按「工具没承载」下结论）。

判据（全本地只读，零网络）：
  K1 名册 = free_tools_latest.json 的 rows（tool/state）；文件缺失或不可析 ⇒ UNVERIFIED。
  K2 模式表 = tool_carrier_patterns.json；名册每个工具 norm(名) 都能取到键，
     否则 ⇒ UNVERIFIED（先拦「分母键错位」，再谈承载）。norm 与门内同一实现。
  K3 承载 = 扫 D:/global_skills/**/*.md（跳过 __pycache__/.git/_bak），按该工具的正则集
     命中去重技能根；计数 0 ⇒ GAP_UNCARRIED。命中面必须自报文件数，空面 ⇒ UNVERIFIED
     （扫不到卷 ≠ 都没承载）。
  K4 基线 tool_carrier_baseline.json 只拦新增；缺 ⇒ UNVERIFIED（R247）。
  K5 有牙自检：正例 = 至少一工具被实扫到 ≥1 承载技能；反例 = 用假正则（不可能命中）重算
     同工具，必须落 GAP。两例齐备才算本门咬得动，否则 WARN。

portable=False：读 D:/global_skills 与名册读数件，均本机绝对路径。
退出码：0 无新增未承载 / 1 有新增 / 2 名册、模式表、扫描面或基线不可得
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GS = "D:/global_skills"
BENCH = os.path.join(ROOT, "06-benchmark")
ROSTER = os.path.join(BENCH, "free_tools_latest.json")
PATTERNS = os.path.join(BENCH, "tool_carrier_patterns.json")
BASELINE = os.path.join(BENCH, "tool_carrier_baseline.json")
TOKEN = "[CARRIER:PASS]"
SKIP = ("__pycache__", ".git", "_bak", "_trash")


def norm(s):
    """归一化工具名：去 cloudflare- 前缀、连字符转空格、upstash-redis 归 upstash。
    键与名册两侧同用此函数，杜绝本轮踩过的「表键用空格、名册用连字符」。"""
    t = (s or "").lower().strip()
    t = t.replace("cloudflare-", "").replace("cloudflare ", "")
    t = t.replace("upstash-redis", "upstash").replace("upstash redis", "upstash")
    t = t.replace("-", " ").replace("_", " ").strip()
    return t


def _read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read().lower()
    except OSError:
        return ""


def load_roster():
    if not os.path.isfile(ROSTER):
        return None, "名册读数件缺失 %s（先跑 free_tools_face 生成）" % ROSTER
    try:
        d = json.load(io.open(ROSTER, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, "名册读数件不可析：%s" % str(e)[:60]
    rows = d.get("rows") or []
    if not rows:
        return None, "名册 rows 为空 ⇒ 分母为空面，不得判绿"
    return rows, None


def walk_vols():
    vols = []
    if not os.path.isdir(GS):
        return None
    for dp, dns, fns in os.walk(GS):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                t = _read(p)
                if t:
                    vols.append((os.path.relpath(p, GS).replace(os.sep, "/"), t))
    return vols or None


def carriers(tool, pats, vols):
    skills, files = set(), 0
    for rel, t in vols:
        if any(re.search(p, t) for p in pats):
            files += 1
            skills.add(rel.split("/")[0])
    return len(skills), files, sorted(skills)[:6]


def evaluate():
    rows, err = load_roster()
    if rows is None:
        return None, err
    if not os.path.isfile(PATTERNS):
        return None, "模式表缺失 %s ⇒ 分母不可建" % PATTERNS
    pat = json.load(io.open(PATTERNS, encoding="utf-8"))
    keys = {norm(k): v for k, v in (pat.get("patterns") or {}).items()}
    missing = [r.get("tool") for r in rows if norm(r.get("tool")) not in keys]
    if missing:
        # K2：分母键错位 —— 本轮亲手踩过的假发现形态，必须先拦
        return None, "模式表键未覆盖名册：%s ⇒ 该工具命中数不可信（r214 踩过连字符/空格）" % missing
    vols = walk_vols()
    if vols is None:
        return None, "扫描面为空或 %s 不可达 ⇒ 空面不判绿（R247）" % GS
    gaps = []
    for r in rows:
        tool = r.get("tool")
        n_skills, n_files, sample = carriers(tool, keys[norm(tool)], vols)
        if n_skills == 0:
            gaps.append("%s|状态=%s 无任何 skill 承载（正则集 %d 条，扫描 %d 卷）" % (
                tool, r.get("state"), len(keys[norm(tool)]), len(vols)))
    return gaps, {"tools": len(rows), "vols": len(vols)}


def teeth(vols):
    """K5：正例（至少一工具真被实扫到）+ 反例（假正则必落 0 承载）。"""
    rows, err = load_roster()
    if rows is None or not vols:
        return False, "输入不可得：%s" % (err or "扫描面空")
    pat = json.load(io.open(PATTERNS, encoding="utf-8")) if os.path.isfile(PATTERNS) else {}
    keys = {norm(k): v for k, v in (pat.get("patterns") or {}).items()}
    pos = neg = False
    for r in rows:
        k = norm(r.get("tool"))
        if k not in keys:
            continue
        ns, _, _ = carriers(r.get("tool"), keys[k], vols)
        if ns > 0:
            pos = True
        ns2, _, _ = carriers(r.get("tool"), ["zzz_no_such_tool_zzz"], vols)
        if ns2 == 0:
            neg = True
    return (pos and neg), "正例有承载=%s 反例假正则判无承载=%s" % (pos, neg)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    gaps, res = evaluate()
    if gaps is None:
        print("[CARRIER:UNVERIFIED] %s（不得按全绿记，R247）" % res)
        return 2
    print("=== 名册工具↔skill 承载面（r214·本机专属）===")
    print("  名册 %d 工具 / 扫描 %d 卷，未承载 = %d" % (res["tools"], res["vols"], len(gaps)))
    vols = walk_vols() or []
    ok, why = teeth(vols)
    print("  [CARRIER:%s] K5 有牙自检：%s" % ("SELFTEST" if ok else "WARN", why));
    if not os.path.isfile(BASELINE):
        print("[CARRIER:UNVERIFIED] 基线件缺失 ⇒ 无法判增量，不按绿记（R247）")
        return 2
    base = set(json.load(io.open(BASELINE, encoding="utf-8")).get("known_uncarried") or [])
    cur = set(gaps)
    new_ones = sorted(cur - base)
    known = sorted(cur & base)
    for h in sorted(base - cur):
        print("  [CARRIER:HEALED] %s 已有承载（基线应同步收缩）" % h)
    for k in known:
        print("  [CARRIER:KNOWN] %s 历史未承载（在基线内）" % k)
    for x in new_ones:
        print("  [CARRIER:GAP] %s 新增：工具接进工作流却无任何 skill 说何时用它" % x)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "tool-carrier-v1", "readonly": True,
                       "tools": res["tools"], "vols": res["vols"],
                       "gaps": sorted(cur), "baseline": sorted(base),
                       "new_gaps": new_ones, "k5_teeth": ok, "k5_detail": why,
                       "note": "搭配的字面形态 = 每个名册工具至少被一个 skill 承载；"
                               "本门前置是模式表键与名册归一化键一一对齐（K2），"
                               "否则 0 命中是探针错不是发现（r214 踩过）",
                       "provenance_cmd": "python 05-exec/r214_tool_carrier_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if new_ones:
        print("[CARRIER:FAIL] 新增未承载 %d 条" % len(new_ones))
        return 1
    print("  %s 无新增未承载工具（历史 %d 条在基线内）" % (TOKEN, len(known)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())