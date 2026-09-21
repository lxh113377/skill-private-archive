# 04 - 核心文件地图

> 本文件记录项目关键文件及其作用。sync 命令会自动更新入口文件部分。
> 归档类型：快照（整体复制到归档）

<!-- SYNC_AUTO_GENERATED_START -->
### 文档: `README.md`
<!-- SYNC_AUTO_GENERATED_END -->

## 核心逻辑文件
<!-- 手动补充（2026-09-22 实测回填） -->
| 文件 | 作用 | 类型 |
|---|---|---|
| `README.md` | **工作区入口**：读法顺序 + 六阶段产物地图 + 门禁复跑命令 | 文档 |
| `memory/07-next-steps.md` | **跨会话唯一入口**；P0 唯一真相源（handoff 致命纪律 #1） | 状态 |
| `memory/05-feature-status.md` | 已完成 / 进行中 / 阻塞 | 状态 |
| `memory/AGENTS.md` | P-1 项目级 Skill 绑定表（命中即加载，防漏用） | 绑定 |
| `TODO.md` | 阶段状态总表（**索引，非入口**）；指向 `memory/07` | 索引 |
| `01-scan/scan_all.py` | 阶段0/1 唯一可复跑工具：三源交叉裁定 + 四维机器扫描 | **脚本**（20,274B） |
| `00-scope/自建skill清单.md` | 自建清单裁定结论（HIGH/MID/LOW + 排除信号） | 结论 |
| `00-scope/注册表失真条目.md` | 注册表 `user_created` 失真条目 | 结论 |
| `01-scan/scan_report.md` | 阶段1 四维机器扫描报告 | 结论 |
| `02-review/*_精读.md` | 6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他） | 结论 |
| `03-audit/自建skill优化审计报告.md` | 阶段3 全量审计结论（P0 25 项分级） | 结论 |
| `04-plan/实施计划.md` | 阶段4 逐项实施计划（含验证命令 + 回滚手段） | 计划 |
| `04-plan/工作流专项建议.md` | 阶段5 工作流专项（闭环落地率 / footer / direct_map 5 步） | 计划 |
| `05-exec/README.md` | 执行证据索引（19 个 patch JSON ↔ P0 编号 ↔ commit） | 索引 |
| `05-exec/第3轮执行报告.md` | 2026-09-22 四维体检 + 建议清单 + 待确认破坏性项 | 报告 |
| `01-scan/overlap_raw.txt` | 阶段1 原始重叠扫描件（282,977B，**中间产物**，待归档） | 原始件 |

## 配置文件
<!-- 手动补充（2026-09-22 实测回填） -->
| 文件 | 作用 |
|---|---|
| `.gitignore` | 生成物 / 备份叠层 / 编辑器元数据（含 `.codebuddy/`）/ 密钥四类边界；已实测生效 |
| `.aiexclude` | 让 AI 搜索跳过噪声目录（init 自动生成） |
| `.codebuddy/plans/自建skill体系优化审计_33834ceb.md` | 平台生成的会话计划（.gitignore 已排除，不入库） |
