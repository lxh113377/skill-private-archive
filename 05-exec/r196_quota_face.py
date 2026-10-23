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
import datetime as _dt
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


def month_start_utc(now=None):
    """本自然月起点（UTC）。单独成函数是为了可被夹具钉住。"""
    now = now or _dt.datetime.now(_dt.timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _parse_iso(s):
    if not s:
        return None
    try:
        return _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def run_minutes(runs, since):
    """对 status=completed 且有 run_started_at/updated_at 的 run，累加墙上分钟。

    返回 (minutes, counted, skipped)。skipped = 缺时间戳或非 completed 的条数，
    必须回传：覆盖度不完整时读数不得被当成「本月的全部消耗」。
    """
    mins, counted, skipped = 0.0, 0, 0
    for x in runs or []:
        a = _parse_iso(x.get("run_started_at"))
        b = _parse_iso(x.get("updated_at"))
        if x.get("status") != "completed" or not a or not b:
            skipped += 1
            continue
        if a < since:
            continue
        d = (b - a).total_seconds() / 60.0
        mins += d if d > 0 else 0.0
        counted += 1
    return round(mins, 2), counted, skipped


def fetch_runs_page(repo, page):
    rc, out = sh(["gh", "api",
                  "repos/%s/actions/runs?per_page=100&page=%d" % (repo, page)])
    if rc != 0:
        return None
    try:
        d = json.loads(out)
    except ValueError:
        return None
    return d.get("workflow_runs") or []


def read_minutes_proxy(repo, month=None, max_pages=8):
    """翻页取到本月初为止的全部 run，返回 (state, info|None, why)。

    翻页停止条件：某页最早 created_at 已早于月初，或页空/取失败。
    取失败时不得只把已取部分当全量 ⇒ 返回 UNVERIFIED 并说明覆盖不全。
    """
    since = month or month_start_utc()
    allr, complete = [], False
    for page in range(1, max_pages + 1):
        rs = fetch_runs_page(repo, page)
        if rs is None:
            return "UNVERIFIED", None, "第 %d 页取不到（限流/网络），覆盖不完整 ⇒ 不折算用量" % page
        if not rs:
            complete = True
            break
        allr += rs
        lo = min((x.get("created_at") or "") for x in rs)
        if lo and _parse_iso(lo) and _parse_iso(lo) < since:
            complete = True
            break
    else:
        return "UNVERIFIED", None, "翻满 %d 页仍未覆盖到月初 ⇒ 覆盖度不足，不折算" % max_pages
    if not allr:
        return "UNVERIFIED", None, "无任何 run 记录"
    m, counted, skipped = run_minutes(allr, since)
    gates = [x for x in allr if x.get("name") == "gates"]
    mg, cg, sg = run_minutes(gates, since)
    return "MEASURED", {"minutes_all_workflows": m, "counted": counted,
                        "skipped_no_ts": skipped, "pages": len(allr),
                        "gates_minutes": mg, "gates_counted": cg,
                        "since": since.strftime("%Y-%m-%d"),
                        "coverage_complete": bool(complete)}, ""



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--login", default="", help="缺省用 gh api user 解析")
    ap.add_argument("--repo", default="lxh113377/skill-private-archive",
                    help="代理分钟作用域仓库（额度是账号级，此处只到 repo 级）")
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

    # --- GitHub Actions 分钟数：两条独立读数，不合并 ---
    # r197 纠正 r196 的定性：官方 billing 端点确实被关停（GAP_PLATFORM 仍成立，它指的是
    # 「拿不到官方 billable 分钟与官方额度值」）；但 run 的 run_started_at / updated_at
    # 时间戳一直都在 ⇒ 「自己算这个月烧了多少墙钟分钟」其实做得到。上一轮我把两个不同
    # 命题混成一行，等于用「官方端点没了」顺带否掉「代理可测」，把缺口报大了。
    login = args.login
    if not login:
        rc, who = sh(["gh", "api", "user", "--jq", ".login"])
        login = who.strip() if rc == 0 and who.strip() else ""
    off = {"tool": "github_actions_minutes_official", "login": login}
    if not login:
        off.update({"state": "UNVERIFIED", "why": "gh 未登录或取不到 login"})
    else:
        st2, _r2, why2 = read_gh_billing(login)
        off.update({"state": st2, "why": why2})
    out_rows.append(off)

    px = {"tool": "github_actions_minutes_proxy", "repo": args.repo}
    if not login:
        px.update({"state": "UNVERIFIED", "why": "gh 未登录，翻页取不到 run"})
    else:
        st3, info3, why3 = read_minutes_proxy(args.repo)
        px.update({"state": st3, "why": why3})
        if info3:
            px.update(info3)
            px["caveat"] = (
                "墙钟分钟 != billable 分钟（GitHub 按 runner 类型与 OS 加权计费，并发 job 各计时）；"
                "作用域是本仓库 != 账号级额度；官方免费分钟数本轮未取到可靠出处"
                "（docs 页面为 JS 壳，服务端渲染取不到表格）⇒ 依 r196 自立的规矩："
                "分母无可靠出处就只报绝对值，不折算百分比。")
    out_rows.append(px)

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
        elif r["state"] == "MEASURED" and "gates_minutes" in r:
            print("  %-24s MEASURED     本月（%s 起）本仓 gates run %d 个 = %.1f 墙钟分钟；"
                  % (r["tool"], r["since"], r["gates_counted"], r["gates_minutes"]))
            print("           %-18s 全部 workflow = %.1f 分钟（计入 %d，缺时间戳 %d）｜覆盖到月初=%s"
                  % ("", r["minutes_all_workflows"], r["counted"],
                     r["skipped_no_ts"], r["coverage_complete"]))
            print("           口径声明：%s" % r.get("caveat", "")[:190])
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
