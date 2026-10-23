# -*- coding: utf-8 -*-
# r199_workers_face.py - Workers invocation count for this month (read-only).
#
# Why this exists (r199): my own r198 ledger note recorded this quota as unmeasurable for two
# reasons, and BOTH were wrong. Credentials do exist - wrangler whoami prints their path; I had
# typed xdg-config while the real directory is the dotted xdg.config, so my probe missed it.
# And the GraphQL analytics endpoint answers HTTP 200 with that same OAuth token.
# Lesson kept in the file header: never widen one measured limit (cannot mint API tokens) into a
# broader claim (analytics unreadable). Probe the real surface before writing a gap into the book.
#
# Exit: 0 measured (any value, including 0) / 2 unverified (never treated as "no usage").
# CALLS_PER_RUN: cloudflare=1 github=0   (实测：python 05-exec/r200_probe_cost_measure.py；最坏足迹含退避重试)
import json
import os
import sys
import urllib.error
import urllib.request

CRED_CANDS = [
    os.path.join(os.environ.get("APPDATA", ""), "xdg.config", ".wrangler", "config", "default.toml"),
    os.path.join(os.environ.get("APPDATA", ""), "xdg-config", ".wrangler", "config", "default.toml"),
]
ACCOUNT_TAG = "04b1466b2606b678a332fe6f26aa87ec"
GRAPHQL = "https://api.cloudflare.com/client/v4/graphql"
QUERY = ("query($accountTag: string, $a: string, $b: string) { viewer { accounts "
         "(filter: {accountTag: $accountTag}) { workersInvocationsAdaptive "
         "(limit: 100, filter: {datetime_geq: $a, datetime_leq: $b}) "
         "{ sum { requests errors } } } } }")


def oauth_token():
    # plain line scan, no regex: pick the value between the first quote pair on the line
    for path in CRED_CANDS:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            continue
        for line in txt.splitlines():
            s = line.strip()
            if not s.startswith("oauth_token"):
                continue
            parts = s.split(chr(34))
            if len(parts) >= 2 and parts[1]:
                return parts[1], path
    return "", ""


def month_window(now=None):
    import datetime as dt
    n = now or dt.datetime.now(dt.timezone.utc)
    start = n.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = n.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%S.000Z"
    return start.strftime(fmt), end.strftime(fmt)


def build_body(tok, start, end):
    payload = {"query": QUERY, "variables": {"accountTag": ACCOUNT_TAG,
                                             "a": start, "b": end}}
    return urllib.request.Request(
        GRAPHQL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "Authorization": "Bearer " + tok})


def sum_invocations(doc):
    # structure mismatch returns None, never 0 - an absent or non-numeric payload is not "no usage".
    # t4 (r199) caught my first version doing exactly that: a malformed sum yielded total=0 with
    # seen=True, which would have printed MEASURED 0 during a schema change or scope outage.
    if not isinstance(doc, dict):
        return None
    try:
        accts = doc["data"]["viewer"]["accounts"]
    except (KeyError, TypeError):
        return None
    if not isinstance(accts, list) or not accts:
        return None
    seen_dataset = False
    total = 0
    for a in accts:
        rows = (a or {}).get("workersInvocationsAdaptive")
        if not isinstance(rows, list):
            continue
        seen_dataset = True
        for grp in rows:
            s = (grp or {}).get("sum")
            if not isinstance(s, dict):
                return None
            v = s.get("requests")
            if isinstance(v, bool) or not isinstance(v, int):
                return None
            total += v
    return total if seen_dataset else None


def classify_err(doc):
    errs = (doc or {}).get("errors")
    if not errs:
        return ""
    txt = json.dumps(errs, ensure_ascii=False)
    low = txt.lower()
    if "could not access" in low or "not authorized" in low or "403" in low:
        return "凭据 scope 不足（需 account 级 analytics 读权限）"
    return "GraphQL 报错：" + txt[:150]


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    tok, src = oauth_token()
    row = {"tool": "cloudflare_workers_requests", "state": "UNVERIFIED", "why": ""}
    if not tok:
        row["why"] = "两个凭据候选路径都取不到 oauth_token（以 wrangler whoami 打印路径为准）"
    else:
        start, end = month_window()
        row["cred_path"] = src
        row["window"] = start[:10] + "~" + end[:10]
        doc = None
        try:
            with urllib.request.urlopen(build_body(tok, start, end), timeout=90) as f:
                doc = json.loads(f.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            row["why"] = "HTTP %s（%s）" % (e.code, "凭据不足" if e.code == 403 else
                                            ("限流" if e.code == 429 else "服务端"))
        except Exception as e:
            row["why"] = "网络异常 %r" % (e,)
        if doc is not None:
            why = classify_err(doc)
            if why:
                row["why"] = why
            else:
                n = sum_invocations(doc)
                if n is None:
                    row["why"] = "返回结构不符，取不到 requests（不得当作 0）"
                else:
                    row["state"] = "MEASURED"
                    row["invocations_month"] = n
    print("=== Workers 调用数（本自然月，官方 GraphQL Analytics schema）===")
    if row["state"] == "MEASURED":
        print("  MEASURED %s 次 ｜ 窗口 %s ｜ 凭据文件 %s" % (
            row["invocations_month"], row.get("window"), os.path.basename(
                os.path.dirname(os.path.dirname(os.path.dirname(row.get("cred_path", "")))))))
    else:
        print("  UNVERIFIED %s" % row["why"][:150])
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "workers-quota-v1", "readonly": True, "row": row,
                       "provenance_cmd": "python 05-exec/r199_workers_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return 0 if row["state"] == "MEASURED" else 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
