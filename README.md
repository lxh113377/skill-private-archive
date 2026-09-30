# 自建 skill 体系优化审计 — 工作区入口

> 更新：2026-09-22 | **跨会话入口 = `memory/07-next-steps.md`（P0 唯一真相源）**
> 权威源：`D:\global_skills`（git）→ 镜像 `C:\Users\37533\.agents\skills`

## 从哪读起（新人 / 新会话，按序）

1. [memory/07-next-steps.md](memory/07-next-steps.md) — P0 未完成项（**唯一入口，先读这个**）
2. [memory/05-feature-status.md](memory/05-feature-status.md) — 已完成 / 进行中 / 阻塞
3. [05-exec/第3轮执行报告.md](05-exec/第3轮执行报告.md) — 最近一轮：四维诊断 + 建议清单 + 待确认破坏性项
4. [03-audit/自建skill优化审计报告.md](03-audit/自建skill优化审计报告.md) — 阶段3 全量审计结论（P0/P1/P2）
5. [04-plan/实施计划.md](04-plan/实施计划.md) — 阶段4 分批复核与回滚手段

## 六阶段产物地图

| 阶段 | 目录 | 产物 | 状态 |
|---|---|---|---|
| 0 范围裁定 | `00-scope/` | 自建skill清单.md / 注册表失真条目.md / scope_result.json | ✅ 完成 |
| 1 四维机器扫描 | `01-scan/` | scan_report.md / scan_result.json / scan_all.py（`overlap_raw.txt` 已迁 `archive/`，2026-09-23 r8 修正此前未同步的索引） | ✅ 完成（第10轮已补齐；2026-09-23 dry-run scope/scan均exit 0） |
| 2 全量精读 | `02-review/` | 6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他） | ✅ 完成 |
| 3 审计报告 | `03-audit/` | 自建skill优化审计报告.md | ✅ 完成 |
| 4 实施计划 | `04-plan/` | 实施计划.md / 剩余待办分类清单.md / 工作流专项建议.md | ✅ 完成 |
| 5 执行 | `05-exec/` | README.md（补丁索引）/ 第2轮·第3轮·第10轮执行报告 / 19 个 patch JSON + D1/D4/D5/R270/R271 补丁目录 | ✅ 完成 |
| 记忆 | `memory/` | handoff 8 文件 + 分卷 + P-1 绑定表（AGENTS.md） | ✅ 建档 |

## 边界与铁律

- 阶段 0-3 **只读取证**；阶段 4 起才改 `D:\global_skills`，且**唯一途径 = `rule_editor.py`**（禁 `write_file` 整体重写 skill 文件）。
- 改完必须：重建派生件 → 复跑三门禁（mirror / noise / evolution）。
- 结论一律标注 `✅已实测 / ⚠️部分实测 / ❌未实测`；禁用旧快照、旧记忆、历史报告当现状。
- 落盘编辑前必须输出 `【数据流假设】` 四要素。

## 收口门禁（改完必须复跑）

```powershell
$env:PYTHONPYCACHEPREFIX="$env:TEMP\pycache_verify"
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-memory-start\references\rule_editor.py" gates
Set-Location 'C:\Users\37533\Desktop\workspace\焚诀'; & "C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe" eval/verify_truth_consistency.py
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-project-handoff\scripts\handoff.py" review "c:\Users\37533\Desktop\workspace\自建skill优化"
```

> 实测基线（2026-09-22）：`gates` = `mirror=pass noise=pass evolution=pass`；焚诀 `verify` = **15 PASS / 0 FAIL / 0 SKIP**；`handoff review` = 5/9（56%）→ 本轮整改后 **7/9（78%）**。
> ⚠️ **校正注（2026-09-22 第 10 轮，R241 只加注不改写）**：上行为当日**当时为真**的数值。当前实测已推进 —— `handoff review` = **9/9（100%）**（D1 修 3 处判据缺陷后）、`handoff status` = **8/8 sections filled**、焚诀 `verify` = **16 PASS / 0 FAIL / 0 SKIP**（新增 C15/C16）、本项目 HEAD = `632d183`。最新数值以本注为准。
> ⚠️ **追加说明（同日，R241 只加注不改历史）**：
> ① `handoff review` 剩余 2 条 warning **均为上游判据缺陷**所致（非内容缺失），见 `memory/06-constraints.md` [BUG]；
> ② `handoff savepoint` 中途曾 1 次被拒（`焚诀\.codebuddy` 未 gitignore 豁免），已由**并行会话**（焚诀 commit `1f354e9`）解除，最终 **exit 0 通过**——详见 `05-exec/第3轮执行报告.md` 第五-附节（含「活跃工具目录不能迁 `_trash`」与「时间戳盲区」两条教训）。

## 版本控制基线（A-project-handoff 致命纪律 #20）

- 远端：`https://github.com/lxh113377/skill-private-archive.git`（私有归档仓）
- 判据：`git rev-parse HEAD` == `git ls-remote origin main` 的 SHA

## 证据面导航（r53 起；对标 `addyosmani/agent-skills` README 挂 50 个文件链接的做法）

> 入口文档只**指路**、不抄数值：正文数字写成台账字段引用（句柄），
> 由 `python 05-exec/r38_debt_aging.py` 现取；源头取不到必须显形为 None，不得沿用旧值。

### 可再生台账

- [debt_runs.jsonl](06-benchmark/debt_runs.jsonl) — 现值由末行/字段再生，报告不抄数
- [gate_runs.jsonl](06-benchmark/gate_runs.jsonl) — 现值由末行/字段再生，报告不抄数
- [md_claim_face_r52_2026-09-25.json](06-benchmark/md_claim_face_r52_2026-09-25.json) — 现值由末行/字段再生，报告不抄数

### 判据证据件（按体积前 8）

- [description基线_2026-09-24.json](06-benchmark/description基线_2026-09-24.json) — 114474 B
- [skill_structure_rubric_r29_2026-09-24.json](06-benchmark/skill_structure_rubric_r29_2026-09-24.json) — 89748 B
- [skill_structure_rubric_2026-09-24.json](06-benchmark/skill_structure_rubric_2026-09-24.json) — 49522 B
- [rationalizations_robustness_r30_2026-09-25.json](06-benchmark/rationalizations_robustness_r30_2026-09-25.json) — 31719 B
- [r31_section_robustness_2026-09-25.json](06-benchmark/r31_section_robustness_2026-09-25.json) — 31103 B
- [rationalizations_robustness_r30b_2026-09-25.json](06-benchmark/rationalizations_robustness_r30b_2026-09-25.json) — 31101 B
- [catalog_attention_tax_r20_2026-09-24.json](06-benchmark/catalog_attention_tax_r20_2026-09-24.json) — 30879 B
- [r31_section_robustness_after_2026-09-25.json](06-benchmark/r31_section_robustness_after_2026-09-25.json) — 30050 B

### 逐轮对标报告（最近 8 轮）

- [全量对标报告_r77_八维结构化_2026-10-01.md](06-benchmark/全量对标报告_r77_八维结构化_2026-10-01.md) — 用户指令直达轮（八维总览+逐项差距+H/M/L建议+分阶段路径）：本地 fresh（171 技能/2.16MB/591py/入口 24.8KB 持平）+ 对手三仓实时（superpowers 293,391★/anthropics 179,154★/addyosmani 100,104★）+ description 双要素宽口径全量 152/171（88.9%，缺 19 名单只出不改）+ gates 27 门实跑 **25/27（两红逐条归因：freshness 自指延迟/retired_face 外部在途）**；P0 四项已执行（报告+证据 JSON+README 同步+门禁实跑）
- [全量对标报告_r76_存量09回填与头模板一致性判据_2026-10-01.md](06-benchmark/全量对标报告_r76_存量09回填与头模板一致性判据_2026-10-01.md) — **收口轮**（r74 §6 遗留 #2，用户裁定「回填 + 立长期判据」）：存量面实测 6 件 09（新 1 / 旧 5），4 件逐字节单行回填（3 件提交、`陪聊` 被其自有交付件判据拦红留树不绕）、`医` 在途只登记；根因不是"忘了同步"而是 `_op_init()` 对已存在 09 **跳过（不覆盖）** ⇒ 模板改动**结构上永不回流**存量 → 受管根 **V3.115.0** 落 `header_drift()` + `--check` advisory 行 + `--fix-header` 自愈出口 + 桩**第八组 H 五腿**（`PASS 八性全成立`，三变异 rc=0，受管根 `b4546e8e` 远端可见）；判据上线当轮即量到更深一层：3 件 09 对 `07⇄09` 权威关系的表述与 `_sync_one` 现实现**相反**（旧句写"会被 sync 覆盖"，实现是"只报冲突不覆盖"）；② M-3 派生件重建**判 BLOCKED**（焚诀根 36→40→42 持续在涨、5 条已 staged，且 `--apply` 的四个输出面全为 `M` ⇒ 强推必覆盖他人产物）
- [全量对标报告_r74_next跨批语义分歧收口_2026-10-01.md](06-benchmark/全量对标报告_r74_next跨批语义分歧收口_2026-10-01.md) — **收口轮**（连挂多轮的 footer 未闭环项闭环）：`--next` 分歧定位到**一处摘要行**（模板 `:8` 写"按 P0→P1→P2 顺序取批"，而 `:17` 字段约定 + `flow.py` + 实现三者均为"当前批次 + 本批全 done 才进下一批"）⇒ **裁定不改行为**、只统一措辞；三处受管根改动（模板 / `flow.py` 报因 / 桩新增**第七组 G**，含**必真对照腿**"P0 全 done 必须落 P1"）；桩七性 PASS、本项目 `[GATE:flow-check-pass]`
- [全量对标报告_r73_坏行行号与继承截断标记_2026-10-01.md](06-benchmark/全量对标报告_r73_坏行行号与继承截断标记_2026-10-01.md) — r72 遗留①②落地：`read_rows` 由报**坏行数**改**逐行报 1-based 行号**（含空行计数，超额 `BAD_SHOW_MAX=10` 显式声明截断）+ 继承行新增 `diff_truncated_inherited` 且本行 `diff_truncated` 归 False（本行未列清单不应显示"被截断"）；行级口径经纯函数 `row_truncated()` 固定不漂移（判据与夹具共用一份逻辑）；夹具 36/36
- [全量对标报告_r72_逐字重复触发自审与三处缺陷_2026-10-01.md](06-benchmark/全量对标报告_r72_逐字重复触发自审与三处缺陷_2026-10-01.md) — 逐字重复触发轮（不降格、不空转）：对 r68 的 `--diff-list`/跨轮趋势做**整跑+自审**，修三处缺陷 —— ① `read_rows` **静默吞坏行**（分母静默变小）→ 改 `(rows, bad_n)` + rc=2；② 面转不可达时 `latest_dirty_n` **留陈旧值**（当现状）→ 归 None 并加 `latest_state`；③ **改签名漏改调用点**（gate 路径仍按旧返回值用，真机腿 T0 当场 `AttributeError`）；夹具 34/34
- [全量对标报告_r71_热度时间窗与新面孔配额_2026-10-01.md](06-benchmark/全量对标报告_r71_热度时间窗与新面孔配额_2026-10-01.md) — r70 遗留①②落地：热度统计由**近 20 行**改**近 6 小时**（`HEAT_WINDOW_HOURS`，不可解析 ts 的行**计数丢弃**不得静默归入任一侧，入窗/丢弃数经 `stats` 可见）+ `NEW_FACE_QUOTA=12`；含一次**语义更正**（配额是「给老面孔预留名额」而非新面孔硬顶：不足时补满 cap）；夹具 32/32
- [全量对标报告_r70_新面孔优先与热度滑动窗口_2026-10-01.md](06-benchmark/全量对标报告_r70_新面孔优先与热度滑动窗口_2026-10-01.md) — r69 遗留①②落地：排序键由 `(-热度, 路径)` 扩为 **`(是否新面孔, -热度, 路径)`**（修「热度 0 沉底被整批截断」的口径代价）+ `heat_index` 增**滑动窗口**（默认近 20 行，窗口在统计前切行）；红线不变（热度/窗口/新面孔一律不进 `dirty_digest`）；夹具 28/28（含 T24 变异腿）
- [全量对标报告_r69_pin清单热度排序与继承链_2026-10-01.md](06-benchmark/全量对标报告_r69_pin清单热度排序与继承链_2026-10-01.md) — r68 遗留①②落地：`diff_files` 由字典序采样改**热度降序**（热度=路径历史出现次数，同热度按路径升序；面级 `diff_order` 显式标注口径）+ `diff_inherit` 改指向**最近一次全量行**（不再引进空壳；无全量行则保留清单不写假指针）；红线：**热度不得进 `dirty_digest`**（否则假报 pin 变动污染趋势），由夹具 T22 双向钉住；夹具 25/25
- [全量对标报告_r68_pin台账增量落账与跨轮趋势_2026-09-30.md](06-benchmark/全量对标报告_r68_pin台账增量落账与跨轮趋势_2026-09-30.md) — r67 遗留①②落地：行内落**未提交集清单**（cap=40 + 截断显式声明）+ **增量落账**（未变面留 `diff_inherit` 指针，单行 ≈6KB→稳态 822B）+ 新增 `--trend` 跨轮趋势（哪一面最常变）；契约分代形状教训（契约只校验行级键 ⇒ 另立 `diff_files_n`/`diff_truncated`）；夹具 20/20
- [全量对标报告_r67_R58-1仓外输入固定面本地面_2026-09-30.md](06-benchmark/全量对标报告_r67_R58-1仓外输入固定面本地面_2026-09-30.md) — R58-1 落地：第 17 维从 CI 面推到**本地面**，新增**第 27 门** `input_pin_face`（各端 junction/镜像面必须钉在声明的权威根 + 输入面 pin 落账使 verdict 可归因）；一手实测 12/12 junction 全绿、2 条 null 逐条列出；夹具 13/13（含 2 变异腿）；契约入册 `input_pins.jsonl`
- [全量对标报告_r66_W46b生成器面接线判红_2026-09-30.md](06-benchmark/全量对标报告_r66_W46b生成器面接线判红_2026-09-30.md) — W-46b 闭环：真死句柄摘牌留注（契约 21→20 键）→ 修判据自身三处缺陷（自排除假阳性 / all() 过紧致假阴性 / 真死句柄）→ `--gate` 三态 + 夹具 12/12 → 注册 **第 26 道常驻门** `generator_face`
- [全量对标报告_r65_M2范围裁定与自建面达标_2026-09-30.md](06-benchmark/全量对标报告_r65_M2范围裁定与自建面达标_2026-09-30.md) — 范围裁定轮：M-2 队列的**自建可修子集 = 1 件（且在途）**，自建面（HIGH+MID=77）双要素率 **98.7%**，余 34 件全属 EXCLUDE/LOW/受保护/未在册；受管根双采样仍在写（45→46）故零受管根写入；W-46b 前置归因（3 条死句柄 = 1 真死 + 1 自排除假阳性 + 1 待裁定）
- [全量对标报告_r64_M2首批收口与在途产物入库_2026-09-30.md](06-benchmark/全量对标报告_r64_M2首批收口与在途产物入库_2026-09-30.md) — 收口轮（承接 r63 §6）：r64-M2 首批 5 件描述双要素修复（受管根 fece2b9d）收口入库，描述基线 128→135 / NO_WHEN 41→34 / 75.7%→79.9%；补齐项目侧在途 4 项 + r62 决策记录；`retired_face` 红归因为外部在途（R269 登记不动）
- [全量对标报告_r63_红门修复与描述全量审计_2026-09-30.md](06-benchmark/全量对标报告_r63_红门修复与描述全量审计_2026-09-30.md) — 6 红门全归因闭环（ratchet 归因上调 87598 / md_claim 12 处补命令 / 3 门传染转绿 / freshness 解环）；H-1 真执行：169 件描述双要素全量审计 75.7%（判据 4 处假阴性先修）、A-ask-questions V2.11.0 + coding-agent V1.1.0 修复；新增 A-project-handoff V3.112.0 遗留任务自动接管协议（takeover.py selftest 10/10）
- [全量对标报告_r60_能力覆盖名册差集_2026-09-30.md](06-benchmark/全量对标报告_r60_能力覆盖名册差集_2026-09-30.md) — 第 18 维新开：14 仓 209 唯一名册 vs 本地 428；37 条真差距候选里 0 件满足「可运行+可移植+与项目组合有交集」；抓出三处前提失效（R59-5 已落地/docx 验证段已 17 条/xlsx 才真缺）；R59-4 退役真执行
- [全量对标报告_r62_八维结构化_2026-09-30.md](06-benchmark/全量对标报告_r62_八维结构化_2026-09-30.md) — 用户指令直达版：对手双仓实时重测（superpowers 293.1k★/anthropics 179.0k★）+ 本地 fresh（169 技能/2.15MB/585py/入口 24.8KB）+ description 双要素抽样 4/9；P0 四项已执行（报告+证据 JSON+抽样+README 同步）
- [全量对标报告_r59_根迁移致判据读死面与退役未移出_2026-09-29.md](06-benchmark/全量对标报告_r59_根迁移致判据读死面与退役未移出_2026-09-29.md) — P0：根迁移把两道常驻判据喂成死面；退役登记了没移出；上游 mcp-builder 装入- [全量对标报告_r46_标记写入唯一入口_2026-09-25.md](06-benchmark/全量对标报告_r46_标记写入唯一入口_2026-09-25.md)
- [全量对标报告_r47_无法定年盲区清零_2026-09-25.md](06-benchmark/全量对标报告_r47_无法定年盲区清零_2026-09-25.md)
- [全量对标报告_r48_契约分代与归属可机检_2026-09-25.md](06-benchmark/全量对标报告_r48_契约分代与归属可机检_2026-09-25.md)
- [全量对标报告_r49_判据输入面五面自证与三处劫持根因修_2026-09-25.md](06-benchmark/全量对标报告_r49_判据输入面五面自证与三处劫持根因修_2026-09-25.md)
- [全量对标报告_r50_权威源扫描扩面与对手枚举面复核_2026-09-25.md](06-benchmark/全量对标报告_r50_权威源扫描扩面与对手枚举面复核_2026-09-25.md)
- [全量对标报告_r51_取数面两路对账与判据接线自失效_2026-09-25.md](06-benchmark/全量对标报告_r51_取数面两路对账与判据接线自失效_2026-09-25.md)
- [全量对标报告_r52_md引用面两路对账与契约陈旧自检_2026-09-25.md](06-benchmark/全量对标报告_r52_md引用面两路对账与契约陈旧自检_2026-09-25.md)

本节链接 35 行 ｜ 06-benchmark JSON 90 ｜ MD 66（2026-10-01 r77 实测；旧值 22/88/52 为 r62 时点，已按 R241 只加注不改写历史正文、本行是现值）
> 取值：`python -c "import glob;print(len(glob.glob('06-benchmark/*.json')),len(glob.glob('06-benchmark/*.md')))"` 与 `grep -c '](06-benchmark/' README.md`

