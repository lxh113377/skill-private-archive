# -*- coding: utf-8 -*-
# r200_probe_cost_measure.py - 零联网实测「静态候选门」一次跑发几个外部调用。
#
# 为什么要有这个件（r200）：第 76 门要求每个联网门声明 CALLS_PER_RUN，而声明值必须是**量出来的**，
# 不是我看着代码估的（本轮我已三次因「没测就写」被自己的夹具推翻）。
# 做法：拦截 subprocess.run / urllib.request.urlopen —— 记录调用意图后返回 rc=1 / 抛 URLError，
# 让被测门自己退化成 UNVERIFIED，于是在**完全不产生外部请求**的前提下数出真实调用次数。
# 副产品：这同时自证了这些门在断网/凭据失效时确实走 UNVERIFIED，而不是崩或假绿。
#
# 候选清单来自第 76 门的静态粗筛（同一函数，口径天然一致），不再手写清单：
# 手写清单曾漏掉 r163_gh_path_face（漏计）并把未挂门的探针算进来（虚增）。
# 归类口径（三处 r200 自抓的仪表缺陷都已修）：
#   ① 按厂商不按端点形态：wrangler 打的就是 Cloudflare API ⇒ cloudflare；git fetch/push ⇒ github。
#   ② 按可执行文件名也算：本仓 gh 常解析成绝对路径 C:\Program Files\GitHub CLI\gh.exe，
#      用 \bgh\b 匹配不到，会把真实 GitHub 调用漏计成「未归类」。
#   ③ 被测件的 stdout 全部吞掉：遍历跑 main 会打印海量噪声（我第一版因此把结果冲掉）。
import contextlib
import io
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
CF_MARK = "cloudflare.com"
GH_MARK = "github.com"


class Counted:
    def __init__(self):
        self.cloudflare = 0
        self.github = 0
        self.other = 0

    def as_dict(self):
        return {"cloudflare": self.cloudflare, "github": self.github}


def classify_cmd(args):
    flat = " ".join(str(a) for a in (args if isinstance(args, (list, tuple)) else [args]))
    low = flat.lower()
    if CF_MARK in low or "wrangler" in low:
        return "cloudflare"
    if GH_MARK in low or "github cli" in low:
        return "github"
    # 按分词判 gh：'gh' / "gh" / gh.exe / gh, 都能成词命中，而 weight / through 不会
    # （r200 自抓：我先想用正则写边界，但字符类里带引号会把 raw 字符串本身截断 ——
    #  分词写法既免转义又更准，且一并覆盖 ②「gh 解析成绝对路径 gh.exe」的漏计）。
    if "gh" in set(re.split(r"[^0-9a-z]+", low)):
        return "github"
    if re.search(r"\bgit\b\s+(fetch|push|ls-remote)", low):
        return "github"
    return None


def measure(script_name):
    import importlib.util as _u
    import inspect
    p = os.path.join(HERE, script_name)
    if not os.path.isfile(p):
        return None, "文件不存在"
    c = Counted()
    real_run = subprocess.run
    real_open = urllib.request.urlopen

    class FakeRes:
        returncode = 1
        stdout = ""
        stderr = "blocked-by-measure"

    def fake_run(args, *a, **k):
        kind = classify_cmd(args)
        if kind == "github":
            c.github += 1
        elif kind == "cloudflare":
            c.cloudflare += 1
        else:
            c.other += 1
        return FakeRes()

    def fake_open(req, *a, **k):
        url = str(getattr(req, "full_url", req)).lower()
        if CF_MARK in url:
            c.cloudflare += 1
        elif GH_MARK in url:
            c.github += 1
        else:
            c.other += 1
        raise urllib.error.URLError("blocked-by-measure")

    subprocess.run = fake_run
    urllib.request.urlopen = fake_open
    argv_bak = sys.argv[:]
    sys.argv = [script_name]
    state = ""
    sink = io.StringIO()
    try:
        spec = _u.spec_from_file_location("tgt_" + re.sub(r"\W", "_", script_name), p)
        mod = _u.module_from_spec(spec)
        with contextlib.redirect_stdout(sink):
            spec.loader.exec_module(mod)
            if hasattr(mod, "main"):
                # 仪表自身的坑（r200 自抓）：各件 main() 签名不一，一律传 argv 会让
                # r32/r196/r113 报 EXC TypeError —— 那是我的仪表坏，不是那些件坏。
                try:
                    sig = inspect.signature(mod.main)
                    rc = mod.main([]) if len(sig.parameters) >= 1 else mod.main()
                    state = "rc=%s" % rc
                except SystemExit as e:
                    state = "exit=%s" % e.code
                except Exception as e:
                    state = "EXC %s: %s" % (type(e).__name__, str(e)[:50])
    finally:
        subprocess.run = real_run
        urllib.request.urlopen = real_open
        sys.argv = argv_bak
    if c.other:
        state += " (未归类进程/HTTP 调用 %d)" % c.other
    return c.as_dict(), state


def candidates():
    import r200_probe_cost_face as pc
    gates = pc.load_gates()
    out = []
    for g in gates:
        low = pc.read_script(g["script"])
        if low is None or not pc.has_machinery(low):
            continue
        if not pc.apis_of(low):
            continue
        out.append((g["script"], g["id"]))
    return gates, out


def main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    gates, cand = candidates()
    print("=== 零联网实测：静态候选 %d 件的外部调用足迹（门表共 %d 门）===" % (len(cand), len(gates)))
    res = {}
    for script, gid in cand:
        d, state = measure(script)
        res[script] = {"gate": gid, "calls": d, "state": state}
        print("  %-34s %-26s %s  %s" % (
            script, gid,
            json.dumps(d, ensure_ascii=False, sort_keys=True) if d else "取不到",
            state or ""))
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "probe-cost-measure-v3", "zero_network": True,
                       "candidates": len(cand), "results": res,
                       "provenance_cmd":
                       "python 05-exec/r200_probe_cost_measure.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
