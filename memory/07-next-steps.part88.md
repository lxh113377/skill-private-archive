# 07-next-steps.part88.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R117-1（r117 登记，P0；r119/r120 部分完成）** 生产路由 REAL_MISS **12 → 7 条**（r119 修 4 条：`读PDF` / `python 脚本下断点单步调试` / `头脑风暴` / `路由触发词质量差需要重生`；r120 定位剩余 7 条中 6 条失败层在 direct_map/tag 短路、1 条在 L0 域过滤）。官方分层分 **88.3% → 90.1%**（271→276/291）。⚠️ **r121 新增 Wilson 判定：当前 90.1% 与基线 88.3% 的 95% 区间重叠 ⇒ 该 +1.8pp 在统计上不可判为提升**（要区间分离需 ≥285/291）。剩余 7 条中 6 条属焚诀 eval 只读红线 ⇒ 转办归属方（R119-2）；1 条（prompt-consolidation）需改注册表域归属 ⇒ 提案第 8 条。达标判据：复跑 `python 05-exec/r117_route_miss_attr.py` 的 face.real_n ≤ 6 且 36 门仍 PASS 且 face.stale_n 不增。 【r121 裁决=挂账至 r123｜账龄 3 轮越宽限 2；R117-1 需改注册表域归属（焚诀侧，提案第 8 条）、R117-2/R117-3 属题集维护方与跨季趋势（转办/下季）】 【r124 裁决=挂账至 r126｜r121 旧账（挂至 r123）到期追讨；REAL_MISS 7 条中 6 条属短路层（焚诀 eval 只读红线）、1 条需改注册表域归属（提案第 8 条）——归属方未动作前本仓无实施面，续转办】 【r124 裁决=降级｜REPEAT 升级裁决：REAL_MISS 7 条全在焚诀 eval 只读红线/注册表归属侧，本仓无实施面；转办记录与提案第 8 条在册，降级为长期看守（外部动作落地后重开）】

- [x] **R117-2（r117 登记，P0→转办）** 8 条过期期望（`deep-research-pro` / `fenjue-advisor-scoring` / `fenjue-cc-audit-cycle` / `multi-search-engine` / `weather` / `tencent-cos-skill__skillhub`）的题面 remap：归属 = 焚诀 eval/ 题集维护方（本仓只读红线，**不代改**），已登记 `06-benchmark/transmit_proposals.json` 第 5 条。复算：`python 05-exec/transmit_obsolescence_check.py` 【r121 裁决=挂账至 r123｜账龄 3 轮越宽限 2；R117-1 需改注册表域归属（焚诀侧，提案第 8 条）、R117-2/R117-3 属题集维护方与跨季趋势（转办/下季）】 【r124 裁决=挂账至 r126｜r121 旧账到期；8 条过期期望属题集维护方（转办在册），本仓红线禁改 eval】 【r124 裁决=降级｜REPEAT 升级裁决：8 条过期期望属题集维护方，本仓红线禁改 eval；转办在册，降级为长期看守】
