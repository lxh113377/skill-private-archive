# DECOMPOSE · r302（需求 4 的实质产出：用 r301 的版本面把「先核对哪几件」排出来；并修掉我自己造成的门红）

> 本卡先于本轮任何产物写入落盘。起点 3bfe8f5（tag r301c）。轮号 = goal 66 ⇒ r302。

## 起点实测（现取）
- HEAD 3bfe8f5、tags r301/r301b/r301c；我名下未交件 0；[RATCHET:PASS]（OVERDUE 0 / DECIDED 269）。
- r301 已产出需求 5 的版本面：49 对 lineage 里 behind=42 / current=1 / local_ahead=5 / unknown=1（口径限制已写死）。
- 两处门态待处置：① **r260_local_baseline FAIL**（我 r300 backfill 刷新 agent-browser 缓存条目造成，已归因）；
  ② **r291_req2 UNVERIFIED**（缺省读 2026-10-27 的 stale shadowstrict，须由 r221 自己刷新）。
- 需求 4 要的是「替换优先级 / 时间节点 / 验证标准 / 回滚预案」。现状：优先级从未有**证据化排序**，
  behind=42 只给了线索，没有把「上游更活跃 + 上游五维 + 声明态」合成一张可执行序。

## 本轮分解（真实派发 = 2 件）
| # | 件 | 可独立验收 | 写面 | 去处 |
|---|---|---|---|---|
| 1 | r260 复现记录**加输入指纹**（保牙修法：同一 doc 重算仍严格相等；doc 被合法刷新判 STALE_INPUT 而非 FAIL）| 判据末行 PASS + 一条「量尺漂移仍必 FAIL」的反向腿 | 05-exec/r260_local_baseline.py | 派 A1 |
| 2 | 需求 4 证据化优先级表：把 behind 态 × 上游五维 × 声明态合成排序 + 12 对抽样补「同名件 sha 是否变」层 | 判据末行 + 两腿负控 | _temp/r302b/ | 派 B1 |
| 3 | 用 r221 自己的生产者刷新 stale shadowstrict ⇒ r291_req2 转绿 | 末行从 UNVERIFIED 变 PASS/FAIL 且明写输入 | 06-benchmark/ | Lead 自干 |
| 4 | security-audit 的 .upstream 落点（受管根，走 rule_editor + 三门禁 + registry diff）| declared_state 从 invalid 变 lineage 或注明无单一同名上游 | D:/global_skills/security-audit/ | Lead 自干 |
| 5 | 收口：三面 + 账龄 + 提交 + 部署 + GM | 现取读数 | 本仓 | Lead |

30 秒卡：① 互不引用工作流 ≥2 是（#1 门修 / #2 需求 4 排序，不同件不同面）；② 各 ≥3 回合 是；③ ≥2 独立面 是；
④ 四问齐（#1 #2 单一产出物 / 单文件面 / 可独立验证）；⑤ 发 2 件；⑥⑦ 判据与期望末行写进 _temp/r302_briefs/；
⑧ 收件后我各复跑一条判据，并对 #1 额外做「反向腿：人为造量尺漂移必须仍 FAIL」。

## skip_reason（负申报）
#3 单写者动作 + 严格串行：那份跟踪面已被我登记为「另一个写者动过」（D7.2），刷新必须由我按它自己的生产者跑并当场比对
前后读数，不能交出去（交出去会让「谁改的、改成什么」不可归因）。
#4 受管根落地动作：红线 2 要求唯一途径 rule_editor、红线 5 要求落地后三门禁 + disk_registry_diff 三类全 0；
且它是我自己落地件的声明落点问题，责任在我。
#5 最终方案·diff·答复（Lead 自留）。
