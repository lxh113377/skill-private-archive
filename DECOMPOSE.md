# DECOMPOSE · r329（兑现两条挂账：死链门 --exclude 接门表 + volume_tiers 逐件越限腿）

> 起点 340e01a（tag r328，11-01 02:3x）｜goal 第 9 回合 ⇒ 轮号 r329（R329-* 领号前核零命中）。
> **本卡先于本轮任何产物写入落盘**（R318-2 纪律；r328 我又违反过一次，本轮不再犯）。

## 起点实测
- 两条挂账均为第 2 次到期 ⇒ 按 R271-2 本轮必须动手，不得再挂。
- R321-1 现核：`05-exec/run_gates.py` 的 md_deadlink_face argv 仍无 `--exclude`；`r220_md_deadlink.py:209-222` 已有 `--exclude=` 实现（但 `startswith` 前缀匹配，不支持通配）。
- R321-6 现核：`05-exec/r150_volume_tiers.py` 不验逐件越限；README **21326B > 16384B** 而该门判 PASS。

## 本轮分解（W=2 ⇒ N=2，但同时派生 1 个复验 job）
| # | 件 | 判据 |
|---|---|---|
| 1 | R321-1：r220 `--exclude` 升级为 fnmatch + 门表 argv 接线 + 变异腿（真死链仍须点名） | `md_deadlink_face` 转绿且 selftest 仍 PASS |
| 2 | R321-6：volume_tiers 加 `root_doc_max` 逐件检查腿（README 显形 OVER 或达标） | 门输出含逐件越限清单，README 现状如实判 |
| 3 | 全量门复验（后台 job） | 红门数不增于起点 |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 是（死链门面 / 体量门面，两件写面不相交：run_gates.py 的 argv 段 vs r150_volume_tiers.py）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 是。
④ 四问过。⑤ 发 0 臂（**理由**：两件都要改同一批门相关文件且需串行跑全量复验；臂三连全灭后按 R325-4 新策略，臂不占关键路径 ⇒ **改为 Lead 自干 + 后台 job 复验**）。
⑥⑦⑧ 见上表。
skip_reason：写面冲突（run_gates.py 与门复验共用同一仓写面，臂并行易撞）+ 严格串行（改判据→跑门→看红）。

## 纪律
- 本轮改的都是本仓 05-exec/*.py（判据本体）⇒ 改后必须全量门复验，禁只跑单门就宣布绿。
- 受管根零写入。
