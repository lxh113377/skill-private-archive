# -*- coding: utf-8 -*-
"""W-27 取值面生成器：把「极性冲突候选」按**规则本体**归一后再数，并生成待裁定单。

存在理由（r56）：r51 那份 `w27_conflict_triage_r51_*.json` 也是**一次性内联脚本**产出的，
仓里没有可复跑的生成器 ⇒ 它同样是死句柄（与 W-32 同病，另立 W-46 说这条通病）。
本脚本三条自证：
  ① 单一来源：不自己再扫一遍规则文件，而是**跑真实 `rule_conflict_scan.py`** 取它的输出
     （两份扫描算法必漂移 —— R292 保质期断言同族）；
  ② 分卷归一：`behavior_core_rules_p3.md` / `..._p6.md` / `appendix` 都是**同一条 #21/#28 规则**
     的分卷载体，不归一就会把 1 对规则放大成 N 对（r51 实测的笛卡尔放大正是这个）；
  ③ 谓词可复核：判定"禁侧是不是呈现形式元规则"用的是**写明在码里的 token 表**，
     命中哪个 token 逐条记进件里，人工可推翻；不写"我看它像"。
只报告不阻断（r25 用户否决拦任务的闸门）：本脚本人工裁定前**不改任何规则正文**。
"""
import datetime
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "rule_conflict_scan.py")
FORM_TOKENS = ("收尾", "结尾", "形式", "footer", "排版", "段落")


def base_rule(loc):
    """把分卷/载体路径归一到**规则本体**名（放大就发生在这一层）。"""
    f = (loc or "").split(":")[0].replace("\\", "/")
    n = os.path.basename(f)
    n = re.sub(r"\.part\d+\.md$", ".md", n)
    m = re.match(r"^behavior_core(?:_rules_p\d+|_appendix)?\.md$", n)
    if m:
        return "core/behavior_core.md（分卷归一）"
    if n.startswith("contract"):
        return "A-memory-start/references/contract.md"
    if n == "SKILL.md":
        d = f.split("/")
        return "SKILL.md:" + (d[-2] if len(d) > 1 else "?")
    return n


def is_form_meta(text):
    hits = [t for t in FORM_TOKENS if t in (text or "")]
    return hits


def main():
    if not os.path.isfile(SCAN):
        print("[TRIAGE:UNVERIFIED] 取不到 rule_conflict_scan.py")
        return 2
    tmpj = os.path.join(tempfile.gettempdir(), "r56_scan_src.json")
    env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r56")
    p = subprocess.run([sys.executable, SCAN, "--json", tmpj],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=os.path.dirname(HERE))
    if not os.path.isfile(tmpj):
        print("[TRIAGE:UNVERIFIED] 扫描器没落出 JSON（rc=%s）⇒ 不判 0 组" % p.returncode)
        return 2
    src = json.loads(io.open(tmpj, encoding="utf-8-sig").read())
    cands = src.get("polarity_candidates")
    if not isinstance(cands, list):
        print("[TRIAGE:UNVERIFIED] 源件无 polarity_candidates 面 ⇒ 不判通过")
        return 2
    if not cands:
        print("[TRIAGE:UNVERIFIED] 候选面为空：空面不得当「已复核」（R247）")
        return 2

    pairs, terms, rows = set(), set(), []
    for c in cands:
        term = str(c.get("term") or "?")
        mb, fb = base_rule((c.get("must") or {}).get("loc")), base_rule((c.get("forbid") or {}).get("loc"))
        pairs.add((term, mb, fb))
        terms.add(term)
        hits = is_form_meta((c.get("forbid") or {}).get("text"))
        rows.append({"term": term, "must_base": mb, "forbid_base": fb,
                     "must_loc": (c.get("must") or {}).get("loc"),
                     "forbid_loc": (c.get("forbid") or {}).get("loc"),
                     "form_meta_tokens": hits})
    dup = len(cands) - len(pairs)
    doc = {
        "schema": "conflict-triage-v2", "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True, "source": "05-exec/rule_conflict_scan.py --json（真实派发，不另起扫描）",
        "total_candidates": len(cands), "distinct_rule_pairs_after_volume_merge": len(pairs),
        "duplicated_pairs": dup, "distinct_terms": len(terms),
        "forbid_side_is_meta_about_presentation": sum(1 for r in rows if r["form_meta_tokens"]),
        "form_meta_token_table": list(FORM_TOKENS),
        "inflation_cause": "同一规则本体被拆成分卷载体（behavior_core_rules_pN / appendix），"
                           "一条 must 对多条 forbid 复制命中 ⇒ 组数被放大；归一到规则本体才是真对数",
        "semantic_verdict": "UNVERIFIED —— 是否构成真互斥须人工裁定：本项目红线禁止改受管根规则正文，"
                            "且 R241 只允许加校正注。本件只给可复算的结构数字与逐条定位。",
        "decision_needed": [{"id": "W-27", "要谁裁": "用户或受管根归属会话",
                             "裁什么": "每条 distinct pair 三选一：① 真互斥→改写其中一侧措辞 "
                                       "② 不互斥（语境不同）→在扫描器加**成对豁免**（须写明理由，"
                                       "禁整词豁免）③ 元规则让位于行为规则（禁侧只谈呈现形式时）",
                             "候选对数": len(pairs)}],
        "distinct_pairs": sorted([{"term": t, "must_base": m, "forbid_base": f}
                                  for (t, m, f) in pairs], key=lambda x: (x["term"], x["must_base"])),
        "rows": rows,
    }
    print("W-27 冲突面：原始候选 %d 组 ｜ 归一到规则本体 %d 对 ｜ 不同共用词 %d 个 ｜ 重复 %d 组"
          % (len(cands), len(pairs), len(terms), dup))
    print("  禁侧疑似呈现形式元规则：%d 组（token 表=%s）"
          % (doc["forbid_side_is_meta_about_presentation"], ",".join(FORM_TOKENS)))
    print("  语义裁定：UNVERIFIED（不改受管根规则正文，待人工裁定）")
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        out = sys.argv[2] if len(sys.argv) > 2 else None
        if out:
            io.open(out, "w", encoding="utf-8", newline="").write(
                json.dumps(doc, ensure_ascii=False, indent=1))
            print("JSON -> %s" % out)
    os.remove(tmpj)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
