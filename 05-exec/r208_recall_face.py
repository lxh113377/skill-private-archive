# -*- coding: utf-8 -*-
"""r208_recall_face.py — 实测知识能否被路由召回（第 88 门，r208）。

存在理由（r208 一手）：第 86 门（skill_wiring_face）守「分卷有没有指针」，但本轮实跑
unified_router 才暴露更深一层：A-memory-start 的按需加载靠 Step 0.6 程序化路由
（unified_router --json），其召回语料 = 各 skill 自己 SKILL.md 的前 N 个字符
（eval/build_indexes.py: "语料 = 磁盘 SKILL.md 前 800 字符（BGE 与 TF-IDF 同源）"，
bge_fullbody_meta.json 的 encoding 字段同证）。⇒ 写进 references/ 的知识，无论指针多齐，
都不在召回语料里：连入场资格都没有（这是必要条件；充分条件见下面 K2 层二）。

本会话实跑证据（unified_router --json 两次，均 rc=0）：
  Q1「wrangler 读 Cloudflare 免费额度 date_geq 过滤字段 Rate limiter budget depleted 怎么查」
     -> top1 = local-mineru（非 win-toolchain-pitfalls），direct_hit = False
  Q2「命令静默无输出 exit code 恒 0 返回 0 结果 文件不存在 工具 command not found」
     （win-toolchain description 原词）-> top1 = commit-archaeologist，仍未召回它
  且 win-toolchain 的 SKILL.md 全文不含 Cloudflare / wrangler / date_geq / GitHub。
即 R805/R810 那两节 CF/GitHub 实测坑进对了 skill（在 references 且已入册），却进不了召回面。

判据（全部本地只读，零网络）：
  K1 召回窗口取自权威构建件 eval/build_indexes.py 的 CORPUS_CHARS（红线6：只读不改）；
     取不到 ⇒ UNVERIFIED，不硬编 800 当真相。
  K2 两层判据（r209 校正：别把「窗口命中」读成「会被召回」）：
     层一（入场券，必要非充分）—— 名册声明「哪个 skill 承载哪个主题的实测知识」，自建口径
       HIGH+MID 复算（磁盘目录真实存在为准，含中文名 skill，同第 86 门）；探针词不在该 skill
       SKILL.md 前 N 字符（与语料严格同源窗口）内 ⇒ 连入场资格都没有。
     层二（真值）—— expect=recalled 的条目须拿 route_truth_latest.json 验：direct_hit=True 或
       rank_of_skill<=TOP_N 才算召回，否则 GAP。r208 版只有层一且据此断言「窗口含词即可召回」，
       本轮实测证伪：用 win-toolchain 自己 description 的原词（必在窗口内）查询 top1 仍是别人，
       而 chaoshi 稳过靠 L0.1 直连表 10 条 pattern（win-toolchain 在 direct_map 里 0 条）。
  K3 基线只拦增量（同 78/86 门）：历史不可召回入基线，新增才 FAIL；基线缺失 ⇒ UNVERIFIED。
  K4 自证有牙：构造不出「窗口内必命中」样本就 WARN —— 防判据空转（不是防「误判可召回」，
     那由层二的真值件负责）；正控条目须能说清凭什么绿（r208 的 chaoshi 正控当时是偶然对的）。

退出码：0 无新增不可召回 / 1 有新增 / 2 基线或权威窗口不可得
portable=False：读 D:/global_skills 与焚诀 eval（本机绝对路径），CI 的 Linux 无此树。
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GS = "D:/global_skills"
EVAL_DIR = "C:/Users/37533/Desktop/workspace/\u711a\u8bc0/eval"
ROSTER = os.path.join(ROOT, "00-scope", "\u81ea\u5efaskill\u6e05\u5355.md")
PROBES = os.path.join(ROOT, "06-benchmark", "recall_probe_registry.json")
BASELINE = os.path.join(ROOT, "06-benchmark", "recall_wiring_baseline.json")
ROUTE = os.path.join(ROOT, "06-benchmark", "route_truth_latest.json")
TOP_N = 5
TOKEN = "[RECALL:PASS]"
BT = chr(96)


def _read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def corpus_window():
    """召回窗口取权威值；取不到返回 None（不硬编 800）。"""
    p = os.path.join(EVAL_DIR, "build_indexes.py")
    if not os.path.isfile(p):
        return None
    m = re.search(r"CORPUS_CHARS\s*=\s*(\d+)", _read(p))
    return int(m.group(1)) if m else None


def own_skills():
    """自建口径 HIGH+MID 分节解析，且磁盘目录真实存在为准（含中文名 skill）。"""
    if not os.path.isfile(ROSTER):
        return None
    tier, out = None, set()
    for line in _read(ROSTER).splitlines():
        s = line.strip()
        m = re.match(r"^##+\s*(HIGH|MID|LOW|EXCLUDE)[\u0028\uff08](\d+)[\u0029\uff09]", s)
        if m:
            tier = m.group(1)
            continue
        if s.startswith("##"):
            tier = None
            continue
        if tier in ("HIGH", "MID") and s.startswith("|") and "---" not in s \
                and s.count(BT) >= 2:
            nm = s.split(BT)[1].strip()
            if nm and os.path.isdir(os.path.join(GS, nm)):
                out.add(nm)
    return out


def evaluate(n, own, reg):
    gaps, checked = [], 0
    for item in reg.get("probes", []):
        skill = item.get("skill", "")
        if skill not in own:
            continue          # 市场件/EXCLUDE 不在自建口径，不代判
        md = _read(os.path.join(GS, skill, "SKILL.md"))
        if not md:
            continue
        checked += 1
        win = md[:n].lower()          # 与语料严格同源窗口
        probes = item.get("probes", [])
        hit = [p for p in probes if p.lower() in win]
        if not hit:
            gaps.append("%s::%s|探针=%s" % (skill, item.get("topic", "?"),
                                            "/".join(probes[:4])))
    return gaps, checked


def route_layer(own, reg):
    """第二层（r209）：路由真值。窗口命中只是入场资格（必要非充分）—— 本轮实跑证伪了
    「窗口含探针 ⇒ 会被召回」：用 win-toolchain 自己 description 的原词查询（必然在窗口内）
    top1=commit-archaeologist、rank=None；换措辞查同主题 rank 仍 None；而 chaoshi 靠 L0.1
    直连表 direct_hit=True 稳过（与窗口无关）。故 expect=recalled 的声明必须拿真值件验。
    真值件缺失/不可析/名册比真值件新 ⇒ err（判据不自己实跑 router，避免绑死焚诀可用性）。"""
    if not os.path.isfile(ROUTE):
        return None, "路由真值件缺失（先跑 r209_route_truth_measure.py --json <件>）"
    try:
        rt = json.load(io.open(ROUTE, encoding="utf-8"))
    except Exception as e:
        return None, "真值件不可解析：%s" % str(e)[:60]
    if os.path.getmtime(PROBES) > os.path.getmtime(ROUTE) + 5:
        return None, "探针名册比真值件新 ⇒ 改过声明却没重测（同第 76 门那族失效）"
    rows = {}
    for r in rt.get("rows", []):
        rows[(r.get("skill"), r.get("topic"))] = r
    gaps, judged = [], 0
    for item in reg.get("probes", []):
        if item.get("expect") != "recalled":
            continue
        skill = item.get("skill", "")
        if skill not in own:
            continue          # 市场件/EXCLUDE 不为它负责，也不给它报红
        judged += 1
        r = rows.get((skill, item.get("topic")))
        if r is None:
            gaps.append("%s::%s|真值件缺此行（重测）" % (skill, item.get("topic", "?")))
            continue
        rank = r.get("rank_of_skill")
        if r.get("direct_hit") or (isinstance(rank, int) and rank <= TOP_N):
            continue
        gaps.append("%s::%s|路由真值未召回 rank=%s top1=%s" % (
                    skill, item.get("topic", "?"), rank, r.get("top1")))
    return gaps, judged

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    n = corpus_window()
    if n is None:
        print("[RECALL:UNVERIFIED] 权威召回窗口不可得（eval/build_indexes.py 缺失或无 "
              "CORPUS_CHARS）⇒ 不硬编口径，不按绿记（R247）")
        return 2
    own = own_skills()
    if own is None:
        print("[RECALL:UNVERIFIED] 自建清单不可读 ⇒ 分母不明，不按绿记")
        return 2
    if not os.path.isfile(PROBES):
        print("[RECALL:UNVERIFIED] 探针名册缺失：%s" % PROBES)
        return 2
    reg = json.load(io.open(PROBES, encoding="utf-8"))
    gaps, checked = evaluate(n, own, reg)
    # 第二层：路由真值（窗口只是入场券）
    rgaps, rjudged = route_layer(own, reg)
    if rgaps is None:
        print("[RECALL:UNVERIFIED] 路由真值层不可用：%s ⇒ 不折算成可召回，不按绿记（R247）" % rjudged)
        return 2
    gaps = gaps + rgaps
    # 第三层（r210 一手）：真实任务语句的召回率。这不是「知识在不在」，而是
    # 「下次我会不会想起来查它」—— 用户说的那句任务话（「查 D1 额度」「开 R2 桶」）
    # 能不能把承载件带进前 3。只读真值件的 tasks 段，不实跑 router（判据不绑焚诀可用性）。
    tasks, tjudged, thits = [], 0, 0
    if os.path.isfile(ROUTE):
        try:
            rt2 = json.load(io.open(ROUTE, encoding="utf-8"))
            tasks = rt2.get("tasks") or []
            tjudged = rt2.get("task_judged")
            thits = rt2.get("task_hits")
            if tjudged is None:
                tjudged = len([x for x in tasks if x.get("want")])
            if thits is None:
                tjudged = len([x for x in tasks if x.get("want")
                              and x.get("outcome") != "DISPUTED"])
                thits = sum(1 for x in tasks
                            if x.get("want") and x.get("outcome") in ("HIT", "HIT_DIRECT"))
        except Exception as e2:
            print("[RECALL:UNVERIFIED] 任务真值段不可读：%s ⇒ 不折算成可召回" % str(e2)[:70])
            return 2
    elif os.path.getmtime(PROBES) > os.path.getmtime(ROUTE) + 5:
        print("[RECALL:UNVERIFIED] 名册比真值件新 ⇒ 改过声明却没重测（同第 76 门那族失效）")
        return 2
    else:
        print("[RECALL:UNVERIFIED] 真值件缺 task 段 ⇒ 先跑 r209_route_truth_measure.py 重测")
        return 2
    tgaps = ["task:%s|期望=%s 实测 top1=%s（任务语句召不回承载件）"
             % (x.get("task"), x.get("want"), x.get("top1"))
             for x in tasks if x.get("want") and x.get("outcome")
                         not in ("HIT", "HIT_DIRECT", "DISPUTED")]
    print("  任务层：有名册归属 %d 条，命中 %d，落空 %d" % (tjudged, thits, len(tgaps)))
    print("=== 实测知识可召回面（r208·本机专属）===")
    print("  召回窗口 = SKILL.md 前 %d 字符（源 eval/build_indexes.py CORPUS_CHARS）" % n)
    print("  窗口层判 %d 条 / 真值层判 %d 条 / 任务层判 %d 条，三层合计不可召回 = %d"
          % (checked, rjudged, tjudged, len(gaps) + len(tgaps)))
    if not os.path.isfile(BASELINE):
        print("[RECALL:UNVERIFIED] 基线件缺失 ⇒ 无法判增量，不按绿记（R247）")
        return 2
    base = set(json.load(io.open(BASELINE, encoding="utf-8")).get("known_uncallable") or [])
    cur = set(gaps) | set(tgaps)      # 任务层也进同一基线口径（三层一套增量判据）
    new_ones = sorted(cur - base)
    known = sorted(cur & base)
    # r211 防伪修复：HEALED 有两种成因，只有一种是好事。基线串里嵌着当时的「期望=<want>」，
    # 拿来与名册当前 want 一比即可分辨 ——
    #   同 want 而 gap 消失  = 召回真变好（HEALED，该收缩基线）
    #   want 被改过 / 条目被删 = 我改了分母（RELABEL/REMOVED，不是修复，r210 的 5 条假 HEALED 即此）
    mon_task = {}
    for x in reg.get("task_probes", []):
        mon_task["task:" + str(x.get("task"))] = x.get("want", "")
    mon_probe = set()
    for x in reg.get("probes", []):
        mon_probe.add("%s::%s" % (x.get("skill"), x.get("topic")))
    for h in sorted(base - cur):
        key = h.split("|")[0]
        why = None
        if key.startswith("task:") and key in mon_task:
            m_want = re.search("期望=(\\S+)", h)
            old_want = m_want.group(1) if m_want else ""
            if old_want != mon_task[key]:
                why = "want 改判 %s → %s ⇒ 是分母改动非召回改善" % (old_want, mon_task[key])
        elif not key.startswith("task:") and key not in mon_probe:
            why = "该条目已不在名册 ⇒ 条目被删/改名，不是召回改善"
        if why:
            print("  [RECALL:RELABEL] %s ⇒ %s" % (h, why))
        else:
            print("  [RECALL:HEALED] %s 已进召回面（基线应同步收缩）" % h)
    for k in known:
        print("  [RECALL:KNOWN] %s 历史不可召回（在基线内）" % k)
    for x in new_ones:
        print("  [RECALL:GAP] %s 新增（三层任一未过 ⇒ 不可召回）" % x)
    # K4 有牙自检：换必然出现在窗口内的词（取该 skill 标题词），必须判可召回
    tooth = False
    for item in reg.get("probes", []):
        skill = item.get("skill", "")
        if skill in own:
            md = _read(os.path.join(GS, skill, "SKILL.md"))
            if md:
                m2 = re.search(r"^#\s+(\S+)", md[: n * 3], re.M)
                if m2 and m2.group(1).lower() in md[:n].lower():
                    tooth = True
                    break
    if not tooth:
        print("  [RECALL:WARN] K4 有牙自检未能构造命中样本（本门可能失去鉴别力）")
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "recall-face-v3", "readonly": True, "window": n,
                       "checked": checked, "truth_judged": rjudged,
                       "task_judged": tjudged, "task_hits": thits, "task_gaps": tgaps,
                       "gaps": sorted(cur), "baseline": sorted(base),
                       "new_gaps": new_ones, "k4_teeth": tooth,
                       "note": "三层召回面：① 语料窗口=SKILL.md 前 N 字符（BGE/TF-IDF 同源），"
                               "写进 references 的知识不在召回面；② 路由真值：窗口命中只是入场券，"
                               "真召回看 direct_map（L0.1 直连）与 BGE rank；③ 任务召回率：真实任务"
                               "语句能否把承载件带进前 3（搭配对了 ≠ 路由认得出）。可达不等于可召回",
                       "provenance_cmd": "python 05-exec/r208_recall_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if new_ones:
        print("[RECALL:FAIL] 新增不可召回 %d 条" % len(new_ones))
        return 1
    print("  %s 无新增不可召回（历史 %d 条在基线内，只准减不准增）" % (TOKEN, len(known)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
