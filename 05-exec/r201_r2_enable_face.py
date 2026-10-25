# -*- coding: utf-8 -*-
# r201_r2_enable_face.py - R2 启用状态面（第 77 门）：带对照组的四路探测，三态强制分开。
#
# 存在理由（r201 一手）：R2 是名册里唯一「代码备好但服务开不了」的项，r163 时代记成
# GAP_SERVICE（wrangler 五路 403/404/500 + code 10042）。本轮重探发现当时那条结论
# 建立在「只试过 wrangler」上，而 r199/r200 已证明同一 OAuth token 能查 CF GraphQL ——
# 于是要分清：R2 打不开到底是 ①服务真没启用 ②客户端/wrangler 的问题 ③凭据失效。
# 三者处置完全不同（①是平台/人工缺口，②换工具即可，③要重登），把 ②③ 误记成 ①
# 会让这一项永远不再被重探。
#
# 关键设计：**必须带活性对照组**。只看到 r2/buckets 403 就下结论，正是本轮我第四次
# 犯的那族错（把 401 编成「要重新登录」）。所以本件同时打一个已知可用的只读端点
# /accounts/<ACC>：它 200 ⇒ 凭据活着，此时 r2 的 403 才能归因给「R2 未启用」；
# 它非 200 ⇒ 本件整体 UNVERIFIED，不得据此断言 R2 状态。
#
# 四路（每路都记 HTTP 码与 CF error code，不猜）：
#   A /accounts/<ACC>                     活性对照（期望 200）
#   B /accounts/<ACC>/r2/buckets          R2 是否可用（10042 = 需在 Dashboard 启用）
#   C /accounts/<ACC>/subscriptions       能否用 API 订阅 R2 免费计划（10000 = scope 不足）
#   D wrangler r2 bucket list             客户端侧同码核对（排除「只有 REST 被封」）
#
# 三态：MEASURED（B 成功且有桶/确为空桶）/ GAP_SERVICE（B=10042 且 A=200 且 C 不可订阅）
#       / UNVERIFIED（A 非 200，或任一关键路取不到响应 ⇒ 不猜）
# 退出：0 = 判定成立（MEASURED 或 GAP_SERVICE 有对照背书）/ 2 = UNVERIFIED。
# 只读：GET 与只读 CLI，不创建桶、不改任何云端配置。
# CALLS_PER_RUN: cloudflare=3 github=0   (实测：python 05-exec/r200_probe_cost_measure.py；断网早退后最坏足迹含退避重试)
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TOKEN_TEXT = "[R2FACE:JUDGED]"
API = "https://api.cloudflare.com/client/v4/"


def get(path, token, tries=3, sleeper=None):
    import time as _t
    sleep = sleeper or _t.sleep
    req = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token, "Content-Type": "application/json"})
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as f:
                body = json.loads(f.read().decode("utf-8", "replace"))
                return f.status, body, ""
        except urllib.error.HTTPError as e:
            # 授权/服务类码是确定性答复：不重试（重试只烧预算，见 probe_cost_face）
            try:
                body = json.loads(e.read().decode("utf-8", "replace"))
            except Exception:
                body = {}
            if e.code in (401, 403, 404, 429):
                return e.code, body, ""
            last = e
        except Exception as e:
            last = e
        if k + 1 < tries:
            sleep(4)
    return 0, {}, ("网络异常 %r" % (last,)) if last else "未知失败"


def cf_code(body):
    for e in ((body or {}).get("errors") or []):
        c = e.get("code")
        if c is not None:
            return int(c)
    return None


def wrangler_r2():
    try:
        # r221 修一：原命令带 --json，但 wrangler 4.152 的 **r2 bucket list 子命令**不认它，
        # 直接以「Unknown argument: json」退出 1 —— 这条被件头称为「客户端侧同码核对」，
        # 实际从未核对过任何东西：参数错误被当成了服务态证据（结论碰巧对，证据是假的）。
        # ⚠ 支持与否按**子命令**分，别一概而论（r221 实测：wrangler d1 list --json 与
        #    wrangler pages project list --json 都 rc=0 且吐 JSON 数组，只有 r2 不认）。
        #    故这里去掉 --json 走文本态，绝不可据此去删 d1/pages 那两路（那会拆了门）。
        r = subprocess.run("wrangler r2 bucket list", capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=180, shell=True)
        return r.returncode, ((r.stdout or "") + (r.stderr or ""))
    except Exception as e:
        return 90, "EXC %r" % (e,)


def judge(a, b, c, wr_rc, wr_out):
    """a/b/c = (status, body, why)。返回 (state, why, detail)。"""
    a_code = a[1].get("success") if isinstance(a[1], dict) else None
    if a[0] != 200 or a_code is not True:
        return ("UNVERIFIED", "活性对照 /accounts 非 200（HTTP %s, code %s）⇒ 凭据层不可用，"
                              "不得据此断言 R2 状态" % (a[0], cf_code(a[1])), {})
    detail = {"control": "alive", "buckets_http": b[0], "buckets_code": cf_code(b[1]),
              "subs_http": c[0], "subs_code": cf_code(c[1]),
              "wrangler_rc": wr_rc, "wrangler_code": None}
    # r221 修二：上一版的正则字面量是 JS 写 Python 时把反斜杠吃掉留下的死正则
    # （"s*:s*(d+)" 里的 \s \d 丢了转义），永远匹配不上 ⇒ 产物 wrangler_code 恒为 null，
    # 看起来像「wrangler 没给码」，实际是解析器坏了。现按 wrangler 真实文案
    # 「[code: 10042]」取值，并把用法错误单独标成不可用证据。
    if re.search("Unknown argument|unexpected argument", wr_out or "", re.I):
        detail["wrangler_usable"] = False
    else:
        detail["wrangler_usable"] = True
        mm = re.search(r"\[code:\s*(\d+)\]", wr_out or "")
        if mm:
            detail["wrangler_code"] = int(mm.group(1))
    if b[0] == 200 and isinstance(b[1], dict) and b[1].get("success"):
        rows = b[1].get("result") or []
        return ("MEASURED", "R2 可用（桶数 %d）⇒ 名册 R2 项可接落地代码" % len(rows), detail)
    if cf_code(b[1]) == 10042:
        # 10042 = 需在 Dashboard 启用；再确认 API 订阅这条路也不通，才敢记 GAP_SERVICE
        if cf_code(c[1]) in (10000, 10042) or c[0] in (403, 404):
            return ("GAP_SERVICE", "R2 未在账号启用（10042），且 API 订阅这条路也不通"
                                  "（subscriptions HTTP %s / code %s）⇒ 属平台+人工条款同意缺口，"
                                  "非凭据缺口（对照 /accounts=200 已证凭据活着）" % (
                                      c[0], cf_code(c[1])), detail)
        return ("UNVERIFIED", "buckets=10042 但订阅通路未定（HTTP %s/code %s）⇒ 不猜" % (
            c[0], cf_code(c[1])), detail)
    return ("UNVERIFIED", "buckets 返回 HTTP %s / code %s，非已知判定形态 ⇒ 不猜" % (
        b[0], cf_code(b[1])), detail)


def main(argv=None):
    import argparse
    import r199_workers_face as wf
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    tok, _src = wf.oauth_token()
    ACC = wf.ACCOUNT_TAG
    if not tok:
        print("=== R2 启用状态面（r201）===")
        print("  UNVERIFIED 本机 wrangler OAuth 凭据取不到（whoami 可核路径）")
        return 2
    # 对照先行且短路：A 拿不到 200 就整体不可判，此时再打 B/C 只会白烧限流预算
    # （r201：第 76 门首跑就抓到我声明 4 / 实测 10 —— 差值正是「全断网时三个 GET 各重试
    #  3 次」。修法不是把数字改成 10，而是修行为：无对照即早退。正常路径 4 次不变，
    #  断网路径从 10 降到 3；这也让「凭据死了还去戳 R2」这种无意义请求消失。）
    a = get("accounts/" + ACC, tok)
    if a[0] != 200 or not (isinstance(a[1], dict) and a[1].get("success")):
        b = (0, {}, "未调用（对照未通过即早退，省预算）")
        c = (0, {}, "未调用")
        wr_rc, wr_out = 0, ""
    else:
        b = get("accounts/" + ACC + "/r2/buckets", tok)
        c = get("accounts/" + ACC + "/subscriptions", tok)
        wr_rc, wr_out = wrangler_r2()
    state, why, detail = judge(a, b, c, wr_rc, wr_out)
    print("=== R2 启用状态面（r201·带活性对照组）===")
    print("  A /accounts        HTTP %s success=%s code=%s   ← 活性对照" % (
        a[0], (a[1] or {}).get("success") if isinstance(a[1], dict) else None,
        cf_code(a[1])))
    print("  B /r2/buckets      HTTP %s code=%s" % (b[0], cf_code(b[1])))
    print("  C /subscriptions   HTTP %s code=%s" % (c[0], cf_code(c[1])))
    print("  D wrangler r2 list rc=%s code=%s" % (wr_rc, detail.get("wrangler_code")))
    print("  判定：%s ｜ %s" % (state, why))
    if state == "MEASURED":
        print("  " + TOKEN_TEXT)
    elif state == "GAP_SERVICE":
        print("  " + TOKEN_TEXT + "（GAP_SERVICE 也是判定成立：带对照证据，非取不到）")
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "r2-enable-v1", "readonly": True, "state": state,
                       "why": why, "detail": detail,
                       "paths": {"accounts": [a[0], cf_code(a[1])],
                                 "buckets": [b[0], cf_code(b[1])],
                                 "subscriptions": [c[0], cf_code(c[1])],
                                 "wrangler": [wr_rc, detail.get("wrangler_code")]},
                       "note": ("三态里 GAP_SERVICE 必须有 /accounts=200 背书，否则降级为 "
                                "UNVERIFIED —— 防止把「凭据失效」误记成「平台没开通」，"
                                "那会让这一项永远不再被重探。"),
                       "provenance_cmd": "python 05-exec/r201_r2_enable_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return 0 if state in ("MEASURED", "GAP_SERVICE") else 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
