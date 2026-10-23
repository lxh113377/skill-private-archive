# 07-next-steps.part137.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R150-3（r150 登记，P1·待归属方）** 体量册 4 条结构缺陷**转办 A-project-handoff**（写入侧在 `handoff_lib/volumegov.py`，R269 不代改）：① `NO_SHARED_KEY` 快照行缺 `head` ⇒ 联动只能按日窗口粗联结；②③ `files` / `growth_ratio` 覆盖 0/41；④ 体量册末条 3.89 天前 > 2 天阈值。**常驻复算面 = 本仓 `05-exec/r150_gov_link.py`**（#47 三件套）。验收：该件 `defects[]` 中这 4 个 kind 全部消失当天即闭环日。取值：`python 05-exec/r150_gov_link.py --json <件>` 读 `defects[].kind`。 【r156 裁决=降级（长期看守）：剩 2 类归属方 schema 缺陷（head 主键 / files+growth_ratio 字段），常驻复算面=第 59 门 gov_link_face 每轮真跑；数值仍被棘轮看守，非作废】

- [x] **R150-4（r150 登记，P1）** 规则契约 R-ENUM / R-ATTR（`D:/global_skills/A-skill-manager/references/governance.md`）**缺 review 环节痕** ⇒ 契约面出 P0 预警 2 条。处置二选一：补对账/夹具登记痕，或把该环节对这类契约显式标为「无独立对账面」（须证实并落文档，禁改判据凑绿 R263）。验收：`python 05-exec/r150_contract_lifecycle.py` 的 `风险预警 P0=0`。 【r152 裁决=执行（终局）：规则契约 review 由关键词代理改记 UNVERIFIED（#32 自抓），P0 预警 2 到 0】

- [x] **R150-5（r150 登记，P1）** **自适应调整机制缺位**：本仓 `memory/06-constraints.md` 无「体量预算」声明行 ⇒ 60 个阈值全吃归属方 `DEFAULT_BUDGET`，项目侧无法审计/微调。处置：按 `templates/06-constraints.md.tmpl §体量预算` 落声明行（先只声明不改值，生效值须回显）。验收：`python D:/global_skills/A-project-handoff/scripts/handoff.py volume --print-budget --project "<本项目根>"` 的 `sources` 不再出现「存在但无「体量预算」行」。 【r150 裁决=执行（终局）：06-constraints.md 已落体量预算 15 行（值=代码默认，零行为变更），--print-budget sources 已变更】

- [x] **R150-6（r150 登记，P2）** 风险预警现为 **advisory 不阻断**；接 `pre-commit` 分级阻断（**仅 P0 预警阻断**，P1/P2 只显形）属 r155。验收：造一条 P0 预警（如临时删某门脚本使 `MISSING_DRAFT` 成立）⇒ hook 阻断并留痕，随后还原。⚠️ 阻断行为**本轮未实测**（#33 声明）。取值：`python 05-exec/r150_contract_lifecycle.py` + `.git/hooks/pre-commit` 运行日志。 【r152 裁决=执行（终局）：P0 预警即判红；r137 已挂契约纪律面 tuple 前缀；夹具 p5a-p5d + m6 实测有牙（29/29）】

- [x] **R149-1（r149 登记，P0·已落地）** `05-exec/r149_derived_freshness.py` 已入册为**第 56 门**（`derived_freshness_face`）：只读 import 焚诀 eval/derivative_watch.stale_sources()（对 eval 零写入，重建动作仍归对方=R269），把第 11 类「等重建」变成机器读数。现算：stale_gsap=True lag=7339.3s（190 件唯一 1 条）。**终判闭环日 = stale_gsap 转 False 当天**。取值：`python 05-exec/r149_derived_freshness.py --json <件>`。 【r155 裁决=销账｜r151 实测该门 PASS 且已修连坐；终判闭环日已到达（stale_gsap True→False，归属方 19:39 重建 BGE），R149-1 的验收本体达成】

