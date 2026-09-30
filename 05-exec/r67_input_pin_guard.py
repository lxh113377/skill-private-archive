# -*- coding: utf-8 -*-
"""R58-1 第 17 维纵深常驻判据：仓外输入固定面（本地面）。

为什么这是「判据输入面」问题，而不是洁癖：
  本仓 26 道门读的全是**本地字节**，而这些字节由仓外三样东西决定 ——
  受管根本体（`D:\\global_skills` / `D:\\global_memory`）、焚诀、以及各端把受管根
  接到自己目录下的 **junction/镜像面**。CI 那一侧 r58 已用「pin 到不可变 SHA」固定了
  checkout；本地面此前**无人固定**：junction 断裂、被替换成真实目录、或被改成指向别处时，
  某端读到的根本不是权威源字节，而所有门禁照绿 —— 与 r58 D-113（未固定 checkout）同族，
  只是入口在本机。

四条不变式（缺一即红）：
  P1 形态/零输入（rc=2）：`paths` / `junction_paths` / `endpoints.active` 任一为空，
     或声明文件读不到 ⇒ UNVERIFIED，禁「没有声明所以全绿」（R247）。
  P2 镜像固定（rc=1）：`endpoints.active` × {skills,memory} 里**非 null** 的声明路径必须
     ① 存在 ② 是 junction/链接 ③ 解析目标 == 对应权威根。声明为 null 的记 `not_declared`
     分档并**逐条列出**（不静默丢，防「分母静默变小而面内全绿」）。
  P3 pin 落账：每次运行把各面 pin（HEAD sha + 未提交集摘要）append 进
     `06-benchmark/input_pins.jsonl`，使每个 verdict 可归因到确定的输入状态
     —— 这是「固定」在本地的等价物。
  P4 本行自洽（rc=1）：本门刚算出的 pin 必须与**同一次运行刚写入台账的那一行**逐字段相等
     （写哪本 / 指哪本 / 比哪本，r53 D-108 同族；防「写一份、判另一份」）。

**advisory（只报不阻断）**：与上一行台账比，列出 pin 变动的面 —— 这是本维度真正的信号，
  但受管根常年被并行会话改（r66 实测 45 条在途），做成硬闸即「消不掉的告警」（W-32 教训）。

r68 增强（回答「本轮的绿是对着哪些未提交字节」与「哪一面最常变」）：
  · 行内新增 `diff_files`（未提交集清单，cap=40）+ `diff_truncated`（超额显式声明）——
    **摘要仍是全量算**，只截断清单，防「清单短了被读成改动少」（R-ENUM）。
  · 新增 `--trend`：读全台账，按面统计「变动次数 / 出现行数 / 最近变动时刻 / 最新未提交条数」，
    按变动次数降序打印（advisory 报告；空台账 ⇒ rc=2，零输入不得判过）。
  · `--gate` 额外打印一行趋势摘要（最常变面）。

用法：`python 05-exec/r67_input_pin_guard.py [--decl F] [--ledger F] [--gate] [--trend]`
退出码：0 全绿 / 1 有违约 / 2 取数面不完整
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DECL = r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json"
DEFAULT_LEDGER = os.path.join(os.path.dirname(HERE), "06-benchmark", "input_pins.jsonl")
# 焚诀仓：本仓的已知外部依赖（项目 AGENTS.md「外部依赖」段登记），无法从 truth_constants 反推，
# 故作为**具名常量**列出并写明来源，而不是从别处抄一份清单（X-26）。
FENJUE_ROOT = r"C:\Users\37533\Desktop\workspace\焚诀"


def _no_bom_json(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def load_declaration(path):
    """读声明面；失败返回带 error 的空壳（调用方必须判空，不得当通过）。"""
    try:
        d = _no_bom_json(path)
    except (OSError, ValueError) as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}
    if not isinstance(d, dict):
        return {"error": "声明文件根不是对象"}
    return d


# 变异钩子（夹具用它证明「这两条守卫确实在起作用」；生产恒为 True，见 r67 夹具 T9/T10）
REQUIRE_JUNCTION = True
REQUIRE_TARGET_EQ = True


def probe_face(path, canon):
    """实测一个镜像面：返回 {declared, exists, kind, target, ok, why}。

    `kind` 用 `lstat().st_reparse_tag` 判 junction/链接（Windows 下 junction 不是 S_ISLNK，
    只判 `os.path.islink` 会把它读成普通目录 —— 这正是本判据要防的形态之一）。
    """
    if not path:
        return {"declared": False, "exists": False, "kind": "not_declared", "target": "",
                "ok": False, "why": "声明为 null（该端设计上无此面）"}
    ap = os.path.abspath(os.path.expandvars(path))
    if not os.path.exists(ap):
        return {"declared": True, "exists": False, "kind": "missing", "target": "",
                "ok": False, "why": "声明路径不存在"}
    try:
        st = os.lstat(ap)
        is_rep = bool(getattr(st, "st_reparse_tag", 0))
    except OSError:
        is_rep = False
    try:
        target = os.path.realpath(ap)
    except OSError:
        target = ""
    kind = "junction" if is_rep else ("dir" if os.path.isdir(ap) else "file")
    if REQUIRE_JUNCTION and not is_rep:
        return {"declared": True, "exists": True, "kind": kind, "target": target, "ok": False,
                "why": "不是 junction/链接（真实目录 = 各端读到的是自己的副本，与权威源已脱钩）"}
    if not canon:
        return {"declared": True, "exists": True, "kind": kind, "target": target, "ok": False,
                "why": "权威根未声明，无法比对"}
    same = os.path.normcase(os.path.normpath(target)) == os.path.normcase(os.path.normpath(canon))
    return {"declared": True, "exists": True, "kind": kind, "target": target,
            "ok": same or (not REQUIRE_TARGET_EQ),
            "why": "" if same else "解析目标 != 权威源"}


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "")
    except OSError as e:
        return 127, str(e)


HEAT_WINDOW_HOURS = 6   # 热度统计**时间窗**（近 N 小时）。r71 取代行窗=20：行窗在轮次密集时太短、稀疏时太长
TS_FMT = "%Y-%m-%dT%H:%M:%S"
NEW_FACE_QUOTA = 12     # cap 内**新面孔最多**占的条数（防新面孔整批挤掉高热度旧项，r70 §6②）
DIFF_CAP = 40           # diff_files 的展示上限；超额只截断**清单**，不截断计数与摘要（截断必须显式声明，R-ENUM）
# 变异钩子：生产恒为 True；夹具用它证明「对应守卫确实在承担判定」
NEW_FACE_FIRST = True   # 关掉 ⇒ 新面孔（热度 0）沉到末位（r70 夹具 T24）
QUOTA_ENFORCED = True   # 关掉 ⇒ 新面孔可占满 cap（r71 夹具 T29）
ORDER_BY_HEAT = True    # 关掉 ⇒ 清单退化为纯路径序（r69 夹具 T20）


def _parse_ts(s):
    try:
        return datetime.datetime.strptime((s or "")[:19], TS_FMT)
    except (ValueError, TypeError):
        return None


def window_rows(rows, hours=None, now=None):
    """按**时间窗**切行：返回 `(入窗行, 丢弃的不可解析行数)`。

    解析不出 ts 的行必须**计数丢弃**，不得静默归入任一侧：当成"窗口内"会虚高热度，
    当成"窗口外"会虚低热度 —— 两种都是静默改分母。`hours<=0` ⇒ 全史（不切）。
    """
    rows = list(rows or [])
    hrs = HEAT_WINDOW_HOURS if hours is None else hours
    if not hrs or hrs <= 0:
        return rows, 0
    cut = (now or datetime.datetime.now()) - datetime.timedelta(hours=hrs)
    kept, dropped = [], 0
    for r in rows:
        t = _parse_ts(r.get("ts"))
        if t is None:
            dropped += 1
            continue
        if t >= cut:
            kept.append(r)
    return kept, dropped


def heat_index(rows, hours=None, now=None, stats=None):
    """路径 -> 时间窗内出现次数（= 变动热度）。纯函数。

    `stats` 是可选出参：填 `rows_in` / `rows_dropped` / `hours`，让「这次统计的分母」可见
    （分母不可见的窗口统计 = 换口径没换尺）。
    """
    kept, dropped = window_rows(rows, hours, now)
    if isinstance(stats, dict):
        stats.update({"rows_in": len(kept), "rows_dropped": dropped,
                      "hours": (HEAT_WINDOW_HOURS if hours is None else hours)})
    acc = {}
    for r in kept:
        for f in r.get("faces") or []:
            for p in f.get("diff_files") or []:
                acc[p] = acc.get(p, 0) + 1
    return acc


def order_diff_files(files, heat=None, cap=None):
    """清单选取与排序：**新面孔优先** -> 热度降序 -> 路径升序；并按 `NEW_FACE_QUOTA` 配额、按 `cap` 截断。

    新面孔 = 时间窗内从未出现过的路径（等价于 `heat == 0`）。两种失效方向都要防：
      · **无配额** ⇒ 新面孔整批挤掉高热度旧项（r70 §6②，本轮修）；
      · **硬顶配额**（如「新面孔一律 ≤12，多出的名额空着」）⇒ 浪费 cap。
    故 `NEW_FACE_QUOTA` 的语义是**给老面孔预留的名额**：先取 `new[:q]`，再取 `old[:cap-q]`；
    任一侧不足时**补满 cap**（补的次序仍是「新面孔优先 → 热度降序」）。
    即：配额保证「老面孔不被整批挤掉」，但不以空置名额为代价。

    ⚠️ 排序/配额**只影响 `diff_files` 清单**，一律不进 `dirty_digest`（见 `pin_face` 红线）。
    """
    files = list(files or [])
    if not (ORDER_BY_HEAT and heat):
        ordered = sorted(files)
        return ordered[:cap] if cap else ordered
    key = lambda p: ((0 if (NEW_FACE_FIRST and heat.get(p, 0) == 0) else 1), -heat.get(p, 0), p)
    ordered = sorted(files, key=key)
    if not (cap and QUOTA_ENFORCED and NEW_FACE_FIRST and NEW_FACE_QUOTA is not None):
        return ordered[:cap] if cap else ordered
    new = [p for p in ordered if heat.get(p, 0) == 0]
    old = [p for p in ordered if heat.get(p, 0) != 0]
    q = max(0, min(NEW_FACE_QUOTA, cap))
    picked = new[:q] + old[:max(0, cap - q)]
    if len(picked) < cap:                      # 配额没用满 ⇒ 补回被让掉的名额
        seen = set(picked)
        for p in ordered:
            if len(picked) >= cap:
                break
            if p not in seen:
                picked.append(p)
                seen.add(p)
    return picked


def pin_face(root, diff_cap=DIFF_CAP, heat=None):
    """算一个输入面的 pin：HEAD sha + 未提交集摘要 + 未提交集清单（≤cap，超额显式声明）。

    摘要（`dirty_digest`，定长，**按路径序全量**算）是**判定**用的；清单（`diff_files`，人读，
    r69 起按**热度降序**）是**归因**用的 —— 回答「本轮判绿是对着哪些未提交字节」。
    清单被 cap 截断时只改清单：`dirty_n` 与 `dirty_digest` 仍按全量算，且 `diff_truncated` 显式标出。
    """
    if not root or not os.path.isdir(root):
        return {"root": root, "state": "unreachable"}
    rc, head = _git(root, "rev-parse", "HEAD")
    if rc != 0:
        return {"root": root, "state": "not_a_repo"}
    rc2, st = _git(root, "status", "--porcelain")
    if rc2 != 0:
        return {"root": root, "state": "status_failed"}
    lines = sorted(l for l in st.splitlines() if l.strip())   # 摘要口径：路径序、全量、与热度无关
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
    return {"root": root, "state": "pinned", "head": head.strip()[:12],
            "dirty_n": len(lines), "dirty_digest": digest,
            "diff_order": "heat" if (ORDER_BY_HEAT and heat) else "path",
            "diff_truncated": len(lines) > diff_cap,
            "diff_files": order_diff_files(lines, heat, cap=diff_cap)}


def judge(decl, faces):
    """纯判定：给声明与「已探好的面表」返回 (rc, report)。faces = [(label, probe_dict)]。"""
    if decl.get("error"):
        return 2, {"reason": "声明面读不到：%s" % decl["error"], "probes": []}
    paths = decl.get("paths") or {}
    jp = decl.get("junction_paths") or {}
    active = (decl.get("endpoints") or {}).get("active") or []
    if not paths or not jp or not active:
        return 2, {"reason": "声明面不完整（paths/junction_paths/endpoints.active 有空项）⇒ 零输入，"
                             "不得判过（R247）", "probes": []}
    viol = [f for f in faces if f["probe"]["declared"] and not f["probe"]["ok"]]
    not_declared = [f for f in faces if not f["probe"]["declared"]]
    return (1 if viol else 0), {"reason": "", "probes": faces, "violations": viol,
                                "not_declared": not_declared}


def build_faces(decl):
    """按声明表逐面实测（不手抄清单：端与路径全部来自 truth_constants）。"""
    canon = {"skills": (decl.get("paths") or {}).get("global_skills"),
             "memory": (decl.get("paths") or {}).get("global_memory")}
    faces = []
    for ep in (decl.get("endpoints") or {}).get("active") or []:
        per_end = (decl.get("junction_paths") or {}).get(ep) or {}
        for kind_name in ("skills", "memory"):
            p = per_end.get(kind_name)
            faces.append({"label": "%s.%s" % (ep, kind_name), "path": p,
                          "probe": probe_face(p, canon.get(kind_name))})
    return faces, canon


def self_consistent(pins, back_faces):
    """P4：刚写入台账的 faces 必须与本次算出的 pin 逐字段相等（写一份判另一份即假绿，D-108 同族）。"""
    return list(back_faces or []) == list(pins or [])


# 变异钩子（r68 夹具 T17 用它证明「变动计数确实在承担趋势判定」；生产恒为 True）
TREND_COUNT_CHANGES = True


# 变异钩子（r68 夹具 T19 用它证明「增量落账确实在省体量」；生产恒为 True）
INHERIT_UNCHANGED = True


def payload_faces(pins, rows):
    """落账用的 faces：**只在相对上一行有变动时**带全量清单，未变面只留指针。

    理由（体量）：清单是给人读的归因件，而受管根常年几十上百条未提交；每行都全量落账
    会让台账按「行数 × 面数 × 清单长」线性膨胀（首次实测单行 ≈6KB）。增量式后，
    稳态每行只带「变动面」的清单。

    r69 修②：指针 `diff_inherit` 指向**最近一次带该面全量清单的行**，不再是紧邻的上一行 ——
    继承行自身清单为空，指向它会让读者跳进空壳（跨多行未变时要顺着跳很多级）。找不到
    任何全量行时不写指针（保留清单本身），避免产生「指向空处的假指针」。

    纯函数，可被夹具双向喂样本。`rows` 为空 ⇒ 全部全量（首行无父可继承）。
    """
    rows = list(rows or [])
    prev = rows[-1] if rows else {}
    prev_by_root = {f.get("root"): f for f in prev.get("faces") or []}

    def last_full(root):
        """最近一次带该面全量清单的行：返回 `(ts, 该面当时的截断态)`；找不到 ⇒ ("", False)。"""
        for r in reversed(rows):
            for f in r.get("faces") or []:
                if f.get("root") == root and f.get("diff_files"):
                    return r.get("ts", ""), bool(f.get("diff_truncated"))
        return "", False

    out = []
    for f in pins or []:
        g = dict(f)
        p = prev_by_root.get(f.get("root"))
        same = bool(p) and (p.get("state"), p.get("head"), p.get("dirty_digest")) == \
                           (f.get("state"), f.get("head"), f.get("dirty_digest"))
        if INHERIT_UNCHANGED and same and f.get("state") == "pinned":
            ts, trunc = last_full(f.get("root"))
            if ts:
                g["diff_files"] = []
                g["diff_inherit"] = ts
                # r73：本行**没有**列清单 ⇒ 本面的 diff_truncated 必须归 False（否则读者会以为
                # 「这次的清单被截断了」）；真正的截断态移到 diff_truncated_inherited。
                g["diff_truncated"] = False
                g["diff_truncated_inherited"] = trunc
        out.append(g)
    return out


def row_truncated(faces):
    """行级「有效截断态」= 本行自己列的截断 **或** 继承来的截断（r68 引入该字段时的含义）。

    抽成纯函数是为了让判据与夹具**共用同一份口径**：夹具若自己重写这行表达式，测的是
    「我记得的逻辑」而不是「跑的那份逻辑」。
    """
    return any(bool(f.get("diff_truncated")) or bool(f.get("diff_truncated_inherited"))
               for f in faces or [])


def read_rows(ledger):
    """读台账全部行：返回 `(行, 坏行行号列表)`（行号 **1-based**，含空行计数）。

    r72 修：不可解析的行**必须计数上报**，不得静默 `continue` —— 静默跳过会让热度分母与
    趋势行数**一起变小而账面全绿**（R-ENUM 同族：分母静默变小）。
    r73 补：只报**个数**在量大时定位成本高 ⇒ 改为**逐行报行号**（报因里直接给出可跳转的位置）。
    台账是 append-only 自产件，坏行只可能来自写崩，属**可自愈**（补齐或用 `--ledger` 指定新本），
    故调用方按 UNVERIFIED 处理合适。
    """
    if not os.path.isfile(ledger):
        return [], []
    out, bad = [], []
    with io.open(ledger, encoding="utf-8") as fh:
        for i, l in enumerate(fh, 1):
            if not l.strip():
                continue
            try:
                out.append(json.loads(l))
            except ValueError:
                bad.append(i)
    return out, bad


BAD_SHOW_MAX = 10   # 报因里最多列出的坏行行号个数；超额显式声明（截断即声明）


def bad_rows_note(bad):
    """把坏行行号列表渲染成报因片段；超过 `BAD_SHOW_MAX` 个则显式声明截断。"""
    bad = list(bad or [])
    if not bad:
        return ""
    shown = ", ".join(str(n) for n in bad[:BAD_SHOW_MAX])
    tail = "（共 %d 行，仅列前 %d）" % (len(bad), BAD_SHOW_MAX) if len(bad) > BAD_SHOW_MAX else ""
    return "行号 %s%s" % (shown, tail)


# 变异钩子（r72 夹具 T30 用它证明「不可达面必须清掉陈旧值」；生产恒为 True）
TREND_STALE_GUARD = True


def trend_of(rows, count_changes=None):
    """跨轮趋势：按面统计 出现行数 / pin 变动次数 / 最近变动时刻 / 最新未提交条数 + 最新状态。

    纯函数（不碰盘），可被夹具双向喂样本。`changes` 只在 `count_changes` 为真时累加
    ——夹具用它做变异（关掉后趋势腿必须翻）。空输入 ⇒ 返回 {}（调用方必须判空）。

    r72 修：面**不可达**时 `latest_dirty_n` 必须归 `None`，不得保留上一个可用值 ——
    否则「最新未提交 N 条」会把一个**陈旧读数**当现状展示（本仓反复踩过的同族）。
    """
    count = TREND_COUNT_CHANGES if count_changes is None else count_changes
    acc, prev = {}, {}
    for r in rows or []:
        for f in r.get("faces") or []:
            root = f.get("root")
            if not root:
                continue
            a = acc.setdefault(root, {"root": root, "rows": 0, "pinned": 0, "changes": 0,
                                      "last_change_ts": "", "latest_dirty_n": None,
                                      "latest_state": ""})
            a["rows"] += 1
            a["latest_state"] = f.get("state") or ""
            if f.get("state") == "pinned":
                a["pinned"] += 1
                a["latest_dirty_n"] = f.get("dirty_n")
            elif TREND_STALE_GUARD:
                a["latest_dirty_n"] = None
            key = (f.get("state"), f.get("head"), f.get("dirty_digest"))
            if root in prev and count and prev[root] != key:
                a["changes"] += 1
                a["last_change_ts"] = r.get("ts", "")
            prev[root] = key
    return acc


def main(argv=None):
    ap = argparse.ArgumentParser(description="R58-1 仓外输入固定面（本地面）")
    ap.add_argument("--decl", default=DEFAULT_DECL)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--trend", action="store_true",
                    help="跨轮趋势：按面统计 pin 变动次数（advisory 报告；空台账 ⇒ rc=2）")
    a = ap.parse_args(argv)

    if a.trend:
        # 只读报告模式：**先于任何落账**执行，故空台账这一支在 CLI 上真实可达（否则永远被本行自己撑开）
        rows_all, bad = read_rows(a.ledger)
        if bad:
            print("[PIN:UNVERIFIED] 台账含 %d 行不可解析（%s）⇒ 取数面不完整，不得判过（R247）"
                  % (len(bad), bad_rows_note(bad)))
            return 2
        if not rows_all:
            print("[PIN:UNVERIFIED] 台账为空 ⇒ 无趋势可比（R247：零输入不得判过）")
            return 2
        acc = trend_of(rows_all)
        top = sorted(acc.values(), key=lambda x: (-x["changes"], -x["rows"], x["root"]))
        print("跨轮趋势（台账 %d 行 / %d 个输入面 ｜ 热度时间窗=近 %s 小时 ｜ 新面孔配额 %s）："
              % (len(rows_all), len(acc), HEAT_WINDOW_HOURS, NEW_FACE_QUOTA))
        for i, x in enumerate(top, 1):
            print("  %d. %-34s 变动 %d 次 / 出现 %d 行 ｜ 最近变动 %s ｜ 最新未提交 %s 条（状态=%s）"
                  % (i, x["root"], x["changes"], x["rows"], x["last_change_ts"] or "-",
                     x["latest_dirty_n"] if x["latest_dirty_n"] is not None else "-",
                     x.get("latest_state") or "-"))
        return 0

    decl = load_declaration(a.decl)
    faces, canon = build_faces(decl)
    rc, rep = judge(decl, faces)
    viol = rep.get("violations", [])

    if rc == 2:
        print("[PIN:UNVERIFIED] %s" % rep["reason"])
        return 2

    print("权威根: global_skills=%s ｜ global_memory=%s" % (canon.get("skills"), canon.get("memory")))
    print("镜像面: 共 %d 条（应判 %d 条，声明 null %d 条）"
          % (len(faces), len(faces) - len(rep.get("not_declared", [])), len(rep.get("not_declared", []))))
    for f in faces:
        pr = f["probe"]
        if not pr["declared"]:
            print("  · %-10s %-44s not_declared（%s）" % (f["label"], f["path"] or "-", pr["why"]))
        elif pr["ok"]:
            print("  ✅ %-10s %-44s -> %s" % (f["label"], f["path"], pr["target"]))
        else:
            print("  ❌ %-10s %-44s %s（实测 target=%s）" % (f["label"], f["path"], pr["why"], pr["target"]))

    # ── P3 pin 落账 + P4 本行自洽 + advisory 变动清单
    # r69：先读全历史 —— 热度索引与「最近一次全量行」都要看历史，不能只看紧邻上一行
    hist, hist_bad = [], []
    try:
        hist, hist_bad = read_rows(a.ledger)
    except OSError as e:
        print("  ⚠️ 台账读不到（%s）⇒ 本行仍落账，但变动清单与热度本轮不可比" % e.__class__.__name__)
    if hist_bad:
        print("[PIN:UNVERIFIED] 台账含 %d 行不可解析（%s）⇒ 取数面不完整，不得判过（R247）"
              % (len(hist_bad), bad_rows_note(hist_bad)))
        return 2
    prev = hist[-1] if hist else None
    heat_stats = {}
    heat = heat_index(hist, stats=heat_stats)
    print("   ℹ️ 热度口径：时间窗 近 %s 小时（入窗 %s 行 / 丢弃不可解析 %s 行）｜新面孔配额 %s"
          % (heat_stats.get("hours"), heat_stats.get("rows_in"), heat_stats.get("rows_dropped"),
             NEW_FACE_QUOTA))
    roots = [canon.get("skills"), canon.get("memory"), FENJUE_ROOT]
    pins = [pin_face(r, heat=heat) for r in roots if r]
    row_faces = payload_faces(pins, hist)
    # 行级聚合：契约只校验**行级**键，逐面清单嵌在 faces 里查不到 ⇒ 另立两枚行级事实
    # （本行落账清单条数合计 / 任一面是否被截断），由 row_required_from 代际接管。
    # 口径（r73 明确，**不因本改而漂移**）：行级 diff_truncated = 「含继承的**有效**截断态」，
    # 即本行自己列的截断态 **或** 继承来的截断态 —— r68 引入该字段时就是这个含义。
    row = {"schema": "input-pins-v1", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "decl": os.path.basename(a.decl), "faces": row_faces,
           "diff_files_n": sum(len(f.get("diff_files") or []) for f in row_faces),
           "diff_truncated": row_truncated(row_faces),
           "mirror_total": len(faces), "mirror_ok": len(faces) - len(viol) - len(rep.get("not_declared", []))}
    try:
        os.makedirs(os.path.dirname(a.ledger), exist_ok=True)
        with io.open(a.ledger, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError as e:
        print("[PIN:UNVERIFIED] 台账写不进去（%s）⇒ 无法固定输入面" % e.__class__.__name__)
        return 2
    back = None
    with io.open(a.ledger, encoding="utf-8") as fh:
        back = [json.loads(l) for l in fh if l.strip()][-1]
    if not self_consistent(row_faces, back.get("faces")):
        print("[PIN:FAIL] 本行自洽破：刚写入的 pin 与本次算出的不一致（写一份判另一份，D-108 同族）")
        return 1
    if prev:
        changed = [f["root"] for f, p in zip(pins, prev.get("faces") or [])
                   if f.get("state") == "pinned" and p.get("state") == "pinned"
                   and (f.get("head"), f.get("dirty_digest")) != (p.get("head"), p.get("dirty_digest"))]
        print("  ℹ️ 与上一行台账比：pin 变动 %d 个面%s（advisory，只报不阻断）"
              % (len(changed), ("：" + ", ".join(os.path.basename(c) for c in changed)) if changed else ""))

    if a.gate:
        if viol:
            print("[PIN:FAIL] 镜像/克隆面固定被破坏 %d 条：%s"
                  % (len(viol), ", ".join(v["label"] for v in viol)))
            print("   处置：对该端重建 junction 指向权威源（或跑既有 check-skill-mirror 链路）；"
                  "本门只判「镜像面是否钉在权威源」这一项事实")
            return 1
        # r72：read_rows 返回值已改为 (rows, bad)；此处 bad 必为 0（前面 hist_bad 已拦截）
        rows_for_trend, _bad = read_rows(a.ledger)
        acc = trend_of(rows_for_trend)
        if acc:
            hot = max(acc.values(), key=lambda x: (x["changes"], x["rows"]))
            print("   ℹ️ 跨轮趋势：最常变面 = %s（变动 %d 次 / 共 %d 行，advisory）"
                  % (hot["root"], hot["changes"], hot["rows"]))
        print("[PIN:PASS] 镜像面 %d 条全部钉在权威源（声明 null %d 条已逐条列出）｜pin 已落账 %d 面"
              % (len(faces) - len(rep.get("not_declared", [])), len(rep.get("not_declared", [])), len(pins)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
