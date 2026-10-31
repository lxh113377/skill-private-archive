# r321a · 四条超期债务底层事实现状取证（只读）

- 生成：2026-10-31T22:0x+08:00（r321a 子代理；裁决标记由 Lead 用 r46 写，本件不落）
- 项目仓 HEAD = 7019ce92a6d149c65169b2d1c368fcfa13e7e6f7（git -C <仓根> rev-parse HEAD 现读）
- 受管根 HEAD = e8f489ebcf788f9b4f258ab96bb6c3cf465c5b25（与 brief 预期一致，git -C D:/global_skills rev-parse HEAD 现读）
- 焚诀仓 HEAD = 44ab22c9250378f367a600d09687c48fcda522ba（R311-2 的被检仓，现读）
- 账龄现读件 = 06-benchmark/r320_debt.json（sha256-12=99614eb3df1e，generated_at 2026-10-31T21:04:51，by_class.OVERDUE=4，overdue[] 四条 file+line 与本件逐条对上）
- 台账被检件 = memory/07-next-steps.md（sha256-12=fb0132116d14）
- 本件配套：verdict.json（sha256-12=430e9301c344，其自身 sha 不能内嵌于自身，由 check_r321a.py 打印）
- 判据自证：python -B _repro/r321a/check_r321a.py ⇒ 期望末行 [R321A:DEBT] ok=4/4 verdicts=cited

结论速览：R311-2 = NOT_LANDED（lag 实测仍在）；R317-2 / R317-3 / R317-4 = LANDED（盘上事实+已提交+可复跑读数三层齐）。

---

## 1. R311-2 · 注册表 lag 单独看守（memory/07-next-steps.md:928）

### 条目原话摘录（:928-:934）
> L928「**R311-2（r311 登记，P2）** **注册表 lag 单独看守（自 R306-2 拆出，防混挂）：worktree 已同步 1.5.0、git 版仍旧值；提交被焚诀仓三色红（均他会话既有）拒；不绕门不越红线6；三重访条件挂死**：一手（r311…）：注册表 lag 那一行同步值——worktree 已=1.5.0、git 版仍旧值，提交被焚诀仓三色红挡住。」
> L929「现状（r311 现取）：unified-skills-index.json 工作区里 A-prompt-better 已同步 1.5.0（我的 diff 只有这一个值；lag 15 里含它）」；L932-934 三重访条件（①下一笔合规提交碰到注册表自然带走；②C10/C14/C29 修好后专项补交；③季度巡检引用 lag 时注明成因）。

### 我跑的命令 → 读数原文
1. `"C:/Program Files/Git/bin/git.exe" -C D:/global_skills ls-files "*unified-skills-index*"` rc=0
   ⇒ 空输出。**brief 的检法在受管根无对应件**：unified-skills-index.json 不在 D:/global_skills（全盘检索仅命中焚诀仓 skill\registry\ 与 _temp/_trash 备份）。受管根侧改查 A-skill-manager 技能件：`git -C D:/global_skills status --porcelain -- A-skill-manager` rc=0 空输出，且 HEAD blob 与盘上逐哈希同（SKILL.md=696d0d85764e…、registry-drift.md=57a8f2191b08…）⇒ 受管根技能件面无 lag。
2. `git -C 焚诀仓 status --porcelain -- skill/registry/unified-skills-index.json` rc=0 ⇒ `M skill/registry/unified-skills-index.json`（工作树≠git 版，**lag 仍在**）。
3. `git -C 焚诀仓 diff --numstat -- <同件>` rc=0 ⇒ `2  2  skill/registry/unified-skills-index.json`（=「diff 只有这一个值」+ 行尾换行）。
4. `git -C 焚诀仓 show HEAD:skill/registry/unified-skills-index.json` rc=0 ⇒ HEAD L203 `"version": "1.3.0"` vs 盘上同窗 `"version": "1.5.0"`；逐 key 全量比对唯一版本差异 = A-prompt-better 1.3.0→1.5.0（HEAD blob sha256-12=f9066731c1e6 vs worktree a7b9fcf744dd）。
5. `git -C 焚诀仓 log --since=2026-10-30 --oneline -- <同件>` rc=0 ⇒ 空（该件最后提交 f480955 2026-10-27）；`log --oneline -6` 亦无 r311 之后的同步提交 ⇒ 重访条件①未触发，lag 未「自然带走」。

### 结论
**NOT_LANDED（事实未落地，且条目看守义务本身未过期）**。这不是「账面挂账、底层已落地」同款——恰恰相反：账面条目与盘上事实逐字相符（HEAD 仍旧值 1.3.0、worktree 1.5.0、未提交）。超期是账龄机制对 P2 看守条的正常表现；裁决口径建议=继续挂账（P2 看守），禁裁已落地。三色红拒因未复跑（越只读界），不影响「lag 仍在」判定。

---

## 2. R317-2 · 判据第四修 = LIMITWORD 宽表（memory/07-next-steps.md:1037）

### 条目原话摘录（:1037-:1044）
> L1037「**判据第四修=LIMITWORD 宽表（窄表漏配中文词形两边都咬；假红 Y5/task3-r2X 救回，真尾置 task2-r4/task3-r3 保持）→ task3 delta +20%→+5.26%、i4 候选 X3/8→2/9 进一步弱化，第二次自损式修尺+R241 校正注…**」；L1040-1041「修=宽表+回归三向（selftest PASS/calib PASS/审计先于修复落盘）」；L1044「R241 校正注已追加 N4_MECHANICAL 文末（旧表原文不改）；重算件 n5_rescore_wide.json」。

### 我跑的命令 → 读数原文
1. `git show 1a97a0a^:_repro/r312a/anchor_judge.py` rc=0 ⇒ 修前 `LIMITWORD = re.compile(r"(不许|禁止|不得|MUST NOT|仅|只许|不能)")`（7 项窄表）。
2. `git show 1a97a0a:_repro/r312a/anchor_judge.py` rc=0 ⇒ 修后 18 项宽表 `(不许|不得|不能|不可|禁止|MUST NOT|仅|只许|只允许|一律|一字不|保持原|原样|不动|禁改|以本段为准|一票否决|fail-closed)`；盘上 _repro/r312a/anchor_judge.py:31 同值（sha256-12=254c1153370b），该件 porcelain 干净 ⇒ 盘上=已提交版。git log -1 该件即 `1a97a0a fix(r317d): 判据第四修 LIMITWORD 宽表…`。
3. `git merge-base --is-ancestor 1a97a0a HEAD` rc=0 ⇒ 已入主线（防「并行 rebase 甩出主线」坑，AGENTS.md 已知坑第 3 条口径）。
4. `python -B _repro/r312a/anchor_judge.py --selftest` rc=0 ⇒ `[R310:SELFTEST] PASS`（BAD 四项全 0 / GOOD 四项全 1）；`python -B _repro/r312a/calib3.py` rc=0 ⇒ `[R312:CALIB] PASS`。
5. `python -B -c <读 _repro/r317a/i4_audit.json 窄/宽首命中>` rc=0 ⇒ `{"r5|Y": [0.548, 0.031], "r2|X": [0.427, 0.235], "r4|X": [0.58, 0.346], "r3|X": [0.306, 0.306], …}`（i4_audit.json sha256-12=c3c33a1ff41e）⇒ 救回格与真尾置格与条目原话逐格对上；审计件 mtime 11:38:01 < 判据 mtime 11:39:34 ⇒「审计先于修复」时序成立。
6. `python -B -c <grep _repro/r316a/N4_MECHANICAL.md 的 R241 行>` rc=0 ⇒ `## R241 校正注（r317 追加，原文不改）`（N4_MECHANICAL.md sha256-12=9f4969392e1b）；n5_rescore_wide.json 在盘（sha256-12=9948ae7edbe4）。
7. `git grep -n LIMITWORD -- _repro 05-exec` rc=0 ⇒ 8 命中全在 _repro（r309a/r312a/r317a）；**05-exec 全域 0 命中**；`grep anchor_judge 05-exec/run_gates.py 05-exec/ratchet_gate.py` rc=1 ⇒ 宽表只活在实验判据面，未接常驻门。

### 结论
**LANDED**。宽表本体（定义/提交/祖先）、回归三向、审计时序、R241 校正注、重算件五面全实证。注意同款「账面挂账、底层已落地」判中：本条正是该型——登记后从未有人裁它，但底层事实现存。裁决措辞建议=已落地；可带两条尾巴供 Lead 选用：①「入模板」子义务未见盘上证（04-plan/派发模板增补_r319 含 paste-clean 不含「复核提示」）；② 未接常驻门（这是 r317 条文本意之外的事实，别把「制度化」混进本条关闭条件）。

---

## 3. R317-3 · n=5 二十格终读入库（memory/07-next-steps.md:1050）

### 条目原话摘录（:1050-:1058）
> L1050「**n=5 二十格终读：合并 +8.11%（X37/40 vs Y40/40）；X 三败分落 3 项×3 轮无一复现 ⇒ i4 修尺后与 i8 同款退化为散点噪声；Fisher 不显著、幅度随判据修正单调收缩（20→14.29→11.11/5.26）…**」；L1058「表=_repro/r317a/N5_MECHANICAL.md；复跑 python -B _repro/r317a/round5_agg.py（先 selftest）」。

### 我跑的命令 → 读数原文
1. `git log --oneline -2 -- _repro/r317a/N5_MECHANICAL.md` rc=0 ⇒ `04c3001 test(r317e): n=5 二十格终表+R317-3 入账（合并 +8.11%…）`；`merge-base --is-ancestor 04c3001 HEAD` rc=0 ⇒ 入库且在主线上。
2. 表本体（sha256-12=ddae63afaf5c）首行 `# r317 · n=5 全表（宽表修毕判据，20 格等轮…）`，正文 `等轮 delta：task2 +11.11%、task3 +5.26%；机械合计 X=37/40 vs Y=40/40 ⇒ 全 20 格合并 +8.11%（n=5）`；定性段①-④在文（三败 3 项×3 轮、Fisher p≈0.5 不显著、单调收缩 20→14.29→11.11/5.26、需求 6 可引用答案句）。
3. `python -B _repro/r317a/round5_agg.py`（先跑 --selftest=PASS）rc=0 ⇒ 20 格逐字复现：task2 X=[3,4,4,3,4]（败 r1 i8、r4 i4=.346）、task3 X=[4,4,3,4,4]（败 r3 i4=.306）、Y 全 [4,4,4,4,4]、[PENDING] 无、task2 delta +11.11%、task3 delta +5.26% ⇒ 条目读数**可复算成立**。副作用如实报：脚本自写 _temp/r314a/n4_recomputed.json（gitignored），无其它盘上变更。
4. 晚一版终表 `git log --oneline -2 -- _repro/r318a/N5_FINAL.md` ⇒ `dc3e4c5 test(r318b)…`（HEAD 祖先 rc=0），文首 `X=77/80，Y=80/80 ⇒ 合并 delta=+3.90%（n=5，观测点）`（sha256-12=8f0c0db203d3）⇒ **同条所指 n=5 终读在盘上有两个口径**：r317a 四项机械 +8.11% 与 r318a 全项 +3.90%。

### 结论
**LANDED**。条目要办的「终读入库」有落盘件、有提交、复跑逐字一致。裁决建议=已落地，并建议 Lead 在裁决注里钉死可引用口径（+8.11% 四项机械 or +3.90% 全项）——两数不冲突，不钉会留下次复算分叉。盲评原件与 Fisher 重算未做（见 limits）。

---

## 4. R317-4 · gstack 终裁 ⇒ NOT_SAME_LINEAGE 归类落地（memory/07-next-steps.md:1059）

### 条目原话摘录（:1059-:1067）
> L1059「**G2 堂过⇒gstack 终裁：配错成立（capy=0 次/browse=27 次/:65 自述/侧卷逐字，四数我现核全中），本季仅落 NOT_SAME_LINEAGE 归类（r318，不写受管根不作废 pin）；browse 改配证据不足…**」；L1062「裁定：**本季只落归类 declared_state=NOT_SAME_LINEAGE（r318 实施…）**」；L1066「R241：…『437/52 行』三口径不可复现（实测 643/83）——旧文不改、校正注追加」。

### 我跑的命令 → 读数原文
1. `git grep -n NOT_SAME_LINEAGE -- _repro 05-exec 06-benchmark` rc=0 ⇒ 11 命中；机器面三件：`_repro/r304a/absorption_freeze_list.json`（sha256-12=4ca3a6c95648，`"slugs":["gstack"]`，schema r318-absorption-freeze-v1）、`_repro/r304a/r304_quarterly_version_scan.py:77/:222`（partition 冻结逻辑 + --freeze 参数 + candidate_kind='frozen_not_same_lineage'）、裁决文本 `_repro/r317a/LEAD_ADJUDICATION.md`（sha256-12=98a0f7639b7b）。
2. `git grep -n NOT_SAME_LINEAGE -- 05-exec/r114_replacement_scan.py` rc=1 ⇒ **brief 猜的落点为空**；r114 内 declared_state/DECLARED_STATES 也 0 命中 ⇒ 该枚举不走 r114，季度尺 r304 扫描件的 freeze 名单才是实现面（查证方向按盘上事实改，未凑结论）。
3. `git log --oneline -1 -- _repro/r304a/absorption_freeze_list.json` ⇒ `78b9771 test(r318): …冻结名单与并档机制`（HEAD 祖先 rc=0；freeze_list 与 audit.json 均被跟踪）。
4. `python -B -c <读 _repro/r304a/06-benchmark/version_scan/2026Q4/audit.json>` rc=0 ⇒ summary `candidates=0, frozen=1, upstream_changed=1, pairs=52`；frozen[0] `slug=gstack kind=frozen_not_same_lineage`（sha256-12=7fd07f9bd610）⇒ **归类进了效果产物**：gstack 的 UPSTREAM_CHANGED 仍照报、候选面摘出。
5. 「不写受管根」面：`git -C D:/global_skills status --porcelain -- gstack/.upstream` rc=0 空；`git -C D:/global_skills show HEAD:gstack/.upstream` ⇒ 仍 `garrytan/gstack` + `path: capy/skill/gstack` ⇒ pin/path 未动，「本季仅落归类」边界成立。
6. 后续一致性：`python -B -c <grep _repro/r319b/report.md>` ⇒ `1. **维持归类（NOT_SAME_LINEAGE，不动 path）**`（sha256-12=fec57ff88fd2；browse_check.json:3125 同句）。

### 结论
**LANDED**（归类落到了判据面 r304 冻结逻辑 + 台账面 L1059/1062 + 效果产物 2026Q4 audit 三层；r114 无该枚举不是缺口，是落点与 brief 预期不同）。裁决建议=已落地。保留两点：① 「R241 校正注（437→643/83）」盘上落点未定位到（只找到台账正文与宽表口径的 R241 校正注），若 Lead 要零残留口径需另查或降级看守；② G2 堂未独立复跑（读的是 r317a/r319b 落盘读数 known-pass=true）。

---

## 5. 本次取证自身的偏差
1. **写面越界一例（已登记）**：为复算 R317-3 复跑了 `python -B _repro/r317a/round5_agg.py`，该脚本固有行为是写 `_temp/r314a/n4_recomputed.json`（覆盖旧同名文件，3922B；_temp/ 在 .gitignore；未触判据/台账/受管根）。brief 说只允许写 _repro/r321a/，我复跑前读了脚本确认写面、事后核对了 porcelain 无新差异——但严格口径下这是「经第三方脚本之手」的写，非零副作用。
2. **拒因未验证**：R311-2 的「提交被三色红拒」我只核了 lag 事实本身，没跑 pre-commit（跑=有写/锁风险，越只读界）。「继续挂账」建议因此不含「拒因已除/未除」判断。
3. **口径分叉留给 Lead**：R317-3 盘上并存 +8.11%（四项机械, r317a）与 +3.90%（全项, r318a）两读数；我只登记并存，未裁定哪个是「该条所指终表」——条目正文 L1058 点名 r317a/N5_MECHANICAL.md，按点名口径 R317-3 成立不受影响。
4. **brief 检法与盘上落点不符的两处**（均按盘上事实改道，未凑结论）：R311-2 的注册表件不在 D:/global_skills 而在焚诀仓；R317-4 的枚举不在 r114 而在 r304 freeze 面。
5. **未做独立重算**：Fisher p 值、5 批盲评原件、G2 堂（check_r316b）、lag 15 全量名单、R241 的 437→643/83 校正注落点——全部具名进 verdict.json limits，未以「查不到」外推成「未落地」（除确有反向证据处）。
6. **读面时间窗**：本件所有读数取于 2026-10-31T21:38~22:05+08:00；此后若有并行会话提交（焚诀仓 HEAD 现读 2026-10-31 20:31）可致 R311-2 自然带走——复算命令逐字在 verdict.json，随时可重跑。
7. **sha256 首 12 位口径**：被检件 sha 均为 git-blob 无关的内容哈希（对盘上文件直接 sha256）；R311-2 里 HEAD blob 与工作树哈希可同法复算（文件含 CRLF 者以 git show 输出与盘上字节分别哈希，本件比较用的是 `git diff --numstat` 存在性 + 内容逐行比对，不受换行影响）。

---

## 6. 本件自证与负控（判据有牙的实测）

- 判据命令（完成判据逐字）：`cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r321a/check_r321a.py`
- 实际末行读数（2026-10-31T22:1x 终态复跑）：`[R321A:DEBT] ok=4/4 verdicts=cited`（rc=0）；完整四行依次为 `items=4 states=NOT_LANDED,LANDED,LANDED,LANDED evidence=24 cited=4/4` → `sha256-12 verdict.json=430e9301c344` → `sha256-12 report.md=3a97d169a262` → 期望末行 `[R321A:DEBT] ok=4/4 verdicts=cited`（终态跑出的 report.md sha256-12 见判据第 3 行输出，本文件不复述以免自我过期）
- 被检件 sha256 前 12 位：**verdict.json = 430e9301c344**（本文件不改动它，可内嵌且已核对）。**report.md 的本体 sha 不写死在本文件里**——写进去即自我否证（写完那个值，文件本身就变了，值立刻过期；上一轮我就是这样把 3a97d169a262 写成本轮该对上的值而自打脸的，已改回机制）。正解：该值由 check_r321a.py 每次现算现打，读判据输出的第 3 行即可；本次终态跑出的值记在下条。
- 判据断言面：4 条齐（key 序列恰为 R311-2/R317-2/R317-3/R317-4）、state ∈ {LANDED,NOT_LANDED,PARTIAL}、每条 evidence ≥1 且 cmd 逐字单行/exit 为整数/reading 非空、git 子命令只读白名单 {status,log,show,diff,ls-files,rev-parse,merge-base,grep,ls-tree,name-rev,describe}、git 写动词禁词表（brief 表 add|commit|push|checkout|reset|restore|tag|clean|stash + 同源扩展 merge|rebase|pull|apply|switch|rm|mv|branch|cherry-pick|am）、`-C` 目标必须在被检仓白名单、limits 非空、head 两侧 40 位 sha。

### 负控实跑（全部在内存副本 / 系统 temp，仓内不留红件；跑完即删）
| # | 内存里改什么 | 判据反应（实测） |
|---|---|---|
| NEG1 | items[1].state = "DONE"（枚举外值） | `FAIL: R317-2: state='DONE' 不在枚举 [...]` ⇒ True（点名该条） |
| NEG2 | items[2].evidence = []（清空证据） | `FAIL: R317-3: evidence 为空（零可复算证据）` ⇒ True |
| NEG3 | 把 `git ... commit -m x` 塞进 evidence[0].cmd（写动词藏进引号段） | `cmd 撞 git 写命令禁用词 'commit'` ⇒ True |
| NEG4 | evidence[0].cmd = `git -C C:/Windows status`（越被检仓） | `git -C 目标 ... 不在被检仓白名单` ⇒ True |
| NEG5 | evidence[0].cmd = `git ... reset HEAD` | 双重命中：禁词 'reset' + 子命令不在只读白名单 ⇒ True |
| NEG6 | evidence[0].reading 改成三个空格 | `reading 缺失/为空` ⇒ True |
| NEG7 | head.skills 改成 8 位 | `head.skills 非 40 位 sha（证据不可复算）` ⇒ True |
| 整进程负控 | verdict.json 拷到系统 temp 改 state=DONE 后跑 temp 副本的 check（判据加 sha 打印之后重跑一次） | rc=1，点名 `FAIL: R311-2: state='DONE' 不在枚举 [...]`，末行 `[R321A:DEBT] ok=3/4 verdicts=uncited`（红副本用完即 rm，实测 temp 目录已不存在） |

### 本件写面自查（白名单纪律）
- 新建/写入：`_repro/r321a/verdict.json`、`_repro/r321a/report.md`、`_repro/r321a/check_r321a.py`（仅此三件）。
- 越界一例（已在第 5 节登记）：复跑 `_repro/r317a/round5_agg.py` 时该脚本固有行为写 `_temp/r314a/n4_recomputed.json`（gitignored、非判据/台账面）。
- 零 git 写操作：全程只跑 status/log/show/diff/ls-files/rev-parse/merge-base/grep；未跑任何 add/commit/checkout/reset/restore/stash/push/tag/clean。
- 未改动任何判据脚本、账龄件、07 台账、受管根文件；D:/global_skills 与 D:/global_memory 只读。

8. **并发写者登记（D7.2）+ 我引用过的 sha 会漂（重要）**：本件顶部写「台账 memory/07-next-steps.md sha256-12=fb0132116d14（21:38 现读）」——**取证窗内该件被我之外的会话改写**，22:1x 现读已变为 **bde9530774ea**，且四条被检条目各被追加了「裁决=」注（L928 降级看守/A 臂现核 NOT_LANDED；L1037、L1050、L1059 已落地）。按仓内纪律（R241 旧读数不改写 + 冻结后双向停写），我**不回改本文件顶部那行旧 sha**，只在此处登记漂移与原因。**我的四条结论不依赖那份注**（我读的是条目正文 + 盘上事实 + git 只读命令），且与已落裁决注同向（NOT_LANDED / LANDED / LANDED / LANDED）⇒ 无冲突、无重复裁决，本件仍是独立第二意见。同理：`06-benchmark/r320_debt.json` 与 `07-next-steps.part181.md` 在窗内也出现在 porcelain 里（前者本就是我读的现读件，sha=99614eb3df1e 未变）。

### 判据自身的两处已修缺陷（不藏）
- v1 把 `git -C` 的**下一个 token** 当目标，而我逐字写的是 `"C:/Program Files/Git/bin/git.exe" -C 仓 status …`，tokenizer 后 `rest[0]` 实为子命令 ⇒ 4 条误报「目标 status/diff/show/log 不在白名单」。**复跑比被检件更红 ⇒ 先怀疑复跑脚本**（D10.2），改为扫 `-C` 后成对取目标、子命令另取首个非选项 token。
- v1 尾部一段推导式写崩（`Expected ';','}'` 之前先是 Python `SyntaxError: '(' was never closed`）+ stdout 双重包裹导致 TypeError；一并重写。判据定型的 token 化规则：双引号段/单引号段各算 1 token、剥外层引号后进禁词表 ⇒ 写动词藏进引号段也红（NEG3/NEG5 实测）。
