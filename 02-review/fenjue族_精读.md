# fenjue族精读审计卡（阶段2 第 2 批）

> 生成：2026-09-14 | code-explorer 子代理只读精读（体积/死链均为实测）
> 范围：`fenjue-advisor-scoring` / `fenjue-memory-audit` / `fenjue-lessons-hitrate` / `fenjue-cc-audit-cycle` / `fenjue-routing-health-check`
> 权威平台口径（A-memory-start:134）：四端 = OC/WB/TR/CX；CC 已弃用 2026-09-08、HM 已卸载 2026-08-08、QW/QoderWork 已卸载 2026-08-01

---

### fenjue-advisor-scoring (25.17KB | refs=0 | 超4KB=是 | 分卷=无)
**触发**: desc≈62字 | triggers=无 | 质量=差（desc 标"三门仅归档"但铁律仍强制走已废 Step1-4）
**死链/过时**: `cc-claude-deepseek-proxy`(:309，无此目录)；`…\Temp\fenjue_prompts`(:83/:377，运行时自建) | 弃用平台名 CC/Claude Code(:3/:33-36/:92-120)、Hermes(:3/:11/:19/:46/:311/:321-323)
**重复/冲突**: ↔openclaw-fenjue-weekly 0.812、↔fenjue-cc-audit-cycle 0.809（后者:70 自称"内置替代"=双源）；17维×150分制 vs cc-audit-cycle:167 的 14维
**闭环**: 门禁=无 | 七步=无 | footer=无 | 版本history=有（3.3.0 与 frontmatter 一致）
**问题**:
- [P0] 核心评分门 = CC（已弃用）— :3/:33-36/:92-120
- [P0] 铁律19 强制"按 Step1-4 执行"，而 Step2/4 = 已废三门取 min，与 :15 自相矛盾
- [P0] 自身 :265 规定"超 4KB 硬判即 0 分" —— 本文件 25.17KB 无分卷，**自我击穿**
- [P1] 已废三门正文占 50-380 行约 75%，现行 R163 仅 27-38 行
- [P1] :309 引用不存在的 skill
- [P2] :83/:377 临时目录实测不存在
**整改**: 1. 删三门正文，CC 门改 OC/TR 2. 拆 .partN 或加索引 TOC

### fenjue-memory-audit (9.51KB | refs=4 | 超4KB=是 | 分卷=无)
**触发**: desc≈300字 | triggers=无 | 质量=中（关键词穷举充分但混含已废端名）
**死链/过时**: `D:\global_memory_archive\审计报告\`(:12，实测无此子目录) | 弃用平台名 CC/HM：audit_workflow.md:399/403/405（名册仍列六端 OC/WB/CC/TC/HM/CX）
**重复/冲突**: :10"总分制152.4" vs :125"最大值160" 内部矛盾；:9/13/22 声明取代的 A-memory-align、fenjue-cogrel-scoring 实测已删除（声明成空转）；与 advisor-scoring 同为焚诀评分（160制 vs 150制）双源
**闭环**: 门禁=有(audit_workflow.md:40/215) | 七步=无 | footer=无 | 版本history=**三处不一致**（frontmatter/:173=1.7.0，version_history.md 表末仅 V1.5.4，缺 V1.6.0）
**问题**:
- [P0] 平台名册过期：audit_workflow.md:405 六端含已弃用 CC/HM
- [P0] :10 的 152.4 制未随 V1.7.0 同步（:174 自称已修）
- [P1] :12 报告落盘目录不存在
- [P1] references 三文件 20.98/51.11/19.55KB 全 >4KB 无分卷
- [P2] rubric_d1_d27.md 文件名与 D28-D30 内容(:1156-1158) 不符
- [P2] desc 末尾混入 frontmatter 字段 `agent_created: true`(:3)
**整改**: 1. 同步 :10 与平台名册至四端口径 2. rubric/audit_workflow 拆 partN

### fenjue-lessons-hitrate (3.22KB | refs=0 | 超4KB=**否** | 分卷=无)
**触发**: desc≈60字 | triggers=无 | 质量=中（Use-when 开头但覆盖面窄）
**死链/过时**: `C:/Users/37533/Desktop/项目/焚诀`(:22，实测 Desktop 下无"项目"目录，真本为 `Desktop\workspace\焚诀`) | 弃用平台名=无
**重复/冲突**: 与 advisor-scoring:41(FP-05)、:373(FP-02) 同源各写一份
**闭环**: 门禁=有(:28-33) | 七步=无 | footer=无 | 版本history=**无**（frontmatter 2.0.0 无旁证）
**问题**:
- [P0] :22 运行路径死链，照抄即 cd 失败
- [P1] :15-17 四个核心文件均为相对路径，绑定死路径后全失效
- [P1] 无版本历史，2.0.0 无变更轨迹
- [P2] 12 条指纹仅 7 条机械可判(:46 有 5 条走人工)
**整改**: 1. :22 改为 `workspace\焚诀` 并补绝对路径 2. 补版本历史节

### fenjue-cc-audit-cycle (9.95KB | refs=0 | 超4KB=是 | 分卷=无)
**触发**: desc≈125字 | triggers=无 | 质量=差（desc 主场景"WB总控台+发CC审计"与 CC 已弃用**直接冲突**）
**死链/过时**: `C:\Users\37533\Desktop\焚诀\STATUS.md`(:118)、`…\memory\`(:107)、`…\prompts\`(:105) —— 实测 `Desktop\焚诀` **不存在**，真本在 `Desktop\workspace\焚诀` | 弃用平台名 QoderWork/QW(:224)、CC(:3/:10/:163-181/:222/:226)、六端(:209)
**重复/冲突**: ↔openclaw-fenjue-weekly 0.852、↔advisor-scoring 0.809；:70 声明后者"本 skill 有内置替代"=双源；:167 14维 vs advisor-scoring 17维/150分制
**闭环**: 门禁=有(:207/:209) | 七步=无 | footer=无 | 版本history=有（2.0.2 一致）
**问题**:
- [P0] 全流程以"发 CC 审计"为核心(:10/:163-181)，CC 已弃用
- [P0] 前置条件 104-108/118 全指向不存在的 `Desktop\焚诀`
- [P0] :209 同步"六端 OC/WB/CC/TC/HM/CX"与权威四端冲突
- [P1] 与 advisor-scoring 双源维护 CC 评分流程(:70)
- [P2] :69 把 openclaw-fenjue-weekly 列为 P2 收尾加载，与其"统领全局"定位倒置
**整改**: 1. CC 全量替换 OC/TR 并修 104-118 路径 2. 合并 advisor-scoring 评分流程

### fenjue-routing-health-check (23.98KB | refs=0 | 超4KB=是 | 分卷=无)
**触发**: desc≈230字 | triggers=无 | 质量=优（触发词穷举 + 复用接口说明完整）
**死链/过时**: `VERSION_LOCK.part2/3/4.md`(:227/:245-247) —— 实测 meta 下仅存 part1 + part15~part29 | 弃用平台名=无
**重复/冲突**: :135 硬编码"总计 144 个 skill" vs 实测 skill_routing.md:9"174 个 / 14 领域"；报告模板 392-424 仅含 CHECK-1/2/3 且 :418"3 PASS"，与现有 5 CHECK 不符；:87"5 个 subagent" vs :76/:487"4 个子任务"；:495-498 版本史称退役对账为 CHECK-4 与 :442 的 CHECK-5 冲突
**闭环**: 门禁=有(:359-372/:489) | 七步=无 | footer=无 | 版本history=有（2.5.1 一致）
**问题**:
- [P0] CHECK-3 主步骤 :227 指向不存在的 VERSION_LOCK.part2/3/4，执行必得 **0 条假阴性**
- [P1] 144 vs 174 skill 计数过期(:135)
- [P1] 报告模板 392-424 未随 CHECK-4/5 扩展，:418"3 PASS"失效
- [P1] 并行子任务数 4/5 自相矛盾(:76/:87/:487)
- [P2] 版本史编号与正文不一致(:495-498 vs :442)
**整改**: 1. :227 改动态枚举 VERSION_LOCK.partN 2. 模板同步 5 CHECK 并删硬编码 144

---

## fenjue族共性结论

1. **平台口径全线过期（最严重）**：3/5 仍把已弃用端当正式端 —— advisor-scoring 的**核心评分门就是 CC**、cc-audit-cycle **全流程"发 CC 审计"**、memory-audit 名册六端含 CC/HM。CC 已弃用 2026-09-08 → 这两个 skill **当前状态下不可执行，属 P0 崩溃级**。
2. **体积硬判自我违反**：4/5 SKILL.md >4KB（25.17/9.51/9.95/23.98KB）且全部无分卷；按 advisor-scoring:265 自定规则（超 4KB 记 0 分）应全部判 0。memory-audit 的 references 三文件更达 51.11/20.98/19.55KB。
3. **路径常年不更新致死链常态化**：lessons-hitrate:22、cc-audit-cycle:104-118、routing-health-check:227 三条实测均不存在，真本统一在 `C:\Users\37533\Desktop\workspace\焚诀`（与审计族同一根因）。
4. **闭环三件套普遍缺失**：5/5 无 footer、无七步闭环；advisor-scoring 连收尾门禁都没有。
5. **族内双源 + 多口径并存**：评分制 150分(advisor-scoring:184) / 160分(memory-audit:125) / 80分达标(cc-audit-cycle:121) 三套并行；advisor-scoring ↔ cc-audit-cycle 互称替代；memory-audit 自身 :10 与 :125 打架。

---

## 🔴 与审计族的交叉根因（两族同源）

`C:\Users\37533\Desktop\焚诀\` **整条路径不存在**（正确为 `Desktop\workspace\焚诀`），在 fenjue族造成 3 处死链、在审计族造成 ≥10 处死链（skill-trigger-diagnosis:25/155/185/194、skill-defer-to-authority:56/209、data-layer-consistency-fix:88/155/279/404 等）。**这是全库单一最高杠杆修复点**：一次批量替换即可消除 13+ 处 P0 死链。
