# DECOMPOSE · r340（R339-2 两件制度化 + C4 具名豁免端到端）—— ⚠️ 本卡为轮中落，开场未落，如实自记

> 起点 0ec29dc（tag r339b）｜goal 第 22 回合 ⇒ 轮号 r340（`R340-*` 领号前核零命中）。
> ⚠️ **诚实**：本轮开场第一动作是查状态与 G-L1 洁净度，**没先落本卡** ⇒ R318-2「先落卡」纪律第八次违反（第七次是 r338）。本卡落在轮中（写报告前），与报告同笔入库，报告内**不写「卡先落」字样**以免重演 r338 的不实形态。
> 机制观察：`commit_msg_face` 的 C4 只能抓「声称了但笔里没有」，抓不到「压根没声称也没落卡」——这是该门的**已知边界**（不是漏洞，纪律类违规无法全靠文本自证），本轮登记为 R340-2 而非静默。

## 起点实测
- R340-* 零命中（可领号）。受管根整体 79 行在途；B 类目标件 CLEAN = theme-factory / ui-ux-pro-max / agent-browser / html-ppt / frontend-slides / security-audit / docx / xlsx / pdf / mcp-builder；DIRTY = ppt-master / story-setup / story-long-write / story-short-write。
- 定量结论（本轮新测）：CLEAN 件的 **prose 孤儿共 13 条**（theme-factory 10 / ui-ux-pro-max 2 / agent-browser 1），html-ppt 的 15 条**全是 noise 桶**（templates/*/README.md 示例目录说明，prose=0）⇒ **CLEAN ∩ 可补链 = 0**：13 条全落在 r323「目录级覆盖保持」与 R323-2「应剪枝不该补链」两个既有裁决内。这条把「等 CLEAN 就补链」的口子定量关掉了。

## 本轮分解（W=2 ⇒ 严格串行 + 同文件冲突）
| # | 件 | 判据 |
|---|---|---|
| 1 | R339-2 半②：C4 具名豁免（「卡先落于 <rev>」不判红）+ 抽 `c4_hits()` 纯函数做端到端夹具 t12/t13 | `[R339:SELFTEST] 13/13 teeth=pass` 且 `--replay 25` 仍 3 真阳 |
| 2 | R339-2 半①：镜像恒红通例入附三第 4 条 + 写手模板补「卡先落于 rNNN」标准句式 | `grep -c 被自身引文形态点着 04-plan/后续维护规范…` ≥1；`grep -c 卡先落于 写手模板` ≥1 |

## 30 秒卡 8 问（补答）
① ≥2 互不引用 ⇒ 否（件2 的句式要对齐件1 的 NAMED_RE 形态）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 否（同一判据族）。④ 过。⑤ 发 0。⑥⑦⑧ 见上。
skip_reason：**严格串行**（模板句式须与门的识别正则一致，先改门再写模板）+ 写面冲突（同文件）。
