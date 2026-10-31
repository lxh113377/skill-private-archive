# DECOMPOSE · r325（R324-2 两份 spec 兑现 + 需求 2 季度时效实测 + 巡检动线实跑）

> 起点 4425ffa（tag r324，11-01 01:36）｜goal 第 5 回合 ⇒ 轮号 r325（R325-* 领号前核零命中，已核）。

## 起点实测（现取 01:4x）
- 三方一致：HEAD = origin/main = 4425ffa；tags r324/r323/r322 在。
- `05-exec/landing_specs/` 现有 **5 份**（A-prompt-better / frontend-skill / frontend-slides / mcp-builder / security-audit），**仍无 r324/r323a**（= R324-2 的缺口）。
- 需求 2 时效面（现取）：`quarterly_r260/2026Q4/replacement_matrix.json` generated_at **2026-10-27T17:09:50Z**（5 天前）；`replacement_matrix_shadowstrict.json` **2026-10-30T14:16:38Z**（2 天前）；季度总产物 `quarterly/2026Q4/audit.json` 2026-10-25。
- 规范 §2 写「每季度首周（1/4/7/10 月）」⇒ 现在 11-01 已过 Q4 首周，**下一窗口 = 2027-01 首周**；但「当期矩阵是否过期」要按判据口径算，不由我口头判。

## 本轮分解（W=3 ⇒ N=3）
| # | 件 | owner | 判据命令 + 期望末行 |
|---|---|---|---|
| 1 | R324-2 兑现：两份 landing spec（r324 入口可达面 / r323a G-L1 门）+ 逐腿读数 | 臂 A `_repro/r325a/` | `python -B _repro/r325a/check_r325a.py` ⇒ `[R325A:SPEC] specs=2 legs=<n> unverified=<k> teeth=pass` |
| 2 | 需求 2 季度时效实测：规范定义 / 矩阵龄期 / cadence 门绿红 / 输入面守卫 / 下季清单 | 臂 B `_repro/r325b/` | `python -B _repro/r325b/check_r325b.py` ⇒ `[R325B:CADENCE] age_days=<n> verdict=<态> gate_rc=<rc> teeth=pass` |
| 3 | Lead：按附三 §5 的巡检动线**真跑一遍**（不是读它），产出本季入口可达面读数 + 台账/报告/提交/tag/推送 | Lead | 动线三命令全 rc=0，读数落 `06-benchmark/entry_reachability_*.json` |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 是（A 写 spec / B 读 eval+benchmark 时效面）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 是（landing 判据 schema 面 vs 季度节律面）。④ 四问全过。⑤ 发 2 件（件3 自留：写共享台账与动线实跑，最终答复）。⑥⑦ brief 七项与判据齐。⑧ 收件后我复跑：A 挑一条 spec 用 `--neg hand-edited` 验它真参与 R 腿；B 用 `quarterly_cadence_face` 门直接跑一遍对账它的 rc。
skip_reason（件3）：写面冲突（memory/07 与 06-benchmark 共享面，串行）+ 最终方案·diff·答复 Lead 自留。

## 并行写面纪律
- 臂 A 只写 `_repro/r325a/` + 两份新 spec；臂 B 只写 `_repro/r325b/`。Lead 交付前不写这两处。
- 部署面（受管根）本轮**零写入**：本轮三件都不需要改受管根（spec 与时效都是本仓侧）。
