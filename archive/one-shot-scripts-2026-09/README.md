# 归档：一次性已服役脚本（2026-09-23 r9 整编）

> 处置：`git mv` 自 `05-exec/`（历史可回滚）；这些脚本使命已完成、清单硬编码当轮实测值，**勿直接复跑**（目标文件已变化）。
> 分类依据见 2026-09-23 五维审查（可复用工具 4 个留 05-exec + 共用库 `_lib.py`；一次性 11 个归档此处）。

| 脚本 | 服役轮次 | 用途摘要 |
|---|---|---|
| `B1-clean-negative-tags.py` | 第10轮 | 负标签清理（GHOSTS 清单硬编码 09-22 实测值） |
| `B6-normalize-registry.py` | 第10轮 | `oc-dispatch-exec-guard` 注册表字段归一化 |
| `B7-fix-registry-domain.py` | 第10轮 | `ican-frontend-design-system`/`testing` 残缺条目修复 |
| `B7-regen-domain-map.py` | 第10轮 | domain_map 快照一次性重生成 |
| `direct_map_dead_targets.py` | 第10轮 | 直连表死目标复扫（输出 direct_map_dead_targets.json） |
| `R272-verify.py` / `R272-verify-e2e.py` | R272 轮 | review 交叉校验判据层 a/b 验证 |
| `R272b-boundary.py` / `R272b-survey.py` / `R272c-narrow.py` | R272 轮 | 判据边界标定 / 全库勘察 / 收窄验证 |
| `unretire_31.py` | 第4轮 | 31 件入册（注册表 120→151；⚠️ 其 _meta 文案数字失真已登记 07 待焚诀校正） |
