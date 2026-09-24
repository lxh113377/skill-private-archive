# 05-feature-status.part20.md

<!-- 本卷为 05-feature-status.part19.md 的延续 -->

- **还账方式（关键：不是把数字调小，是改写法）**：整段执行记录被写进 SKILL.md 的 `## 版本历史` 区，而该区属**每轮注入面**、同版全文在 `references/version_history.md`（按需加载）本就存在 ⇒ 纯重复计费。把 V10.68.0/V10.69.0 两条长段落各换为一行摘要（保留版本号与 C13 锚点句，指向分卷），本版 V10.70.0 也按「区一行 + 分卷全文」写。实测 `wc -c SKILL.md` **29,041 → 26,593B**；焚诀 C25 注入区 62,889B / 余量 **220B → 1,583B**、C31 余量 4.0%（其 <5% 告警仍在，剩余面来自其他技能增长，不属本仓可减项，且**不为变绿删规则本体**）。受管根 `928517a`，C13 实测仍 ✅（frontmatter 10.70.0 == 区首条）；未删规则本体、未改任何阈值、未碰 frontmatter description（⇒ 不触派生件重建）。
- **本仓棘轮顺势收紧**：`ratchet_gate.py --update` 只降不升 ⇒ `inject_union_bytes` 基线 89,014 → **86,346**；本仓口径与焚诀口径不同（本仓并集含**本项目注入壳 AGENTS.md**），故仍显示超硬顶为**非阻断告警**，这正是 r18 N2 的原始病灶：C25 只管它自己那 5 个文件，别的项目的壳完全在预算外。
- **仍开放的两项转办**：① **目录税棘轮**——全库 name+description 每轮 ~45,250 字符，焚诀 C25/C31 均不覆盖，本仓已用 `ratchet_gate.py` 的 `catalog_grand_chars` 自持拦住**本仓可见增长面**（跨仓强制仍需焚诀）；② **C33′ 计数断言内容级门禁**——`claim_truth_scan.py` 已可跑、当前 4 条候选（2 条经复核为语义误报已登记盲区）。接线指南已更新为可核对版：`05-exec/r20b_fenjue_wiring/README.md`。
- **纪律自用（本轮新立的写法规范即刻生效于自己）**：07 属注入面，本轮起 r21c 条目按短行写、长记录进分卷；外部红项不代清：`gates` 的 2 处 MISMATCH 属 `ican-frontend-design-system`（并行会话在途，本仓零触碰），`-Fix` 是单向 源→镜像、覆写会吞其镜像侧在途工作，故按 R269 只登记不擅动。

- **r29 判据自证轮（第 29 轮）** — M2 双口径（`rubric_hits(calibre)` 复用 r17 description 判据，四层自证 9/9 + `--against` 与 r28 归档正文口径 7 列全等 + RC=2 反例）→ **推翻两条上一轮自家结论**（verification 缺口的 32.4% 是措辞假阴性 59.0%→72.3%；overview 列五家全 100% 无鉴别力）→ 范围过滤护栏 `r29_scope_filtered_queue.py`（r28 H2 队列 top14 全是市场/上游件属越界）→ 双过滤后真队列 **3 条补「验证」段清零**（受管根 `6a4f97b`，26 行纯新增零夹带）→ M1 常驻页并入双口径 + 修 `C1~C28`→`C33`。镜像门禁 mismatch=6→pass。全文见 `06-benchmark/全量对标报告_r29_双口径与范围过滤_2026-09-24.md`。

- **r29b H1/H3 补做轮（2026-09-24 第 29 轮 b 段，用户标注驱动）** — 复测推翻"模板被占用"误判：真实落点 `A-skill-manager/assets/creator/init_skill.py` + `references/lifecycle-create.md` 当时均干净。受管根 `afe0f13` 落地新建技能强制三段（反理性化表 / 验证含反例与未达成表述 / 破坏性命令作用域守卫）+ `quick_validate.py` 缺段提醒（提醒级不阻断，避免存量技能集体变红）+ 修 `read_text()` 未指定编码的中文崩溃坑；冒烟 py_compile PASS、生成骨架实含 3 段、校验器三侧齐；四门禁全绿。壳文件 `SKILL.md`/`version-history.md` 属他人 in-flight，未夹带、版本号未升。
