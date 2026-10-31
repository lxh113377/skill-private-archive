# r306b B1 · A-prompt-better 换装：准入规格 + 回滚演练（只演不落地）

> 交付 = 准入规格一件 + 演练证据两件。我**没有**执行换装、**没有**写受管根、**没有** git 写、**没有**跑门禁总控。
> 下文所有「通过」= 规格与判据通过，**不**指落地完成。

## 0. 必须先报的一条（它改变了父级的下一步）

**换装在本轮工作期间被外部连续落地两次。** 实测时间线（同一份受管根，我三次取读数）：

| 我取证时 | HEAD | 盘上件版本 | 字节 |
|---|---|---|---|
| 约 14:13 | 942002f0 | 1.3.0 | 28761 |
| 约 14:24 | 17cc0c81 | 1.4.0 | 30606 |
| 约 14:41 | f39eb3c0 | 1.5.0 | 35594 |

两笔落地提交正文都自述为 rule_editor 换装动作（第一笔「增量并入 r306 … 1.3.0->1.4.0」，第二笔「换装升级 r306b：1.4.0 转述升级为 1.5.0 逐字钉定」）。
实测盘上态 == HEAD 版、工作区对该技能干净 ⇒ 不是我写的，也不是脏树残留。

⇒ **规格按真实两笔链建立**：base_ref = 第一笔落地的父提交（17cc0c81~1 = 942002f0…），链上两笔（5 + 4 = 9 处 hunk）。
⇒ **中途那次判据全线报红是真信号，不是假象**：当时规格只挂第一笔，重放腿/版本腿/镜像腿同时报红（漏打 + 版本漂移 + 镜像滞后）——
   这正是不变式该有的行为：**有人改了件而补丁链没挂上，必须红**。
⇒ 父级若还要再改这件：新落地的补丁必须**追加为链上第三笔**并同步版本期望；只改件不挂链 = 本判据立刻判红。

## 1. 写面自查

| 项 | 状态 | 实测依据 |
|---|---|---|
| 新建 | 只新建本轮指定目录（含其下补丁子目录与演练子目录） | 清单见文末附录 |
| 既有文件改动 | 0 件 | 四件参照件工作区状态全 clean，blob 前缀 1469d89a1a / fcd6a9a782 / 3c261f7134 / 3cf0a5f24f 未变 |
| 受管根 | 只读 | 演练对象是副本；全程只有 show / cat-file / hash-object / 读盘 |
| 门禁总控 | 未运行 | 只读了那份通用重放工具的 370 行实现 |
| 负控副本 | 用完即删，现已不存在 | 演练子目录只剩副本、改前快照、假回滚产物三件 |
| 本目录跟踪态 | 未被跟踪（命中仓忽略规则第 16 行的临时目录规则） | check-ignore 实测 |

## 2. 副本构造方式

做法：把**落地前基线版**文本（按基线 ref 现取的字节）写进本目录演练子目录下的同名副本，同目录再留一份改前逐字快照；
之后改 / 退 / 比全部只在副本上做。

为何不选另两种：工作树模式需要 git 写（本轮禁止）；整根复制是 MB 级成本、会把别人的在途面一起抄进来污染判据。

一条实现纪律（不是洁癖）：写副本一律走 `io.open(..., newline="")` ⇒ **不做行尾翻译**。
本机 autocrlf=true，若按平台默认写回，LF 被译成 CRLF，「退回」看着成功而 sha 已变 ——
第 5 节的假回滚负控就是专门把它造出来一次（实测 sha 从 01884cd1 变 fbcb1c00）。

## 3. 改 → 验 → 退 → 逐字全等（演练主结果，逐字读数）

```json
{
 "scratch_copy": "_repro/r306b/drill/A-prompt-better_SKILL.md",
 "how": "git show 17cc0c81~1:A-prompt-better/SKILL.md 的字节写入本目录副本（逐字节写、无行尾翻译）；不建 worktree、不 git 写、受管根零改动",
 "pre_sha256": "01884cd11aed608ba09d3911e96f0d4143a034ce75980719a0c04cf54f3d0aa3",
 "pre_bytes": 28761,
 "post_sha256": "fac939d845fa3b6780c9fa9b50638d49ed0a84cf8d6b1b421af0c049839728e8",
 "post_bytes": 28761,
 "post_equals_head_text": true,
 "revert_sha256_snapshot": "01884cd11aed608ba09d3911e96f0d4143a034ce75980719a0c04cf54f3d0aa3",
 "revert_identical_snapshot": true,
 "revert_sha256_git_show": "01884cd11aed608ba09d3911e96f0d4143a034ce75980719a0c04cf54f3d0aa3",
 "revert_identical_git_show": true,
 "revert_identical": true
}
```

四枚 sha 的读法与三方对齐：

- 改前 `01884cd11aed…`（28761B）= 基线版文本的 sha256，**且等于早前换装证据包里记录的 local_sha256**（三方对齐，非我推算）
- 改后 `fac939d845fa…`（35594B）= 当前 HEAD 版的 sha256 ⇒ 副本**逐字节复现**真落地态（`post_equals_head_text=true`）
- 退回（快照覆盖）`01884cd11aed…`；退回（按基线 ref 重取）`01884cd11aed…` ⇒ 两条通道都回到改前
- `revert_identical=true` 的口径 = **sha 相等 且 再做一次全文 == 逐字比对为 True**（两件事分别断言，不拿哈希冒充逐字）

## 4. 腿 A：旧文必拒（逐字实测）

判据：把补丁链应用到**与 old 不符的文本**上必须被拒（命中数 0，或 != 1），**不得静默跳过**。
算法与通用重放工具同语义：顺序 find、只替换第一处、幂等项（old 是 new 的子串）仍拒多命中。

判据脚本打印行（逐字）：
```
A legA       ok          ["A1 整链打到已落地文本上（每处 old 都与当前文件不符）：命中 PB-17cc0c81-01=count0 PB-17cc0c81-02=count0 PB-17cc0c81-03=count0 PB-17cc0c81-04=count0 PB-17cc0c81-05=count0 PB-f39eb3c0-01=count0 PB-f39eb3c0-02=count0 PB-f39eb3c0-03=count0 PB-f39eb
```

三形态结构化实测（逐字）：
```json
{
 "on_landed_text_all_hunks": {
  "errs": [
   "PB-17cc0c81-01(count=0)",
   "PB-17cc0c81-02(count=0)",
   "PB-17cc0c81-03(count=0)",
   "PB-17cc0c81-04(count=0)",
   "PB-17cc0c81-05(count=0)",
   "PB-f39eb3c0-01(count=0)",
   "PB-f39eb3c0-02(count=0)",
   "PB-f39eb3c0-03(count=0)",
   "PB-f39eb3c0-04(count=0)"
  ],
  "hits": [
   "PB-17cc0c81-01=count0",
   "PB-17cc0c81-02=count0",
   "PB-17cc0c81-03=count0",
   "PB-17cc0c81-04=count0",
   "PB-17cc0c81-05=count0",
   "PB-f39eb3c0-01=count0",
   "PB-f39eb3c0-02=count0",
   "PB-f39eb3c0-03=count0",
   "PB-f39eb3c0-04=count0"
  ],
  "rejected": true,
  "silently_skipped": false
 },
 "stale_old_first_hunk": {
  "errs": [
   "PB-17cc0c81-01(count=0)",
   "PB-f39eb3c0-01(count=0)"
  ],
  "hits": [
   "PB-17cc0c81-01=count0",
   "PB-17cc0c81-02=count1"
  ],
  "rejected": true
 },
 "ambiguous_old": {
  "old_repr": "连续两个换行",
  "errs": [
   "NEG-AMB(count=177)"
  ],
  "hits": [
   "NEG-AMB=count177"
  ],
  "rejected": true
 }
}
```

被拒用的真实锚文本 —— 链上第一笔（版本面）逐字：
```text
【old · 命中基线版，与已落地版不符】
  NOT a general chat skill. This skill should be used when the user explicitly
  calls it or when the task involves sending prompts to external AI models
  and the user wants them optimized first.
version: 1.3.0
last_updated: 2026-09-28
triggers:
  - 优化提示词
  - prompt优化

【new · 应用后】
  NOT a general chat skill. This skill should be used when the user explicitly
  calls it or when the task involves sending prompts to external AI models
  and the user wants them optimized first.
version: 1.4.0
last_updated: 2026-10-31
triggers:
  - 优化提示词
  - prompt优化
```

链上第二笔（对同一版本面的再改写，证明**两笔之间有真实前后依赖、顺序不可换**）：
```text
【old】
  NOT a general chat skill. This skill should be used when the user explicitly
  calls it or when the task involves sending prompts to external AI models
  and the user wants them optimized first.
version: 1.4.0
last_updated: 2026-10-31
triggers:
  - 优化提示词

【new】
  NOT a general chat skill. This skill should be used when the user explicitly
  calls it or when the task involves sending prompts to external AI models
  and the user wants them optimized first.
version: 1.5.0
last_updated: 2026-10-31
triggers:
  - 优化提示词
```

## 5. 腿 B：回滚必须逐字全等（逐字实测）

```json
{
 "true_revert_equals_pre": true,
 "fake_crlf": {
  "true_pre_sha": "01884cd11aed608ba09d3911e96f0d4143a034ce75980719a0c04cf54f3d0aa3",
  "fake_sha": "fbcb1c00a38e1999263009b3e7ca3a9dc91bc7b6ebbc64f591519f600531ceb6",
  "differs": true
 },
 "fake_half_chain": {
  "differs_from_pre": true,
  "applied": 8,
  "total": 9
 }
}
```

判据脚本打印行（逐字）：
```
D drill      ok          ["pre=01884cd11aed(28761) post=fac939d845fa(35594) rev_snapshot=01884cd11aed rev_refetch=01884cd11aed", "post==HEAD:True revert==pre:True 假回滚报红(行尾/半链):True True"]
```

两种**假退**都造出来试过，且都必须不等（否则第 3 节那个「相等」没有对照）：
- 假退一：同一文本按平台默认行尾写回（686 处 LF 变 CRLF）⇒ sha 不等，报红
- 假退二：只打链上前 8 笔（半链）⇒ 末端态与改前不等，报红

## 6. 判据自身的负控（把规格改坏，逐条实跑）

```text
N2 首轮（单链时代）：替换串不在该 hunk 内（indexOf=-1）⇒ 空操作负控，作废重做 | rc=0 | 报红=否 |（空操作，作废）
N1 版本期望改回上一版 | rc=1 | 报红=是
N2 一处 old 尾部追加不可能串（漏打/锚点被改坏） | rc=1 | 报红=是
N3 一处 new 尾部加一字（末端态被手改） | rc=1 | 报红=是
N4 base_ref 取更早提交（基线取错） | rc=1 | 报红=是
N5 required 镜像根指向不存在目录 | rc=2 | 报红=是
N6 裸指针词表加入文中真存在的词 | rc=1 | 报红=是
N7 同一笔补丁重复挂两次（多打） | rc=1 | 报红=是
N8 上游声明件挂一笔假补丁（改写未挂链） | rc=1 | 报红=是
N9 假回滚·行尾翻译（写盘不做 newline 直通） | rc=- | 报红=是
N10 假回滚·半链（只打前 8 笔） | rc=- | 报红=是
```

覆盖缺陷类型：漏打 / 多打 / 事后手改一字 / 基线取错 / required 根缺失 / 裸指针 / 未挂链的改写 / 版本漂移 / 假回滚两种。

**自曝一（判据自证直接命中）**：负控第一轮有一条写的是「把某笔 hunk 的 old 里一个小节标题换掉」，跑出 rc=0 仍绿。
按纪律**先怀疑复跑脚本**而不是判据：探针实测那个待替换串在该 hunk 里根本不存在（indexOf=-1）⇒ 变异是空操作，
「负控没红」不能用来证明判据无牙。重做为「old 尾部追加必然不存在的串」后立刻报红。
写成规矩：**负控必须先断言变异真的生效**（mutated=true），否则它证明的是我的字符串拼接，不是判据。

**自曝二（同族）**：补丁生成器第一版漏写「离开 hunk 头」的自增，同一 hunk 被二次处理、命中数归零，
报出「找不到唯一锚点」的**假失败**；我先用只读探针逐档打命中数（第一档就已 count=1）定位到生成器本身，而不是放宽锚点判据。

不变式（一条内核抓四类）：
```
盘上文本 == 在 base_ref 版上按顺序重放本单全部补丁的结果
```

## 7. 规格里两处「先读现形才敢写」的判定（禁凭记忆的部分）

1. **版本史形态与三份参照件不同**：本件是**中文小节标题 + Markdown 表格行**（竖线 V1.5.0 竖线 2026-10-31 竖线 变更 竖线），
   三份参照件都是「短横 加粗 版本 加粗 括号日期」的项目符号行。故规格写 `history_form: markdown-table` 与 `history_row_regex`，
   并点名一条**已实测的工具缺陷**：通用工具的版本腿只认项目符号行，对本件取不到史行会判 BAD
   （实测本件项目符号行 12 条，无一是版本行；本件的版本腿由自证脚本按表格实现，实测 fm 与 hist 双向一致 1.5.0/2026-10-31）。
   修法在工具侧，不在被测件侧 —— 把表格改成项目符号来迁就工具 = 改被测件换假绿，禁止。
2. **frontmatter 现形**：版本键与日期键都是单行 `键: 值`（键名与参照件一致，故规格沿用），现值 1.5.0 / 2026-10-31；
   全文 **CR 计数 = 0**（纯 LF，改前改后都 0）⇒ 重放可按字节级断言，不必先归一行尾。
3. **登记不改**（本轮禁写受管根）：本件版本史表格的分隔行被压在 V1.3.0 记录之后而非表头之后（本轮之前既有，非本轮引入），渲染会断表。
   要修须另开一单把补丁追加进本单规格链，否则重放腿判红。

## 8. 裸指针 / 镜像 / 上游声明件（一并实测）

```json
{
 "bare_pointer_hits": 0,
 "mirrors": [
  {
   "root_label": ".agents/skills",
   "required": true,
   "lag": []
  },
  {
   "root_label": ".claude/skills",
   "required": false,
   "lag": [
    "A-prompt-better/SKILL.md(缺失)",
    "A-prompt-better/.upstream(缺失)"
   ]
  },
  {
   "root_label": ".codex/skills",
   "required": false,
   "lag": [
    "A-prompt-better/SKILL.md(缺失)",
    "A-prompt-better/.upstream(缺失)"
   ]
  }
 ],
 "side_unchanged_since_r304": true
}
```

镜像读数解释：required 根本单两件全同 lag=0；另两个根**目录存在而本件缺失**，按 required/observed 分离口径只报状态、不判红
（把「我猜谁在读它」写进判据才是缺陷）。上游声明件自建立后未被这两笔落地动过（实测等值），
故规格给它挂**空补丁链**当「没被偷偷改写」的守卫 —— 负控 N8 就是专门假挂一笔把它判红。

## 8.5 把规格直接喂给通用重放工具（已实测，逐字）

只读取证、未跑门禁总控。读数：
```text
R replay           ok           A-prompt-better/SKILL.md hunks=9; A-prompt-better/.upstream hunks=0
N new-files        ok           无新增件
P pointer-clean    ok           bare=0; masked=0
V version          BAD          fm=1.5.0/2026-10-31 hist=None/None want=1.5.0
[LANDING-CHECK] spec=A-prompt-better R=ok N=ok P=ok V=BAD M=ok gate=FAIL
```

同一次运行加 hand-edited 负控（内存里把盘上文本改一个字符）：
```text
[LANDING-CHECK] spec=A-prompt-better R=BAD N=ok P=ok V=BAD M=ok gate=FAIL
R replay           BAD          … A-prompt-better/SKILL.md/REPLAY-MISMATCH@line734
```

两条结论：① 规格形态与既有三件兼容（四条腿直接绿）；② 唯一那条红是工具的版本腿只认项目符号史行（hist 取不到），
与本规格 version.note 的预判**逐字吻合** => 待修在工具侧（版本腿加表格分支），不在被测件侧。

## 9. 复现命令与期望末行

```
cd "C:/Users/37533/Desktop/workspace/skill焚诀"
C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B 自建skill优化/_repro/r306b/check_r306b.py
```

期望退出码 `0`；期望末行（逐字，实测）：
```
[R306B:SPEC] spec_ok=true fields=7 patches=9 drill=revert_identical=true pre_sha=01884cd1 post_sha=fac939d8
```

字段口径：`fields=7` = 规格顶层键数（与三份参照件同集，脚本首行打印 sorted(keys)）；
`patches=9` = 本单补丁链 hunk 总数（= 5 + 4 两笔；补丁**文件**数 = 2 记在 K 腿明细里）。

## 10. 结论分档（已实测 / 部分实测 / 未实测）

| 结论 | 档 |
|---|---|
| 规格件字段齐（7 键同参照件）、可 json.loads、两笔链可解析且每项含 id/old/new | 已实测 |
| base_ref + 9 处 hunk 顺序重放 == 当前 HEAD（字节级，命中数 9/9 全为 1） | 已实测 |
| 改→验→退→逐字全等（两通道，四枚 sha 全对，post 逐字等于 HEAD） | 已实测 |
| 腿 A 三形态必拒（整链 9/9 count=0、篡改 count=0、歧义 count=177）、无静默跳过 | 已实测 |
| 腿 B 真退全等 + 两种假退必不等 | 已实测 |
| 判据自身负控 10 条（含 1 条我跑成空操作后作废重做） | 已实测 |
| 版本腿按表格形态与 frontmatter 双向一致（1.5.0 / 2026-10-31） | 已实测 |
| 裸指针 0 条、required 镜像全同、声明件未被改写 | 已实测 |
| 通用工具的版本腿对本件判 BAD（形态不匹配） | 已实测（登记为工具缺陷，**未修**） |
| 上游 blob 与本地件四区吸收是否逐字忠实（内容级 I1–I4） | 未实测（本轮不重跑早前换装证据，只锚其 blob 短 sha 742deafa） |
| 换装该不该做、值不值得 | 不属本件（裁定在早前轮次侧，我只出规格与演练） |
| 镜像同步对全部端是否生效 | 部分实测（只核规格声明的三个根） |
| 本件体量是否越过技能主文件软门槛 | 未实测（禁跑门禁总控，且非本件判据面） |

**再次声明：本件未落地。** 盘上的 1.5.0 来自外部两笔 rule_editor 提交，不是我写的。

## 附录：本轮产出清单

```text
A-prompt-better.json
check_r306b.py
diag_b.py
drill
drill_result.json
gen_b.py
patches
rollback_drill.md
-- 补丁子目录 --
patch_r306_absorb.json
patch_r306_b_verbatim.json
-- 演练子目录 --
A-prompt-better_SKILL.md
fake_revert_crlf.txt
pre_snapshot.bin
```

