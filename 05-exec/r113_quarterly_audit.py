# -*- coding: utf-8 -*-
r'''r113_quarterly_audit.py -- 季度 skill 巡检一键入口（需求 5：长效定期巡检机制）。

存在理由（本仓形态，不是通用 template）：
  第 19 维（版本落后面）到 r113 才建起可判面（39/182），但此前**没有巡检节律**：
  r97 §4 P4 只把「twelve_face 季度重测」写在散文里，无人可复跑、无产物落点。
  本件把「每季度扫一遍：身份 / 上游关系 / 裁决 / 元数据」钉成**单命令 + 落盘产物**，
  使「是否出现更优开源替代」这个问题每季度被机器问一次，而不是靠谁想起来。

  判据链（复用，不重造）：本件只做编排与落盘，判定全部调用既有件 --
    · r112_provenance_scan.py   身份四档（declared/inferred/self_built/unknown）
    · r112_upstream_probe.py    六态内容寻址关系（可 --offline 复用缓存）
    · r112_swap_gate.py         五态裁决 + 盲区具名
    · r112_provenance_face.py   常驻门（离线结构判据）
    · gh api repos/<R>          上游仓元数据（stars/pushed/license/issues）
    · r114_replacement_scan.py  替代候选面（第 ⑥ 段；r114 建）
    · r114_quality_ab.py        eval 内三方法对照（第 ⑦ 段；r115 起降级为旁证）
    · r117_route_miss_attr.py   生产路由 miss 归因（第 ⑧ 段；r117 建）
    · r115_quality_truth.py     质量主指标四层（第 ⑨ 段；r115 起为唯一质量口径）

  反「取数失败销毁证据」（r112 cache-guard 范式，本件是 K-4 推广的第一件）：
    巡检产物写**同一路径**（quarterly/<季度>/audit.json）⇒ 一次网络抖动不得把上一季
    好产物覆盖成失败桩。守卫 = 任一步失败即**保留旧产物**并把失败痕迹写 sidecar
    audit.error.json（cache_error 同族）；只有全部步骤可用才原子替换主产物。
    零输入/全失败 ⇒ rc=2（R247）。

用法：
  python 05-exec/r113_quarterly_audit.py
  python 05-exec/r113_quarterly_audit.py --offline
  python 05-exec/r113_quarterly_audit.py --quarter 2026Q4 --json <件>
退出码：0 全步通过 / 1 保留旧产物（本实现用 2 表示面不可用）/ 2 面不可用（零输入，禁记绿）。
'''
import argparse
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
PY = sys.executable
GH = os.environ.get("GH_BIN") or r"C:\Program Files\GitHub CLI\gh.exe"

# 季度巡检的上游候选源（与本仓 r112/r113 实测在册者同源；禁手抄扩张，扩面须带取证）
UPSTREAM_REPOS = [
    "anthropics/skills", "obra/superpowers", "addyosmani/agent-skills",
    "github/spec-kit", "sickn33/agentic-awesome-skills", "kepano/obsidian-skills",
    "mattpocock/skills", "vercel-labs/skills", "calesthio/OpenMontage",
    "affaan-m/ECC", "composiohq/awesome-claude-skills",
]


def current_quarter(t=None):
    t = t or time.localtime()
    return "%dQ%d" % (t.tm_year, (t.tm_mon - 1) // 3 + 1)


def run_step(name, argv, timeout=900):
    """跑一步并原样保留 stdout/stderr（失败不得静默）。"""
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=ROOT)
    except Exception as exc:  # noqa: BLE001 - 任何异常都记为该步失败，不冒泡吞掉
        return {"step": name, "rc": None, "error": repr(exc), "ms": int((time.time() - t0) * 1000),
                "stdout_tail": "", "stderr_tail": ""}
    return {"step": name, "rc": p.returncode, "ms": int((time.time() - t0) * 1000),
            "stdout_tail": (p.stdout or "")[-1500:], "stderr_tail": (p.stderr or "")[-1500:]}


def fetch_meta(offline=False):
    """上游仓元数据（gh api）。失败逐仓具名 UNVERIFIED，禁留空。"""
    out = {}
    for r in UPSTREAM_REPOS:
        if offline:
            out[r] = {"state": "SKIPPED_OFFLINE"}
            continue
        try:
            p = subprocess.run([GH, "api", "repos/" + r], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60)
        except Exception as exc:  # noqa: BLE001
            out[r] = {"state": "UNVERIFIED", "error": repr(exc)}
            continue
        if p.returncode != 0:
            out[r] = {"state": "UNVERIFIED", "rc": p.returncode,
                      "stderr": (p.stderr or "")[:200]}
            continue
        try:
            d = json.loads(p.stdout)
        except ValueError as exc:
            out[r] = {"state": "UNVERIFIED", "error": "json:" + repr(exc)}
            continue
        out[r] = {"state": "OK", "stars": d.get("stargazers_count"),
                  "pushed_at": (d.get("pushed_at") or "")[:10],
                  "license": (d.get("license") or {}).get("spdx_id") or "UNLICENSED",
                  "open_issues": d.get("open_issues_count"), "archived": d.get("archived")}
        time.sleep(0.3)
    return out


def atomic_write_json(path, doc):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarter", default=None, help="季度标识，缺省按当前日期算")
    ap.add_argument("--out-dir", default=os.path.join(BENCH, "quarterly"))
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--offline", action="store_true", help="不联网，复用上游缓存")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    q = args.quarter or current_quarter()
    qdir = os.path.join(args.out_dir, q)
    os.makedirs(qdir, exist_ok=True)
    main_out = args.json_out or os.path.join(qdir, "audit.json")
    err_out = os.path.join(qdir, "audit.error.json")

    prov = os.path.join(qdir, "provenance.json")
    up = os.path.join(qdir, "upstream.json")
    swap = os.path.join(qdir, "swap_gate.json")
    repl = os.path.join(qdir, "replacement_matrix.json")
    qual = os.path.join(qdir, "quality_ab.json")

    steps = []
    steps.append(run_step("provenance_scan",
                          [PY, os.path.join(HERE, "r112_provenance_scan.py"), "--json", prov]))
    probe_argv = [PY, os.path.join(HERE, "r112_upstream_probe.py"), "--scan", prov, "--json", up]
    if args.offline:
        probe_argv.append("--offline")
    steps.append(run_step("upstream_probe", probe_argv))
    steps.append(run_step("swap_gate",
                          [PY, os.path.join(HERE, "r112_swap_gate.py"),
                           "--scan", prov, "--probe", up, "--json", swap]))
    steps.append(run_step("provenance_face",
                          [PY, os.path.join(HERE, "r112_provenance_face.py")]))
    # r114 第 ⑥ 段：替代候选面（需求 2「每个 skill 3-5 个候选」的季度重扫）
    repl_argv = [PY, os.path.join(HERE, "r114_replacement_scan.py"), "--json", repl]
    if args.offline:
        repl_argv.append("--offline")
    steps.append(run_step("replacement_scan", repl_argv))
    # r114 第 ⑦ 段：eval 内三方法对照（**口径降级**：r115 已证它不是生产路由读数，
    # 保留只为跨季观察「轻量匹配」而存在；质量主指标看第 ⑨ 段 r115_quality_truth.py）
    qual_argv = [PY, os.path.join(HERE, "r114_quality_ab.py"), "--json", qual, "--quiet"]
    steps.append(run_step("quality_ab", qual_argv))
    # r117 第 ⑧ 段：生产路由 miss 归因（STALE_EXPECT / UNREGISTERED / REAL_MISS / UNDECIDABLE）
    # 离线也跑：评分与注册表都在本机，不依赖网络（只在 eval 侧现算，焚诀 eval 只读）
    rmiss = os.path.join(qdir, "route_miss_attr.json")
    steps.append(run_step("route_miss_attr",
                          [PY, os.path.join(HERE, "r117_route_miss_attr.py"),
                           "--json", rmiss, "--quiet"]))
    # r117 第 ⑨ 段：质量主指标（r115 起 = 生产路由 L1/L2/L3/L4 四层，权威件读数）
    truth = os.path.join(qdir, "quality_truth.json")
    steps.append(run_step("quality_truth",
                          [PY, os.path.join(HERE, "r115_quality_truth.py"),
                           "--json", truth, "--quiet"]))

    meta = fetch_meta(offline=args.offline)
    failed = [s["step"] for s in steps if s["rc"] != 0]
    meta_unv = sorted([r for r, v in meta.items() if v.get("state") == "UNVERIFIED"])

    face_ok = all(os.path.isfile(p) for p in (prov, up, swap, repl, qual, rmiss, truth)) and not failed
    face_reason = None
    if not os.path.isfile(prov):
        face_ok = False
        face_reason = "provenance 产物缺失（零输入面）"
    elif failed:
        face_reason = "失败步: " + ",".join(failed)

    doc = {
        "schema": "quarterly-skill-audit-v1",
        "quarter": q,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cmd": "python 05-exec/r113_quarterly_audit.py --quarter " + q,
        "steps": steps,
        "failed_steps": failed,
        "upstream_meta": meta,
        "upstream_meta_unverified": meta_unv,
        "artifacts": {"provenance": prov, "upstream": up, "swap_gate": swap,
                      "replacement_matrix": repl, "quality_ab": qual,
                      "route_miss_attr": rmiss, "quality_truth": truth},
        "face_ok": face_ok,
        "face_reason": face_reason,
    }

    if not face_ok:
        # 守卫（cache_error 同族）：主产物是「上一季的好件」时原样保留，本轮痕迹只进 sidecar
        doc["kept_previous_main"] = os.path.isfile(main_out)
        atomic_write_json(err_out, doc)
        print("  取数面不完整（%s）⇒ 主产物未覆写（旧件保留），痕迹入 %s"
              % (face_reason, os.path.relpath(err_out, ROOT)))
        if not args.quiet:
            print("[QUARTERLY:DEGRADED] 面不可用 ⇒ rc=2（R247：零输入/全失败不得记绿）")
        return 2

    atomic_write_json(main_out, doc)
    if os.path.isfile(err_out):
        os.remove(err_out)
    if not args.quiet:
        print("季度巡检 %s 完成：%d 步全通过 ｜ 上游元数据 OK=%d UNVERIFIED=%d"
              % (q, len(steps), len(UPSTREAM_REPOS) - len(meta_unv), len(meta_unv)))
        if meta_unv:
            print("  具名 UNVERIFIED: %s" % ", ".join(meta_unv))
        print("JSON -> %s" % main_out)
        print("[QUARTERLY:PASS] 产物=%s" % os.path.relpath(main_out, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
