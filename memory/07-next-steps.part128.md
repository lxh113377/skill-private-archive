# 07-next-steps.part128.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R153-1（r153 登记，P0·已落地）** **治理考核校验面落成 = 第 60 门** `gov_acceptance_face`（`05-exec/r153_gov_acceptance.py`）：A1-A6 一键复跑，三态与 run_gates 同口径（rc=0 但 pass_token 缺记 UNVERIFIED，R247），A6 归属方侧项按 #47 ③ 只显形不计总判。实测 `[GOVACC:PASS] 5/5 PASS｜FAIL 0｜UNVERIFIED 0`；夹具 `python 05-exec/r150_gov_fixtures.py` 到 **35/35 含变异 7 项**（a6a-e 五腿 + 内联 m7 把假绿分支注回）。门数 59 到 60，对账未登记 0。验收：`python 05-exec/run_gates.py` 末段「执行 60 门」。 【r156 裁决=执行（终局）：第 60 门在位且 A1-A6 实测 5/5 PASS，本期销账】

- [x] **R153-2（r153 登记，P1·部分落地，含归因更正）** **A2 时效腿判红归因更正**：联动面 `VOL_LEDGER_STALE` 原被我在 R150-3 记成**归属方缺陷**，实测**是我方进程缺口** —— 未按归属方文档跑收尾动作 `handoff.py volume <本仓> --snapshot`（本轮执行后体量册龄期 3.91 天到 0.0 天，A2 由 FAIL 转 PASS，A6 缺陷 4 条到 3 条）。**剩余真归属方缺陷 2 类**：`NO_SHARED_KEY`（快照行缺 `head`）与 `VOL_FIELD_EMPTY`（`files`/`growth_ratio` 覆盖 0/N）—— 常驻复算面 = `r150_gov_link.py`，转办提案已挂。**收尾动作现应常态化**：每轮收口跑一次 `volume --snapshot`（否则 A2 会因读数陈旧判红）。取值：`python 05-exec/r153_gov_acceptance.py`。 【r156 裁决=降级（长期看守）：归因更正已落文；剩余动作=每轮收尾跑 volume --snapshot（A2 时效腿自动把关，不跑即红）——机制已常驻，转看守】

- [x] **R150-10（r152 登记，P1）** **反向验证体检普查（#48 同族）**：本轮给三面补齐常驻断言（`python 05-exec/r150_gov_fixtures.py` → **29/29 含变异 6 项**：p5a P0 阻断 / p5c 对照 / p5d 接线 / 内联 m6 摘分支有牙）。建议按 #48 把「只打印 want、从不比对 got」形态普查到其余常驻门（R151-5 已立同族待办，本条是其在 r150 三面上的落地面）。**附带坑（本轮自抓）**：夹具里写 stub 内容时若把换行写成双转义，落盘会是**字面反斜杠 n** ⇒ stub 变单行、正文判空 ⇒ 假红（本轮实测：stub 单行导致 RULE 契约 draft FAIL）；写 stub 必须保证真换行。 【r156 裁决=执行（终局）：#48 普查已由第 61 门 selftest_census_face 承接（48 件/候选 0/自证三腿全中），三面断言含于夹具 35/35。⑦ 明示放行注记：本条作者即本会话（r152 轮亲笔登记），非编号改写】

- [x] **R151-1（r151 登记，P0·已落地）** **第 56 门连坐判定根治**：`closed = (not gsap) and (not others)` 改为 `closed = not gsap`（#35 他人漂移不连坐——旧式与同文件注释及门表 covers 的自述直接矛盾，把**已闭环读成未闭环**=假红）。同时把八态逐腿断言做进脚本本体（`--selftest`，每次真实读数前先自证；失配即 rc=1 不出读数）。**变异对照证明有牙**：连坐式注回临时副本 => FAIL S3（want=(False,1,True) got=(False,1,False)）rc=1，未变异对照 rc=0，真实件 sha 未变。取值：`python 05-exec/r149_derived_freshness.py --selftest`、`python ./_temp/r151_mut_probe.py`。 【r155 裁决=销账｜本轮实测：closed=not gsap 已生效，八态逐腿断言入本体（--selftest 8/8），变异对照有牙（连坐回归 FAIL S3 rc=1 / 对照 rc=0 / 真实件 sha 未变），第 56 门全量跑 PASS】

