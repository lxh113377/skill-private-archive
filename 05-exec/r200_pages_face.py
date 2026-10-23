# -*- coding: utf-8 -*-
# r200_pages_face.py - 账号级 HTTP 请求量面（第 75 门）：Pages/zone 流量到底有多少。
#
# 为什么补这一面（r200）：r199 打通 Workers 调用数后，名册里 Cloudflare Pages 这一项仍只有
# 「部署可溯源」而没有流量读数 —— 而 Pages 恰恰是本仓在生产用的那个（supermarket-web.pages.dev）。
#
# 参数名不猜（本轮第三次踩同一族坑后立的硬规矩）：1d 数据集的时间过滤是
# date_geq / date_leq，由 Cloudflare GraphQL introspection 的
# AccountHttpRequests1dGroupsFilter_InputObject.inputFields 自报（实测 10 个输入字段：
# AND OR date date_geq date_gt date_in date_leq date_lt date_neq date_notin）。
# 注意它与 workersInvocationsAdaptive 的 datetime_geq/datetime_leq **不同名**，
# 官方 examples 只演示了后者 —— 照抄会把 1d 打挂（实测报 unknown arg datetime_geq）。
#
# 口径声明（刻意不折算百分比）：分子是**账号级 httpRequests1dGroups**，含该账号下所有
# zone/Pages 的 HTTP 请求；分母「10 万请求/天」是名册声称的 **Workers** 免费额度，
# 两者量纲与归属都不同 ⇒ 只报绝对值与最高单日。实测 Workers 本月调用数为 0（r199 门），
# 说明这些流量来自 Pages 静态与 zone，不是 Workers。
# CALLS_PER_RUN: cloudflare=3 github=0   (实测：python 05-exec/r200_probe_cost_measure.py；最坏足迹含退避重试)
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TOKEN_TEXT = "[QUOTA:PASS]"
# 1d 用 date（YYYY-MM-DD），不是 datetime
Q_1D = ("query($accountTag: string, $a: Date, $b: Date) { viewer { accounts"
        "(filter: {accountTag: $accountTag}) { httpRequests1dGroups(limit: 60,"
        "filter: {date_geq: $a, date_leq: $b}) { sum { requests } dimensions { date } } } } }")


def int_requests(grp):
    # 结构不符一律 None：缺字段/非数值/布尔都不得折算成 0（额度面最坏的假绿）
    if not isinstance(grp, dict):
        return None
    s = grp.get("sum")
    if not isinstance(s, dict):
        return None
    v = s.get("requests")
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def sum_days(rows):
    # 返回 (total, days, per_day|None)；任一行结构不符 ⇒ None（不得把部分当全量）
    if rows is None or not isinstance(rows, list):
        return None, None, None
    per = []
    total = 0
    for g in rows:
        v = int_requests(g)
        if v is None:
            return None, None, None
        d = ((g.get("dimensions") or {}).get("date")) if isinstance(g, dict) else None
        per.append((d, v))
        total += v
    return total, len(per), per


def unwrap_payload(doc):
    # 结构走通则返回 rows，否则 None（UNVERIFIED 而非 0）
    if not isinstance(doc, dict) or doc.get("errors"):
        return None
    try:
        accts = doc["data"]["viewer"]["accounts"]
    except (KeyError, TypeError):
        return None
    if not isinstance(accts, list) or not accts:
        return None
    rows = []
    for acct in accts:
        got = (acct or {}).get("httpRequests1dGroups")
        if got is None:
            return None
        rows.extend(got)
    return rows


def post(query, variables, token, endpoint, tries=3, sleeper=None):
    import time as _t
    sleep = sleeper or _t.sleep
    body = json.dumps({"query": query, "variables": variables}).encode()
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(endpoint, data=body, headers={
                "Content-Type": "application/json", "Accept": "application/json",
                "Authorization": "Bearer " + token})
            with urllib.request.urlopen(req, timeout=90) as f:
                return json.loads(f.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            # r200 自抓（本轮第三次同类错，前两处见报告 §41）：上一版只列 403/429，于是
            # 实测撞到的 401 掉进重试分支，最后被上层文案写成「网络/代理瞬态；与凭据无关」
            # —— 把确定性授权拒绝读成瞬态，正是我本轮刚立的规矩的违反。
            # 授权层（401/403）是确定性拒绝 ⇒ 不重试（重试只烧限流预算，正是第 76 门要防的
            # 无声增长）；429/5xx 属可重试；其余异常走网络分支。
            if e.code in (401, 403, 429):
                return {"errors": [{"message": "HTTP %s" % e.code}]}
            last = e
        except Exception as e:
            last = e
        if k + 1 < tries:
            sleep(5)
    return None


def main(argv=None):
    import argparse
    import r199_workers_face as wf
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)

    tok, src = wf.oauth_token()
    row = {"tool": "cloudflare_pages_http_requests", "state": "UNVERIFIED", "why": ""}
    if not tok:
        row["why"] = "本机 wrangler OAuth 凭据取不到（whoami 可核路径）"
    else:
        a, b = wf.month_window()
        row["window"] = a[:10] + "~" + b[:10]
        doc = post(Q_1D, {"accountTag": wf.ACCOUNT_TAG, "a": a[:10], "b": b[:10]},
                   tok, wf.GRAPHQL)
        if doc is None:
            # 走到这里只会是「连不上/无 HTTP 响应」（URLError、超时、5xx 重试耗尽）：
            # 授权类已在 post() 内以 errors 返回，不会落到这一支 ⇒ 这句才敢说不涉及凭据
            row["why"] = "GraphQL 请求未拿到 HTTP 响应（网络/代理不可达，或 5xx 重试耗尽）⇒ 不折算用量"
        elif doc.get("errors"):
            txt = json.dumps(doc["errors"], ensure_ascii=False)
            # r200 第四次自抓同一族错：我上一版写「需 wrangler login 或换 token」，是拿 401
            # 直接编出因果。实测翻盘 —— 同一 token 打 REST /accounts 得 HTTP 200，隔 20s 再打
            # GraphQL 也 200 ⇒ 这个 401（code 10000 Authentication error）是 CF GraphQL 侧
            # 偶发，凭据没死。所以文案只说事实与下一步，不断言要重新登录（误导向下一轮折腾凭据）。
            # 本件对 401 不自行重试（省预算），但 run_gates 层有「重跑仍 X ⇒ 判真红」的第二次机会。
            row["why"] = ("GraphQL 返回 401（CF 侧认证类偶发；同 token 的 REST 通路实测可用，"
                          "故不断言凭据失效）⇒ 本轮不可得，不折算用量"
                          if "401" in txt else
                          "授权被拒 HTTP 403（scope 问题）" if "403" in txt else
                          "限流（HTTP 429：CF GraphQL 预算耗尽；每轮足迹见 probe_cost_face）"
                          if "429" in txt else
                          "GraphQL 报错：" + txt[:130])
        else:
            rows = unwrap_payload(doc)
            if rows is None:
                row["why"] = "返回结构不符 ⇒ 不可得（不得当作 0）"
            else:
                total, days, per = sum_days(rows)
                if total is None:
                    row["why"] = "某行 requests 非数值 ⇒ 不可得（不得当作 0）"
                else:
                    top = sorted(per, key=lambda x: -(x[1] or 0))[:3]
                    row.update({"state": "MEASURED", "requests_total": total,
                                "days": days, "top_days": top,
                                "caveat": ("账号级 httpRequests（含该账号所有 zone/Pages 流量），"
                                           "与名册「Workers 10 万请求/天」不同量纲不同归属 ⇒ 不折算"
                                           "百分比；Workers 侧本月调用数见 workers_quota_face。")})
    print("=== Cloudflare Pages / 账号级 HTTP 请求量（r200）===")
    # 门禁 token 只在 MEASURED 时出：取不到不得带 PASS 字样（R247）
    if row["state"] == "MEASURED":
        print("  MEASURED 本月合计 %s 次 ｜ 有数据天数 %d ｜ 窗口 %s" % (
            row["requests_total"], row["days"], row.get("window")))
        print("  最高三日:", row["top_days"])
        print("  口径声明：%s" % row["caveat"])
        print("  %s" % TOKEN_TEXT)
    else:
        print("  UNVERIFIED %s" % row["why"])
    if args.out:
        doc = {"schema": "pages-http-v1", "readonly": True, "row": row,
               "provenance_cmd": "python 05-exec/r200_pages_face.py --json <件>"}
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return 0 if row["state"] == "MEASURED" else 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
