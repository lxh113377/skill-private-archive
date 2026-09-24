# -*- coding: utf-8 -*-
"""r30_section_robustness.py - 任意 rubric 段的「判据稳健性」四档检验（只读，取代同名一次性工具）。

存在理由：r18~r28 的六段解剖结论建立在关键词锚点上，而锚点会把"对手恰好用了那个词"
误判成"对手做得更严"。r29 对 verification 实测出 32.4% 是措辞假阴性后，本工具把这套
自证流程推广成每次引用对标数字前的固定动作，四档：
  档1 现行尺      = skill_structure_rubric_scan.RUBRIC[section]（r18/r28 原尺，可比历史）
  档2 近义        = 同义词（严格同义：表达同一意图的不同词）
  档2b 宽近似     = 功能等价但语义更宽的写法（"我们其实有类似内容吗"的上界）
  档3 仅标题      = 只有小节标题命中才算（最严格，衡量"是否作为制度存在"）
输出真队列 = 档2b 仍缺 ∩ 自建维护面（HIGH+MID，见 r29_scope_filtered_queue.py 同一裁定文件）。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "05-exec"))
import skill_structure_rubric_scan as S  # noqa: E402
from skill_structure_rubric_scan import GS_ROOT, is_reparse_dir, frontmatter_fields  # noqa: E402
from r29_scope_filtered_queue import parse_scope, DIRTY_SKILLS  # noqa: E402

EXTRA = {
    "verification": {
        "near": [r"(质量门|质检|对账|复跑|复测|自证|校验|断言|退出码|exit\s*code|assert|回归|"
                 r"通过标准|达标|checklist|检查项|逐项检查|验证命令|proof|evidence|截图|录屏|日志|smoke)"],
        "broad": [r"(输出|产物|结果|报告).{0,6}(存在|非空|一致|正确)|Test-Path|可打开|可播放"],
        "heading": r"^#{2,4}\s*.*(验证|校验|核验|验收|证据|判据|质量门|质检|对账|退出条件|检查清单|"
                   r"Verification|Test|QA|Checklist|Evidence|Definition of Done|DoD|Exit)",
    },
    "rationalizations": {
        "near": [r"(反理性化|理性化|托词|借口|自我说服|自我辩解|偷懒|走捷径|搪塞|敷衍|"
                 r"Rationali[sz]ation|Anti-?[Rr]ational|excuse|temptation)"],
        "broad": [r"(反模式|常见误区|容易搞错|容易忽略|不要(做|用|以为)|不该|不宜|误用|滥用|"
                  r"禁忌|坑|慎用|禁止事项|不适用|何时不用|什么时候不用|别用|Don'?t|Never|Avoid|"
                  r"Anti-?[Pp]attern|pitfall|红线)"],
        "heading": r"^#{2,4}\s*.*(反理性化|理性化|托词|借口|反模式|常见误区|禁忌|红线|禁止|"
                   r"不适用|何时不用|边界|别用|坑|Don'?t|Never|Avoid|Rational|Anti-|Pitfall)",
    },
}


def build(pats):
    return [re.compile(p, re.I) for p in pats]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default="verification", choices=sorted(EXTRA))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--json")
    args = ap.parse_args()

    cfg = EXTRA[args.section]
    base = build(S.RUBRIC[args.section])
    near = build(S.RUBRIC[args.section] + cfg["near"])
    broad = build(S.RUBRIC[args.section] + cfg["near"] + cfg["broad"])
    heading = re.compile(cfg["heading"], re.M | re.I)

    tiers, err = parse_scope()
    if err:
        print("FAIL(R247): %s" % err)
        return 2

    rows = []
    for md in sorted(GS_ROOT.glob("*/SKILL.md")):
        if is_reparse_dir(md.parent):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        blob = body + "\n" + "\n".join(frontmatter_fields(text).values())
        t1 = any(r.search(body) for r in base)
        t2 = any(r.search(blob) for r in near)
        t3 = any(r.search(blob) for r in broad) or bool(heading.search(body))
        rows.append({"skill": md.parent.name, "bytes": len(text.encode("utf-8")),
                     "tier": tiers.get(md.parent.name, "UNLISTED"),
                     "t1": t1, "t2": t2, "t3": t3,
                     "heading_only": bool(heading.search(body))})
    N = len(rows)
    if N == 0:
        print("FAIL(R247): 枚举 0 个文件，不得出任何覆盖率结论")
        return 2
    c1, c2, c3 = (sum(1 for r in rows if r[k]) for k in ("t1", "t2", "t3"))
    print("=== rubric 段「%s」四档稳健性（n=%d，端 QD r30）===" % (args.section, N))
    print("档1 现行尺(标题锚点)      命中 %3d = %5.1f%% | 缺 %d" % (c1, 100.0 * c1 / N, N - c1))
    print("档2 +严格同义             命中 %3d = %5.1f%% | 缺 %d" % (c2, 100.0 * c2 / N, N - c2))
    print("档2b +功能等价宽写法      命中 %3d = %5.1f%% | 缺 %d" % (c3, 100.0 * c3 / N, N - c3))
    print("档3 仅小节标题(制度级)    命中 %3d = %5.1f%%" % (
        sum(1 for r in rows if r["heading_only"]),
        100.0 * sum(1 for r in rows if r["heading_only"]) / N))
    print("\n措辞假阴性：严格同义档2 - 档1 = %d 条（占档1 原判缺 %.1f%%）；"
          "宽近似档2b - 档1 = %d 条（占 %.1f%%）" % (
              c2 - c1, 100.0 * (c2 - c1) / max(1, N - c1),
              c3 - c1, 100.0 * (c3 - c1) / max(1, N - c1)))
    print("读法：档2 = 「确实有但换了词」；档2b = 「有相近的负面指引但未做成借口表」⇒ 借档2b 报缺口最保守，"
          "借档1 报缺口最激进，引用时必须指名档位。")

    def q(min_tier):
        out = [r for r in rows if not r[min_tier] and r["tier"] in ("HIGH", "MID")]
        return sorted(out, key=lambda r: -r["bytes"])

    hard, soft = q("t3"), q("t2")
    print("\n自建维护面真队列：档2b 仍缺 %d 条 | 档2（严格同义仍缺，最硬）%d 条" % (len(hard), len(soft)))
    print("队列 top %d（按体积降序；*=档2b 也缺，无*=仅严格同义缺）:" % args.top)
    for r in soft[: args.top]:
        flag = "⚠在途" if r["skill"] in DIRTY_SKILLS else ("  " if r in hard else "* ")
        print("  %-32s %7dB tier=%-4s %s" % (r["skill"], r["bytes"], r["tier"], flag))
    print("\n档2b 全缺且属自建（这批是无论如何都得补的）%d 条: %s" % (
        len(hard), ", ".join(r["skill"] for r in hard[:20])))

    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": "section-robustness-v2", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "readonly": True, "section": args.section, "n": N,
            "counts": {"tier1": c1, "tier2_near": c2, "tier2b_broad": c3,
                       "tier3_heading": sum(1 for r in rows if r["heading_only"])},
            "queue_strict": [{"skill": r["skill"], "bytes": r["bytes"]} for r in soft],
            "queue_all_tiers_missing": [{"skill": r["skill"], "bytes": r["bytes"]} for r in hard],
            "rows": rows,
            "caveat": "DIRTY_SKILLS 为 r29 一次实测快照，复用前须重跑受管根 git status 核对",
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2\n" % (exc,))
        raise SystemExit(2)
