# r285 · #37 守卫**误伤面**量化（已实测）
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


> **本件只量化误伤，不改判据。** 判据本体 `D:/global_memory/05-exec/r161_bounce_back.py`、闸本体 `D:/global_memory/scripts/bounce_guard_hook.py`、规则主卷 `behavior_core.md` / `rule37_never_bounce_back_any_conversation.md` 全程**只读**（收尾复算 sha：r161 `4a15db7607f7`、hook `9c69a7ef810e`、behavior_core `e695301adba8`、rule37 主卷 `0af64e478511`，mtime 仍是 2026-10-29T09:08/09:10Z，早于本会话）。
> 数据件 = [r285_guard_false_positive.json](r285_guard_false_positive.json)（schema `guard-fp-v1`，含 129 条逐命中明细）；统计脚本 = `_temp/r285k/r285k_stats.py`（判据命令即它本身）。未跑 run_gates.py、未写 `D:/global_skills`、未改 06-benchmark 他人件、未动 git。

## 1. 读数四件套（#44⑨：面 · 分子/分母 · 切点 · 稳定时刻）
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


| 项 | 值 |
|---|---|
| **面** | **行面（消息面的代理）**：语料**逐行**喂真 `normalize()`（我→老大）+ 真解析器 `parse_rule_patterns()` 现读的 **14 条正则**（不手抄、不自写等价物）。一行命中 = 「这行若原样出现在收尾消息里，闸会 DENY」。等价性自证：每行同时跑 `mod.scan(PATS, line)` 与本件的带位置循环 ⇒ **mismatch = 0 / 36037 行** |
| **分子/分母** | **38 / 129 = 29.5%**（判红里的误伤占比 = 1 − 精确率）。绝对面 **1.05 误伤/千行**（38/36037）；闸的原始判红面 = **124 命中行 / 129 条 pattern-hit = 3.44 行/千行** |
| **切点** | 三腿 **DN1 ∨ DN2 ∨ DN3** 任一成立 ⇒ 该命中记「技术性提及」= 误伤；分母 = `hits_raw`。整体开关 `--no-denoise`（关三腿、代码保留不删）；另排除本会话自产两件防自指（见 §3 末）|
| **语料 + sha** | `06-benchmark/*.md` **全量 197 份** + `自建skill优化/memory/07-next-steps.md` = **198 份 / 36,037 行**；`corpus.sha12 = 0ef9053d497b`（口径：按文件名排序逐份拼 `name+NUL+sha256(bytes)+LF` 再取 sha256 前 12 位；JSON 内附 `corpus_per_file_sha` 198 行逐份 sha）。**未缩样**（brief 的「前 120 份」上限用不上）|
| **稳定时刻 + 漂移面** | 末次权威跑 2026-10-29T22:41Z（本地 2026-10-30 06:41 Asia/Shanghai）。**语料是活面**：`corpus_drift_watch` 记录到取数窗内 `free_tool_roster_latest.md`、`07-next-steps.md`、`全量对标报告_r285_…_2026-10-30.md`（他人件，只读）被别的会话写过 ⇒ 同一条命令在 22:35Z / 22:38Z / 22:41Z 三次得到 `128/37 @cfe670d3ea1e → 151/46 @9ccb84e82f28 → 129/38 @0ef9053d497b`。**引用本读数必须配 sha `0ef9053d497b`；07 卷行号会漂，具名例的稳定定位子是 `sentence` 原文 + 该件 sha（JSON 每条已带）** |

## 2. 逐 pattern 命中与误伤（真下标；14 条里 8 条在本语料开火）
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


| idx | 正则（截断） | raw | 判误伤 | 误伤率 |
|---|---|---|---|---|
| 0 | `老大(该\|应该\|要不要\|是否\|…)` | 4 | 4 | 100% |
| 1 | `(要不要\|是否\|能不能\|可不可以).{0,12}(老大\|提交\|跑\|做\|…)` | 33 | 7 | 21% |
| 2 | `(?<![不需没无])(?:请\|需要\|需\|得\|须\|先)…(?:确认\|拍板\|…)` | 60 | 4 | 7% |
| 3 | `等(你\|老大)` | 5 | 2 | 40% |
| 8 | `(?:若\|如果\|待\|等)…老大…(?:认为\|…\|拍板\|回复)` | 3 | 0 | 0% |
| 9 | `(?<![不需没无])(?:需\|请\|要)…老大…(?:授权\|…\|定夺)` | 3 | 2 | 67% |
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。

| 10 | `(?:要\|需\|得\|须\|该\|请)[^。！？；]{0,6}哪[一两几]?[条个项种]` | 13 | 12 | 92% |
| 12 | `(?:告\|通)?知?(老大\|你)[^。！？；]{0,8}(?:任务\|下一步\|接下来)` | 8 | 7 | **88%** |
| — | 其余 6 条（idx 4/5/6/7/11/13）本语料**零命中** | 0 | 0 | — |
| 合计 | | **129** | **38** | **29.5%** |

两个最伤的族：**idx 12**（Lead 一手例所在族：`normalize` 把「我…任务」拼成「老大…任务」）7/8 误伤；**idx 10**（「…哪个 / 哪种 / 哪几条」技术疑问代词）12/13 误伤 —— 它在陈述「该看哪个指标」这类**技术选择**，没向任何人要决策。**归因面**：129 条命中里 **25 条由 normalize 制造**（原文不含 老大/你，替换后才成立），其中 12 条判误伤 ⇒ 「我→老大」这条替换本身就是误伤发生器（JSON `normalize_manufactured`）。

## 3. 去噪规则（件内定义、可复算；实现唯一源 = 脚本 `quote_spans / dn2_check / classify`）
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


- **DN1 引用面**（6 条）：命中整段落成对引用标记内（反引号 / 「」 / 『』 / “”）⇒ 那是**引用**（正则字面量、历史违规原文、被审文本节选），本句并未向老大要决策。奇数反引号按「延伸到行尾」处理（markdown 行内码被换行截断）。
- **DN2 技术复合词**（1 条）：命中段内**最后一个**技术名词（任务 / 下一步 / 接下来）右邻构成复合词 —— 后缀表 `级 集 队列 目录 清单 池 表 树 卡 状态 参数 定义 拆分 排程 调度 名 数 标识 ID id Key key JSON json task queue file name script list`，或右邻是 `[A-Za-z0-9_-]`（标识符形态）。**DN2b 有界窗口**：紧邻判不上时在右邻 ≤6 字内找「名词+后缀」复合词 —— 一手必要性：Lead 例被文中省略号截成 `…关于任务，而「任务级 A/B」…`，只按紧邻这条腿会漏判真技术名词（实测：该腿把 07 卷 L50 从「留红」纠正为「误伤」）。
- **DN3 无受话人且无请求标记**（31 条）：命中所在**整句**用「带索引映射的原文」取 —— 必须用原文面，因为 normalize 把「我」变成「老大」会**伪造出受话人**。句中既不含第二人称受话词 `您\|你\|老大\|老板`，也不含疑问/请求标记 `吗 ？ ? 还是 或者 要不要 请 等你 要我 给我 给一句 点头 拍板 定夺 授权 确认 同意 选 挑 决定 是否 答复 回复 指示 批复 示下 定一下 说一下 说一句` ⇒ 纯陈述句。
- **保守性与切点写死**：DN3 只按句级分隔符（。！？；与 Markdown 表格竖线）切句、**不按逗号切** ⇒ 句取越长越容易含标记 ⇒ 本件的 **38 是下界**（真实误伤只多不少）。未单独剔除 ``` 代码块行：全部物理行同时进分子与分母（两侧同尺度）。
- **防自指排除**（`corpus.excluded_self_referential`）：本会话那两件产出正落在 06-benchmark 里，且为了举证会大段引用正则字面量与回抛原句 ⇒ 若计入就是「报告量自己」，读数每改一次报告就动一次。实测：排除前 22:38Z 那次冲到 151/46（含 `r285_guard_false_positive.md` 自身的引用行），排除后回到 129/38。**他人件 `全量对标报告_r285_迁库二次事故收口_2026-10-30.md` 未排除**（只读、照常计入语料）。

## 4. 具名误伤例（文件:行号 + 原句；1–6 是 normalize→「老大…任务」族）

| # | 位置（sha 前 8 位为定位子） | 命中片段 ⇐ pat | 原句（截断） | 腿 |
|---|---|---|---|---|
| 1 | `07-next-steps.md:50`（e93589fe） | 老大此前那句关于任务 ⇐ 12 | 我草稿里「…那句关于任务级 A/B 不可复算…」被抓成 bounce=老大此前那句关于任务，而「任务级 A/B」是技术名词、句中既无请求也无等待 | DN2 |
| 2 | `全量对标报告_r163_…2026-10-22.md:2050`（249d6ccc） | 老大的下一步 ⇐ 12 | 而我的下一步更危险： | DN3 |
| 3 | `全量对标报告_r163_…2026-10-22.md:3315`（249d6ccc） | 老大给自己定的下一步 ⇐ 12 | 上轮我给自己定的下一步是：「等 win-toolchain/SKILL.md 干净，就给它的 description…」 | DN3 |
| 4 | `全量对标报告_r163_…2026-10-22.md:3351`（249d6ccc） | 老大上轮那句「8 条任务 ⇐ 12 | 我上轮那句「8 条任务只 3 条召回」如果按正确分母重算，其实是 | DN3 |
| 5 | `全量对标报告_r278_…2026-10-29.md:67`（3f056fd0） | 老大不把结构提升冒充任务 ⇐ 12 | 我不把结构提升冒充任务质量（那正是 #36 假完成的形态） | DN3 |
| 6 | `07-next-steps.md:1979`（e93589fe） | 老大给自己定的下一步 ⇐ 12 | ① 上轮我给自己定的下一步是「等 win-toolchain/SKILL.md 干净就给 description 补任务级触发词 | DN3 |
| 7 | `全量对标报告_r163_…2026-10-22.md:1029`（249d6ccc） | 老大可以 ⇐ 0 | 复核发现该阻塞是**假的**：我可以自建一份干净克隆绕开他人工作副本 | DN3 |
| 8 | `全量对标报告_r163_…2026-10-22.md:2575`（249d6ccc） | 老大该 ⇐ 0 | ### 52.5 三门禁分诊：fail 不等于我该修 | DN3 |
| 9 | `全量对标报告_r266_…2026-10-29.md:62`（a1233568） | 等老大 ⇐ 3 | **既存大范围漂移**（清单含 brainstorming / cloudbase / coding-agent 等我从未触碰的件） | DN3 |
| 10 | `交付物基数对账_r261_2026-10-28.md:4` | 该命令读的是哪个 ⇐ 10 | 每个数都附「取值命令」与「该命令读的是哪个面」 | DN3 |
| 11 | `全量对标报告_r124_…2026-10-20.md:44` | 该看哪个 ⇐ 10 | 「该看哪个指标」的答案：**两个都该看，它们回答不同问题** | DN3 |
| 12 | `free_tool_roster_latest.md:9` | 能不能跑 ⇐ 1 | 工具在本机能不能跑 | DN3 |

全部 38 条都在 JSON `hits_detail`（129 条逐命中带 `file/line/pat_idx/frag/dn1/dn2/dn3/compound/sentence/normalize_manufactured/denoised`）与 `named_examples`（含逐件 sha）。**留红不误删**的反例：同族 idx 12 的 `全量对标报告_r163_…:3235`「想起某条知识的，是我或老大在任务现场会说出的那句话」三腿全不成立 ⇒ 仍判红（那句确实把老大当受话人）；`全量对标报告_r109_…:75`「须老大三选一（实减/重设硬顶/显式豁免）」留红（真在等老大选）。

## 5. 反面对照（缺此节结论无效）

1. **r161 POSITIVE 全量 22 条**（brief 要 ≥8，取**全集不挑选**）过同一把尺 + 同一条去噪 ⇒ **22/22 仍判红，missing=[]**。判红语义取严格式：真回抛上**任一**降噪腿成立即算削弱（`still_red = red and not any(leg)`）。
2. **真闸腿**（跑 `bounce_guard_hook.py --check-file`，即生产 DENY 本体而不是我的尺）：pat12 误伤面抽 6 条 ⇒ **6/6 rc=1 真被 DENY**（误伤是活的，不是纸上推演）；POSITIVE 抽 8 条 ⇒ **8/8 DENY**；r161 NEGATIVE 9 条 ⇒ **9/9 PASS**。
3. **开关腿（负控）**：`--no-denoise` 关三腿 ⇒ **分母 36037 不变、hits_raw=129 不变、判红回到 129 = hits_raw、denoised=0**，`sha12/lines_total` 与正控逐字相同 ⇒ 降噪是唯一变量。断言由脚本自身在正控跑里起子进程复算（`switch_leg`，实测 rc=0 / PASS，子行末行 `[GUARD:FP] raw=129 denoised=0 pos_controls=22/22 red`）。
4. **官方 NEGATIVE 腿**：`mod.NEGATIVE` 9 条经同一尺 **raw_red = 0** ⇒ r161 注释「r183 实测零误伤」在夹具面复现成立；本件的 38 条是**语料面**新增读数，不与该声明冲突（夹具窄、语料宽）。

## 6. 结论（已实测；含一条部分实测）
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


- 闸在这份技术文档语料上的判红里 **29.5%（38/129）是技术性提及**（下界）；绝对密度 **1.05/千行**；124 命中行里 **36 行的命中可全部降噪**、88 行至少一条须留红。
- 高危两族 = **idx 12（88%，normalize 造的「老大…任务」）** 与 **idx 10（92%，“…哪个/哪种”技术疑问代词）**；`idx 2`（60 条仅 4 误伤，7%）判得准、`idx 8`（3 条零误伤）判得准，不必动。
- 反面腿齐 ⇒ **降噪不削弱闸**（真回抛 22/22 + 真闸 DENY 面全绿）。本件**只出读数，不提改判据动作**；最小改法仍归已登记待办（07 卷 R285-3），不在本件写面。
- **部分实测 / 未取证（如实标）**：真实**消息出口面**的误伤率未测 —— 本件测的是行面代理（闸只吃 `send_message/ask_user_question` 的文本字段，而语料不是消息面）。要把行面率当消息面率引用，得另取一次消息面证据（对 `~/.dsh/tmp/bounce-guard.log` 的 DENY/PASS 逐条判读，或把历史收尾消息逐条喂 `bounce_guard_hook.py --check-file`）。**语料漂移面已实测但不可冻结**：多会话同写 07 卷与 06-benchmark，本件只能钉 sha，不能保证下一条命令复现同一分子分母（三次跑的三个数已如实列在 §1）。

## 7. 判据命令与期望末行

```
C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_temp/r285k/r285k_stats.py"
```
期望末行：`[GUARD:FP] raw=129 denoised=38 pos_controls=22/22 red`　（语料未被他会话改写时；改写后末行仍成立，只是 raw/denoised 随 sha 移动 ⇒ 以 `corpus.sha12=0ef9053d497b` 为准）
负控 = 同一条命令加 `--no-denoise --out <_temp/r285k/xxx.json>` ⇒ 期望末行 `[GUARD:FP] raw=129 denoised=0 pos_controls=22/22 red`（`lines_total / hits_raw / sha12` 须与该次正控逐字相同 ⇒ 证明降噪是唯一变量）。
> 取值：本节的每个数都由判据命令现取 —— `python -B _temp/r285k/r285k_stats.py`（读 `hits_detail`、
> `corpus.sha12`、`positive_controls`）；开关腿 `--no-denoise --out <temp.json>`；真闸腿见件内
> `gate_face_rows`。逐条明细与逐文件 sha 在 `06-benchmark/r285_guard_false_positive.json`。


实测时刻 2026-10-29T22:41Z（本地 2026-10-30 06:41 Asia/Shanghai）· 语料 sha12 `0ef9053d497b` · 判据正则 14 条（`parse_rule_patterns()` 现读，非手抄）。
