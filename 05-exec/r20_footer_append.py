# -*- coding: utf-8 -*-
r"""r20_footer_append.py — 把 r20 轮次的 GM 日志段 + 数据流假设 + footer 锚点块落盘（幂等）。

来源: 本轮实测（受管根 `9a15f4e` rule_editor 写前脏源检测、A-memory-start frontmatter 10.69.0、
      `05-exec/r20_dirty_source_stub.py` 10/10、受管根 29 条他人在途、A-get-memory 为 staged M）。
流向: 本脚本 → `D:\global_memory\memory\2026-09-24.md`（append-only）→ 下游
      `upgrade_footer_gate.py` 取全局最后一个完整块校验 → [GATE:evolution-*]。
结构: UTF-8 无 BOM；footer = begin 标记 + [skill清单] 恰 1 行 + [升级建议] ≤ N+1 行 + end 标记；
      已含同一 session 标记则跳过（幂等）。
异常: 写后读回八项锚点（R213），缺任一 exit 1；不覆盖他人已追加内容（只在文末 append）。
"""

import io
import os
import sys

LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r20-0924"

BLOCK = """
## 19:0x 自建skill优化 r20（第三次标注驱动·机制化轮，QD 端）
- 对 r19b 两条「未闭环升级建议」再加标注 ⇒ 先复核自己上一轮的阻塞理由，结论是**两条都过度保守**：`rule_editor.py` 与 `A-get-memory/SKILL.md` 都在 `D:\\global_skills`（不属焚诀 `eval/` 只读红线），且本仓 r13 的 B4 早有直接改 `rule_editor.py` 的先例。
- **落地「写前脏源检测」**（受管根 `9a15f4e`，A-memory-start **V10.69.0**）：`write_text` 写前取磁盘指纹、写后把 rel/pre_sha/post_sha 追加 `write_chain.jsonl`（在受管根外，不污染 status）；`commit` 在 staging 前比对「HEAD 指纹 vs 写入链」——动手前即脏且链上无记录 ⇒ **fail-closed 中止** + 逐文件处置建议，放行须 `--allow-dirty-source` 并落 override 留痕。根因 = 本仓两次整文件夹带（f6f5b0c 我带走他人 splitvol 1 行 / 4b75d80 他人带走我的 contract.md hunks），而既有归属校验只查「写完后有没有被再改」，两次都落在它盲区。
- 验证（TDD + 两层含对照）：`05-exec/r20_dirty_source_stub.py` 先跑出红（`_multi_author_findings` 不存在）→ 实现 → **10/10**；层 a 7 例已知答案；层 b′ 两侧实测 = 受管根真实他人在途文件被点名（真阳性）+ V10.69.0 正常提交未被误拦（生效路径，链上自有记录）；迁移首笔（rule_editor.py 由升级前旧版写入、链上无记录）**被新判据正确拦下**，据实走逃生门并写明归因。
- `A-get-memory` 条款不硬闯（该文件被并行会话 staged 占用，版本已 4.29.0，新门禁本就拦）⇒ 备好 `05-exec/r20-patches/patch_agetmemory_jig_clause.json` + README 一键命令与验收判据，交归属会话。
- 回归：本仓门禁三条 55/55 + 18/18 + `[CONTRACT:PASS]`（8 份基线）全绿；受管根 mirror/noise/evolution pass（stub 一红 = 焚诀在途 C29）；verify 29 PASS/1 FAIL 同因；C13 PASS。

【数据流假设】
来源: `D:\\global_skills\\A-memory-start\\references\\rule_editor.py` 实测行文本（第 80 模块级 flag、192-196 write_text、884-888 git add 循环、1364-1365 main global、1379 argparse 循环、1415 flag 取值）+ `git status --porcelain` 29 条他人在途 + `_head_blob`/`_file_sha256` 既有指纹工具
流向: `05-exec/r20_dirty_source_patchgen.py` → `05-exec/r20-patches/patch_ruleeditor.json`（6 hunk，dry-run 全命中才写盘）→ rule_editor 自身 replace --no-commit（旧版执行，故链上无记录）→ commit 时**新判据真的触发**→ `--allow-dirty-source` 落 `dirty_source_overrides.jsonl` → 之后 SKILL.md/version_history 由新版写入（链上有记录）→ commit 无告警（生效路径实证）；下游消费者 = 所有走 rule_editor 的会话
结构: `write_chain.jsonl` 每行仅 {rel, pre_sha, post_sha}（无时间戳依赖，避免新增 import）；BACKUP_DIR 在受管根外 ⇒ 链文件不进 `git status`；HEAD 指纹读不到（新文件）或磁盘指纹读空 → 判「不报」；链按 rel 隔离（防跨文件背书）
异常: 编号预检两次 fail-closed 且都是**真问题**——提交说明含旧 R 号（改措辞根治，不走逃生门）；迁移首笔脏源（正当场景，用 `--allow-dirty-source` 一次并在说明内写归因）；`-Fix` 单向 源→镜像 后 mirror 复跑 pass；受管根他人在途（A-get-memory 已 staged）不做任何 `git add`/`reset` 触碰

<!-- footer:begin session=qd-zijian-r20-0924 ts=2026-09-24T19:10:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-memory-start, A-get-memory)
[升级建议] skill=A-memory-start | 五问=缺失步骤 | 改法=rule_editor commit 前增加写前脏源检测并 fail-closed | 对照=已取(证据=迁移首笔被新判据拦下需显式放行，V10.69.0 正常提交链上有记录未被误拦，两侧均实跑) | 状态=已闭环(证据=D:\\global_skills\\A-memory-start\\SKILL.md#版本行:V10.69.0)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=交付判据类工具前强制跑夹具门禁 | 对照=已取(证据=未变异夹具 PASS 与 4 项判据变异全部 rc=1 被拦) | 状态=未闭环(原因=该文件被并行会话 staged 占用(版本已 4.29.0)，新落地的脏源门禁对此类提交 fail-closed；补丁与一键命令已备 05-exec/r20-patches/patch_agetmemory_jig_clause.json + README，交归属会话落地)
<!-- footer:end -->
"""

NEED = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = io.open(LOG, encoding="utf-8-sig").read()
    if KEY in log:
        print("[SKIP] r20 footer 已存在（幂等）")
        return 0
    with open(LOG, "wb") as f:
        f.write((log.rstrip("\n") + "\n" + BLOCK).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    miss = [k for k in NEED if k not in back]
    print("[GM日志] 读回验证=%s | 缺失=%s | 文件=%dB" % (not miss, miss or "-", os.path.getsize(LOG)))
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
