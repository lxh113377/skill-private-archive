# r302b · 需求4 替换优先级（证据化序，49 行全序）

本件只做一件事：把版本态、上游五维、声明态三个可判面合成一张可复算的替换序并明写判据。
本件不裁定值不值得换装（那是拍板人的裁定）；时间节点与验证标准只给「若要做」的建议形态。

## 1. 排序判据（写死，可复算）

- **C1-state-priority** 规则：主分层只看 state：BEHIND > UNKNOWN > CURRENT > LOCAL_AHEAD（rank 0、1、2、3），分层先于分数。 ｜ 只看字段：state ｜ 理由：同一输入两次跑必须同序；主观印象不可复算，故只留可判字段。
- **C2-score-desc** 规则：同一 state 层内按 upstream_score_total 降序。 ｜ 只看字段：upstream_score_total ｜ 理由：取本体五维之和，禁自己算五维（复制口径即第二真相源）。
- **C3-pushed-desc** 规则：同层同分再按 upstream_pushed_at 降序（YYYY-MM-DD 按整数比较）。 ｜ 只看字段：upstream_pushed_at ｜ 理由：同层同分时，整仓推送更近者更可能仍在变化。
- **C4-slug-asc** 规则：仍有并列按 slug 升序，末尾以 repo 升序兜底 ⇒ 全序唯一。 ｜ 只看字段：slug, repo ｜ 理由：保证同一输入连跑两次排名完全一致（stable 判据）。
- **C5-tier-cut** 规则：T1=BEHIND 且总分>=19；T2=BEHIND 且总分<19；T3=CURRENT 或 LOCAL_AHEAD；U=UNKNOWN（单列且写原因）。 ｜ 只看字段：state, upstream_score_total ｜ 理由：19 为派发口径写死的阈值（非本件自选）；改阈值须重新裁定并留痕。
- **C6-invalid-out** 规则：声明态 kind=invalid 的对不进 49 行表，单列 invalid_rows，走改声明或补 path 另一条路。 ｜ 只看字段：kind ｜ 理由：声明失效不等于有可核对的上游。

比较器（等价伪码；末尾以 repo 升序兜底 ⇒ 全序唯一）：

```
state_rank = {BEHIND: 0, UNKNOWN: 1, CURRENT: 2, LOCAL_AHEAD: 3}
sort_key = (state_rank[state], -upstream_score_total, -as_int(upstream_pushed_at), slug, repo)
```

口径要点：五维取本体缓存件（禁自己算五维）；19 分阈值由派发口径写死；分数相同才看推送日，推送日相同才看 slug。

## 2. T1（BEHIND 且总分 >= 19）

| rank | slug | repo | state | total | fc | eff | compat | docs | community | pushed_at | local_updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | gstack | garrytan/gstack | BEHIND | 24 | 4 | 5 | 5 | 5 | 5 | 2026-10-30 | 2026-10-27 |
| 2 | coding-agent | sickn33/agentic-awesome-skills | BEHIND | 24 | 5 | 5 | 5 | 5 | 4 | 2026-10-29 | 2026-10-27 |
| 3 | figma | heygen-com/hyperframes | BEHIND | 23 | 4 | 5 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 4 | hyperframes | heygen-com/hyperframes | BEHIND | 23 | 4 | 5 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 5 | hyperframes-cli | heygen-com/hyperframes | BEHIND | 23 | 4 | 5 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 6 | hyperframes-media | heygen-com/hyperframes | BEHIND | 23 | 4 | 5 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 7 | hyperframes-registry | heygen-com/hyperframes | BEHIND | 23 | 4 | 5 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 8 | diagram-maker | github/awesome-copilot | BEHIND | 22 | 5 | 4 | 5 | 4 | 4 | 2026-10-30 | 2026-10-27 |
| 9 | brainstorming | obra/superpowers | BEHIND | 20 | 4 | 2 | 5 | 4 | 5 | 2026-10-29 | 2026-10-27 |
| 10 | rag-eval | NVIDIA-AI-Blueprints/rag | BEHIND | 20 | 3 | 5 | 5 | 5 | 2 | 2026-10-29 | 2026-10-04 |
| 11 | test-driven-development | obra/superpowers | BEHIND | 20 | 4 | 2 | 5 | 4 | 5 | 2026-10-29 | 2026-10-27 |
| 12 | verification-before-completion | obra/superpowers | BEHIND | 20 | 4 | 2 | 5 | 4 | 5 | 2026-10-29 | 2026-10-25 |
| 13 | writing-plans | obra/superpowers | BEHIND | 20 | 4 | 2 | 5 | 4 | 5 | 2026-10-29 | 2026-10-17 |
| 14 | agent-browser | vercel-labs/agent-browser | BEHIND | 19 | 4 | 3 | 5 | 3 | 4 | 2026-10-30 | 2026-10-20 |
| 15 | electron | vercel-labs/agent-browser | BEHIND | 19 | 4 | 3 | 5 | 3 | 4 | 2026-10-30 | 2026-10-20 |
| 16 | story | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 17 | story-cover | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 18 | story-deslop | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 19 | story-import | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 20 | story-long-analyze | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 21 | story-long-write | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 22 | story-review | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 23 | story-scan | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 24 | story-setup | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 25 | story-short-analyze | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 26 | story-short-write | worldwonderer/oh-story-claudecode | BEHIND | 19 | 4 | 3 | 5 | 4 | 3 | 2026-10-30 | 2026-10-27 |
| 27 | grill-me | mattpocock/skills | BEHIND | 19 | 4 | 1 | 5 | 4 | 5 | 2026-10-29 | 2026-10-27 |
| 28 | oracle | steipete/oracle | BEHIND | 19 | 2 | 5 | 5 | 4 | 3 | 2026-10-27 | 2026-10-25 |
| 29 | commit-archaeologist | Shubhamsaboo/awesome-llm-apps | BEHIND | 19 | 3 | 3 | 5 | 3 | 5 | 2026-10-22 | 2026-10-04 |
| 30 | scope-creep-detector | Shubhamsaboo/awesome-llm-apps | BEHIND | 19 | 3 | 3 | 5 | 3 | 5 | 2026-10-22 | 2026-10-04 |

## 3. T2（BEHIND 且总分 < 19）

| rank | slug | repo | state | total | fc | eff | compat | docs | community | pushed_at | local_updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 31 | ppt-master | hugohe3/ppt-master | BEHIND | 18 | 2 | 2 | 5 | 4 | 5 | 2026-10-30 | 2026-10-27 |
| 32 | find-skills | vercel-labs/skills | BEHIND | 18 | 3 | 3 | 5 | 3 | 4 | 2026-10-29 | 2026-10-20 |
| 33 | algorithmic-art | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-21 |
| 34 | brand-guidelines | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-22 |
| 35 | canvas-design | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-21 |
| 36 | doc-coauthoring | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-10-20 |
| 37 | docx | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-10-27 |
| 38 | frontend-design | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-29 |
| 39 | internal-comms | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-22 |
| 40 | pdf | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-10-27 |
| 41 | theme-factory | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-09-22 |
| 42 | xlsx | anthropics/skills | BEHIND | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-10-27 |

## 4. U（state=UNKNOWN，单列）

U 不并入 T3，也不静默丢弃；原因逐字如下（取自版本态源件的取值命令字段）。

| rank | slug | repo | state | total | pushed_at | local_updated |
|---|---|---|---|---|---|---|
| 43 | subagent-driven-development | obra/superpowers | UNKNOWN | 20 | 2026-10-29 | None |

逐字原因：

```
slug=subagent-driven-development repo=obra/superpowers
reason=LOCAL parse_version(read(D:\global_skills\subagent-driven-development\SKILL.md)) -> 1.3.0 ; fm_field(text,last_updated) -> None ; UPSTREAM load_cache()[repo__obra_superpowers].pushed_at -> 2026-10-29
cache_face=state=OK tree=OK skill_md_n=15
```

## 5. T3（CURRENT 或 LOCAL_AHEAD）

| rank | slug | repo | state | total | fc | eff | compat | docs | community | pushed_at | local_updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 44 | chart-visualization | antvis/chart-visualization-skills | CURRENT | 15 | 3 | 2 | 5 | 3 | 2 | 2026-09-22 | 2026-09-22 |
| 45 | data-analysis | K-Dense-AI/scientific-agent-skills | LOCAL_AHEAD | 25 | 5 | 5 | 5 | 5 | 5 | 2026-10-26 | 2026-10-27 |
| 46 | ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | LOCAL_AHEAD | 21 | 4 | 4 | 5 | 3 | 5 | 2026-10-26 | 2026-10-29 |
| 47 | mcp-builder | anthropics/skills | LOCAL_AHEAD | 16 | 4 | 1 | 3 | 3 | 5 | 2026-10-28 | 2026-10-30 |
| 48 | html-ppt | lewislulu/html-ppt-skill | LOCAL_AHEAD | 13 | 2 | 0 | 5 | 3 | 3 | 2026-09-14 | 2026-10-04 |
| 49 | frontend-slides | zarazhangrui/frontend-slides | LOCAL_AHEAD | 13 | 2 | 0 | 5 | 3 | 3 | 2026-06-23 | 2026-10-30 |

## 6. 计数与守恒

- 行数 pairs = 49
- tiers：T1=30 T2=12 T3=6 U=1
- state 计数：{"BEHIND": 42, "CURRENT": 1, "LOCAL_AHEAD": 5, "UNKNOWN": 1}
- 守恒：tier 计数之和 = 49；state 计数之和 = 49；行数 = 49；ok=True
- 声明失效（不进本表）：13 条
- 抽样 sha：12 条

## 7. 负向对照（两腿，实测）

### 腿 A：防排序自相矛盾（分层优先于分数）

```json
{
 "assert": "score 相同（15）时 state=BEHIND 必须比 state=CURRENT 更靠前（分层优先于分数）",
 "input_verbatim": [
  {
   "case": "synthetic equal-score, differing state",
   "state": "BEHIND",
   "score": 15,
   "tier": "T2",
   "rank": 1
  },
  {
   "case": "synthetic equal-score, differing state",
   "state": "CURRENT",
   "score": 15,
   "tier": "T3",
   "rank": 2
  }
 ],
 "pass": true,
 "real_data_gap": "数据面实测无同分对：BEHIND 总分取值 [16, 18, 19, 20, 22, 23, 24]，CURRENT 总分取值 [15]，交集为空 ⇒ 同分跨层只能用合成输入对比较器做负控。"
}
{
 "assert": "真实冲突：BEHIND 总分低者仍须排在 LOCAL_AHEAD 总分高者之前",
 "behind_row": {
  "slug": "ppt-master",
  "repo": "hugohe3/ppt-master",
  "state": "BEHIND",
  "score": 18,
  "tier": "T2",
  "rank": 31
 },
 "local_ahead_row": {
  "slug": "data-analysis",
  "repo": "K-Dense-AI/scientific-agent-skills",
  "state": "LOCAL_AHEAD",
  "score": 25,
  "tier": "T3",
  "rank": 45
 },
 "pass": true
}
{
 "assert": "U 单列且按 state 优先级排在 T3 之前",
 "unknown_rank": 43,
 "first_t3_rank": 44,
 "pass": true
}
```

### 腿 B：防静默丢行（守恒 + unknown 逐字）

```json
{
 "assert": "state 计数之和 == tiers 计数之和 == 行数（49）",
 "state_counts": {
  "BEHIND": 42,
  "CURRENT": 1,
  "LOCAL_AHEAD": 5,
  "UNKNOWN": 1
 },
 "tier_counts": {
  "T1": 30,
  "T2": 12,
  "T3": 6,
  "U": 1
 },
 "rows_n": 49,
 "pass": true,
 "unknown_rows_verbatim": [
  {
   "slug": "subagent-driven-development",
   "repo": "obra/superpowers",
   "state": "UNKNOWN",
   "score_total": 20,
   "tier": "U",
   "rank": 43,
   "cache_face": "state=OK tree=OK skill_md_n=15",
   "reason_verbatim": "LOCAL parse_version(read(D:\\global_skills\\subagent-driven-development\\SKILL.md)) -> 1.3.0 ; fm_field(text,last_updated) -> None ; UPSTREAM load_cache()[repo__obra_superpowers].pushed_at -> 2026-10-29"
  }
 ]
}
```

## 8. 这一层回答不了什么（前置缺口，具名不掩盖）

- 版本态比的是「本地件最后更新日」对「整个上游仓最后推送日」⇒ 它不回答「那个同名 SKILL.md 内容变了没有」。
- 要回答内容是否变，需要「本地吸收时该同名件的 sha」作基准；盘上没有这个基准 ⇒ 本表只能判版本面落后，不能判内容漂移。
- 12 对抽样里已有上游 sha：只能证明「上游那个文件当前是这个 sha」，不能证明「它变过」。
- 五维取自本体缓存快照：community 维含推送新鲜度，缓存生成早于最新推送的仓，分数可能偏低 ⇒ 分数是快照读数，不是实时值。

## 9. 声明失效的对（单列，另行处理）

这些对不满足「有可核对的上游」，故不进 49 行表；处理路径是改声明或补 path，不是换装。

| slug | repo | declared_path | tree_skill_md_n | declared_matrix | next_route |
|---|---|---|---|---|---|
| browser-cdp | ChromeDevTools/chrome-devtools-mcp | None | 7 | ChromeDevTools/chrome-devtools-mcp | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| browser-cdp | vercel-labs/agent-browser | None | 11 | ChromeDevTools/chrome-devtools-mcp | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| defuddle | adbar/trafilatura | None | 0 | kepano/defuddle | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| defuddle | kepano/defuddle | None | 0 | kepano/defuddle | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| dogfood | microsoft/playwright-mcp | None | 0 | microsoft/playwright-mcp | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| dogfood | web-infra-dev/midscene | None | 0 | microsoft/playwright-mcp | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| electron | microsoft/playwright | skill-data/electron | 10 | vercel-labs/agent-browser | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| security-audit | trailofbits/skills | None | 97 | trailofbits/skills | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| taskflow | gastownhall/beads | None | 3 | gastownhall/beads | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| web-access | D4Vinci/Scrapling | None | 1 | Panniantong/Agent-Reach | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| web-access | Panniantong/Agent-Reach | None | 1 | Panniantong/Agent-Reach | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| web-access | firecrawl/firecrawl | None | 5 | Panniantong/Agent-Reach | 改声明（声明路径已失效）或补 path（声明面缺 path） |
| web-access | unclecode/crawl4ai | None | 0 | Panniantong/Agent-Reach | 改声明（声明路径已失效）或补 path（声明面缺 path） |

## 10. 时间节点与验证标准的建议（若要做；本件不代裁）

前提：先补「吸收时基准 sha」，否则任何「内容变了」的结论都不可判（缺口已在第 8 节具名）。

若要做，建议的时间节点形态（不是排期承诺）：
1) 先做 T1 抽样面的上游当前 sha 核对（12 对可直接对），通过后再补基准 sha；
2) 基准补齐后做同名件内容级比对，得到「真变化」集合；
3) 按比对结果分批换装，一批一验，批间留回退点；
4) T2 与 T3 只做巡检式核对；U 单独挂账直到能判。

若要做，验证标准应是什么（可判、非主观）：
- 版本面：换装后本地标注版本 == 上游当前标注版本（限同名件）。
- 内容面：同名件内容哈希 == 上游当前哈希；没有基准时只能记当前哈希，不能判变化。
- 行为面：该件自带的判据命令仍绿。
- 系统面：镜像一致、噪声、进化 三门禁仍绿，注册表对账三类全 0。

回滚预案应是什么（形态）：
- 换装前对受影响件做文件级快照；失败按批整体回滚。
- 单件级回滚覆盖不到拓扑改动时，必须用文件级快照而不是对象级。

以上只是「若要做」的标准形态；值不值得换装由拍板人裁定。

## 11. 抽样 sha（12）

| slug | repo | path | sha |
|---|---|---|---|
| agent-browser | vercel-labs/agent-browser | skills/agent-browser/SKILL.md | 67e8a49ad8d8e5874b9e3a5d802df68d5e5e7d76 |
| diagram-maker | github/awesome-copilot | skills/excalidraw-diagram-generator/SKILL.md | 1a290eae1c7a164f59422e3d8811709ef3357d85 |
| electron | vercel-labs/agent-browser | skill-data/electron/SKILL.md | e4bf00e8e669e43d717e00050df320455352fa86 |
| figma | heygen-com/hyperframes | skills/figma/SKILL.md | 2a33e19bee8715a5225f6743d91a828aa8b66ea2 |
| gstack | garrytan/gstack | capy/skill/gstack/SKILL.md | 11bd23cc72e7535978675f6da3ddcf39d7720b5b |
| hyperframes | heygen-com/hyperframes | skills/hyperframes/SKILL.md | 6f4166472b0f0c6f26e4b3db6829ecf385686701 |
| hyperframes-cli | heygen-com/hyperframes | skills/hyperframes-cli/SKILL.md | 7f51bc528abc5bb4f3e9659de97332dfea9047ca |
| hyperframes-media | heygen-com/hyperframes | skills/media-use/SKILL.md | ddb316eac41a15ab54d0b3de538fd1d0f9b474fc |
| hyperframes-registry | heygen-com/hyperframes | skills/hyperframes-registry/SKILL.md | 7b1bc6a6c95c02ee03319cc8adaba7e54b020cba |
| ppt-master | hugohe3/ppt-master | skills/ppt-master/SKILL.md | 39e6c8a6ab8e1c1e18dfcbfee879d0ae31dbe4ee |
| story | worldwonderer/oh-story-claudecode | skills/story/SKILL.md | f99b794a131a8946418f73e27f24a564d8580f74 |
| story-cover | worldwonderer/oh-story-claudecode | skills/story-cover/SKILL.md | a01d8b2a6acb6b8c3822367c750303b88ee785da |

边界：这些 sha 是「上游同名件当前哈希」，不是「本地吸收时哈希」；没有吸收时基准就无法判定它是否变过。

## 12. 取值命令

```
python build_r302b.py                      # 重建 priority.json 与 report.md
python build_r302b.py --repo <repo>        # 单仓五维取值（本体缓存口径，含命中面）
python check_r302b.py                      # 守恒与稳定性，末行固定为 R302:PRIORITY 判据行
```

逐行取值命令已写进 priority.json 的 rows[].score_cmd 与 rows[].state_cmd。

