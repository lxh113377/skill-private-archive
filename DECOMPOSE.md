# DECOMPOSE · r319（「吸收未入口」全库巡检首跑 + browse 对账备料 + coding-agent INC-03 落地走道）

> 本卡先于本轮任何产物写入落盘。起点 bd3b7f2（tag r318 后）。goal 第 90 回合 ⇒ r319。

## 起点实测（现取）
- HEAD bd3b7f2、我名下仓 dirty=0；受管根 HEAD=a0092c9c（我 1.4.0 落地后位）。
- 受管根他面在途脏件（data-analysis/diagram-maker/figma/dingtalk-shared 等，非我产出）⇒ **本轮写面只碰
  coding-agent 与项目仓**；撞车即停（D7.2）。
- r318 揭出新缺陷类：**落盘未入口**（coding-agent 四卷吸收后入口不链=路由不可达）⇒ 同类若在其它 51 对
  存在，吸收成本全空转——本轮首查全库。

## 本轮分解（真实派发 = 2 臂并行 + Lead 2 件）
| # | 件 | 验收 | 写面 |
|---|---|---|---|
| A1 | 入口可达性巡检 52 对全库：正文引用的卷不存在=断链；卷存在而正文不链=孤儿（未入口）；双向+已知
|    | 答案堂（正例=coding-agent 修好后应孤儿 0；反例=git 前态 0fcf7842~1 的 F 臂应报孤儿）| [R319A:ENTRY] court=PASS broken=<n> orphans=<n> | _temp/r319a/ |
| A2 | G4 browse 对账备料（gstack 改配补齐件）：browse 触发面/工具面与本地命令面逐条对账，仍先过堂 | [R319G4:BROWSE] court=pass verdict=<..> | _temp/r319b/ |
| L1 | Lead：coding-agent INC-03（designed-for 分档一句）走 rule_editor；INC-01/02 留重裁（需 references 深改）| compare OK+基线刷新+mirror | 受管根 coding-agent |
| L2 | Lead：paste-clean 例句化入派发模板+收口 | grep 复验+入账/tag/账龄/GM | 项目仓 |

30 秒卡：① ≥2 互不引用工作流 是；② 是；③ 是；④ 齐；⑤ 发 2；⑥⑦ 判据入 brief；⑧ 我复跑巡检+对账各一。
skip_reason：INC 落地=受管根单写者严格串行；例句化/合账=决策本体自留。
