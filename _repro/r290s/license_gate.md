# license_gate.md — security-audit ← cloudflare/security-audit-skill 换装许可门（R289-5 第②步）

> 结论：**已实测 · spdx=MIT class=permissive cap=5 restricted=0 ⇒ 允许并入（MAY_MERGE）**。
> 单源纪律：档位只由仓内唯一分类器 `05-exec/r114_replacement_scan.py` 的 `classify_body` + `license_class` + `LICENSE_CAPS` 产生（R260-5「读实现优先于写探针」：本目录**不重复实现**任何指纹表或名单，重复实现 = 两处口径漂移，r262 一手踩过）。

## 1. 函数签名（现读，非猜）

    inspect 实测：classify_body(text_upper) -> (spdx|None, 档位, 受限措辞命中 list)
                  license_class(lic, body_class=None) -> 档位（有正文证据时正文优先于 API 字段）
                  LICENSE_CAPS = {copyleft:1, weak-copyleft:2, restricted:1, unknown:4, permissive:5, none:5}

取值命令（可复跑，一次跑完签名 + 判定）：

    C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r290s/license_gate.py
    C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B _repro/r290s/_probe_r114.py   # 含 inspect.signature 逐字打印

实跑输出（逐字抄录，2026-10-30 本机）：

    [LICENSE] api_spdx=MIT body_spdx=MIT body_class=permissive final_class=permissive cap=5 restricted_hits=0
    [LICENSE] hits=[] bytes=1078 sha256=e598e694aa506650c7192d5ea3be0e50aca0d356ea00551c53429f0b01eb6391
    [LICENSE-PREP] spdx=MIT class=permissive cap=5 restricted=0 gate=PASS

签名实测行（`_probe_r114.py` 输出，逐字）：

    SIG classify_body (text_upper)
    SIG license_class (lic, body_class=None)
    SIG parse_sidecar (text)

调用形态注意（实测）：`classify_body` 内部只做空白折叠、**不再 .upper()**，所以必须传 `LICENSE_TEXT.upper()`；传原文会判成 `unknown`（假阴方向危险）。

## 2. spdx / class / cap 读数

| 项 | 值 | 取值命令 |
|----|----|----------|
| API `license.spdx_id` | MIT | `gh api repos/cloudflare/security-audit-skill --jq "{full_name,default_branch,spdx:(.license.spdx_id // \"NONE\"),pushed_at,archived}"` |
| 正文指纹 spdx（classify_body） | MIT | 上方 license_gate.py |
| 正文档位（body_class） | permissive | 同上 |
| 归一档位（license_class(MIT, body_class)） | permissive | 同上 |
| cap（LICENSE_CAPS） | 5 | 同上 |
| 受限措辞命中 RESTRICTED_PHRASES | 0 命中（空列表） | 同上 |
| 仓库归档状态 | archived=false | 同 API 命令 |

两侧一致（API 与正文互证，非只信字段）：GitHub 字段会骗人（r261 实测两例 dify / Imbad0202 报 NOASSERTION 实为受限），
本件按 R261-6 口径**必须读到正文**再定档 —— 本次两侧同为 MIT/permissive，才允许放行。

## 3. 受限命中明细（逐文件扫拟并入正文）

理由：只看 LICENSE 不够，difify 型缺陷正是「LICENSE 名义宽松 + 正文自带商业条件」。故对每个拟并入件再跑一遍 `classify_body`：

| 件 | 字节 | 档位 | spdx | 受限措辞 |
|----|------|------|------|----------|
| DATA-ISOLATION-AND-LIFECYCLE.md | 7798 | unknown | null | 0 命中 |
| HUNTING.md | 22446 | unknown | null | 0 命中 |
| LICENSE | 1078 | permissive | MIT | 0 命中 |
| README.md | 6950 | unknown | null | 0 命中 |
| SKILL.md | 22026 | unknown | null | 0 命中 |
| VALIDATION-AND-REPORTING.md | 17843 | unknown | null | 0 命中 |
| report-schema.json | 14494 | unknown | null | 0 命中 |
| validate-coverage-ledger.cjs | 33522 | unknown | null | 0 命中 |
| validate-coverage-ledger.test.cjs | 28483 | unknown | null | 0 命中 |

档位 `unknown` 在这里的含义 = 「该正文里没有许可指纹」（散文与代码本就不该有），
**不是**受限证据；真正禁并入的是 restricted / copyleft / weak-copyleft / none 或命中受限措辞（`RESTRICTED_PHRASES` 6 条实测全部 0 命中）。
复算命令：同 §1 第一条（`[SCAN]` 行 + `license_scan.json`）。

## 4. 能否并入 · 结论

- **允许并入**（MAY_MERGE）：spdx=MIT class=permissive cap=5 restricted=0，且 risky_files 为空（实测）。
- 归属义务（MIT 唯一条件 = 保留版权与许可声明）：随件带 `LICENSE`（1078B，sha256=e598e694aa50 前 12）或
  在吸收分卷头写明 `cloudflare/security-audit-skill` 谱系 + 上游 sha —— 本材料已在 `staging/security-audit/references/upstream-cloudflare-sec.md` 卷头做到（署名 + 坐标 + 行区间对照表）。
- 与本地既有谱系不冲突：本地 `.upstream` = `trailofbits/skills`（CC-BY-SA-4.0，copyleft 档），
  本次**不并入** trailofbits 侧新内容，只并入 MIT 侧增量 ⇒ 不产生「copyleft 正文混入 permissive 增量」的归属纠缠（实测：`parse_sidecar` 对新增注释行同解，见 §5）。
- 许可门先行：门未过 ⇒ 后续 ③④ 步不得动手。本门 PASS（已实测）。

## 5. 侧车改动可证惰性（已实测）

    取值：python -B _repro/r290s/license_gate.py  # 末三行 [SIDECAR]
    实测：parse_sidecar(now)=["trailofbits/skills", null] parse_sidecar(after_patch)=同解 inert=True

含义：`patch_upstream.json` 往 `.upstream` 追加的是 `#` 注释行，漂移腿（`05-exec/r114_replacement_scan.py` 的 `parse_sidecar`）解析结果不变
⇒ 不会把 security-audit 的 upstream_repo 从 trailofbits/skills 改成 cloudflare（那是「换谱系」，本件只做「并入增量」，按 R265-3 以本地为壳）。
反例（实测）：若追加 `path: skills/security-audit` 行，`parse_sidecar` 第二元素会变成该路径 ⇒ 改变判定面，所以**禁止**这么写（本材料未这么写）。

## 6. 未完成项（如实）

- 上游无 version 字段（frontmatter 无 `version:`）⇒ 本地 2.0.1→2.1.0 是本仓自定递增，标 **未实测**（非上游口径）。
- `validate-findings.cjs` / 其余 12 个分卷未取入（净增量只需三能力）⇒ 不在本次许可门面内，无结论。
