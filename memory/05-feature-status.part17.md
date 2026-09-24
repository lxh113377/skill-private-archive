# 05-feature-status 分卷 17 — 已完成：2026-09-24 第 21 轮（r20 机制化轮）

> 主壳只留一行指针，本卷承载全文（R224 条目级归档口径）。

- **r20 机制化轮（2026-09-24，第 21 轮，QD 端）** — 用户对 r19b 回复的两条「未闭环升级建议」加标注 ⇒ 先自查上一轮给出的阻塞理由是否成立，结论 **两条都过度保守**：`rule_editor.py` 与 `A-get-memory/SKILL.md` 均在 `D:/global_skills`（不属焚诀 `eval/` 只读红线），且本仓 r13 的 B4 早有直接改 `rule_editor.py`（备份落点迁出受管根）的先例。
  - **落地机制 ①：rule_editor「写前脏源检测」（受管根 `9a15f4e`，A-memory-start `version: 10.69.0`）**。判据：既有归属校验只回答「我写完之后有没有被人再改」，不回答「我**动手以前**它脏不脏」——后者才是本仓两次整文件夹带的真根因（`f6f5b0c` 把并行会话在 `splitvol.py` 的在途 1 行带进我的提交；`4b75d80` 把我的 `contract.md` hunks 带进他人提交）。实现：`write_text` 写前取磁盘指纹、写后把 `rel/pre_sha/post_sha` 追加到 `BACKUP_DIR/write_chain.jsonl`（BACKUP_DIR 自 B4 起在受管根外，不污染 `git status`）；`commit` 在 staging **之前**比对「HEAD 指纹 vs 写入链」——脏且链上无记录即判多源共存，**fail-closed 中止**并给逐文件处置建议；确需放行加 `--allow-dirty-source`，落 `dirty_source_overrides.jsonl` 留痕。边界：HEAD 不可读（新文件）与磁盘指纹读空一律不报（不猜测）；写入链按 `rel` 隔离，防跨文件背书。
  - **验证（严格 TDD + 两层含对照，R238）**：先写 `05-exec/r20_dirty_source_stub.py` 跑出红（`FAIL RED 前置：_multi_author_findings 已实现`）→ 实现 → **10/10 `[GATE:stub-pass]`**；层 a 7 例已知答案（干净基座不误报 / 自有链中间态不误报 / 他人在途必报 / 文案含可执行处置 / HEAD 不可读不报 / 指纹读空不报 / 链按文件隔离）；层 b′ 用**真实数据两侧**：受管根现有他人在途文件被点名（真阳性）+ **生效路径由随后 V10.69.0 那次正常提交实测未被拦**（链上自有记录 ⇒ 不误报）。迁移首笔（`rule_editor.py` 自身由旧版写入、链上无记录）按新判据被正确拦截，据实走 `--allow-dirty-source` 并写明归因。
  - **落地机制 ②（改为备好补丁）**：`A-get-memory` 的「判据类工具交付三条硬判据」条款——该文件此刻被并行会话占用（staged `M`、版本已 4.29.0），**新落地的脏源门禁本就 fail-closed 拦这种提交**，故不硬闯；补丁与一键命令、验收判据放 `05-exec/r20-patches/patch_agetmemory_jig_clause.json` + `README_agetmemory_jig_clause.md`，待归属会话收口后落地。
  - **回归**：本仓三条门禁命令（`r19_scan_fixtures.py` 55/55、`r19_baseline_contract_fixtures.py` 18/18、`baseline_contract_scan.py` `[CONTRACT:PASS]` 8 份基线）全绿；受管根 `gates` = mirror/noise/evolution pass（`stub` 一红 = 焚诀在途 C29）；`verify_truth_consistency.py` = 29 PASS / 1 FAIL（同因，外部）；C13 版本线 PASS。
  - **登记**：受管根出现 staged-but-uncommitted（`A-get-memory` 首列 `M`）属并发风险信号，本仓未做任何 `git add`/`reset` 触碰。
