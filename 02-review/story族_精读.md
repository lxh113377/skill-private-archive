# story族精读审计卡（阶段2 第3批）· 小说创作流水线 11 个

> 生成：2026-09-14 | code-explorer 只读精读 | 主文件合计 **278,833 B**，11/11 全超 4KB

| skill | 字节 | 流水线位置 | 门禁 | 版本一致 | 关键问题 |
|---|---|---|---|---|---|
| story-setup | 35,388 | 初始化(最前置) | Y | **Y**(1.2.8 三处自洽) | [P0] :135 依赖不存在的 `scripts/generate-codex-agents.py`/`sync-opencode.py`；[P1] 硬编码"13 个 SKILL.md"实测仅 12 |
| story-import | 36,833 | 导入(setup 后) | Y | N | [P1] 长/短篇两套分叉重复实现(3-L :234 / 3-S :493) |
| story-long-scan | 17,347 | 扫榜(长篇) | Y | N | [P1] Phase1-4 与 short-scan 逐节同构，仅平台表不同 |
| story-short-scan | 9,206 | 扫榜(短篇) | **N** | N | [P1] **全族唯一无质量门**（long-scan:149-157 有） |
| story-long-analyze | 26,173 | 拆文(长篇) | Y | N | [P1] 与 short-analyze 6 个**同名不同体** references(27.81/33.68KB) 无同步 |
| story-short-analyze | 17,285 | 拆文(短篇) | Y | N | [P1] 版本 3.0.0 孤高 vs 族内 1.x；20 refs 中 6 个同名不同体 |
| story-long-write | 19,866 | 写作(长篇) | Y | N | [P2] 已用 R178 分卷，但 `templates.md` 56.54KB 未再分卷 |
| story-short-write | 36,157 | 写作(短篇) | Y | N | [P1] 全族最大且**未分卷**，与 long-write 的分卷实践双标 |
| story-review | 35,399 | 审查(通用) | Y | N | [P1] 硬编码 `agents_version==22`(:39) 与 setup 双写 |
| story-deslop | 30,147 | 润色(通用) | Y | N | [P1] 7 Gate 手写规则与 `anti-ai-writing.md` 双源 |
| story-cover | 15,032 | **无声明** | Y | N | [P1] 全族唯一无「流程衔接」段 → 流水线脱链 |

## 🎯 合并决策：**只合并 1 对**（11 → 10）

**关键判据：sim 0.911 是表层相似，不是流程可替换。**

| 对 | sim | 差异性质 | 建议 |
|---|---|---|---|
| **scan** | 0.845 | **纯篇幅/平台参数**：Phase1-5 骨架逐字同构，差异只有平台清单与 scraper 数（5 平台/5 脚本 vs 4 平台/2 脚本） | ✅ **合并为 `story-scan --length=long\|short`** |
| **analyze** | 0.853 | **流程本质不同**：Stage 0-6 + 并行 agent + `_progress.md schema_version:2` vs Stage 2-6 单线程 + `_meta.json` 五段式；且 **6 个同名 references 内容不同体** | ❌ 保留 2 个 |
| **write** | **0.911** | **流程本质不同**（相似度最高但不可合并）：长篇 `正文/第XXX章`+`追踪/`+`大纲/` 四件套 + 日更/大修状态机 vs 短篇单文件 `正文.md` + 8000/800 字硬门槛一次成稿 | ❌ 保留 2 个 |

合并 write 对会把 36KB 推到 70KB+（`if length==long then … else …` 全篇分支）；analyze 对的同名不同体 references **无法用参数消解**。

**scan 合并的额外收益**：顺手补齐 short-scan 缺失的采集质量门，并统一两者不一致的下游契约（long-scan:280 落盘 `选题决策.md`，short-scan 只给清单）。

## 整族收敛？不能整族合并，但建议加 1 个薄路由

- 反对整族收敛：write/analyze 流程已判定不可参数化；`story-setup` 是唯一部署器（写 `.story-deployed`、7 agent、6 端模板）；`story-review` 是唯一质检器（S1-S4 Findings）。
- **建议新增 ~2KB 的 `story` 路由 skill**：只做「意图 → 命令」分发并声明完整流水线（setup→import→scan→analyze→write→review→deslop/cover）。理由：流水线位置只散落在各 skill 的「流程衔接」表里，**没有机读总图**；story-cover 已因此彻底脱链。

**必须保留独立入口**：`story-setup`（部署器，被 import:87/review:40 反向依赖）、`story-review`（质检器，被 import:576 硬跳转）、`story-deslop`（唯一"改文"路径，review 只报不改 :161）、`story-cover`（需补流程衔接段挂回）。

## 共性结论

1. **闭环三件套全族归零**：11/11 grep「七步」「footer」**0 命中**；门禁 10/11（仅 short-scan 无）；版本一致 1/11。**与前 3 批同病，属全库系统性缺口**。
2. **资产硬复制 ~460KB 且被文档自承认**：`check-ai-patterns.js` 59.87KB×4、`anti-ai-writing.md` 36.19KB×5、`banned-words.md` 9.03KB×6；deslop:362 与 review:163 明文写「这些脚本都是本 skill 的本地副本」——**重复是被设计进去的**，改一处需同步 4-6 处。
3. **跨 skill 硬编码耦合 2 处无单一权威**：①`agents_version: 22` 双写在 setup:18/39/222/230 与 review:39（后者 `>22` 也降级 solo，**等于封死升级**）；②setup 四处硬编码「13 个 SKILL.md」，实测 story* 11 + browser-cdp = **12**，已漂移。
4. **分卷实践同族双标**：short-write 36,157B 未分卷，而 long-write 已用 R178 压到 19,866B；但 long-write 的 `templates.md` 自身 56.54KB 也未再分卷。
