# -*- coding: utf-8 -*-
# r200_cf_introspect_probe.py - 让 Cloudflare GraphQL 自报参数名（把「不猜」这件事做成可复算动作）。
#
# 存在理由（r200）：本轮我照官方 examples 给 1d 数据集写了 datetime_geq，实测 unknown arg；
# 上一轮我连猜 sinceDate / since / until 三次全错。改成 introspection 后**一个请求**就拿到
# 准确字段名。这条路径比任何单个读数都值钱，所以固化成常驻件：任何一轮都能重算「参数名到底是什么」，
# 而不是留在报告里当历史说法。
#
# 只读：仅 __schema / __type introspection，不改任何云端配置。
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def gql(query, token, endpoint, tries=4, sleeper=None):
    # 本轮实测 CF 侧偶发 SSLEOFError / URLError（本机走代理链）⇒ 退避重试；
    # 但授权层（401/403）是确定性拒绝，重试只烧限流预算 ⇒ 立即抛出（r200 自抓：
    # 上一版这里对所有异常一律重试，401 被白打 4 次）。
    # 重试耗尽则抛出，由上层归 UNVERIFIED；绝不得把「取不到」当成「参数名不存在」。
    import urllib.error
    import time as _t
    sleep = sleeper or _t.sleep
    body = json.dumps({"query": query}).encode()
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(endpoint, data=body, headers={
                "Content-Type": "application/json", "Accept": "application/json",
                "Authorization": "Bearer " + token})
            with urllib.request.urlopen(req, timeout=90) as f:
                return json.loads(f.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise
            last = e
            if k + 1 < tries:
                sleep(5)
        except Exception as e:
            last = e
            if k + 1 < tries:
                sleep(5)
    raise last


def main(argv=None):
    import argparse
    import r199_workers_face as wf
    ap = argparse.ArgumentParser()
    ap.add_argument("--contains", default="HttpRequests1dGroupsFilter",
                    help="筛选 INPUT_OBJECT 名含此子串（默认 1d filter）")
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)

    tok, src = wf.oauth_token()
    res = {"state": "UNVERIFIED", "why": "", "type_count": None, "inputs": {}}
    if not tok:
        res["why"] = "本机 wrangler OAuth 凭据取不到"
    else:
        try:
            doc = gql("{ __schema { types { name kind } } }", tok, wf.GRAPHQL)
            types = (((doc.get("data") or {}).get("__schema") or {}).get("types") or [])
            res["type_count"] = len(types)
            cands = [t["name"] for t in types
                     if t.get("kind") == "INPUT_OBJECT" and args.contains in (t["name"] or "")]
            for name in cands[:4]:
                d2 = gql('{ __type(name: "%s") { inputFields { name } } }' % name,
                         tok, wf.GRAPHQL)
                fields = [x["name"] for x in (((d2.get("data") or {}).get("__type") or
                                               {}).get("inputFields") or [])]
                res["inputs"][name] = fields
            if res["type_count"] and res["inputs"]:
                res["state"] = "MEASURED"
            else:
                res["why"] = "introspection 返回空（CF 只暴露部分类型），不得据此断言参数名"

        except urllib.error.HTTPError as e:
            # 只报码与已证事实，不编因果（r200：401 曾被我写成「凭据问题」，实测同 token
            # REST 通路 200、隔 20s GraphQL 也 200 ⇒ CF GraphQL 侧偶发）。见 r200_pages_face 注释。
            res["why"] = ("HTTP %s（CF GraphQL 认证类偶发，同 token 的 REST 通路可用；不据此断言凭据失效）"
                          % e.code if e.code in (401, 403) else
                          "HTTP %s 限流（预算耗尽）" % e.code if e.code == 429 else
                          "HTTP %s" % e.code)
        except Exception as e:
            res["why"] = "调用失败 %r（网络/代理不可达类；授权类已单列，不混作瞬态）" % (e,)
    print("=== Cloudflare GraphQL 参数名自报（r200）===")
    if res["state"] == "MEASURED":
        print("  类型总数 %d ｜命中候选 %d 个" % (res["type_count"], len(res["inputs"])))
        for k, v in res["inputs"].items():
            print("  %-50s 输入字段 %d: %s" % (k, len(v), v[:12]))
        print("  [PROBE:READONLY] introspection 完成（探针非门，不出门禁 token）")
    else:
        print("  UNVERIFIED %s" % res["why"][:160])
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "cf-introspect-v1", "readonly": True, "result": res,
                       "provenance_cmd": "python 05-exec/r200_cf_introspect_probe.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return 0 if res["state"] == "MEASURED" else 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
