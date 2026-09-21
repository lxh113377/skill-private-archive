# 07-next-steps.part1.md

<!-- 本卷为 07-next-steps.md 的延续 -->

## 已完成

- [ ] 收尾 A-get-memory 反哺（写 D:\global_memory 需 PowerShell 通道 + 写后读回验证 R213）
- [ ] **待你裁定（灰区）**：`local-asr`/`local-computer-use`/`local-realtime-translator`/`local-tts`/`local-txt2img` 的 `meta.json` 含 `download_count`+`author`+`download_url` = **Intel 分发样例包**，非从零编写。当前按市场件排除（自建 85）；若你认为它们算「在用即自建」，我改回（自建 90）
- [ ] 阶段4 首批：批量替换 `C:\Users\37533\Desktop\焚诀\` → `Desktop\workspace\焚诀\`（覆盖 13+ 处 P0 死链，全库单一最高杠杆）
- [ ] 修正权威平台口径行：`A-memory-start:134/153/157` 仍写「HM 已卸载 2026-08-08」→ 用户 2026-09-14 确认 HM 已回归，需改回在役端（属阶段4 规则文件改动，走 rule_editor.py）
- [ ] 阶段2 收尾后：确认 fenjue-advisor-scoring / fenjue-cc-audit-cycle 退役前有无反向引用（用户已确认二者日常不再使用）
- [ ] 阶段1 补跑：`attention_sim.py` + `content_snr.py` + `negative_tag_audit.py`；扫描脚本补「通配符引用（如 `wf_*.ps1`）」死链检测
- [ ] 阶段4 首批：A族 P0 整改（A-project-handoff 拆卷、A-get-memory 两条死链、版本号漂移、平台名清理）— 走 rule_editor.py + 三门禁

## P1 — 应该做
- [ ] 阶段2：按族分批全量精读 102 个自建 skill（A族 → fenjue/审计族 → local/story → 其他）
- [ ] 裁定 LOW 灰区 33 个归属（阻塞阶段2 范围）

## P2 — 可以做
- [ ] direct_map 误命中复核（「优化自建skill」误直连 vp-perspective-audit）
- [ ] A-memory-start Step 0.6 补 PowerShell `&` 调用符与 venv 降级链

## 最近对话摘要
- 2026-09-14 — 完成阶段0：三源交叉裁定自建清单。判定逻辑经两轮修正（①`user_created=false` -4 权重过重误杀本地目录 → 改为硬排除市场信号；②补 frontmatter homepage 第四源）。最终 自建 102（HIGH 68+MID 34）/ EXCLUDE 34 / 灰区 33 / 注册表失真 42。同时 init 项目记忆（10 文件 + P-1 绑定表 11 行）。

## 已完成
<!-- - [x] 已完成的事项 -->
- [x] 项目记忆 init（10 文件 + P-1 绑定表）— 2026-09-14
- [x] 权威源定位：unified-skills-index.json / platform-oc.json / disk_manifest.json 三源与字段口径实测 — 2026-09-14
- [x] 阶段0 范围裁定：scan_all.py --stage scope 落盘 3 文件（清单/失真条目/scope_result.json）— 2026-09-14
- [x] 阶段1 四维扫描：scan_report.md + scan_result.json + overlap_raw.txt；两轮判据修正（死链/触发词误报）— 2026-09-14
- [x] 阶段2 第1批 A族精读（5 个）→ 02-review/A族_精读.md；新抓 wf_*.ps1 死链、版本漂移 13 个、248 个 .bak 违反自家轮转规则 — 2026-09-14
- [x] 撤销错误升级建议「init 后生成 EXPERIENCE.md」：实测 Step 7 V4.6.0 已降级不落盘；派生新条目 = A-project-handoff init 提示仍引用已降级行为 — 2026-09-14
- [x] 阶段2 第2批：fenjue族 5 + 审计族 15 精读落盘；审计族给出 15→8 合并决策；定位 vp-perspective-audit 误命中根因（缺负向边界）— 2026-09-14
- [x] TODO.md 阶段待办总表建立（含 2 项阻塞待人工裁定）— 2026-09-14
- [x] **阶段4 A3/A4/A5 三项完成**（commit `bc225b3`）：A3 补 `version: 1.0.0`×9（4 个市场件按新口径跳过）／A5 `openclaw-dual-gate-quality-audit` description 收窄 + 新增负向边界段／A4 回填 7 个 local `meta.json` description（清单漏 `local-vram`；性质修正 = 上游 marvis 打包 bug，不参与路由）。`[GATE:mirror-pass]` missing=0 mismatch=0，工作区 status=0 — 2026-09-14
