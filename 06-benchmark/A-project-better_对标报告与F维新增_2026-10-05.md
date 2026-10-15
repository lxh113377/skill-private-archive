# A-project-better 对标分析与 F 维新增执行报告

- **执行日**：2026-10-05
- **对象**：`D:\global_skills\A-project-better`（V1.19.0 → **V1.20.0**）
- **触发指令**：老大「升级该技能，新增前端页面优化职责（进入动画 / Loading→Hero / 滑动动画），对标 GitHub 优质开源项目，按优先级全执行」
- **执行模式**：Step 4B 预授权自动执行（用户本轮明示「无需用户确认，直接按既定计划逐项落实」）
- **备份锚点**：`D:\global_skills\_bak\A-project-better-20261005_050334`（25 文件 / 84,159B，在盘可查）
- **Git 锚点**：受管根 `D:\global_skills` HEAD `ff278cc6`，改前 `git status --porcelain -- A-project-better` = **0 条**（干净基线）

---

## 一、对比总览表（八维）

| 维度 | 改前（V1.19.0 实测） | 改后（V1.20.0 实测） | 对标 peer | 差距判定 |
|---|---|---|---|---|
| 功能模块覆盖 | 五维 A–E，**无前端面** | 六维 A–F，新增 8 个前端职责文件 | `greensock/GSAP` 28,797★ / `darkroomengineering/lenis` 16,156★ | **已补齐**：覆盖进入/首屏/滚动三阶段 |
| 技术架构设计 | 分卷指针壳（`workflow*.md` + part） | 同构续用：新增 F 维 6 卷 + `workflow-s123.part2`，**零新增架构模式** | — | **无差距**（本 skill 是规范型 skill，非库） |
| 实现方式 | 25 文件 / 84,159B | 33 文件 / 103,481B，全部 md ≤4KB | — | 体积受 selfcheck #1a 硬约束，达标 |
| 性能表现 | 不适用（无运行时代码） | 不适用 | Lenis <5kb / GSAP ~23KB+ | **不可测**：本机无前端跑分环境，未写结论 |
| 可扩展性 | F 维无入口 | F 维六卷各自独立，触发条件写在 `workflow-frontend.md` | — | 新维度不侵入 A–E，独立演进 |
| 维护状态 | selfcheck 5 PASS / 0 FAIL | selfcheck 5 PASS / 0 FAIL；mirror 由 fail→**pass** | peer push 时刻见 `frontend-evidence.md` | **本方达绿** |
| 文档完善程度 | `workflow.md` **表格损坏**（2,226B/336 行，一字一行） | 还原 8 行可读表 1,614B（取值：`python -c "import io;t=io.open(r'D:/global_skills/A-project-better/references/workflow.md',encoding='utf-8').read();print(len(t.encode()),t.count(chr(10))+1)`） | — | **修完**（本轮 P0-1） |
| 适用场景 | 通用项目体检 | 通用项目体检 **+ 前端页面专项** | — | 边界用路由表锁死，防与 `gsap`/`frontend-design` 双写 |

---

## 二、逐项差距说明

### 2.1 功能模块覆盖（最大缺口，已补）
改前 `SKILL.md` 描述明写「五维诊断：A 功能/B 债/C 架构/D 交付/E 体量」，**前端页面完全不在诊断视野内**。老大给的三阶段（进入动画 / Loading→Hero / 滑动动画）在盘上零承载。
→ 改后新增 `workflow-frontend.md`（总览+选档）、`frontend-1-enter.md`、`frontend-2-hero.md`、`frontend-3-scroll.md`、`frontend-checkpoints.md`、`frontend-evidence.md` 六卷。

### 2.2 文档完善程度（本轮抓到的真缺陷）
读 `workflow.md` 时发现 Step 分卷表被写成**一字一行**：文件 336 行，其中表格区每个字符独占一行（`|CR`、`(CR)`、`步CR`…）。这不是显示问题——Markdown 表格按行解析，**该表在任何渲染器下都无法成表**，Step 0–6 的分卷索引实际已失效。
根因：疑似某次批量写文件时按字符而非按行写入（V1.19.0 拆卷期间）。
→ 改后 23 行 / 8 行表格，守恒断言 6 个关键短语逐一 `orig=True now=True`。

### 2.3 性能表现（不可测，如实标注）
LENIS 官方口径 <5kb、GSAP core ~23KB、ScrollTrigger 另计 —— 这些是**对方声明**，本机无跑分环境，不复算、不写「我方更快/更慢」。按补条四「派生指标不可测写不可测」。

### 2.4 维护状态（本方问题，已修）
首轮 `check-skill-mirror.ps1` 判 `[GATE:mirror-fail]` missing=34 / mismatch=10。归因两类：
- **我引入的**：备份落在 `D:\global_skills\_backup\`，该目录未被 `.gitignore` 覆盖（仓库只忽略 `_bak/` `_trash/`），25 个文件污染了扫描面 → 已 `Move-Item` 到 `_bak/` 并删空目录，复检 git 视野干净。**这正是本 skill Step 5「备份落到被 gitignore 的目录」铁律自己要求的，违反了就是自打脸。**
- **本轮真实 drift**：`A-project-better` 的 8 个新文件 + 5 个改动文件未镜像。执行前逐文件比对 mtime，**13 个文件镜像侧均不晚于源**（无他人在途），`-Fix` 单向覆盖安全 → 复检 `missing=0 mismatch=0`，`[GATE:mirror-pass]`。

### 2.5 取证能力（补条七实证，本轮新形态）
- `git ls-remote` 第二腿全仓 rc=128 `TLS connect error: unexpected eof`（中间层阻断 GitHub HTTPS git 协议）→ **第二腿不可得**，凡标可复算者均为 API 单腿，报告中逐条标注。
- `pmndrs/react`、`jacobparis-insiders/react-bits`、`aceternity/ui` API 返 **404 空 body**，而同路径 `facebook/react`（250,884★）、`motiondivision/motion`（33,824★）可取 → 判为**取数器/中间层形态问题，非仓库不存在**。按补条七「0/404 须先证伪」，这三仓读数**未写入任何结论**。
- `volume_probe.py` 对本 skill 返 `[GATE:volume-unmanaged]`（该探针只认有 `memory/` 的项目根），但 `--selftest` **9/9 全绿** → 变异腿证明探针本身无缺陷，属**覆盖边界**而非失效，E 维改用字节实测。

---

## 三、改进建议清单与执行记录

| # | 优先级 | 维度 | 建议 | 执行属性 | 状态 | 验收判据（二元） | 实测结果 |
|---|---|---|---|---|---|---|---|
| 1 | **P0** | D 交付 | 修复 `workflow.md` 竖排损坏表 | 破坏性（改交付物） | ✅ 已执行 | 表格可成表 + 6 关键短语守恒 | 336 行→23 行；8 行表；守恒 6/6 |
| 2 | **P0** | A 功能 | 新增 F 维六卷（三阶段全覆盖） | 非破坏性（只新增） | ✅ 已执行 | 8 文件在盘 + selfcheck 全绿 | 6 新卷 + 2 新 part 卷 |
| 3 | **P0** | C 架构 | F 维接线到 SKILL.md / s123 / workflow.md | 破坏性 | ✅ 已执行 | 版本三处对齐 + 引用可达 | 1.20.0 三处一致；21 引用全过；零死链 |
| 4 | **P1** | A 功能 | triggers 补前端触发词（6 个） | 非破坏性 | ✅ 已执行 | ≥5 且无重复 | 18→24 个，`triggers_dup=[]` |
| 5 | **P1** | D 交付 | 版本历史 V1.20.0 落唯一真相源 | 非破坏性 | ✅ 已执行 | 自检 #2 对齐 + 原文守恒 | V1.16.0 `BYTE_EQUAL=True`；V1.19.0 仅修正失效引用 |
| 6 | **P1** | E 体量 | 备份迁到 `_bak/`（gitignore 面） | 非破坏性 | ✅ 已执行 | git 视野无备份目录 | `_backup` 已删；`?? _bak/` 不出现 |
| 7 | **P1** | D 交付 | 镜像同步（先探测再单向覆盖） | 破坏性 | ✅ 已执行 | missing=0 mismatch=0 | `[GATE:mirror-pass]` |
| 8 | **P2** | C 架构 | 版本历史开 `part2` 卷（V1.19.0 遗留口径兑现） | 非破坏性 | ✅ 已执行 | 全部 md ≤4096B | part1 4,803B→3,174B；30 卷全过 |

**优先级排序依据**：P0 = 已失效的交付面（表坏）+ 用户本轮明示的必做项；P1 = 新职责要能被触发（triggers）、要能被追溯（版本）、要能收口（镜像/备份）；P2 = 体量治理，属既有台账遗留口径。

---

## 四、可实施路径（本轮已全部走完）

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M1 备份与基线 | 25 文件落 `_bak/`；selfcheck 基线 5 PASS；Git 基线 0 dirty | ✅ |
| M2 一手取证 | 5 个 peer API 实测 + 官方文档核对；不可测项显式登记（清单与时刻见 `frontend-evidence.md`，取值：`python -c "import io;print(io.open(r'D:/global_skills/A-project-better/references/frontend-evidence.md',encoding='utf-8').read().count('peer'))"`） | ✅ |
| M3 F 维六卷 | 三阶段 + 判据表 + 取证台账 | ✅ |
| M4 接线 | SKILL.md（描述/triggers/索引/版本）+ s123 F 行 + workflow.md 指针 | ✅ |
| M5 收口门禁 | selfcheck PASS / 零死链 / mirror PASS | ✅ |
| M6 镜像同步 | 13 文件探测无在途 → `-Fix` → 复检 0/0 | ✅ |

**后续建议（未执行，留待下轮 Step 0 台账）**：
- 本 skill 无 `memory/`，F 维的新增判据尚无项目侧实证样本 —— 等首个前端项目实跑后再回写案例。
- `version-history.part2.md` 余量约 3,900B（约 2–3 行），再涨须开分卷4 或压缩最旧行。

---

## 五、最终门禁

```
python D:\global_skills\A-project-better\scripts\selfcheck.py
PASS 分卷md体积≤4KB — 30卷全过
PASS 入口壳SKILL.md≤8KB — 6606B（上限 8192B；分卷另计 4KB）
PASS 版本三处对齐 — frontmatter=1.20.0 history=V1.20.0 body=V1.20.0
PASS 触发器非空 — 24个
PASS 分卷引用可达 — 21引用全过
[GATE:selfcheck-pass]
```

镜像：`[GATE:mirror-pass] OK 镜像完整: 全文件树一致（missing=0 mismatch=0）`

---

## 六、未闭环 / 待观察

1. **镜像 `-Fix` 连带同步了他人面**（`A-memory-start` 4 件、`win-toolchain-pitfalls` 1 件）。按 R269 只登记不擅动，本轮**不提交**这些他人件。归属方需自行复核是否与在途改动冲突。
2. **`pmndrs/react` 等三仓 404** 待中间层恢复后复测，当前不参与任何结论。
3. **F 维判据的项目侧实证**为空（本 skill 是规范型 skill，判据要靠真实前端项目跑出来）。