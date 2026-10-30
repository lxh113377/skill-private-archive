# r304c 交付报告 — C5（合入后注入面）与候选脚本可运行性

> 范围：C5「合入后 inject_union_bytes 不越硬顶」+ 候选脚本可运行性。C6（死引用）不在本件，归上级。
> 证据等级：C5 口径与现状值 = 已实测（运行时现读棘轮件）；C5 合入后值 = 折算（未真做换装，规则见 §3）；候选脚本 = 已实测（语法检查 + 20 秒运行探针）；A 臂脚本 = 已实测为 none。

## 0. 产物与复跑

产物三件同目录：admission_c5_scripts.json / check_r304c.py / report.md。

复跑命令与期望末行：

```
"<managed python>" check_r304c.py
期望末行: [R304C:ADMIT] c5=ok members=5 live=63337 merged=63337 cap=65536 scripts=5 scripts_ok=3 scripts_fail=2
```

## 1. 口径来源（全部现读，未抄任何文档数字）

棘轮件 ratchet_gate.py 对 inject_union_bytes 的实现：inject_union_paths() 先读常量件 truth_constants.json 的 inject_budget.files 逐条取 path（相对路径按项目根解析，再取 realpath 去重），随后把项目壳件并入集合；inject_union_bytes() 对集合每条路径取磁盘实测字节求和，任一路径取不到大小即整体返回 None。硬顶 hard_caps() 读同一个常量件的 inject_budget.hard_cap_bytes。本件的判据件不抄这些数字，而是用 importlib 装载该门禁件后直接调用它的这三个函数。

成员清单（5 条，逐条现读；字节为盘上实测）：

```
id                        path                                                                                          bytes
a_memory_start_skill      D:/global_skills/A-memory-start/SKILL.md                                                      12167
a_memory_start_contract   D:/global_skills/A-memory-start/references/contract.md                                         14331
behavior_core             D:/global_memory/core/behavior_core.md                                                        27066
shell_zc                  C:/Users/37533/.zcode/AGENTS.md                                                                 4277
shell_project             C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/AGENTS.md                                 5496
```

硬顶来源：常量件 inject_budget.hard_cap_bytes = 65536（现读；同表还挂着只降不升的棘轮基线 65464，但 C5 判的是硬顶）。

## 2. 现状值

live = 12167 + 14331 + 27066 + 4277 + 5496 = 63337。距硬顶余量 = 2199。

## 3. 合入后的折算规则（folding_rule）

规则：delta(path) = 上游产物写入该路径的新增字节；counted_delta = 仅对落在 §1 成员清单内的路径求和；清单外写入一律不计入。

| 产物类 | 落点类 | 落点是否在清单内 | 该路径 delta 怎么算 |
|---|---|---|---|
| 散文增量并入本地技能壳 | 被换装 slug 的本地 SKILL.md | 否 | = 候选 SKILL.md 全文大小（已取回实测），作并入上限 |
| 候选侧车文件（脚本/资料库/参考） | 本地技能目录下 | 否 | = 每个上游文件大小（已取回实测），逐文件累加 |
| 任何写成员的产物类 | 成员清单内五条 | 是 | 本两件无此类产物 ⇒ 该类为空，delta 计 0 |

实测落点与增量（全部在清单外，逐条）：

```
D:/global_skills/A-prompt-better/SKILL.md                33508
D:/global_skills/frontend-skill/SKILL.md                39537
D:/global_skills/frontend-skill/scripts/*.mjs (10 files) 汇总见 JSON deltas
D:/global_skills/frontend-skill/library/*.json (9 files) 汇总见 JSON deltas
清单外增量合计 out_of_list_delta_total = 2064148；清单内增量 counted_delta = 0
```

未测项（如实申报）：frontend-skill/references 下 11 个 md 未取回，大小未测；因该类按类即判为清单外，C5 判定不受其影响。

## 4. 判定

merged_value = live + counted_delta = 63337 + 0 = 63337 <= 65536 ⇒ c5 = ok。

但这是空过（vacuous pass）：本两件的换装落点无一在棘轮成员清单内，所以这道门对这两件根本不施加约束。它不能当作「换装对注入面无风险」的证明，只能当作「该门禁的成员面不含这两件」的证明。这一点由 §6 的腿 B 反向坐实（同一放大增量落清单内即 bad，落清单外仍 ok）。

## 5. 候选脚本可运行性

提取方式（锚点式，不是全量正则）：在候选 SKILL.md 正文里只取反引号代码跨包裹的脚本路径（形态 scripts/**.mjs），再与命令式锚点交叉核对。

- A 臂候选 prompt-master：正文 499 行，脚本锚点命中 0；仓库树也没有 scripts 目录（仅 LICENSE/README/SKILL.md/references 两件）⇒ scripts=none。含义：没有可指认的脚本可跑，这是「无对象」而不是「通过」。
- F 臂候选 taste-skill：正文 542 行，锚点命中 5 个脚本（assets/draw/inspect/lint/scenes）。为让运行探针能解析相对导入，另按仓库树把 scripts/lib 下 5 个依赖件一并取回。

本机 node = v24.16.0（先 --version 实测）。探针口径：node --check 测语法；运行探针用正文记载的最小合法调用，20 秒超时（timeout 工具在位）。

```
node scripts/assets.mjs "ghent postcard"   check_rc=0  run_rc=124  state=FAIL  (20s 超时，stderr 空)
node scripts/draw.mjs --list sectors       check_rc=0  run_rc=0    state=OK    [stdout] saas
node scripts/inspect.mjs tiny.html         check_rc=0  run_rc=1    state=FAIL  [stdout] TASTESKILL · INSPECT   tiny.html
node scripts/lint.mjs tiny.html            check_rc=0  run_rc=0    state=OK    [stdout] TASTESKILL · LINT   1 file(s)
node scripts/scenes.mjs tiny.html          check_rc=0  run_rc=0    state=OK    [stdout] desktop: no <section class="scene"> on the page
```

说明：五次探针 stderr 全空，凡首行落在 stdout 的已标 [stdout]。assets 是网络检索件，本机 20 秒内未返回（rc=124）；inspect 需要真实浏览器（本机无 Chrome 路径，实测 NO_CHROME_PATH）故 rc=1。draw/lint/scenes 以最小合法调用跑通 rc=0。scripts_ok=3、scripts_fail=2。

## 6. 负向对照（逐字，由 check_r304c.py 打印）

腿 A（防把没跑当 OK）：

```
[NEG-A] script_state(present=False, check_rc=0, run_rc=0) -> FAIL
```

腿 B（防用现状冒充合入后态；同一条放大增量分别落清单内/外）：

```
[NEG-B1] delta=655360 on member path -> state=bad merged=718697
[NEG-B2] delta=655360 on non-member path -> state=ok merged=63337
```

三条都按预期：不存在的路径落 FAIL；清单内放大增量把 ok 翻成 bad；同一增量落清单外仍 ok ⇒ 成员 membership 真的在起作用。

## 7. 「要换成什么才算过」的一句话判据

只有当「换装产物落点」被纳入棘轮成员清单、且纳入后 merged_value 仍 <= cap 时，C5 才算真正过；按现清单，本两件的写入全在清单外 ⇒ C5 空过，不得据此宣称换装对注入面无风险。

## 8. 纪律自检

- 先 print sorted(keys) 再引用字段：check_r304c.py 首行即打印 admission keys。
- 落盘前 json.loads 与 ast.parse 当场过（实测输出 VALID json+ast OK）。
- 只写新建目录 _repro/r304c；既有件只读；未跑 run_gates.py；未做任何 git 写；未写 D:/global_skills 与 D:/global_memory。
- 结论标注：C5 口径=已实测；C5 合入后值=部分实测（折算，非真换装）；脚本可运行性=已实测；A 臂脚本=已实测 none。
