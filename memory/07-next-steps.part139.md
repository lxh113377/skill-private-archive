# 07-next-steps.part139.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R148-2（r148 登记，P0·已落地）** **AGENTS.md #46「处方须声明适用边界」已立规**：任何处方推广到第 2 个靶前必须逐靶跑效力面复测，提案须带 `适用边界` 字段写明「对哪种形态测过、在哪类无效」；无边界不得跨靶执行。**一手实证**：r135 处方在其余 2 靶 0/2 有效且 margin 更差（github ②−0.1725/③−0.2780；vwt ②−0.1084/③−0.2364）。第 48 门 r136 补 `boundary_missing_n` 腿（效力面支撑却无边界=判红），反向验证有牙：正常 0/摘边界 1/还原 0。取值：`python 05-exec/r136_proposal_evidence.py --json <件>` 的 `face.boundary_missing_n`；`python ./_temp/v34_bt_probe.py`。 【r151 裁决=销账｜#46 在册，且第 48 门 boundary_missing 腿常驻（本轮 proposal_evidence_face PASS、boundary 腿在位）；r151 又补 #48 逐腿比对条，本线收口】

- [x] **R148-3（r148 登记，P1·已落地）** **github/vwt 两对未照搬执行转观察项**（#34 纪律自用）：`06-benchmark/neighbor_rank_r148_2026-10-21.json`——根因分别为「期望归属存疑」（github 职责实近 code-review）与「近邻语义竞争 B_NEIGHBOR_RANK」（vwt↔local-asr 语义重叠），非语言。验收改挂期望侧对账（归属判定权在焚诀 eval 侧）。提案 corpus_lang_mismatch/direct_map_regex_preempt 已补 `适用边界`。取值：`python 05-exec/r133_new_skill_ingress.py --json <件>` 的 `lang_mismatch` 明细。 【r151 裁决=降级（转长期看守）｜期望归属判定权在焚诀 eval 侧，本仓无可开处方（r148 实测 0/2 有效，#46 禁照搬）；看守面 = r133 ingress 的 lang_mismatch 读数 + neighbor_rank_r148 观察件，禁滚新到期日（X-17）】

- [x] **R148-4（r148 登记，P2）** **残留：第 11 类生产面翻绿依赖归属方重建**。gsap 源侧已达标但生产 route 仍读旧 BGE 向量（本仓 eval 只读不代跑）——转办链的最后一公里在对方手里。建议：归属方重建 BGE 后复跑 r128 夹具 + r133 面双确认；在此之前 w47 t1b 保持红 1 条（诚实显示，禁按 0 记绿 R247）。 【r151 裁决=销账｜**本条正是 r151 翻绿的那条**：归属方 2026-10-21 19:39:47 重建 BGE（产物 mtime 晚于 gsap 源 23:26:28），第 56 门 stale_gsap 由 True 转 False、w47 t1b 假绿腿转 PASS。r149 挂的常驻面今天自动发现了闭环日（#47 生效实证）】

- [x] **R147-1（r147 登记，P0·已落地）** **安装写入顺序已重排为 日志→pending→台账**（`r138_install_hooks.py`，#45 真相源先行）：日志行数只增 ⇒ 台账/pending 任何崩溃前缀都只**滞后**（missing≥0）⇒ 落在宽限可救侧。不变式：`台账 lines ≤ 日志行数` 恒成立（超前 = 死窗，已不可能出现）。取值：`python 05-exec/r147_write_order_sweep.py --json <件>` 的 `face.source_idx`（日志<pending<台账 出现位置）。 【r151 裁决=销账｜第 55 门 write_order_sweep_face 本轮全量跑 PASS（L1 源码顺序 / L2 新序死窗 0 / L3 旧序死窗>0 反向案齐备）；不变式「台账 lines ≤ 日志行数」历轮未破】

- [x] **R147-2（r147 登记，P0·已落地）** `05-exec/r147_write_order_sweep.py` 已入册为**第 55 门**（`write_order_sweep_face`）。三条腿：L1 源码写入顺序（防回退）/ L2 新序崩溃前缀穷举 missing<0 数必须=0 / **L3 反向案：旧序穷举必须 >0（探针无牙则本面读数不可信）**。实测：新序 0 死窗全 PASS / 旧序 2 死窗 RED / VERDICT ALL-CORRECT；单门跑 PASS rc=0 3.2s、现场 finally 正确还原。取值：`python 05-exec/r147_write_order_sweep.py --json <件>`。 【r151 裁决=销账｜该门本轮实测 PASS（python 05-exec/run_gates.py --gate write_order_sweep_face 读 rc=0），穷举探针跑完现场三件正确还原】

