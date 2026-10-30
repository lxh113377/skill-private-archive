# verifications.md — security-audit 换装**后**的验证判据（R290 材料包 · R289-5 第 1-4 步）

> 状态：**已实测** = 2026-10-30 本机真实 stdout 逐字抄录（全量逐字见 [`measured_outputs.json`](measured_outputs.json)）；**未实测** = 只能落盘后由 Lead 复验（红线 2：本材料零写入受管根）。
> 解释器必须用受管 venv：`C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（LibreOffice 自带 python 会把探针假报 —— 已定事实）。
> 下文 `<PY>` = 该绝对路径；判据本体 = [`check_r290s.py`](check_r290s.py)（七条腿 + 六负控，任何模式零写入）。
> 读数绑定（D9）：被检文件 sha256 前 12 与 mtime 记在 coords.json 的 read_face_sha（triage=b10861cea6e2 / 交集=8c91684021bc / 台账=684a0928fc8c / 本地 SKILL=e3f38afe2046）；sha 变了即读数过期，先重跑探针再喂补丁。
> 引用纪律：引判据输出时锁**稳定字段**；`links=` 与 `calls=` 两项随本文件自身内容增长，故按最后一次实跑值写入（重跑即复算，不当常量用）。

## 0. 顺序硬约束：先建新件，后打补丁（反序即死链 —— 已实测有牙）

落盘次序（由 Lead 经 `rule_editor.py` 执行；本件只出材料，不动受管根）：

    ① 先落两个新件。依据（实测 rule_editor.py:1455 代码路径）：它**没有新建能力** —— op_replace
       走 read_text(path)，目标件不存在即失败 ⇒ 新件须由 Lead 从 _repro/r290s/staging/ 逐字节复制
       进受管根并 git add（r289 的 r289_newfile.py 同法）：
         security-audit/references/upstream-cloudflare-sec.md
         security-audit/scripts/validate-coverage-ledger.cjs
    ② 再打补丁（一个 --file 只吃一个目标件 ⇒ 两份数组件、两次调用）：
       <PY> D:/global_skills/A-memory-start/references/rule_editor.py replace --file security-audit/SKILL.md  --patch _repro/r290s/patch_local.json    --dry-run
       <PY> D:/global_skills/A-memory-start/references/rule_editor.py replace --file security-audit/.upstream --patch _repro/r290s/patch_upstream.json --dry-run
    ③ 两次 dry-run 全绿（4/4 + 1/1）才去掉 --dry-run 落盘；批量用 --no-commit，末尾 commit --file ... --file ... --fix-mirror 收口

为什么不能反序（**已实测**；order 负控 = 模拟「新件尚未落盘那一刻」的盘）：

    <PY> -B _repro/r290s/check_r290s.py --only D --neg order
    实测（逐字）：
    PASS D [R290S-D-LINKS] claim_new=Y links=22 dead=0 detail=-
    [R290S-NEGCTL] neg=order leg_red=Y meaning=has_teeth

⇒ 两条新指针 `references/upstream-cloudflare-sec.md` 与 `scripts/validate-coverage-ledger.cjs` 在反序时刻**同时判死链** ⇒ 顺序不可交换。
本仓同族前例（写在这里是为了别再赌一次）：
- `06-benchmark/全量对标报告_r289b_阶段C首次真换装_2026-10-30.md`:44 —— 素材一起纳入发布面 ⇒ 死链 0 跳 **16**；
- `_repro/r287m/README.md`:42 —— 「顺序硬约束：先建新件，再打补丁（反序 = **5 条死链**，已实测 _probe_order.py）」；
- `memory/07-next-steps.md` L58（R285-1）—— 可重建副本入库 ⇒ 发布面死链 0 暴增 **68**。

## 1. 判据① 死链面：文中引用的每个路径必须落地

    <PY> -B _repro/r290s/check_r290s.py --only D
    期望末行（已实测）：
    PASS D [R290S-D-LINKS] claim_new=Y links=22 dead=0 detail=-

口径：链接解析复用仓内单源 `05-exec/r220_md_deadlink.py` 的 scan_lines（围栏感知 + 占位符跳过），本件不重写正则；
落地面 = 受管根 security-audit 在盘件 ∪ 暂存新件；外链（含 `://`）不计死链（与 r220 dead() 同口径）。

牙（**已实测**）：把一条**本不存在**的引用文件写进面 ⇒ 死链腿判红并点名：

    <PY> -B _repro/r290s/check_r290s.py --only D --neg deadlink
    FAIL D [R290S-D-LINKS] claim_new=Y links=22 dead=2 detail=skill:D:/global_skills/security-audit/SKILL.md:257->./nope_r290s_unwritten.md;here:verifications.md:266->./nope_r290s_unwritten.md
    [R290S-NEGCTL] neg=deadlink leg_red=Y meaning=has_teeth

落盘后复验（真实受管根；**未实测** —— 本件未写盘）：

    <PY> -B 05-exec/r220_md_deadlink.py D:/global_skills/security-audit
    期望末行：[GATE:deadlink-pass]（若报 [GATE:deadlink-fail] ⇒ 新指针未落地或被 ignore 吞掉，停手回滚）

## 2. 判据② 可执行面：文中写明的每个 flag 必须真被脚本支持

    <PY> -B _repro/r290s/check_r290s.py --only E
    期望末行（已实测）：
    PASS E [R290S-E-EXEC] mode=live_rc1 calls=1 usage_zero_flag=Y bad_flags=0 detail=- win_caveat=Y

实测依据（现跑、非记忆；取值命令逐字如下，均在 coords.json 的 verbatim_evidence.commands 内）：

    $ gh api "repos/cloudflare/security-audit-skill/contents/skills/security-audit/validate-coverage-ledger.cjs?ref=main" --jq ".sha + \" \" + (.size|tostring)"
    $ git hash-object _repro/r290s/staging/security-audit/scripts/validate-coverage-ledger.cjs
    $ node _repro/r290s/staging/security-audit/scripts/validate-coverage-ledger.cjs
    $ node _repro/r290s/staging/security-audit/scripts/validate-coverage-ledger.cjs --help
    $ node _repro/r290s/upstream/validate-coverage-ledger.test.cjs

    零参数跑    rc=1  stderr=Usage: node validate-coverage-ledger.cjs <path-to-coverage-ledger.json>
    带 --help 跑 rc=1  stderr=Failed to read coverage ledger: OS no-follow and nonblocking input protection is unavailable
    带 --check-coverage 跑 rc=1  stderr=Failed to read coverage ledger: OS no-follow and nonblocking input protection is unavailable
    上游自测套件 rc=0  ℹ tests 31 / ℹ pass 24 / ℹ fail 0 / ℹ skipped 7

由此定两条文档纪律（写错即骗人）：
1. 该脚本 usage 是**零 flag**（只吃一个位置参数）⇒ 任何文档给它写 `--flag` 都是假参数。牙（**已实测**）——负控注入一行调用形态（反例，不得当用法抄）：
   FAIL E [R290S-E-EXEC] mode=live_rc1 calls=1 usage_zero_flag=Y bad_flags=1 detail=--check-coverage win_caveat=Y
   [R290S-NEGCTL] neg=argflag leg_red=Y meaning=has_teeth
2. 本机（Windows）实跑它**读不了任何输入**（no-follow 保护不可用 rc=1）⇒ SKILL.md 与分卷必须写明这层限制，
   否则等于教人「Windows 上跑一遍就能验台账」。判据 `win_caveat=Y` 校验面内含该声明（已实测 Y）；
   Linux/macOS 侧可跑（上游自测 24 pass 已实测）。

## 3. 判据③ 版本三处一致 + 逐字节等值

    <PY> -B _repro/r290s/check_r290s.py --only F
    期望末行（已实测）：
    PASS F [R290S-F-VERSION] fm=2.1.0/2026-10-30 hist=2.1.0/2026-10-30 coords=2.1.0/2026-10-30 sidecar_sha_ref=Y
    <PY> -B _repro/r290s/check_r290s.py --only B
    期望末行（已实测）：
    PASS B [R290S-B-VERBATIM] mode=live cjs=33522B blob=0ef58657bef1 api=0ef58657bef1 equal=Y slices=5 missing=- vol=9458B

B 腿两条独立命令必须同值（**已实测**逐字）：

    gh api "repos/cloudflare/security-audit-skill/contents/skills/security-audit/validate-coverage-ledger.cjs?ref=main" --jq ".sha + \" \" + (.size|tostring)"
      => 0ef58657bef18b26a92321df6c8e3d31bc8e6659 33522
    git hash-object _repro/r290s/staging/security-audit/scripts/validate-coverage-ledger.cjs
      => 0ef58657bef18b26a92321df6c8e3d31bc8e6659   byte_identical=true

分卷取材面 = segments.json 的 5 个上游行区间（B 腿逐块核 missing=-，已实测）。
版本口径（如实）：上游 frontmatter **无 version 字段** ⇒ 2.0.1 → 2.1.0 是本仓自定递增（**未实测**于上游，属仓规、不是上游事实）。
三处同源生成、不手抄：patch_local.json 的 SEC-FM-VERSION（frontmatter）+ SEC-VERSION-HISTORY（版本史首行）+ coords.json 的 post_reskin；
侧车吸收注内 sha 必须 == coords.upstream.head_sha（F 腿 sidecar_sha_ref=Y 已实测）。

## 4. 判据④ 锚点唯一（换装前必查，落盘后重跑同一条）

    <PY> -B _repro/r290s/check_r290s.py            # 全七腿
    <PY> -B _repro/r290s/check_r290s.py --dry      # 离线自检：外部取数腿改读 coords.json 存档（仍零写入）

**已实测** full 全文逐字（含末行）：

    PASS A [R290S-A-ANCHORS] hunks=5 old_unique=5/5 seq_errs=0 broken=-
    PASS B [R290S-B-VERBATIM] mode=live cjs=33522B blob=0ef58657bef1 api=0ef58657bef1 equal=Y slices=5 missing=- vol=9458B
    PASS C [R290S-C-LICENSE] api=MIT body=MIT class=permissive cap=5 restricted_hits=0 md_reconcile=Y verdict=MAY_MERGE
    PASS D [R290S-D-LINKS] claim_new=Y links=22 dead=0 detail=-
    PASS E [R290S-E-EXEC] mode=live_rc1 calls=1 usage_zero_flag=Y bad_flags=0 detail=- win_caveat=Y
    PASS F [R290S-F-VERSION] fm=2.1.0/2026-10-30 hist=2.1.0/2026-10-30 coords=2.1.0/2026-10-30 sidecar_sha_ref=Y
    PASS G [R290S-G-DRIFT] components=2 ids=5/5 drift=-
    [SEC-AUDIT-PREP] hunks=5 old_unique=5/5 license=MIT gate=PASS

dry 末行（已实测）与 full 末行同值 ⇒ --dry 不是放水开关：

    [SEC-AUDIT-PREP] hunks=5 old_unique=5/5 license=MIT gate=PASS

A 腿不信任 _verify 自报：现场重算每个 old 的 count + 行对齐切片证明（row_aligned）+ old/new 行尾对称。
两个数组件的每个元素自带 _verify（同算法现算写入，含 start/end 字节区间与 old/new 字节数）。单跑：

    <PY> -B _repro/r290s/check_r290s.py --only A
    期望：
    PASS A [R290S-A-ANCHORS] hunks=5 old_unique=5/5 seq_errs=0 broken=-

## 5. 负向对照（六条，全部**已实测**；构造全在内存，用完不留任何副本）

每条负控的语义 = 「这条腿必须判红」；判绿 = 判据恒绿无牙 ⇒ [R290S-NEGCTL] 的 has_teeth 就是这件事的机器断言。
注意负控跑的末行仍写 gate=PASS，那是「按预期判红」的通过态（leg_red=Y），不是判据失效；
若出现 meaning=CONST_GREEN_NO_TEETH 才是事故。

    # 负控 anchor-absent：把任一 old 改一个字符 ⇒ A 腿点名 id + count0（不存在）
    <PY> -B _repro/r290s/check_r290s.py --only A --neg anchor-absent
    FAIL A [R290S-A-ANCHORS] hunks=5 old_unique=4/5 seq_errs=1 broken=SEC-FM-VERSION(count0/alignN/tailY),SEC-FM-VERSION(count=0) @ SKILL.md
    [R290S-NEGCTL] neg=anchor-absent leg_red=Y meaning=has_teeth

    # 负控 anchor-multi：old 换成盘上重复最多的整行（运行时 Counter 现挑，不硬编码 —— r287m 曾因硬编码造出恒绿负控）
    <PY> -B _repro/r290s/check_r290s.py --only A --neg anchor-multi
    FAIL A [R290S-A-ANCHORS] hunks=5 old_unique=4/5 seq_errs=1 broken=SEC-FM-VERSION(count9/alignY/tailY),SEC-FM-VERSION(count=9) @ SKILL.md
    [R290S-NEGCTL] neg=anchor-multi leg_red=Y meaning=has_teeth

    # 负控 deadlink：把本不存在的引用文件写进面 ⇒ 死链腿判红
    <PY> -B _repro/r290s/check_r290s.py --only D --neg deadlink
    FAIL D [R290S-D-LINKS] claim_new=Y links=22 dead=2 detail=skill:D:/global_skills/security-audit/SKILL.md:257->./nope_r290s_unwritten.md;here:verifications.md:334->./nope_r290s_unwritten.md
    [R290S-NEGCTL] neg=deadlink leg_red=Y meaning=has_teeth

    # 负控 order：先补丁后建件（撤新件认领）⇒ 死链腿判红（即 §0 那条）
    <PY> -B _repro/r290s/check_r290s.py --only D --neg order
    FAIL D [R290S-D-LINKS] claim_new=N links=22 dead=2 detail=skill:D:/global_skills/security-audit/SKILL.md:56->references/upstream-cloudflare-sec.md;skill:D:/global_skills/security-audit/SKILL.md:56->scripts/validate-coverage-ledger.cjs
    [R290S-NEGCTL] neg=order leg_red=Y meaning=has_teeth

    # 负控 argflag：给零 flag 脚本写一个 flag ⇒ 可执行腿判红
    <PY> -B _repro/r290s/check_r290s.py --only E --neg argflag
    FAIL E [R290S-E-EXEC] mode=live_rc1 calls=1 usage_zero_flag=Y bad_flags=1 detail=--check-coverage win_caveat=Y
    [R290S-NEGCTL] neg=argflag leg_red=Y meaning=has_teeth

    # 负控 drift：数组件与材料件漂移 ⇒ G 腿判红并点名 id
    <PY> -B _repro/r290s/check_r290s.py --only G --neg drift
    FAIL G [R290S-G-DRIFT] components=2 ids=5/5 drift=DRIFT:SEC-FM-VERSION @ patch_local.json
    [R290S-NEGCTL] neg=drift leg_red=Y meaning=has_teeth

    # 正常态对照：同一条不带 --neg 必须判绿
    <PY> -B _repro/r290s/check_r290s.py --only G
    期望：
    PASS G [R290S-G-DRIFT] components=2 ids=5/5 drift=-

残留自查：ls _repro/r290s 里无任何 *_neg* / *_draft* 文件（负控全内存构造）。

另有**文件副本版**负控两条（真改盘上件再跑同一条判据，证明 A/D/G 读的是文件内容而非自报字段），
逐字输出与复跑命令见 `_repro/r290s/negctl_filecopy_proof.md`（副本建在 `_repro/r290s/_negctl*/` 内，已 rm -rf）。

## 6. 总判据（Lead 验收用）

    cd 自建skill优化 && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r290s/check_r290s.py

期望末行（**已实测**逐字）：

    [SEC-AUDIT-PREP] hunks=5 old_unique=5/5 license=MIT gate=PASS

落盘后 Lead 侧另跑（本件按禁止项**未跑** run_gates.py，未做任何 git 写）：

    <PY> D:/global_skills/A-memory-start/references/rule_editor.py gates                          # mirror/noise/evolution/stub
    <PY> -B 05-exec/r220_md_deadlink.py D:/global_skills/security-audit                            # 期望 [GATE:deadlink-pass]
    git -C D:/global_skills show --name-status HEAD                                                # 范围应恰为 4 件（2 新 + SKILL.md + .upstream）
    git -C D:/global_skills status --porcelain | grep -vc security-audit                            # 他人脏件零卷入（r289 同法核数）
    grep -n 2.1.0 D:/global_skills/security-audit/SKILL.md                                          # 改后全文复读（R277-1），不看 diff 条数
    undo 前先验双前提：.bak 在盘 + git cat-file -e HEAD:security-audit/SKILL.md

## 7. 台账那条说法的核验结论（先核再写，不凭记忆）

- 台账原句（memory/07-next-steps.md L42，R261-7）：`security-audit←cloudflare/security-audit-skill（OS 沙箱 + write isolation + coverage-ledger）` ⇒ **已实测：成立**。
- 本地合并面（SKILL.md + references/*.md，共 407 行）逐条指行：

    <PY> -B _repro/r290s/capability_probe.py
    MERGED_FILES ['SKILL.md', 'upstream-owasp-asi.md'] lines=407
    NEEDLE os_sandbox       patterns=3 hits=1 detail=[('upstream-owasp-asi.md', 64, '- agent 生成码在无沙箱情况下不得 `eval()` / `exec()`')]
    NEEDLE write_isolation  patterns=3 hits=0 detail=[]
    NEEDLE coverage_ledger  patterns=4 hits=1 detail=[('SKILL.md', 50, '本 skill 独占的是：OWASP 逐类深扫、**变体分析**（同类漏洞全站扩散查找）、供应链台账、不安全默认值普查、误报反驳验证、补丁后')]
    [CAP-PROBE] done

  · os_sandbox 唯一命中 = references/upstream-owasp-asi.md:64「agent 生成码在**无沙箱**情况下不得 eval/exec」= 禁令，不是沙箱执行方案；
  · write_isolation = 合并面 **0 命中**；
  · coverage_ledger 唯一命中 = SKILL.md:50「供应链台账」= 依赖清单表述，与上游 coverage-ledger.json（覆盖台账）**同名异物**；
  · 上游侧可指行（净增量）：SKILL.md L31-42（OS-enforced sandbox 四控）、L54-86（Write isolation + race-safe 提升 11 步）、L92-105（Coverage and prior runs），加 validate-coverage-ledger.cjs 33522B（本地无 scripts 目录，实测）；
  ⇒ 上游有净增量 ⇒ **不适用 KEEP_LOCAL 退路**（KEEP_LOCAL 要求「本地已含该能力且能逐条指行」，这三行都指不出来）。
- 坐标**不在** r275 两件面件里（**已实测**；字段名先 print sorted(keys) 再引用 —— 本仓已 6 次栽在猜字段名）：
    == r275_different_impl_triage.json rows=7
       row0 keys: ['cap_local', 'cap_upstream', 'evidence_cmd', 'evidence_status', 'face_upstream_lines_in_local_pct', 'fetch_attempts', 'local_only', 'local_path', 'local_version', 'measured', 'overlap', 'skill', 'switch_plan', 'upstream_http_code', 'upstream_only', 'upstream_path', 'upstream_ref', 'upstream_repo', 'upstream_version', 'verdict', 'verdict_evidence']
    == r275_three_channel_intersection.json rows=55
       row0 keys: ['ch1_tag', 'ch2_content', 'ch3_move', 'layer', 'layer_criteria', 'same_lineage', 'same_lineage_source', 'skill', 'upstream_path', 'upstream_ref', 'upstream_repo']
    triage skills: ['brainstorming', 'coding-agent', 'data-analysis', 'find-skills', 'gstack', 'subagent-driven-development', 'ui-ux-pro-max']

  · r275_different_impl_triage.json：rows=7，**不含** security-audit（行字段名含 skill / verdict，无 slug / tier）；
    7 件 = brainstorming / coding-agent / data-analysis / find-skills / gstack / subagent-driven-development / ui-ux-pro-max；
  · r275_three_channel_intersection.json：rows=55，**含** security-audit 一行（行字段名含 skill / layer，**无 verdict**）：
    upstream_repo=trailofbits/skills、upstream_path=null、upstream_ref=null、layer=L4、l4_subreason=REPO_LEVEL_NO_PATH、
    ch1_tag.rel=UNKNOWN_UPSTREAM_RELEASE、ch1_tag.upstream_ref_reason=rc=1:gh: Not Found (HTTP 404)、ch2_content.reading=ABSENT、
    ch3_move.verdict=UPSTREAM_MOVED、ch3_move.upstream_commits_since=9、local_version=2.0.1；该行 notes 原文「仓级口径: upstream_path 为空, 只证明整仓动过, 不得当落后依据」
  ⇒ cloudflare 坐标按 brief 退路用 gh api 现查（命令 + 输出全部抄进 [`coords.json`](coords.json)；除 §3 的版本递增外无 UNVERIFIED 项）。
    复算：
    <PY> -B _repro/r290s/_read275.py

## 8. 许可门（第②步）读数

- 结论（**已实测**）：spdx=MIT class=permissive cap=5 restricted=0 ⇒ MAY_MERGE；逐文件明细与归属义务见 [`license_gate.md`](license_gate.md)。
- 复算（C 腿现场跑单源，并与 license_gate.md 读数对账，防「文档说 MIT 而现算不是」）：

    <PY> -B _repro/r290s/license_gate.py
    [LICENSE] api_spdx=MIT body_spdx=MIT body_class=permissive final_class=permissive cap=5 restricted_hits=0
    [LICENSE] hits=[] bytes=1078 sha256=e598e694aa506650c7192d5ea3be0e50aca0d356ea00551c53429f0b01eb6391
    [LICENSE-PREP] spdx=MIT class=permissive cap=5 restricted=0 gate=PASS
    <PY> -B _repro/r290s/check_r290s.py --only C
    期望：
    PASS C [R290S-C-LICENSE] api=MIT body=MIT class=permissive cap=5 restricted_hits=0 md_reconcile=Y verdict=MAY_MERGE

- 单源签名（**已实测** inspect，非猜）：classify_body(text_upper) / license_class(lic, body_class=None) /
  LICENSE_CAPS={copyleft:1, weak-copyleft:2, restricted:1, unknown:4, permissive:5, none:5}；
  坑：classify_body 必须传**已大写**正文（内部只做空白折叠、不再 .upper()）—— 传原文会假阴判成 unknown。
- 侧车改动可证惰性（**已实测**）：parse_sidecar 补丁前后同解 ⇒ 本材料不把谱系从 trailofbits/skills 改成 cloudflare
  （那是「换谱系」；本件只按 R265-3 以本地为壳并入增量）。

## 9. 材料件清单与写面自证

| 件 | 用途 | 状态 |
|----|------|------|
| [`coords.json`](coords.json) | 上游/本地坐标 + 每条取值命令 + 逐字节证据 + UNVERIFIED 清单 | 已实测 |
| [`license_gate.md`](license_gate.md) / [`license_gate.py`](license_gate.py) / [`license_scan.json`](license_scan.json) | 许可门（单源判定 + 逐文件明细） | 已实测 |
| [`patch_local.json`](patch_local.json) | SKILL.md 4 hunks（喂 --file security-audit/SKILL.md），每元素带 _verify | 已实测唯一 |
| [`patch_upstream.json`](patch_upstream.json) | .upstream 1 hunk（喂 --file security-audit/.upstream） | 已实测唯一 |
| [`patch_material.json`](patch_material.json) | 总件：hunks + 新件清单 + _verify 全表 + 顺序约束 + rule_editor 命令 | 已实测 |
| [`staging/`](staging) | 两个新件暂存副本（① 步逐字节复制进受管根） | 校验器与上游 blob 逐字节相同 |
| [`segments.json`](segments.json) / [`blocks/`](blocks) | 上游行区间台账 + 逐字块 | 已实测 |
| [`capability_probe.py`](capability_probe.py) / [`_read275.py`](_read275.py) / [`_probe_r114.py`](_probe_r114.py) | 三条读数探针（只读） | 已实测 |
| [`measured_outputs.json`](measured_outputs.json) | 本文件全部引文的逐字来源（full + dry + 六负控 + 三探针） | 已实测 |
| [`check_r290s.py`](check_r290s.py) | 判据本体（七腿六负控，零写入） | 已实测 gate=PASS |
| `negctl_filecopy_proof.md` | 文件副本版负控（两条变体 + 复跑命令 + 删副本自查） | 已实测 rc=1 判红 |

写面红线自证：全部产出只落在 `C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r290s/`；
受管根 `D:/global_skills` 与 `D:/global_memory` **零写入** —— 实测 git -C D:/global_skills status --porcelain -- security-audit 输出为空；
05-exec/、06-benchmark/、_repro/ 未改（只读复用 r114_replacement_scan.py 与 r220_md_deadlink.py）；无 git 写；未跑 run_gates.py。

未取入内容（如实）：上游其余分卷（ATTACK-CLASSES / HUNTING / RECONNAISSANCE / VALIDATION-AND-REPORTING 等）、validate-findings.cjs、report-schema.json
⇒ 理由：三能力只需三段正文；引它们要连带整张分卷网络（未随件引入 ⇒ 引用必成死链，见 §0）。若要全量换装，另开一单按同八步走。
E 腿边界（如实）：只核本材料唯一引入的可执行件 validate-coverage-ledger.cjs；分卷正文不含任何 markdown 相对链接（实测 0 条）⇒ 不新增死链面。
