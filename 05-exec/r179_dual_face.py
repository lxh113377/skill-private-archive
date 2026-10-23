# -*- coding: utf-8 -*-
"""r179_dual_face.py - Cloudflare Pages 部署面的可追溯性 + 镜像内容一致性.

存在理由（r178/r179 一手实测）：焚诀 Global 与超市 web 都用了 Cloudflare Pages，而
wrangler pages project list 实测两个项目 Git Provider = No => push main 不会自动重部署
CF 侧（r179 实测 deployment_trigger.type 就是 ad_hoc）。r178 的脱钩缺陷（CF Production
的 source 指向 GitHub 已不存在的孤儿 commit a60aa83）是靠手工排查发现的；没有面看守，
下次 force-push 会再犯且没人知道。第 65 门只答「工具有没有」、第 67 门只答「谁在引用」，
都没答「用出来的部署面是否可溯源、镜像是否与主站一致」。

两类线必须分开判（r179 按权威口径改对，见下「架构误判自抓」）：
  kind=mirror  两面是同一份产物（hub：CF 镜像 = GH project page）=> 必须 sha256 逐字节相同。
  kind=distinct 两端是**不同前端**（超市：CF=管理后台+API，GH=微信顾客端，且 GH 侧由
               独立仓 lxh113377/lxh113377.github.io 发布）=> 只要求各自在线，**禁比内容**。

判据（缺一不判绿）：
  A 可追溯（两类都要）：CF 最新 Production 部署的 commit_hash 在 GitHub 远端实际可达
    （gh api 命中）。「非空即绿」不算 - 孤儿 commit 正是非空的。
  B 镜像对齐（仅 mirror）：同路径 CF 与 GH 响应体 sha256 相同。不看时间戳 - r178 实测
    「CF 落后 GH 6 天」是元数据假信号，两面 sha 其实相同。
  C 取数诚实：任一路 HTTP 失败 / 取不到 commit_hash / gh 不可达 => UNVERIFIED，禁折算成通过。

r179 自抓四处（首跑即错，全是「猜」出来的）：
  1) CF API 的 source 字段实测为 **null**；commit 实际在
     deployment_trigger.metadata.commit_hash。首跑读 source => 恒「取不到」。
  2) CF API URL 用了 TIERS 的 key hub，而项目名实为 global-memory-hub => 404。
     现用显式 cf_project 字段，并由 t8/t9 双腿盯住。
  3) 超市 GH 侧照抄 hub 的 project-page 模式拼出 lxh113377.github.io/supermarket-web，
     实测 **404**；真实形态是用户站根 lxh113377.github.io。
  4) **架构误判**：把超市当成「CF/GH 同产物」做 sha 比对，实测报 DRIFT - 但差异只有
     两个 asset 文件名（index-25Md9VAM.js vs index-DNSM587E.js，长度同为 2284B）。
     查权威 chaoshi-web-deploy 才知两端是**不同前端**，本来就该不同。判据错会把正常的
     异构报成漂移。现按 kind 分流，distinct 面不比内容。

取值：python 05-exec/r179_dual_face.py [--json out.json] [--selftest]
退出码：0 = 全部可溯源（且 mirror 面一致）；1 = 脱钩或镜像漂移；2 = UNVERIFIED。
"""

# CALLS_PER_RUN: cloudflare=2 github=0   (实测：python 05-exec/r200_probe_cost_measure.py；最坏足迹含退避重试)  # (未归类进程调用 4)
import argparse
import hashlib
import io
import json
import os
import shutil
import re
import subprocess
import sys
import urllib.error
import urllib.request

CACHEBUST = "?v=r180"
TOKEN_RE = re.compile(r'oauth_token\s*=\s*"([^"]+)"')
HEX_RE = re.compile(r'^[0-9a-f]{7,40}$')
CF_ACCOUNT_ID = "04b1466b2606b678a332fe6f26aa87ec"

# 双线名册。所有 URL/字段均由 r179/r180 实测钉死，禁按模式猜。
TIERS = {
    "hub": {
        "kind": "mirror",
        "cf_project": "global-memory-hub",
        "cf_base": "https://global-memory-hub.pages.dev",
        "gh_base": "https://lxh113377.github.io/global-memory-hub",
        # CF 产物由哪个仓的提交构建（追溯对账仓）= 与 GH 侧同仓（hub 双线同源）
        "cf_trace_repo": "lxh113377/global-memory-hub",
        "paths": ["/", "/console/"],
    },
    "supermarket": {
        "kind": "distinct",
        "cf_project": "supermarket-web",
        "cf_base": "https://supermarket-web.pages.dev",
        "gh_base": "https://lxh113377.github.io",
        # r181 自抓：GH 侧仓是 lxh113377.github.io，但**超市 CF 产物来自 supermarket-web 仓**
        #   （实测 378c826 在 supermarket-web rc=0、在 lxh113377.github.io rc=422）。
        #   追溯必须比对**产出该 CF 部署的仓**，不是对端在线仓。
        "cf_trace_repo": "lxh113377/supermarket-web",
        "paths": ["/"],
    },
}


def sha12(b):
    return hashlib.sha256(b).hexdigest()[:12]


def commit_hash_of(deploy):
    """CF 部署对象里取 commit hash。r179 实测 source 为 null，真值在
    deployment_trigger.metadata.commit_hash；两处都兜，但优先 trigger。"""
    dt = (deploy or {}).get("deployment_trigger") or {}
    md = dt.get("metadata") or {}
    return (md.get("commit_hash") or deploy.get("source") or "").strip()


def compare_tier(label, cf_fetch, gh_fetch, production_deploy_of, gh_commit_exists):
    """纯函数：四个取数器可注入 => 夹具能喂假数据做双向验与变异验。"""
    cfg = TIERS[label]
    kind = cfg["kind"]
    rows, bad, unver = [], [], []
    # B 镜像对齐：仅 mirror 面比内容。三分支显式，未知 kind 走 else 判 UNVERIFIED
    #   （r180 t11 抓到：原实现把未知 kind 静默当 distinct，一旦写错就漏检漂移）
    if kind == "mirror":
        for p in cfg["paths"]:
            try:
                cb = cf_fetch(cfg["cf_base"] + p + CACHEBUST)
                gb = gh_fetch(cfg["gh_base"] + p + CACHEBUST)
            except Exception as e:
                unver.append("%s: %s" % (p, type(e).__name__))
                continue
            same = sha12(cb) == sha12(gb)
            rows.append({"path": p, "cf_sha": sha12(cb), "gh_sha": sha12(gb),
                         "cf_bytes": len(cb), "gh_bytes": len(gb), "same": same})
            if not same:
                bad.append("%s CF=%s(%dB) GH=%s(%dB) 镜像内容漂移" % (
                    p, sha12(cb), len(cb), sha12(gb), len(gb)))
    elif kind == "distinct":
        # 不同前端（超市 CF=管理后台+API、GH=微信顾客端）只验各自在线，禁比内容
        for side, base in (("cf", cfg["cf_base"]), ("gh", cfg["gh_base"])):
            try:
                b = (cf_fetch if side == "cf" else gh_fetch)(base + "/" + CACHEBUST)
                rows.append({"side": side, "bytes": len(b), "sha": sha12(b), "up": True})
            except Exception as e:
                unver.append("%s: %s" % (side, type(e).__name__))

    else:
        bad.append("kind=%r 既不是 mirror 也不是 distinct ⇒ 拒绝默认放行" % kind)

    # A 可追溯：两类都必须有可溯源的 commit_hash
    try:
        dep = production_deploy_of(label) or {}
        src = commit_hash_of(dep)
        trig = (dep.get("deployment_trigger") or {}).get("type") or "?"
    except Exception as e:
        src, trig = "", "ERR"
        unver.append("cf_deploy: %s" % type(e).__name__)
    if HEX_RE.match(src):
        try:
            src_state = "PINNED" if gh_commit_exists(cfg["cf_trace_repo"], src) else "ORPHAN"
        except Exception as e:
            src_state = "UNVERIFIED"
            unver.append("gh_probe: %s" % type(e).__name__)
    else:
        src_state = "UNVERIFIED"
    if src_state == "ORPHAN":
        bad.append("CF Production commit_hash %s 在 %s 远端不存在（脱钩）" % (src, cfg["cf_trace_repo"]))
    elif src_state == "UNVERIFIED":
        bad.append("CF Production 取不到可溯源的 commit_hash（当前 %r）" % (src or ""))

    if kind not in ("mirror", "distinct"):
        verdict = "UNVERIFIED"   # 名册写错 ⇒ 不许静默放行（r180 t11）
    elif bad:
        verdict = "DRIFT" if src_state != "UNVERIFIED" else "UNVERIFIED"
    elif unver:
        # r181 自抓：原实现只在「行全空」时才 UNVERIFIED，于是 distinct 面单侧 HTTP 失败
        #   仍判 OK（尾行出现 (取数失败) 却 PASS）—— 与本文档判据 C「任一路失败即 UNVERIFIED」
        #   直接矛盾。判据与实现不一致时以**判据**为准，改为 fail-closed。
        verdict = "UNVERIFIED"
    else:
        verdict = "OK"
    return {"label": label, "kind": kind, "cf_project": cfg["cf_project"],
            "rows": rows, "verdict": verdict, "cf_commit": src or "(取不到)",
            "trigger_type": trig, "source_state": src_state,
            "cf_trace_repo": cfg["cf_trace_repo"],
            "problems": bad, "fetch_errors": unver}


def _request(url, headers=None, timeout=30, tries=3):
    """带 429 退避的请求。r180 实测：本门加诊断脚本连打十几次 CF API，撞出
    HTTP 429 code 10429 Rate limited（以及被限流伪装成的 401 code 10000）。
    限流是临时态，与「工具不可用」两回事 => 必须退避重试，重试仍败才如实 UNVERIFIED。"""
    import time
    hdr = {"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
    if headers:
        hdr.update(headers)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429 and i < tries - 1:
                time.sleep(3 * (i + 1))
                continue
            raise
    raise last


def _http(url):
    return _request(url)


def _cf_token():
    cfg = os.path.join(os.path.expandvars("%APPDATA%"), "xdg.config",
                       ".wrangler", "config", "default.toml")
    m = TOKEN_RE.search(io.open(cfg, encoding="utf-8").read())
    if not m:
        raise RuntimeError("wrangler oauth_token 取不到")
    return m.group(1)


# CLI 表格用 Unicode 框线 U+2502 而非 ASCII |（r180 首跑只认 | => 恒解析不到）。
ROW_RE = re.compile(r'[\u2502|]\s*([0-9a-f-]{36})\s*[\u2502|]\s*Production\s*[\u2502|]\s*([^|]*?)\s*[\u2502|]\s*([0-9a-f]{7,40})\s*[\u2502|]')


def _cf_production_deploy(label):
    """取 CF 最新 Production 部署的 commit。**官方 CLI 优先**（r180 自我一致性修正）：
    r173 刚在 win-toolchain-pitfalls 立了 §9.11「写裸 API 封装前先 wrangler --help 看官方
    有没有」，本轮却又先写了裸 API —— 结果被自己连打十几次撞到 HTTP 429/401 而整面
    UNVERIFIED；而 wrangler pages deployment list 实测 rc=0 直接给出 Source 列。
    输出形状校验（r163 教训：rc=0 也可能回帮助文本）：必须解析出 36 位 uuid + hex Source，
    且首列 uuid 与 short_id 前缀一致，否则 raise => UNVERIFIED，禁读成「没有部署」。"""
    proj = TIERS[label]["cf_project"]
    # §9.1 坑：Windows 上 subprocess 传裸名 "wrangler" 会 FileNotFoundError
    #   （CreateProcess 不补扩展名；本机真体是 D:\npm-global\wrangler.CMD）。
    #   取 shutil.which 的绝对路径，并按 §9.1 验非零字节，防 0 字节残件伪装成「可用」。
    import shutil
    exe = shutil.which("wrangler") or shutil.which("wrangler.cmd")
    if not exe:
        raise RuntimeError("wrangler 不在 PATH（取不到面，不等于没有部署）")
    if os.path.getsize(exe) == 0:
        raise RuntimeError("wrangler 解析到 0 字节残件 %s（§9.1 形态）" % exe)
    env = dict(os.environ)
    env["NO_COLOR"] = "1"
    r = subprocess.run([exe, "pages", "deployment", "list", "--project-name", proj],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180, env=env)
    blob = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        raise RuntimeError("wrangler rc=%s %s" % (r.returncode, blob[:80]))
    ms = ROW_RE.findall(blob)
    if not ms:
        raise RuntimeError("CLI 无可解析的 Production 行（形状校验失败）")
    uuid, branch, sha = ms[0]
    return {"environment": "production", "id": uuid,
            "deployment_trigger": {"type": "cli",
                                   "metadata": {"commit_hash": sha, "branch": branch}}}


# 只有这些签名才是「commit 确实不存在」的定论；其余 rc!=0 一律不可判定。
ABSENT_MARKS = ("No commit found", '"status":422', '"status": 422')


def _gh_commit_exists(repo, sha):
    """定论式三态：存在 True / 确证不存在 False / **不可判定则 raise**（→ UNVERIFIED）。

    r184 自抓（假红根因）：原实现只写 returncode == 0，于是 gh 超时、限流、网络失败、
    登录态抖动统统被算成「commit 不存在」⇒ 判据自己造成假脱钩红。实测复现：同一
    commit 5106dac 单独跑 PINNED、进全量门禁跑 ORPHAN。「调用失败」与「取到否值」
    必须分开（r163 反向假绿同族）。另按 §9.1 走绝对路径 + 验非零字节，防 PATH 序漂移
    把真 gh 换成空壳/同名第三方件。"""
    import shutil
    exe = shutil.which("gh") or shutil.which("gh.exe")
    if not exe:
        raise RuntimeError("gh 不在 PATH（不等于 commit 不存在）")
    if os.path.getsize(exe) == 0:
        raise RuntimeError("gh 解析到 0 字节残件 %s（§9.1 形态）" % exe)
    r = subprocess.run([exe, "api", "repos/%s/commits/%s" % (repo, sha), "--jq", ".sha"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=90)
    if r.returncode == 0:
        return True
    blob = (r.stderr or "") + (r.stdout or "")
    if any(k in blob for k in ABSENT_MARKS):
        return False
    raise RuntimeError("gh 探测失败（非定论）: %s" % blob[:80])


def run_all():
    return [compare_tier(k, _http, _http, _cf_production_deploy, _gh_commit_exists)
            for k in sorted(TIERS)]


def _dep(hash_v, trig="ad_hoc"):
    return {"deployment_trigger": {"type": trig, "metadata": {"commit_hash": hash_v}},
            "source": None, "environment": "production"}


def selftest():
    results = []
    A = b"<html>same body</html>"

    def cf_ok(u):
        return A

    def gh_ok(u):
        return A

    def gh_drift(u):
        return b"<html>OTHER body</html>"

    def run(name, cond, detail=""):
        results.append((name, bool(cond)))
        print(("PASS " if cond else "FAIL ") + name + ("  " + detail if detail else ""))

    t = compare_tier("hub", cf_ok, gh_ok, lambda l: _dep("abc1234"), lambda r, s: True)
    run("t1 mirror 两面同 + commit 可达 => OK",
        t["verdict"] == "OK" and t["source_state"] == "PINNED", t["verdict"])

    t = compare_tier("hub", cf_ok, gh_drift, lambda l: _dep("abc1234"), lambda r, s: True)
    run("t2 mirror 两面内容不同 => DRIFT", t["verdict"] == "DRIFT")

    t = compare_tier("hub", cf_ok, gh_ok, lambda l: _dep("a60aa83"), lambda r, s: False)
    run("t3 commit 不可达 => 抓到 r178 脱钩形态",
        t["source_state"] == "ORPHAN" and t["verdict"] == "DRIFT", str(t["problems"])[:56])

    # r180 真实形态：supermarket 两端不同产物，内容不同**不该**判漂移
    t = compare_tier("supermarket", cf_ok, gh_drift, lambda l: _dep("abc1234"),
                     lambda r, s: True)
    run("t4 distinct 两端内容不同 => 不判漂移（异构是正常的）",
        t["verdict"] == "OK", t["verdict"])

    def boom(u):
        raise urllib.error.URLError("net down")

    t = compare_tier("supermarket", boom, boom, lambda l: _dep("abc1234"), lambda r, s: True)
    run("t5 任一路取不到数 => UNVERIFIED（判据 C：fail-closed，禁报 OK）",
        t["verdict"] == "UNVERIFIED" and len(t["fetch_errors"]) == 2,
        "distinct 面不比内容，但取数失败不得判绿")

    # r179 自抓 1：顶层 source 为 null 时不得当成「一致」
    t = compare_tier("hub", cf_ok, gh_ok, lambda l: {"source": None, "environment": "production"},
                     lambda r, s: True)
    run("t6 只读顶层 source（r179 首跑的错）=> 取不到 commit，判 UNVERIFIED",
        t["source_state"] == "UNVERIFIED" and t["verdict"] == "UNVERIFIED")

    # 反向对照：同一份部署，走 commit_hash 路径就能取到
    t = compare_tier("hub", cf_ok, gh_ok, lambda l: _dep("7d6981c1df1c"), lambda r, s: True)
    run("t7 同一部署走 deployment_trigger 路径 => 取到 commit（证明修对了）",
        t["cf_commit"] == "7d6981c1df1c" and t["source_state"] == "PINNED")

    bad_keys = [k for k, v in TIERS.items() if v["cf_project"] == k]
    run("t8 无 cf_project 等于 key 的线（防拿 key 拼 API）", len(bad_keys) == 0)

    saved = TIERS["hub"]["cf_project"]
    try:
        TIERS["hub"]["cf_project"] = "hub"
        caught = len([k for k, v in TIERS.items() if v["cf_project"] == k]) > 0
        run("t9 变异(cf_project 退回 key) => 被 t8 抓到（非装饰腿）", caught)
    finally:
        TIERS["hub"]["cf_project"] = saved

    orig = globals()["sha12"]
    try:
        globals()["sha12"] = lambda b: "0"
        t = compare_tier("hub", cf_ok, gh_drift, lambda l: _dep("abc1234"), lambda r, s: True)
        run("t10 变异(sha 恒等) => mirror 漂移被漏检（证明判据依赖真 sha）",
            t["verdict"] == "OK")
    finally:
        globals()["sha12"] = orig

    # 架构腿：kind 只能是 mirror/distinct，写错不得静默放行
    saved_k = TIERS["hub"]["kind"]
    try:
        TIERS["hub"]["kind"] = "same"
        t = compare_tier("hub", cf_ok, gh_drift, lambda l: _dep("abc1234"), lambda r, s: True)
        run("t11 kind 写错（非 mirror/distinct）=> 不比内容但如实可见",
            t["kind"] == "same" and not t["rows"])
    finally:
        TIERS["hub"]["kind"] = saved_k
    # r180 聚合腿：取不到数必须是 UNVERIFIED，不得被归成 DRIFT（否则限流会误报成内容漂移）
    t = compare_tier("hub", cf_ok, gh_ok, lambda l: {}, lambda r, s: True)
    run("t12 CF 取不到 commit => UNVERIFIED 而非 DRIFT（聚合归类不混）",
        t["verdict"] == "UNVERIFIED", t["verdict"])

    # r181 自抓腿：追溯仓与 GH 对端仓**可以不同**（超市正是），但追溯仓写错就会误报脱钩。
    no_trace = [k for k, v in TIERS.items() if not v.get("cf_trace_repo")]
    run("t13 每条线都显式声明 cf_trace_repo（追溯仓不得留空）", len(no_trace) == 0,
        str(no_trace))
    run("t14 hub 追溯仓 = GH 侧同仓；超市则指向 supermarket-web（异构已验证）",
        TIERS["hub"]["cf_trace_repo"].endswith("global-memory-hub")
        and TIERS["supermarket"]["cf_trace_repo"].endswith("supermarket-web"),
        "hub=%s supermarket=%s" % (TIERS["hub"]["cf_trace_repo"],
                                  TIERS["supermarket"]["cf_trace_repo"]))

    # r181 单侧腿：distinct 面只有一侧失败也必须 UNVERIFIED（这是本轮真实抓到的形态）
    t = compare_tier("supermarket", boom, gh_ok, lambda l: _dep("abc1234"),
                     lambda r, s: True)
    run("t15 distinct 面单侧 HTTP 失败 => UNVERIFIED（抓 r181 尾行矛盾）",
        t["verdict"] == "UNVERIFIED" and len(t["fetch_errors"]) >= 1, t["verdict"])

    # r184 假红腿：_gh_commit_exists 必须分清「不存在」与「探测失败」。
    #   桩掉 subprocess.run / shutil.which / os.path.getsize ⇒ 不依赖本机是否装 gh。
    m_call = _gh_commit_exists
    import types as _tp

    class _Rc:
        def __init__(self, rc, stderr, stdout=""):
            self.returncode, self.stderr, self.stdout = rc, stderr, stdout

    def _mk(res):
        return lambda *a, **k: res

    _real = (subprocess.run, shutil.which, os.path.getsize, list(globals()["ABSENT_MARKS"]))
    try:
        shutil.which = lambda n: "C:/fake/gh.exe"
        os.path.getsize = lambda p: 12345
        # 定论否值 => False
        subprocess.run = _mk(_Rc(1, "gh: No commit found for SHA: deadbee (HTTP 422)", ""))
        run("t16 定论否值（No commit found / 422）=> False",
            m_call("lxh/x", "deadbee") is False)
        # 限流 => raise（不得折算成脱钩）
        subprocess.run = _mk(_Rc(1, "HTTP 429: Too Many Requests", ""))
        try:
            m_call("lxh/x", "abc1234")
            r429 = "NO-RAISE"
        except RuntimeError:
            r429 = "RAISE"
        run("t17 限流 429 不得判不存在 => 必须 raise（防假红）", r429 == "RAISE", r429)
        # 网络失败 => raise
        subprocess.run = _mk(_Rc(1, "connection reset by peer", ""))
        try:
            m_call("lxh/x", "abc1234")
            rn = "NO-RAISE"
        except RuntimeError:
            rn = "RAISE"
        run("t18 网络失败 => 必须 raise（不可折算成脱钩）", rn == "RAISE", rn)
        # rc=0 => True
        subprocess.run = _mk(_Rc(0, "", "0123456789abcdef"))
        run("t19 rc=0 => True（存在）", m_call("lxh/x", "abc1234") is True)
        # 变异：清空定论词表 => 真·不存在也退化成 raise（证明词表有牙、不是装饰）
        globals()["ABSENT_MARKS"] = []
        subprocess.run = _mk(_Rc(1, "gh: No commit found for SHA: deadbee (HTTP 422)", ""))
        try:
            m_call("lxh/x", "deadbee")
            mut = "NO-RAISE"
        except RuntimeError:
            mut = "RAISE"
        run("t20 变异(清空定论词表) => 定论否值退化为 raise（词表非装饰）", mut == "RAISE", mut)
    finally:
        subprocess.run, shutil.which, os.path.getsize = _real[0], _real[1], _real[2]
        globals()["ABSENT_MARKS"] = _real[3]


    n = sum(1 for _, ok in results if ok)
    print("[DUALFACE:SELFTEST] %d/%d" % (n, len(results)))
    return 0 if n == len(results) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    tiers = run_all()
    # r180 自抓聚合 bug：原写法 bad = verdict != OK，把 UNVERIFIED（取不到数）也算进
    #   「脱钩/漂移」=> rc=1 报成内容问题。取不到数是取数面故障，必须与漂移分开归口
    #   （audit-runner-safe-aggregate 同族：别让一种失败洗成另一种）。
    bad = [t for t in tiers if t["verdict"] == "DRIFT"]
    unv = [t for t in tiers if t["verdict"] == "UNVERIFIED"]
    doc = {"schema": "dual-tier-face-r180-v2",
           "cmd": "python 05-exec/r179_dual_face.py --json <out>",
           "note": "kind=mirror 才比 sha；commit 取 deployment_trigger.metadata.commit_hash"
                   "（顶层 source 实测为 null）；取不到数判 UNVERIFIED",
           "tiers": tiers}
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    for t in tiers:
        print("  %-12s kind=%-8s %-11s commit=%-14s %s trigger=%s" % (
            t["label"], t["kind"], t["verdict"], str(t["cf_commit"])[:14],
            t["source_state"], t["trigger_type"]))
        for p in t["rows"]:
            if "path" in p:
                print("      %-12s CF=%s(%dB) GH=%s(%dB) same=%s" % (
                    p["path"], p["cf_sha"], p["cf_bytes"], p["gh_sha"], p["gh_bytes"],
                    p["same"]))
            else:
                print("      %-12s up=%s %dB sha=%s" % (
                    p["side"], p["up"], p["bytes"], p["sha"]))
        for q in t["problems"]:
            print("      [!] " + q)
        for e in t["fetch_errors"]:
            print("      (取数失败) " + e)
    if unv and not bad:
        print("[DUALFACE:UNVERIFIED] %d 条线取不到数(限流/凭据/字段缺) => 不判绿也不指控漂移" % len(unv))
        return 2
    if unv and bad:
        print("[DUALFACE:FAIL] %d 条漂移/脱钩 + %d 条取不到数" % (len(bad), len(unv)))
        return 1
    if bad:
        print("[DUALFACE:FAIL] %d 条线脱钩/漂移" % len(bad))
        return 1
    print("[DUALFACE:PASS] %d 条 CF 部署面可溯源（mirror 面内容一致）" % len(tiers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
