# -*- coding: utf-8 -*-
"""r331 候选健康面：需求 2 的「社区活跃度 / 维护状态」两维的**时效守卫**。

为什么需要它（一手）：r331 实测 `replacement_matrix.json` 的 937 个候选里 `pushed_at` 超 12 个月的只有 1 件、
`archived=true` 的 1 件 ⇒ 「维护状态良好」**实测成立**。但**没有任何判据会在它下次变坏时报警** ——
季度巡检若只跑替代矩阵重算，那些「当时活跃、现在停摆」的上游仓不会被单独点名（r260 已为此立过 maintenance_trim_face，
但那条只守「生产矩阵排序前有没有过滤」，不守「巡检当期的候选面健康度」）。

三态口径（逐字来自 r114 §3.1 / §4 C3-C4 的本仓既定口径，不新造）：
  · stale      = pushed_at 距今 > 365 天（r114 C4「12 个月内 pushed_at」）
  · archived   = 上游仓 archived=true（停摆）
  · restricted = license 属 copyleft/NC/UNLICENSED（r113-3 / r262 正文级覆盖口径）
"""
import argparse, datetime, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_MATRIX = os.path.join(ROOT, "06-benchmark", "quarterly_r260", "2026Q4", "replacement_matrix.json")

# 受限许可（r113-3 结案口径 + r262 正文级覆盖）——只列**已知**的，未列出的不算受限（禁猜）
RESTRICTED = ("AGPL", "GPL", "LGPL", "CC-BY-SA", "CC-BY-NC", "UNLICENSED", "NOASSERTION")


def parse_date(s):
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def license_restricted(lic):
    u = (lic or "").upper()
    if not u:
        return True    # 空/取不到 ⇒ 无可信许可 ⇒ 按受限（与 r113-3 同口径）
    return any(k in u for k in RESTRICTED)


def scan(matrix, today, pack=None):
    d = json.load(io.open(matrix, encoding="utf-8"))
    rows = d.get("rows") or []
    total = 0
    stale, arch, restricted = [], [], []
    nolic = []
    per_repo = {}
    for r in rows:
        for c in (r.get("candidates") or []):
            total += 1
            repo = c.get("repo") or "?"
            p = parse_date(c.get("pushed_at"))
            if p is None:
                nolic.append(repo)
            elif (today - p).days > 365:
                stale.append({"repo": repo, "pushed_at": str(c.get("pushed_at")), "days": (today - p).days})
            if c.get("archived"):
                arch.append({"repo": repo, "archived": True})
            if license_restricted(c.get("license")):
                u = (c.get("license") or "").upper()
                if u in ("NOASSERTION", ""):
                    g = body_grade(repo, pack) if pack is not None else "no_pack"
                    restricted.append({"repo": repo, "license": c.get("license"), "body": g})
                else:
                    # AGPL/GPL/UNLICENSED 等明牌受限：字段即证据，不必正文（正文腿只管撒谎字段面）
                    restricted.append({"repo": repo, "license": c.get("license"), "body": "api_explicit"})
            per_repo[repo] = per_repo.get(repo, 0) + 1
    return {
        "schema": "r331-candidate-health-1",
        "matrix": os.path.relpath(matrix, ROOT).replace(os.sep, "/"),
        "generated_at": d.get("generated_at"),
        "today": today.isoformat(),
        "total_candidates": total,
        "distinct_repos": len(per_repo),
        "stale": stale,
        "archived": arch,
        "restricted": restricted,
        "restricted_body_breakdown": _breakdown(restricted),
        "pushed_at_unparsable": nolic,
        "stale_rate": round(len(stale) / float(total), 4) if total else None,
    }



# r337（R331-2 兑现）：restricted 轴从「按 API 字段一刀切」升级为「正文证据分级」。
# 一手背景：R261-6 实测 GitHub 的 license.spdx_id 对 NOASSERTION 仓撒谎（dify 报 NOASSERTION、
# 正文实为 modified Apache + 商业限制条款）。r262 建了正文抓包件但 candidate_health 没消费它 ⇒
# 本门 143 条 restricted 里 86 行只有字段证据。本腿把证据分三档：body_confirmed / api_field / body_unknown。
BODY_PACK_DEFAULT = os.path.join(ROOT, "06-benchmark", "license_body_r262.json")
BODY_RESTRICTED = ("copyleft", "restricted", "noncommercial", "proprietary")


def load_body_pack(path):
    """读正文抓包件；不可得 ⇒ 返回 None（本腿自动退回字段口径并显影，R247 禁静默）。"""
    try:
        d = json.load(io.open(path, encoding="utf-8-sig"))
        return d.get("repos") or {}
    except Exception:
        return None


def body_grade(repo, pack):
    """NOASSERTION/空许可行的证据分档：body_confirmed|body_permissive|body_unknown|no_pack。"""
    if pack is None:
        return "no_pack"
    e = pack.get(repo)
    if not e:
        return "body_unknown"     # pack 里没有该仓 = 没正文证据，保守档
    cls = (e.get("license_body_class") or "").lower()
    st = (e.get("state") or "").upper()
    if st != "OK":
        return "body_unknown"
    if cls in BODY_RESTRICTED:
        return "body_confirmed"
    if cls in ("permissive", "apache-2.0", "mit", "bsd", "isc", "unlicense_note"):
        return "body_permissive"
    return "body_unknown"


def _breakdown(restricted):
    """restricted 按证据档聚合（供末行输出与报告对账）。"""
    c = {}
    for x in restricted:
        b = x.get("body") or "none"
        c[b] = c.get(b, 0) + 1
    return c

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=DEFAULT_MATRIX)
    ap.add_argument("--today", default="", help="YYYY-MM-DD；缺省取本机今天（判据复算须显式给，防随日期漂移）")
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--max-stale-rate", type=float, default=0.02,
                    help="stale 占比硬顶；默认 2%（r331 实测 0.1% ⇒ 留 20 倍余量给上游自然衰退）")
    ap.add_argument("--body-pack", dest="bp", default=BODY_PACK_DEFAULT,
                    help="正文抓包件（r262）；不可得时 restricted 腿退回字段口径并显影 no_pack")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        ok1 = license_restricted("AGPL-3.0") and not license_restricted("MIT")
        ok2 = license_restricted("") and license_restricted("NOASSERTION")
        ok3 = parse_date("2026-10-25") is not None and parse_date("garbage") is None
        print("[R331:SELFTEST] restricted_agpl_not_mit=%s empty_and_noassertion=%s date_parse=%s" % (ok1, ok2, ok3))
        return 0 if (ok1 and ok2 and ok3) else 1
    if not os.path.isfile(a.matrix):
        print("[R331:HEALTH] rc=2 UNVERIFIED 矩阵不存在: " + a.matrix)
        return 2
    today = parse_date(a.today) if a.today else datetime.date.today()
    if today is None:
        print("[R331:HEALTH] rc=2 UNVERIFIED --today 不可解析: " + a.today)
        return 2
    pack = load_body_pack(os.path.abspath(a.bp)) if a.bp else None
    doc = scan(a.matrix, today, pack)
    doc["body_pack"] = {"path": a.bp, "loaded": pack is not None, "repos_n": (len(pack) if pack else 0)}
    if doc["total_candidates"] == 0:
        print("[R331:HEALTH] rc=2 UNVERIFIED 候选面为空（禁按 0 条记绿，R247）")
        return 2
    if a.out:
        io.open(a.out, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    n = doc["total_candidates"]
    rate = doc["stale_rate"] or 0.0
    rc = 0
    if rate > a.max_stale_rate:
        rc = 1
        print("[R331:STALE-OVER] stale %d/%d = %.2f%% > 硬顶 %.2f%%：%s"
              % (len(doc["stale"]), n, rate * 100, a.max_stale_rate * 100,
                 ", ".join(x["repo"] + "(" + x["pushed_at"] + ")" for x in doc["stale"][:8])))
    _bd = doc["restricted_body_breakdown"]
    print("[R331:HEALTH] cands=%d repos=%d stale=%d(%.2f%%) archived=%d restricted=%d unparsable=%d body[confirmed=%d permissive=%d unknown=%d no_pack=%d]"
          % (n, doc["distinct_repos"], len(doc["stale"]), rate * 100,
             len(doc["archived"]), len(doc["restricted"]), len(doc["pushed_at_unparsable"]),
             _bd.get("body_confirmed", 0), _bd.get("body_permissive", 0),
             _bd.get("body_unknown", 0), _bd.get("no_pack", 0)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
