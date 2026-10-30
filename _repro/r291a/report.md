# r291a 零兼容回归读数面 · 5 笔落地 × 6 维矩阵

> 生成：`python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py`（现读，无手抄数字）。取值时刻 2026-10-30T11:14:52+0800。
>
> **本面测的是产物/接口兼容（description 触发语义、frontmatter 字段集合、相对指针可达性、
> 命令面、版本史行数、镜像同步），不等于业务质量。** 质量移动的读数面在 `05-exec/r278_landing_effect.py`。

## 0. 三张 sha 表（base / before / after，全部 git 现读）

| 落地 | slug | base（首笔之父） | before（改前文本所在） | after | before=base? | before blob 见证 | 链内提交=本笔? |
|---|---|---|---|---|---|---|---|
| L1-r266-tdd-pointer | test-driven-development | `87934d48` | `87934d48` | `079b91f3` | True | True | True |
| L2-r269-frontend-slides-register | frontend-slides | `3681df5e` | `3681df5e` | `6394cbae` | True | True | True |
| L3-r272-277-frontend-slides-migration | frontend-slides | `d14fc49a` | `d14fc49a` | `89efb3e6` | True | True | True |
| L4-r279-ui-ux-pro-max-merge | ui-ux-pro-max | `25929181` | `3c72867d` | `3da30832` | False | True | False |
| L5-r312-mcp-builder-relayout | mcp-builder | `3da30832` | `3da30832` | `79862372` | True | True | True |

坑（件内固化，不再靠人记）：079b91f3 是误提交他会话降级那笔，它的 <sha>~1 不等于改前状态；故 L4 的 before 显式钉在 3c72867d，并用 blob 等值见证（before_blob_witness）证明那确实是落地前最后一态。

## 1. 矩阵（格 = 状态 + 关键读数 + 取值命令）

| 落地 \ 维 | trigger_semantics | frontmatter_fields | relative_pointers | command_surface | version_history | mirror_sync | 笔判定 |
|---|---|---|---|---|---|---|---|
| **L1-r266-tdd-pointer** | **PASS** identical_all=True / lost=none | **PASS** dropped=[] added=[] | **REGRESSION** dead=1 red=['test-driven-development/writing-good-tests.md'] | **UNVERIFIED** cmds=0 unsup_strict=None | **PASS** rows=1->1 dropped=[] | **REGRESSION** agents=REGRESSION myskills=N/A_NOT_A_MIRROR | REGRESSION |
| **L2-r269-frontend-slides-register** | **PASS** identical_all=True / lost=none | **PASS** dropped=[] added=[] | **REGRESSION** dead=1 red=['frontend-slides/bold-template-pack'] | **UNVERIFIED** cmds=3 unsup_strict=None | **PASS_ADDED_BLOCK** rows=None->3 dropped=[] | **REGRESSION** agents=REGRESSION myskills=N/A_NOT_A_MIRROR | REGRESSION |
| **L3-r272-277-frontend-slides-migration** | **PASS** identical_all=True / lost=none | **PASS** dropped=[] added=[] | **PASS** dead=0 red=[] | **UNVERIFIED** cmds=3 unsup_strict=None | **PASS** rows=3->4 dropped=[] | **REGRESSION** agents=REGRESSION myskills=N/A_NOT_A_MIRROR | REGRESSION |
| **L4-r279-ui-ux-pro-max-merge** | **PASS** identical_all=True / lost=none | **PASS** dropped=[] added=[] | **PASS** dead=0 red=[] | **PASS** cmds=2 unsup_strict=[] | **PASS** rows=6->7 dropped=[] | **REGRESSION** agents=REGRESSION myskills=N/A_NOT_A_MIRROR | REGRESSION |
| **L5-r312-mcp-builder-relayout** | **PASS** identical_all=True / lost=none | **PASS** dropped=[] added=[] | **PASS** dead=0 red=[] | **UNVERIFIED** cmds=0 unsup_strict=None | **PASS_ADDED_BLOCK** rows=None->1 dropped=[] | **REGRESSION** agents=REGRESSION myskills=N/A_NOT_A_MIRROR | REGRESSION |

每格取值命令（逐格可复跑，命令即出处）：

- `L1-r266-tdd-pointer`
  - trigger_semantics → `PASS | identical_all=True | lost=none | moved_into_body=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim trigger_semantics --landing L1-r266-tdd-pointer`
  - frontmatter_fields → `PASS | dropped=[] added=[] | before=['name', 'description', 'last_updated', 'version'] after=['name', 'description', 'last_updated', 'version']`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim frontmatter_fields --landing L1-r266-tdd-pointer`
  - relative_pointers → `REGRESSION | links=1 dead=1 red=['test-driven-development/writing-good-tests.md'] preexisting=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim relative_pointers --landing L1-r266-tdd-pointer`
  - command_surface → `UNVERIFIED | cmds 0->0 | flags 0->0 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no scripts/*.py at this ref: no --help support face exists`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim command_surface --landing L1-r266-tdd-pointer`
  - version_history → `PASS | rows 1->1 | dropped=[] added=[] | `
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim version_history --landing L1-r266-tdd-pointer`
  - mirror_sync → `REGRESSION | mirror=REGRESSION | bytes=11466 | mirror stale at ancestor ref(s) eb1d70c18633, 3b8f0863b2a8, 80dcf13a119f; last mirror sync for this path = 38be46b 2026-08-26T03:40 chore(mirror): 镜像同步快照——对齐 D:\global_skills（含 A-get-memory/chaoshi-web-deploy/cloudbase__`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim mirror_sync --landing L1-r266-tdd-pointer`
- `L2-r269-frontend-slides-register`
  - trigger_semantics → `PASS | identical_all=True | lost=none | moved_into_body=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim trigger_semantics --landing L2-r269-frontend-slides-register`
  - frontmatter_fields → `PASS | dropped=[] added=[] | before=['name', 'description', 'last_updated', 'version'] after=['name', 'description', 'last_updated', 'version']`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim frontmatter_fields --landing L2-r269-frontend-slides-register`
  - relative_pointers → `REGRESSION | links=13 dead=1 red=['frontend-slides/bold-template-pack'] preexisting=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim relative_pointers --landing L2-r269-frontend-slides-register`
  - command_surface → `UNVERIFIED | cmds 3->3 | flags 2->2 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=extract-pptx.py@python.exe rc=1 no-usage-output`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim command_surface --landing L2-r269-frontend-slides-register`
  - version_history → `PASS_ADDED_BLOCK | rows None->3 | dropped=[] added=None | before arm has no Version history block and the landing introduced one: nothing was eaten, so the R241 axis cannot regress on null -> set`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim version_history --landing L2-r269-frontend-slides-register`
  - mirror_sync → `REGRESSION | mirror=REGRESSION | bytes=20073 | mirror still serves the pre-landing text; landing shas 6394cbae1e5d00f8a60e383f761613664cca2b41`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim mirror_sync --landing L2-r269-frontend-slides-register`
- `L3-r272-277-frontend-slides-migration`
  - trigger_semantics → `PASS | identical_all=True | lost=none | moved_into_body=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim trigger_semantics --landing L3-r272-277-frontend-slides-migration`
  - frontmatter_fields → `PASS | dropped=[] added=[] | before=['name', 'description', 'last_updated', 'version'] after=['name', 'description', 'last_updated', 'version']`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim frontmatter_fields --landing L3-r272-277-frontend-slides-migration`
  - relative_pointers → `PASS | links=15 dead=0 red=none preexisting=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim relative_pointers --landing L3-r272-277-frontend-slides-migration`
  - command_surface → `UNVERIFIED | cmds 3->3 | flags 2->2 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=extract-pptx.py@python.exe rc=1 no-usage-output`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim command_surface --landing L3-r272-277-frontend-slides-migration`
  - version_history → `PASS | rows 3->4 | dropped=[] added=['1.4.1'] | `
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim version_history --landing L3-r272-277-frontend-slides-migration`
  - mirror_sync → `REGRESSION | mirror=REGRESSION | bytes=20073 | mirror stale at ancestor ref(s) d14fc49a9f7a, 56d83407f712, 545474993d23; last mirror sync for this path = be2f2f2 2026-08-03T12:04 feat: Marvis 6 技能镜像同步 (R140)`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim mirror_sync --landing L3-r272-277-frontend-slides-migration`
- `L4-r279-ui-ux-pro-max-merge`
  - trigger_semantics → `PASS | identical_all=True | lost=none | moved_into_body=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim trigger_semantics --landing L4-r279-ui-ux-pro-max-merge`
  - frontmatter_fields → `PASS | dropped=[] added=[] | before=['name', 'description', 'last_updated', 'version'] after=['name', 'description', 'last_updated', 'version']`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim frontmatter_fields --landing L4-r279-ui-ux-pro-max-merge`
  - relative_pointers → `PASS | links=0 dead=0 red=none preexisting=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim relative_pointers --landing L4-r279-ui-ux-pro-max-merge`
  - command_surface → `PASS | cmds 1->2 | flags 3->6 | unsup_strict []->[] | unsup_wide []->[] | `
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim command_surface --landing L4-r279-ui-ux-pro-max-merge`
  - version_history → `PASS | rows 6->7 | dropped=[] added=['1.6.0'] | `
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim version_history --landing L4-r279-ui-ux-pro-max-merge`
  - mirror_sync → `REGRESSION | mirror=REGRESSION | bytes=4071 | mirror stale at ancestor ref(s) 3c72867d489b, 6d53d132e686, b2156d5b3b90; last mirror sync for this path = 38be46b 2026-08-26T03:40 chore(mirror): 镜像同步快照——对齐 D:\global_skills（含 A-get-memory/chaoshi-web-deploy/cloudbase__`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim mirror_sync --landing L4-r279-ui-ux-pro-max-merge`
- `L5-r312-mcp-builder-relayout`
  - trigger_semantics → `PASS | identical_all=True | lost=none | moved_into_body=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim trigger_semantics --landing L5-r312-mcp-builder-relayout`
  - frontmatter_fields → `PASS | dropped=[] added=[] | before=['name', 'description', 'license', 'last_updated', 'version'] after=['name', 'description', 'license', 'last_updated', 'version']`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim frontmatter_fields --landing L5-r312-mcp-builder-relayout`
  - relative_pointers → `PASS | links=14 dead=0 red=none preexisting=none`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim relative_pointers --landing L5-r312-mcp-builder-relayout`
  - command_surface → `UNVERIFIED | cmds 0->0 | flags 0->0 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=connections.py@python.exe rc=1 no-usage-output; evaluation.py@python.exe rc=1 no-usage-output`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim command_surface --landing L5-r312-mcp-builder-relayout`
  - version_history → `PASS_ADDED_BLOCK | rows None->1 | dropped=[] added=None | before arm has no Version history block and the landing introduced one: nothing was eaten, so the R241 axis cannot regress on null -> set`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim version_history --landing L5-r312-mcp-builder-relayout`
  - mirror_sync → `REGRESSION | mirror=REGRESSION | bytes=9132 | mirror still serves the pre-landing text; landing shas 79862372928ddb9906707f4c0bc9136d208e37e8`
    - cmd: `python -B C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/r291a_compat_face.py --dim mirror_sync --landing L5-r312-mcp-builder-relayout`

## 2. 负向对照（实测输出，非声明）

### NC1 同文本必同读 + 交换臂必须亮

```json
{
 "landing": "L4-r279-ui-ux-pro-max-merge",
 "leg_same_text_same_reading": {
  "trigger_identical_all": true,
  "frontmatter_dropped": [],
  "frontmatter_added": [],
  "version_rows_equal": true,
  "all_status": {
   "trigger_semantics": "PASS",
   "frontmatter_fields": "PASS",
   "version_history": "PASS"
  }
 },
 "leg_a_ok": true,
 "leg_swapped_arms": {
  "statuses": {
   "trigger_semantics": "PASS",
   "frontmatter_fields": "PASS",
   "version_history": "REGRESSION"
  },
  "lost_evidence": [],
  "frontmatter_dropped": [],
  "version_dropped": [
   "1.6.0"
  ]
 },
 "leg_b_lits": [
  "version_history"
 ],
 "leg_b_ok": true,
 "pass": true
}
```

### NC2 注入不存在的相对指针（临时副本，用完删除）

```json
{
 "landing": "L5-r312-mcp-builder-relayout",
 "injected_targets": [
  "_r291a_ghost_pointer_does_not_exist.md",
  "sub/ghost2_r291a.md"
 ],
 "injected_line": "ghost leg [ghost](_r291a_ghost_pointer_does_not_exist.md) and [g2](sub/ghost2_r291a.md)",
 "status": "REGRESSION",
 "red_named": [
  "mcp-builder/_r291a_ghost_pointer_does_not_exist.md",
  "mcp-builder/sub/ghost2_r291a.md"
 ],
 "ghost_named": [
  "mcp-builder/_r291a_ghost_pointer_does_not_exist.md",
  "mcp-builder/sub/ghost2_r291a.md"
 ],
 "temp_copy_path": "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r291a/negctl/injected_copy.md",
 "temp_copy_removed": true,
 "negctl_dir_removed": true,
 "residual_files_matching_ghost": [],
 "residual_n": 0,
 "pass": true
}
```

## 3. 汇总（按格计数，不做 any()/all() 洗绿）

```json
{
 "status_histogram": {
  "PASS": 17,
  "REGRESSION": 7,
  "UNVERIFIED": 4,
  "PASS_ADDED_BLOCK": 2
 },
 "landings": 5,
 "cells": 30,
 "regression_cells": 7,
 "unverified_cells": 4,
 "per_landing_verdicts": {
  "L1-r266-tdd-pointer": "REGRESSION",
  "L2-r269-frontend-slides-register": "REGRESSION",
  "L3-r272-277-frontend-slides-migration": "REGRESSION",
  "L4-r279-ui-ux-pro-max-merge": "REGRESSION",
  "L5-r312-mcp-builder-relayout": "REGRESSION"
 },
 "top_verdict_by_precedence": "REGRESSION",
 "precedence": "REGRESSION > UNVERIFIED > NO_REGRESSION (a cell that cannot be judged is named, never folded into pass; no any()/all() washing)"
}
```

## 3b. 红格的第二面（HEAD 复算 + 主线祖先，防止把「当时断」读成「现在断」）

| 落地 | 指针红项 | 在 HEAD 是否已恢复 | 本笔各 commit 是否仍是 HEAD 祖先 |
|---|---|---|---|
| L1-r266-tdd-pointer | ['test-driven-development/writing-good-tests.md'] | restored_by_head=['test-driven-development/writing-good-tests.md'] still_dead=[] | {"079b91f3": true} |
| L2-r269-frontend-slides-register | ['frontend-slides/bold-template-pack'] | restored_by_head=['frontend-slides/bold-template-pack'] still_dead=[] | {"6394cbae": true} |
| L3-r272-277-frontend-slides-migration | none | restored_by_head=[] still_dead=[] | {"9aaa9214": true, "294e3ac6": true, "89efb3e6": true} |
| L4-r279-ui-ux-pro-max-merge | none | restored_by_head=[] still_dead=[] | {"30b84b20": true, "3da30832": true} |
| L5-r312-mcp-builder-relayout | none | restored_by_head=[] still_dead=[] | {"79862372": true} |

> 判读口径：指针维的判定取**落地 commit 当时的 git tree**（那才是一个 clone 能检出的状态），HEAD 复算只作第二面披露；格不因 HEAD 恢复而降级。

## 4. 判不了就写 UNVERIFIED（退路清单）

- `L1-r266-tdd-pointer` / command_surface → 原因：UNVERIFIED | cmds 0->0 | flags 0->0 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no scripts/*.py at this ref: no --help support face exists；需要的外部条件：a runnable --help face at that ref (scripts/*.py that answers --help), or a non-python entry probe for js/sh CLIs, or an owner statement that the skill ships no CLI and its body advertises no flags
- `L2-r269-frontend-slides-register` / command_surface → 原因：UNVERIFIED | cmds 3->3 | flags 2->2 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=extract-pptx.py@python.exe rc=1 no-usage-output；需要的外部条件：a runnable --help face at that ref (scripts/*.py that answers --help), or a non-python entry probe for js/sh CLIs, or an owner statement that the skill ships no CLI and its body advertises no flags
- `L3-r272-277-frontend-slides-migration` / command_surface → 原因：UNVERIFIED | cmds 3->3 | flags 2->2 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=extract-pptx.py@python.exe rc=1 no-usage-output；需要的外部条件：a runnable --help face at that ref (scripts/*.py that answers --help), or a non-python entry probe for js/sh CLIs, or an owner statement that the skill ships no CLI and its body advertises no flags
- `L5-r312-mcp-builder-relayout` / command_surface → 原因：UNVERIFIED | cmds 0->0 | flags 0->0 | unsup_strict None->None | unsup_wide []->[] | support face unavailable: no --help face produced; failures=connections.py@python.exe rc=1 no-usage-output; evaluation.py@python.exe rc=1 no-usage-output；需要的外部条件：a runnable --help face at that ref (scripts/*.py that answers --help), or a non-python entry probe for js/sh CLIs, or an owner statement that the skill ships no CLI and its body advertises no flags

