# R301C · 需求 5「版本面」—— 三层里的第一层：新鲜度面（freshness）

> 本件只答一个问题：**上游是否比本地新**（时间轴：本地 `last_updated` vs 上游 `pushed_at`）。
> **不答**「值不值得换装 / 该不该升级」—— 那是需求 4（价值/优先级裁定）的产出，本面不越界。
> 上一版（同目标件）要求 62 对全取上游正文 + 逐对比版本 + 报告，实测跑不完即死；本版缩为「先新鲜度面（零正文取数）+ 12 对上游正文抽样」。

## 1. 口径（写死，不在本件里改）

| 项 | 取值 |
|---|---|
| 判定时间轴 | `local_last_updated`（本地 SKILL.md 头部 `last_updated:`） vs `upstream_pushed_at`（上游仓 pushed_at），两者都规整为 `YYYY-MM-DD` 后字符串比较 |
| upstream 比 local 新 | **BEHIND** |
| 相同 | **CURRENT** |
| upstream 更旧 | **LOCAL_AHEAD** |
| 任一侧取不到 | **UNKNOWN**（缺数据绝不猜） |
| 版本号 `version` | 允许缺失，缺即记 `None`；**不得用 pushed_at 去补版本号**（两把尺不许混，版本号不参与 state 判定） |
| 样本 | 取 `pushed_at` 最新的 12 个 lineage 对，`gh api repos/<owner>/<repo>/contents/<path>` base64 解码取上游 SKILL.md，再用**同一个** parse_version 解析其 version；取不到 ⇒ `sampled_state=UNVERIFIED` 并抄 stderr |
| `sampled=` 定义 | 成功取回并解析的上游样本数（`sampled_state==VERIFIED`）；本次 attempted=12 |

## 2. 取数来源（全部已在盘上，只用不造）

- lineage 对清单：`自建skill优化/_repro/r299a/results/r299_inject_result.json` 里 `kind==lineage` 的行 —— 总行 62，其中 lineage **49** 行，invalid 13 行（不在本面范围）。
- 上游 `pushed_at`：`import 05-exec/r114_replacement_scan.py` 用它的 `load_cache()`，取 `repo__<key_of(repo)>` 条目（cache pack entries 414；lineage 覆盖 49/49）。
- 本地 `version` / `last_updated`：正文从 `D:/global_skills/<slug>/SKILL.md` **只读**；version 用本体 `r114_replacement_scan.parse_version`（入参 = 单个 text 串；docstring 先 print 再调用）；`last_updated` 用**已有的** `r112_provenance_scan.fm_field`（见 §8 偏差说明）。

## 3. 读数（复算命令 + 期望末行）

```
cd "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r301c"
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B check_r301c.py
```

期望末行（本次实测逐字）：

```
[R301C:FRESH] pairs=49 behind=42 current=1 local_ahead=5 unknown=1 sampled=2
```

## 4. 逐对读数（49 对 lineage）

| slug | repo | local_version | local_last_updated | upstream_pushed_at | state |
|---|---|---|---|---|---|
| agent-browser | vercel-labs/agent-browser | 3.2.0 | 2026-10-20 | 2026-10-30 | BEHIND |
| algorithmic-art | anthropics/skills | 1.0.0 | 2026-09-21 | 2026-10-28 | BEHIND |
| brainstorming | obra/superpowers | 1.2.0 | 2026-10-27 | 2026-10-29 | BEHIND |
| brand-guidelines | anthropics/skills | 1.0.0 | 2026-09-22 | 2026-10-28 | BEHIND |
| canvas-design | anthropics/skills | 1.0.0 | 2026-09-21 | 2026-10-28 | BEHIND |
| chart-visualization | antvis/chart-visualization-skills | 1.0.0 | 2026-09-22 | 2026-09-22 | CURRENT |
| coding-agent | sickn33/agentic-awesome-skills | 1.3.0 | 2026-10-27 | 2026-10-29 | BEHIND |
| commit-archaeologist | Shubhamsaboo/awesome-llm-apps | 1.0.0 | 2026-10-04 | 2026-10-22 | BEHIND |
| data-analysis | K-Dense-AI/scientific-agent-skills | 1.4.0 | 2026-10-27 | 2026-10-26 | LOCAL_AHEAD |
| diagram-maker | github/awesome-copilot | 1.2.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| doc-coauthoring | anthropics/skills | 2.0.0 | 2026-10-20 | 2026-10-28 | BEHIND |
| docx | anthropics/skills | 2.2.0 | 2026-10-27 | 2026-10-28 | BEHIND |
| electron | vercel-labs/agent-browser | 1.1.0 | 2026-10-20 | 2026-10-30 | BEHIND |
| figma | heygen-com/hyperframes | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| find-skills | vercel-labs/skills | 1.1.0 | 2026-10-20 | 2026-10-29 | BEHIND |
| frontend-design | anthropics/skills | 2.1.0 | 2026-09-29 | 2026-10-28 | BEHIND |
| frontend-slides | zarazhangrui/frontend-slides | 1.4.2 | 2026-10-30 | 2026-06-23 | LOCAL_AHEAD |
| grill-me | mattpocock/skills | 1.2.0 | 2026-10-27 | 2026-10-29 | BEHIND |
| gstack | garrytan/gstack | 1.3.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| html-ppt | lewislulu/html-ppt-skill | 1.0.0 | 2026-10-04 | 2026-09-14 | LOCAL_AHEAD |
| hyperframes | heygen-com/hyperframes | 1.7.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| hyperframes-cli | heygen-com/hyperframes | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| hyperframes-media | heygen-com/hyperframes | 1.7.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| hyperframes-registry | heygen-com/hyperframes | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| internal-comms | anthropics/skills | 1.0.0 | 2026-09-22 | 2026-10-28 | BEHIND |
| mcp-builder | anthropics/skills | 1.1.0 | 2026-10-30 | 2026-10-28 | LOCAL_AHEAD |
| oracle | steipete/oracle | 1.2.0 | 2026-10-25 | 2026-10-27 | BEHIND |
| pdf | anthropics/skills | 1.1.0 | 2026-10-27 | 2026-10-28 | BEHIND |
| ppt-master | hugohe3/ppt-master | 6.6.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| rag-eval | NVIDIA-AI-Blueprints/rag | 2.6.0 | 2026-10-04 | 2026-10-29 | BEHIND |
| scope-creep-detector | Shubhamsaboo/awesome-llm-apps | 1.0.0 | 2026-10-04 | 2026-10-22 | BEHIND |
| story | worldwonderer/oh-story-claudecode | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-cover | worldwonderer/oh-story-claudecode | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-deslop | worldwonderer/oh-story-claudecode | 1.2.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-import | worldwonderer/oh-story-claudecode | 1.3.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-long-analyze | worldwonderer/oh-story-claudecode | 1.2.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-long-write | worldwonderer/oh-story-claudecode | 1.4.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-review | worldwonderer/oh-story-claudecode | 1.5.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-scan | worldwonderer/oh-story-claudecode | 1.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-setup | worldwonderer/oh-story-claudecode | 1.6.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-short-analyze | worldwonderer/oh-story-claudecode | 3.1.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| story-short-write | worldwonderer/oh-story-claudecode | 1.3.0 | 2026-10-27 | 2026-10-30 | BEHIND |
| subagent-driven-development | obra/superpowers | 1.3.0 | null | 2026-10-29 | UNKNOWN |
| test-driven-development | obra/superpowers | 1.3.0 | 2026-10-27 | 2026-10-29 | BEHIND |
| theme-factory | anthropics/skills | 1.0.0 | 2026-09-22 | 2026-10-28 | BEHIND |
| ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | 1.6.0 | 2026-10-29 | 2026-10-26 | LOCAL_AHEAD |
| verification-before-completion | obra/superpowers | 1.7.2 | 2026-10-25 | 2026-10-29 | BEHIND |
| writing-plans | obra/superpowers | 1.0.0 | 2026-10-17 | 2026-10-29 | BEHIND |
| xlsx | anthropics/skills | 1.2.0 | 2026-10-27 | 2026-10-28 | BEHIND |

统计：BEHIND **42** · CURRENT **1** · LOCAL_AHEAD **5** · UNKNOWN **1**（总 49）。
`local_version` 缺失（None）本地件 0/49 件（按规则记 None，不补）。

非 BEHIND 的对（须逐字复核）：

- `chart-visualization` / `antvis/chart-visualization-skills` local_last_updated=`2026-09-22` upstream_pushed_at=`2026-09-22` ⇒ **CURRENT** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\chart-visualization\SKILL.md)) -> 1.0.0 ; fm_field(text,last_updated) -> 2026-09-22 ; UPSTREAM load_cache()[repo__antvis_chart_visualization_skills].pushed_at -> 2026-09-22`
- `data-analysis` / `K-Dense-AI/scientific-agent-skills` local_last_updated=`2026-10-27` upstream_pushed_at=`2026-10-26` ⇒ **LOCAL_AHEAD** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\data-analysis\SKILL.md)) -> 1.4.0 ; fm_field(text,last_updated) -> 2026-10-27 ; UPSTREAM load_cache()[repo__K_Dense_AI_scientific_agent_skills].pushed_at -> 2026-10-26`
- `frontend-slides` / `zarazhangrui/frontend-slides` local_last_updated=`2026-10-30` upstream_pushed_at=`2026-06-23` ⇒ **LOCAL_AHEAD** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\frontend-slides\SKILL.md)) -> 1.4.2 ; fm_field(text,last_updated) -> 2026-10-30 ; UPSTREAM load_cache()[repo__zarazhangrui_frontend_slides].pushed_at -> 2026-06-23`
- `html-ppt` / `lewislulu/html-ppt-skill` local_last_updated=`2026-10-04` upstream_pushed_at=`2026-09-14` ⇒ **LOCAL_AHEAD** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\html-ppt\SKILL.md)) -> 1.0.0 ; fm_field(text,last_updated) -> 2026-10-04 ; UPSTREAM load_cache()[repo__lewislulu_html_ppt_skill].pushed_at -> 2026-09-14`
- `mcp-builder` / `anthropics/skills` local_last_updated=`2026-10-30` upstream_pushed_at=`2026-10-28` ⇒ **LOCAL_AHEAD** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\mcp-builder\SKILL.md)) -> 1.1.0 ; fm_field(text,last_updated) -> 2026-10-30 ; UPSTREAM load_cache()[repo__anthropics_skills].pushed_at -> 2026-10-28`
- `subagent-driven-development` / `obra/superpowers` local_last_updated=`null` upstream_pushed_at=`2026-10-29` ⇒ **UNKNOWN** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\subagent-driven-development\SKILL.md)) -> 1.3.0 ; fm_field(text,last_updated) -> None ; UPSTREAM load_cache()[repo__obra_superpowers].pushed_at -> 2026-10-29`
- `ui-ux-pro-max` / `nextlevelbuilder/ui-ux-pro-max-skill` local_last_updated=`2026-10-29` upstream_pushed_at=`2026-10-26` ⇒ **LOCAL_AHEAD** ｜ evidence: `LOCAL parse_version(read(D:\global_skills\ui-ux-pro-max\SKILL.md)) -> 1.6.0 ; fm_field(text,last_updated) -> 2026-10-29 ; UPSTREAM load_cache()[repo__nextlevelbuilder_ui_ux_pro_max_skill].pushed_at -> 2026-10-26`

## 5. 上游正文抽样（12 对，pushed_at 最新）

| slug | repo | path | upstream_version | sha | sampled_state |
|---|---|---|---|---|---|
| agent-browser | vercel-labs/agent-browser | skills/agent-browser/SKILL.md | None | 67e8a49ad8d8e5874b9e3a5d802df68d5e5e7d76 | VERIFIED |
| diagram-maker | github/awesome-copilot | skills/excalidraw-diagram-generator/SKILL.md | None | 1a290eae1c7a164f59422e3d8811709ef3357d85 | VERIFIED |
| electron | vercel-labs/agent-browser | skill-data/electron/SKILL.md | None | e4bf00e8e669e43d717e00050df320455352fa86 | VERIFIED |
| figma | heygen-com/hyperframes | skills/figma/SKILL.md | None | 2a33e19bee8715a5225f6743d91a828aa8b66ea2 | VERIFIED |
| gstack | garrytan/gstack | capy/skill/gstack/SKILL.md | None | 11bd23cc72e7535978675f6da3ddcf39d7720b5b | VERIFIED |
| hyperframes | heygen-com/hyperframes | skills/hyperframes/SKILL.md | None | 6f4166472b0f0c6f26e4b3db6829ecf385686701 | VERIFIED |
| hyperframes-cli | heygen-com/hyperframes | skills/hyperframes-cli/SKILL.md | None | 7f51bc528abc5bb4f3e9659de97332dfea9047ca | VERIFIED |
| hyperframes-media | heygen-com/hyperframes | skills/media-use/SKILL.md | None | ddb316eac41a15ab54d0b3de538fd1d0f9b474fc | VERIFIED |
| hyperframes-registry | heygen-com/hyperframes | skills/hyperframes-registry/SKILL.md | None | 7b1bc6a6c95c02ee03319cc8adaba7e54b020cba | VERIFIED |
| ppt-master | hugohe3/ppt-master | skills/ppt-master/SKILL.md | 6.8.0 | 39e6c8a6ab8e1c1e18dfcbfee879d0ae31dbe4ee | VERIFIED |
| story | worldwonderer/oh-story-claudecode | skills/story/SKILL.md | None | f99b794a131a8946418f73e27f24a564d8580f74 | VERIFIED |
| story-cover | worldwonderer/oh-story-claudecode | skills/story-cover/SKILL.md | 1.0.0 | a01d8b2a6acb6b8c3822367c750303b88ee785da | VERIFIED |

样本判读：12/12 **取回成功**（`VERIFIED`，sha 已抄）；其中上游 SKILL.md 头部**有** `version:` 的只有 2 对（ppt-master=6.8.0、story-cover=1.0.0），其余 10 对上游正文无 `version:` 字段 ⇒ 按规则记 `None`，**不用 pushed_at 补**。

样本 evidence_cmd（逐字）：
- `agent-browser`: `gh api repos/vercel-labs/agent-browser/contents/skills/agent-browser/SKILL.md -> base64 decode -> parse_version`  sha=`67e8a49ad8d8e5874b9e3a5d802df68d5e5e7d76` stderr=``
- `diagram-maker`: `gh api repos/github/awesome-copilot/contents/skills/excalidraw-diagram-generator/SKILL.md -> base64 decode -> parse_version`  sha=`1a290eae1c7a164f59422e3d8811709ef3357d85` stderr=``
- `electron`: `gh api repos/vercel-labs/agent-browser/contents/skill-data/electron/SKILL.md -> base64 decode -> parse_version`  sha=`e4bf00e8e669e43d717e00050df320455352fa86` stderr=``
- `figma`: `gh api repos/heygen-com/hyperframes/contents/skills/figma/SKILL.md -> base64 decode -> parse_version`  sha=`2a33e19bee8715a5225f6743d91a828aa8b66ea2` stderr=``
- `gstack`: `gh api repos/garrytan/gstack/contents/capy/skill/gstack/SKILL.md -> base64 decode -> parse_version`  sha=`11bd23cc72e7535978675f6da3ddcf39d7720b5b` stderr=``
- `hyperframes`: `gh api repos/heygen-com/hyperframes/contents/skills/hyperframes/SKILL.md -> base64 decode -> parse_version`  sha=`6f4166472b0f0c6f26e4b3db6829ecf385686701` stderr=``
- `hyperframes-cli`: `gh api repos/heygen-com/hyperframes/contents/skills/hyperframes-cli/SKILL.md -> base64 decode -> parse_version`  sha=`7f51bc528abc5bb4f3e9659de97332dfea9047ca` stderr=``
- `hyperframes-media`: `gh api repos/heygen-com/hyperframes/contents/skills/media-use/SKILL.md -> base64 decode -> parse_version`  sha=`ddb316eac41a15ab54d0b3de538fd1d0f9b474fc` stderr=``
- `hyperframes-registry`: `gh api repos/heygen-com/hyperframes/contents/skills/hyperframes-registry/SKILL.md -> base64 decode -> parse_version`  sha=`7b1bc6a6c95c02ee03319cc8adaba7e54b020cba` stderr=``
- `ppt-master`: `gh api repos/hugohe3/ppt-master/contents/skills/ppt-master/SKILL.md -> base64 decode -> parse_version`  sha=`39e6c8a6ab8e1c1e18dfcbfee879d0ae31dbe4ee` stderr=``
- `story`: `gh api repos/worldwonderer/oh-story-claudecode/contents/skills/story/SKILL.md -> base64 decode -> parse_version`  sha=`f99b794a131a8946418f73e27f24a564d8580f74` stderr=``
- `story-cover`: `gh api repos/worldwonderer/oh-story-claudecode/contents/skills/story-cover/SKILL.md -> base64 decode -> parse_version`  sha=`a01d8b2a6acb6b8c3822367c750303b88ee785da` stderr=``

## 6. 实测程度申报

- **已实测**：49/49 对 lineage 的两侧日期都从盘上取到并逐对比对（48 对判出确定 state）；上游 pushed_at 来自 `load_cache()` 既有缓存（零新正文取数），本地日期来自只读 SKILL.md。
- **已实测（抽样）**：12 对上游 SKILL.md 正文经 `gh api .../contents/` 取回并 base64 解码（sha 落 `fresh_scan.json`），版本用同一个 parse_version 解析。
- **部分实测 / 有缺口**：上游 version 字段本身在多数上游 SKILL.md 中不存在（12 对里仅 2 对有值）⇒ 上游「版本号」这条尺子覆盖面天然有限，记为 None 而非编造；本面因此**不**以版本号下任何 state 判定。
- **未实测**：invalid 13 行（非 lineage）未纳入；62 对全量上游正文版本比对（上一版目标）本轮明确不做；`LOCAL_AHEAD`（5 对）未逐对追因（本面只出 state，不做出因裁定）。

## 7. 负向对照（两腿，逐字实测输出）

命令：
```
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B negctl_r301c.py
```

**腿 A（防恒判 BEHIND）**：取 `agent-browser`（真实 state=BEHIND，local=2026-10-20 / upstream=2026-10-30），把 upstream 人为改成比 local 更旧 ⇒ 必须 LOCAL_AHEAD；再把任一侧置 None ⇒ 必须 UNKNOWN。
```
LEG_A_BASE slug=agent-browser repo=vercel-labs/agent-browser local_last_updated=2026-10-20 upstream_pushed_at=2026-10-30 real_state=BEHIND
LEG_A1 in=(local=2026-10-20, upstream=2000-01-01 人为改旧) out=LOCAL_AHEAD expect=LOCAL_AHEAD PASS
LEG_A2 in=(local=2026-10-20, upstream=None) out=UNKNOWN expect=UNKNOWN PASS
LEG_A3 in=(local=None, upstream=2026-10-30) out=UNKNOWN expect=UNKNOWN PASS
LEG_A RESULT: PASS
```

**腿 B（防全 UNKNOWN 冒充完成）**：非 UNKNOWN 的真实判对 **43** 对（门限 ≥5），逐字抄前 5 对的两侧日期与取值命令：
```
LEG_B slug=agent-browser repo=vercel-labs/agent-browser local_last_updated=2026-10-20 upstream_pushed_at=2026-10-30 state=BEHIND cmd=LOCAL parse_version(read(D:\global_skills\agent-browser\SKILL.md)) -> 3.2.0 ; fm_field(text,last_updated) -> 2026-10-20 ; UPSTREAM load_cache()[repo__vercel_labs_agent_browser].pushed_at -> 2026-10-30
LEG_B slug=algorithmic-art repo=anthropics/skills local_last_updated=2026-09-21 upstream_pushed_at=2026-10-28 state=BEHIND cmd=LOCAL parse_version(read(D:\global_skills\algorithmic-art\SKILL.md)) -> 1.0.0 ; fm_field(text,last_updated) -> 2026-09-21 ; UPSTREAM load_cache()[repo__anthropics_skills].pushed_at -> 2026-10-28
LEG_B slug=brainstorming repo=obra/superpowers local_last_updated=2026-10-27 upstream_pushed_at=2026-10-29 state=BEHIND cmd=LOCAL parse_version(read(D:\global_skills\brainstorming\SKILL.md)) -> 1.2.0 ; fm_field(text,last_updated) -> 2026-10-27 ; UPSTREAM load_cache()[repo__obra_superpowers].pushed_at -> 2026-10-29
LEG_B slug=brand-guidelines repo=anthropics/skills local_last_updated=2026-09-22 upstream_pushed_at=2026-10-28 state=BEHIND cmd=LOCAL parse_version(read(D:\global_skills\brand-guidelines\SKILL.md)) -> 1.0.0 ; fm_field(text,last_updated) -> 2026-09-22 ; UPSTREAM load_cache()[repo__anthropics_skills].pushed_at -> 2026-10-28
LEG_B slug=canvas-design repo=anthropics/skills local_last_updated=2026-09-21 upstream_pushed_at=2026-10-28 state=BEHIND cmd=LOCAL parse_version(read(D:\global_skills\canvas-design\SKILL.md)) -> 1.0.0 ; fm_field(text,last_updated) -> 2026-09-21 ; UPSTREAM load_cache()[repo__anthropics_skills].pushed_at -> 2026-10-28
LEG_B RESULT: PASS n=43
```

## 8. 偏差说明（自决 + 回滚）

- 派发文本写「version 与 last_updated 都用本体 parse_version」，但实测 `r114_replacement_scan.parse_version` **只解 `version:`**（源码 596-609 行，docstring 亦只承诺 version）。**自决**：version 仍用 parse_version（逐字合规），`last_updated` 改用**仓内既有的** `r112_provenance_scan.fm_field(text,last_updated)`（源码 63-68 行），避免自写第二份解析器。**回滚**：若判定必须用 parse_version 解 last_updated，则本面无法取该侧日期、全部 state 只能 UNKNOWN；文件全在 `_repro/r301c/`，删除即回滚，未触任何仓内既有文件。
- 写面：仅 `_repro/r301c/`；`D:/global_skills` 只读、`D:/global_memory` 未碰、未跑 run_gates.py、未做 git 写。

## 9. 复算产物

- `fresh_scan.json`：`pairs[]`（49）+ `samples[]`（12）
- `check_r301c.py`：末行固定六字段读数
- `negctl_r301c.py`：两腿负控
- `build_r301c.py` / `fresh_judge.py`：取数与判定核心（正式件与负控共用 classify）
