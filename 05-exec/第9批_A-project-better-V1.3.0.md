# 第 9 批：更新 `A-project-better`（V1.2.1 → V1.3.0）

> 日期：2026-09-22　对象：`D:\global_skills\A-project-better\`（受管根）

## 一、需求

用户要求：**在制定项目优化方向之前，必须先检查任务中遗留的待办任务，并对这些未完成事项进行梳理与确认**，确保优化方向的制定基于对现有任务状态的完整了解，避免遗漏或重复处理。

## 二、方案裁定（按钮交互，用户拍板）

| 决策点 | 选项 | 用户裁定 |
|---|---|---|
| 改动范围 | 同轮拆卷 / 只加内容 / 仅拆版本历史 | **同轮拆卷**（合规，SKILL.md → ≤4KB） |
| 落地形态 | 新增独立 Step 0 / 并入 Step 1 第 5 源 / Step 0 + Step 3 双点 | **新增独立 Step 0** |
| 收尾范围 | 全链路 / 改源+镜像 / 只改源 | **全链路** |
| noise 违规处置 | 迁 GM `_trash` / 迁焚诀 `_trash` / 保留登记 | **迁 GM 的 `_trash`** |

## 三、改动清单（实测字节）

| 文件 | 字节 | 说明 |
|---|---|---|
| `A-project-better/SKILL.md` | 12.79KB → **3,913B** | 七步骨架 + 三条硬线 + 分卷索引；`version: 1.3.0` |
| `A-project-better/references/workflow.md` | **10,991B** | 新增：Step 0~6 完整细则 |
| `A-project-better/references/rules.md` | **3,689B** | 新增：执行属性判定表 + 反模式 + 自检清单 + 不要做的事 |
| `A-project-better/references/version-history.md` | **2,640B** | 新增：完整版本历史（V1.0.0~V1.3.0） |

## 四、Step 0 设计要点（本次核心交付）

**Step 0「遗留待办盘点」= 强制前置门禁**

1. **6 类采集源**：`memory/07-next-steps.md`（含 `partN` 分卷）/ 项目根 `TODO.md`·`TASKS.md`·`ROADMAP.md` / `memory/05-feature-status.md` 的 🚧进行中·📋计划中 / **上次本 skill 产出的「待确认（未执行）」区** / 对话口述 / 会话内 todo 清单
2. **逐条归一化 + 实测核验**：每条落一行台账（来源 file:line / 待办原文 / 声明状态 / 实测状态 / 是否仍有效）；疑似已完成**必须实测**（R240）；三态 = 仍有效 / 已完成（附证据）/ 已失效（附原因）；已完成与失效项**只加注不改写**（R241）
3. **按钮确认归类**：`AskUserQuestion` 呈现三态归类结果待确认；**未获确认不得进入 Step 1**；正文纯文字问句不算确认
4. **输出「遗留待办台账」= Step 2/3 唯一基线**，三条输出契约：
   - **不遗漏**：台账中"仍有效"的 P0 项，Step 3 清单必须有对应条目（不做须写明理由）
   - **不重复**：Step 3 新建议与台账同义时**合并为一条**并标注 `接续遗留 #N`，禁止两条同义建议
   - **可续接**：台账带编号，Step 6 回写按同编号对账（完成打勾 / 顺延 / 失效标注）

配套改动：Step 2 诊断摘要新增「遗留台账对账」行；Step 3 每条建议新增「台账对账标记」（`接续遗留 #N` / `新增` / `遗留 #N 本轮不做`）；Step 6 新增第 4 条「与台账编号级对账」，并明确 Step 4B 的「待确认（未执行）」条目原样保留带号，供下一轮 Step 0 采集源 #4 续接。

## 五、内容零丢失机械核对

用一次性 Python 脚本比对原文（备份副本）非空有效行在新文件集中的命中情况：

```
原文非空有效行=123  未命中=14
```

14 条未命中**逐条确认为有意改写**：`version: 1.2.1`（版本 bump）、`description`（新增遗留待办盘点表述）、场景/命名对位/衔接规则（精简）、Step 标题 `###`→`##`（层级统一，共 6 条）、`**执行属性（每条必填…）**`（升为 `rules.md` 标题）、「选项必须用平台按钮控件给」（增补 Step 0/Step 6 场景）、「不要在 Step 1 修改任何文件」（扩为「Step 0 / Step 1」）。

⇒ **零内容丢失**。

## 六、收尾门禁实测（全绿）

| 门禁 | 命令 | 结果 |
|---|---|---|
| 镜像 | `check-skill-mirror.ps1 -Fix` | MISSING 3 + MISMATCH 1 补齐 → **`[GATE:mirror-pass]`** |
| 派生件 | 焚诀 `build_indexes.py --apply` | 151 skill / 25 派生件 / 守恒校验 PASS |
| 真值 | 焚诀 `verify_truth_consistency.py` | **16 PASS / 0 FAIL / 0 SKIP** |
| 账实 | `disk_registry_diff.py` | **0 漏注册 / 0 回滚 / 0 幽灵** |
| 门禁协议 | `rule_editor.py gates` | **`mirror=pass noise=pass evolution=pass`** |

## 七、提交与备份

| 仓 | commit | 远端 |
|---|---|---|
| `D:\global_skills` | **`96e6108`** | origin/main 已同步（post-commit 自动 push） |
| `C:\Users\37533\.agents\skills` | **`73265c7`** | **该仓无 remote**（纯本地仓，commit 即闭环） |
| 焚诀 | **`b8df069`** | origin/master 已同步 |

备份（原 V1.2.1 全文，可 1 步还原）：
`D:\global_memory\_trash\A-project-better_20260922\SKILL.md`（13,100B）

## 八、本轮新增环境事实（长期价值）

1. **GM 的 `_bak` 是「根级合规、嵌套违规」**：`焚诀\memory_content` 是 junction → `D:\global_memory`；焚诀 `noise_lint.py` 的 `QUARANTINE_ZONES` 认根级 `_bak`，但**二级扫描（depth=2）用 `STRAY_NAME` 把子目录内的 `_bak` 判 violation**（`_trash` 不在该正则 ⇒ 不报）。⇒ **GM 备份落点应为 `D:\global_memory\_trash\<标签>_<ts>\`**；该点与 A-skill-manager 铁律 3 的「放 `_bak`」字面冲突，**冲突时以焚诀 noise 门禁为准**。
2. **`.agents\skills` 镜像仓无 remote**：`git push` 输出 usage、`branch -vv` 无 upstream ⇒ 该仓「本地 commit 即闭环」。
