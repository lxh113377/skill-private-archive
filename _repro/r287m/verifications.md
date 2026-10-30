# verifications.md — mcp-builder 换装后的验证判据（R287m）

> 判据实现 = `_temp/r287m/check_r287m.py`（材料自证，六条腿）与 `_temp/r287m/verify_landed.py`（落盘后复验，
> 复用同一实现，不留第二真相源）。两者**只读**受管根：补丁在内存重放，绝不写 D:/global_skills（红线 2）。
> 解释器必须用受管 venv：`C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe`。
> 本文件每条「已实测」都是 2026-10-30 本机真实 stdout 的逐字抄录。

## 0. 换装前置读数（现受管根，应判 MISSING_V2）

命令：

    gh api "repos/anthropics/skills/commits?path=skills/mcp-builder&per_page=1" --jq ".[0].sha[0:12]"; test -f "D:/global_skills/mcp-builder/reference/node_mcp_server_v2.md" && echo LOCAL=HAS_V2 || echo LOCAL=MISSING_V2

期望末行：`LOCAL=MISSING_V2`（首行 `ca45fc496a34`）。已实测输出即为此两行。
判据出处（逐字复算）= `06-benchmark/三通道交集面_r275_2026-10-30.md` 第 143-144 行 mcp-builder 节。
同件负控：test 目标换成 `reference/node_mcp_server.md` 已实测 ⇒ 末行变 `LOCAL=HAS_V2`（判据有牙）。

## 1. 判据① 死链面：被引用的每个路径必须在盘上存在

命令：

    <PY> -B _temp/r287m/check_r287m.py --only D

已实测期望输出（两行，判据取末行）：

    PASS D [R287M-D-LINKS] links=16 dead=0 -
    [MCP-PREP-SUB] only=D ok=PASS

口径：文档面 = 换装后的 SKILL.md + node_mcp_server.md（内存重放结果）+ 其余 reference/*.md + 新增件暂存副本；
每条相对引用 `](./x)` 判「存在」= 盘上 isfile，或被 `patch.json` 的 new_file.local_target /
`newfile_manifest.json` 认领（本次唯一新增件）。
牙（已实测，`_probe_order.py`）：把新增件从认领集撤掉（等价「先打补丁、后建新件」的错误顺序）
⇒ 输出 `dead=5` 并判红，末行 `[R287M-ORDER] newfile-first proven: dead 0 -> 5` ⇒ 顺序约束有牙。

落盘后复验（真实受管根）：

    <PY> -B _temp/r287m/verify_landed.py

期望末行：`[MCP-LANDED] dead=0 args_ok=1 version_ok=1 v2=1 gate=PASS`
已实测（换装**前**跑它必判红，即本判据非恒绿）当前真实输出为：

    [MCP-LANDED] dead=0 args_ok=1 version_ok=1 v2=1 gate=FAIL

FAIL 的两个来源（已实测逐字）：`FAIL [R287M-F-VERSION] fm=1.0.0/2026-09-29 hist=-/- rows=0 consistent=NO`
与 `[R287M-V2-ONDISK] exists=no`。
已实测（内存预览树 = 换装后的等效盘，`_mk_preview.py` 生成 `_landed_preview/`）：

    <PY> -B _temp/r287m/verify_landed.py --root _temp/r287m/_landed_preview --newfile-list _temp/r287m/_landed_preview/_manifest.json
    期望：PASS [R287M-D-LINKS] links=17 dead=0 -  …  [MCP-LANDED] … gate=PASS

## 2. 判据② 可执行面：文档写明的每个脚本参数必须被该脚本 --help 支持

本仓已三次栽在「文档写的参数脚本不认」。受管 venv 无 anthropic/mcp 包，裸跑
`python scripts/evaluation.py --help` 在 import 期就 ModuleNotFoundError（已实测），
所以用 `_help_of.py` 打桩顶掉缺失依赖（argparse 构造期不触碰这些符号），取 argparse 真实 usage，不读源码猜。

    <PY> -B _temp/r287m/check_r287m.py --only E

已实测期望输出：

    PASS E [R287M-E-ARGS] scripts=1 flag-refs=7 unsupported=0 -
    [MCP-PREP-SUB] only=E ok=PASS

取值面（实测）：scripts/evaluation.py 的 usage 认 -h -t -m -c -a -e -u -H -o；
reference/evaluation.md 六处调用共 7 个参数引用全部命中（含 -c/-a/-e/-t/-u/-H/-o）。
口径边界（写进实现，防假红/假绿）：只算围栏代码块内的调用，且脚本必须在 scripts/ 真实存在；
`python your_server.py --help`（python_mcp_server.md:716）是用户自写服务器的占位符，不是本件脚本，不计入。
牙（已实测）：注入 --totally-made-up-flag ⇒ `flag-refs=8 unsupported=1 evaluation.py --totally-made-up-flag` 并判红。

## 3. 判据③ 版本一致性：frontmatter version / last_updated 与版本史行三者一致

    <PY> -B _temp/r287m/check_r287m.py --only F

已实测期望输出：

    PASS F [R287M-F-VERSION] fm=1.1.0/2026-10-30 hist=1.1.0/2026-10-30 rows=1 consistent=yes
    [MCP-PREP-SUB] only=F ok=PASS

三处同源生成（`gen_patch.py` 机械产出，非手抄）：
`SKILL-FM-VERSION` 把本地叠加行 version 1.0.0 改为 1.1.0、last_updated 改为 2026-10-30（上游无这两行 ⇒ 不删只递增，
r275 人读结论「本地叠加项须保留」已实测：_upstream_SKILL.md 里确实没有 version/last_updated）；
`SKILL-VERSION-HISTORY` 在文末追加 Version history 小节，首行为 1.1.0（2026-10-30）并带上游 sha ca45fc496a34。
落盘后同一判据由 verify_landed.py 复跑（见 §1 末命令）。
额外只读探测（`_probe_collide.py`，已实测）：把补丁 new 全文喂给 rule_editor 自己的编号正则与
_hist_numbers ⇒ `R:[] V:[]`，即落盘不会触发 R231 编号预检 fail-closed，Lead 无需 --allow-collide。

## 4. 负向对照（全部实测输出在案）

    <PY> -B _temp/r287m/check_r287m.py --only A --neg anchor-absent
    期望末行 [MCP-PREP-SUB] only=A ok=PASS；实测 PASS，点名 SKILL-STRUCTURE-PTR(count=0)，顺序重放命中 0 次 @ SKILL.md

    <PY> -B _temp/r287m/check_r287m.py --only A --neg anchor-multi
    期望末行 [MCP-PREP-SUB] only=A ok=PASS；实测 PASS，点名 NODE-V1-BANNER(count=22)

    <PY> -B _temp/r287m/check_r287m.py --only D --neg deadlink
    期望末行 [MCP-PREP-SUB] only=D ok=PASS；实测 PASS，dead=1 node_mcp_server_v2.md->./node_mcp_server_UNWRITTEN_v9.md

    <PY> -B _temp/r287m/check_r287m.py --only E --neg argflag
    期望末行 [MCP-PREP-SUB] only=E ok=PASS；实测 PASS，unsupported=1 evaluation.py --totally-made-up-flag

    <PY> -B _temp/r287m/verify_landed.py            # 落盘判据跑真根：换装前应 gate=FAIL（已实测）
    <PY> -B _temp/r287m/_probe_order.py             # 先补丁后建件：dead 0 -> 5（已实测）

负控自身的教训（原样留档，避免后人重踩）：anchor-multi 首版硬编码 "## Overview" 造多命中，
实测该串在 node_mcp_server.md 只出现 1 次 ⇒ 负控恒绿（没有牙）。改为运行时用 Counter 现挑
「盘上重复最多的非空行」才拿到 count=22。这就是 D10.2「判据脚本自身必须过负控」的又一例。
负控全部内存构造，用完不留副本（本目录无 *_neg 残留文件，负控行即上面命令）。


## 4b. 第五腿负控：数组件漂移（已实测）

    <PY> -B _temp/r287m/_drift_test.py

实测输出（三行，用完即复原）：

    rc=1
    last=FATAL: 数组件与 patch.json 漂移: NODE-V1-BANNER
    restored_identical=True

口径：把 `patch_node_mcp_server.md.json` 的 old 改一个字符 ⇒ `load_patch()` 必须硬拒并点名 id；
存在理由：Lead 真正喂给 rule_editor 的是**数组件**（一份一次调用），拆件与本体漂移则锚点断言失真。

## 5. 总判据（Lead 验收用）

    cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _temp/r287m/check_r287m.py

期望末行（已实测逐字）：

    [MCP-PREP] hunks=8 old_unique=8/8 upstream_sha=49b2fe48f339 license=Apache-2.0 gate=PASS

落盘后再跑 verify_landed.py，期望末行 `[MCP-LANDED] dead=0 args_ok=1 version_ok=1 v2=1 gate=PASS`。
仓规门禁由 Lead 在受管根侧执行（本件按禁止项未跑 run_gates.py）：rule_editor.py gates（mirror/noise/evolution）
+ disk_registry_diff 三类全 0。

## 6. 坐标与读数（从判据出处复算抄录，非记忆）

取值命令（存档可复跑）：

    <PY> -B _temp/r287m/_extract275.py        # 从 r275 抽 mcp-builder 行（含 rows[28]）
    <PY> -B _temp/r287m/_extract_coords.py    # 四通道逐件对账，输出 _coord_rows.txt
    <PY> -B _temp/r287m/_numbers.py           # 许可/提交/新件数字现取，落 numbers.json
    gh api "repos/anthropics/skills/commits/main" --jq ".sha"   # 已实测 ca45fc496a3436251f191354091d557da31c15b5

已实测读数（逐字）：
- `06-benchmark/r275_three_channel_intersection.json` rows[28]（skill=mcp-builder）：
  upstream_repo=**anthropics/skills**，upstream_path=**skills/mcp-builder**，upstream_ref=null，
  same_lineage=true（source=r264.semantics=SAME_LINEAGE），ch1.rel=UNKNOWN_UPSTREAM_RELEASE
  （release_error="rc=1:gh: Not Found (HTTP 404)"），local_version=1.0.0，ch3.verdict=UPSTREAM_MOVED，
  ch3.upstream_commits_since=1，capped=false，local_last_commit=2026-10-20T09:25:30+08:00，
  layer=**L4**，l4_subreason=PATH_LOCALIZED_NOT_EXECUTABLE，ch2_content.reading=ABSENT
- `06-benchmark/r264_superpowers_follow_version_diff.json`：**该件 rows 内没有 mcp-builder**（已实测 hits=0，
  它只测 obra/superpowers@v7.0.1）；同源判定实据在 sidecar `06-benchmark/r264_sidecar_semantics.json
  rows[skill=mcp-builder]` = semantics=SAME_LINEAGE / rule=path_in_tree / shared_local_n=11 / path_probe=exists
- `06-benchmark/r271_version_channel2.json` rows[mcp-builder]：verdict=UPSTREAM_MOVED / commits_since=1（ch3 原件）
- `06-benchmark/r263_declared_upstream_face.json` rows[mcp-builder]：license=UNLICENSED（API 字段 null 的回填），
  stars=184459，pushed_at=2026-10-09，release_error=gh 404
- 上游提交（现取）：sha ca45fc496a3436251f191354091d557da31c15b5，author date 2026-10-28T19:20:38Z，
  标题 "Update mcp-builder skill: teach v2 of the MCP TypeScript SDK (#2087)"，files=3
  （SKILL.md +26/-10、reference/node_mcp_server.md +2/-0、reference/node_mcp_server_v2.md 新增 35171B/747 行）

## 7. 落地方案与一条实测出的阻塞点（给 Lead）

方案 = replace 补丁（2 个既有件，8 hunk）+ **新增独立文件**（1 件）。不是纯 replace：
1. `reference/node_mcp_server_v2.md` 在本地不存在、在上游是**新增**件 ⇒ 没有 old 可切，只能整件新增。
   本地/上游差异不构成退路情形：另两件差异方向全部是「上游有 v2、本地无」（diff 实测 6 hunk + 1 hunk，
   本地仅 frontmatter/LICENSE/NOTICE 领先，补丁已全部保留）。
2. 阻塞点（**只读探测实证**，`_probe_newfile.py`，未写盘）：rule_editor.py **不能创建新文件**。
   resolve() 安全区分支为 isfile 判定，非文件即 sys.exit，实测输出：
   SYSEXIT: ERROR: 安全区内文件不存在: D:\global_skills\mcp-builder\reference\node_mcp_server_v2.md
   同型先例记录 = `06-benchmark/全量对标报告_r163_免费工具可达性对账与gh空壳遮蔽_2026-10-22.md` 第 5266 行。
   候选路（Lead 择一，本件无权落盘）：
     A. Lead 在受管根先建占位件（0B 或先 copy 暂存件），再走 rule_editor replace；
     B. 新件这一笔用 cp 落上游逐字节原文（sha 由 B 腿复算），两个既有件仍走 rule_editor replace。
   建议 B，并在台账记例外理由（resolve 不支持新建，实测证据在上）。
3. **顺序硬约束：先落新增件，再打 SKILL.md / node_mcp_server.md 补丁**；反序即造 5 条死链（§1 实测）。
4. rule_editor 调用形态（读实现所得）：一个 --file 只吃一个目标件 ⇒ 跨件必须拆。已备好数组件
   `patch_SKILL.md.json`（7 hunk）与 `patch_node_mcp_server.md.json`（1 hunk）；`patch.json` 是材料本体 +
   _verify 断言（hunks 段与数组件同源同字节）。建议 --no-commit 两件连打后用
   `rule_editor.py commit --file … --file … --desc` 一次收口（R215d），再跑三门禁 + disk_registry_diff。
5. 许可面零改动（Apache-2.0，详见 license_gate.md）：LICENSE/LICENSE.txt 与上游字节级同一份，NOTICE 在位。

注：文中 `<PY>` = C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe。