# -*- coding: utf-8 -*-
"""r208_recall_face.py — 实测知识能否被路由召回（第 88 门，r208）。

存在理由（r208 一手）：第 86 门（skill_wiring_face）守「分卷有没有指针」，但本轮实跑
unified_router 才暴露更深一层：A-memory-start 的按需加载靠 Step 0.6 程序化路由
（unified_router --json），其召回语料 = 各 skill 自己 SKILL.md 的前 N 个字符
（eval/build_indexes.py: "语料 = 磁盘 SKILL.md 前 800 字符（BGE 与 TF-IDF 同源）"，
bge_fullbody_meta.json 的 encoding 字段同证）。⇒ 写进 references/ 的知识，无论指针多齐，
都不在召回语料里：路由召不回它，Agent 就不会去读那卷。

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
  K2 探针名册（recall_probe_registry.json）声明「哪个 skill 承载哪个主题的实测知识」；
     自建口径 HIGH+MID 复算（以磁盘目录真实存在为准，含中文名 skill，同第 86 门）；
     探针词若不在该 skill 的 SKILL.md 前 N 字符（与语料严格同源窗口）内 ⇒ GAP_UNCALLABLE。
  K3 基线只拦增量（同 78/86 门）：历史不可召回入基线，新增才 FAIL；基线缺失 ⇒ UNVERIFIED。
  K4 自证有牙（K4 内存法）：换一个必然出现在窗口内的探针词 ⇒ 必须判可召回，防恒真。

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
    print("=== 实测知识可召回面（r208·本机专属）===")
    print("  召回窗口 = SKILL.md 前 %d 字符（源 eval/build_indexes.py CORPUS_CHARS）" % n)
    print("  探针条目（自建口径内）= %d，其中不可召回 = %d" % (checked, len(gaps)))
    if not os.path.isfile(BASELINE):
        print("[RECALL:UNVERIFIED] 基线件缺失 ⇒ 无法判增量，不按绿记（R247）")
        return 2
    base = set(json.load(io.open(BASELINE, encoding="utf-8")).get("known_uncallable") or [])
    cur = set(gaps)
    new_ones = sorted(cur - base)
    known = sorted(cur & base)
    for h in sorted(base - cur):
        print("  [RECALL:HEALED] %s 已进召回面（基线应同步收缩）" % h)
    for k in known:
        print("  [RECALL:KNOWN] %s 历史不可召回（在基线内）" % k)
    for x in new_ones:
        print("  [RECALL:GAP] %s 新增：知识在 references，但 SKILL.md 召回窗口内无探针" % x)
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
            json.dump({"schema": "recall-face-v1", "readonly": True, "window": n,
                       "checked": checked, "gaps": sorted(cur), "baseline": sorted(base),
                       "new_gaps": new_ones, "k4_teeth": tooth,
                       "note": "召回语料=SKILL.md 前 N 字符（BGE/TF-IDF 同源）；"
                               "写进 references 的知识不在召回面：可达不等于可召回",
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
