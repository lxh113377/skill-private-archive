# 自建 skill 体系优化审计报告

> 生成：2026-09-14 | 阶段0-2 全部产物汇总
> 范围：`D:\global_skills` 自建 skill **103 个已全量精读**（7 批）；其中 11 个经精读判定为市场/上游件，真自建约 **91 个**
> 方法：三源交叉裁定 → 四维机器扫描 → 子代理分族全量精读（只读）
> 可信度：本文结论均标注 ✅已实测（子代理逐条附文件:行号证据，原文见 `02-review/` 七份审计卡）

---

## 一、四维结论

| 维度 | 结论 | 实测数据 |
|---|---|---|
| **体积（注意力税）** | 🔴 系统性失守 | 102 个中 **83 个超 4KB（81%）**；全库 `*.part*.md` 实测 **0 个**——4KB 拆卷机制**从未作用于 skill 自身**。最大：`A-project-handoff` 84,818B(20.7×)、`openclaw-task-supervision` 32,570B、`agent-browser` 28,360B、`chaoshi-web-deploy` 39,434B |
| **触发与路由** | 🟠 局部失效 | description <40 字 9 个；**`sq-cleanmgr-c` 无 `description` 字段 → 9 个触发词永不命中**；`A-ask-questions` 仅 29 字且触发词全为同义泛词；**全库仅 2/15 审计族 skill 有 frontmatter `triggers:`**，而其中 3 个正是审触发词质量的 skill |
| **死链·过时·冲突** | 🔴 最严重 | 机器扫 4 个 + 精读新增 **17 个 P0 死链**；`Desktop\焚诀` 单条路径漂移覆盖 **13+ 处**；跨 skill 规则冲突 3 处；规则自违 2 例 |
| **重复合并与闭环** | 🔴 闭环全库性缺口 | 合并：审计族 15→8、story 11→10、local 保留(合 2 组)、编码族 2→1、清理 2→1。**闭环：七步闭环与 footer 协议在各批命中率均 0-1/15**，属全库系统性缺口而非个别族问题 |

---

## 二、P0 清单（按「一次修复能覆盖多少处」排序）

### 🥇 第一梯队：单条修复覆盖多处的杠杆项

| # | 问题 | 覆盖 | 修复动作 |
|---|---|---|---|
| P0-1 | `C:\Users\37533\Desktop\焚诀\` **整条路径不存在**（正确为 `Desktop\workspace\焚诀`） | **13+ 处**（fenjue 3 + 审计族 ≥10：skill-trigger-diagnosis:25/155/185/194、skill-defer-to-authority:56/209、data-layer-consistency-fix:88/155/279/404…） | 全库批量替换路径串 |
| P0-2 | **CC(Claude Code) 已弃用 2026-09-08 却仍是核心执行门** | `fenjue-advisor-scoring`（核心评分门=CC）、`fenjue-cc-audit-cycle`（全流程"发 CC 审计"）、`cross-platform-agent-sync`（12+ 处）、`windows-cli-utf8-wrapper`（主示例）、`discover-agent-cli`、`workflow-preflight-check`、`prompt-system-audit` 等 | 替换为 OC/TR；**已停用两件走退役而非修复** |
| P0-3 | `prompt-system-audit` 的 V8/V9 围绕 `common_prompts.md`，该文件**全盘 0 命中** | V8/V9 两个审计维度不可执行 | 定位真实真相源或标注该维度废弃 |
| P0-4 | **Notion MCP 未配置**（mcp.json 仅 playwright/lighthouse-ops） | 4 个 Notion 件共 **30.8KB 整体空转**，从未跑通过 | 合并为 1 个占位件，待 MCP 接入启用 |

### 🥈 第二梯队：单点崩溃（照抄即失败）

| # | skill | 证据 |
|---|---|---|
| P0-5 | `chaoshi-image-optimization` 硬编码 `ffmpeg-8.1.1-full_build`，实测只有 `ffmpeg-9.0` | Step2/2.5/3 **脚本必崩** |
| P0-6 | `fenjue-routing-health-check` CHECK-3 指向 `VERSION_LOCK.part2/3/4`（不存在） | 执行得 **0 条假阴性**（比报错更危险） |
| P0-7 | `c-cleanup` 引 `scripts/scan_nvidia_cache.ps1`、`cleanup_workspace.ps1` | 实测 scripts/ 仅 2 文件 → 运行即断 |
| P0-8 | `wps-knowledgebase` 4 处引用（`references/workflow.md`/`scripts/run.js`/`setup.js`） | 目录**只有 SKILL.md** |
| P0-9 | `first-principles-decomposer` Integration 段 4 个联动 skill | 全部不存在 |
| P0-10 | `hook-analyzer-skill` + `report-generator-skill` 共同上游 `video-breakdown-skill` | 不存在 → 两件输入契约悬空 |
| P0-11 | `A-get-memory` 引 `scripts/trace_view.py`、`scripts/wf_*.ps1` | 实测无此二文件（4 处引用） |
| P0-12 | `openclaw-fenjue-weekly` 收尾硬门禁指向 `sync-global-memory` skill | 不存在 → 门禁不可执行 |
| P0-13 | `openclaw-task-supervision` 兜底依赖 `qoder_start_task` | Qoder 2026-08-01 卸载 → 错误处理#7 全废 |
| P0-14 | `cross-platform-agent-sync` 引 `A-memory-align` | 全库 0 命中 |
| P0-15 | `deep-research-pro` 核心脚本 `ddg-search` | 不存在 → 全流程不可执行（且为市场包） |
| P0-16 | `skill-install` 安装目标 `~/.codebuddy/skills/` | 不存在且非四端同步面 |
| P0-17 | `story-setup` 引 `scripts/generate-codex-agents.py`、`sync-opencode.py` | 目录内无此二文件 |
| P0-18 | `wechat-voice-transcription:62` 称 `local-asr` 已删除 | 实测 `D:\global_skills\local-asr` **存在** → 事实错误误导路由 |
| P0-19 | `data-layer-consistency-fix` 4 处注册表路径（缺 workspace 段） | 与 P0-1 同源 |
| P0-20 | `cloudbase-webapp-deploy-debug` 全篇教 `tcb` | `chaoshi-web-deploy:10` 已宣告停运并禁 tcb → **执行即误导** |

### 🥉 第三梯队：治理规则自违（不改则后续推不动）

| # | 问题 | 证据 |
|---|---|---|
| P0-21 | `A-project-handoff` 84,818B 无分卷，却用 `split` 强制他处 4KB 拆卷 | SKILL.md:553 vs 自身 716 行 |
| P0-22 | `bigfile-split` 自身 15,360B(3.75×) 却强制全库 ≤4096B **零豁免** | L18-23 vs 实测 15KB |
| P0-23 | `fenjue-advisor-scoring:265` 自定"超 4KB 记 0 分"，自身 25.17KB | 自我击穿 |
| P0-24 | `cross-platform-agent-sync:264` 自定"分卷 ≤4KB 硬上限"，自身 19.59KB refs=0 | 自违 |
| P0-25 | `A-project-handoff` frontmatter `3.22.0` vs 版本历史 `V3.35.0` | 差 13 个版本 |

---

## 三、P1 清单（按族归并，择要）

- **A族**：`A-memory-start:60` 门禁模板仍列 CC/HM 与同文件 :134 弃用声明自相矛盾；`.rule_backup/` 248 个 .bak、同日同文件 8 份（违反自家 R198.7）；`A-ask-questions` description 29 字 + `solution_exploration.md` 孤儿；`A-prompt-better` 版本历史表格 :672 多余分隔行
- **fenjue族**：评分制三套并行（150/160/80 分）；`routing-health-check` 硬编码"144 个 skill" vs 实测 174；`memory-audit` 版本三处不一致
- **审计族**：`skill-manager` 28.19KB 无 references；`defer-to-authority` C6"禁止委托" vs `openclaw-dual-gate` 铁律#3"必须子代理" **规则冲突**；`vp-perspective-audit` 缺"何时不用我"负向边界（**路由误命中根因**）
- **story族**：`agents_version: 22` 双写在 setup 与 review（**封死升级**）；setup 硬编码"13 个 SKILL.md"实测 12；资产硬复制 ~460KB 且文档自承认是"本地副本"
- **local族**：`local-vram` 文档与实现漂移（SKILL.md 无门禁但 run.ps1:50-53 会硬退）；OCR 三方/图生成二方触发冲突无仲裁
- **其他族**：`shell-encoding-pitfalls` 的 `name` 与目录名不一致；`static-site-batch-audit-fix:129` 与 `agent-browser:411` 事实冲突；`hermes-installer`/`9b-lightworkflow` 依赖 HM（**口径已裁决：HM 回归，转保留**）

---

## 四、P2 清单（合并与优化）

| 决策 | 对象 | 结果 |
|---|---|---|
| 合并 | 审计族 15 个 | **→ 8 顶层 + 3 references**（命中率链 5→2、注册表外科 3→1、指令+数据层 2→1） |
| 合并 | `story-long-scan` + `story-short-scan`(0.845) | → `story-scan --length=long\|short` |
| **不合并** | `story-long-write`↔`short-write`(**0.911**)、`long-analyze`↔`short-analyze`(0.853) | 长篇状态机 vs 短篇单次成稿；analyze 有 6 个**同名不同体** references，无法参数化 |
| **不合并** | local 族 10 个 | 模态互斥，合并=10 倍注意力税；改为合并 2 组 + 抽 `_shared/local-runtime` + 薄路由仲裁 |
| 合并 | `shell-encoding-pitfalls` + `utf8-encoding-fix`(0.803) | → 1 个 |
| 留一弃一 | 留 `c-cleanup` / 弃 `sq-cleanmgr-c` | sq 是 marketplace 件 + 无 description（死 skill） |
| 退役 | `cloudbase-webapp-deploy-debug`、`deep-research-pro`、`multi-search-engine`、`skill-install` | 停运/市场件/目标不存在 |
| 退役 | `fenjue-advisor-scoring`、`fenjue-cc-audit-cycle` | **用户确认日常已不再使用** → 走归档而非修 CC |
| 降级 | `taskflow-inbox-triage` → `taskflow/references/` | 父子示例关系，66 行重复率 >90% |

---

## 五、工作流闭环专项（阶段5 输入）

1. **七步闭环 / footer 协议是全库系统性缺口**：各批命中率 0-1/15，仅 `A-memory-start`、`A-prompt-better`、`A-ask-questions`、`prompt-consolidation` 有七步；footer 仅 `A-memory-start`、`A-get-memory` 有
2. **footer 协议四处重复定义**（A-memory-start:69/:93 + A-get-memory:166-170/:292），虽互标"唯一真相源"仍属双写
3. **方案探索模板三源并存且互相否认**（A-ask-questions:122-140 / 其 references/solution_exploration.md / A-memory-start:91 称后者为死链但文件真实存在）
4. **路由误命中已定位根因**：`vp-perspective-audit` 缺"何时不用我"负向边界（同族 `skill-hitrate-full-audit:19-23` 有该列）+ description 含"适用于任何多 agent 系统"→ 触发面覆盖全族
5. **跨 skill 规则冲突 3 处**：defer C6 禁止委托 vs dual-gate 强制子代理；chaoshi-web-deploy 禁 tcb vs cloudbase 全篇教 tcb；agents_version 双写

---

## 六、阶段 4 批次建议

| 批次 | 内容 | 杠杆 |
|---|---|---|
| **批1** | P0-1 路径批量替换 + P0-2 CC 替换（已停用两件走退役） | 覆盖 **20+ 处 P0** |
| **批2** | P0-3/4 真相源定位与 Notion 件合并；P0-5~20 逐个单点修复 | 18 个单点 |
| **批3** | P0-21~25 治理规则自违（先拆 `A-project-handoff` 84KB、`bigfile-split` 自拆） | 恢复治理可信度 |
| **批4** | 平台口径统一（含 **A-memory-start:134 需改回「HM 在役」**）+ 元数据漂移（版本/name 一致性） | 全库一致性 |
| **批5** | 合并与退役（审计族/story/local/编码族/清理族） | 103 → 约 85 |

> 每批执行约束：走 `rule_editor.py`，禁止 `write_file` 整体重写；改完 `build_registry.py --apply` 重建派生件；复跑三门禁（mirror / noise / evolution）。

---

## 七、仍需人工裁定

1. **真自建口径修正**：精读判定 11 个为市场/上游件，需确认是否从「自建 102」移出（真自建 → 约 91），并回改 `00-scope/自建skill清单.md`
2. **LOW 灰区 33 个**归属（github/gsap/obsidian-* 等）
3. **退役确认**：`cloudbase-webapp-deploy-debug`、`deep-research-pro`、`multi-search-engine`、`skill-install`、两个已停用 fenjue 件的最终处置
