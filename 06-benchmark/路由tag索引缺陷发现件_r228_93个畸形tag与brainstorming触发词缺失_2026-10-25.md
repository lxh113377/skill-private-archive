# 路由 Tag 索引缺陷发现件 r228：469 个 tag 里 93 个是「整行散文」，含要求的 7 条 REAL_MISS 之一

> 用途：要求 6「质量提升」剩余缺口的**根因发现**（只报不改）。
> 归属：产物与生成器都在**焚诀仓**（`D:\...\焚诀\eval\`），非本仓；本仓红线 6 定「焚诀 eval 只读不改」⇒ 本件只登记，不代改。
> 所有数字附取值命令（±12 行内可复现）。

## 1. 发现（一句话）

路由的 L0.5「Tag 精确过滤」层（会**短路** BGE 语义召回）所读的倒排索引 `eval/skill_tags.json` 里，
**469 个 tag 中有 93 个不是触发词，而是整行散文**（含 `description: …` 原文、`Step 0.8 …` 等）；
这些畸形 tag 覆盖 **64 个技能**。它们既无法在真实问句里被精确命中，又占用了 tag 面。

> 取值：`python -c` 读 `焚诀/eval/skill_tags.json`，取 `index` 的键；
> 判畸形 = 键首匹配 `^\s*(description|触发词|name|title)\s*[:：]` 或键长 > 40；再并集其值域得到受影响技能数。

## 2. 根因（钉到 file:line，不猜）

生成器 `焚诀/eval/build_skill_tags.py` 的 `extract_triggers_from_skill_md()`：

```python
L49:            for line in fm.split('\n'):
L50:                if 'trigger' in line.lower() or '触发' in line:
L51:                    triggers.append(line.strip())      # ← 整行入库，未做字段/长度约束
```

⇒ frontmatter 里**任何**含「触发」二字的行被**整行**当成触发词。而 skill 的 description 常在同一行里写
「触发词：…」，于是那一整段 `description: 技能全生命周期唯一总管——…` 变成了一个 tag。

同函数 L54-64 的正文扫描**未排除 frontmatter**，因此同一段会被再切一次，产生 `触发词：提示词整合、…` 这类碎片 tag。

> 实测样例（均为 tag 键原文，非我改写）：
> · `description: 技能全生命周期唯一总管——增/删/改/合并/上架/四端同步/…` → `A-skill-manager`（1 技能）
> · `description: 音频交付流水线（语音旁白 / 主题音乐 / 可选 MP4）—…` → `audio-deliverable-pipeline`
> · `description: 任务后经验反哺引擎。四维度反思+…` → `A-get-memory`
> · `Step 0.8 阶段边界动态重评估门禁 + 非首轮快速重加载协议（每轮…` → `A-memory-start`
> · `*.json。禁直改派生件；禁 scan_skills 全量重生（冲 triggers）。` → `A-skill-manager`

## 3. 与要求 6 剩余缺口的关系（一处已证，一处待归属方核）

7 条 REAL_MISS 里，**brainstorming 那条已被本件解释**：

| 项 | 实测 |
|---|---|
| 问句 | 「灵感枯竭帮我发散一波点子」（期望 brainstorming，实得 story）|
| 该件自己声明的触发词 | `头脑风暴、发散点子、灵感枯竭、创意激荡、思路发散、来点想法、brainstorm、ideation`（**就在其 SKILL.md description 原文里**）|
| 索引里指向它的 tag | `Figma / 设计 / UI / 前端 / SVG / shadcn / 落地页 / 图标`（8 个，**全是设计类，无一个来自它自己的触发词**）|
| `头脑风暴` tag | **存在**，但映射到 14 个技能、**独独不含 brainstorming** |

⇒ 该件的**已声明触发词一个都没进索引**，索引给它的反而是设计域词；Tag 层无法短路，只能落到 BGE，
而 BGE 在「点子/发散」上选了 story。**这不是过拟合机会，是索引缺陷**：修它只需让索引收进该件
自己已声明的触发词，不需要塞任何测试集语句。

⚠️ 未证部分（如实标注，不猜）：`头脑风暴` 这个 tag 的映射表来自 `build_skill_tags.py` 的哪个来源段
（`_meta.sources` 记三个来源：CONTEXT_SKILL_MAP / SKILL.md triggers / domain_tags），本件**未逐源定位**，
留归属方（焚诀会话）核实。本件只断言「已观测到该 tag 不含 brainstorming」这一事实。

## 4. 为什么不在本仓改（边界的理由）

| 项 | 依据 |
|---|---|
| 产物 `焚诀/eval/skill_tags.json` 是**生成件** | 由 `build_skill_tags.py` 写出（L114 `out_path = … 'skill_tags.json'`），手改会下次重生成即被冲掉 |
| 生成器在焚诀仓 | 本仓 `memory/AGENTS.md` 红线 6：「焚诀 `eval/` 只读调用不改」|
| 跨仓改动会碰别人在途面 | R269：不擅动他人在途文件 |

⇒ 正确的动作是**把根因钉到 file:line 并登记归属方**（本件），而不是代改他人仓的生成件。

## 5. 建议的最小修复（供归属方采纳，非本仓执行）

| # | 建议 | 理由 |
|---|---|---|
| 1 | L49-51 的整行入库加约束：只取 `triggers:` / `触发词:` 键的**值**，并对值做长度上限（如 ≤20 字符）| 直接消掉 93 个畸形 tag 中的大多数 |
| 2 | L54 的正文扫描**排除 frontmatter 段** | 消掉同段被二次切分产生的碎片 tag |
| 3 | 重建后复核：畸形 tag 数应显著下降；`头脑风暴` 应含 `brainstorming` | 可复算的验收 |

> 建议命令（归属方侧，本仓未执行）：`python eval/build_skill_tags.py` 后按本文 §1 的判畸形口径复算计数。

## 6. 与要求 6 的关系（口径不变，不夸大）

本件**不改变**要求 6 的结论：口径 C 仍算术不可达（需 114.8 > 评测上限 95.2），口径 B 仍 −41.7% 达标。
它的价值是把「剩余 7 条 REAL_MISS」从「路由就是不行」细化为**可定位、可修、且修法不过拟合**的具体缺陷，
并给出了该修法**在本仓之外**的正确归属。
