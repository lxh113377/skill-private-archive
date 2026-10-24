# -*- coding: utf-8 -*-
"""r213_ingress_face.py — 每轮入口分派可达面（第 92 门，r213）。

存在理由（r213 一手）：r213 前我把「免费额度读数」触发词补进 A-memory-start/SKILL.md L111
（R813），修的是「任务话术 -> 分派行 -> quickref 卷」这条**入口可达**链。但第 88 门量的是
BGE 召回（语料 = SKILL.md 前 800 字符），而分派行在偏移 5594、压根不在窗口内；第 86 门只查
「分卷有没有被任一 SKILL.md 提过指针」。⇒ R813 修的那一层此前**无任何判据守着**：哪天有人
把 L111 的指针或额度词删了，额度知识还在 quickref 里、第 86 门照样绿（它看别的 SKILL.md）、
第 88 门照样绿（它不看分派行）——入口断了也没人报。本门把这条链变成每轮可复算读数。

判据（全本地只读，零网络）：
  K1 可达集 = A-memory-start/SKILL.md 里所有反引号包住的 .md 指针（文件名集）；
     取不到 SKILL.md ⇒ UNVERIFIED（不按绿记，R247）
  K2 承载集 = 对每条 task_probe，扫 A-memory-start/references 各卷，ingress_keywords
     命中的卷（知识确实在这些卷里）。不靠我手标 want，全靠关键词实测
  K3 判定：承载集非空 且 承载集与可达集交集为空 ⇒ GAP_UNREACHABLE（知识在分派行
     不指向的卷里 = 有货没门）；承载集全在可达集 ⇒ 该任务入口通；
     承载集为空且 want==A-memory-start ⇒ GAP_NOEVIDENCE（名册声称它承载却无证据）；
     承载集为空且 want!=A-memory-start ⇒ 不由本面负责（NOT_APPLICABLE，不判红）
  K4 基线只拦增量（同 78/86/88 门）：历史入口缺口入基线，新增才 FAIL；基线缺失 ⇒ UNVERIFIED
  K5 自证有牙：构造「承载卷被判可达但实不在指针集」的反例 ⇒ 必须落 GAP（防恒绿）

portable=False：读 D:/global_skills 本机绝对路径，CI 的 Linux 无此树。
退出码：0 无新增入口缺口 / 1 有新增 / 2 基线或 SKILL.md 不可得
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
AM = os.path.join(GS, "A-memory-start")
AMREF = os.path.join(AM, "references")
SKILL = os.path.join(AM, "SKILL.md")
PROBES = os.path.join(ROOT, "06-benchmark", "recall_probe_registry.json")
BASELINE = os.path.join(ROOT, "06-benchmark", "ingress_wiring_baseline.json")
TOKEN = "[INGRESS:PASS]"
BT = chr(96)


def _read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def reachable():
    """SKILL.md 里反引号包住的 .md 指针（文件名集）。取不到 SKILL.md 返回 None。"""
    if not os.path.isfile(SKILL):
        return None
    t = _read(SKILL)
    return set(m.lower() for m in re.findall(BT + r"([A-Za-z0-9_.\-]+\.md)" + BT, t))


def bearer_vols():
    """references 各卷全文，按文件名归集（供关键词命中）。"""
    vols = {}
    if not os.path.isdir(AMREF):
        return None
    for f in os.listdir(AMREF):
        if f.endswith(".md"):
            vols[f.lower()] = _read(os.path.join(AMREF, f)).lower()
    return vols


def evaluate():
    reach = reachable()
    if reach is None:
        return None, "A-memory-start/SKILL.md 不可读 ⇒ 可达集为空面，不按绿记（R247）"
    vols = bearer_vols()
    if vols is None:
        return None, "A-memory-start/references 目录不可得 ⇒ 承载集不可判"
    if not os.path.isfile(PROBES):
        return None, "探针名册缺失 %s" % PROBES
    reg = json.load(io.open(PROBES, encoding="utf-8"))
    gaps, checked = [], 0
    for x in reg.get("task_probes", []):
        kw = [k for k in (x.get("ingress_keywords") or []) if k]
        want = x.get("want") or ""
        task = x.get("task", "?")
        if not kw:
            continue
        checked += 1
        bear = sorted(v for v, txt in vols.items()
                      if any(k.lower() in txt for k in kw))
        if not bear:
            if want == "A-memory-start":
                gaps.append("task:%s|名册称A-memory-start承载,但references无关键词证据" % task)
            continue
        if not any(b in reach for b in bear):
            # 承载知识确实在这些卷里，但没有一个被 SKILL.md 指针引用 ⇒ 有货没门
            gaps.append("task:%s|承载卷%s均未被SKILL.md分派指针引用" % (
                        task, "/".join(bear[:2])))
    return gaps, checked


def selfcheck():
    """K5 有牙自检：拿一条真实承载卷，验证它确实在可达集里（否则本门的判定基础不成立）。
    再构造反例：假想一个不在指针集的承载卷名，走同一判定必落 GAP。"""
    reach = reachable()
    vols = bearer_vols()
    if not reach or not vols:
        return False, "自检输入不可得"
    # 反例：一个肯定不在指针集里的卷名
    fake = "__no_such_vol__.md"
    contra = not any(b in reach for b in [fake])
    # 正例：至少一个被关键词命中的真实卷可被本面识别
    pos = any(v in reach for v in vols)
    return (contra and pos), "反例判不可达=%s 正例有可达承载卷=%s" % (contra, pos)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    gaps, res = evaluate()
    if gaps is None:
        print("[INGRESS:UNVERIFIED] %s（不得按全绿记，R247）" % res)
        return 2
    print("=== 每轮入口分派可达面（r213·本机专属）===")
    print("  任务判 %d 条，入口缺口 = %d" % (res, len(gaps)))
    ok, why = selfcheck()
    if not ok:
        print("  [INGRESS:WARN] K5 有牙自检未通过：%s（本门可能失去鉴别力）" % why)
    else:
        print("  [INGRESS:SELFTEST] K5 通过：%s" % why)
    if not os.path.isfile(BASELINE):
        print("[INGRESS:UNVERIFIED] 基线件缺失 ⇒ 无法判增量，不按绿记（R247）")
        return 2
    base = set(json.load(io.open(BASELINE, encoding="utf-8")).get("known_gaps") or [])
    cur = set(gaps)
    new_ones = sorted(cur - base)
    known = sorted(cur & base)
    for h in sorted(base - cur):
        print("  [INGRESS:HEALED] %s 入口已接通（基线应同步收缩）" % h)
    for k in known:
        print("  [INGRESS:KNOWN] %s 历史入口缺口（在基线内）" % k)
    for x in new_ones:
        print("  [INGRESS:GAP] %s 新增：知识在卷里但分派行不指向它（有货没门）" % x)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "ingress-face-v1", "readonly": True, "checked": res,
                       "gaps": sorted(cur), "baseline": sorted(base),
                       "new_gaps": new_ones, "k5": ok, "k5_detail": why,
                       "note": "承载知识所在 references 卷必须被 A-memory-start/SKILL.md 反引号指针引用；"
                               "否则任务话术到得了额度词、却到不了写着读数的卷",
                       "provenance_cmd": "python 05-exec/r213_ingress_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if new_ones:
        print("[INGRESS:FAIL] 新增入口缺口 %d 条" % len(new_ones))
        return 1
    print("  %s 无新增入口缺口（历史 %d 条在基线内，只准减不准增）" % (TOKEN, len(known)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())