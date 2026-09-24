# 05-feature-status.part21.md

<!-- 本卷为 05-feature-status.part20.md 的延续 -->

- **本仓棘轮顺势收紧**：`ratchet_gate.py --update` 只降不升 ⇒ `inject_union_bytes` 基线 89,014 → **86,346**；本仓口径与焚诀口径不同（本仓并集含**本项目注入壳 AGENTS.md**），故仍显示超硬顶为**非阻断告警**，这正是 r18 N2 的原始病灶：C25 只管它自己那 5 个文件，别的项目的壳完全在预算外。
- **仍开放的两项转办**：① **目录税棘轮**——全库 name+description 每轮 ~45,250 字符，焚诀 C25/C31 均不覆盖，本仓已用 `ratchet_gate.py` 的 `catalog_grand_chars` 自持拦住**本仓可见增长面**（跨仓强制仍需焚诀）；② **C33′ 计数断言内容级门禁**——`claim_truth_scan.py` 已可跑、当前 4 条候选（2 条经复核为语义误报已登记盲区）。接线指南已更新为可核对版：`05-exec/r20b_fenjue_wiring/README.md`。
- **纪律自用（本轮新立的写法规范即刻生效于自己）**：07 属注入面，本轮起 r21c 条目按短行写、长记录进分卷；外部红项不代清：`gates` 的 2 处 MISMATCH 属 `ican-frontend-design-system`（并行会话在途，本仓零触碰），`-Fix` 是单向 源→镜像、覆写会吞其镜像侧在途工作，故按 R269 只登记不擅动。

- **r29 判据自证轮（第 29 轮）** — M2 双口径（`rubric_hits(calibre)` 复用 r17 description 判据，四层自证 9/9 + `--against` 与 r28 归档正文口径 7 列全等 + RC=2 反例）→ **推翻两条上一轮自家结论**（verification 缺口的 32.4% 是措辞假阴性 59.0%→72.3%；overview 列五家全 100% 无鉴别力）→ 范围过滤护栏 `r29_scope_filtered_queue.py`（r28 H2 队列 top14 全是市场/上游件属越界）→ 双过滤后真队列 **3 条补「验证」段清零**（受管根 `6a4f97b`，26 行纯新增零夹带）→ M1 常驻页并入双口径 + 修 `C1~C28`→`C33`。镜像门禁 mismatch=6→pass。全文见 `06-benchmark/全量对标报告_r29_双口径与范围过滤_2026-09-24.md`。

- **r29b H1/H3 补做轮（2026-09-24 第 29 轮 b 段，用户标注驱动）** — 复测推翻"模板被占用"误判：真实落点 `A-skill-manager/assets/creator/init_skill.py` + `references/lifecycle-create.md` 当时均干净。受管根 `afe0f13` 落地新建技能强制三段（反理性化表 / 验证含反例与未达成表述 / 破坏性命令作用域守卫）+ `quick_validate.py` 缺段提醒（提醒级不阻断，避免存量技能集体变红）+ 修 `read_text()` 未指定编码的中文崩溃坑；冒烟 py_compile PASS、生成骨架实含 3 段、校验器三侧齐；四门禁全绿。壳文件 `SKILL.md`/`version-history.md` 属他人 in-flight，未夹带、版本号未升。

- **r30 反理性化首批轮（2026-09-25 第 30 轮）** — 四档稳健性工具段参数化（`05-exec/r30_section_robustness.py`）→ **rationalizations 严格同义零假阴性（档1=档2=13.9%，与 verification 的 29.2% 相反）但档2b=71.1%** ⇒ 定性为"缺的是借口→反驳这一形式，不是负面指引本身"；真队列取最保守口径 14 条，首批 5 条逐技能写特有失败形态落表（`story-scan`/`video-breakdown-skill`/`local-vram`/`code-review`/`utf8-encoding-fix`，受管根 `359d0fc` 50 行纯新增零夹带），复测档1 23→28、档3 55→60。维护状态维度首次实测化（4 仓 stars/pushed/issues，**issue 存量与星标同向**⇒高星标≠高维护度）并入常驻页。全文见 `06-benchmark/全量对标报告_r30_四档稳健性与反理性化首批_2026-09-25.md`。
