# README.md — R287m mcp-builder 合并增量换装材料（Lead 收件箱）

生成：2026-10-30 · 子代理件 · 写面仅本目录（`_temp/r287m/`）· 受管根零写入（已实测：
`git -C D:/global_skills status --porcelain -- mcp-builder` 行数 = **0**，且 find -mmin -70 命中 0 个文件）。

## 判据命令与期望末行（已实测）

    cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _temp/r287m/check_r287m.py
    [MCP-PREP] hunks=8 old_unique=8/8 upstream_sha=49b2fe48f339 license=Apache-2.0 gate=PASS

落盘后复验（期望 gate=PASS）：

    … -B _temp/r287m/verify_landed.py
    [MCP-LANDED] dead=0 args_ok=1 version_ok=1 v2=1 gate=PASS

⚠ 换装**落盘后** `check_r287m.py` 的 A 腿会转 FAIL（old 已被替换掉，不再存在于盘上）——
这是设计使然（它是「换装前」的材料自证件），届时以 verify_landed.py 为准，不要据此判材料坏。

## 四件交付物

| 文件 | 说明 | 关键读数（现取）|
|---|---|---|
| `upstream_node_mcp_server_v2.md`（不入库：`.gitignore` 豁免，clone 后按 newfile_manifest.json 的 repo/ref/path 用 gh api 重建并核 sha256[:12]=49b2fe48f339） | 上游新增件原文（gh api base64 解码，未改一字节）| 35171 B / 747 行 / sha256[:12] `49b2fe48f339` / git blob `5d61f896d970…` == gh api .sha |
| [patch.json](./patch.json) | rule_editor replace 材料（8 hunk，全为逐字切片）+ `_verify`（逐 old 断言 `text.count(old) == 1`）+ coordinates + new_file | hunks=8，all_pass=true，old/new 均出自 difflib 切片（`gen_patch.py`）|
| [verifications.md](./verifications.md) | 换装后验证判据（死链 / 参数可执行 / 版本三处一致）+ 六条负控实测输出 | 判据①②③各带命令与期望末行 |
| [license_gate.md](./license_gate.md) | 许可门：r114 单源 classify_body + license_class | spdx=Apache-2.0 / class=permissive / cap=5 / 受限命中=0 ⇒ **可并入** |
| [check_r287m.py](./check_r287m.py) | 判据本体（六腿 A-F）| 只读受管根，补丁在内存重放 |
| [verify_landed.py](./verify_landed.py) | 落盘后复验器（复用 check_r287m 的 D/E/F 腿）| 换装前跑它 gate=FAIL（有牙，已实测）|

## 直接喂 rule_editor 的数组件（一份一次调用）

    patch_SKILL.md.json            # 7 hunk，target = D:/global_skills/mcp-builder/SKILL.md
    patch_node_mcp_server.md.json  # 1 hunk，target = …/reference/node_mcp_server.md

为什么要拆（读实现所得）：`rule_editor.op_replace` 先 `resolve(args.file)` 再
`_plan_patches(read_text(path), items)` ⇒ 一个 `--file` 只吃一个目标件，跨件必须分次调用。
`check_r287m.load_patch()` 会机械对账数组件与 patch.json 的 `(id, old, new)` 逐字同源 + 集合等价；
漂移负控已实测（`_drift_test.py`：改一个字符 ⇒ `FATAL: 数组件与 patch.json 漂移: NODE-V1-BANNER`，rc=1，用完即复原）。

## 落地配方（本件不落盘，按红线 2 交 Lead）

    # 顺序硬约束：先建新件，再打补丁（反序 = 5 条死链，已实测 _probe_order.py）
    cp _temp/r287m/upstream_node_mcp_server_v2.md D:/global_skills/mcp-builder/reference/node_mcp_server_v2.md
    sha256sum D:/global_skills/mcp-builder/reference/node_mcp_server_v2.md      # 期望 49b2fe48f339… 开头
    # 然后（rule_editor 不能创建新文件：resolve() 实测 sys.exit「安全区内文件不存在」）
    python D:/global_skills/A-memory-start/references/rule_editor.py replace --file mcp-builder/SKILL.md --patch _temp/r287m/patch_SKILL.md.json --dry-run
    python D:/global_skills/A-memory-start/references/rule_editor.py replace --file mcp-builder/SKILL.md --patch _temp/r287m/patch_SKILL.md.json --no-commit
    python D:/global_skills/A-memory-start/references/rule_editor.py replace --file mcp-builder/reference/node_mcp_server.md --patch _temp/r287m/patch_node_mcp_server.md.json --no-commit
    python D:/global_skills/A-memory-start/references/rule_editor.py commit --file mcp-builder/SKILL.md --file mcp-builder/reference/node_mcp_server.md --desc "R287m mcp-builder 同源拉平 anthropics/skills@ca45fc496a34（#2087，TS SDK v2）"
    # 再按红线 5：rule_editor.py gates（mirror/noise/evolution）+ disk_registry_diff 三类全 0
    … -B _temp/r287m/verify_landed.py     # 期望 gate=PASS

编号预检已只读探测过（`_probe_collide.py`）：补丁文本喂 rule_editor 自己的 RE_R_NUM/RE_V_NUM/_hist_numbers
⇒ R:[] V:[] ⇒ 落盘不会触发 R231 fail-closed，**无需 --allow-collide**。

## 坐标（从判据出处复算抄录，非记忆）

- repo=`anthropics/skills` · ref=`main` · sha=`ca45fc496a3436251f191354091d557da31c15b5`（2026-10-28T19:20:38Z，
  标题 `Update mcp-builder skill: teach v2 of the MCP TypeScript SDK (#2087)`，files=3）
- upstream_path=`skills/mcp-builder`；新增件 `skills/mcp-builder/reference/node_mcp_server_v2.md`
- 读数出处：`06-benchmark/r275_three_channel_intersection.json` rows[28]（layer=L4、
  l4_subreason=PATH_LOCALIZED_NOT_EXECUTABLE、ch1.rel=UNKNOWN_UPSTREAM_RELEASE、ch3.verdict=UPSTREAM_MOVED）、
  `06-benchmark/r264_sidecar_semantics.json`（semantics=SAME_LINEAGE；注：r264 主件 rows 内**无** mcp-builder，
  实测 hits=0，它只测 obra/superpowers@v7.0.1）、`06-benchmark/r271_version_channel2.json`、
  `06-benchmark/r263_declared_upstream_face.json`（license=UNLICENSED 为 API null 回填，见 license_gate.md）
- 复算脚本（留档）：`_extract275.py`、`_extract_coords.py`、`_numbers.py`、`_sync_meta.py`、`_lic_gate.py`
- 取上游原文：`_decode.py`（gh api contents ?ref=main 的 base64 解码 + sha/bytes 记录）
- 生成补丁：`gen_patch.py`（difflib 切片，人不手打一个字符）+ `_shape_patch.py`（整形 + 拆件）

## 状态标注

- **已实测**：判据六腿全绿、四条负控全红得有牙、MISSING_V2 复算、上游 blob 三方相等、许可门、
  数组件漂移负控、rule_editor 不能建新件、编号预检零碰撞、受管根零写入、先补丁后建件会造 5 条死链。
- **部分实测**：换装后 verify_landed 的真盘 gate=PASS 只在**内存预览树**（`_landed_preview/`）验过
  （真盘落盘是 Lead 的动作，本件无权执行）。
- **未实测**：rule_editor 真提交与三门禁/disk_registry_diff（按 brief 禁止项与本件写面，未跑）。
