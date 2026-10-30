# R291-B2 mcp-builder 执行级 A/B —— 判据与读数（缩范围重派补齐件）

本轮只补少的两件（判据 + 读数）；存活资产（harness / cmdspec / 两臂文本）一律只读复用。
所有数字都来自本轮真实跑出来的证据件，凡标「已实测」的都可在 §9 判据命令下复算。

## 0. 一句话结论

改前 2 条文档命令面 / 1 条 rc=0；改后 3 条 / 2 条 rc=0。新增那 1 条（B 独有 codemod）真跑通并真把
v1 工程改写成 v2（源码 import 换包 + manifest 换包）；产物面持平 1 对 1。已实测。

## 1. 基准坑实测（每轮重跑 git，不抄表）

| 点位 | ref | blob 前 12 | 字节 | 意义 |
|---|---|---|---|---|
| before | 79862372~1 | 5e3fac986fe7 | 9132 | brief 指定的改前 ref |
| after | 79862372 | 8f640a5939ca | 11436 | R312 换装提交（改后） |
| BASE | e64c17d3 | 5e3fac986fe7 | 9132 | 最后一个真动 mcp-builder/SKILL.md 的提交 |
| 他会话提交 | 079b91f3 | 5e3fac986fe7 | 9132 | brief 点名的坑位探针 |
| HEAD | HEAD | 8f640a5939ca | 11436 | 现头，证明改后无后续覆盖 |

判读：before == BASE == 079b91f3（同 blob 5e3fac986fe7）=> 079b91f3 那类他会话提交没动过本文件，
本行的 ~1 确实等于改前态；after == HEAD => 改后即现头。79862372 的直接父 3da30832 动的是别的面
（ui-ux-pro-max），未动本文件 —— 这正是 brief 警告的那类坑，已实测排除。已实测。

## 2. 口径（与 r285/r281 逐字对齐）

字段名与语义复用 自建skill优化/06-benchmark/r285_exec_commands_ab.json 的 caliber_note：判据件在运行
时直接读那份权威件取基底文本（读不到就 SystemExit，禁止凭记忆复述口径），只覆盖 mcp-builder 行特有
的形状差异（§6）。commands_found 的分母来自受管的 r285 抽取器 _repro/r285l/r285_common.mjs 的
extractCommands（由 harness 直接调用），未另立触发词。

三分类纪律（本轮三类都为 0，且都不进 rc_zero、不记文档缺陷、不记 0 增益）：
- 工具链缺失 => blocked_not_runnable：0（npx 与受管 python 都在 harness 的 PATH 上）。
- 需外部凭据 => needs_external_account：0（三行都不打第三方账号门；本轮未创建任何凭据）。
- 占位符解不开 => placeholder_unresolved：0（fixture 说明见 §3）。

## 3. 逐命令真实 rc 与产物

两臂各自先 wipe 自己的树；每行跑前再快照它声明的 output 目录，只有新出现的文件才算产物。
fixture（your_server.py 与 v1 形 codemod 工程）写在任何行之前 => 永不计产物。

| 臂 | 命令（文档字面） | argv 形态 | 真实 rc | stdout/stderr | 新产物（路径+字节） | 断言 |
|---|---|---|---|---|---|---|
| A | npx @modelcontextprotocol/inspector | literal | SIGNAL:SIGTERM（25s 超时掐停；service 永不退出） | 361B / 810B | 无 | banner=true |
| A | python -m py_compile your_server.py | resolved | 0 | 0B / 0B | py_work/__pycache__/your_server.cpython-313.pyc = 1517B | artifact=true |
| B | npx @modelcontextprotocol/codemod@latest v1-to-v2 | literal | 0 | 1072B / 810B | 无（就地改写） | gained/kept_away/rewrite_met/manifest_has_v2/manifest_drops_v1 全 true；src 389B 到 429B，sha12 c231b6101238 到 2fd7f5c51d03 |
| B | npx @modelcontextprotocol/inspector | literal | SIGNAL:SIGTERM | 361B / 810B | 无 | banner=true |
| B | python -m py_compile your_server.py | resolved | 0 | 0B / 0B | py_work/__pycache__/your_server.cpython-313.pyc = 1517B | artifact=true |

A 臂 banner 实证片段（stdout 原文）：MCP Inspector Web is up and running at: http://127.0.0.1:6274
codemod 改写实证（B 臂 work/run/mcp-builder_B/codemod_proj）：src_server.ts 的 import 变成
@modelcontextprotocol/server 与 @modelcontextprotocol/server/stdio 加 zod；package.json 的 dependencies
由 @modelcontextprotocol/sdk ^1.0.0 变成 @modelcontextprotocol/server ^2.4.0 加 zod ^4.2.0。已实测。

## 4. 读数与增益

| 字段 | A 改前 | B 改后 | delta |
|---|---|---|---|
| commands_found | 2 | 3 | +1 |
| runnable | 2 | 3 | +1 |
| rc_zero | 1 | 2 | +1 |
| blocked_not_runnable / needs_external_account / placeholder_unresolved | 0 / 0 / 0 | 0 / 0 / 0 | 0 |
| persisted_artifacts | 1 | 1 | 0 |
| doc_claim_met | Y | Y | 0 |
| executions / variant_executions | 2 / 0 | 3 / 0 | +1 / 0 |

doc_claim 主张按臂文本自动选面：A = 3.2 的 Python 校核真 rc=0 且落产物；B = A 的全部 加 B 独有 codemod
真改写。B 独有行是 cmdspec 内置、靠抽取器在臂文本里命中才跑 => 读数不由人挑（反挑闸见 §5）。

## 5. 退路条款（本行不触发）与反挑闸

改前 2 条、改后 3 条都实测跑过 => 「文档本就无可执行命令」的退路不触发；若真为零，本件会如实记
commands_found=0 并写「无命令面可测」，绝不造一条文档里不存在的命令凑增益。造假在机制上不可能：
抽取器命中的每条 literal 必须有手排 argv 行，否则 harness 直接抛错停摆（本轮 unmatched=0）；反过来
cmdspec 里有而臂文本没有的行自动跳过 —— 负控 1 里 codemod 行就是这样消失的（skipped 为
["mcpbuilder.codemod"]）。已实测。

## 6. 与 r285 那 3 件的可比性

可比：字段名、语义、抽取器、三分类都一致；r285 三件（ui-ux-pro-max 引自 r281、test-driven-development、
frontend-slides）与本行同形 —— 跑文档字面命令，读 rc 与新产物。三处差异必须写明才叫可比：

1. 本行含一条永不退出的 service 命令（inspector），r285 三件没有这种形状。它进 commands_found 与
   runnable，由 cmdspec 的 requires_rc_zero=false 排除在 rc_zero 分子之外，证据是 banner 断言；两臂同形
   => 对 delta 贡献 0。既不虚增增益，也不被当成文档缺陷。
2. 本行的核心增益效果是就地改写而非新增文件，所以判定用 rewrite 断言加 manifest 换包，不能用
   persisted_artifacts 计数（r285 的 ui-ux 行是产物型，那里计数才正当）。
3. 被检面同口径：都只看该臂 SKILL.md 一个文件（rel = mcp-builder/SKILL.md）。reference 指南
   node_mcp_server_v2.md 里另有 4 条 literal（npx -y / inspector node dist/index.js / codemod /
   npx tsc --noEmit，见 _temp/r291b/texts/extract_r285caliber.json）不在被检面内 => 与 r285 一致，不是遗漏。

## 7. 负向对照两腿（逐字输出）

腿 1 同文必同读（把 B 臂文本换成 A 那份，走 harness 的 sub 模式重跑）：
```
[NEGCTL-1] identical=True PASS: identical text -> identical readings, field by field
[NEGCTL-1] B text=32f54257ab8b A text=32f54257ab8b substituted_B_with=SUBSTITUTED:run_A_SKILL.md
[NEGCTL-1] B-only codemod row skipped after substitution: ["mcpbuilder.codemod"] differing_fields=[]
两臂读数逐字段相等：found=2 runnable=2 rc0=1 blocked=0 ext=0 unresolved=0 art=1 claim=Y exec=2 var=0
```

腿 2 篡改一个 rc_zero 写进副本重算：
```
[NEGCTL2] tampered field = mcp-builder.arms.B.rc_zero 2 -> 1
[NEGCTL2][validator] [CONSISTENCY] FAIL
[NEGCTL2][validator] [MISMATCH mcp-builder.arms.B.rc_zero: stored=1 recomputed=2]
[NEGCTL2][validator] [EXEC-AB-B] rows=1 commands_ok=2/3 artifacts_before=1 artifacts_after=1
[NEGCTL2] validator_exit=2 named_field=YES copy_deleted=YES residue_hits=0
[NEGCTL2] PASS: teeth confirmed (MISMATCH named, non-zero exit, copy removed)
```

诚实标注（不是藏拙）：identical 判定故意不含 inspector 的 rc —— 它是 service 行，rc 由超时/端口时序
决定而非文本决定（修补前臂 B 曾因端口占用读 rc=1，正是这条的证据）。该排除项写在判据件的
NC1_SUB_KEYS 注释里，out.json 的 negative_controls.control_1_identical_text.excluded_from_identical 也写了。

## 8. 存活 harness 的两处修补（都留痕；只读原件未动）

1. 每臂前释放 6274-6278 上本 harness 自己遗留的 node/python 监听（freePorts + port_cleanup 逐条记录）。
   根因：spawnSync 超时只 SIGTERM 直系子进程，inspector 拉起的 HTTP 服务存活并占住 6274，臂 B 于是读
   rc=1「MCP Inspector PORT IS IN USE at http://127.0.0.1:6274」—— 这是 r283 污染面下沉一层（进程而非目录）。
   实测效果：修补前两臂读数不可比（A SIGNAL:SIGTERM、B rc=1）；修补后两臂同读 SIGNAL:SIGTERM 且 banner=true。
2. 去掉 PYTHONPYCACHEPREFIX（原值把 .pyc 重定向到写面外的 TMP/pycache）。根因：py_compile 明明落产物，
   persisted_artifacts 却恒读 0 —— 那是读数错，不是文档无产物；改回解释器默认（__pycache__ 落在源文件旁，
   仍在该臂自己的 wipe 树内，不跨臂泄漏）。实测效果：art 从 0 变每臂 1。

修补 diff 摘要（只读原件 sha12 476c890f6d1d 未变，本轮复扫 problems=0）：新增 import cp 与 NL、
INSPECTOR_PORTS + pidImage + freePorts 三个函数、三处 freePorts 调用点、texts 目录自愈 mkdir、ENV 少一行。

## 9. 判据命令与期望末行（可直接复跑）

```
cd /d "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291b2"
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B check_r291b.py
```
期望末行：[EXEC-AB-B] rows=1 commands_ok=2/3 artifacts_before=1 artifacts_after=1

负控腿 2：同目录下 ... -B check_r291b.py --negctl2（期望 PASS: teeth confirmed 且 residue_hits=0）
负控腿 1 重跑："C:/Program Files/nodejs/node.exe" harness/r291_measure.mjs sub "<写面>/texts/run_A_SKILL.md"
  然后再 ... -B check_r291b.py --sub-evidence harness/results/sub_raw.json --emit

## 10. 写面 / 只读面纪律

- 写面只在 _repro/r291b2/：三件交付物 out.json / check_r291b.py / report.md；同目录下的 harness/、texts/、
  work/ 是证据件（harness 按它自己的 TMP 相对布局必然落这三处），未写到 r291b2 之外任何位置。
- 只读面 _temp/r291b/（harness/、texts/、probe/）未写、未改名、未删除：判据件每次校验都按开工指纹
  逐件复扫 size 与 sha，本轮 [RO-DRIFT] problems=0。已实测。
- 受管根 D:/global_skills 只跑 git 只读子命令（rev-parse / cat-file / show / log / status）；未做 git 写；
  未改仓内其它文件；未跑 run_gates.py。已实测。
- 第 114/115 号门只扫 06-benchmark/*.json 的出处类字段，本件在 _temp 写面下不入册（_temp/ 是任意层级
  gitignore 模式）。因此 provenance_cmd 与 r285 同形为单条换行连接字符串、且不含任何 _temp 路径；本轮用
  该门自己的 REF_RE 加 unresolvable 规则对 out.json 模拟扫过一次：prov_string_fields=1、unresolvable=0。
  已实测。真实跑 run_gates.py 由 Lead 在入库时机自决 —— 本轮 brief 明令禁跑。

## 11. 已实测 / 未实测清单

已实测：两臂文本的 git blob 与字节、五点位基准坑对拍、三行命令真实 rc 与产物字节、codemod 改写实证、
port_cleanup 三次动作、负控两腿输出、判据件双向（绿跑 rc=0 + 篡改跑 rc=2 且点名字段）、只读面零漂移。

未实测（诚实登记，不在本行增益里主张）：
1. _temp/r291b/probe 那一轮的旧读数不作数，本轮全部读数由 r291b2 自己的 run_raw.json 现推。
2. reference 指南文件里的 4 条 literal 未跑（与 r285 只看 SKILL.md 的口径一致，见 §6 第 3 条）。
3. 生成的 MCP server 的业务质量未测；本行只测可执行性与产物面。
4. 增益「值不值」未判（那是质量面的事）；本行只交读数与判据。
