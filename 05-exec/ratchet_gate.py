# -*- coding: utf-8 -*-
r"""ratchet_gate.py — 注入面/度量棘轮门禁（本仓自持，只降不升；R19-2 的等价落点）。

为什么要它：r18/r19 实测出两条硬事实——① 平台技能目录每轮注入 ~45k 字符；② C25 只测它自己那 5 个
文件，而「P0 强制注入区」的另一套定义（attention_sim 的 6 文件）与之并集 **69,494B > 硬顶 65,536B
却仍判 PASS**，且**别的项目的注入壳完全在预算外**（本项目 AGENTS.md 实测 29,293B）。
把这条做成焚诀 C 系列判据要写它的 `eval/`（项目红线：只读调用不改，且该仓此刻 27 条在途），
转办两轮未回收 ⇒ 于是在**本仓权限内**先做成会拦人的东西：本文件即「超棘轮 / 超硬顶 / 无基线」
三类都 exit 非 0 的门禁，命令已挂进 `memory/AGENTS.md`「项目门禁命令」段（A-memory-start R193 在
修改类任务动手前实跑）。

五项指标（全部现算，不抄历史值）：
  catalog_grand_chars        平台技能目录 name+description 合计字符（`catalog_attention_tax.py` 产物）
  inject_union_bytes         C25 注入区 5 文件 **实测磁盘字节** ∪ 本项目注入壳 AGENTS.md（并集去重）
  claim_candidates           计数断言失真候选（`claim_truth_scan.py` 产物）
  drift_ruleish_candidates   累积漂移规则类候选（`cumulative_drift_scan.py` 产物）
  desc_over_cap              description 超官方 1024 上限条数（`description_baseline_scan.py` 产物）

R247：指标算不出（非数值）或基线缺该项 ⇒ 判失败，禁止「拿不到就当通过」。
用法：python 05-exec/ratchet_gate.py [--baseline 06-benchmark/inject_ratchet_baseline.json]
                                    [--json out.json] [--update] [--quiet]
退出码：0 全合规 / 1 有发现（超棘轮、超硬顶、无基线、指标缺失）/ 2 环境或输入不可用
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent
BENCH = WS / "06-benchmark"
GS = Path(r"D:\global_skills")
PROJ_SHELL = WS / "AGENTS.md"
DEFAULT_BASELINE = BENCH / "inject_ratchet_baseline.json"
TRUTH_CONSTANTS = Path(r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json")

METRIC_NAMES = ("catalog_grand_chars", "inject_union_bytes", "claim_candidates",
                "drift_ruleish_candidates", "desc_over_cap", "username_in_skill_files",
                "overdue_debt_items",
                "deferred_debt_items",
                "repeat_debt_items")   # r45 W-14：改期>=2 次的堆单独看守，防「降级」变成新免检通道
SCHEMA = "zijian-inject-ratchet-v2"   # W-37（r56）：新增必填面 refresh_days ⇒ 代际升 v2（旧件按新契约判红是有意的，须重生成）
FACE_NOTES = {}   # r50 W-25：指标取值时的"读取面"自证结果，main() 里如实打印（不算进指标值）

# ---- W-36（r54）：每个指标必须声明"多久必须重算一次" ----
# 动因（r54 双侧实测）：对手五家只有 2 家在 workflow 里声明节律（pre-commit 12 行 / spec-kit 7 行），
# 其余 0 —— 说明"多久跑一次"是被显式声明的对象；而我方 r53 差点拿 33 轮前的源件跟现值比
# （那次报的是命名假阳性，但揭开的是真缺口：没有任何地方声明过预算，源件烂在柜里也照样出数）。
METRIC_SOURCES = {
    "catalog_grand_chars": "catalog_attention_tax_*.json",
    "inject_union_bytes": None,          # 源 = 焚诀 truth_constants.json（活体清单，见 source_age_days）
    "claim_candidates": "claim_truth_*.json",
    "drift_ruleish_candidates": "cumulative_drift_*.json",
    "desc_over_cap": "description*.json",
    "username_in_skill_files": "LIVE",   # 活体 glob 受管根，无源件 ⇒ UNVERIFIED
    "overdue_debt_items": "debt_aging_r*.json",
    "deferred_debt_items": "debt_aging_r*.json",
    "repeat_debt_items": "debt_aging_r*.json",
}
METRIC_REFRESH_DAYS = {
    "catalog_grand_chars": 30, "inject_union_bytes": 14, "claim_candidates": 30,
    "drift_ruleish_candidates": 30, "desc_over_cap": 30, "username_in_skill_files": 14,
    "overdue_debt_items": 3, "deferred_debt_items": 3, "repeat_debt_items": 3,
}   # 债务三态预算 3 天：账龄尺每轮必跑，超过一轮即说明我漏跑了
# ⚠️ 上表 r56 起**只作种子**（`--seed-refresh-days` 一次性写进基线件），判定不再读它。

# W-37（r56）：再生预算的**权威声明面 = 基线件的 `refresh_days` 字段**，由契约做集合全等。
# 存在理由：预算原先只活在这个代码字典里，契约看不见 ⇒ 谁删掉某一项，collect_metrics 只会
# 静默少一项而不报错，"多久必须重算"退化成没人看守的注释（r54 D-97 登记、r55 收口时仍挂账）。
# 对手对照：pre-commit/spec-kit 把节律写在被 CI 解析的 workflow 里 —— 声明即被校验。
BASELINE_REFRESH_DAYS = {}


def set_baseline_budgets(mapping):
    """装载基线件声明的预算；非 dict 一律按「未声明」处理（禁回落代码常量当豁免表）。"""
    global BASELINE_REFRESH_DAYS
    BASELINE_REFRESH_DAYS = mapping if isinstance(mapping, dict) else {}
    return BASELINE_REFRESH_DAYS


def refresh_budget(metric):
    """取某指标的再生预算 ⇒ (预算 or None, 理由)。预算合法域与夹具一致：整数 ∈ (1, 60]。"""
    v = BASELINE_REFRESH_DAYS.get(metric)
    if isinstance(v, int) and not isinstance(v, bool) and 1 < v <= 60:
        return v, ""
    return None, "基线未声明该指标预算（refresh_days 缺项或越界，不回落代码常量）"


def source_age_days(metric):
    """取该指标源件的最新 mtime 年龄（天）；取不到 ⇒ None（活体/缺件），由调用方记 UNVERIFIED。"""
    import time as _t
    pat = METRIC_SOURCES.get(metric)
    if pat == "LIVE":
        return None
    if pat is None:
        cand = [TRUTH_CONSTANTS] if TRUTH_CONSTANTS.exists() else []
    else:
        cand = glob.glob(str(BENCH / pat))
    if not cand:
        return None
    try:
        return (_t.time() - max(os.path.getmtime(f) for f in cand)) / 86400.0
    except OSError:
        return None


def face_metric_refresh(age_days, budget_days):
    """三态：OK / STALE / UNVERIFIED。年龄或预算任一取不到 ⇒ UNVERIFIED，**不得当成 OK**。"""
    if not isinstance(budget_days, (int, float)) or budget_days <= 0:
        return "UNVERIFIED"
    if age_days is None:
        return "UNVERIFIED"
    return "OK" if age_days <= budget_days else "STALE"


def merge_note(prev_note, base_note, generated_at, changed):
    """把 --update 的归因段接在历史留账之后。返回 (新 note, 是否缩短)。

    存在理由（r55 实测）：`--update` 原先整份重建 doc 再落盘，等于每次刷新都把
    「这个基线值凭什么是它」的逐轮归因刷掉一遍（本仓 note 496 字 → 33 字，
    r38「真实敞口 22 而非 0」/ r40「真值直取证据件，未做人工削减」两条依据全丢）。
    留账与指标值同等重要 ⇒ 只增不减；任何缩短都交回调用方拒写（宁可红，不许刷留账）。
    """
    prev = str(prev_note or "").strip()
    if prev.startswith(base_note):
        trail = prev[len(base_note):].strip()
    else:
        trail = prev                      # 人工改过的 note：整条当留账保住，禁按长度切片
    seg = " ｜%s 自动核定 %s" % (
        generated_at, "、".join("%s %s→%s" % (k, a, b) for k, (a, b) in sorted(changed.items()))) \
        if changed else ""
    new = base_note + ((" " + trail) if trail else "") + seg
    return new, (len(new) < len(prev))


def refresh_summary(path=None):
    """W-38（r56）：给外部（账龄尺台账）用的再生健康度快照。

    必须自己装载基线预算 —— 否则调用方拿到的是一律 UNVERIFIED 的假结论
    （W-37 起预算不在代码里，装载是前提不是可选）。
    """
    bl = load_baseline(str(path or DEFAULT_BASELINE))
    set_baseline_budgets(bl.get("refresh_days"))
    return refresh_status()


def refresh_status():
    """返回 {指标: (状态, 年龄, 预算, 理由)}，并顺带把 STALE 记进 FACE_NOTES 供打印。

    W-37（r56）：预算改由基线件提供。取不到即 UNVERIFIED 且理由指认基线 ——
    **不回落代码常量**，否则契约外的运行仍按旧预算跑，等于给自己留一张豁免表。
    """
    out = {}
    for k in METRIC_NAMES:
        age = source_age_days(k)
        budget, why = refresh_budget(k)
        st = face_metric_refresh(age, budget)
        out[k] = (st, age, budget, why)
        if not why:
            FACE_NOTES.pop(k + "·预算", None)
        else:
            FACE_NOTES[k + "·预算"] = (False, why)
        if st == "STALE":
            FACE_NOTES[k + "·再生"] = (False, "源件已 %.1f 天未重算（预算 %s 天）⇒ 该指标转 unknown"
                                       % (age, budget))
    return out


def _read_json(glob_pat):
    """取匹配到的最新一份 JSON（按 mtime）。无文件/解析失败 → None（调用方记 unknown）。"""
    files = sorted(glob.glob(str(glob_pat)), key=lambda p: os.path.getmtime(p))
    if not files:
        return None
    try:
        with io_open(files[-1]) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def io_open(path):
    return open(str(path), "r", encoding="utf-8-sig")


def _latest(pattern):
    files = sorted(glob.glob(str(BENCH / pattern)), key=lambda p: os.path.getmtime(p))
    return files[-1] if files else None


def catalog_grand_chars():
    d = _read_json(BENCH / "catalog_attention_tax_*.json")
    return d.get("grand_chars") if isinstance(d, dict) else None


def claim_candidates():
    d = _read_json(BENCH / "claim_truth_*.json")
    return len(d.get("candidates") or []) if isinstance(d, dict) else None


def drift_ruleish_candidates():
    d = _read_json(BENCH / "cumulative_drift_*.json")
    return len(d.get("flagged_ruleish") or []) if isinstance(d, dict) else None


def desc_over_cap():
    d = _read_json(BENCH / "description*.json")
    return (d.get("summary") or {}).get("over_cap") if isinstance(d, dict) else None


def face_counted_vs_observed(counted, observed):
    """读取面自证（r50 W-25，X-24 的交叉断言形态）：成功读取数必须等于枚举数。

    存在理由：`username_in_skill_files` 里 `except OSError: continue` 会**静默跳过**读不到的文件，
    于是 n 是在比声称面更小的面上算出来的，而指标数字本身不带这个信息 —— 棘轮拿它和历史比，
    比的其实是两个不同的面。两条结构途径（枚举 vs 成功读取）不等即判红。
    """
    if observed == 0:
        return (False, "枚举到 0 件 ⇒ 该指标无从计算，不得当作 0 命中（R247）")
    if counted != observed:
        return (False, "成功读取 %d < 枚举 %d ⇒ 有 %d 件被静默跳过，指标是在缩小的面上算的"
                % (counted, observed, observed - counted))
    return (True, "读取面 == 枚举面（%d 件）" % observed)


def username_in_skill_files():
    """r34 第十一维落点：**含本机账号名的 SKILL.md 个数**（只降不升）。

    来源（实测）：`05-exec/r34_portability_surface.py` 量得本体系 167 个 SKILL.md 里
    **49 个含机器专属路径**，其中**明文含当前 Windows 账号名**的有 26 个；
    对手侧 addyosmani/agent-skills、obra/superpowers、anthropics/skills 三家抽样
    （25/15/19 个文件）**命中 0**，AAS 29 个里 1 个、mycelium 29 个里 2 个。
    ⇒ 这是本体系第一处"可测地落后于全部对手"的维度，且 C20（技能可移植性棘轮）早就存在却管不到这一类。

    两个刻意的设计：
      · 账号名由 `os.environ["USERNAME"]` 派生，**不把用户名再写死一遍**（否则本脚本自己成为新的泄漏点）；
      · 取不到账号名或扫不到文件 ⇒ 返回 None 进 unknown（R247：算不出不等于 0 命中）。
    """
    user = (os.environ.get("USERNAME") or "").strip()
    if not user or len(user) < 3:
        return None
    rx = re.compile(re.escape(user), re.IGNORECASE)
    n = 0
    scanned = 0
    paths = sorted(GS.glob("*/SKILL.md"))
    for f in paths:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        if rx.search(text):
            n += 1
    ok, why = face_counted_vs_observed(scanned, len(paths))
    FACE_NOTES["username_in_skill_files"] = (ok, why)
    if not ok:
        return None            # 面不完整 ⇒ 数字不参与棘轮比对（宁可 unknown，也不拿错面冒充可比值）
    return n if scanned else None


def _debt_class_state(key):
    """读最新一份账龄证据件的某个分类态；任一自洽条件不满足一律 None（算不出即红）。

    刻意不写死轮次：debt_aging_r*.json 按 mtime 取最新（r39 夹具 t17 实测——写死轮次会让
    新证据件永不生效、指标抱着旧值说谎）。分类之和 != open_total 时**两个态一起**失去可信度，
    不得单独放行。
    """
    d = _read_json(BENCH / "debt_aging_r*.json")
    if not isinstance(d, dict):
        return None
    by, ev = d.get("by_class") or {}, d.get("evidence") or {}
    total = ev.get("open_total")
    if not isinstance(total, int) or isinstance(total, bool):
        return None
    if key not in by:
        return None
    if sum(by.values()) != total:
        return None
    return by[key]


def overdue_debt_items():
    """r38 第十四维落点：超宽限且无裁决标记的待办数（只降不升）。"""
    return _debt_class_state("OVERDUE")


def deferred_debt_items():
    """r40 W-4：带到期日的延期项数（只降不升）。

    存在理由：r39 给 22 条超期都下了裁决后 OVERDUE 归 0，而 DEFERRED 从 9 涨到 23 ——
    只看 overdue 会让"给每条写个挂账至 rNN"持续把账面做干净，债务只是换了个格子。
    配套 W-5：两态连续 3 轮同时不降 ⇒ 停开新维度轮。
    """
    return _debt_class_state("DEFERRED")
def repeat_debt_items():
    """r45 W-14：被改期 >=2 次的待办数（只降不升）。

    存在理由（r44 D59 实测）：那一轮把 OVERDUE 从 16 压到 1，其中 11 条是靠「降级为长期看守」实现的；
    降级是**合法终局裁决**，但如果没有独立指标，「全部降级」就能把账面做得比真还债还干净。
    本指标把这条退路也纳入只降不升的看守面。取值面 by_class.REPEAT，与 overdue/deferred 同一自洽门。"""
    return _debt_class_state("REPEAT")


def inject_union_paths():
    """注入区**路径并集**（realpath 去重）。清单里登记的 bytes 不作数，只取盘上实存路径。
    抽成单源是为了让"逐件拆解"的取证脚本与棘轮判据共用同一个枚举器 —— 两份算法必漂移。
    """
    paths = set()
    try:
        tc = json.load(io_open(TRUTH_CONSTANTS))
        files = ((tc.get("inject_budget") or {}).get("files")) or []
    except (OSError, ValueError, AttributeError):
        files = []
    for row in files:
        p = (row or {}).get("path")
        if p:
            paths.add(os.path.realpath(p))
    if PROJ_SHELL.exists():
        paths.add(os.path.realpath(PROJ_SHELL))
    return paths


def inject_union_bytes():
    """C25 注入区清单（**实测磁盘字节**，不取清单里登记的数字）∪ 本项目注入壳，按路径去重求和。

    这里刻意不用 `bytes` 字段：r19 实测清单登记值会滞后于盘上真实大小，
    而「注入区双源且互不校验」正是要防的病灶（N2）。
    """
    paths = inject_union_paths()
    if not paths:
        return None
    total = 0
    for p in paths:
        try:
            total += os.path.getsize(p)
        except OSError:
            return None
    return total


def hard_caps():
    try:
        tc = json.load(io_open(TRUTH_CONSTANTS))
        cap = (tc.get("inject_budget") or {}).get("hard_cap_bytes")
    except (OSError, ValueError, AttributeError):
        cap = None
    return {"inject_union_bytes": cap} if isinstance(cap, int) else {}


COMPUTE = {"catalog_grand_chars": catalog_grand_chars,
           "inject_union_bytes": inject_union_bytes,
           "claim_candidates": claim_candidates,
           "drift_ruleish_candidates": drift_ruleish_candidates,
           "desc_over_cap": desc_over_cap,
           "username_in_skill_files": username_in_skill_files,
           "overdue_debt_items": overdue_debt_items,
           "deferred_debt_items": deferred_debt_items,
           "repeat_debt_items": repeat_debt_items}


def collect_metrics():
    """现算全部指标。返回 (metrics, unknown)——算不出的进 unknown，绝不填 0 冒充。

    W-36（r54）追加一档：源件**超期**（STALE）也算"算不出"⇒ 进 unknown。
    UNVERIFIED 不进 unknown —— 活体扫描类指标本就没有源件，判它红等于逼我造一个假源件。
    """
    metrics, unknown = {}, []
    refresh = refresh_status()
    globals()["LAST_REFRESH"] = refresh
    for name in METRIC_NAMES:
        if refresh.get(name, ("",))[0] == "STALE":
            unknown.append(name)                          # 陈旧源件不配当现值参与棘轮比对
            continue
        try:
            val = COMPUTE[name]()
        except Exception:
            val = None
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            unknown.append(name)
        else:
            metrics[name] = val
    return metrics, unknown


def load_baseline(path):
    try:
        with io_open(path) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return {"error": "%s: %s" % (type(e).__name__, e), "metrics": {}}
    if not isinstance(data, dict) or not isinstance(data.get("metrics"), dict):
        return {"error": "基线缺 metrics 字典", "metrics": {}}
    return data


def evaluate(metrics, baseline, caps):
    """返回 (findings, unknown)。未知指标名不参与判定（由调用方保证名单一致）。"""
    findings, unknown = [], []
    for name, val in metrics.items():
        if name not in METRIC_NAMES:
            continue
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            unknown.append(name)
            continue
        base = baseline.get(name)
        if not isinstance(base, (int, float)) or isinstance(base, bool):
            findings.append("%s=%s 无基线记录 ⇒ 禁止放行（先人工核定基线，不得默认通过）" % (name, val))
            continue
        if val > base:
            findings.append("%s=%s 超棘轮基线 %s（+%s，只降不升）" % (name, val, base, val - base))
        cap = caps.get(name)
        if isinstance(cap, int) and val > cap:
            findings.append("%s=%s 超硬顶 %s（+%s）" % (name, val, cap, val - cap))
    return findings, unknown


def inject_face():
    """注入面成员路径集合（与 inject_union_bytes 同一取法，供归因校验用）。"""
    paths = set()
    try:
        tc = json.load(io_open(TRUTH_CONSTANTS))
        for row in ((tc.get("inject_budget") or {}).get("files")) or []:
            p = (row or {}).get("path")
            if p:
                paths.add(os.path.realpath(p))
    except (OSError, ValueError, AttributeError):
        pass
    if PROJ_SHELL.exists():
        paths.add(os.path.realpath(str(PROJ_SHELL)))
    return paths


def attribute_raise(now_m, base_m, attr):
    """棘轮上调的唯一合法通道：**一项**增长被**一条**归因完整解释。

    棘轮只降不升是刻意的，但实测会出现「合法的外部增长」——2026-09-24 本仓 inject_union_bytes
    +447B 全部来自并行会话往 behavior_core.md 立 #23（用户明令的铁律）。既不能为此放宽判据
    （那等于把棘轮交给人心情），也不能永久卡死自己 ⇒ 开一条**必须留账**的窄门：
    commit 可解析 + path 确在注入面内 + delta 与实增**逐字节相等** + reason 非空。
    任何一条不满足即维持阻断。
    """
    grows = {k: int(now_m[k]) - int(base_m[k]) for k in METRIC_NAMES
             if isinstance(now_m.get(k), (int, float)) and isinstance(base_m.get(k), (int, float))
             and now_m[k] > base_m[k]}
    if not grows:
        return True, "无增长，无需归因"
    if len(grows) > 1:
        return False, "多项同时长大 %s，一条归因不足以解释" % grows
    name, delta = list(grows.items())[0]
    cands = [a for a in (attr or []) if isinstance(a, dict)]
    if name != "inject_union_bytes":
        return False, "指标 %s 的增长不可按文件归因（只有注入面有成员清单）" % name
    if len(cands) != 1:
        return False, "需要且仅需要一条归因记录，实测 %d 条" % len(cands)
    a = cands[0]
    if not str(a.get("reason") or "").strip():
        return False, "缺 reason"
    if not str(a.get("commit") or "").strip():
        return False, "缺 commit"
    if int(a.get("delta") or -1) != delta:
        return False, "归因 delta=%s 与实增 %s 不符" % (a.get("delta"), delta)
    rp = os.path.realpath(str(a.get("path") or ""))
    if rp not in inject_face():
        return False, "path 不在注入面成员内: %s" % a.get("path")
    if not _commit_exists(rp, str(a["commit"])):
        return False, "commit 在该文件所属仓内解析不到: %s" % a["commit"]
    return True, "%s +%d 由 %s@%s 解释" % (name, delta, os.path.basename(rp), a["commit"])


def _commit_exists(path, sha):
    """从文件所在目录向上找 .git，在该仓里解析 commit（找不到仓/对象、或对象不是 commit 即 False）。"""
    import subprocess
    d = Path(path).resolve().parent
    for cand in [d] + list(d.parents):
        if (cand / ".git").exists():
            r = subprocess.run(["git", "-C", str(cand), "cat-file", "-t", sha], capture_output=True)
            return r.returncode == 0 and (r.stdout or b"").strip() == b"commit"
    return False


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--json")
    ap.add_argument("--update", action="store_true",
                    help="把现状写成基线（**只允许下调**；上调或缺项一律拒绝）")
    ap.add_argument("--seed-refresh-days", action="store_true", dest="seed_refresh_days",
                    help="W-37：把代码种子表 METRIC_REFRESH_DAYS 一次性写进基线件 refresh_days 字段"
                         "（此后基线件为权威声明面，改预算=改基线件并须过契约集合全等）")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict-cap", action="store_true", dest="strict_cap",
                    help="把「超硬顶」也按阻断处理（默认非阻断告警，便于跨项目既有超限不拦本仓修改任务）")
    ap.add_argument("--raise-baseline", action="store_true", dest="raise_baseline",
                    help="带归因上调基线（唯一合法通道；须同时给 --commit/--path/--delta/--reason，不成立即 exit 1）")
    ap.add_argument("--commit", default="")
    ap.add_argument("--path", default="")
    ap.add_argument("--delta", type=int, default=-1)
    ap.add_argument("--reason", default="")
    args = ap.parse_args()

    # W-37（r56）：基线必须先装载 —— 再生预算的权威声明面在基线件里，
    # 而 collect_metrics → refresh_status 就要用它（原先顺序是"先判定后读基线"）。
    bl = load_baseline(args.baseline)
    if args.seed_refresh_days:
        if not bl.get("metrics"):
            print("[RATCHET:REFUSE] 基线不可用，无从播种预算")
            return 2
        doc = dict(bl)
        doc["refresh_days"] = dict(METRIC_REFRESH_DAYS)
        doc["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        doc["note"] = str(bl.get("note") or "") + " ｜%s 预算播种：refresh_days 由代码种子表写入基线件，此后基线为权威、代码表不再参与判定（W-37）" % doc["generated_at"]
        Path(args.baseline).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[RATCHET:SEEDED] 预算写入 %s（%d 项）；此后改预算=改基线件，且须过契约集合全等"
              % (args.baseline, len(doc["refresh_days"])))
        return 0
    set_baseline_budgets(bl.get("refresh_days"))
    metrics, unknown = collect_metrics()
    caps = hard_caps()

    if args.raise_baseline:
        if not bl.get("metrics"):
            print("[RATCHET:REFUSE] 基线不可用，无从归因")
            return 2
        _grow = {k: int(metrics[k]) - int(bl["metrics"][k]) for k in METRIC_NAMES
                 if isinstance(metrics.get(k), (int, float)) and isinstance(bl["metrics"].get(k), (int, float))
                 and metrics[k] > bl["metrics"][k]}
        if not _grow:
            print("[RATCHET:REFUSE] 现状并未长大 ⇒ 归因上调无的放矢（拒绝，防把留账本当装饰刷条数）")
            return 1
        rec = [{"commit": args.commit, "path": args.path, "delta": args.delta, "reason": args.reason}]
        ok, why = attribute_raise(metrics, bl["metrics"], rec)
        if not ok:
            print("[RATCHET:REFUSE] 归因不成立：%s（棘轮维持原值，判据不为人心情让路）" % why)
            return 1
        doc = dict(bl)
        ledger = list(doc.get("attributed_raises") or [])
        ledger.append(dict(rec[0], metric="inject_union_bytes",
                           at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                           from_value=bl["metrics"].get("inject_union_bytes"),
                           to_value=metrics.get("inject_union_bytes")))
        doc["metrics"], doc["attributed_raises"] = metrics, ledger
        Path(args.baseline).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[RATCHET:RAISED-ATTRIBUTED] %s ⇒ 基线 %s→%s，累计留账 %d 条"
              % (why, ledger[-1]["from_value"], ledger[-1]["to_value"], len(ledger)))
        return 0

    if args.update:
        if unknown:
            print("[RATCHET:REFUSE] 指标缺失 %s ⇒ 拒绝写基线（禁止把算不出的项写成 0）" % unknown)
            return 2
        old = bl.get("metrics") or {}
        raised = {k: (v, old[k]) for k, v in metrics.items() if k in old and v > old[k]}
        if raised and bl.get("schema") == SCHEMA:
            print("[RATCHET:REFUSE] 拒绝抬基线：%s" % json.dumps(raised, ensure_ascii=False))
            print("   要接受更大的实测面，须人工改本消息说明理由后手动写文件（棘轮的意义就在于此）")
            return 1
        doc = {"schema": SCHEMA, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "metrics": metrics, "hard_caps": caps,
               "sources": {"catalog": _latest("catalog_attention_tax_*.json"),
                           "claim": _latest("claim_truth_*.json"),
                           "drift": _latest("cumulative_drift_*.json"),
                           "desc": _latest("description*.json"),
                           "inject_files": "焚诀 truth_constants.inject_budget.files 实测 + 本项目 AGENTS.md"},
               "note": "只降不升棘轮；缺项/超顶/无基线一律 exit 非 0（R247）"}
        # r55 修类缺陷：上面这份 doc 原先是**整份重建**后直接落盘 ⇒ 每次 --update 都会
        # 抹掉历史 note 的逐轮归因与 attributed_raises 留账（实测：本仓 note 从 496 字被刷成
        # 33 字，r38「真实敞口 22 而非 0」、r40「真值直取证据件未做人工削减」两条依据全丢）。
        # 归因文字是「这个基线值凭什么是它」的唯一凭据，与指标值同等重要 ⇒ 只增不减，
        # 且缩短即拒写（宁可红，不许把留账当装饰刷掉）。
        base_note = doc["note"]
        new_note, shrunk = merge_note(bl.get("note"), base_note,
                                      doc["generated_at"],
                                      {k: (old.get(k), v) for k, v in metrics.items()
                                       if k in old and isinstance(old.get(k), (int, float))
                                       and isinstance(v, (int, float)) and old[k] != v})
        doc["note"] = new_note
        for carry in ("attributed_raises",):
            if bl.get(carry) and not doc.get(carry):
                doc[carry] = bl[carry]
        # W-37（r56）：`--update` 只刷「指标值」，**不得顺手重算预算声明面** ——
        # 预算是"多久必须重算"的承诺，若每次刷新都被代码值覆盖，就永远改不动也追不到。
        if bl.get("refresh_days"):
            if doc.get("refresh_days") not in (None, bl["refresh_days"]):
                print("[RATCHET:REFUSE] --update 试图改写预算声明面（%s→%s）⇒ 拒写；"
                      "改预算请显式编辑基线件并过契约" % (
                          bl["refresh_days"], doc.get("refresh_days")))
                return 1
            doc["refresh_days"] = bl["refresh_days"]
        elif doc.get("refresh_days"):
            print("[RATCHET:REFUSE] 老基线无预算面而新件有 ⇒ 来源不明，拒写（应先跑 --seed-refresh-days）")
            return 1
        if shrunk:
            print("[RATCHET:REFUSE] note 留账将缩短（%d→%d 字）⇒ 拒写基线"
                  % (len(str(bl.get("note") or "")), len(doc["note"])))
            return 1
        Path(args.baseline).parent.mkdir(parents=True, exist_ok=True)
        Path(args.baseline).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[RATCHET:BASELINE] 写入 %s（%d 项指标）" % (args.baseline, len(metrics)))
        return 0

    print("=== 注入面/度量棘轮门禁 (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("基线: %s%s" % (args.baseline, "" if bl.get("metrics") else "  ⚠️ %s" % bl.get("error", "无内容")))
    for name in METRIC_NAMES:
        val = metrics.get(name)
        base = (bl.get("metrics") or {}).get(name)
        cap = caps.get(name)
        print("  %-26s 实测=%-8s 基线=%-8s 硬顶=%s" % (
            name, val if val is not None else "缺失",
            base if base is not None else "-", cap if cap else "-"))
    if unknown:
        print("缺失指标（不得当 0）: %s" % ", ".join(unknown))
    if bl.get("error"):
        print("[RATCHET:FAIL] 基线不可用 → 先跑 `--update` 建立基线")
        return 2
    _ar = bl.get("attributed_raises") or []
    if _ar:
        print("  ℹ️ 归因抬基线留账 %d 条；最近：%s @%s（%s → %s，%s）" % (
            len(_ar), _ar[-1].get("reason", "-"), _ar[-1].get("commit", "-"),
            _ar[-1].get("from_value", "-"), _ar[-1].get("to_value", "-"), _ar[-1].get("at", "-")))
    findings, _unknown2 = evaluate(metrics, bl["metrics"], caps)
    # 两级判定：超棘轮/无基线 = 本次长大或判据失效 ⇒ 阻断（exit 1）；
    # 超硬顶 = 可能是跨项目既有事实（C25 只管它自己那 5 个文件）⇒ 默认告警不阻断，
    # 加 --strict-cap 升级为阻断。刻意不做「为了让门禁变绿而删掉硬顶比较」——那正是 R263 禁的形态。
    blocking = [f for f in findings if "超硬顶" not in f]
    advisory = [f for f in findings if "超硬顶" in f]
    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": SCHEMA, "generated_at": datetime.now().isoformat(timespec="seconds"),
            "baseline_file": str(args.baseline), "metrics": metrics, "unknown": unknown,
            "hard_caps": caps, "findings": findings,
            "blocking": blocking, "advisory": advisory,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    for f in advisory:
        print("  ⚠️ 非阻断告警: %s" % f)
    if blocking or unknown:
        for f in blocking:
            print("  - %s" % f)
        print("[RATCHET:FAIL] 阻断项 %d 项（超棘轮/无基线/指标缺失），另有非阻断告警 %d 项"
              % (len(blocking) + (1 if unknown else 0), len(advisory)))
        return 1
    if advisory and args.strict_cap:
        print("[RATCHET:FAIL] --strict-cap 生效：超硬顶 %d 项按阻断处理" % len(advisory))
        return 1
    print("[RATCHET:PASS] %d 项指标均在棘轮基线内（只降不升）；非阻断告警 %d 项" % (len(metrics), len(advisory)))
    for k, (ok, why) in sorted(FACE_NOTES.items()):     # r50 W-25：读取面自证（全 OK 时不刷屏）
        if ok is not True:
            print("  ⚠️ 读取面 %s ⇒ %s" % (k, why))
    rf = globals().get("LAST_REFRESH") or {}
    if rf:                                              # W-36（r54）：声明了周期就得看得见执行结果
        bad = {k: v for k, v in rf.items() if v[0] != "OK"}
        print("  再生周期（W-36）：%d/%d 指标在预算内 ｜ 非 OK：%s" % (
            len(rf) - len(bad), len(rf),
            " ".join("%s=%s(%s)" % (k, v[0],
                                    "%.1fd/%sd" % (v[1], v[2]) if v[1] is not None and v[2]
                                    else (v[3] or "无源件"))
                     for k, v in sorted(bad.items())) or "无"))
        decl = sum(1 for v in rf.values() if v[2] is not None)
        print("  预算来源：基线件 refresh_days 已声明 %d/%d 项%s" % (
            decl, len(rf),
            "" if decl == len(rf) else " ⇒ 未声明项记 UNVERIFIED，**不回落代码常量**（W-37）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
