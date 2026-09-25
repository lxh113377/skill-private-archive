# 05-feature-status.part27.md

<!-- 本卷为 05-feature-status.part26.md 的延续 -->

- **r36 引用可解析性维度轮（2026-09-25 第 36 轮）** — 新建第十二维尺（`05-exec/r36_cmd_resolvability.py`，只读、`--ours` 离线可跑）：首跑「0 DEAD」是**假绿**（只扫代码块 ⇒ 494 处漏检 454=92%），二跑「2 处 DEAD」是**假缺陷**（`../assets/x` 属产物 HTML 相对路径）；两次均由自抽验抓回。修正版真数 **1030 处 / 92.2% / 真 DEAD 0 / UNLOCATED 80 待定性**；受管根零改动（不制造假整改）。立 X-7（首跑干净≠结论）+ 判据输出文案须与实现同改。**并补正 r35 从未落库的记忆回写**（脚本只做替换未写盘却打印"done"，且提交漏跑 `git show --stat` 核对）。全文见 `06-benchmark/全量对标报告_r36_引用可解析性_2026-09-25.md`。

- **r37 门禁假阳性治理轮（2026-09-25 第 37 轮）** — 新建第十三维并**用它解除自身阻塞**：`handoff.py noise` 连红 7 轮的 5 条 VIOL 经取证全部为假阳性（3 条 Git 已跟踪治理件 + 2 条 `.git` 内工具运行态日志）。按 R263 改判据不改数据，上游 **A-project-handoff V3.54.1**（`b98cdb5` 代码 + 文档同步）落三件：`git_tracked()` 三重收窄放行 / 二级深扫跳过 `.git` / auto-memory 根件放行面扩到 `reference-*` 且不外溢。验证 = 层a 新桩 `05-exec/r37_noise_tracked_stub.py` **修前红 8 → 修后 16/16**（5 条保牙反例）+ 层b 四根 `[GATE:noise-pass]`（violation 全 0）+ 层c **`savepoint` 首次转绿**（AC-OBS-05 结束 7 轮连红）。配套：证据件 `06-benchmark/noise_falsepositive_r37_2026-09-25.json`（before 取自改动前自动备份原件实跑，非记忆值）+ 契约入册（10 pattern）+ **第 8 道常驻门 `noise_tracked_stub`**（`[GATES:PASS] PASS=8`）+ 立 **X-9**（禁为凑绿迁走/删除/改名 Git 已跟踪根部件）。自纠：首版桩 2 条**假反例**（未跟踪件写在 `git add -A` 之前、误判 `_bak` 可在名中命中——`STRAY_NAME` 实为行尾锚定）由 R220 抽验抓回后重做；`run_gates.py` 去掉硬编码「10 份/8 pattern」陈旧值，改指取值命令（L-5）。
