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


def run_step(name, argv, timeout=900, ok_rc=(0,)):
    """跑一步并原样保留 stdout/stderr（失败不得静默）。

    r214 加 ok_rc（缺省 (0,) ⇒ 全部既有调用方语义不变）：有些步的非零退出码是**结论**
    而不是故障 —— 需求 6 可达性面判「算术不可达」按设计退 1。不区分就会把诚实结论记成
    失败步、把整个巡检永久打成 DEGRADED，正是 R211-3 登记的「设计内红与真故障红长得一样」同族。
    """
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=ROOT)
    except Exception as exc:  # noqa: BLE001 - 任何异常都记为该步失败，不冒泡吞掉
        return {"step": name, "rc": None, "error": repr(exc), "ms": int((time.time() - t0) * 1000),
                "stdout_tail": "", "stderr_tail": ""}
    rc = p.returncode
    return {"step": name, "rc": rc, "ms": int((time.time() - t0) * 1000),
            # r214 自抓：首版写成 rc not in ok_rc（方向反了），把「声明过的合法结论」
            # 判成失败、把默认步的 rc=1 判成结论。正确口径 = 非零且在 ok_rc 白名单内。
            # 反向验证三条腿（结论步 rc=1 / 默认步 rc=1 / rc=2）才能抓出方向写反；
            # 常驻守卫 = 本文件里的 req6_attainability 这一步本身：谓词再被写反，它的 rc=1
            # ⇒ face_ok=False ⇒ 巡检打 DEGRADED（红得可见），不需要再造一个孤儿夹具。
            "conclusion_rc": rc != 0 and rc in ok_rc,
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


def _read_swap_impact(path):
    """从 swap_impact.json 读「换装影响量」四数（句柄化，禁抄值）。

    三态：件缺失/解析失败 ⇒ None（禁当 0 影响引用）；
    正控未翻转 ⇒ discriminating_power=False，此时任何「0 影响」读数都不得引用
    （实验无鉴别力，R247/W-47 同族）。
    """
    import io as _io
    import json as _json
    if not os.path.isfile(path):
        return None
    try:
        with _io.open(path, encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    s = d.get("summary") or {}
    return {
        "variants_n": s.get("variants_n"),
        "local_improved_n": s.get("local_improved_n"),
        "local_degraded_n": s.get("local_degraded_n"),
        "subnet_changed_n": s.get("subnet_changed_n"),
        "cross_flips_n": s.get("cross_flips_n"),
        "negative_control_pass": (s.get("negative_control") or {}).get("pass"),
        "positive_control_pass": (s.get("positive_control") or {}).get("pass"),
        "discriminating_power": s.get("discriminating_power"),
        "source": os.path.relpath(path, ROOT).replace(os.sep, "/"),
    }


def _read_domain_face(path):
    """从 domain_face.json 读 L0 域过滤面五数（句柄化，禁抄值）。

    三态：件缺失/解析失败 ⇒ None（禁当 0 引用）。
    口径红线（r120 §2.3）：mismatch_n 是**潜在脆弱面**，不是缺口数；
    可引用的缺陷数 = real_fail_n。两个数必须同列，禁只报一个。
    """
    import io as _io
    import json as _json
    if not os.path.isfile(path):
        return None
    try:
        with _io.open(path, encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    f = d.get("face") or {}
    g = d.get("global_cf") or {}
    return {
        "questions_n": f.get("questions_n"),
        "mismatch_n": f.get("mismatch_n"),
        "mismatch_pct": f.get("mismatch_pct"),
        "mismatch_raw_n": f.get("mismatch_raw_n"),
        "calibration_diff_n": f.get("calibration_diff_n"),
        "exposed_n": f.get("exposed_n"),
        "real_fail_n": f.get("real_fail_n"),
        "domain_filter_net_pp": g.get("delta_pp"),
        "domain_filter_verdict": g.get("verdict"),
        "source": os.path.relpath(path, ROOT).replace(os.sep, "/"),
    }


def _read_tag_closure(path):
    """从 tag_closure.json 读第 9 类失败层四数（句柄化，禁抄值）。

    三态：件缺失/解析失败 ⇒ None（禁当 0 引用）。
    tag_closed_n 与 domain_closed_n 是**结构不可达**的两种成因，禁并成单数：
    前者更靠前（tag 闭包在 bge_recall 之前），影响面更窄但每条都更致命。
    """
    import io as _io
    import json as _json
    if not os.path.isfile(path):
        return None
    try:
        with _io.open(path, encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    fa = d.get("face") or {}
    return {
        "questions_n": fa.get("questions_n"),
        "reachable_n": fa.get("reachable_n"),
        "unreachable_n": fa.get("unreachable_n"),
        "tag_closed_n": fa.get("tag_closed_n"),
        "domain_closed_n": fa.get("domain_closed_n"),
        "tag_trap_n": fa.get("tag_trap_n"),
        "source": os.path.relpath(path, ROOT).replace(os.sep, "/"),
    }

def _read_trace_face(path):
    """从 trace_face.json 读生产流量面五数（句柄化，禁抄值）。

    三态：件缺失/解析失败 ⇒ None（禁当 0 引用）。
    ⚠️ 该文件会被轮换：r120 实测 23,630 行/15 天，后续实测 894 行/0.03 天 ⇒
    span_days 与 freshness_days 必须与 unique_n 同列，禁只报一个规模数。
    """
    import io as _io
    import json as _json
    if not os.path.isfile(path):
        return None
    try:
        with _io.open(path, encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    f = d.get("face") or {}
    return {
        "rows_n": f.get("rows_n"),
        "unique_n": f.get("unique_n"),
        "noise_n": f.get("noise_n"),
        "empty_q_n": f.get("empty_q_n"),
        "low_n": f.get("low_n"),
        "span_days": f.get("span_days"),
        "freshness_days": f.get("freshness_days"),
        "conservation_ok": f.get("conservation_ok"),
        "source": os.path.relpath(path, ROOT).replace(os.sep, "/"),
    }


def _read_req6_att(path):
    """从 req6_attainability.json 读需求 6 阈值可达性结论（句柄化，禁抄值）。

    三态同其余读数：件缺失 / 解析失败 / 无 result ⇒ None（禁当「可达」或「不可达」引用）。
    存在理由（r214）：结论只活在旁件里 = 下一轮没人打开它，就会继续把需求 6 记成
    「还没做到」而不是「这条尺子做不到」；写进主产物才每轮可见。
    """
    import io as _io
    import json as _json
    if not os.path.isfile(path):
        return None
    try:
        with _io.open(path, encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    r = d.get("result")
    if not isinstance(r, dict):
        return None
    return {
        "verdict": r.get("verdict"),
        "threshold_relative_pct": r.get("threshold_relative_pct"),
        "baseline_score": r.get("baseline_score"),
        "current_score": r.get("current_score"),
        "current_relative_gain_pct": r.get("current_relative_gain_pct"),
        "ceiling_score": r.get("ceiling_score"),
        "need_score_relative_reading": r.get("need_score_relative_reading"),
        "max_possible_relative_gain_pct": r.get("max_possible_relative_gain_pct"),
        "gap_to_need_points": r.get("gap_to_need_points"),
        "extra_hits_needed_for_threshold": r.get("extra_hits_needed_for_threshold"),
        "two_readings_agree": r.get("two_readings_agree"),
        "source": os.path.relpath(path, ROOT).replace(os.sep, "/"),
    }


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
    # r211 第 ⑥ 段前置：先重生本地输入面（W-46 死句柄补口）。
    # 动因（实测）：该段原先吃 _temp/local_fm_r114.json —— 全史零入库、全仓无生成器，
    # 且 _temp 会被并行会话按扩展名清场（R189-2），于是第 ⑥ 段**永久跑不起来**。
    # 接成前置步而不是「记得先手工跑一次」：长效机制依赖人的记性 = 没有机制。
    local_fm = os.path.join(BENCH, "local_frontmatter.json")
    steps.append(run_step("local_fm",
                          [PY, os.path.join(HERE, "r211_local_fm.py"),
                           "--json", local_fm, "--quiet"]))
    # r114 第 ⑥ 段：替代候选面（需求 2「每个 skill 3-5 个候选」的季度重扫）
    repl_argv = [PY, os.path.join(HERE, "r114_replacement_scan.py"),
                 "--local-fm", local_fm, "--json", repl]
    if args.offline:
        repl_argv.append("--offline")
    # 冷缓存实测预算（缺省 timeout=900s 不够）：池缓存 _temp/r114_search_cache 同会被清场，
    # 清场后本步要重打 14 条 search（SEARCH_SLEEP 2.2s）+ 逐仓 measure ~378 仓 × 2 请求
    # （r114 自记「串行 311 仓 ≈ 83 分钟」，现 --workers 8 ⇒ 下界约 10 分钟，但含限流退避）。
    # 给 2400s 是量出来的上界余量，不是「为了变绿放宽」——超时与失败在产物里同样具名（rc=None/error 行）。
    steps.append(run_step("replacement_scan", repl_argv, timeout=2400))
    # r217 前置步（池包幂等维护）：把「记得每季度手跑一次打包」从人身上拿掉。
    # 存在理由：05-exec/r217_pool_pack.py 是 R213-1 的生成器，但生成器没人调用 = 死句柄
    #   （W-46 / 与我今早已修的 R211-7 同一形态）；而机制的输入面 _temp/r114_search_cache/
    #   被 gitignore 且并行会话按扩展名清过场（R189-2 实测 212 件）⇒ 不自动续池，离线复算
    #   迟早再红一次。放在 replacement_scan **之后**：联网轮新增的散件条目当轮即并进入库包。
    # 幂等：包已覆盖活面时 --ensure 不写（mtime 不动）；活面被清空而包在 ⇒ 原包不动（防自杀式重建）。
    # rc=1 = 漂移后重建失败等真故障 ⇒ 用默认 run_step 计入失败步，不洗绿。
    pool_pack = os.path.join(BENCH, "pool_cache_r217.json")
    steps.append(run_step("pool_pack_ensure",
                          [PY, os.path.join(HERE, "r217_pool_pack.py"),
                           "--ensure", "--out", pool_pack, "--quiet"]))
    # r220 新增步（判据切换的前置定量）：严格口径 skill_md_exact_n 会不会改变任何 C1 分桶结论。
    # 存在理由：我把「是否切换判据」记成「须另行单独裁」后，这句话本身不可复算 —— 没人算过
    #   翻转数与双读数覆盖率。本步把它钉成读数；输入 = 本轮刚产的 replacement_matrix.json（零网络）。
    # rc 语义：0 = 零翻转（覆盖满则 READY、不足则 CLEAN）；1 = 检得分桶翻转（真问题，须逐条读）；
    #   2 = 无任何双读数行 = 切换前置无法量化，属**输入面真缺口**（不是设计内红）⇒ 计入失败步。
    caliber_flip = os.path.join(qdir, "caliber_flip.json")
    steps.append(run_step("caliber_flip",
                          [PY, os.path.join(HERE, "r220_caliber_flip.py"),
                           "--matrix", repl, "--json", caliber_flip, "--quiet"]))
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
    # r217 新增步（需求 6 口径 B 的反造假账）：逐条比较本轮与基线轮的 REAL_MISS 状态迁移。
    # 存在理由：口径 B 的「REAL_MISS 12→7」此前只由我一次性脚本自证过（R183-1 同族：结论不可复算），
    # 且「改善」有三条造假通路 —— 挪账（改判 STALE/UNDECIDABLE）、缩分母（删题面）、假消失（题面出集）。
    # 现件 = 本轮刚产的 rmiss（在 quarterly/<季度>/ 下，不进 glob 面）；
    # 基线 = 06-benchmark **根目录**里轮号最大的 route_miss_attr_*.json —— 口径要说准：
    # 那不是「固定锚」，而是「上一次入库到根目录的那一轮」。季产物落在 quarterly/<季度>/ 子目录，
    # 不参与该 glob ⇒ 若没人把新一轮结果入库到根目录，锚会停在 r216_live。
    # 这是有意保守（锚不动 ⇒ 跨季可比），但必须知道它不会自动前进，否则「相对基线」会悄悄变成
    # 「相对半年前」（AGENTS「禁硬编码当下值」同族：这里禁的是假装锚会自己走）。
    # 前进锚的合法动作 = 把新一轮件显式复制到 06-benchmark 根并在台账具名（本步不自动做）。
    # rc=1 = 红线破（真故障）⇒ 计入失败步、不把巡检洗绿；rc=2 = 输入面不可用，同样计入失败步。
    miss_mig = os.path.join(qdir, "miss_migration.json")
    steps.append(run_step("miss_migration",
                          [PY, os.path.join(HERE, "r217_miss_migration.py"),
                           "--current", rmiss, "--json", miss_mig, "--quiet"]))
    # r117 第 ⑨ 段：质量主指标（r115 起 = 生产路由 L1/L2/L3/L4 四层，权威件读数）
    truth = os.path.join(qdir, "quality_truth.json")
    steps.append(run_step("quality_truth",
                          [PY, os.path.join(HERE, "r115_quality_truth.py"),
                           "--json", truth, "--quiet"]))
    # r120b 第 ⑪ 段（R120-1 落地）：L0 域过滤面常驻读数。
    # 存在理由：r120 首析即量出 25.7% 题面域失配（生产口径），但**当时是一次性脚本**，
    # 而域归属会随注册表增删持续漂移 ⇒ 不常驻就等于「量过一次就永远信那一次」。
    # 本段只读 eval/ 与注册表，零网络；口径校准（raw vs norm）同列输出，
    # 防下一轮把「潜在脆弱面」当「缺口数」引用（r120 §2.3 已立该口径红线）。
    domain_face = os.path.join(qdir, "domain_face.json")
    steps.append(run_step("domain_face",
                          [PY, os.path.join(HERE, "r120_domain_face.py"),
                           "--json", domain_face],
                          timeout=900))
    # r120b 第 ⑫ 段（R120-4 落地）：生产流量面常驻读数。
    # 存在理由：r120 首析 route_trace 即证「路由缺口在合成题面不在真实使用」，但属一次性脚本，
    # 而生产流量每日新增 ⇒ 不常驻就等于结论永远停在 10-20。本段只读 jsonl，零网络。
    # ⚠️ 该文件会被轮换（r120 当时 23,630 行 / 15 天，本轮实测 894 行 / 0.03 天）⇒
    #   freshness_days 与 span_days 必须同列输出，禁只报 unique_n 让人以为一直是那个规模。
    # r126 第 ⑬ 段（第 9 类失败层「Tag 闭包」常驻读数）。
    # 存在理由：r120 立了第 8 类（域过滤），r126 发现同族更靠前的一层 —— tag_hits 非空时
    # bge_recall 只在 tag 命中的 skill 内搜，于是 tag 判错一个，期望件连 BGE 的边都碰不到。
    # 一手：279 题 79 题不可达（tag 27 / domain 51），15 题 tag_trap（raw_rank<=5 却结构不可达）。
    tag_closure = os.path.join(qdir, "tag_closure.json")
    steps.append(run_step("tag_closure",
                          [PY, os.path.join(HERE, "r126_tag_closure.py"),
                           "--json", tag_closure]))
    trace_face = os.path.join(qdir, "trace_face.json")
    steps.append(run_step("trace_face",
                          [PY, os.path.join(HERE, "r120_trace_face.py"),
                           "--json", trace_face]))
    # r119 第 ⑩ 段（S-4 落地）：换装影响量常驻读数。
    # 存在理由：r118 实测「换装对生产路由影响 0」是需求 6 的机制判据，但它此前只活在
    # r118 报告里 —— 下一季换装队列重新开工时，没有人会复跑这个沙箱，
    # 「0 影响」会退化成一句没人验证的传说。本段把沙箱接进季度巡检：
    #   · 每季现跑 r118_swap_sim.py（47 变体全量，本地 eval 面，零网络）；
    #   · 读数写进主产物 swap_impact 段（local_improved / local_degraded / 正负控判别力）；
    #   · 负控不通过或正控不翻转 ⇒ 该段 UNVERIFIED，禁把「无影响」当结论引用（R247）。
    # 口径：沙箱较慢（~2-4 分钟），故给 1800s 超时；失败不阻塞其余段，
    #       但 face_ok 会把失败步具名（见下方 failed 计算，本段已并入 steps）。
    swap_impact = os.path.join(qdir, "swap_impact.json")
    steps.append(run_step("swap_impact",
                          [PY, os.path.join(HERE, "r118_swap_sim.py"),
                           "--json", swap_impact],
                          timeout=1800))
    # r214 新增步（需求 6 定量收口）：阈值在本面**算术上可不可达**。
    # 段号刻意不写在注释里（本仓 r214 一手：我上一版把它标成「第 ⑯ 段」，而实际它是
    # steps 列表里的第 14 步）—— 步数由产物自述，手抄必漂移（X-24 / AGENTS「禁硬编码计数」）。
    # 取值：python -c "import json;d=json.load(io.open('06-benchmark/quarterly/2026Q4/audit.json',encoding='utf-8'));print(len(d['steps']))"
    # 存在理由：需求 6 自 r114 起每轮记「未达 2.0%」，但只给过三重定性证明（r131 §1.2），
    # 从没把「差多少」算成「能不能到」——于是「继续磨」与「必须换尺子」两种下一步动作
    # 无法区分。本段读同一次巡检的 quality_truth 产物（零网络，权威件自算的 max_achievable）。
    # rc=1 = 判「算术不可达」是**结论**不是故障 ⇒ ok_rc=(0, 1)，防把诚实结论记成 DEGRADED。
    req6_att = os.path.join(qdir, "req6_attainability.json")
    steps.append(run_step("req6_attainability",
                          [PY, os.path.join(HERE, "r214_req6_attainability.py"),
                           "--current", truth, "--json", req6_att, "--quiet"],
                          ok_rc=(0, 1)))
    _r120b_domain_reading = _read_domain_face(domain_face)
    _r120b_trace_reading = _read_trace_face(trace_face)
    _r126_tag_reading = _read_tag_closure(tag_closure)

    meta = fetch_meta(offline=args.offline)
    # r214：rc=1 且该步声明了 1 是合法结论（conclusion_rc）⇒ 不计失败步。
    # rc=None（超时/异常）与 rc>=2 仍一律算失败，判据强度只收紧不放宽。
    failed = [s["step"] for s in steps
              if s["rc"] != 0 and not (s["rc"] == 1 and s.get("conclusion_rc"))]
    meta_unv = sorted([r for r, v in meta.items() if v.get("state") == "UNVERIFIED"])

    face_ok = (all(os.path.isfile(p) for p in
                   (prov, up, swap, repl, qual, rmiss, truth, swap_impact, domain_face,
                    trace_face, tag_closure, req6_att, miss_mig, pool_pack, caliber_flip))
               and not failed)
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
                      "route_miss_attr": rmiss, "quality_truth": truth,
                      "swap_impact": swap_impact, "domain_face": domain_face,
                      "trace_face": trace_face, "tag_closure": tag_closure,
                      "req6_attainability": req6_att,
                      "miss_migration": miss_mig,
                      "caliber_flip": caliber_flip},
        "swap_impact_reading": _read_swap_impact(swap_impact),
        "domain_face_reading": _r120b_domain_reading,
        "trace_face_reading": _r120b_trace_reading,
        "tag_closure_reading": _r126_tag_reading,
        "req6_attainability_reading": _read_req6_att(req6_att),
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
