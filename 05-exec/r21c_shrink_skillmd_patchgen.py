# -*- coding: utf-8 -*-
r"""r21c_shrink_skillmd_patchgen.py — 生成「A-memory-start/SKILL.md 版本历史区长条目换摘要」补丁。

来源: 焚诀 verify 实跑（C25 注入区 64,252B / 余量 220B，C31 告警「余量 <5%，再有一次技能增长即破硬顶」）
      + 其 P0-18 记账「A-memory-start/SKILL.md 21:25 一笔 +1085B 是击穿源，清红唯一正路 = 增长方瘦身」
      + 本仓实测：`wc -c SKILL.md`=27956、`grep -c V10.68.0/V10.69.0 references/version_history.md`=1/1（全文已在分卷）。
流向: 读本文件第 161/162 行原文作 `old`（**不手抄**，防 R271 型整行/子串语义错）→
      `rule_editor replace --patch` 换为一行摘要 → 注入面回吐 → 焚诀 C25 余量上升 →
      本仓 `ratchet_gate.py --update` 顺势收紧基线（只降不升方向合法）。
结构: 保留「V10.69.0」在区首条（C13 比对 frontmatter 与 `## 版本历史` 首条版本，删行即破坏该门禁）；
      两条长段落压缩为一行摘要 + 指向 references 分卷；不删任何规则本体、不改判据阈值。
异常: dry-run 未命中即不写盘；命中数≠2 视为文件已被并行会话改动 ⇒ 停手重测（R269 不覆写他人在途）。
"""

import json
import sys
from pathlib import Path

RE = Path(r"D:\global_skills\A-memory-start\SKILL.md")
OUT = Path(__file__).resolve().parent / "r21c-patches"
OUT.mkdir(exist_ok=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lines = RE.read_text(encoding="utf-8").split("\n")
    longs = [(i, l) for i, l in enumerate(lines)
             if l.startswith("> V10.68.0 (2026-09-24):") or l.startswith("> V10.69.0 (2026-09-24):")]
    if len(longs) != 2:
        print("[GUARD] 命中 %d 条长条目（期望 2）⇒ 文件形态与预期不符，停手不生成补丁" % len(longs))
        return 2
    hunks = []
    for _i, l in longs:
        ver = l.split("(")[0].strip("> ").strip()
        if l.startswith("> V10.69.0"):
            summ = ("> %s (2026-09-24): **rule_editor 写前脏源检测（受管根 9a15f4e）**"
                    "——脏源判定链与桩件详见 `references/version_history.md` 同版条目。"
                    "本行是 C13 门禁锚点，版本号须与 frontmatter `version:` 同步 bump。" % ver)
        else:
            summ = ("> %s (2026-09-24): **注入面端数口径改口八端（受管根 961bad6/33fcffd）**"
                    "——判据与夹具详见 `references/version_history.md` 同版条目。"
                    "本行是 C13 门禁锚点，版本号须与 frontmatter `version:` 同步 bump。" % ver)
        hunks.append({"old": l, "new": summ})
    p = OUT / "patch_shrink.json"
    p.write_text(json.dumps(hunks, ensure_ascii=False, indent=1), encoding="utf-8")
    back = json.loads(p.read_text(encoding="utf-8"))
    saved = sum(len(h["old"]) - len(h["new"]) for h in back)
    print("补丁已生成 %s：hunk=%d 预计回吐=%d 字符（≈%dB，CJK 按 UTF-8 3B/字估算更大）"
          % (p.name, len(back), saved, saved * 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
