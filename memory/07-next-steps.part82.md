# 07-next-steps.part82.md

<!-- 本卷为 07-next-steps.part75.md 的延续 -->

## 新增待办（下轮承接）

- **完成标准实测**：upstream_only **73 → 0**、local_only 31 → 14、文件 6,046B/152 行 → 11,226B/222 行、swap 裁决 UPGRADE_REVIEW → LOCAL_AHEAD_KEEP。

### ④ 工具可靠性：取数失败不得销毁证据（改造 4，中优先级）

- **自伤实测**：一次网络 EOF 让 14KB 好件被 280B 失败桩覆盖，随后 --offline 复算把已升级件读成 UNVERIFIED（ok_n 24→18）。
- **修法**：`fetch_candidate` 失败不覆盖已成功缓存，改记 `cache_error` 侧车字段；成功照旧覆盖；损坏件用已验证字节复原（sha256 与上游登记值逐字节相等）。
- **常驻门**：`cache_guard_fixtures` 4 腿（g1 好件保留 / g2 变异体抓旧实现 / g3 成功仍覆盖 / g4 无旧件失败照写）。
- **取值**：`python 05-exec/r112_cache_guard_fixtures.py` → `[GATE:fixture-pass]` 4/4；`python 05-exec/r112_upstream_probe.py --refresh --json <件>` → face.ok_n=24。

## 新增待办（下轮承接）

- [x] **【P0·待办 R112-1（r112 登记·非历史项）】** 补 127 件 unknown 的上游身份（declared 优先，inferred 次之），目标 unknown 127 → < 100。做法：先扫盘上安装器元数据（`_skillhub_meta.json`/`meta.json`/`_meta.json`），再对剩余件按 r96 上游语料 slug 做**同名候选**登记（严格标 inferred，不冒充同源）。完成标准：`python 05-exec/r112_provenance_scan.py --json <件>` 的 tiers.unknown 下降且守恒仍 182。 【r119 勾销：r113 执行完毕：unknown 127→56（目标 <100 已达成），守恒 182==182；闭环登记见 part78】
- [x] **【P0·待办 R112-2（r112 登记·非历史项）】** 余 11 件 UPGRADE_REVIEW 逐件裁决（test-driven-development 20 行增量 / github 17 / react-best-practices 14 / shadcn 14 / theme-factory 10 / hyperframes-registry 3 / obsidian-bases 3 / defuddle 1 / healthcare 三件各 1 / web-design-guidelines 1）。做法：逐件读 upstream_only 行 → 判断是否值得合入（本地是否已有等价或更强内容）→ 走 rule_editor replace --dry-run 再落。完成标准：每件给出「升级 / 保留本地 / 人工合并」三选一裁决并附证据行号。 【r119 勾销：r116/r117 执行完毕：11 件逐件四分类 REAL_DELTA=5 / META_ONLY=2 / LOCAL_AHEAD=4，守恒 OK；闭环登记见 part78】
- [x] **【P1·待办 R112-3（r112 登记·非历史项）】** 15 件 UNVERIFIED 换候选源重取（brainstorming / code-review / docx / find-skills / frontend-design / frontend-slides / grill-me / hyperframes 三件 / pdf / security-audit / ui-ux-pro-max / verification-before-completion / xlsx）。做法：扩候选源（不只 r96 语料 slug），或显式登记「非同源/无上游」。完成标准：每件有具名结论，UNVERIFIED 数下降或全部具名转档。 【r119 勾销：part42 已闭环：15 件 UNVERIFIED 换候选源重取或显式转「非同源/无上游」】
- [x] **【P1·待办 R112-4（r112 登记·非历史项）】** 「取数失败不得销毁证据」范式推广：扫描全库其它取数/缓存脚本（`r96_twelve_face.py` / `r60_capability_roster.py` / `r105_*` 等）是否存在同形态（失败写盘覆盖好件）。完成标准：逐件列出「有/无该形态」，有则同轮修并补腿。 【r119 勾销：part42 已闭环：「取数失败不得销毁证据」范式推广扫全库取数脚本】
> 【r121 合并】R112-5 的在账处已统一至主壳 `07-next-steps.md`（同号双登记致重复计账，r121 新增「同号多副本面」判据首跑即抓到本行）。本行原文为 r112 轮登记副本，内容与主壳条目一致（mirror 300s 超时 + noise 2 项外部在途），处置与状态以主壳为准；本行改为指针，不再作为独立待办计入。
