# -*- coding: utf-8 -*-
"""r196_quota_face.py — 免费层额度面（第 72 门）：名册工具的免费额度还剩多少，能不能被机器读到。

存在理由（r196 一手）：前 71 门答的是「工具有没有 / 谁在引用 / 部署可不可溯源 / CI 在不在判定」，
没有任何一面回答「**这么用下去会不会悄悄吃穿免费额度**」。免费套餐的价值恰恰在额度内，
吃穿了就不再是免费工具 —— 故把额度做成每轮可复算读数，并强制区分两种「读不到」：
  · GAP_PLATFORM：平台把该能力下线了（有官方依据，不靠加凭据解决）；
  · UNVERIFIED  ：本轮取不到数（限流 / 未登录 / 解析失败），按 R247 既不得记绿也不得记红。

三态（每个工具一行）：
  MEASURED     取到用量绝对值 ⇒ 打印绝对值；仅当额度值有名册出处时才算比例
  GAP_PLATFORM 平台能力缺口，附官方依据串
  UNVERIFIED   取不到 ⇒ 具名原因

关键实现坑（均为本机实测，不是推演）：
  1) Windows 上 wrangler 是 .CMD shim（D:\\npm-global\\wrangler.CMD，339B），
     subprocess 不带 shell=True 直接 FileNotFoundError ⇒ 必须走 shell；
  2) wrangler --json 会在 JSON 后追加 ANSI 着色的 WARNING 行，且 NO_COLOR 对其无效
     ⇒ 裸 json.loads 报「Extra data」；须先去 ANSI、再做括号平衡扫描截取数组。
用法：python 05-exec/r196_quota_face.py [--json 件]
退出：0 = 无红（含 UNVERIFIED，因为读不到不等于超限）/ 1 = 有用量超过所声明额度
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
TOKEN = "[QUOTA:PASS]"

# 额度出处 = 本仓名册（截图来源），不是 GitHub/Cloudflare 官方文档 ⇒ 只用作「已声明值」，
# 读数一律以实测绝对值为准；比例须标注其分母来自名册。
ROSTER_LIMITS = {
    "cloudflare_d1": ("5 GiB 存储", 5 * 1024 ** 3),
}

GH_BILLING_DOC = ("github.blog/changelog/2025-09-26-"
                  "product-specific-billing-apis-are-closing-down")


def sh(cmd, shell=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180, shell=shell)
        return r.returncode, ((r.stdout or "") + (r.stderr or ""))
    except Exception as e:  # noqa: BLE001
        return 90, "EXC %r" % (e,)


def first_json_array(s):
    """括号平衡扫描取第一个完整 JSON 数组（wrangler 会在其后追加告警行）。"""
    depth, start = 0, None
    for i, c in enumerate(s):
        if c == "[":
            if depth == 0:
                start = i
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0 and start is not None:
                return s[start:i + 1]
    return None


def read_d1():
    """返回 (state, rows|None, why)。rows = [{name,file_size}]。"""
    rc, raw = sh("wrangler d1 list --json", shell=True)
    if rc != 0:
        return "UNVERIFIED", None, "wrangler d1 list rc=%s（未登录/网络/限流？）" % rc
    clean = ANSI_RE.sub("", raw)
    seg = first_json_array(clean)
    if not seg:
        return "UNVERIFIED", None, "输出里取不到 JSON 数组（wrangler 形态变了）"
    try:
        rows = json.loads(seg)
    except ValueError as e:
        return "UNVERIFIED", None, "JSON 解析失败 %r" % (e,)
    if not isinstance(rows, list):
        return "UNVERIFIED", None, "JSON 顶层不是数组"
    return "MEASURED", rows, ""


def read_gh_billing(login):
    """GitHub Actions 分钟数额度：实测已被平台下线 ⇒ GAP_PLATFORM（有官方依据）。"""
    rc1, out1 = sh(["gh", "api", "users/%s/settings/billing" % login])
    rc2, out2 = sh(["gh", "api", "users/%s/settings/billing/actions" % login])
    m1 = re.search(r'"status":\s*"?(\d{3})', out1)
    m2 = re.search(r'"status":\s*"?(\d{3})', out2)
    s1 = m1.group(1) if m1 else ("rc%d" % rc1)
    s2 = m2.group(1) if m2 else ("rc%d" % rc2)
    # 官方 changelog（2025-09-26）明写关停 Actions/Packages/共享存储的产品级 billing API
    if rc1 != 0 and rc2 != 0:
        return "GAP_PLATFORM", None, ("两态端点皆不可用（%s / %s），官方已于 2025-09-26 关停产品级 "
                                      "billing API：%s" % (s1, s2, GH_BILLING_DOC))
    rows = {}
    try:
        rows = json.loads(out2) if out2.strip().startswith("{") else {}
    except ValueError:
        rows = {}
    return "MEASURED", rows, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--login", default="", help="缺省用 gh api user 解析")
    args = ap.parse_args()

    out_rows = []
    over = 0

    # --- Cloudflare D1 ---
    st, rows, why = read_d1()
    entry = {"tool": "cloudflare_d1", "state": st, "why": why}
    if st == "MEASURED":
        tot = sum(int(r.get("file_size") or 0) for r in rows)
        lim_name, lim = ROSTER_LIMITS["cloudflare_d1"]
        entry.update({"instances": len(rows), "bytes": tot,
                      "mib": round(tot / 1048576.0, 2),
                      "limit_label": lim_name, "limit_bytes": lim,
                      "pct_of_roster_limit": round(100.0 * tot / lim, 3),
                      "note": "分母为名册声称值（截图来源），非 CF 官方文档；"
                              "num_tables 实测恒 0 不可信，不得据此读成「库是空的」"})
        if tot > lim:
            over += 1
    out_rows.append(entry)

    # --- GitHub Actions 分钟数 ---
    login = args.login
    if not login:
        rc, who = sh(["gh", "api", "user", "--jq", ".login"])
        login = who.strip() if rc == 0 and who.strip() else ""
    g = {"tool": "github_actions_minutes", "login": login}
    if not login:
        g.update({"state": "UNVERIFIED", "why": "gh 未登录或取不到 login"})
    else:
        st2, rows2, why2 = read_gh_billing(login)
        g.update({"state": st2, "why": why2})
    out_rows.append(g)

    doc = {"schema": "quota-face-v1", "readonly": True,
           "generated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
           "provenance_cmd": "python 05-exec/r196_quota_face.py --json <件>",
           "rows": out_rows, "over_limit_count": over}

    print("=== 免费层额度面（r196）===")
    for r in out_rows:
        if r["state"] == "MEASURED" and "bytes" in r:
            print("  %-24s MEASURED     实例 %d ｜ 合计 %s MiB ｜ 名册额度 %s ⇒ 已用 %.3f%%"
                  % (r["tool"], r["instances"], r["mib"], r["limit_label"],
                     r["pct_of_roster_limit"]))
        elif r["state"] == "GAP_PLATFORM":
            print("  %-24s GAP_PLATFORM %s" % (r["tool"], r["why"][:150]))
        elif r["state"] == "MEASURED":
            print("  %-24s MEASURED     %s" % (r["tool"], json.dumps(r, ensure_ascii=False)[:150]))
        else:
            print("  %-24s UNVERIFIED   %s" % (r["tool"], r["why"][:150]))
    print("-" * 72)
    n_gap = sum(1 for r in out_rows if r["state"] == "GAP_PLATFORM")
    n_unv = sum(1 for r in out_rows if r["state"] == "UNVERIFIED")
    doc["gap_platform_count"] = n_gap
    doc["unverified_count"] = n_unv
    if over:
        print("[QUOTA:FAIL] 有用量超过名册声称额度的工具 %d 个" % over)
        rc_exit = 1
    else:
        print("%s 实测 %d 项｜平台缺口 %d 项｜取不到 %d 项（取不到不等于超限，R247）"
              % (TOKEN, sum(1 for r in out_rows if r["state"] == "MEASURED"), n_gap, n_unv))
        rc_exit = 0
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return rc_exit


if __name__ == "__main__":
    sys.exit(main())
