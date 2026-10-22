# 07-next-steps.part91.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R136-2（r136 登记，P0·已落地）** **8 条无支撑提案已逐条处理**：4 条补读数面 + evidence + acceptance（`skill_hitrate_stale_expectations`→`r131_direct_closure.py` 的 face.stale_n；`route_miss_shortcircuit_layer`→`r131_closure_layers.py` 的 face.by_first_layer；`domain_filter_latent_exposure`→`r128_ruler_reconcile.py --semantics latent` 的 counts.latent_realized_n；`derivative_watch_domain_skip_drift`→焚诀侧 `python eval/verify_truth_consistency.py --json` 的 C10/C16 detail）；另 4 条（`catalog_tax_ratchet`/`inject_union_merge`/`claim_truth_gate`/`noise_scope_footgun`）**无读数面**，已显式标注「未验证，仅为候选方向」并写明须先建读数面。**最终 11/11 完整**。 【r140 裁决=挂账至 r142｜并行会话 R135/R136 系合规续挂，R269 不代收口】 【r143 校正注：11/11 提案完整且历轮提案面 PASS，本条闭环】

- [x] **R136-3（r136 登记，P1·已落地）** **AGENTS.md #34「纪律须作用到自己身上」**已立规，与 #31/#32/#33 构成四条强制条目（处方 / 判据面 / 结论层 / 纪律自用）。**反面实证已写入文件**：修之前 11 条提案只有 3 条能追到读数面，8 条追不到 —— **不是别人的问题，是我自己写提案时没走自己立的纪律**。 【r140 裁决=挂账至 r142｜并行会话 R135/R136 系合规续挂，R269 不代收口】 【r143 校正注：#34 已立且第 48 门常驻，本条闭环】

- [x] **R136-4（r136 登记，P2）** **本轮又撞到 #32 的形态（第三次）**：新写的判据**路径写死**，反向验证时探针文件喂不进去 ⇒ 探针跑的是真台账，报出真值 8，**看起来「验证通过」实则根本没验到探针**。修法 = 路径可注入（`--proposals`）。**教训升级**：反向验证的探针必须**能被判据真的读到**，否则「探针通过」是假的 —— 判据跑对了真数据 ≠ 探针被验到。已并入 #32 的形态表（新增第 ④ 种：路径不可注入形态）。 【r140 裁决=挂账至 r142｜并行会话 R135/R136 系合规续挂，R269 不代收口】 【r143 校正注：路径注入防护已固化（--probes 参数 + r141 复用），本条闭环】

- [x] **R135-2（r135 登记，P1·已落地）** `05-exec/r135_lang_boost_efficacy.py` 已入册为**第 47 门**（`lang_boost_efficacy_face`）。**意义**：把「语料类处方先测效力」固化为常驻可复算面 —— 任何「补触发词/改 description」类处方，写进提案前先跑本面看 margin 是否真的动了。⚠️ 门表对账已登记（未登记 0）、准入门已登记（未声明 0）。 【r140 裁决=挂账至 r142｜并行会话 R133-R135 系合规续挂，R269 不代收口】 【r143 校正注：效力面已入册为第 47 门且历轮终态 PASS，本条闭环】

- [x] **R135-3（r135 登记，P1·已落地）** **w47 正控三态化已落地**：t0 前置（工具可跑）/ t1a 假红腿 / t1b 假绿腿。**意义**：夹具读数直接可分辨「判据口径错（假红）」与「语料/路由漂移（假绿）」，不必再另起脚本定位 —— 这正是 r132–r135 连续四轮追查成本的根源。**自抓**：拆腿后 t1a 仍 FAIL，因为断言带了 `rc1 == 0` 而工具有任何不一致就返回 rc=1 ⇒ **退出码与计数必须分离**，已修。取值：`python 05-exec/r128_w47_reconcile_fixtures.py`（本轮读数 t0 PASS / t1a PASS / t1b FAIL）。 【r140 裁决=挂账至 r142｜并行会话 R133-R135 系合规续挂，R269 不代收口】 【r143 校正注：w47 三态化已并入 r142 终态夹具，本条闭环】
