# DECOMPOSE · r323（首个真实补链落盘 + 需求6 判据口径改造预研 + G-L1 门定义机械化）

> 起点 ccfa01f（tag r322，11-01 00:28）｜goal 第 3 回合 ⇒ 轮号 r323（`grep -rn R323- memory/ 04-plan/ 05-exec/ 06-benchmark/` 现值须先核为 0）。

## 起点实测（现取 00:31）
- 受管根 79 行 dirty，但 **索引暂存 0 行** ⇒ rule_editor 落盘前提（索引空）满足；落盘风险面 = 目标件本体是否 CLEAN。
- 目标入口件态：**CLEAN 5 个**（gstack / ui-ux-pro-max / theme-factory / agent-browser / frontend-skill）；**DIRTY 8 个**（ppt-master / story-setup / story-long-write / data-analysis / diagram-maker / hyperframes-media / story-review / story-short-analyze）⇒ 后者一律不动。
- 逐条补链面实测（v2 prose 孤儿）：只有 **2 件是「1 条文件、真该挂链」**：`agent-browser/references/commands.md`（293 行完整命令参考）、`frontend-skill/references/tells.md`（116 行 dated registry）；其余全是目录级（theme-factory 10 个 themes、ui-ux-pro-max 2 个 upstream 卷、gstack 6 个嵌套已可达）。
- r322 三件交付件全部在盘可复算（verdict.json / census_v2_top.json / corpus_census.json）。

## 本轮分解（W=3 独立就绪 ⇒ N=3）
| # | 件 | owner | 判据命令 + 期望末行 |
|---|---|---|---|
| 1 | 真实补链落盘：agent-browser 的 references 导航表补 `commands.md`（或裁定它是刻意不链的旧镜像残留 ⇒ 改为剪枝并记录理由）；+ frontend-skill/references/tells.md 判定 | **Lead 自留**（写面 = 受管根入口件，唯一途径 rule_editor） | 落盘后 `git -C D:/global_skills show --name-only HEAD` + `python -B _repro/r322b/r322_v2_census.py --closure top` 该件 orphans 下降 |
| 2 | G-L1 门定义机械化：把「目标件本体是否 CLEAN」写成可复跑判据（现在只落纸在本表 §7.3），替换「全仓 0 行」这条永不满足的字面门 | 臂 A `_repro/r323a/` | `python -B _repro/r323a/check_r323a.py` ⇒ `[R323A:GL1] targets=13 clean=5 dirty=8 gate=ok teeth=pass` |
| 3 | 需求6 判据口径改造预研：把 `exact` judge 能否扩成「任务书 ⇒ 应触达哪几个 skill」的多标签尺做可行性取证（含现成 `frozen_blind_eval.py` 的 judge 实现读码、以及是否已有 annotate 多标签能力） | 臂 B `_repro/r323b/` | `python -B _repro/r323b/check_r323b.py` ⇒ `[R323B:MULTILABEL] verdict=<REACHABLE|PARTIAL|BLOCKED> judges=<n> teeth=pass` |
| 4 | Lead：台账/报告收口 + 三读数提交 + tag + 推送复算 | Lead | add 后 / commit 后 / 消息声明数 三者一致 |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 是（A 写判据 / B 读 eval 源码）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 是（受管根本体 vs 焚诀 eval 源码）。④ 四问全过。⑤ 发 2 件（件1/件4 自留，理由 = 写面为受管根入口件与共享台账）。⑥⑦ brief 七项 + 判据写全。⑧ 收件后我复跑：A 逐件现核 clean/dirty 与 `git status` 对账；B 用其读数对 frozen_blind_eval.py 的 judge 分支逐条核。
skip_reason（件1/件4）：写面冲突（受管根入口件唯一途径 rule_editor，他人 79 行在途）+ 最终方案·diff·答复 Lead 自留。

## 并行写面纪律
- 臂 A/B 只写各自 `_repro/r323[ab]/`；Lead 在交付前不写这两目录。
- Lead 落盘只动 CLEAN 件本体，DIRTY 件零触碰；每笔 commit 前核 `git show --name-status` 非本件路径 = 0。
