# DECOMPOSE · r324（把巡检判据从一次性目录搬进常驻面并正式登册 = 需求 5 的真落地）

> 起点 9f0a992（tag r323，11-01 01:08）｜goal 第 4 回合 ⇒ 轮号 r324（R324-* 领号前先核零命中）。

## 起点实测与缺口定位（现取）
- 本仓/受管根/远端三方一致：HEAD = origin/main = 9f0a992。受管根 79 行他人在途（索引 0 行）。
- **需求 5 的真缺口**：r321–r323 产出的四件巡检判据（入口普查 v1/v2、嵌套闭包审计、G-L1 目标件门）**全部还住在 `_repro/`**。
  `05-exec/` 现只有 r113_quarterly_audit / r150_volume_tiers / r155_selftest_census / r260_quarterly_cadence，**没有入口可达面**。
- 准入门 `.read_face_registry.json` 现 51 条，结构 = `{"<script>": {"evidence": "<路径>", "registered_at": "<ts>"}}`；未登册的产读数脚本会被判 UNDECLARED（r260 实测硬拒）。
- 需求 2 时效：`replacement_matrix_shadowstrict.json` = 2026-10-30T14:16Z（3 天前，在效期内）；`quarterly/2026Q4/audit.json` = 2026-10-25（rows=0 是它的结构）。

## 本轮分解（W=3 独立就绪 ⇒ N=3）
| # | 件 | owner | 判据命令 + 期望末行 |
|---|---|---|---|
| 1 | 入口可达面**常驻化**：把 v2 普查（含三处修正 + 四桶）从 `_repro/r322b/` 搬进 `05-exec/` 为 `r324_entry_reachability_face.py`，输入面不用 `_temp`/`_repro` 硬编码，输出可落 `06-benchmark/` | 臂 A `_repro/r324a/` | `python -B _repro/r324a/check_r324a.py` ⇒ `[R324A:PERMANENT] portable=ok parity=ok teeth=pass` |
| 2 | G-L1 目标件门常驻化 + 落 `landing_specs` 三件扩展（G-L1 gate / v2 census / 本件自身），使 `landing_replay_check.py` 能对它们复算 | 臂 B `_repro/r324b/` | `python -B _repro/r324b/check_r324b.py` ⇒ `[R324B:SPEC] specs=<n> replay=ok teeth=pass` |
| 3 | 季度巡检规范补「入口可达面」巡检段 + 判据件入册义务（把 R322-2 的验收靶从纸面变成有主） | **Lead 自留**（写 04-plan 共享件） | 规范件新增段可 grep 到；与 05-exec 实际件名一致 |
| 4 | Lead：登册（`.read_face_registry.json` 加 2 条）+ 跑准入门 + 台账/报告/提交/tag/推送 | Lead | `python -B 05-exec/r129_reconcile_admission.py` ⇒ 未声明数不增 |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 是（A 搬普查判据 / B 扩 landing spec / 两件写面不相交）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 是（`05-exec/` 常驻面 vs `05-exec/landing_specs/` 复算面）。④ 四问全过。⑤ 发 2 件（件3/件4 自留：写面为 04-plan 共享件与登册面，同文件先串后派 + 最终答复）。⑥⑦ brief 七项与判据齐。⑧ 收件后我复跑：A 用它的 parity 腿复算 624/552/72 三读数与我 r322 读数逐项对；B 跑 `landing_replay_check.py --spec` 验两件 spec 的 R/N/P/V/M 五腿。
skip_reason（件3/件4）：写面冲突（04-plan 与 .read_face_registry 属共享权威件，须串行）+ 最终方案·diff·答复 Lead 自留。

## 并行写面纪律
- 臂 A 只写 `_repro/r324a/` 与 `05-exec/r324_entry_reachability_face.py`（新件，非他人面）；臂 B 只写 `_repro/r324b/` 与 `05-exec/landing_specs/*.json`。
- Lead 在交付前不写这两处；登册与规范件由 Lead 串行做。
- 每笔提交前核 `git show --name-status` 非本会话路径 = 0。
