# -*- coding: utf-8 -*-
"""阶段5-② 从 retired_skills 黑名单摘除 31 个「磁盘在役但被误列退役」的 skill（2026-09-22）

背景（✅已实测）：`build_registry.scan_disk_skills()` 会跳过 `truth_constants.RETIRED_SKILLS` 命中的
磁盘 skill（R198.6 fail-closed「禁止批量入库还原」）。实测这 31 个（**21 个市场件 + 10 个 local-* 族**，
与磁盘实测交集精确核对）
**全部命中黑名单但从未被移除**，因此长期不入册。用户 2026-09-22 裁定：**全部 31 个入册**。

用法：
  python unretire_31.py            # dry-run：只打印将摘除的名字与前后条数
  python unretire_31.py --apply    # 写回 truth_constants.json（原地、保持 indent=2 / ensure_ascii=False）
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TC = Path(r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json")

TARGETS = [
    # 21 个市场件（2026-09-21 OC 卸载时按「插件源技能」登记退役，其后经市场重新安装回磁盘）
    "brainstorming", "brand-guidelines", "chart-visualization", "defuddle", "executing-plans",
    "figma", "frontend-design", "internal-comms", "json-canvas", "knowledge-capture",
    "meeting-intelligence", "notion-cli", "obsidian-bases", "obsidian-cli", "obsidian-markdown",
    "research-documentation", "slides", "spec-to-implementation", "test-driven-development",
    "theme-factory", "writing-plans",
    # 10 个 local-*（Intel 分发样例包；灰区裁定 = 排除「维护范围」，用户裁定仍入册）
    "local-asr", "local-computer-use", "local-img2img", "local-mineru", "local-ocr-npu",
    "local-realtime-translator", "local-screenshot-qa", "local-tts", "local-txt2img", "local-vram",
]


def main():
    apply = "--apply" in sys.argv
    data = json.loads(TC.read_text(encoding="utf-8"))
    before = list(data["retired_skills"])
    # 注：TARGETS 里 20 个市场件的清单实为 21 项（含 writing-plans）——以「磁盘实测∩黑名单」为准，
    # 这里按实际交集摘除，避免手抄清单与磁盘不一致。
    hit = sorted(set(before) & set(TARGETS))
    data["retired_skills"] = [n for n in before if n not in set(hit)]

    print("黑名单摘除: %d 个（前 %d → 后 %d）" % (len(hit), len(before), len(data["retired_skills"])))
    for n in hit:
        print("   - %s" % n)
    if not apply:
        print("DRY-RUN：未写盘（加 --apply 才写）")
        return 0

    data["_meta"] += ("; 2026-09-22 用户裁定「31 个磁盘在役件入册」：从 retired_skills 摘除 "
                      + str(len(hit)) + " 项（20 个市场件为 2026-09-21 OC 卸载时登记、其后经市场重装回磁盘；"
                      "11 个 local-* 为 Intel 分发样例包，灰区裁定仅限「维护范围」不含入册）")
    TC.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    re_read = json.loads(TC.read_text(encoding="utf-8"))
    ok = len(re_read["retired_skills"]) == len(before) - len(hit)
    print("写后守恒校验: %s（%d 条）" % ("PASS" if ok else "FAIL", len(re_read["retired_skills"])))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
