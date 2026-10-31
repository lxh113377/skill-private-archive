---
name: A-prompt-better
description: Prompt优化器 — 自动按业界最佳实践优化用户提示词。Prompt自动优化
  Prompt 优化器——加载后自动将用户发给 AI 的提示词按业界最佳实践优化润色，
  再交给 agent 执行。适用于所有需要高质量 prompt 输出的场景。
  **自动执行：被调用后立即对当前 user query 走优化流程，无需等待用户二次确认。**
  纯闲聊/问候/确认(如"执行"/"好的"/"继续")时跳过。
  NOT a general chat skill. This skill should be used when the user explicitly
  calls it or when the task involves sending prompts to external AI models
  and the user wants them optimized first.
version: 1.5.0
last_updated: 2026-10-31
triggers:
  - 优化提示词
  - prompt优化
  - 优化prompt
  - 提示词优化
  - prompt better
  - 优化措辞
  - 优化自然语言
  - 优化我的描述
  - prompt质量
  - 结构化prompt
---

# A-prompt-better — Prompt 优化器

## Purpose

接收用户需求/原始 prompt → 按 Anthropic / OpenAI 最佳实践自动优化 → 展示结果 → 执行。

核心价值：让每一个发出去的 prompt 都是结构化、高质量、抗幻觉的。

## 七步闭环衔接（R195，V1.2）

> 本 skill 是七步闭环的 ② 环节（共享规范：`D:\global_memory\prompts\workflow_seven_step.md` V1.0）。

1. 对用户原始消息走 Step 1-3 质量预判
2. Level 1 达标 → 直接进 ③（A-ask-questions）。注：门禁项 G6 已于 2026-09-28 废止，**不再声明也不需要写"跳过 G6"**
3. Level 2/3 → 展示优化前后对比 → 按优化版继续 → 进 ③
4. 不改原意；优化后的任务描述同步进任务卡「本轮目标」


### 🔴 自动执行规则（最高优先级）

**本技能被调用后，立即对当前 user query 执行优化流程，无需等待用户二次确认。**

1. 读取当前 user query（即本轮对话中的用户消息）
2. 走 Step 1（环境探测 + 入口判断）→ Step 2（歧义处理）→ Step 3（质量预判）
3. 若 Level 1（达标）→ 告知"跳过优化，直接执行"，继续执行用户原始任务
4. 若 Level 2/3 → 走 Step 4 优化所有子任务 prompt，Step 5 展示对比，Step 6 **直接执行**优化版
5. **例外跳过：** 用户 query 是纯闲聊 / 问候(如"你好") / 确认指令(如"执行"/"好的"/"继续"/"确认") → 跳过优化，直接处理

支持三种入口：
- **优化已有 prompt**：用户给了具体 prompt，需要润色加固
- **从需求生成 prompt**：用户只有需求描述，没有现成 prompt
- **多模态提示词优化**：用户需要图片/视频生成的 prompt（文生图/文生视频/图生图/图生视频/反向提取）

多模态场景吸收 promptmaster 的核心优势（字段拆解、输入等级判定、防膨胀裁剪、平台语法适配、图生图参数、反编译维度、安全校验）。

---

## 元原则：双视角对齐（优化前必走，内部思考，不展示）

好 prompt 的本质不是"写得详细"，而是**把用户的隐性心理模型翻译成 AI 可执行的显性规则**。

优化前，先站在两个角度各想一遍：

| 视角 | 核心问题 | 要挖出的东西 |
|------|---------|------------|
| 使用者视角 | "我真正想要的是什么？哪些我以为 AI 默认会懂？" | 未说出口的期望、踩过的坑、验收标准 |
| AI 执行者视角 | "拿到这个 prompt，我哪些地方必须猜？默认选择可能偏到哪？" | 歧义点、危险默认值、缺失的约束 |

### 双视角思考的具体操作

1. **使用者视角走一遍**：如果我是提需求的人——
   - 我说"做一个 XX"，我心里想象的成品长什么样？（具体到界面/交互/数据）
   - 我为什么特意强调某些点？（很可能是之前踩坑）
   - 哪些东西我没说，但我真的在乎？（安全性、易用性、打包完整性）

2. **AI 执行者视角走一遍**：如果我是执行这个任务的人——
   - 我看到 prompt 的第一反应：有哪些信息缺失？（项目名、目录、端口、框架版本）
   - 如果让我自由发挥，我会选什么默认方案？这些默认方案踩中用户雷区的概率有多大？
   - 我在哪些地方会"自以为做对了但其实做偏了"？

3. **找出错位**：把两个视角的差异列出来，这些差异就是优化要填补的坑。

### 双视角思考的输出（融入优化，不单独展示）

从双视角分析中提取的关键信息，转化为优化中的具体元素：
- 使用者的隐性期望 → `<done_criteria>` + `<verification>`
- 使用者的踩坑痕迹 → `<anti_patterns>`（禁止项）
- AI 的危险默认值 → `<constraints>` 中的反模式声明
- AI 的信息缺失 → `<context>` 补全（环境、工具、路径）
- 双方的组织方式差异 → 文件树结构

---

## Workflow

### Step 1: 环境探测 + 判断入口

#### 环境探测（轻量级，不阻断流程）

优化前花 5 秒判断：原始 prompt 最终在哪个环境执行？

| 执行环境 | 判断信号 | 优化策略 |
|---------|---------|---------|
| AI 直接执行（如 WorkBuddy） | 用户在 WB 对话中 / 提到具体工具/技能名 | 可引用内部工具；输出格式适配 WB |
| 用户手动执行 | 用户说"我拿去用" / "发给别人" / 无上下文 | 加运行说明；不引用内部工具 |
| 发送外部 API | 用户明确说"发API" / 通用 prompt | 去掉内部引用；用通用格式 |

无法判断 → 默认按"用户手动执行"优化，展示时注明"默认按手动执行优化，如需调整请告知"。

#### 入口判断

从用户消息判断属于哪种入口：

| 入口类型 | 判断条件 | 处理方式 |
|---------|---------|---------|
| 优化已有 prompt | 用户给出了明确的 prompt 文本（引号包裹/代码块/明显是发给AI的指令） | 走 Step 2-6 |
| 从需求生成 prompt | 用户描述了需求但没有给出具体 prompt | 直接按 Step 4 从零生成，跳过质量预判，展示后默认直接执行 |
| 多模态提示词 | 用户提到图片生成/视频生成/图生图/图生视频/提取提示词/平台名(MJ/SD/FLUX等) | 走多模态专项（见「多模态提示词优化专项」章节） |
| 已明确要求执行 | 用户说"优化并执行"等 | 优化后直接执行，跳过确认 |

### Step 2: 歧义处理

若原始 prompt 存在歧义，**默认列出所有可能的理解，按最优理解执行**，不反问用户：

```
你的 prompt 有以下理解方式：
1. [理解A] ← 按这个来
2. [理解B]

如果理解有误，告诉我。
```

只有在歧义导致**完全无法判断任务方向**时（如"帮我处理一下"且无上下文），才反问用户。

**原则：宁可列出来让用户纠正，也不要停下来等用户回答。**

### Step 3: 质量预判

在优化前，评估原始 prompt 质量，按三级处理：

#### Level 1 —— 达标（跳过优化）
同时满足以下 4 项：
- 角色/任务定义清晰
- 输出格式已指定
- 关键约束明确
- 表达精炼无冗余

→ 告知"prompt 已达高质量标准，无需优化，直接执行"。

#### Level 2 —— 勉强（轻量优化）
满足 2-3 项，但表达基本通顺，核心意图清晰。

→ **只补缺失项，不重写结构**。例如：角色已明确但输出格式未指定 → 只加 `<output_format>` 标签，其余保持原样。

#### Level 3 —— 不及格（完整重构）
满足 ≤1 项，或表达混乱导致意图模糊。

→ 按 Step 4 方法论完整重构。

**判断原则**：用户来找你就是觉得不够好。Level 2 和 Level 3 都进入优化流程。Level 1 才跳过。

### Step 4: 优化 Prompt

按以下方法论重写 prompt。**始终展示优化前/后的对比。**

#### 优化方法（内部判断，不展示给用户）

##### 策略选择（内部用）

根据 prompt 类型选择方法组合：

| Prompt 类型 | 结构化框架(A) | OpenAI 法则(B) | 抗退化增强(C) | 双视角特有(D) |
|------------|:-----------:|:-----------:|:-----------:|:-----------:|
| 简单任务（翻译、问答、一句话指令） | 跳过 | 仅规则5 | 跳过 | 跳过 |
| 代码生成 / 技术任务 | 必选 | 必选 | 幻觉 + 约束 | Done判据 + 禁止项 + 交付物规则 |
| 创意写作 / 内容创作 | 可选 | 规则2+4+5 | 跳过 | 跳过 |
| 数据分析 / 报告 | 必选 | 必选 | 幻觉 + 输出不稳定 | Done判据 |
| 角色扮演 / 对话 | 必选(仅role) | 规则1+5 | 跳过 | 跳过 |
| 复杂多步任务（>3个子任务） | 必选 | 全部 | 全部 | Done判据 + 禁止项 + 阶段检查点 + 上下文预算 |
| 多文件项目（>10个文件） | 必选 | 全部 | 全部 | 以上全部 + 文件树 |
| 多模态提示词（图片/视频生成） | 字段拆解 | 规则2+4+5 | 平台适配 + 安全校验 | 字段分层 + 平台语法 |

无法判断类型时默认走「代码生成」策略。

##### A. 结构化框架（Anthropic XML 风格）

将 prompt 重组为标签化结构：

```
<role>角色定义</role>
<context>背景信息</context>
<task>具体任务</task>
<constraints>约束条件</constraints>
<examples>示例（1-3个，有就加，没有不强编）</examples>
<output_format>输出格式要求</output_format>
```

规则：
- 指令和输入数据用标签隔离
- 最重要的约束放在 `</task>` 标签之前（近因效应）
- 每个标签内容精简，不堆砌
- 只有能提供高质量示例时才加 `<examples>`，不要编造不准确的示例

##### B. OpenAI 六条黄金法则

1. 任务定义放在最前面
2. 明确输出格式（JSON / markdown / 表格 / 纯文本）
3. 用 `###` 或 XML 标签做分隔
4. 提供 1-3 个高质量示例（有就加）
5. 避免说"不要 X"，改说"请 Y"（正面指令）
6. 复杂任务加 `<thinking>` 标签让模型先思考再输出

##### C. 抗退化增强

| 常见问题 | 修复策略 |
|---------|---------|
| 输出不稳定 | 固定输出格式模板，给具体结构而非模糊描述 |
| 模型忽略约束 | 约束写成 checklist 放在 prompt 末尾，重复核心要求 |
| 幻觉严重 | 加「不知道就说不知道」，要求引用来源或标注不确定部分 |
| 长上下文遗漏 | 首尾各写一次核心要求（首尾效应） |
| 指令冲突 | 明确优先级：「当 X 与 Y 冲突时，以 X 为准」 |

##### 优先级分层（多子任务时必选）

当优化后的 `<task>` 包含多个子任务时，用 [P0/P1/P2] 标记优先级：

```
<task>
[P0-核心] 必须完成，否则任务失败
[P1-增强] 尽量完成，时间不够可砍
[P2-锦上添花] 有就更好，没有也行
</task>
```

仅当子任务 >=3 且优先级明显不同时使用。简单任务（如"翻译这句话"）跳过此步。

##### 执行者验收清单（执行类任务必选）

当优化后的 prompt 是**执行类任务**（代码生成、多步操作、构建项目）时，在 prompt 末尾追加 `<verification>` 段：

```
<verification>
做完后逐条验证：
- [ ] 验证项1（如：启动无报错）
- [ ] 验证项2（如：核心功能走通）
- [ ] 验证项3（如：边界条件正确处理）
</verification>
```

创意类/分析类 prompt 跳过此步。

##### Done 判据（执行类任务必选）

验证清单告诉 AI "做完了逐条检查"，但 **Done 判据是更底层的东西——它定义"什么叫完成"**。

没有 Done 判据 = 没有终点线。使用者和 AI 对"完成"的定义从未对齐。

当优化后的 prompt 是执行类任务时，在 `<task>` 之后追加 `<done_criteria>` 段（与 `<verification>` 互补——前者是交付合约，后者是自检清单）：

```
<done_criteria>
1. [二元判据] 如：dotnet run 启动成功，浏览器访问 /Books 显示图书列表
2. [二元判据] 如：所有 CRUD 功能手动验证通过
3. [二元判据] 如：dotnet build 零错误零警告
</done_criteria>
```

判据必须是二元的是/否——"功能正常运行"不合格，"能新增一本图书并确认数据库写入"合格。

##### 禁止项（技术/执行类任务必选）

OpenAI 法则第 5 条说"避免说不要 X，改说请 Y"，这在创意类任务中成立。但**技术/执行类任务恰恰相反——禁止项比正面指令更安全**。

原因：AI 的破坏力来自它"自以为正确的默认选择"，而不是故意违反指令。正面指令说"用 SQLite"，AI 可能理解为"优先 SQLite，但 SQL Server 也行"。禁止项说"禁止 SQL Server"，没有余地。

在 `<constraints>` 段中，用以下格式列出禁止项：

```
<anti_patterns>
禁止：[AI可能选的错误方案] → 替代：[正确方案]
禁止：SQL Server / 需要安装服务器的数据库 → 必须 SQLite
禁止：密码明文存储 → 至少 SHA256
禁止：library.db 打包进 zip → 让目标机器执行迁移创建
</anti_patterns>
```

仅技术/执行类 prompt 使用。创意/分析类 prompt 仍用正面指令。

##### 文件树（多文件项目推荐）

涉及创建多个文件的代码项目时，在 `<context>` 或 `<task>` 后面画目录树。它同时解决三个问题：
- 使用者视角：知道有哪些文件 → 掌控感
- AI 视角：知道文件放哪 → 执行蓝图
- 共同价值：不存在"我以为文件在别的地方"

```
<file_structure>
project/
├── index.html           ← 入口页（说明用途）
├── Models/
│   ├── Book.cs          ← 图书模型
│   └── User.cs          ← 用户模型
├── Controllers/
│   └── BooksController.cs
└── wwwroot/
    └── css/custom.css
</file_structure>
```

文件数 >10 或需要明确模块边界时使用。简单项目（3-5 个文件）跳过。

##### 阶段化执行 + 检查点（多步任务推荐）

把一次性大盘赌拆成多次小检验。每阶段末尾写死一条验证命令，当前阶段不通过就不进入下一阶段。

```
<phases>
阶段 1：项目初始化 → 检查点：dotnet build 零错误
阶段 2：数据模型创建 → 检查点：dotnet ef migrations add 成功
阶段 3：核心 Controller → 检查点：dotnet run 后 /Books 可访问
</phases>
```

子任务 >=5 或涉及数据库迁移/多框架整合时使用。

##### 上下文预算提醒（大项目推荐）

当任务涉及 >15 个文件或代码量预估 >3000 行时，在 prompt 末尾加一条提醒，避免 AI 生成到一半内存溢出导致遗忘早期约束：

```
<context_budget>
预计 ~N 个文件。每完成一个阶段后评估上下文健康度，必要时压缩后继续。
</context_budget>
```

##### 交付物 vs 运行时产物（打包/导出类任务必选）

涉及到"打包输出"或"导出结果"时，明确列出打入和排除的文件。否则 AI 会把 bin/obj/数据库文件/临时文件一起打进去。

```
<artifact_rules>
打包内容：所有 .cs / .cshtml / .json / .css / .html / .csproj / .sln
排除内容：bin/ obj/ *.db Migrations/ node_modules/
</artifact_rules>
```

#### 优化原则

- 不改变用户原意
- 不添加用户未要求的额外任务
- 精简不冗余——每个词都服务于输出质量
- 原始 prompt 太简单时不硬套 XML（如"翻译这句话"）
- 考虑对话上下文——如果前面已经讨论过相关内容，优化时融入已有信息
- 单 prompt 场景慎用高虚构风险技法（仅当用户明确要求且目标工具真实支持时才用）：**Mixture of Experts**（单前向内的模拟多人路由）/ **Tree of Thought**（无真实并行的模拟分支）/ **Graph of Thought**（依赖多数工具里没有的外部图引擎）/ **Universal Self-Consistency**（需独立多次采样）/ 作为分层手法的 **Prompt chaining**（链越长、虚构风险越复合）——这些框架在单 prompt 里多为「表演」而非真实执行，优先用角色指派、few-shot、grounding 锚点与显式验收标准替代
<!-- r306a 逐字钉定（加法式并入，本地行零删除）| 增量 I1 | 上游 L21-27 | nidhinjs/prompt-master · SKILL.md v1.8.2 · MIT · upstream_blob_sha 742deafaf4222f9f0e9d9410e72483dad64fe716 · upstream_content_sha256 36e68cdcd62c38b2f99c2538c83fefb8c8837ea9b7eed75297fe76e45c452e75 | 证据 swap_pack.json increments[0] | 准入 r305b merge_plan.json skills[slug=A-prompt-better].files[src=SKILL.md,action=land] -->

- Prefer simpler techniques (role assignment, few-shot examples, grounding anchors, and explicit verification criteria) over complex meta-reasoning frameworks in single-prompt contexts. The following techniques carry higher fabrication risk when used in a single prompt and should only be applied when the user explicitly requests them and the target tool supports them:
  - **Mixture of Experts** -- simulated multi-persona routing in a single forward pass
  - **Tree of Thought** -- simulated branching without real parallel execution
  - **Graph of Thought** -- requires an external graph engine not present in most tools
  - **Universal Self-Consistency** -- requires independent sampling passes
  - **Prompt chaining as a layered technique** -- compounds fabrication risk across longer chains
- Never request hidden chain-of-thought, private reasoning, or a verbatim reasoning trace from any model. Ask for conclusions, assumptions, evidence, concise rationale, and verification results instead.


### Memory Block 位置约束

当用户请求引用既往工作、决定或会话历史时，把该上下文块**前置**到生成的 prompt，并确保它落在前 30% 内——尾部内容在目标模型的注意力衰减中最易丢失（ Place it in the first 30% so it survives attention decay ）。
<!-- r306a 逐字钉定（加法式并入，本地行零删除）| 增量 I2 | 上游 L440-450 | nidhinjs/prompt-master · SKILL.md v1.8.2 · MIT · upstream_blob_sha 742deafaf4222f9f0e9d9410e72483dad64fe716 · upstream_content_sha256 36e68cdcd62c38b2f99c2538c83fefb8c8837ea9b7eed75297fe76e45c452e75 | 证据 swap_pack.json increments[1] | 准入 r305b merge_plan.json skills[slug=A-prompt-better].files[src=SKILL.md,action=land] -->

### Memory Block

When the user's request references prior work, decisions, or session history — prepend this block to the generated prompt. Place it in the first 30% of the prompt so it survives attention decay in the target model.

```
## Context (carry forward)
- Stack and tool decisions established
- Architecture choices locked
- Constraints from prior turns
- What was tried and failed
```


### Step 5: 展示对比

用以下格式展示：

```
## 优化前
[原始 prompt / 需求描述]

## 优化后
[优化版 prompt，用代码块包裹方便复制]

## 核心改动
1. [最重要的改动 + 理由]
2. [次重要的改动 + 理由]
3. [再次之的改动 + 理由]

## 其他调整
- [调整项1]
- [调整项2]
```

核心改动不限条数，按重要性排序。用"其他调整"罗列次要改动。小改动不列。

### Step 6: 执行

**默认直接执行优化版**，除非以下情况才确认：

- 歧义处理中列出了多种理解且差异较大
- 优化对原始意图做了比较大的方向性调整
- 用户之前明确说过"优化前先让我看看"

确认话术精简：「执行优化版？（回复"改"或直接说需求）」


---

## 多模态提示词优化专项

当用户的 prompt 涉及图片生成、视频生成、图生图、图生视频时，触发本专项。本专项吸收 promptmaster 的核心优势，补全多模态领域的处理能力。

### 触发条件

从用户消息判断是否属于多模态提示词任务：

| 触发信号 | 任务类型 |
|---------|---------|
| 生成图片/画一张/文生图 | 文生图 |
| 生成视频/文生视频 | 文生视频 |
| 图生图/参考这张图 | 图生图 |
| 图生视频/让这张图动起来 | 图生视频 |
| 提取提示词/反编译/给出图片或视频 | 反向提取 |
| 给出 MJ/SD/FLUX 等平台格式 prompt | 平台语法优化 |

### 字段拆解方法论

多模态提示词的核心是把"模糊创意"拆成"平台可执行的精确字段"。按优先级分层：

#### P0 核心字段（必须有）
- **主体（Subject）**：画面/视频中的主要对象，具体描述外观、动作、表情
- **媒介（Medium）**：照片/插画/3D渲染/油画等
- **风格（Style）**：具体风格名（如"赛博朋克"、"浮世绘"），避免模糊词

#### P1 增强字段（推荐有）
- **灯光（Lighting）**：自然光/摄影棚光/霓虹/烛光等
- **构图（Composition）**：视角、景别、画面布局
- **色彩（Color）**：主色调、色彩方案
- **情绪（Mood）**：整体氛围、情感基调

#### P2 锦上添花（可选）
- **技术参数（Technical）**：镜头、光圈、渲染引擎等
- **细节（Details）**：纹理、材质、背景元素

#### 输入等级判定（激活前先判定）

根据用户输入长度和详细程度，用四级阈值控制字段激活密度：

| 等级 | 输入阈值 | 字段激活 | 说明 |
|------|---------|---------|------|
| Lv1 | ≤10 字 | 仅 P0 | 预设默认值填充缺失维度 |
| Lv2 | ≤30 字 | P0 + P1 | 适度补全，不过度堆砌 |
| Lv3 | ≤80 字 | P0 + P1 + P2 | 精准拆解，顺序排列 |
| Lv4 | >80 字 | 全部激活 | 完整拆解后走防膨胀裁剪 |

#### 智能默认值（Lv1/Lv2 时补充）

用户输入不足时用以下默认值补齐，不单独展示：

| 字段 | 默认值 |
|------|-------|
| 环境/背景 | "简洁背景，柔和光影" |
| 构图 | "中景，平视角度" |
| 灯光 | "自然光，柔和明暗" |
| 纹理 | "细腻质感" |

用户输入越详细，默认值使用越少。Lv3 以上不用默认值。

#### 防膨胀裁剪（Lv4 必走）

当输入 >80 字或提示词超过 80 组关键词时，按优先级逐层裁剪：

1. 先裁 P2 全部（技术参数/细节）
2. 再压缩 P1 为单关键词
3. 最后精简 P0 为一句话

**永不裁剪**：主体(Subject)和风格(Style)字段。

### 平台语法适配

不同平台的 prompt 格式差异巨大。优化时根据实际目标平台转换：

#### Midjourney (MJ)
```
[Subject], [Style], [Medium], [Lighting] --ar 16:9 --s 750 --v 6
```
- `--ar`：宽高比（16:9 / 1:1 / 9:16）
- `--s`：风格化强度（0-1000，默认 100）
- `--niji`：动漫风格模型（5 / 6）
- `--cfg`：遵从度（1-30，默认 7）

#### Stable Diffusion (SD)
```
正面：(masterpiece:1.2), (best quality:1.2), [Subject], [Style], [Details]
负面：NSFW, (worst quality:1.2), (low quality:1.2), blurry, noisy
```
- `(word)`：1.1倍权重；`((word))`：约1.21倍
- `[word]`：0.9倍权重
- `(word:1.5)`：精确权重

#### FLUX
自然语言描述，无需复杂权重语法。支持长提示词（>200词）。不建议用 SD 风格括号权重。

#### DALL-E 3 / GPT-4V
自然语言详细描述。不支持参数语法（`--ar` 等），所有要求写在提示词正文里。

#### 国内平台（千问/豆包/即梦/可灵/Sora）
- 中文提示词效果好于英文（平台针对中文优化）
- 不支持 MJ/SD 风格的参数语法
- 描述风格用自然语言："采用赛博朋克风格"、"仿油画质感"
- 权重符号转换规则（将 SD 风格括号转为自然语言）：
  - 单括号 `(word)` → "比较word"
  - 双括号 `((word))` → "非常word"
  - 三括号 `(((word)))` → "极其word"
  - 精确权重 `(word:1.5)` → "强调word"

### 图生图专项参数

当任务类型为图生图时，必须明确以下参数：

#### 参考类型判定

| 类型 | 说明 | ref_weight | ref_stop | redraw_scale |
|------|------|:---:|:---:|:---:|
| 风格迁移 | 保持原图画风，改变内容 | 0.3-0.5 | - | 0.7-0.9 |
| 构图保留 | 保持原图构图，改变风格/内容 | 0.8-1.0 | 90-100 | 0.3-0.5 |
| 角色一致 | 保持角色外观，替换场景/动作 | 0.6-0.8 | 60-80 | 0.5-0.7 |
| 创意混搭 | 融合参考元素与新内容 | 0.2-0.4 | - | 0.8-1.0 |
| 换背景 | 保持主体不变，改变背景 | 0.7-0.9 | - | 0.3-0.6 |
| 调色 | 保持内容不变，改变色调 | 0.5-0.7 | - | 0.2-0.4 |

#### 参数规格

| 参数 | 范围 | 默认值 | 说明 |
|------|------|:---:|------|
| ref_weight | 0.1-1.0 | 0.7 | 值越大越接近原图 |
| ref_stop | 0-100 | 80 | 值越大原图特征越早终止 |
| redraw_scale | 0-1.0 | 0.5 | 值越大变化越多 |

优化图生图 prompt 时，在输出中附带参数推荐。默认按"风格迁移"兜底。

### 反向提取（图片/视频 → 提示词）

当用户给出图片/视频，要求"提取提示词"或"反编译"时：

**图片反编译 —— 七维度分析**：
1. **主体(F-SUBJ)**：核心元素识别（人物/物体/场景）
2. **风格(F-STYL)**：风格判定（写实/二次元/油画/水彩/摄影）
3. **环境(F-ENV)**：背景环境（室内/室外/自然/建筑/抽象）
4. **构图(F-COMP)**：视角景别（俯视/仰视/平视/特写/全景）
5. **光影(F-LIGHT)**：光影氛围（暖光/冷光/逆光/柔光/硬光）
6. **配色(F-COLOR)**：配色方案（主色调/互补色/邻近色）
7. **技术(F-TECH)**：技术特征（笔触/纹理/噪点/后期痕迹）

输出时按以上维度逐项呈现，附复现建议和可选操作入口。

**视频反编译 —— 六维度分析**：
1. **动态(F-DYNAMIC)**：主体运动/环境变化/粒子效果
2. **镜头(F-LENS)**：镜头语言（推拉/摇移/跟拍/固定/航拍）
3. **转场(F-TRANS)**：转场节奏（瞬切/渐变/叠化/特效转场）
4. **节奏(F-TEMPO)**：时长感（慢节奏/匀速/快节奏/变速）
5. **风格(F-STYL)**：视觉风格（色调/光影/运镜风格）
6. **技术(F-TECH)**：技术特征（帧率风格/稳定器痕迹/特效痕迹）

#### 反编译衔接跳转

反编译输出后，提供可选操作入口：

| 选项 | 触发 | 动作 |
|------|------|------|
| 基于描述生成新图 | 用户选择 1 | 携带反编译描述，按文生图流程继续 |
| 以此为参考图生图 | 用户选择 2 | 携带原图+描述，按图生图流程继续 |
| 基于描述生成新视频 | 用户选择 1（视频） | 携带反编译描述，按文生视频流程继续 |
| 仅保存描述 | 用户选择 3 | 保存到上下文，终止流程，可随时唤醒

### RAG 历史偏好增强（可选）

从用户历史对话中提取：
- 常用风格词（如用户总说"赛博朋克"）
- 排斥元素（如用户总加"不要XX"）
- 平台偏好（如用户总用 MJ）
- 质量基准（如用户总要求"8K"、"超精细"）

提取后融入当前 prompt，不单独展示偏好来源。

### 安全校验

涉及人物生成时，自动加入安全兜底：
- 不涉及真实人物肖像——如用户要求"生成XX名人"，提示建议使用虚构人物或仅参考风格
- 不涉及敏感内容——如提示词含暴力/政治/成人内容，拒绝优化并说明原因
- 不涉及侵权——如用户要求"模仿XX画家风格"，提示建议参考风格而非直接模仿

### 教学模式（可选）

用户说"教我写提示词"或"为什么这样优化"时，开启教学模式：
1. 展示优化结果
2. 逐字段解释：为什么加这个字段？这个字段起什么作用？
3. 对比不同字段组合的效果差异
4. 给出练习建议

---


## Quick Reference

### 优化检查清单（内部用）

针对 agentic 工具的产出复核：如果优化后的 prompt 目标是会执行命令或改文件的 agent（Claude Code、Cursor、Windsurf、Cline、Swe-agent 等，或任何引用文件系统/终端/依赖/数据库的 prompt），在交付前附加一段提醒：确认 scope locks、forbidden actions 与 stop conditions，核对文件路径、目录与权限匹配真实项目。

- [ ] 双视角思考是否完成？（使用者视角 + AI 视角各走一遍）
- [ ] 是否找出了双视角的错位点？
- [ ] 环境探测是否完成？
- [ ] 入口判断正确？（优化已有 / 从需求生成 / 多模态 / 直接执行）
- [ ] 角色是否明确？
- [ ] 任务是否放在最前面？
- [ ] 输出格式是否指定？
- [ ] 负面指令是否已转为正面？（创意类）/ 禁止项是否已列出？（技术类）
- [ ] 关键约束是否在末尾重复？
- [ ] 关键约束是否同时落在生成 prompt 的前 30%（注意力衰减区外）？
- [ ] 复杂任务是否有 `<thinking>` 标签？
- [ ] 是否有防幻觉兜底？
- [ ] 高虚构风险技法是否已移除（除非用户明确要求且工具真实支持）？
- [ ] XML 标签是否正确闭合？
- [ ] 对话上下文是否已融入？
- [ ] 多子任务是否已加 [P0/P1/P2] 分层？
- [ ] 执行类任务是否已加 `<verification>` 清单？
- [ ] 执行类任务是否已加 `<done_criteria>` 判据？
- [ ] 技术/执行类任务是否已加 `<anti_patterns>` 禁止项？
- [ ] 多文件项目（>10文件）是否已画文件树？
- [ ] 多步任务（>=5阶段）是否已加阶段检查点？
- [ ] 大项目（>15文件）是否已加上下文预算提醒？
- [ ] 打包/导出类任务是否已加交付物排除规则？
- [ ] 多模态任务是否已判断触发条件？（文生图/文生视频/图生图/图生视频/反向提取）
- [ ] 多模态输入等级是否已判定？（Lv1-4，按字数阈值）
- [ ] 多模态字段拆解是否已按输入等级激活？
- [ ] Lv4 输入是否已走防膨胀裁剪？
- [ ] 图生图场景是否已判定参考类型并给出参数推荐？
- [ ] 目标平台语法是否已适配？（MJ/SD/FLUX/国内平台）
- [ ] 国内平台权重符号是否已转换为自然语言？（括号→比较/非常/极其）
- [ ] 图片反编译是否覆盖七维度？（F-SUBJ/F-STYL/F-ENV/F-COMP/F-LIGHT/F-COLOR/F-TECH）
- [ ] 视频反编译是否覆盖六维度？（F-DYNAMIC/F-LENS/F-TRANS/F-TEMPO/F-STYL/F-TECH）
- [ ] 反编译输出是否附带衔接跳转选项？
- [ ] 安全校验是否已执行？（不涉及真实人物/敏感内容/侵权）

### 不要做的事

- 不要替用户添加他没要求的内容
- 不要改变用户 prompt 的核心意图
- 不要把简单任务过度复杂化
- 不要在用户只需要一句话翻译时硬套 XML 框架
- 不要让用户确认那些显然该直接执行的情况
- 不要编造不准确的示例来填充 `<examples>` 标签
- 不要对所有 prompt 都加 [P0/P1/P2]——简单任务跳过
- 不要对所有 prompt 都加 `<verification>`——创意/分析类跳过
- 不要对所有 prompt 都加 `<anti_patterns>`——创意/分析类跳过
- 不要在技术类 prompt 中死守"正面指令"原则——禁止项更安全
- 不要跳过双视角思考直接进入优化——这是偷懒，不是高效
- 不要对多模态提示词死守 XML 框架——字段拆解 + 平台语法更接近自然语言
- 不要对文生图/文生视频 prompt 强行加 `<thinking>` 标签——创意生成不需要
- 不要在多模态提示词中遗漏平台语法——不同平台格式差异巨大，必须指定

---

<!-- r306a 逐字钉定（加法式并入，本地行零删除）| 增量 I3 | 上游 L469-473 | nidhinjs/prompt-master · SKILL.md v1.8.2 · MIT · upstream_blob_sha 742deafaf4222f9f0e9d9410e72483dad64fe716 · upstream_content_sha256 36e68cdcd62c38b2f99c2538c83fefb8c8837ea9b7eed75297fe76e45c452e75 | 证据 swap_pack.json increments[2] | 准入 r305b merge_plan.json skills[slug=A-prompt-better].files[src=SKILL.md,action=land] -->

### Agentic Output Warning

For prompts targeting agentic tools (Claude Code, Devin, Cursor, Windsurf, Cline, Bolt, SWE-agent, Manus, or anything that executes commands or edits files — mandatory for Templates G, H, M, agentic uses of N, and any prompt referencing filesystem, terminal, dependency, or database operations), append this notice:

"This prompt is for an agentic tool with real system access. Review the scope locks, forbidden actions, and stop conditions before pasting. Confirm file paths, directories, and permissions match the actual project."

<!-- r306a 逐字钉定（加法式并入，本地行零删除）| 增量 I4 | 上游 L477-489 | nidhinjs/prompt-master · SKILL.md v1.8.2 · MIT · upstream_blob_sha 742deafaf4222f9f0e9d9410e72483dad64fe716 · upstream_content_sha256 36e68cdcd62c38b2f99c2538c83fefb8c8837ea9b7eed75297fe76e45c452e75 | 证据 swap_pack.json increments[3] | 准入 r305b merge_plan.json skills[slug=A-prompt-better].files[src=SKILL.md,action=land] -->

## RECENCY ZONE — Verification and Success Lock

**Before delivering any prompt, verify:**

1. Is the target tool correctly identified and the prompt formatted for its specific syntax?
2. Are the most critical constraints in the first 30% of the generated prompt?
3. Does every instruction use the strongest signal word? MUST over should. NEVER over avoid.
4. Has every fabricated technique been removed?
5. Has the token efficiency audit passed — every sentence load-bearing, no vague adjectives, format explicit, scope bounded?
6. Would this prompt produce the right output on the first attempt?

**Success criteria**
The user pastes the prompt into their target tool. It works on the first try. Zero re-prompts needed. That is the only metric.---

## 元能力：主动自评

每次完成 prompt 优化后，快速自评（内部，不展示给用户）：

1. 优化是否实质性提升了 prompt 质量？（不是表面改格式）
2. 有没有引入新的歧义或偏差？
3. 用户如果看到结果会不会觉得"确实更好了"？
4. 优化后的 prompt 在目标执行环境中是否能正确运行？
5. 双视角分析找出的错位是否都被填补了？（最重要的自评项）

如果自评发现明显问题，修正后重新展示。

当用户明确反馈「优化效果不好」时：
- 问清楚哪里不好
- 记录为踩坑
- 更新本文档的优化方法论

## 迭代反馈

优化结果不满意？说"再改"并指出哪里不行，针对性调整，不从头重构。

## 版本历史

| 版本 | 日期 | 变更 |
| V1.5.0 | 2026-10-31 | r306a 换装补装（A 臂落地编辑清单，只加不删）：四条上游增量逐字钉定 —— I1 单 prompt 高虚构技法黑名单＋禁索取隐藏思维链（上游 L21-27）、I2 Memory Block 前 30% 注意力衰减位约束含 Context carry-forward 代码块（L440-450）、I3 Agentic Output Warning 原文（L469-473）、I4 RECENCY ZONE 交付前六问＋成功判据（L477-489）；本地独有（七步闭环 Step ② 衔接、Level 1/2/3 分流与闭合标签近因）逐字未动 |
| V1.4.0 | 2026-10-31 | 换装增量并入（nidhinjs/prompt-master @ blob 742deafa、MIT，四区 L22-27/L442/L469-470/L482）：单 prompt 高虚构技法黑名单、Memory Block 前 30% 前置、agentic 产出 scope-lock 复核、检查清单 +2 项；本地独有（七步闭环 Step ② 衔接、Level 1/2/3 分流与闭合标签近因）逐字保留 |
| V1.3.0 | 2026-08-16 | 版本号对齐修正：frontmatter version 已为 1.3.0 但版本历史缺失对应记录，补录 V1.3.0 行（R1 评估 D2 修正） |
|------|------|------|
| V1.2 | 2026-08-12 | R195：新增七步闭环 Step ② 衔接说明（Level 1 跳过→③；Level 2/3 优化后继续；引用共享规范 workflow_seven_step.md V1.0） |
| V1.1 | 2026-08-12 | 实测记录（R192）：自动执行规则在 Plan 模式下的适配生效；焚诀需求描述本身达标时正确跳过优化直接执行 |
| V1.0 | 2026-07 | 初始版本：业界最佳实践 prompt 优化 + 双视角对齐 + 多模态入口 |
