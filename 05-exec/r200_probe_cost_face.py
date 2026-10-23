# -*- coding: utf-8 -*-
# r200_probe_cost_face.py - 探针自成本面（第 76 门）：一次全量门禁跑要花掉多少外部 API 调用。
#
# 存在理由（r200 一手）：本轮 r200_pages_face 连打 4 次，第 2 次撞到 Cloudflare GraphQL 的
# 「Rate limiter budget depleted」⇒ **监控免费额度这件事本身在消耗免费额度**。而我刚给每轮
# 新增会打 CF 的门，此后每轮成本上升却没有任何面在看这个数。它无声增长的结局是两头假：
# 判据把自己饿死（拿不到读数），而读数缺失又被读成「额度很安全」。
#
# 口径（v5。前面各版的错都在本轮实测里被抓出来，逐条留在注释里以免下次重犯）：
#   ① 分母 = 门表已注册 ＋ 有外部机械 ＋ 命中厂商标记 的件；未挂门的临时探针不计
#      （v1 按目录扫全部 .py，把 r132 这类未注册件算进分母，虚增成本）。
#   ② 按厂商不按端点形态：wrangler CLI 打的就是 Cloudflare API ⇒ cloudflare；
#      git fetch/push 走 GitHub ⇒ github（v1/v2 只看 GraphQL 主机字面量，整件漏计了
#      r163_free_tools_face / r163_turnstile_face 两个 wrangler 门）。
#   ③ 声明比对必须大小写无关：read_script 统一 lower()，而 DECL_RE 不带 re.I 时
#      10 个已声明件全被读成「未声明」—— 成本面自己少算，比根本没有这个面更坏（v4 实测）。
#   ④ 静态粗筛必有假阳性，所以本面**以实测 manifest 为准做对账**，而不是只要求「有声明」：
#      实测 r113_cache_guard_face* 足迹 0/0（只起本地子进程）⇒ 不要求声明、不计成本；
#      声明值 ≠ 实测值 ⇒ FAIL（这才是牙齿：改了联网面却没重测，CI 同轮即红）。
#   ⑤ 不写排除名单（排除名单是第二真相源）：本件自身无 urlopen / 无 subprocess 调用，
#      由机械判定自然排除。
# 声明写法（值必须实测，不许估）：件内一行
#   # CALLS_PER_RUN: cloudflare=3 github=0   (实测：python 05-exec/r200_probe_cost_measure.py)
# 缺 manifest ⇒ UNVERIFIED（rc=2，取不到不等于超限，R247）。
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOKEN = "[PROBECOST:PASS]"
MANIFEST = os.path.join(ROOT, "06-benchmark", "probe_cost_measure_latest.json")
DECL_RE = re.compile(r"CALLS_PER_RUN\s*:\s*(.+)", re.I)   # 必须 re.I，见口径 ③
API_KEYS = ("cloudflare", "github")

CF_NEEDLES = ("api.cloudflare.com", "cloudflare.com", "wrangler")
GH_NEEDLES = ("api.github.com", "github.com", "gh.exe", "gh.cmd", "github cli",
              "'gh'", '"gh"', "gh api", "gh auth", "gh run", "gh --version",
              "gh version")
GIT_OUT = re.compile(r"\bgit\b\s+(fetch|push|ls-remote)")
MECH = ("urlopen", "http.client", "requests.get", "requests.post",
        "subprocess.run", "subprocess.popen", "subprocess.call", "shutil.which")


def load_gates():
    import importlib.util as _u
    spec = _u.spec_from_file_location("rg_self", os.path.join(HERE, "run_gates.py"))
    mod = _u.module_from_spec(spec)
    bak = sys.argv[:]
    sys.argv = ["run_gates.py"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = bak
    return [{"id": g.get("id"), "script": g.get("script"),
             "portable": bool(g.get("portable"))}
            for g in (getattr(mod, "GATES", []) or []) if g.get("script")]


def read_script(name):
    p = os.path.join(HERE, name)
    if not os.path.isfile(p):
        return None
    try:
        return io.open(p, encoding="utf-8", errors="replace").read().lower()
    except OSError:
        return None


def has_machinery(low):
    return any(n in low for n in MECH)


def apis_of(low):
    hits = []
    if any(n in low for n in CF_NEEDLES):
        hits.append("cloudflare")
    if any(n in low for n in GH_NEEDLES) or GIT_OUT.search(low):
        hits.append("github")
    return hits


def parse_decl(low):
    m = DECL_RE.search(low or "")
    if not m:
        return None
    d = {}
    for part in m.group(1).strip().split():
        if "=" in part:
            k, _, v = part.partition("=")
            if k in API_KEYS:
                try:
                    d[k] = int(v)
                except ValueError:
                    return None
    return d or None


def load_manifest():
    if not os.path.isfile(MANIFEST):
        return None, "manifest 不存在（先跑 r200_probe_cost_measure.py）"
    try:
        doc = json.load(io.open(MANIFEST, encoding="utf-8"))
    except (ValueError, OSError) as e:
        return None, "manifest 解析失败 %r" % (e,)
    res = doc.get("results") or {}
    if not res:
        return None, "manifest 无 results（零候选也要有文件，说明扫描跑过）"
    return res, ""


def build(gates, texts, measured):
    rows = []
    problems = []
    totals = {}
    ci_totals = {}
    for g in gates:
        low = texts.get(g["script"])
        if low is None or not has_machinery(low) or not apis_of(low):
            continue
        name = g["script"]
        m = measured.get(name)
        mcalls = (m or {}).get("calls")
        decl = parse_decl(low)
        row = {"gate": g["id"], "script": name, "apis": apis_of(low),
               "portable": g["portable"], "declared": decl, "measured": mcalls}
        if mcalls is None:
            row["state"] = "UNMEASURED"
            problems.append("%s 静态判为联网门但 manifest 里没有实测值 ⇒ 先重跑测量器" % name)
        elif mcalls.get("cloudflare", 0) == 0 and mcalls.get("github", 0) == 0:
            row["state"] = "NO_EXTERNAL_CALLS"      # 静态假阳性：只起本地子进程
        elif decl is None:
            row["state"] = "UNDECLARED"
            problems.append("%s 实测每轮 %s 次外部调用但未声明 CALLS_PER_RUN" % (name, mcalls))
        elif decl != mcalls:
            row["state"] = "MISMATCH"
            problems.append("%s 声明 %s ≠ 实测 %s ⇒ 件被改过而 manifest 未重测" % (
                name, decl, mcalls))
        else:
            row["state"] = "OK"
            for a in apis_of(low):
                n = int(decl.get(a, 0))
                totals[a] = totals.get(a, 0) + n
                if g["portable"]:
                    ci_totals[a] = ci_totals.get(a, 0) + n
        rows.append(row)
    return rows, problems, totals, ci_totals


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)

    gates = load_gates()
    texts = {g["script"]: read_script(g["script"]) for g in gates}
    measured, mwhy = load_manifest()
    print("=== 探针自成本面（r200·第 76 门：声明 ⇄ 实测对账）===")
    if measured is None:
        print("  [PROBECOST:UNVERIFIED] %s" % mwhy)
        rc = 2
        rows, problems, totals, ci_totals = [], [], {}, {}
    else:
        rows, problems, totals, ci_totals = build(gates, texts, measured)
        for r in rows:
            print("  %-26s %-22s 声明=%s 实测=%s ⇒ %s" % (
                r["gate"], "+".join(r["apis"]), r["declared"], r["measured"], r["state"]))
        n_ok = sum(1 for r in rows if r["state"] == "OK")
        n_fp = sum(1 for r in rows if r["state"] == "NO_EXTERNAL_CALLS")
        print("  门表 %d 门 ｜静态候选 %d ｜对账一致 %d ｜静态假阳性(实测0次) %d" % (
            len(gates), len(rows), n_ok, n_fp))
        print("  本机每轮最坏足迹=%s ｜CI 每轮(portable子集)=%s" % (
            json.dumps(totals, ensure_ascii=False, sort_keys=True),
            json.dumps(ci_totals, ensure_ascii=False, sort_keys=True)))
        for p in problems:
            print("  [PROBECOST:FAIL] %s" % p)
        rc = 1 if problems else 0
        if not problems:
            print("  %s %d 个联网门声明与实测一致（改了联网面不重测即 MISMATCH 判红）" % (
                TOKEN, n_ok))
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "probe-cost-v5", "readonly": True,
                       "gate_table_count": len(gates), "rows": rows,
                       "problems": problems, "worst_case_per_run": totals,
                       "ci_per_run": ci_totals, "manifest": os.path.basename(MANIFEST),
                       "note": ("口径见件头：分母=门表已注册＋有外部机械＋命中厂商标记；"
                                "以零联网实测 manifest 对账，静态假阳性不计成本。"
                                "本轮实测撞过一次 CF GraphQL 限流（Rate limiter budget "
                                "depleted），故监控自身的调用足迹必须可见。"),
                       "provenance_cmd": "python 05-exec/r200_probe_cost_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return rc


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
