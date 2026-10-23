# 07-next-steps.part127.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R155-2（r155 登记，P1）** **唯一候选待复核**：`05-exec/r51_retrieval_fixtures.py` 的 `bad` 计数器被判「仅赋值未引用」—— 属**候选非判决**，须读一次退出路径确认（真缺陷则修，假阳则再收窄判据）。**该面本轮自身连抓三轮假阳（候选 6 → 3 → 1）**：① 初版按「退出那一行含旗」判接线 ⇒ 把 `if ok == n: return 0` 形态全判死旗（含我自己的 r150_gov_fixtures.py）；② 家族规则后又把 `bad = json.loads(...)`／`bad = [n for ...]`／`bad = re.findall(...)` 这三种**名字撞车**当成判定旗。收窄为「**计数器**（赋 int 常量或 `+=`）家族 + AST 守卫检测（If 测试含旗 且 分支内有退出）」，撞车项降级单列。 【r156 裁决=作废（终局）：r51_retrieval_fixtures.py 系假阳第4形态——bad 是失败清单经 check(not bad) 汇入 RESULTS，退出由 fails 把守；判据已修（AugAssign 仅数值 += 算计数）且 --selftest 死旗腿仍在牙（SELFTEST-PASS）】

- [x] **R155-3（r155 登记，P1·已落地→见 R156-1）** **普查面登记为门（第 61 门）**：本面现为手工面，须入 `run_gates.py#GATES` + `r130 --record` + `.read_face_registry.json` 登记（口径同第 57–60 门：`--json` 留痕 + pass_token + portable 标注）。验收：`python 05-exec/run_gates.py` 末段「执行 61 门」且 `gate_table_reconcile` 未登记 0。 【r156 裁决=执行（终局）：已入册第 61 门 selftest_census_face（GATES 61、对账 1 行、read_face_registry 齐）】

- [x] **R154-1（r154 登记，P0·已落地）** **归档环节补证**：本迁移同时补上目标① 的**归档**环节 —— 规则立了却没归档是实践缺口（r154 实测坐实）。归档件带 header 注明来源与「原文零改写（R241）」；迁移工具 `05-exec/r154_shell_archive.py` 内置四条自证（V1 迁移量≥20KB / V2 每份≤4096B / V3 分卷拼接**逐字节等于**原文 / V4 壳内无残留且指针路由俱在），**不通即拒绝落盘**（首跑即抓到两处自身缺陷：指针标题误命中规则正则、分块按行数算漏换行）。 【r159 裁决=销账｜r158 复验成立：memory/06-constraints.part6..part16 共 11 个归档件，逐个带 header 声明来源 + 原文零改写（R241）；取值 python ./_temp/r158_hdr.py。自抓：首版脚本用「前 6 行含归档或来源」计数误报 1/16，改逐件读全头后为 11/11 —— 判据自身缺陷同 X-7，未凭它下结论】

- [x] **R154-2（r154 登记，P0·未落地·待归并）** **提交待归并**：本轮所有产出**未提交** —— 工作区 `memory/07-next-steps.md`、`AGENTS.md`、`05-exec/run_gates.py`、`05-exec/r137_commit_gate_map.py`、`transmit_proposals.json`、`gate_reconcile_registry.json` 等**混有并行会话的在途改动**（如 r151 条目、`r149_derived_freshness.py` 的 M 态）；按 G-b 前提②「不代他人提交」禁整体 `git add`。⇒ 门禁 `commit_gate_map_face` 因此恒 UNVERIFIED（空暂存清单，**提交即解**），`gate_run_freshness` 随之判红（自指元门，读上一行台账）。处置：下一轮先跑 G-a/G-c 三闸确认并行会话已静默，再按**文件点名**提交（禁目录级 add），逐笔 `git show --name-only` 核对。 【r155 裁决=执行（终局）：已按文件点名提交 85162a5（44 件）；提交前过 G-a/G-c 并核实 HEAD dd67102 只含对方自己的件】

