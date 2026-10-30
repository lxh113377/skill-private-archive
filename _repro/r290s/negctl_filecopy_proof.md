# 负向对照（文件副本版）—— 证明判据读盘上真实件、有牙（已实测）

> 与判据内建 `--neg`（内存构造）互补：本件把材料**复制成副本**、在副本上真实改文件再跑同一条判据，
> 证明 A/D/G 三条腿读的是盘上件内容而不是自报字段。副本一律建在 `_repro/r290s/_negctl*/` 之内，
> 用完 `rm -rf`（现不存在：`ls _repro/r290s` 无 `_negctl` 目录，已实测）。判据本体全程未改动。

## 副本构造命令（可复跑）

    NEG=_repro/r290s/_negctl && mkdir -p $NEG/05-exec $NEG/_repro/r290s
    cp 05-exec/r220_md_deadlink.py 05-exec/r114_replacement_scan.py $NEG/05-exec/
    cp -r _repro/r290s/* $NEG/_repro/r290s/    # 判据按 __file__ 推 ROOT，故必须造 05-exec 同级结构
    cd $NEG && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r290s/check_r290s.py

## 变体 ①：副本里 patch_local.json 的一个 old 改一个字符 + verifications.md 写进一条本不存在的引用文件

实测 rc=1（判红，且点名 id 与死链目标）：

    PASS A [R290S-A-ANCHORS] hunks=5 old_unique=5/5 seq_errs=0 broken=-
    PASS B [R290S-B-VERBATIM] mode=live cjs=33522B blob=0ef58657bef1 api=0ef58657bef1 equal=Y slices=5 missing=- vol=9458B
    PASS C [R290S-C-LICENSE] api=MIT body=MIT class=permissive cap=5 restricted_hits=0 md_reconcile=Y verdict=MAY_MERGE
    FAIL D [R290S-D-LINKS] claim_new=Y links=23 dead=1 detail=here:verifications.md:266->./nope_filecopy_unwritten.md
    PASS E [R290S-E-EXEC] mode=live_rc1 calls=1 usage_zero_flag=Y bad_flags=0 detail=- win_caveat=Y
    PASS F [R290S-F-VERSION] fm=2.1.0/2026-10-30 hist=2.1.0/2026-10-30 coords=2.1.0/2026-10-30 sidecar_sha_ref=Y
    FAIL G [R290S-G-DRIFT] components=2 ids=5/5 drift=DRIFT:SEC-ABSORB-POINTER @ patch_local.json
    [SEC-AUDIT-PREP] hunks=5 old_unique=5/5 license=MIT gate=FAIL

读数解释：改的是组件件、没改材料件 ⇒ G 腿抓到漂移（`DRIFT:SEC-ABSORB-POINTER`）；
把本不存在的引用文件写进 verifications.md ⇒ D 腿判红并点名 `nope_filecopy_unwritten.md`。

## 变体 ②：只改 A 腿输入（patch_material.json 的 hunk old），并同步数组件以隔离 A 腿单点

实测 rc=1（A 腿现场重算，不信 `_verify` 自报；F 腿同时因该 hunk 不再命中而落到未换装文本，属**连锁判红**，非误报）：

    FAIL A [R290S-A-ANCHORS] hunks=5 old_unique=4/5 seq_errs=1 broken=SEC-VERSION-HISTORY(count0/alignN/tailY),SEC-VERSION-HISTORY(count=0) @ SKILL.md
    PASS B / PASS C / PASS D(links=22 dead=0) / PASS E
    FAIL F [R290S-F-VERSION] fm=2.1.0/2026-10-30 hist=1.1.0/2026-09-29 coords=2.1.0/2026-10-30 sidecar_sha_ref=Y
    PASS G [R290S-G-DRIFT] components=2 ids=5/5 drift=-
    [SEC-AUDIT-PREP] hunks=5 old_unique=4/5 license=MIT gate=FAIL

读数解释：`old_unique=4/5` 且点名 `SEC-VERSION-HISTORY(count0)` ⇒ 「把任一 old 改一个字符 ⇒ 判据必须报该 hunk 不唯一/不存在并点名 id」这条硬要求由**真实文件改动**满足；
F 腿报 `hist=1.1.0/2026-09-29` 正是「版本史补丁未生效」的真相（该 hunk 失效后盘上仍是旧版本史），两条腿互为佐证。

## 收尾自查（已实测）

    rm -rf _repro/r290s/_negctl _repro/r290s/_negctl2        # 副本用完即删，且只在 _repro/r290s 之内
    ls _repro/r290s | grep -i negctl                          # 只命中本件（.md），无任何副本目录残留
    cd 自建skill优化 && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r290s/check_r290s.py

本体（未改动）重跑末行：`[SEC-AUDIT-PREP] hunks=5 old_unique=5/5 license=MIT gate=PASS`（rc=0，已实测）。

> 内建六条 `--neg` 负控的逐字输出见 `measured_outputs.json` 与 `verifications.md` §5。
