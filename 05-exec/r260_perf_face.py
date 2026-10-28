# -*- coding: utf-8 -*-
"""r260_perf_face.py — 需求1「性能指标维」的数据源（2026-10-28 r260，零外网，受管根只读）。

为什么要造这个件（缺口是复核出来的，不是听来的）：
  06-benchmark/inventory_r227_2026-10-25.json 的 perf 字段全集只有 note /
  routing_cases / routing_hits / routing_top1_pct 四个键，191 行里带任何运行时
  字段（ms/elapsed/bytes/count/latency 类词根）的行数 = 0，且 inventory 自己
  承认「无单件执行耗时源」。=> 性能维在数据面上是空的，任何打分都是无源之水。
  本件把这一维从「note 里的一句话」换成「77 行可复跑读数」。

四个读数（口径在本 docstring 写死，别处不另立第二套）：
  P1 skillmd_bytes = D:/global_skills/<slug>/SKILL.md 的磁盘字节数（体量代理）
  P2 refs_files / refs_md / refs_bytes = <slug>/references/ 递归文件数、其中 .md
     卷数、总字节。为什么同时记两个数：本体系把「分卷」当正文体积单位（refs_md），
     但 references/ 里也有非 .md 资产，只报一个数就会把口径混掉。
  P3 route_ms_med  = 该件触发词首条丢进 unified_router.route() 的单题耗时，同题
     跑 3 次取中位（毫秒）。三个必须写进代码的环境前提：
       FENJUE_ROUTE_TRACE=0   不写 eval/route_trace.jsonl —— 否则测量动作本身在改焚诀派生件（红线6）
       FENJUE_ROUTE_CACHE=0   跨进程结果缓存回读的是上一次的耗时（r108 实测连跑两次都回同一个 1221.4ms），会造假
       先热身再计时             route() 首次进 BGE 分支要付 onnx 冷加载（实测 1745ms 对 2.4ms），冷启动记在 meta.warmup_ms，不摊到随机一件头上
     无触发词 => status=NO_TRIGGER 且 route_ms_med=None（**不是 0**：0 会把测不到伪装成极快）。
  P4 self_hit      = route() 的 top1 是否 == 自身 slug（召回真值）。r209 已证伪「窗口命中
     蕴含会被召回」，所以这里只认 top1，不认「进了候选」。

触发词取哪一条（可审计，来源记在 trigger_src）：
  fm_list   frontmatter 的 triggers: 块列表首项  —— 结构化字段，最接近该件自陈的唤起词
  fm_inline frontmatter 的 triggers: [a, b] 流式列表首项
  desc      description 散文里的「触发词：」后第一个分隔项（、，,;；/| 切）
  none      三者皆无 => NO_TRIGGER。只在本件自己的 SKILL.md 里取，绝不借第三方索引，
            免得把 A 的词算到 B 头上（同名域互串是真实风险）。

自证：python 05-exec/r260_perf_face.py --json <产物> 末行 [PERFFACE:PASS] 且行数 == 77；
负向对照：--selfcheck 走同一套 extract/measure 函数查一个不存在的 slug，断言
  skillmd_bytes/route_ms_med 都是 None 且 route_ms_med != 0，另加一条真实 query
  证明计时器不是恒 None（否则 None-everywhere 会假绿）。申报绿而实红 = 假交付（#36）。
"""
import argparse
import io
import json
import os
import re
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                        # 05-exec 的上一层 = 项目根（路径不硬编码，换机可跑）
GS = "D:/global_skills"                             # 受管根：本件**只读**，一个字节都不写（红线3）
EVAL_DIR = "C:/Users/37533/Desktop/workspace/\u711a\u8bc0/eval"   # 焚诀 eval：只 import 调 route()（红线6）
# 文件名「自建skill清单.md」用 \u 转义拼写：源码里不出现裸中文文件名，避开 shell/编辑器二次转码把路径打散
ROSTER = os.path.join(ROOT, "00-scope", "\u81ea\u5efa" + "skill" + "\u6e05\u5355.md")
DEFAULT_OUT = os.path.join(ROOT, "06-benchmark", "r260_perf_face.json")
PROGRESS = os.path.join(ROOT, "_temp", "r260_perf_face.progress.jsonl")
BT = chr(96)                                        # 名册表格里 slug 两侧的符号；用 chr 取，源码不写字面量
QUOTE_CHARS = chr(34) + chr(39)                     # YAML 列表项可能被引号包裹，统一剥掉
NEG_SLUG = "__no_such_skill_r260__"                 # 负向对照用 slug：磁盘上必然不存在
EXPECTED_ROWS = 77                                  # 口径裁定 HIGH 51 + MID 26 = 77，禁换分母

# 名册表格行 = | BT slug BT | ... ；只吃这一形态，段落说明文字没有前导竖管，天然跳过
ROW_RE = re.compile(r"^\|\s*" + BT + r"([^" + BT + r"]+)" + BT + r"\s*\|")
FM_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---", re.S)   # frontmatter 块（YAML 头），无头则空串
TRIG_LIST_RE = re.compile(r"^triggers:[ \t]*\r?\n((?:[ \t]*-[ \t]*[^\r\n]+\r?\n?)+)", re.M)
TRIG_INLINE_RE = re.compile(r"^triggers:[ \t]*\[([^\]\r\n]*)\]", re.M)
TRIG_CN_RE = re.compile(r"\u89e6\u53d1\u8bcd[:\uff1a][ \t]*([^\r\n]+)")
SPLIT_RE = re.compile(r"[\u3001\uff0c,;\uff1b/|]+")            # 中文散文里触发词的分隔符集


def parse_roster(path=ROSTER):
    """名册 -> [(slug, tier)]，顺序 HIGH 后 MID。

    为什么按节切而不是全文正则：同一文件里 LOW/EXCLUDE 也用同样的表格形态，
    全文正则会悄悄把分母从 77 涨到 128 —— 层级状态机是唯一能把口径钉死的写法。"""
    out = []
    tier = None
    for line in io.open(path, encoding="utf-8").read().splitlines():
        if line.startswith("## "):                  # 二级标题 = 层级边界
            head = line[3:].strip()
            tier = "HIGH" if head.startswith("HIGH") else ("MID" if head.startswith("MID") else None)
            continue
        if tier:
            m = ROW_RE.match(line)
            if m:
                out.append((m.group(1).strip(), tier))
    return out


def read_skill_md(slug):
    """返回 (字节数, frontmatter 文本, 全文)。件不存在 -> (None, None, None)。

    errors=replace：一件坏字节不该毁掉整轮 77 行的产物；坏件照样有一行可追。"""
    path = os.path.join(GS, slug, "SKILL.md")
    if not os.path.isfile(path):
        return None, None, None
    nbytes = os.path.getsize(path)                   # P1：磁盘字节，不按字符数（体量维要的是搬运成本）
    text = io.open(path, encoding="utf-8", errors="replace").read()
    m = FM_RE.match(text)
    return nbytes, (m.group(1) if m else ""), text


def measure_refs(slug):
    """P2：references/ 递归 (文件数, .md 卷数, 总字节)。无 references 目录 -> 全 0。

    为什么递归而不是只点顶层：本体系的分卷机制会把 partN 落在子目录，
    只数顶层会把「已拆卷」误判成「单卷」。"""
    d = os.path.join(GS, slug, "references")
    files = 0
    md = 0
    total = 0
    if os.path.isdir(d):
        for base, _dirs, names in os.walk(d):
            for fn in names:
                fp = os.path.join(base, fn)
                try:
                    total += os.path.getsize(fp)     # 坏链/占用中的文件跳过并继续，不整轮崩
                    files += 1
                    if fn.lower().endswith(".md"):
                        md += 1
                except OSError:
                    pass
    return files, md, total


def first_trigger(fm):
    """该件首条触发词 -> (词, 来源)。优先级 fm_list > fm_inline > desc，理由见模块 docstring。"""
    if fm is None:
        return None, "missing_skill"
    m = TRIG_LIST_RE.search(fm)
    if m:
        for line in m.group(1).splitlines():        # 块列表：取第一条非空 - 项
            v = line.strip()
            if v.startswith("-"):
                v = v[1:].strip().strip(QUOTE_CHARS)
                if v:
                    return v, "fm_list"
    m2 = TRIG_INLINE_RE.search(fm)                   # 流式列表 triggers: [a, b]
    if m2:
        parts = [p.strip().strip(QUOTE_CHARS) for p in m2.group(1).split(",")]
        parts = [p for p in parts if p]
        if parts:
            return parts[0], "fm_inline"
    m3 = TRIG_CN_RE.search(fm)                       # 兜底：description 散文里的触发词标记
    if m3:
        for tok in SPLIT_RE.split(m3.group(1)):
            tok = tok.strip().strip(QUOTE_CHARS).strip("\u3002\uff0e. ")
            if tok:
                return tok, "desc"
    return None, "none"


_UR = None


def load_router():
    """import unified_router 一次。env 必须**在 import 之前**设：TRACE_ENABLED 是模块顶层读的常量。"""
    global _UR
    os.environ["FENJUE_ROUTE_TRACE"] = "0"
    os.environ["FENJUE_ROUTE_CACHE"] = "0"
    if _UR is None:
        if EVAL_DIR not in sys.path:
            sys.path.insert(0, EVAL_DIR)
        import unified_router as UR
        _UR = UR
    return _UR


def warm_up(UR):
    """付掉 onnx 冷加载，返回热身耗时 ms。选一条必然进 BGE 分支的题（非直连），否则热不到语义层。"""
    t0 = time.perf_counter()
    UR.route("\u628a\u8fd9\u6b21\u8e29\u7684\u5751\u8bb0\u5230\u7ecf\u9a8c\u5e93\u91cc")
    return round((time.perf_counter() - t0) * 1000.0, 2)


def measure_route(UR, query, reps=3):
    """P3+P4：同一题跑 reps 次。返回 (中位ms, 每次ms, top1, direct_hit, 候选数, 置信档)。

    为什么中位不均值：单次读数会被 GC / 索引首建这类一次性开销甩成右偏（实测同一题
    1745 / 2.35 / 1.86 ms，均值 583 是纯粹的谎，中位 2.35 才是稳态）。
    参数一律用生产默认（route(query)）：本维要的是现役生产路径的耗时，不是关掉 L2/L3 后的下限。"""
    ms = []
    res = None
    for _ in range(reps):
        t0 = time.perf_counter()
        res = UR.route(query)
        ms.append((time.perf_counter() - t0) * 1000.0)
    cands = res.get("candidates") or []
    return (round(statistics.median(ms), 3), [round(x, 3) for x in ms], res.get("top1"),
            res.get("direct_hit"), len(cands), res.get("confidence"))


def build_row(slug, tier, UR, reps=3):
    """一件的完整读数行。抽成函数是为了让负向对照走**同一套**代码（判据自证 D10.2）。"""
    nbytes, fm, _text = read_skill_md(slug)
    rfiles, rmd, rbytes = measure_refs(slug)
    trig, src = first_trigger(fm)
    row = {"slug": slug, "tier": tier, "skillmd_bytes": nbytes,
           "refs_files": rfiles, "refs_md": rmd, "refs_bytes": rbytes,
           "trigger": trig, "trigger_src": src}
    if not trig:
        # 关键分支：测不到就写 None，绝不写 0（0 会被下游当成「极快」而误评高分）
        row.update({"route_ms_med": None, "route_ms_all": None, "top1": None,
                    "direct_hit": None, "n_candidates": None, "confidence": None,
                    "self_hit": None, "status": "NO_TRIGGER" if fm is not None else "MISSING_SKILL"})
        return row
    med, allms, top1, dh, nc, conf = measure_route(UR, trig, reps=reps)
    row.update({"route_ms_med": med, "route_ms_all": allms, "top1": top1,
                "direct_hit": dh, "n_candidates": nc, "confidence": conf,
                "self_hit": (top1 == slug), "status": "OK"})
    return row


def dump_json(path, meta, rows):
    """原子写：临时文件 + os.replace。节奏纪律要求边做边落盘，半截 JSON 比没有 JSON 更坏。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp." + str(os.getpid())
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "rows": rows}, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())                          # 落盘到底，别只落进页缓存就宣称已写
    os.replace(tmp, path)


def load_progress(path=PROGRESS):
    """--resume：读回 _temp 的逐行进度，返回 {slug: row}。坏行跳过（追加式日志的常态，不因此弃用整份）。"""
    done = {}
    if not os.path.isfile(path):
        return done
    for line in io.open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            if isinstance(r, dict) and r.get("slug"):
                done[r["slug"]] = r
        except ValueError:
            continue
    return done


def append_progress(row, path=PROGRESS):
    """每测完一件立刻追加一行并 flush —— 会话被打断时，已有的每一行都还在。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + chr(10))
        f.flush()


def selfcheck(reps=3):
    """负向对照 + 判据自证：返回 0 = 绿。"""
    UR = load_router()
    warm_up(UR)
    bad = build_row(NEG_SLUG, "HIGH", UR, reps=reps)
    v1 = bad["skillmd_bytes"] is None                 # 不存在的件：体量读数必须 None
    v2 = bad["route_ms_med"] is None                  # 耗时必须 None（MISS）
    v3 = bad["route_ms_med"] != 0                     # 且**不等于 0**（0 = 伪装成极快）
    v4 = bad["status"] == "MISSING_SKILL"
    v5 = bad["self_hit"] is not True                  # 判据不能恒真
    good = build_row("c-cleanup", "HIGH", UR, reps=reps)  # 正向：证明计时器不是恒 None
    v6 = isinstance(good["route_ms_med"], (int, float)) and good["route_ms_med"] > 0
    print("NEGCTRL slug=%s bytes=%s ms=%s status=%s self_hit=%s" % (
        NEG_SLUG, bad["skillmd_bytes"], bad["route_ms_med"], bad["status"], bad["self_hit"]))
    print("POSCTRL slug=c-cleanup ms=%s top1=%s self_hit=%s" % (
        good["route_ms_med"], good["top1"], good["self_hit"]))
    ok = all([v1, v2, v3, v4, v5, v6])
    print("CHECKS bytes_none=%s ms_none=%s ms_not_zero=%s status=%s hit_not_true=%s timer_alive=%s" % (
        v1, v2, v3, v4, v5, v6))
    print("[PERFFACE:PASS] selfcheck" if ok else "[PERFFACE:FAIL] selfcheck")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="r260 perf face measurement (HIGH+MID 77)")
    ap.add_argument("--json", dest="out", default=DEFAULT_OUT, help="output JSON path")
    ap.add_argument("--reps", type=int, default=3, help="timed reps per query, take median")
    ap.add_argument("--resume", action="store_true", help="reuse _temp progress rows")
    ap.add_argument("--selfcheck", action="store_true", help="negative control only")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")      # 中文 Windows 默认 GBK，不重配就乱码/崩
    except Exception:
        pass
    if args.selfcheck:
        return selfcheck(args.reps)
    roster = parse_roster()
    UR = load_router()
    warm = warm_up(UR)                                # 冷启动单独记账，不摊进任何一件（见 docstring）
    meta = {"round": "r260", "date": "2026-10-28", "roster": ROSTER.replace(chr(92), "/"),
            "denominator": "HIGH+MID 77", "reps": args.reps,
            "env": {"FENJUE_ROUTE_TRACE": "0", "FENJUE_ROUTE_CACHE": "0"},
            "warmup_ms": warm, "route_entry": "unified_router.route(query) production defaults",
            "router": EVAL_DIR.replace(chr(92), "/") + "/unified_router.py"}
    done = load_progress() if args.resume else {}
    if not args.resume and os.path.isfile(PROGRESS):
        os.remove(PROGRESS)                           # 非 resume 一律重开，避免旧轮的行混进本轮分母
    rows = []
    for slug, tier in roster:
        if slug in done:
            row = done[slug]
        else:
            row = build_row(slug, tier, UR, reps=args.reps)
            append_progress(row)
        rows.append(row)
        dump_json(args.out, meta, rows)               # 边做边落盘：每完成一件写一次全量产物
        print("  %-34s %-5s bytes=%-7s refs=%d/%dB trig[%s]=%-16s ms=%-8s top1=%-26s self=%s" % (
              slug[:34], tier, row["skillmd_bytes"], row["refs_md"], row["refs_bytes"],
              row["trigger_src"], str(row["trigger"])[:16], str(row["route_ms_med"]),
              str(row["top1"])[:26], row["self_hit"]))
    measured = [r for r in rows if isinstance(r["route_ms_med"], (int, float))]
    neg = build_row(NEG_SLUG, "HIGH", UR, reps=args.reps)   # 负控一并写进产物，交付件自带证据
    meta["rows"] = len(rows)
    meta["route_ms_measured"] = len(measured)
    meta["no_trigger"] = sum(1 for r in rows if r["status"] == "NO_TRIGGER")
    meta["self_hit_true"] = sum(1 for r in measured if r["self_hit"])
    meta["negative_control"] = {k: neg[k] for k in ("slug", "skillmd_bytes", "refs_files", "refs_md",
                                                    "refs_bytes", "trigger", "trigger_src", "route_ms_med",
                                                    "top1", "self_hit", "status")}
    dump_json(args.out, meta, rows)
    ok = (len(rows) == EXPECTED_ROWS and len(measured) > 0 and neg["route_ms_med"] is None
          and neg["route_ms_med"] != 0 and neg["status"] == "MISSING_SKILL")
    print("rows=%d measured=%d no_trigger=%d self_hit=%d warmup_ms=%s" % (
        len(rows), len(measured), meta["no_trigger"], meta["self_hit_true"], warm))
    print("[PERFFACE:PASS] rows=%d" % len(rows) if ok else "[PERFFACE:FAIL] rows=%d" % len(rows))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
