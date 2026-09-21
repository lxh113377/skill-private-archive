# 05-feature-status.part3.md

<!-- 本卷为 05-feature-status.md 的延续 -->

## ✅ 已完成（2026-09-22 第 4 轮：用户授权 D1–D5，全部执行）

- **D1 修 3 处门禁判据缺陷**（受管根 `7cc7d4d`，`A-project-handoff` **V3.42.0**）：AC 计数剔 HTML 注释（假通过）/ 新增 `has_feature_entries()` 兼容「`## ✅ 已完成` + 普通列表项」（假阴性）/ `status` 先判 sync 占位再计数（口径矛盾）；三函数**下沉 `common.py` 单一真相源**。验证：层a 隔离桩 **11/11**、层b 集成含对照（生效路径 PASS ＋ 注释-only 反例仍被拦）、本项目 `review` **56% → 100%**、三门禁全绿、焚诀 `verify` **15 PASS**
- **D2① 直连表修正**（焚诀 `bf5e284`，已推送 SHA 一致）：收窄 vp 过泛 pattern（去裸 `提出建议`）；**系统性复扫出 7 死目标 / 11 条死直连**并全数重指或删除；死目标复扫 **0**；回归套件 **ALL PASS**（T2 直连 **47/47**、T3 top1 死件 → `A-skill-manager`）；连带修 **6 处**过期测试期望
- **D2② 注册表 `user_created` 复核（口径已裁定）**：注册表口径 = **120 条**（verify C1/C2/C10 三方守）；A 类（死件）**0**、B 类（true+市场信号）**0** → 09-14 报的「42 条失真」在当前口径**不复现**；C 类 85 条**不可判为失真**（反证 `canvas-design`）；2 条真脏数据登记 P2。附带量化：磁盘含 `SKILL.md` **151** vs 注册表 **120**（仅磁盘有 31；**仅注册表有 0**）；阶段0 自建清单 90 → 仅 **60** 在册
- **D3 归档与轮转**：`.rule_backup` 仅 1 组超阈值（`A-memory-start.SKILL.md` @09-19 共 10 份）→ 保留 5、**迁移（非删除）** 5 至 `D:\global_memory_archive\_trash\backup-rotation\A-memory-start\2026-09-19\`；总数 **40 → 35**；`overlap_raw.txt`（283KB）→ `archive/`；随后 `sync` 刷新目录树

## ✅ 已完成（2026-09-22 第 6 批：用户追加三项）

- **修 `rule_editor.py commit --fix-mirror`**（受管根 `7d8a8e1`，`A-memory-start` **V10.62.0 → V10.63.0**）
  - **根因（✅已实测）**：该 flag 的修复**只挂在 `_do_commit` 的失败分支**，而**三仓（`D:\global_skills` / 焚诀 / `D:\global_memory`）`.git/hooks` 实测只有 `post-commit`（自动 push）、没有 `pre-commit`** ⇒ `_do_commit` 永远 rc=0 ⇒ 该分支是**死代码**；文档「已挂 `hooks/pre-commit`」属**设计意图而非既成事实**
  - **修法**：改为**提交前主动三步** —— ① 只读检查（`check-skill-mirror.ps1` 不带 `-Fix`）② 漂移则 `-Fix` ③ **复核**，复核仍失败则**显式告警**（不静默）；新增 `_mirror_check_only()`（脚本不存在时返回 True 且告警，不把「检查不可用」误报为「镜像漂移」）
  - **验证（两层含对照，✅已实测）**：反例基线 = 应用补丁后镜像实测 `missing=0 mismatch=3` + `[GATE:mirror-fail]`；生效路径 = 同一 `commit --fix-mirror` 自动打印「检测到镜像漂移 → 自动 `-Fix` → 镜像已补齐（复核通过）」→ `gates` = `mirror=pass`，**零手工操作**
  - 落盘 **R270**（区内追加，速查区 **6 不变**；282 行 / 64,000B）+ 通用判据「任何『提交后修复』型开关都必须有『提交前主动检查』路径；自查一行 `Test-Path <repo>/.git/hooks/pre-commit`」
  - 收口：`coldstart --check` 6 行全等、焚诀 `verify` **16 PASS / 0 FAIL**（C13 已对齐 V10.63.0）
- **v2 清单 LOW 30 / EXCLUDE 43 维持不变**（用户裁定）→ 自建口径定格 **77 条**，记入 `01-goal.md` 范围裁定 + `06-constraints.md`
- **31 件纳入版本化 —— 已授权，粒度待定**：入库前体检发现全量 **57.6MB** 中约 **44MB 为第三方依赖与产物**（openvino `bin/` 29.6MB + `wheels/` 9.8MB + `nltk_data/` 5.0MB + `.pyc` 0.3MB；另有 `tests/` 素材 7.5MB、`assets/` 参考音频 3.6MB），无 `node_modules` / 嵌套 `.git`；因 git 历史**不可瘦身**，须先定粒度再入库
