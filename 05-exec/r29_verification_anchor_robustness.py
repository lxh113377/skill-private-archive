# -*- coding: utf-8 -*-
"""r29_verification_anchor_robustness.py - 判据稳健性检验：verification 缺口有多少是措辞假阴性（只读）。

触发：r29 实测 story-scan 带「采集质量门（必做）」却被判 verification=false
⇒ 现行锚点集（验证/验收/证据/判据/核验/检查清单/退出条件/门禁/实测 + 少量英文）过窄。
对标结论若建立在锚点措辞上，就是把"对手用了这个词"当成"对手做得更好"。
本工具用三档锚点集对同一批文件重跑，量化措辞占比，并把三档全 FAIL 的项留作真队列。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "05-exec"))
from skill_structure_rubric_scan import GS_ROOT, is_reparse_dir, frontmatter_fields  # noqa: E402
from r29_scope_filtered_queue import parse_scope, DIRTY_SKILLS  # noqa: E402

# 档位1：现行尺（与 skill_structure_rubric_scan.RUBRIC['verification'] 同源，禁止各说各话）
import skill_structure_rubric_scan as S  # noqa: E402
NARROW = S.RUBRIC["verification"]

# 档位2：宽锚点（补同族写法：质量门/对账/复跑/自证/校验/退出码/断言/截图/日志…）
WIDE_EXTRA = [r"(质量门|质检|对账|复跑|复测|自证|校验|断言|退出码|exit\s*code|assert|"
              r"截图|录屏|日志|smoke|回归|通过标准|达标|checklist|检查项|逐项检查|"
              r"验证命令|验收|proof|evidence)"]

# 档位3：段落级（标题行含校验词才算，避免正文顺带一提也计分）
HEADING_ONLY = re.compile(
    r"^#{2,4}\s*.*(验证|校验|核验|验收|证据|判据|质量门|质检|对账|退出条件|检查清单|"
    r"Verification|Test|QA|Checklist|Evidence|Definition of Done|DoD|Exit)",
    re.M | re.I)


def build(patterns):
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    rx_narrow, rx_wide = build(NARROW), build(NARROW + WIDE_EXTRA)
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
        fields = frontmatter_fields(text)
        fm = "\n".join(fields.values())
        n = any(r.search(body) for r in rx_narrow)
        w = n or any(r.search(body) for r in rx_wide) or any(r.search(fm) for r in rx_wide)
        h = bool(HEADING_ONLY.search(body))
        rows.append({"skill": md.parent.name, "bytes": len(text.encode("utf-8")),
                     "tier": tiers.get(md.parent.name, "UNLISTED"),
                     "narrow": n, "wide": w or h, "heading": h})

    N = len(rows)
    if N == 0:
        print("FAIL(R247): 枚举 0 个 SKILL.md，不得下结论")
        return 2
    cn = sum(1 for r in rows if r["narrow"])
    cw = sum(1 for r in rows if r["wide"])
    ch = sum(1 for r in rows if r["heading"])
    print("=== verification 三档锚点稳健性检验（n=%d）===" % N)
    print("档1 现行尺(标题锚点)  命中 %3d = %5.1f%%  | 缺失 %d" % (cn, 100.0 * cn / N, N - cn))
    print("档2 +同族措辞/宽锚点  命中 %3d = %5.1f%%  | 缺失 %d" % (cw, 100.0 * cw / N, N - cw))
    print("档3 仅段落标题命中    命中 %3d = %5.1f%%  | 缺失 %d" % (ch, 100.0 * ch / N, N - ch))
    art = (cw - cn)
    print("\n措辞假阴性量级: 档2 - 档1 = %d 条（占原判缺口的 %.1f%%）" % (
        art, 100.0 * art / max(1, N - cn)))
    print("=> 原报「verification 缺 40.4%%」里，%d 条只是没用那组词；" % art)
    print("   真缺口 = 档2 仍缺的 %d 条。" % (N - cw))

    true_q = [r for r in rows if not r["wide"]]
    in_scope = sorted([r for r in true_q if r["tier"] in ("HIGH", "MID")], key=lambda r: -r["bytes"])
    print("\n三档全缺 且 属自建维护面（真 H2 队列）%d 条:" % len(in_scope))
    for r in in_scope:
        flag = " ⚠在途" if r["skill"] in DIRTY_SKILLS else ""
        print("  %-34s %7dB tier=%-4s%s" % (r["skill"], r["bytes"], r["tier"], flag))
    print("\n（对照：档1 缺但档2 命中 = 纯措辞差异样本 top6: %s）" % ", ".join(
        [r["skill"] for r in rows if r["wide"] and not r["narrow"]][:6]))

    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": "verification-anchor-robustness-v1",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "readonly": True,
            "n": N, "narrow": cn, "wide": cw, "heading_only": ch,
            "wording_artifact_count": art,
            "true_queue_in_scope": in_scope,
            "true_queue_all": [{"skill": r["skill"], "tier": r["tier"]} for r in true_q],
            "anchor_sets": {"narrow": NARROW, "wide_extra": WIDE_EXTRA},
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
