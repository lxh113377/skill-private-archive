# r299 · 声明仓并入候选池的改造取证（R296-4）· 需求 2 与需求 3 之间那条断链的第一手读数

> 本件只做取证与设计，**不改 r114 本体**（改本体的连带面太大，见第 5 节）。
> 判据：python -B _repro/r299a/r299_declared_inject.py（末行见第 1 节，四腿全 PASS，rc=0）

## 1. 结论（已实测）

| 读数 | 值 | 取值命令 |
|---|---|---|
| 有 .upstream 声明的行 | 55（矩阵 191 行中） | python _repro/r299a/allrepos.py |
| 声明的**不同仓**数 | 31 | 同上 |
| 多仓侧车（一行以上 owner/repo） | 5 件 | 同上（末段列出） |
| 采集到树并判态的（本件×声明仓）对 | 62 | python -B _repro/r299a/r299_declared_inject.py |
| lineage（声明能落地 = 确是我们的上游） | 49 对 | 同上 |
| invalid（声明失效：路径与 slug 目录都不落地） | 13 对 / 7 件 | 同上 |
| tree 不可得 | 0（补采 6 仓后清零） | 同上 |
| **进五维打分的对数** | **62/62** | 同上 scored_with_dims |
| 翻档面（invalid 且现行 NO_OS_CANDIDATE） | **0** | 同上 flip |
| 四腿 | legA / legB / legC / legD 全 PASS | 同上 |

两条最要紧的解释：
- **需求 3 的缺口可以量化闭合**：r298 实测 declared_upstream_in_face 在 pad_only 13 件上 0/13，
  本轮把这 31 个声明仓**全部真量了一遍**（backfill 两批共 18 仓、api_calls 36、errors 0），
  62/62 对都拿到行内五维（例：awesome-llm-apps = fc3/eff3/compat5/docs3/community5，total 19，
  stars 142977、pushed 2026-10-22、Apache-2.0）⇒「已知上游是谁却没评估过它」这句话现在有反证了。
- **需求 2 的档位不因它改变**：flip=0 说明注入声明仓**不会**把任何 NO_OS_CANDIDATE 翻成有替代，
  也不会把 MATCHED 拉下来。它的价值是「把上游纳入打分面」而不是「改判替代是否存在」⇒
  这正好支持 lineage 不得计入 skill_n 的裁定（否则就是把上游当替代凑数）。

## 2. 三种语义的实测可分性（腿逐字输出）

判据本体 _repro/r299a/r299_declared_inject.py 的 classify()：
- **① lineage** = 声明能在该仓树里落地：声明 path 命中（path_hit）**或** 树中有「目录段=slug 变体」的
  SKILL.md（slug_hits）**或** 整仓即本件（根级 SKILL.md + 仓名含 slug）。三态共同点：
  counts_toward_skill_n = False。
- **③ invalid** = 仓可测、树完整未截断，且声明路径与 slug 目录**都**落不到 ⇒ 声明失效。
  实测例：kepano/defuddle 与 microsoft/playwright-mcp 全树 **0** 个 SKILL.md（而 defuddle/dogfood
  声明的正是它们）；gastownhall/beads 有 3 个但没有 taskflow 同名路径。
- **② other_source** 本件按设计不产（他源同名件由矩阵候选面负责）；判别边界：①②的分界是
  「该仓是否出现在本件的 .upstream 里」，不看描述相似度 —— 描述相似会放宽成假绿。

四腿（负向对照，实测逐字）：
- legA（防乐观）：采集件里没有该仓 ⇒ unmeasured，不得被下游读成「无替代」。PASS
- legB（防恒判失效）：awesome-llm-apps 的 agent_skills/commit-archaeologist/SKILL.md 必判 lineage，
  且带五维、counts_toward_skill_n=False。PASS。sha a80214bea587 —— 与 r298 我用 gh api 独立测得的
  sha **逐字相同**（两条不同通路对上同一 sha = 本轮最硬的一次互证）。
- legC（防「只看 slug 目录」）：data-analysis 声明 K-Dense-AI/scientific-agent-skills +
  path: skills/exploratory-data-analysis ⇒ 声明路径命中=True、slug命中=False，必须判 lineage。PASS。
- legD（双向，防我自己刚引入的放宽）：
  D1 正向 html-ppt 声明 lewislulu/html-ppt-skill（全树唯一 SKILL.md 在根级、仓名含 slug）⇒ 必须 lineage。PASS。
  D2 反向 web-access 声明 Panniantong/Agent-Reach（全树也唯一 1 个 SKILL.md，但那是**别人的另一个技能**）
  ⇒ 必须仍判 invalid。PASS。

## 3. 本轮我自己造的三个缺陷（全部自查发现，全部留证据不删）

① **v1 不看 path: 子路径、且只取第一个声明仓**。后果实测：12 行被判 invalid，其中 5 行是误判
   （coding-agent、data-analysis、diagram-maker、hyperframes-media、story-scan 全因侧车写的是
   path: 子目录、目录名与本地 slug 不等）；另外 5 件多仓侧车的第二/三/四个仓**完全没进判定**。
   证据保留为 _repro/r299a/r299_inject_result_v1_pathblind.json（不删，作为「判据先错后对」的对照）。
   v1→v2 翻正 = 5 对（cmp 输出逐条列出）。
② **v1 用 r114 缓存的计数字段当路径证据** ⇒ 把「看不见路径」当成「路径不存在」，给 33 行判了
   invalid。这正是本仓反复登记的「把取不到写成结论」（R247）。修法：真采一次树（collect.py，
   gh 直连 argv 不经 shell），取不到就显式 unmeasured。
   同族小错三条：采集器第 1 批输入取自矩阵行的 declared_upstream_repo（只有第一个仓）⇒ 6 个声明仓
   没采到，补采后 unmeasured 清零；backfill 里我写了取一个不存在的字段 ⇒ KeyError，删掉（采集件的
   键本身就是 repo 名）；两次 bash 采集器全军覆没（CRLF 让 gh 拿到带回车的 URL、空 heredoc 拉起
   交互式解释器）⇒ 改 Python subprocess 走 argv 列表，从结构上消灭这一类。
③ **我差点引入一个新的假绿**：腿 D 设计时我原打算把「全树只有 1 个 SKILL.md」也算根级命中。
   自查立刻发现它会把 web-access → Panniantong/Agent-Reach（唯一 SKILL.md 是 Agent-Reach 自己的）
   洗成 lineage ⇒ 收窄为「只认仓名含 slug」，并加 D2 反向腿把这个风险钉成可复算断言。
   ⇒ 教训固化：**放宽判据的每一条都要配一条反向腿**，否则放宽是单向的、只有收益没有代价，
   而这种改动看起来永远是对的。

## 4. 顺带挖出关于我自己落地件的一条事实

security-audit（我 r291 换装、r298 修可移植性的那件）的 .upstream 声明 trailofbits/skills，
但该仓 97 个 SKILL.md 里**没有** security-audit 同名路径，侧车也没写 path: ⇒ 本轮判 invalid（声明失效）。
这不是判据错：它说明我的声明只到「上游容器仓」这一级，没有可核对的落点。处置登记为待办：
要么补 path:（需先人读确认对应哪个 plugin），要么在侧车里注明「本件系多源合成、无单一同名上游」。
不擅改（改 .upstream 会影响 r291_req2_compliance 的判定面，且属受管根落地动作，须走 rule_editor 单独一单）。

## 5. 改本体的连带面（为什么不在这轮动 r114）

r299c 那条下游审计还在跑（无交付前我不代写），但从我自己实读的 r114 结构看，最小改动点至少 4 处，
且有一处会直接改档位语义：
- L1037 之后：池里注入声明仓（注意 pool 以 full_name 为键、L1042-1044 按 stars 取优 ⇒ 注入不能覆盖既有同名条目）
- L1050-1062 fam_pool 构造：按 slug 定向注入，不得污染全局族池
- L1209 skill_n 与 L1233-1248 裁决链：lineage 必须**不进** skill_n（本件已证明该裁定可行）
- L1216-1217 _up/_up_in_face：现在「一态包三条」，须拆成 lineage / invalid / unmeasured 三个字段
外加 r291_req2_compliance.py 的 rel==skill 判达标面（若新增档位名，那行会被污染 —— r299c 正在量化）。

## 6. 下一步（按可验收顺序）

1. 收 r299b / r299c 两条臂（判据落盘 + 收尾消息双前提满足后我独立复跑）。
2. 把根级单件仓（gstack、frontend-slides、html-ppt）的 lineage 结论回填到 04-plan 的巡检判据描述里。
3. 按第 5 节的 4 处最小改动动 r114 本体 + 配夹具腿（注入不存在的声明仓 ⇒ 必判 unmeasured；
   注入真实 path 声明 ⇒ 必判 lineage），改后须复算现行 191 行档位分布并逐条解释漂移。
4. security-audit 的 .upstream 落点问题单独一单（走 rule_editor）。
