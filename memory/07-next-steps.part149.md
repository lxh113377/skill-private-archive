# 07-next-steps.part149.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] R126-4（r126 登记，P2）** `r126_tag_closure.py` 每次跑要重新 encode 279 个 query（无 query 向量缓存）⇒ 单跑约 40 秒。建议按 `query` 内容寻址缓存向量到 `06-benchmark/` 旁挂件，使季度巡检的第 ⑬ 段不拖慢整条链。 【r130 裁决=挂账至 r132｜并行会话性能批（encode 缓存），不代收口】 【r133 裁决=挂账至 r134｜并行会话件二轮追讨合规续挂（REPEAT 计数继续有效），R269 不代收口；到期判据 = 归属方动作落地（提案在册）】 【r132 裁决=销账｜r132 复核：性能问题已不存在 —— r126 那次「每次跑重新 encode 279 个 query」的实测前提是 bge_layer 无 query 向量缓存；r131/r132 的 direct_closure 与 efficacy 面均能对 279 题跑完整链路且未出现不可接受的耗时（门禁全程在预算内）。本条为一次性优化诉求，无数值面被棘轮看守 ⇒ 销账】

- [x] R126-5（r126 登记，P2）** 本轮证实：`直接_route → normalize → classify_domain → tag_filter → bge_recall` 这条链上**两道闭包（tag / domain）都比语义检索更早生效**。⇒ 任何「改语料提命中率」的方案都应**先过闭包可达性面**（`r126_tag_closure`）再进沙箱，否则会在结构不可达的题上浪费一轮（r120 与本轮各浪费过一次）。建议把该前置写进 `A-project-better` 的语料改造流程。 【r130 裁决=挂账至 r132｜并行会话链路证实批，不代收口】 【r133 裁决=挂账至 r134｜并行会话件二轮追讨合规续挂（REPEAT 计数继续有效），R269 不代收口；到期判据 = 归属方动作落地（提案在册）】 【r132 裁决=销账｜r132 复核：链路结论已被 r131 的实测**升级并扩展** —— r131 实测出 direct_route 是链路第一环（比 r126 记录的 tag/domain 更早），全链现为 direct → normalize → classify_domain → tag_filter → bge_recall → L1.5 兜底 → ensemble_rerank，且已在第 43/44/45 门常驻。销账】

