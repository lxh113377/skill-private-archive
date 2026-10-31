# r307a · 第一件真换装（A-prompt-better 1.3.0→1.5.0）需求 6 执行级 A/B · 怎么读这组数

> 结论标记：**已实测**。判定器、两版全文、三条腿读数、spec 五腿复跑全部本轮现取，文末判据命令可复算。

## 0. 一句话读数

执行级五项对这一组 before/after **算不出百分比**：两版字面命令集都是空集，delta 的分母（改前臂 rc=0 数）= 0，
比例 0/0 无定义 ⇒ 判据诚实报 delta=not_applicable verdict=na。这**不是**「增量为零」也**不是**「提升为零」，而是
**这把尺的量程之外** —— 该件换装的增量是四条方法论断言 + 检查清单 +2 项 + 版本头，**零新命令**，本就不该用命令面尺去量。

## 1. 五项读数（本轮真跑，非抄旧件）

| 项（口径逐字沿用 r285 件的 caliber_note） | 改前 1.3.0 | 改后 1.5.0 |
|---|---|---|
| 字面命令集 commands_found | 0 | 0 |
| 实跑数 runnable | 0 | 0 |
| rc=0 数（= delta 公式分母） | 0 | 0 |
| 落盘件数 persisted_artifacts（各臂独立清空目录） | 0 | 0 |
| 声明兑现 doc_claim_met | not_computable | not_computable |

取版 sha：改前 01884cd11aed / 改后 fac939d845fa，与回滚链 pre 01884cd1、现 fac939d8 逐位一致 ⇒ **取版未串（已实测）**。
宽形扫描（额外 19 个命令触发族，含 node/npm/curl/git/pip/pytest/dotnet/docker 等）两版各命中 2 行且**逐字相同、位置相同**
（Done 判据举例片段里的 dotnet run），不构成任一臂的命令面增量 —— 这条只数形、未实跑，标 部分实测。

## 2. 这组数怎么读 —— 需求 6 的证据面在哪

**必须明写：该件的需求 6 证据面 = 内容层（逐字钉定 4/4 + 本地独有 2/2 + spec 五腿全绿），不是执行级 A/B。**
本轮内容层全部现验（非抄 r306）：
- 逐字钉定 4/4：四条上游增量探针（I1 高虚构技法黑名单 / I2 Memory Block 前 30% / I3 Agentic Output Warning / I4 RECENCY ZONE 六问）
  在改前文本各命中 **0**、改后各命中 **1** ⇒ 四条确为本次并入（已实测）。
- 检查清单 +2：两条新增检查项在改前 0 命中、改后各 1 命中（已实测）。
- 本地独有 2/2：LO1 七步闭环衔接、LO2 Level 分流+闭合标签近因的逐字块，改前改后**都在** ⇒ 换装未吃掉本地件（已实测）。
- 加法式零删除：改前正文行逐行比对，**丢失正文行数 = 0**，仅版本头 version/last_updated 两行按预期改写（已实测）。
- spec 五腿独立复跑：R=ok N=ok P=ok V=ok M=ok gate=PASS，其中 V 腿读到 fm=1.5.0/hist=1.5.0/want=1.5.0，
  R 腿读到本件 SKILL.md hunks=9（已实测，本轮只读受管根、判据产物写进本件临时目录）。

所以这组 A/B 的正确读法：**执行级 = na（量程外），内容层 = 全绿**。需求 6 对该件的「替换完成」判据，
落在「逐字钉定可机器核对 + 本地独有守住 + spec 五腿过门」这条**内容契约面**上，而不是「文档多给一条真能跑的命令」这条命令面上。
这与 r285 里 test-driven-development / frontend-slides 两件**改前改后五项逐项相等**的先例同族 —— 那两件差值零是「没碰命令面」，
本件差值不可计是「根本没有命令面可碰」。三种情形都说明：**执行级五项对指南性增量天然不敏感**。

## 3. 这对「任务级 30%」意味着什么

- 现行唯一可引用的执行级先例 r281 给 +22.22%（Q_A=18→Q_B=22），**其增益全部来自新增一条真可跑、真可落盘的命令**
  （Step 2b 的 persist + output-dir 调用）—— 那是**命令面增量**。本件是**内容面增量**，无同类新增，借不到这 +22.22% 的机制。
- 拿本件的执行级读数去凑需求 6 的「≥30%」是**方法外推错误**：r281 的六维 Q 锚定在 dashboard 设计系统那道题上
  （含产物存在/内容完整/未编造/指令遵循四维），本件没有该锚题输入 ⇒ 只能借它的**公式形态**与**负控纪律**，不能借它的**分数面**（腿 B 实测拒因成立）。
- 结论对任务级：**单靠换装文本 A/B，此类指南性件恒为 na，不产出任何可引用的执行级百分比**；
  要拿执行级数字论证该件收益，得先造一道与 prompt 优化对口的**锚题**、同一题面双臂执行，才有资格谈 r281 式百分比。
  这条作为下一步登记（属本件范围外的待办；卡点=无锚题输入，实测证据=本件 delta 无定义 + 腿 B 拒绝外推）。

## 4. 两条负向对照（都有本轮实测输出，逐字见数据件的 negative_controls）

- **腿 A（防恒 0/恒 na 假平）**：判定函数不动、真实解释器不动，只把两版换成人为有差的两份文本（改后臂多 2 条命令声明）
  ⇒ 读数 q_a=1 q_b=3 delta=+200.00% verdict=reported、five_items=5/5。**证明尺子真的在数东西**，不是对任何输入都吐 na。
- **腿 B（防把方法外推）**：把 r281 原题集逐字与本件任务文本喂同一 transfer 判据 ⇒ 题面不同，判据**拒绝**出百分比，
  报 delta=not_applicable verdict=na 并点名拒因 rubric_is_task_anchored_and_task_text_differs。**证明判定不会硬把不相关题集外推出一个数**。

## 5. 已知偏差与如实挂账

1. 查询型剔除在本件为空操作（两版提取命令皆 0，无从剔除）。
2. 声明兑现项两版都判 not_computable（无可机械判定的执行声明），**不冒充 Y/N**。
3. 宽形扫描的 dotnet 两行只数形未实跑；即便实跑也不进任一臂差值（两臂同现，非增量）。
4. 本轮步数超 brief 上限（≤12，实际约 16）：前段读三件现成口径 + 取两版全文 + 结构探查占用较多回合；
   产出三件均完整无截断，停在哪 = 已完成，无半件。
5. 受管根与记忆根全程只读（两版全文用 git show 取，未 git 写、未写受管根、未写记忆根、未跑 run_gates）；
   spec 五腿复跑仅把判据 JSON 写进本件临时目录。

## 6. 判据命令与期望末行（本轮全部实跑通过）

```text
PY=C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
# (1) 真臂 1.3.0 vs 1.5.0 —— 期望末行 five_items=4/5 q_a=0 q_b=0 delta=not_applicable verdict=na
$PY -B check_r307a.py --mode five_items --before before_130.md --after after_150.md --workdir work_real --py "$PY"
# (2) 腿 A 负控（人为有差伪件）—— 期望末行 five_items=5/5 q_a=1 q_b=3 delta=+200.00% verdict=reported
$PY -B check_r307a.py --mode five_items --before sim_before.md --after sim_after.md --workdir work_sim --py "$PY"
# (3) 腿 B 负控（r281 原题集逐字 vs 本件题面）—— 期望 REFUSE 行 + 末行 five_items=0/5 delta=not_applicable verdict=na
$PY -B check_r307a.py --mode r281_transfer --task-file task_r307a.txt --rubric-task "<r281 件 task_text 字段逐字>"
# (4) 内容面旁证：spec 五腿独立复跑 —— 期望 gate=PASS、R/N/P/V/M 全 ok
$PY -B 05-exec/landing_replay_check.py --spec 05-exec/landing_specs/A-prompt-better.json --js <本件临时目录>/landing_legs_rerun.json
```

实测时刻 2026-10-31T07:50:23.138Z ｜ 改前 sha12 01884cd11aed ｜ 改后 sha12 fac939d845fa。
