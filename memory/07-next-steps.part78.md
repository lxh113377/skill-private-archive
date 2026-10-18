## r113 摘要 (二)

⑥ **三笔升级的复算验证（防「断言先于执行」X-30）**：TDD `upstream_only 20→11`（合入 9 行）、obsidian-bases `3→0`（转 UP_TO_DATE）、hyperframes-registry `3→2`；本地内容零丢失（TDD local_only 43→43 / registry 6→9 净增 / obsidian 5→0 且**移除的是原错误示例** and/or/not 三键并存）。镜像面 4 件 SHA256 全等（只同步自家文件，未跑全局 `-Fix`）。⑦ **需求 2/3 首份交付**：GitHub 五查询并集 **132 仓**检索面（`gh api search/repositories`，产物 06-benchmark/gh_search_r113_2026-10-18.json）+ 15 仓**客观测量**（技能件数/blob/workflow/tests/docs/治理件，产物 candidate_measure_r113_2026-10-18.json）+ 8 族逐族结论（6 族保留本地、2 族定向升级已完成）+ **五维评分矩阵**（锚定字段：skill_md_n / workflow+tests / license+平台 / readme+docs / stars+pushed）。⑧ **需求 4 首份交付**：`04-plan/迁移替换方案_r113_2026-10-18.md`（逐件优先级 / 时间节点 / 验证标准 / 回滚预案 + 三条前置红线）。⑨ **需求 5 首份交付**：`05-exec/r113_quarterly_audit.py`（单命令编排既有四判据 + 上游元数据；**反「取数失败销毁证据」** = 任一步失败保留旧主产物、痕迹入 sidecar）+ `04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md` + 首份产物 `06-benchmark/quarterly/2026Q4/`（`[QUARTERLY:PASS]`，11 仓元数据 OK=11 / UNVERIFIED=0）。⑩ **需求 6 的可复算表达**：主指标 M1 身份可判定率 30.2%→69.2%（+39.0pp / 相对 +129.2%）+ N1–N4 反指标（四档守恒 / 门禁 35 门 PASS / 本地内容不丢失 / 镜像一致）全为持平或改善；**边界如实登记**：M1 是判定面覆盖率而非任务成功率，禁写成「任务质量提升 129%」。

- [x] R112-2 余 11 件 UPGRADE_REVIEW 逐件裁决（升级 / 保留本地 / 人工合并三选一并附行号证据）（由 flow 登记；状态: todo）

- [x] R112-1 补 127 件 unknown 的上游身份（declared 优先，inferred 次之；目标 unknown 127 → <100，守恒仍 182）（由 flow 登记；状态: todo）
