# 05-feature-status.part22.md

<!-- 本卷为 05-feature-status.part21.md 的延续 -->

- **r29 判据自证轮（第 29 轮）** — M2 双口径（`rubric_hits(calibre)` 复用 r17 description 判据，四层自证 9/9 + `--against` 与 r28 归档正文口径 7 列全等 + RC=2 反例）→ **推翻两条上一轮自家结论**（verification 缺口的 32.4% 是措辞假阴性 59.0%→72.3%；overview 列五家全 100% 无鉴别力）→ 范围过滤护栏 `r29_scope_filtered_queue.py`（r28 H2 队列 top14 全是市场/上游件属越界）→ 双过滤后真队列 **3 条补「验证」段清零**（受管根 `6a4f97b`，26 行纯新增零夹带）→ M1 常驻页并入双口径 + 修 `C1~C28`→`C33`。镜像门禁 mismatch=6→pass。全文见 `06-benchmark/全量对标报告_r29_双口径与范围过滤_2026-09-24.md`。

- **r29b H1/H3 补做轮（2026-09-24 第 29 轮 b 段，用户标注驱动）** — 复测推翻"模板被占用"误判：真实落点 `A-skill-manager/assets/creator/init_skill.py` + `references/lifecycle-create.md` 当时均干净。受管根 `afe0f13` 落地新建技能强制三段（反理性化表 / 验证含反例与未达成表述 / 破坏性命令作用域守卫）+ `quick_validate.py` 缺段提醒（提醒级不阻断，避免存量技能集体变红）+ 修 `read_text()` 未指定编码的中文崩溃坑；冒烟 py_compile PASS、生成骨架实含 3 段、校验器三侧齐；四门禁全绿。壳文件 `SKILL.md`/`version-history.md` 属他人 in-flight，未夹带、版本号未升。
