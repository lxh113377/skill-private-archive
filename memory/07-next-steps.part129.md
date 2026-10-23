# 07-next-steps.part129.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R151-2（r151 登记，P0·已落地）** **第 11 类 gsap 靶生产终判四条件本轮全部现算达成**：① 第 56 门 stale_gsap=False / class_11_closed=True；② r135 效力面 BASELINE margin +0.0843、self=0.6412>rival=0.5569、rank=1 top1=gsap；③ w47 夹具 8/8（t1b 假绿腿由历轮 FAIL 转 PASS = 假绿 0）；④ r133 ingress 全件搜索无 gsap。归属方 2026-10-21 19:39:47 重建 BGE（产物 mtime 晚于 gsap 源 2026-10-20 23:26:28；取值 `Get-Item 'C:\Users\37533\Desktop\workspace\焚诀\eval\bge_fullbody_embeddings.npy'\`）。提案 corpus_lang_mismatch 已落 r151_execution + acceptance_r151（A/C 闭环，**B 段不随之销账**）。取值：`python 05-exec/r135_lang_boost_efficacy.py --json <件>`、`python 05-exec/r128_w47_reconcile_fixtures.py（读末二行 8/8；本件无 argparse，--json 静默忽略不落快照——r151 自抓）`。 【r155 裁决=销账｜四条件本轮全部现算达成并入库（commit dd67102：报告 + 4 个读数件）；提案 acceptance_r151 已落，B 段两对单独转观察项不随之销账】

- [x] **R151-3（r151 登记，P1·已落地）** **归属方口径形状守卫（防假闭环）**：探针坐实旧实现失真三态——对方 `source`→`slug` 改名时读成 stale_gsap=False/closed=True/**rc=0 放行**（假闭环）；返回 list[str] 或 dict 时 **AttributeError 裸崩**。新增 `relay_shape_check()` + S7/S8 两腿：不认识的面 => **UNVERIFIED rc=2**，绝不判闭环（R247）。另 `lag_s` 改名不改判定但 lag 静默变 None => 新增 face.lag_field_missing 显形。取值：`python ./_temp/r151_relay_shape_probe.py`。 【r155 裁决=销账｜relay_shape_check 已入本体，S7/S8 两腿常驻（改字段名/改返回类型由 rc=0 放行改判 rc=2 UNVERIFIED），face.lag_field_missing 显形在位】

- [x] **R151-4（r151 登记，P1·已落地）** **14 条 OVERDUE 逐条裁账 + #48 立规**：8 条第 11 类/w47 线（4 销账 + 2 降级长期看守 + 2 已裁不重复）+ 6 条宽限/写序线（全部销账，r146 pending 通道与 r147 第 55 门已治理）。写裁决唯一入口 r46_mark_verdict（锚点定位，X-19）：12 条 [MARK:OK] 逐条读回、1 条 [MARK:REFUSED] 幂等拒写。读数 OVERDUE 14=>0、DECIDED 45=>59、W-12 INCOMPLETE=>OK、棘轮阻断项 1=>0。**AGENTS.md #48「反向验证的每条腿须比对 want⇄got」已立规**（#32 第五形态）。取值：`python 05-exec/r38_debt_aging.py --json <件> --ledger 06-benchmark/debt_runs.jsonl`、`python 05-exec/ratchet_gate.py --json <件>`。 【r155 裁决=销账｜裁账动作与 #48 立规均已入库（commit dd67102 + 0cc77fa）；#48 正文已由 r154 归档至 memory/06-constraints.part16.md（报告 §11 已加校正注，R241 原文不改）】

- [x] **R151-5（r151 登记，P1，到期 r153）** **其余门的反向验证按 #48 普查**：本轮只治第 56 门；历轮大量夹具是「打印 want 不看 got」同族形态（r149 六态、r134 两次反向验证各抓一 bug 皆此病）。判据：逐门须具备 `--selftest` 且退出码由 want⇄got 比对决定，非「跑完没报错」。取值：`python 05-exec/run_gates.py --json <件>` 后逐门核。 【r156 裁决=销账（由 r155 普查面承接）｜并行会话已建 05-exec/r155_selftest_census.py 并入库（commit 65c0cb7），本轮只读复跑读数：自测/夹具件 48｜OK 48｜候选 0｜弱信号 10（advisory），rc=0。普查面常驻即看守该形态，本会话不再重复造第二个真相源（#48 与本仓单源纪律）】

