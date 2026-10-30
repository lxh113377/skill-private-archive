# license_gate.md — mcp-builder 上游件许可门（R287m）

## 结论（先行）

**可并入。** 上游件许可 = **Apache-2.0**（正文指纹判定），license_class = **permissive**，
封顶 cap = **5**（r114 LICENSE_CAPS 表），受限措辞命中 = **0**。
不属于 restricted / copyleft / weak-copyleft ⇒ 不触发「不可并入」条款。
若本门读数变成 restricted/copyleft/weak-copyleft（含 none/unknown 保守拦），结论必须改写为「**不可并入**」，
判据由 check_r287m.py 的 C 腿自动给出（gate= 字段直接打印 可并入/不可并入）。

## 取值命令（现取，非记忆；已实测 rc=0）

    PY=C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
    # 1) 取上游许可正文（skills/mcp-builder/LICENSE.txt @ main，base64 解码）
    gh api "repos/anthropics/skills/contents/skills/mcp-builder/LICENSE.txt?ref=main" --jq .content > _temp/r287m/_lic.b64
    #    解码后 = _temp/r287m/_upstream_LICENSE.txt：11345 B / sha256[:12] bc6b3af2f331 / git blob 4f881c52d1f7
    # 2) 单源分类（classify_body + license_class 一律调 05-exec/r114_replacement_scan.py，禁在 _temp 另写一套）
    $PY -B _temp/r287m/_lic_gate.py      # 打印四项读数
    $PY -B _temp/r287m/_numbers.py       # 读数落 numbers.json（判据 C 腿据此比漂移）
    $PY -B _temp/r287m/_sync_meta.py     # 补 api_blob_sha / license_body_restricted_hits
    # 3) 复算入口（判据）
    $PY -B _temp/r287m/check_r287m.py --only C
    # 期望：PASS C [R287M-C-LICENSE] spdx=Apache-2.0 class=permissive cap=5 hits=0 drift=no gate=可并入
    #       [MCP-PREP-SUB] only=C ok=PASS

## 读数表（全部实测，附判据出处行号）

| 读数 | 值 | 出处 |
|---|---|---|
| classify_body → spdx | Apache-2.0 | 05-exec/r114_replacement_scan.py:464 函数 + :417 指纹表（"Apache License" + "Version 2.0" 双条件命中）|
| classify_body → 档位 | permissive | :464-492（无受限命中、无 restricted 名单命中）|
| RESTRICTED_PHRASES 命中 | 0 | :456-458 六条措辞全不中 |
| license_class(spdx) | permissive | :635-670 |
| license_class(spdx, body_class=permissive) | permissive（正文优先）| :646-651 注释即本仓 dify / Imbad0202 两反例 |
| LICENSE_CAPS[permissive] | 5（不降档）| :405 |
| 上游仓根 LICENSE 是否存在 | 不存在（contents 实测：README.md / THIRD_PARTY_NOTICES.md / skills / spec / template / .claude-plugin / .gitignore / .claude-plugin）| gh api repos/anthropics/skills/contents |
| gh api repos/anthropics/skills --jq .license | null（空输出，rc=0）| 现取 |
| gh api repos/anthropics/skills/license | HTTP 404（Not Found）| 现取；与 r263 记录的 release/license 404 同族 |
| r263 侧车 license 字段 | UNLICENSED | 06-benchmark/r263_declared_upstream_face.json rows[mcp-builder]；回填逻辑 = r114:225/332 的 or UNLICENSED |
| license_class("UNLICENSED") 无正文时 | none ⇒ 只看 API 字段会误判禁并入 | :653-654 |
| 本地 LICENSE.txt | 11345 B / sha256[:12] bc6b3af2f331 / blob 4f881c52d1f7 ⇒ **与上游字节级同一份** | 实测（_numbers.py git hash-object 双取）|
| 本地 LICENSE | 同上（同内容两份并存，11345 B 各一）| 实测 |
| 本地 NOTICE | 854 B，已声明改编 anthropics/skills + Apache-2.0 保留署名 | D:/global_skills/mcp-builder/NOTICE |
| 上游 skill 目录许可件 | skills/mcp-builder/LICENSE.txt 11345 B / blob 4f881c52d1f72f4cfb720e339e2d35c3058d01a9 | gh api contents |

## 判定链（照抄 r114 口径，不自造规则）

1. **API 字段为 null ⇒ r263 记 UNLICENSED，但不得据此直接禁并入。** GitHub 的 license 端点按仓根 LICENSE
   解析，而 anthropics/skills 仓根没有许可件（实测 contents 清单），许可在**子目录级**
   skills/mcp-builder/LICENSE.txt，正文是标准 Apache-2.0 全文。这正是 r114 立「正文优先」的原因
   （docstring 具名 dify / Imbad0202 两例：NOASSERTION 被 API 报成 unknown 而正文才是真相）。
2. classify_body(正文) = Apache-2.0 / permissive，受限措辞 0 命中。
   注意：标准 Apache 文件头自带 "YOU MAY NOT USE THIS FILE EXCEPT IN COMPLIANCE WITH THE LICENSE"，
   r262 二版已把泛化 "MAY NOT USE" 从措辞表删掉（否则全 Apache 仓被误杀）⇒ 本次 0 命中是真 0，不是漏检。
3. 档位 ∈ {copyleft, weak-copyleft, restricted}（本门另把 none/unknown 保守拦）才写「不可并入」；
   本档 permissive ⇒ **可并入**。
4. 并入义务：保留 Apache-2.0 许可正文与署名（NOTICE）。本地两份许可件与上游字节一致、NOTICE 在位
   ⇒ 换装（新增 node_mcp_server_v2.md + 8 hunk 补丁）**不需要改任何许可件**，许可面零改动。
5. 上游件本体不含新增许可风险：新增件 node_mcp_server_v2.md 是同仓同许可文档（同目录同级许可覆盖）。

## 换装前后许可不变量（建议 Lead 落盘后复跑）

    $PY -B _temp/r287m/check_r287m.py --only C   # 许可门
    test -f D:/global_skills/mcp-builder/LICENSE.txt -a -f D:/global_skills/mcp-builder/NOTICE && echo LIC_FILES=OK || echo LIC_FILES=MISSING
    # 期望末行 LIC_FILES=OK（许可件不许被换装动作删除）

状态标注：本文件所有读数 = 已实测（2026-10-30）。
