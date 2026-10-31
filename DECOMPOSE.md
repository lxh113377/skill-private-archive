# DECOMPOSE · r331（需求 2 的「社区活跃度 / 维护状态」两维：实测成立 + 建时效守卫判据）

> 起点 92643ba（tag r330）｜goal 第 11 回合 ⇒ 轮号 r331（`R331-*` 领号前核零命中）。**卡先落**。

## 起点实测（本轮现取）
- r330 后台门 job（bash-193）仍在跑，输出直落文件（40 行）；本轮不阻塞等它，收尾时再收。
- **需求 2 的数据面其实是齐的**（我上一轮看错）：`replacement_matrix.json` 的 `rows[].candidates[]` 每件都带
  `stars / pushed_at / license / archived / score5{fct,eff,compat,docs,community}` —— 活跃度（stars/community）与维护状态（pushed_at/archived）都在。
- 但 `upstream_meta` 顶层字段**不存在** ⇒ 没有「上游仓级别的汇总」面；且**这两个维度没有任何时效守卫**。

## 本轮要测的两个数（已现算，待写进判据）
- 937 个候选里 `pushed_at` 超 12 个月的 = **1** 件（`trimstray/test-your-sysadmin-skills 2024-11-19`，占 0.1%）；
- `archived=true` 的 = **1** 件。
⇒ **「维护状态良好」实测成立**，但**没有任何判据会在它下次变坏时报警**。这就是本轮要补的。

## 本轮分解（W=2 ⇒ N=2）
| # | 件 | 判据 |
|---|---|---|
| 1 | 写 `05-exec/r331_candidate_health.py`：对矩阵 937 候选逐件判 `pushed_at≤12个月` / `!archived` / `license` 非受限，输出三态汇总 + 逐件超期清单 | `[R331:HEALTH] cands=<n> stale=<k> archived=<k> restricted=<k>` |
| 2 | 接进季度巡检动线（附三 §5 补一行）+ 台账/报告/提交/tag/推送 | 动线命令可跑通 |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 否（同一件事的两步：量→守卫）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 否。
⇒ 命中「严格串行」（后一步输入=前一步实测读数），**不派臂**（且臂三连+两连全灭，按 R325-4 不占关键路径）。
④ 四问过。⑤ 发 0。⑥⑦⑧ 见上表。
skip_reason：**严格串行**（守卫判据必须基于实测读数写阈值；先量后写不可并行）。
