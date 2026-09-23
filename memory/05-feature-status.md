# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- 代码质量五维审查 + A/B/C 批执行（2026-09-23 r8，3 只读子代理并行审查 → 用户按钮选 A+B/C 批）：**A 批** = `apply_patches.py` 4 修（①CRLF 双重换行 P0：读取归一化+按原行尾复原 ②临时文件+os.replace 原子写 ③写盘事务化+失败自动回滚 ④行区间重叠预检+相对路径按补丁目录解析）——正反夹具 **12/12**（CRLF/LF/BOM 保持、重叠拒绝、只读写失败自动回滚、跨目录相对路径）；`scan_all.py` 8 修（frontmatter CRLF ×2、死链分支不可达+切片错 P0×2、quotepath、QW/CC 正则、meta.json fail-open 留痕、references isdir、walk 剪枝）+ 清单打分文案对齐——py_compile ×3 + 双阶段 dry-run exit 0。**B 批** = 120/151 双口径注记（user_created_audit.json / direct_map_dead_targets.json 加 `_registry_epoch`）+ AC-OBS-03 校正注 + 清单 L7 打分说明校正注 + 根 README overlap_raw 陈旧引用清理 + 01-scan README 裸数组标注与 r8 漂移登记 + 05-exec README 补丁双格式 runner 标注。**C 批** = user_created_audit.py `generated` 动态化；truth_constants 失真按焚诀红线只登记（07 r8 条）。**重要发现**：scope 复跑 = 56/21 vs 冻结 51/26（切分漂移非笔误，冻结件不动，待裁定）
- 09 节补建 + noise_lint 修补文档同步收口（2026-09-23 r7，zijian.json 中断会话续接）：① 遗留台账 6 项实测复核——受管根在途清零、焚诀 stub-pass 14/14 两项销账，09 缺节与文档同步两项阻塞解除；② 项目侧 `flow --init` 补建 `memory/09-workflow-state.md`（check PASS，status 9 节全 filled，review 9/9）；③ 受管根 `7ebd682`（rule_editor 三文件白名单收口，A-get-memory 他人在途零夹带）：A-project-handoff 3.50.0→**3.51.0** + version-history 补 V3.51.0 条目（d88b5ee 补登记，零代码变更）+ commands.md §11 补二级扫描豁免口径；④ gates mirror/noise/evolution/stub 四门禁全绿；新登记他人在途（A-get-memory 1 条 + 焚诀 36 M + GM 日志 footer 格式漂移）见 07 r7 条

- 上游根因修：**noise_lint 二级扫描三处口径一致性修补**（2026-09-23 第 13 轮 r6，受管根 `d88b5ee`，仅 1 文件 44 行）：① 一级豁免传递（一级判 `quarantine` 的顶层项不再深扫，顺带留档免重复调 git）；② 二级子项自身命中 `QUARANTINE_DIRS`（如 `_bak`）即跳过（与一级同一判定入口）；③ junction/符号链接顶层项跳过二级扫描（内容归目标根口径，覆盖不丢只去重，新增 `is_reparse_dir()`）；验证 = 层a 隔离桩 **14/14**（含修前/修后对照：修前报 `sub/_bak`+`ignored_dir/_bak`+`jnk/_bak` 三处假阳性 vs 修后 0；三类真散落修前修后均判 VIOL）+ 层b `noise` 四根复跑 **`[GATE:noise-pass]`**（焚诀 38/15/**0**）；本项目 savepoint 由被拒 → **安全落盘**；⚠️ 版本行/版本历史/`commands.md §11` 三处文档同步**暂缓**（并行会话已占用 3.49.0 正在改这三个文件，避免二次夹带）
- 上游口径落地：**06-约束卷纳入「条目归档自愈」**（2026-09-23 第 13 轮 r5，A-project-handoff **V3.48.0**）：① 设计 = `TRIM_ENTRY_TARGETS`（07+05+06）与 `SPLIT_TARGETS` **解耦**——06 含红线等必须始终可见章节，通用拆卷会搬走它们，故只走条目归档；② 判据 = `closed_marker`（已修复/已闭环/已解除/已销账 且 不含 未修复/未闭环/部分解决/待观察…）+ **留痕章节白名单**（只迁「已知 Bug」「技术债」）+ **分区不变式**（归档∪留守 = 原文，只搬不移除/不复制）；③ 配套：承接卷就地续拆、CLI 迁后复跑拆卷、`volume_health` 活载卷只读可见；④ 验证 = 层a 隔离桩 **34/34** + 既有 V3.47.0 桩 15/15 复跑全绿（07/05 零回归）+ 层b 真机（焚诀 06 零变更；本项目 06 13,075B→7,097B 迁 13 条、行守恒 missing=0/dup=0、红线留主卷）；⑤ 收益 = 本项目注入壳 **33,029B → 26,594B（-6,435B/轮）**，其中 06 节 12,148B→6,182B

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）
- **卷3** `05-feature-status.part3.md` — 已完成：2026-09-22 第 4 轮（D1–D5 授权项执行结果）
- **卷4** `05-feature-status.part4.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷5** `05-feature-status.part5.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷6** `05-feature-status.part6.md` — 已完成：2026-09-22 第 10 轮（Step 0 首次实跑 + 记忆层回写 + 阶段1 补齐 + B1–B7 授权执行）
- **卷7** `05-feature-status.part7.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷8** `05-feature-status.part8.md` — 已完成：2026-09-23 第 13 轮（性能瓶颈三维实测分析）
- **卷9** `05-feature-status.part9.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷10** `05-feature-status.part10.md` — 05-feature-status 分卷（R199 自动拆卷）

