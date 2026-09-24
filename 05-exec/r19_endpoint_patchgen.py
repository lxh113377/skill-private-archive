# -*- coding: utf-8 -*-
r"""r19_endpoint_patchgen.py — 生成「注入面端数口径改口八端」的 rule_editor 补丁 JSON（三份）。

来源: `05-exec/claim_truth_scan.py` 首跑 10 条候选 + 本次逐行实测（`SKILL.md:32/60/92/131/135/139`、
      `contract.md:10/85` 行原文，已用 json.dumps 取字节精确文本，含 `D:\global_memory\` 单反斜杠
      与 `D:\\global_memory\\` 双反斜杠两种形态）；权威端清单 = `焚诀/eval/truth_constants.json`
      `endpoints.active`（8 端，C3/C16 实测 PASS）。
流向: 生成 `05-exec/r19-patches/patch_{skillmd,contract,vhist}.json` → 由 `rule_editor.py replace
      --patch` 落盘受管根 → 派生件不涉及（**只改正文与版本历史，未碰 frontmatter description**，
      故无需 build_indexes 重建；description 内的 `V9.7.0 瘦身版` 留待 R19-1 重建窗口）。
结构: 每份 JSON = 数组，元素 {old, new}；全部 UTF-8；行内子串替换（非整行覆盖，R271 语义）。
异常: rule_editor dry-run 任一条未命中 ⇒ 不写盘（脚本外由调用方按 rc 判断并停下修锚点）；
      历史句（OpenClaw 退役 / ZC 入役）不删不改，只在其后追加带日期的校正注（R241）。
"""

import io
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "r19-patches"
OUT.mkdir(exist_ok=True)

EIGHT = "HM/WB/CX/TC/ZC/OC/QW/QD"

SKILLMD = [
    {
        "old": "# A-memory-start — 全局记忆入口（V9.7.0 瘦身版）",
        "new": "# A-memory-start — 全局记忆入口（瘦身版 · 契约全文见 references/contract.md）",
    },
    {
        "old": "✅ G2 任务类型判定+平台探测: <闲聊/简单/继续/复杂> | <HM/WB/CX/TC/ZC> (统一路径已解析)",
        "new": "✅ G2 任务类型判定+平台探测: <闲聊/简单/继续/复杂> | <%s> (统一路径已解析，"
               "端数权威 = 焚诀/eval/truth_constants.json 的 endpoints.active)" % EIGHT,
    },
    {"old": "（V1.1：任务卡模板/五端适配/每端脚本/失败模式）",
     "new": "（V1.1：任务卡模板/八端适配/每端脚本/失败模式）"},
    {"old": "## File Resolution（五端统一，绝对路径）",
     "new": "## File Resolution（八端统一，绝对路径）"},
    {
        "old": r"| 权威源 | `D:\global_memory\`（五端 junction/镜像：HM/WB/CX/TC/ZC；TR=TRAE(别名 TC)；",
        "new": r"| 权威源 | `D:\global_memory\`（八端 junction/镜像：%s；TR=TRAE(别名 TC)；" % EIGHT,
    },
    {
        "old": "HM(Hermes) 于 2026-09-14 恢复在役（用户在役确认）；OC 已退役 2026-09-21 用户确认） |",
        "new": "HM(Hermes) 于 2026-09-14 恢复在役（用户在役确认）；OC 已退役 2026-09-21 用户确认"
               "【2026-09-24 校正注：退役的是 OpenClaw 本体；代号 oc 于 2026-09-23 由 OpenCode 接管复用"
               "（用户在役确认），qw/qd 于 2026-09-24 入役 ⇒ 在役端现为八端；原文保留不改，因其在当日为真】） |",
    },
    {"old": "| 意图路由（五端权威） |", "new": "| 意图路由（八端权威） |"},
    {"old": "version: 10.67.0", "new": "version: 10.68.0"},
    {
        "old": "> V10.67.0 (2026-09-23): **执行契约分卷拆分",
        "new": "> V10.68.0 (2026-09-24): **注入面端数口径改口八端（自建skill优化 r19 实物层实测发现）**——"
               "正文 `File Resolution`/G2 枚举/意图路由行仍写「五端 / `<HM/WB/CX/TC/ZC>`」，与真相源 "
               "`endpoints.active`=8 端脱节（oc 代号被 OpenCode 接管复用、qw/qd 入役后文本未跟）；"
               "H1 与正文的「V9.7.0 瘦身版」版本戳一并改为无戳表述（防同类漂移复发）。"
               "只改正文与版本历史，**未碰 frontmatter description** ⇒ 不触派生件重建；"
               "description 内同串留待重建窗口（登记为待办）。验证：`05-exec/claim_truth_scan.py` 复跑 "
               "endpoint 族候选由 6 句降至 0；新增夹具 `05-exec/r19_baseline_contract_fixtures.py` 18/18 + "
               "变异对照 `05-exec/r19_fixture_mutation_check.py` 4/4。"
               "本行是 C13 门禁锚点，版本号须与 frontmatter `version:` 同步 bump。\n"
               "> V10.67.0 (2026-09-23): **执行契约分卷拆分",
    },
]

CONTRACT = [
    {"old": "> 🔴 **统计口径铁律（五端生效）**：", "new": "> 🔴 **统计口径铁律（八端生效）**："},
    {
        "old": r"五端共享 D:\\global_memory\\（HM/WB/CX/TC/ZC；ZC 于 2026-09-22 入役）；"
               r"0.1.2-0.1.3 权威启动表与五端速查见 references/detail_archive.md。",
        "new": r"八端共享 D:\\global_memory\\（%s；ZC 于 2026-09-22 入役，"
               r"代号 oc 于 2026-09-23 由 OpenCode 接管复用【原文「OC 已退役」指 OpenClaw 本体，"
               r"留痕不改】，qw/qd 于 2026-09-24 入役）；"
               r"0.1.2-0.1.3 权威启动表与八端速查见 references/detail_archive.md。" % EIGHT,
    },
]

VHIST = [
    {
        "old": "> V10.67.0 (2026-09-23): **执行契约分卷拆分（P0-2）**",
        "new": "> V10.68.0 (2026-09-24): **注入面端数口径改口八端（自建skill优化 r19 实物层实测发现）**——"
               "`claim_truth_scan.py` 首跑 10 条候选，其中 6 条落在本 skill 每轮注入文本面："
               "`SKILL.md` L60 平台枚举 `<HM/WB/CX/TC/ZC>`、L92「五端适配」、L131「五端统一」、"
               "L135「五端 junction/镜像」+「OC 已退役」、L139「五端权威」与 `contract.md` L10「五端生效」/"
               "L85「五端共享」；真相源 `焚诀/eval/truth_constants.json` `endpoints.active` = 8 端"
               "（wb/tr/cx/hm/zc/oc/qw/qd；oc 代号 09-23 由 OpenCode 接管复用、qw/qd 09-24 入役）。"
               "H1「V9.7.0 瘦身版」版本戳同步改为无戳表述。范围纪律：**只改正文与版本历史，"
               "不碰 frontmatter description**（description 属注册表/BGE/skill_content 派生件镜像，"
               "改它必须整链重建，按「派生件三方脱节」教训留待重建窗口）；历史句一律保留原文、"
               "其后追加带日期校正注（R241）。验证：`python 05-exec/claim_truth_scan.py` endpoint 族候选 "
               "6→0；`python 05-exec/r19_baseline_contract_fixtures.py` 18/18；"
               "`python 05-exec/r19_fixture_mutation_check.py` 变异 4/4 被拦（含未变异对照组）。"
               "同步 frontmatter 10.67.0 → 10.68.0。\n"
               "> V10.67.0 (2026-09-23): **执行契约分卷拆分（P0-2）**",
    },
]


def dump(name, payload):
    p = OUT / name
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def main():
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    for fname, data in (("patch_skillmd.json", SKILLMD), ("patch_contract.json", CONTRACT),
                        ("patch_vhist.json", VHIST)):
        p = dump(fname, data)
        with io.open(p, "r", encoding="utf-8") as f:
            back = json.load(f)
        print("%-24s hunk=%d 读回=%s" % (p.name, len(back), "OK" if len(back) == len(data) else "FAIL"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
