# 跟版差异（只读）· obra/superpowers 的 5 件本地 skill · r264

> 目的：给 R263-2（跟版队列）的**头部同源组**产出可执行依据。**全程只读**：未写 D:/global_skills。
> 上游 = `obra/superpowers` @ `v7.0.1`（来源 `gh releases/latest`）；本地版本全 `1.3.0`。
>
> **产出方式如实说明**：本件由子代理产出 JSON 后在生成 md 那一步失败（#44⑦ 明确失败）；**Lead 独立复验其读数后**
> 补齐守恒字段与本 md。复验方式 = 用 `gh api` 直取上游 @v7.0.1 的 `skills/<slug>` 目录清单与本地目录逐个比对。
> 若我的复验与它冲突，以我这一侧为准（#44⑥ 两份冲突不取折中）—— 本次两侧一致。

## 1. 判据说清：两种「跟版」方式后果不同（不许笼统说「同步」）

5 件**全部** `only_upstream = 0`：上游**没有任何一个本地缺失的文件**。差异方向是「本地多出文件」+「同名文件字节不同」。

- **只覆盖同名文件** ⇒ 不会删本地独有件；但同名件的上游版本会顶掉本地版本（各件被覆盖的文件见 §3 表）。
- **整目录镜像上游** ⇒ **会删掉本地独有文件**（`.upstream` / `LICENSE` / `NOTICE` / 本地 `references/*` / 本地提示词）。

⇒ 换装方案必须先作答「用哪种同步语义」，这是 §3 的覆盖清单存在的理由。

## 2. 逐件文件级差异（面 = 5 件；分母 = 每件的本地/上游文件集合）

| slug | 本地/上游版本 | only_local | only_upstream | 字节不同 | 文件级完全一致 |
|---|---|---|---|---|---|
| `brainstorming` | 1.3.0 → v7.0.1 | 5 | 0 | **7** | no |
| `subagent-driven-development` | 1.3.0 → v7.0.1 | **11** | 0 | 1 | no |
| `test-driven-development` | 1.3.0 → v7.0.1 | 6 | 0 | 1 | no |
| `verification-before-completion` | 1.3.0 → v7.0.1 | 3 | 0 | 1 | no |
| `writing-plans` | 1.3.0 → v7.0.1 | 4 | 0 | 1 | no |

取值：`python -c` 读 `06-benchmark/r264_superpowers_follow_version_diff.json` 的 `rows[].only_local/only_upstream/size_diff` 长度；
同件 `conservation.rows == 5`、`unavailable_n == 0`、`rows_fully_identical == []`。

## 3. 覆盖清单与回滚（逐件具名，数字取自 JSON `overwrite_risk`）

| slug | 会被上游顶掉的同名文件 | 本地独有（镜像方式会删） |
|---|---|---|
| `brainstorming` | `SKILL.md`、`builder-check-prompt.md`、`scripts/frame-template.html`、`scripts/helper.js` | `.upstream`、`LICENSE`、`NOTICE`、`references/upstream-superpowers-v7.md`、`spec-document-reviewer-prompt.md` |
| `subagent-driven-development` | `SKILL.md`、`scripts/task-done`、`scripts/task-start` | `.upstream`、`LICENSE`、`NOTICE`、`references/anti-rationalization.md`、`references/context-economy.md`、`references/execution-flow.md`（共 11 项） |
| `test-driven-development` | `SKILL.md`、`writing-good-tests.md` | `.upstream`、`LICENSE`、`NOTICE`、`references/upstream-agent-skills-tdd.md`、`references/upstream-agent-skills-tdd-part2.md`、`testing-anti-patterns.md` |
| `verification-before-completion` | `SKILL.md` | `.upstream`、`LICENSE`、`NOTICE` |
| `writing-plans` | `SKILL.md` | `.upstream`、`LICENSE`、`NOTICE`、`plan-document-reviewer-prompt.md` |

回滚前提（实测，非推定）：`git -C D:/global_skills rev-parse HEAD` = `8e358806a369be65a4270c321c3fe7f9213cffdf`
⇒ 受管根是 git 仓库 ⇒ 文件级回滚可用（`git -C D:/global_skills checkout -- <路径>`），另有逐件回滚说明见 JSON `rows[].rollback_note`。
取值：`python -c` 读同件的 `git_facts` 与 `rows[].rollback_note`。

## 4. 判据自证（含负控）

- 正常位：`unavailable_n = 0`、`rows = 5`、`rows_fully_identical = []`（无一件「完全一致」⇒ 5 件都真存在差异，没有被静默跳过的件）。
- **负控（brief 要求，已实测）**：把 `brainstorming` 的本地目录指向不存在的路径（`D:/global_skills/brainstorming__DOES_NOT_EXIST_NEGCTL`）
  ⇒ 观测 `state = UNVERIFIED`（原因码 `LOCAL_DIR_MISSING`），**不得静默当成「无差异」**。
- 复跑：`python _temp/r264_follow_version_diff.py --negctl brainstorming _temp/r264_negctl.json`（负控）+ 同脚本无参跑正常位。
每件另有 `rows[].evidence_cmd`（逐条可复跑）。

## 5. 结论（本件不作换装决定）

- 5 件在 r264 语义分类里全部是 **SAME_LINEAGE**（分类面：47/55 件同源），版本落后为真：本地 1.3.0 vs 上游 v7.0.1。
- 落地形态需先裁（覆盖同名 vs 镜像目录），且要保留本地独有件（LICENSE/NOTICE 与本地上游留档 references）。
- 执行转入 R263-2：写面必须走 `rule_editor`（红线 2）+ 备份 + 三门禁（红线 5），**本件不做任何写入**。

