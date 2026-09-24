# -*- coding: utf-8 -*-
r"""r19b_footer_append.py — 把 r19b 轮次的 GM 日志段 + 数据流假设 + footer 锚点块落盘（幂等）。

来源: 本轮实测（受管根 `961bad6`/`33fcffd`、claim 候选 10→4、镜像 -Fix 后三门 pass、
      夹具 18/18 与变异 4/4、`git log -S` 归因夹带来源 4b75d80）。
流向: 本脚本 → `D:\global_memory\memory\2026-09-24.md`（append-only 权威端日志）
      → 下游门禁 `upgrade_footer_gate.py`（取全局最后一个完整块校验）→ [GATE:evolution-*]。
结构: UTF-8 无 BOM；footer 块 = begin 标记 + [skill清单] 恰 1 行 + [升级建议] ≤ N+1 行 + end 标记；
      已含同一 session 标记则跳过（幂等，防重复追加）。
异常: 写后读回验证八项锚点（R213），缺任一项即 exit 1 并打印缺失清单（禁静默成功）。
"""

import io
import os
import sys

LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r19b-0924"

BLOCK = """
## 18:5x 自建skill优化 r19b（标注驱动续做，QD 端）
- 用户对 r19 回复的「两条未闭环升级建议 + 三条下一步」加标注 ⇒ 按既有授权把可做部分全部做完：R19-3 契约族（`schemas/r19/baseline-contracts.json` 8 pattern / 13 条具名不变式 + `baseline_contract_scan.py`；严格 TDD：先看夹具红 → 实现 → 18/18，真跑 8 份基线 `[CONTRACT:PASS]`）；夹具「有牙」对照补齐（`r19_fixture_mutation_check.py` 变异 4/4 被拦 + 未变异对照组 PASS）；三条命令写入 `memory/AGENTS.md`「项目门禁命令」段 = 自觉型升机器型。
- 注入面端数失真 6 句改口八端：受管根 `961bad6` + `33fcffd`（A-memory-start **V10.68.0**，C13 PASS），`claim_truth_scan` 候选 **10→4**、A-memory-start 端数族归零；**未碰 frontmatter description**（派生件镜像须整链重建，留 R19-1）；`check-skill-mirror.ps1 -Fix` 后 mirror/noise/evolution pass。
- 三处新发现并登记：① 拟提判据与焚诀本轮新落地 C29（index.md 对账）撞号 ⇒ 转办项重编号 C30′/C31′/C32′；② `rule_editor commit` 整文件夹带**二次复现**（我在 contract.md 的在途 hunks 被并行 `4b75d80` 带走，内容无损，`grep -c 八端`=2 实测）⇒ 「同文件他人改动预检」建议升 P1；③ 余下 4 候选中 `A-get-memory`「四端版本号」2 处经复核为语义误报（指 VERSION_LOCK 组件非在役端）⇒ 登记扫描器盲区，不改数据凑绿。
- 逃生门 `--allow-collide` 用 1 次并归因（读台账：近 30 天累计 1 次）= 同会话同版本分两笔收口（第二笔 replace 漏加 `--no-commit` 提前入库），非跨会话撞号。

【数据流假设】
来源: `05-exec/r19-patches/*.json` 与受管根 `A-memory-start/SKILL.md`、`references/contract.md`、`references/version_history.md` 行原文（先 json.dumps 取字节精确文本，实测 SKILL.md 第 60/92/131/135/139 行与 contract.md 第 10/85 行）+ `焚诀/eval/truth_constants.json` endpoints.active=8（C3/C16 PASS）+ `焚诀/skill/registry/disk_manifest.json` count=167
流向: 三份 patch JSON → `rule_editor.py replace --patch`（dry-run 先行：9/2/1 处全命中）→ 受管根正文与版本历史 → Codex 镜像 `C:\\Users\\37533\\.agents\\skills`（`check-skill-mirror.ps1 -Fix` 单向 源→镜像）→ 下游 `claim_truth_scan` 与 verify C13 复跑；新契约 JSON → `baseline_contract_scan.py` → `06-benchmark/baseline_contract_check_2026-09-24.json` → 07/05 台账引用。**不写 frontmatter description ⇒ 不触注册表/BGE/skill_content 重建链**
结构: 受管根用行内子串替换（R271 语义，禁整行覆盖）；UTF-8 无 BOM；version_history 必须含 V10.68.0 条目，否则 C13「frontmatter == 版本历史最大版本」失效；契约 required 走点路径、invariants 走具名注册表键（未知键 = 报「契约与实现脱节」）；记忆体字节数 05 主壳 2962B / part15 3287B / part16 1923B 全部 ≤4096B 硬判据
异常: 编号预检 fail-closed 两次——R241 撞号（改措辞根治，不走逃生门）与 V 号未超基线（正当同号，`--allow-collide` 并读台账归因）；dry-run 未命中即不写盘；镜像 mismatch=4 走「只读检查 → -Fix → 复核」三步至 mirror=pass；契约 pattern 零命中或 artifacts 为空 ⇒ 判 FAIL（禁「无文件=通过」R247）；注册表 manifest 不可读 ⇒ consistent=None 不静默；本脚本写后读回缺锚点 ⇒ exit 1

<!-- footer:begin session=qd-zijian-r19b-0924 ts=2026-09-24T18:55:00+08:00 -->
[skill清单] 本轮调用=3 个 (A-memory-start, A-get-memory, superpowers:test-driven-development)
[升级建议] skill=A-memory-start | 五问=过期指令 | 改法=注入面端数口径改口八端并去版本戳 | 对照=已取(证据=改前 claim_truth_scan 10 候选含本文件 6 句，改后端数族归零且 gates mirror/noise/evolution pass、C13 PASS) | 状态=已闭环(证据=D:\\global_skills\\A-memory-start\\SKILL.md#版本行:V10.68.0)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=交付判据类工具前强制跑夹具门禁 | 对照=已取(证据=未变异夹具 PASS 与 4 项判据变异全部 rc=1 被拦，两侧均实跑) | 状态=未闭环(原因=本仓落点已挂 memory/AGENTS.md 项目门禁命令段，全局落点须登记焚诀 eval/stubs/registry.json，本项目对焚诀 eval/ 只读)
[升级建议] skill=rule_editor | 五问=错误信息 | 改法=commit 前增加同文件他人改动预检 | 对照=已取(证据=同类夹带二次复现，r18 f6f5b0c 与本轮 4b75d80 均为整文件提交带走他人在途 hunks) | 状态=未闭环(原因=rule_editor 属受管根 A-memory-start/references，改其提交语义影响全部会话，转归属会话并建议升至 P1)
<!-- footer:end -->
"""

NEED = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = io.open(LOG, encoding="utf-8-sig").read()
    if KEY in log:
        print("[SKIP] 本会话 r19b footer 已存在（幂等）")
        return 0
    with open(LOG, "wb") as f:
        f.write((log.rstrip("\n") + "\n" + BLOCK).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    miss = [k for k in NEED if k not in back]
    print("[GM日志] 读回验证=%s | 缺失锚点=%s | 文件=%dB" % (not miss, miss or "-", os.path.getsize(LOG)))
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
