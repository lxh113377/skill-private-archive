# 07-next-steps.part141.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R146-4（r146 登记，P2）** **残留：pending 与台账的双写顺序**：安装时先写台账再写 pending，两步之间崩溃会出现「台账已更新但 pending 未更新」（合法宽限态消失但无篡改）。当前影响 = 下次重装补齐；彻底方案 = 先写 pending 再写台账（崩溃窗口期落在「合法宽限」侧而非「误红」侧）。另：pending 内容过期不会自动清理（下次安装覆盖，单 hook 只记最新一条——历史 pending 不进台账）。取值：`python 05-exec/r142_install_history.py --json <件>` 的 `rows[].h7_note`。 【r150 裁决=执行（终局）：已由 R147-1 写入顺序重排治理（日志→pending→台账，死窗为 0），本期销账】 【r151 裁决=销账｜该残留由 r147 崩溃前缀穷举治理（写序改为 日志→pending→台账），第 55 门 write_order_sweep_face 三条腿常驻；本轮该门 PASS】

- [x] **R145-3（r145 登记，P1·已落地）** **R144-4 已由 R145-1 治理**（窗口期宽限），本条为 R144-4 的闭环确认：量化坐实（`_temp/v28_window.py`）→ 宽限判别落地 → 三态验证通过。 【r151 裁决=销账｜闭环确认件：三条件宽限已生效（第 54 门 H7 历轮 PASS），R144-4 已由 r146 pending 通道 + r147 写序重排双重治理】

- [x] **R145-4（r145 登记，P2）** **残留：宽限的信任面收窄到单会话**。当前判别依赖「缺行 session ∈ 当前进程 env 会话」——若窗口期跨会话（会话 A 装、会话 B 跑门），B 的 env 里没有 A 的 session ⇒ 仍会误红。**当前缓解**：跨会话窗口期回落到 git_user 匹配（同人仍宽限）。**建议**：若要更稳，把「已装未提交」状态写进一个 git 内的 pending 标记件（安装脚本 `git add` 台账 + pending 标记，提交后自动消失），可彻底消除跨会话误红；代价是引入第二份需同步的状态。 【r151 裁决=销账｜该残留的建议方案（git 内 pending 标记件）已由 r146 落地为 #44/H7 pending 通道，四态反向验证在案；r147 进一步把写序改为真相源先行】

- [x] **R135-1（r135 登记，P0·转办焚诀/受管根侧）** **第 11 类的处方已按实测改写**：提案第 11 条新增 `r135_correction` + `acceptance_r135`（四步：① 选变体须 verdict=EFFECTIVE，**「末尾追加」是 NO_EFFECT 不得选**；② 改后重建 BGE 派生件，top1=gsap 且 margin>0；③ 第 11 类面 lang_mismatch_n / new_skill_preempt_n 归 0；④ w47 6/6 归绿）。**实测有效的两条**：把中文触发词写进 **frontmatter**（margin −0.0586 → +0.0216）或把 description 换成**短中文摘要**（→ +0.1827）。取值：`python 05-exec/r135_lang_boost_efficacy.py --json 06-benchmark/lang_boost_efficacy_r135_2026-10-21.json`。 【r140 裁决=挂账至 r142｜并行会话 R133-R135 系合规续挂，R269 不代收口】 【r151 裁决=销账｜r151 实测第 11 类 gsap 靶生产终判闭环四条件（第 56 门 stale_gsap=False、r135 效力面 BASELINE margin +0.0843 top1=gsap、w47 夹具 8/8 含 t1b 假绿归零、r133 ingress 面 gsap 已消失）；提案已落 r151_execution + acceptance_r151。B 段 github/vwt 两对不随本条销账，转 neighbor_rank_r148 观察项长期看守】

