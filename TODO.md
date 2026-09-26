# TODO — 阶段状态总表（索引，**非入口**）

> **入口声明（2026-09-22 修正）**：跨会话**唯一入口 = `memory/07-next-steps.md`**（A-project-handoff 致命纪律 #1）。本文件只做「六阶段状态总表」，**不承载 P0** —— 此前本文件自称「唯一入口」，与 handoff 法定入口冲突，已消解。
> 更新：2026-09-22（第 10 轮） | 当前阶段：**阶段0-5 全部完成**（阶段5 两项 `direct_map` / 注册表复核已收口）
> 权威范围：`00-scope/自建skill清单.md` | 权威源：`D:\global_skills`（git）→ 镜像 `C:\Users\37533\.agents\skills`
> 三处分工（消三重同义源）：查「下一步做什么」→ `memory/07-next-steps.md`；查「哪个阶段到哪」→ 本表；查「上一轮干了啥」→ `05-exec/README.md`。

## 六阶段状态总表（2026-09-22 实测）

| 阶段 | 状态 | 产物 | 未闭环项 |
|---|---|---|---|
| 0 范围裁定 | ✅ 完成 | `00-scope/`（3 文件） | — |
| 1 四维机器扫描 | ✅ 完成 | `01-scan/` + `archive/` | — （2026-09-22 第 10 轮补齐三脚本与通配符检测，见 `05-exec/第10轮执行报告.md`） |
| 2 全量精读 | ✅ 完成 | `02-review/`（6 份族卡，7 批） | — |
| 3 审计报告 | ✅ 完成 | `03-audit/`（P0 25 项分级） | — |
| 4 实施计划 + 执行 | ✅ 完成（4 批） | `04-plan/` + `05-exec/` | 批5 其余项（用户裁定「只做 b」，b 已完成） |
| 5 工作流专项 | ✅ 完成（2026-09-22） | `04-plan/工作流专项建议.md` | ① `direct_map` 误命中 + 7 死目标已修（焚诀 `bf5e284`）② 注册表口径已裁定 **151 条**（焚诀 `28daf6e`） |
| 记忆层 | ✅ 建档 + 归档启用（本轮回填） | `memory/` 8 文件 + 分卷 + P-1 | 无（`archive/` 已启用：`scope-v1-169-2026-09-14/` + `overlap_raw.txt`） |

> **~~待确认（破坏性，未执行）~~ → ✅ 已闭环（2026-09-22 第 10 轮实测复核）**：**D7** 受管根 39 条残留脏项已于受管根 `172eb88` 一次提交完成（6 项迁移删除 + 跟进 33 个 `.rule_backup/*.bak`）；复测 `git -C D:\global_skills status --porcelain` = **零条**。（原文保留见 `memory/06-constraints.md` 与第 3 轮报告第十二节，R241 只加注不改写。）

## 待人工裁定（阻塞项）

| # | 事项 | 阻塞什么 | 建议 |
|---|------|---------|------|
| 1 | LOW 灰区 33 个归属（github/gsap/obsidian-*/spike/story/browser-cdp 等） | 阶段2 精读范围 | 建议：带 homepage 的已排除；其余 31 个多为社区包，`story`/`browser-cdp` 需用户确认 |
| 2 | 42 条 `user_created` 失真是否直接改注册表 | 阶段5 | 改前须 `build_registry.py --apply` 重建派生件并复跑门禁 |
| ~~3~~ | ~~HM 口径冲突~~ | — | ✅ **已裁决 2026-09-14：用户确认「HM 又下回来了」** → HM 恢复为在役端；`hermes-installer`、`9b-lightworkflow` **保留**；扫描脚本弃用名单已移除 Hermes/HM |

### 本轮补充（2026-09-14 末）

| 项 | 内容 | 状态 | 证据 |
|---|---|---|---|
| **B5-1** | **57 个遗留未提交改动处置** | ✅ 完成 | 按来源分 3 个 commit：① `A-memory-start/references/contract.md`（R232 配套漏提交）`f2d9faf` ② `cloudbase__skillhub` 市场包升级 2.33.2→2.34.2 + 2 新文件 + `github` 元数据 ③ `A-java-problem` 1.2.0→1.2.1。**工作区 status=0 清零** |
| **B2** | **退役 6 个 skill** | ✅ 完成 | commit `716ae69`；`cloudbase-webapp-deploy-debug`／`deep-research-pro`／`multi-search-engine`／`skill-install`／`fenjue-advisor-scoring`／`fenjue-cc-audit-cycle`。**副本已于 2026-09-14 按用户要求彻底删除**（`_trash/retired-2026-09-14/` 目录已移除，**不可回滚**）；源端+镜像端均已删除；镜像 `[GATE:mirror-pass]` |
| **_trash 清理** | 退役副本彻底删除 | ✅ 完成 | `retired-2026-09-14/`（6 副本 104.2 KB）已删；⚠️ `_trash` 内另有本会话拆卷前的 3 个原始备份（`A-project-handoff_.rule_backup` 55.8KB、`bigfile-split.SKILL.md.*.bak` 15KB、`cross-platform-agent-sync.SKILL.md.*.bak` 19.6KB）→ 待你确认拆卷结果无误后可清 |
| **审计修正** | `notion-research-documentation` | 🔍 新发现 | 该 skill **已在 `_trash`**（51.3 KB，先前会话退役）→ 审计报告中「4 个 Notion 件空转」实际在役仅 **3 个**（`knowledge-capture`／`meeting-intelligence`／`spec-to-implementation`） |
| **引用清理** | 退役留下的 6 处活跃引用 | ✅ **4/6 已清** | ① `A-get-memory/scripts/sync_skill_router.py` 删 `skill-install` 与 `deep-research-pro` 清单项（**脚本**，已 `py_compile` 验证）② `A-project-handoff:170` 表格行标注退役 ③ `skill-hitrate-improvement-pipeline:94` 标注退役。**剩余 2 处判定为历史案例记录**（`fenjue-routing-health-check:37` 的 2026-07-10 周维护复盘、`step2_4_missed_audit.md:5/26` 的漏用教训举例）→ 改之属篡改历史，**保留原文**；如需防误导可后续加退役标注 |
| **A1** | `A-get-memory` 死链修复 | ✅ 完成 | commit `5bcb550`；4 处（`trace_view.py`×3 + `wf_*.ps1`×1）标注实测缺失并给替代路径；版本历史行不动 |
| **A2** | `openclaw-task-supervision` Qoder 通道 | ✅ 完成 | commit `b6bf36e`；Qoder 段加失效警告（2026-08-01 已卸载），保留原文作设计参考 |
| **A3** | ~~14~~ **13 个 skill 补 `version:` 字段** | ✅ 完成 | commit `bc225b3`；**实做 9 个**（`ican-deploy`/`cross-platform-skill-sync`/`skills-security-check`/`shell-encoding-pitfalls`/`utf8-encoding-fix`/`wechat-voice-transcription`/`report-generator-skill`/`hook-analyzer-skill`/`agent-browser`）→ `version: 1.0.0`；**按新口径跳过 4 个**（`electron`/`shadcn`/`taskflow`/`taskflow-inbox-triage` 阶段2 已改判市场/上游件，补了会被上游覆盖）；`skill-install` 已退役。**核验：13 个正文全无 V 号** → 1.0.0 无倒退风险 |
| **A4** | ~~6~~ **7 个 local `meta.json` description 退化** | ✅ 完成 | commit `bc225b3`；**实做 7 个**（原清单**漏了 `local-vram`**）；**性质修正**：`meta.json` 是**腾讯 marvis 市场分包元数据**（`type=英特尔用户专区`+`download_url`），退化是**上游打包 bug**（YAML 多行块的 `|` 被直接塞进 JSON），**不参与路由**（路由读 SKILL.md frontmatter，7 个 SKILL.md description 实测全部正常且含丰富触发词）；改法 = **用同文件 `display_description` 回填**（零新增信息、零风险） |
| **A5** | `openclaw-dual-gate-quality-audit` description 收窄 | ✅ 完成 | commit `bc225b3`；description 重写（原为「…自评+Codex独立逐文件审计。openclaw双门禁审计」同短语重复）→ 补适用范围 + 4 个改投边界 + 7 个触发词；正文新增 `## 何时不用本 skill（负向边界）` 表格段（改投目标：`openclaw-task-supervision`/`openclaw-fenjue-weekly`/`skill-hitrate-full-audit`/`vp-perspective-audit`）；补丁留档 `05-exec/A5_patch.json` |

**执行顺序**：批3 → 批1 → 批2 → 批4 → 批5（批3 先做 = 先修治理规则自违，后续推 4KB 分卷才有说服力）

| 项 | 内容 | 状态 | 证据 |
|---|---|---|---|
| 3.5 | `A-project-handoff` frontmatter `3.22.0` → `3.35.0` | ✅ 完成 | commit `805465e`；读回 `version: 3.35.0` |
| 3.6 | `A-memory-start` frontmatter `10.27.0` → `10.28.0` | ✅ 完成 | 同上；源端与镜像端读回均为 `10.28.0` |
| — | 三门禁 | ✅ `[GATE:mirror-pass]`（missing=0 mismatch=0 extra=0） | `check-skill-mirror.ps1` |
| **1.1** | **全库 `Desktop\焚诀` → `Desktop\workspace\焚诀`** | ✅ **完成** | commit `1b6fe6d`；**11 文件 34 处**（实测命中 35 处，其中 1 处在 `_trash` 已跳过）；`[GATE:mirror-pass]`+`[GATE:noise-pass]`；改后残留命中=0 |
| **1.4a** | **平台口径统一（第1轮）**：`A-memory-start` G2 门禁模板 + 口径定义行 | ✅ 完成 | commit `5e89bb6`；模板 `<OC/WB/CC/TC/HM/CX>` → `<OC/WB/TR/CX>`；HM 改回在役 |
| **1.4b** | **平台口径统一（第2轮）**：`A-project-handoff`:124/142 + `A-get-memory`:422 | ✅ 完成 | commit `42760fc`；两文件单次收口 |
| 1.4c | 平台口径统一（余量） | ⬜ 待做 | **剩余活跃引用 90 处**（原 110，已扣 `pre-cc-check` 脚本名误匹配）。分类：路径映射表（`cross-platform-agent-sync` 4 处 `.claude\` 路径，CC 弃用后应删整条）／平台清单类（`cross-platform-skill-sync`:3/14/15、`skill-drift-surgery` 8 处、`data-layer-consistency-fix` 5 处、`discover-agent-cli` 5 处）／历史案例（`data-layer-consistency-fix:237`）。**口径基准：OC/WB/TR/CX（TR=TRAE=TC），CC 移除，HM 在役** |
| 3.1 | `A-project-handoff` 84,818B → 拆 references/ 分卷，主文件 ≤4KB | ⬜ 待做 | 需新建 references 文件，工程量大，单独一轮 |
| 3.2 | `bigfile-split` 15,360B 自拆为 6 卷 | ✅ 完成 | commit `98b974c`；主文件 **15362B → 3626B**，6 卷均 ≤4096B；镜像 `[GATE:mirror-pass]`；内容校验 14 章节 0 缺失 |
| **3.4** | `cross-platform-agent-sync` 19.59KB 自拆为 8 卷 | ✅ 完成 | commit（2026-09-14）；**20058B → 1764B**，8 卷均 ≤4096B；32 章节 0 缺失；`[GATE:mirror-pass]` |
| 3.3 | `fenjue-advisor-scoring` 退役 | ⬜ 待做 | 用户已确认不再使用；**退役前须确认无反向引用** |
| **2.x** | **死链修复 6 项**（本轮）| ✅ 完成 | ① `shell-encoding-pitfalls` name 与目录名对齐 ② `wechat-voice-transcription` local-asr 事实更正 ③ `first-principles-decomposer` 4 个不存在联动 skill 标为待建 ④ `c-cleanup` 两条不存在脚本 ⑤ `story-setup` 两个不存在生成脚本 ⑥ `wps-knowledgebase` 引用文件缺失声明（该 skill 仅剩 SKILL.md）。两个 commit，`[GATE:mirror-pass]` |
| 2.x | 死链剩余 | ⬜ 待做 | `A-get-memory`(trace_view.py + wf_*.ps1，5 处)、`openclaw-fenjue-weekly:73` 死门禁、`openclaw-task-supervision` Qoder 通道、`fenjue-routing-health-check` VERSION_LOCK.part2/3/4、`chaoshi-image-optimization` ffmpeg 版本路径、`hook-analyzer`/`report-generator` 共同上游 |

**本轮跑通的执行链路（可复用模板）**：
```
① rule_editor.py show --file <f> --lines N-M        # 改动前实测锚点
② rule_editor.py replace ... --dry-run              # 预览命中（须=1）
③ rule_editor.py replace ... --no-commit            # 落盘+自动备份+[verify] PASS
④ rule_editor.py commit --file A --file B --desc "" --fix-mirror   # 单次收口（镜像拦截自动修复）
⑤ check-skill-mirror.ps1 → [GATE:mirror-pass]       # 验证
```

## 📦 历史节已迁出（r58 体量治理 VOL-D908D）

> 本文件原有 11 个历史/阶段详情节 **原样**（逐字节）迁至 `memory/todo-history.part1.md`，此处只留本指针。
> 迁移动作与行守恒由 `05-exec/r58_todo_shell_slim.py` 机器把关（丢失原文行==0 且 无法归因新增行==0 才落盘）。
> 触发迁出的判据：本文件每轮注入 31,685B > `root_doc_max` 16,384B（取值 `python <handoff.py> volume <项目根>`）。
> 禁按「让 volume 变绿」反向操作：本件只搬不移除，任何一行在历史卷里找不到即为事故（R247）。

> ⚠️ **校正注（r58，2026-09-26，R241 只加注不改写）**：上方「六阶段状态总表」与历史卷里的
> 「阶段2 🚧 进行中 / 阶段3 ⬜ / 阶段4 ⬜」是 **2026-09-14~09-22 时点状态**，与当前实况不符。
> 当前实况（取值 `python 05-exec/run_gates.py` + `python <handoff.py> status <项目根>`）：
> 阶段 0-4 均已交付（见 `memory/05-feature-status.md`），阶段5 工作流专项进行中；
> 本文件定位是**索引非入口**，跨会话唯一入口 = `memory/07-next-steps.md`。

