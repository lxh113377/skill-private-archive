# r306a — A 臂换装「落地编辑清单」（任务 A1 · r306 派发）

本件只出清单、不落地：权威技能目录本轮零写入（写面只有本目录）。是否宣布换装由 Lead 裁定。

## 三件交付物

1. edits.json — 6 条局部编辑：E1 一条 replace 改 frontmatter 版本对；E2-E5 四条 insert 各钉定一条上游增量；E6 一条 insert 补版本历史行。字段 op / anchor / old / new / why / evidence，另带 swap_pack_entry（证据包里的数组名＋下标＋逐字引用串，供逐条回查）。
2. merged_preview.md — 按清单顺序在内存演算出的新全文（基线 685 换行 → 734 换行），供落地前肉眼核对；只写在本目录。
3. check_r306a.py — 判据：自行重演算再取三读数，并带两条负控腿。

支撑件：criteria_r306a.json（读数表：逐字探针、上游区间、基线 sha、前态计数、执行口径）、local_snapshot.SKILL.md（演算基线 = 重读本地件的冻结快照）、negcontrol_log.txt（控制位与两腿逐字输出）。

## 现形偏差（已实测）

brief 说本地件 675 行、version 1.3.0、sha 前缀 01884cd1；本轮重读实得 686 行（含末空行）、version 1.4.0、last_updated 2026-10-31、sha 前缀 de986705。其版本历史 V1.4.0 行自称四区增量已并入，实为中文转述：四条增量的上游逐字探针在基线上实测 0 命中。故锚点全部按重读现形构造，版本条走 1.4.0 → 1.5.0（不是 1.3.0 → 1.4.0）。落地日若不是 2026-10-31，把 E1 的 new 第二行改成落地日。

## 执行口径

按清单顺序逐条字面拼接：replace 用 new 整串替换 anchor；insert 按 placement 接在 anchor 之后或之前。别走正则替换通道（new 内含美元符与反引号会被误解析），别裁剪 new 的首尾换行（那是与本地行对齐的排版）。本清单只覆盖正文件的增量改写；同计划里另三个整文件 land 项属复制动作。

## 判据命令与期望末行

```
<Python 解释器> -B <本目录>/check_r306a.py
```

末行期望：[R306A:MERGE] edits=6 increments_present=4/4 local_only_kept=2/2 anchors_unique=true version=1.4.0->1.5.0，上一行 GATE=PASS，退出码 0。

## 负控复算入口

```
<Python 解释器> -B <本目录>/check_r306a.py --drop-increment I2   # 期望 3/4 且 FAIL、退出码 1
<Python 解释器> -B <本目录>/check_r306a.py --drop-local LO1      # 期望 1/2 且 FAIL、退出码 1
```

## 结论标注

- 已实测：6 条锚点唯一命中；四条增量逐字块命中且字节级等值；基线每一行在新文里都还在（丢失行数 0）；两条本地独有逐字整块完整；基线 sha 与权威源一致；控制位 PASS；腿 A 对 I1/I2/I3/I4 各跑一次全 FAIL；腿 B 对 LO1/LO2 各跑一次全 FAIL；判据件过语法解析、两件数据过 JSON 解析。
- 部分实测：只在内存演算，未对权威目录写入；上游逐文本体取自 r303b 证据包抓回的候选件，未钉 commit，行号可能随上游漂移（该证据包 unknown 条目 U5 已记此险）。
- 未实测：落地后的加载与注入生效；另三个整文件的复制；门禁跑批（本任务禁面）。

