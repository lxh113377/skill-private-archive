# DECOMPOSE · r321（收双臂产出 → 补链批次表 + 断链口径复核 + 账龄 4 条处置）

> 本卡先于本轮任何产物写入落盘。起点 7019ce9（tag r320 后）。goal 第 1 回合（本会话）⇒ 轮号按仓内口径取 r321（git log 最大 rNN 320 + 1）。

## 起点实测（现取，2026-10-31T21:3x）
- 三解释器探针：venv 3.13.14 OK / LibreOffice 3.13.15 OK / `C:\Program Files\Python312` ENOENT（README 门禁行写的这个已不存在 ⇒ 本轮用 venv，并登记文档漂移）。
- A1 臂（入口普查）已交付：`_repro/r320a/entry_census/report.r320.md` + `entry_scan.r320.json`，court=pass，broken_total=10、orphan_total=624、orphan_kb=4781。
- A2 臂（browse 对账）已交付：`_repro/r319b/report.md`，`[R319G4:BROWSE] court=pass verdict=unclear matched-axes=3/6`（合格产出）。
- 两臂均已在 git 暂存（`git status` 58 行），**未提交** ⇒ 本轮首务 = 复跑判据收件，再并入。
- 账龄现值（`06-benchmark/r320_debt.json` @21:04）：OVERDUE 4（R311-2 账龄9轮、R317-2/3/4 账龄3轮）、ACTIVE 6、DECIDED 332、REPEAT 0；`input_face.dup` ok=false（撞号 3 组）⇒ 面 FAIL 既存。

## 本轮分解（W=无依赖并行面 4 ⇒ N=max(2,min(8,4,ceil(T/45)))=4）
| # | 件 | owner | 验收（判据命令 + 期望末行） |
|---|---|---|---|
| 1 | 复跑双臂判据（check_r319a / check_r319b）独立取证，不采信自述 | Lead | 两条原命令逐字重现，末行与臂报告一字不差 |
| 2 | 4 条 OVERDUE 底层事实现核（已落地/未落地 + 证据路径）⇒ Lead 落裁决 | 臂 A `_repro/r321a/` | `python -B _repro/r321a/check_r321a.py` 末行 `[R321A:DEBT] ok=4/4` |
| 3 | A1 断链 10 条真伪二分（`split-NN.md` 疑为模板占位符=判据假阳）⇒ 修正口径 | 臂 B `_repro/r321b/` | `python -B _repro/r321b/check_r321b.py` 末行 `[R321B:BROKEN] real=<n> placeholder=<n> teeth=pass` |
| 4 | A1 孤儿榜→补链批次表（件级 top + 每批动作/回滚/优先级），落 `04-plan/` | Lead | 批次表内每条路径在 `entry_scan.r320.json` 可反查命中 |
| 5 | 轮次报告 + 台账收口 + 显式清单提交 + tag + 推远端复算 | Lead | `[GATES:*]` 现读；`git rev-parse HEAD` == `git ls-remote origin` |

## 30 秒卡 8 问
① 互不引用工作流 ≥2 ⇒ 是（件2 读台账面 / 件3 读受管根面，零交叉）→ 必须派 ≥2。② 单件 ≥3 回合 ⇒ 是。③ ≥2 独立面取证 ⇒ 是。④ 四问（可独立验收 ∧ 写面不相交 ∧ 输入可预固定 ∧ ≤45min）⇒ 两件全过。⑤ 本轮发 2 件（≠1）。⑥ brief 七项随派发正文写全。⑦ 每件判据命令+期望末行见上表。⑧ 收件后我复跑：件2 我复跑 r38_debt_aging 现读 OVERDUE 归零；件3 我复跑 check_r319a 原命令对比其修正前后读数。
skip_reason：件1/件4/件5 = Lead 自留（最终方案·diff·答复 + 写面为共享台账，同文件先串后派）。

## 并行写面纪律（D7.2）
- 臂 A/B 只准写各自 `_repro/r321a|b/`；Lead 在两者交付前不写这两目录。
- 双臂产物名带轮号后缀，禁与规范名抢写（r320 那次 Lead 自己抢写过，见 `CONFLICT_NOTE_lead_self.md`）。