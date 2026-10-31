# r322b · 入口可达性普查 v2（三处口径修正 + 四桶分账）

> Lead 自干（B 臂两轮全灭、第三次跑出 probe 后无收尾；按其 probe 线索与实测读数自建）。
> 判据：`python -B check_r322b.py` ⇒ `[R322B:V2CENSUS] broken_real=0 placeholder=9 orphans_top=624 orphans_nested=618 conservation=ok teeth=pass`

## 1. 首跑差 64 的根因（不修就永远对不上官方读数）

我的 v2 首跑报 `orphans_top=560`，官方旧件报 624，差 64 —— 全部是中文名文件（story-setup 32 + story-long-write 32）。
根因**不在 v2 的修正逻辑**，而在**复用的旧函数**：旧件 `git()` 调用没有带 `-c core.quotepath=false`，
`ls-tree` 对非 ASCII 路径输出八进制转义引号形态（本仓 16509 条里 109 条中文路径），不 unquote 就整批丢掉中文文件。
⇒ v2 自建 `tree_clean()`（带 quotepath=false + 逐行解码），首跑即精确复现 `624`。这条是本轮最有价值的自抓：
**旧读数 624 本身是对的，但它依赖的 tree 通道是脆的**（同一条命令换个 git 配置就会静默少 64 个文件）。

## 2. 三处口径修正（每处都有前后读数）

| 修正 | 前 | 后 | 判据 |
|---|---|---|---|
| P-1 噪声白名单（OFL 许可 30 / LICENSE 3 / 目录 README 28 / `_` 内部索引 11） | 624 全算空转 | **552 真候选 + 72 噪声**（prose_kb 4447 + noise_kb 334 = 4781） | 守恒腿 T2；负控 `--neg noise` 关白名单必须红 |
| P-2 占位符展开对树 + 生成物三桶 | broken=10 全判真断链 | **broken_real=0 / placeholder=9 / generated_output_ref=1** | 分桶守恒腿 T3；反例 `dispatch-NN.md`（占位形态但 0 命中）仍须红 |
| P-4 嵌套闭包 `--closure nested` | 只从顶层 SKILL.md 展开 | orphans 624→**618**，gstack 6→**0**；新增 1 条 broken 具名 `.github/workflows/test.yml` | T4；负控 `--neg nested` 使两口径读数相同必须红 |

## 3. 本轮最重要的结论：旧读数的 10 条「断链」**没有一条是真断链**

| 桶 | 条数 | 成员 |
|---|---|---|
| `PLACEHOLDER_PATTERN` | 9 | 9 个 story-* 的 `references/split-NN.md` —— 展开 glob 均命中 ≥1 个真实文件（split-01..10 共 34 个） |
| `GENERATED_OUTPUT_REF` | 1 | `html-ppt/examples/my-talk/index.html` —— `scripts/new-deck.sh <name>` 的运行产物 |
| `GENERATED_INSTRUCTION_REF` | 1（仅 nested 口径） | `gstack/.github/workflows/test.yml` —— 嵌套入口 `qa/SKILL.md:435` 与 `design-review/SKILL.md:412` 的 **Create 指令** |
| **真断链** | **0** | —— |

⚠️ 三条桶都**仍计入 broken 分母并在报告显形**，不判「不是断链」：静态可达口径下「入口提到、树里没有」就是缺陷，
桶只解释缺陷**类型**、不改判定（B 臂已在 html-ppt 那条论证过同一原则：一开口子任何反引号里的 typo 都能免责）。

## 4. 两口径读数（nested 是结构口径，不是运行面裁决）

| 口径 | broken | 其中真断链 | orphans | 噪声 | prose |
|---|---|---|---|---|---|
| top（旧行为） | 10 | 0 | 624 | 72 | 552 |
| nested（含嵌套入口） | 11 | 0 | 618 | 72 | 546 |

- nested 少 6 个孤儿 = gstack 的 qa/ 与 review/ 六个文件被嵌套入口逐字引用（r322a 已逐条核）
- nested 多 1 条 broken = 上面那条 GENERATED_INSTRUCTION_REF
- **运行面**（路由加载件后是否进一步吃嵌套 SKILL.md）仍 UNVERIFIED（r322a §5）⇒ 本件只称「结构可达」，不下运行结论

## 5. 对批次表的修订

- 逐条挂链下界：r321 的 259（552 − 293 目录级覆盖）**维持**；gstack 6 件（其中 1 条 near-fake）从 B6 摘出 ⇒ **约 253**
- B4 story 族：96/132 件的孤儿**全部是真孤儿**（无嵌套入口）⇒ 批次不变
- ppt-master 147 件**全部真孤儿** ⇒ B1 不变

## 6. 本件偏差与未覆盖面

- `GENERATED_OUTPUT_REF` 的启发式只认 html-ppt 的 new-deck.sh 一处（通用形态【入口提到 `scripts/<x>.sh <arg>` 且同件存在该脚本】未做泛化，会漏同类）。
- `GENERATED_INSTRUCTION_REF` 目前靠人工具名 1 条，未做成规则（nested 口径下若新增条目需人工核）。
- cloudbase 32 个嵌套件不在 52 件吸收名册面内，未纳入。
- 旧读数 624「是对的」这一结论的前提是 `quotepath=false`；这解释了为什么 r320 臂在正确的配置下能得 624 而我首跑 560。

## 7. 追加自抓（写本件过程中发现，编号顺延为 P-5）

**P-5 嵌套入口引用的是「安装后镜像路径」，不是件内相对路径。**
`gstack/review/SKILL.md:294` 写的是 `Read `.claude/skills/review/checklist.md``、:302 是 `...greptile-triage.md`、:351 是 `...design-checklist.md`；
`gstack/qa/SKILL.md` 对 `references/issue-taxonomy.md` 同类。⇒ **同一批文件同时存在两种引用形态**：件内相对路径、安装后镜像路径。

我的判定用的是 basename 包含 ⇒ 两种形态都能命中，所以 5/6 判「可达」。但若判据改成**严格件内路径解析**，这 5 条会全部翻红
（`.claude/skills` 不在件内）。⇒ 「嵌套入口的可达性」本身有两个正确性级别：

| 级别 | 口径 | 读数 |
|---|---|---|
| L1 basename 可达 | 文本里出现过该文件名 | gstack 5/6 可达（本件采此级，与 v2 全库口径一致） |
| L2 路径解析可达 | 引用的路径能在件内解析到真实文件 | **0/5 可解析**（都指向 `.claude/skills/...`） |

⇒ 这不是豁免、是**缺口**：L2 未实装。处置写死在案：若将来要按 L2 收紧，必须同时给出「镜像路径 ⇒ 件内路径」的显式映射规则，
否则收紧会把 5 条本来就正确的引用判成断链（假红）。**本轮不动口径**，只登记（承 R263「先评审再改尺」）。

## 8. 本件最终读数（三口径 × 四桶）

```
python -B r322_v2_census.py --closure top    --json census_v2_top.json
python -B r322_v2_census.py --closure nested --json census_v2_nested.json
python -B check_r322b.py                    # [R322B:V2CENSUS] broken_real=0 placeholder=9 orphans_top=624 orphans_nested=618 conservation=ok teeth=pass
```