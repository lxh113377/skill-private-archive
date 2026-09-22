# 05-feature-status.part8.md

<!-- 本卷为 05-feature-status 分卷（2026-09-23 第 13 轮，part7 将超 4KB 故新建） -->

## ✅ 已完成（2026-09-23 第 13 轮）

- 性能瓶颈三维实测分析（用户任务，约束=不改功能行为）→ `05-exec/性能瓶颈分析与优化方案.md`（commit `0d1f0af`）
  - 实测：每会话固定注入 ~146KB 上下文税（A-memory-start SKILL.md 68,676B / contract.md 44,847B / 项目注入壳 32,871B）；6 个 ⚙️ 速查区占主文件 67%（46,190B）；墙钟全健康（router 1.12s、gates 8.20s、noise 5.61s、status 0.08s、review 0.07s）；磁盘 2.14MB + GM 1.3MB 无压力
  - 结论：唯一真瓶颈 = 上下文注入税；P0 方案两项待授权（速查区迁 references / contract 拆分），P1 两项登记（注入壳瘦身 / router direct_hit 短路），P2 三项观察
  - 附带实测：`trim-shell` 判据盲区（不认普通 `- 描述` 已完成条目，05 主壳原样未动）→ R269 登记上游债；`split --check` 判 05 主壳「索引壳，主卷不拆」= 设计内形态
  - 收尾：lessons.part34 新建（🟢 1 条）、GM 日志 + footer 块 `[GATE:evolution-pass]`（skill=3 建议=2）

### r2（2026-09-23 同日）：P0-1+P0-2 经用户授权执行收口

- ✅ **P0-1** A-memory-start/SKILL.md 六个 ⚙️ 速查区（46,195B / 67%）原字节切片迁 `references/quickref-browser-devtools / direct-map-pairing / cli-subprocess / current-state-history / fault-triage / delivery-consistency.md` 六卷，主文件留「⚙️ 速查区索引」指针区（区数 16→11）—— **68,676B → 24,759B（-64%）**，版本 **V10.66.0**（受管根 commit，8 文件白名单 + `--fix-mirror`）
- ✅ **P0-2** `references/contract.md` R-CURRENT 全文（17,669B）迁 `contract-rules-verification.md`、规则文件维护工作流（10,409B）迁 `contract-rules-maintenance.md`，主文件留条目索引 stub，**「contract.md R-CURRENT 第 N 条」锚点全保留** + MANDATORY READ 复杂行增补强制 `#07`—— **44,847B → 18,616B（-58%）**，版本 **V10.67.0**（受管根 commit，5 文件白名单 + `--fix-mirror`）
- ✅ 对照复测（两层）：生效路径 = gates `mirror=pass noise=pass evolution=pass`（stub=fail 为开工前既有债）+ 焚诀 verify 迁移前后均 **19 PASS / 0 FAIL**；反例两道防线实测仍拦 = 未提交态 `mirror=fail` 被拦（防线未放松）、编号预检对「R251 作条目首号」fail-closed 拦截后改语义表述放行（R262 判据生效）
- 效果：每会话固定注入（A-memory-start 主文件+contract）**113.5KB → 43.4KB（-62%）**；复杂任务另省 contract 细则面 ~26KB（改按需读两分卷）
- 收尾：升级建议 A-memory-start 一条转**已闭环**（证据 = SKILL.md#版本行 V10.67.0，对照=已取）；P1-3a/P1-4 留 07 P0 待授权

