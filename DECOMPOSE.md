# DECOMPOSE · r281（需求6 的任务级缺口）

## 前提实测（先证「经典 A/B 做不了」，不假装做了）
- 外部评手 oracle CLI 不存在（which oracle 无；~/.workbuddy/binaries 只有 PortableGit/libreoffice/node/python）⇒ 无 LLM 评手；
- .dsh 下会话日志实测是 transport/route 事件（lane/status 502），不是任务级使用记录；
- 无 tool_skill_matrix_latest.json（使用计数面缺件）⇒ 真实使用反馈只能靠件内自述（需求 1 的已知限制）。
⇒ 结论：同任务跑两遍打分不可复算，本面不做该形态；改做**工件级 A/B**：改前/改后两版文本（git 取）
   做六维机械 rubric + 真实脚本冒烟 ⇒ 可复算、无需 LLM。

## 分解
| # | 件 | 可独立验收 | 写面 | 输入可预固定 | ≤45min | 去处 |
|---|---|---|---|---|---|---|
| 1 | 六维机械 rubric 盲评（三件 × 两态） | ✅ 件 + 末行 | 06-benchmark/r281_artifact_ab.json | ✅ 三件基准 sha 已定 | ✅ | **派 G**（避免我出尺自己量） |
| 2 | 冒烟真跑（ui-ux search.py 产物、FS 备份版指针可达） | ✅ 命令+rc+产物 | 06-benchmark/r281_smoke.json | ✅ | ✅ | Lead 自干（与 R278 面同写面，D7.2 单写者） |
| 3 | 收口 | ✅ | 本仓 | ✅ | ✅ | Lead（最终答复自留） |

30 秒卡：① 是（G 盲评 vs 我冒烟，写面互不相交）；② 是；③ 是（文本层 + 产物层）；④ 是；
⑤ 发 1 件（G）+ 2 件自留；⑥⑦ 七项与判据末行负控见 _temp/r281g_brief.txt；⑧ 我复跑 G 的统计器正腿与两条负控。

skip_reason（负申报）：#2 严格串行 + 写面冲突（06-benchmark/r278_landing_effect.json 本会话在写）；#3 决策本体。
