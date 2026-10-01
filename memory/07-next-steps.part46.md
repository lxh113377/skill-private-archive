# 07-next-steps.part46.md

<!-- 本卷为 07-next-steps.part45.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P0·下轮首推 W-18（r46 新立）】** 此后所有「补标/回写」类一次性脚本一律改走 `python 05-exec/r46_mark_verdict.py --key <锚点> --round <NN> --verdict <裁决｜原因>`，禁再出现行号索引写入；违反即视为 W-9 同族缺陷复发（工具已不接收行号，绕开即手工写，手工写无读回验证）。 【r49 裁决=执行完毕（持续生效）｜r47 12/12、r48 3/3、r49 5/5 全部经写入器落标（备份件在 05-exec/mark_backup），零手工行号写入】

- [x] **【P0·下轮首推 W-16（r45 新立，优先级最高）】** 任何写记忆标记的临时脚本都必须复用 `r38_debt_aging.find_item_line()`（标题锚点，命中数 != 1 即拒写并报告），禁用行号索引写入。实证据：H-3″ 项三轮标记后裁决标记数仍为 0（W-9 真因）。复现：`python 05-exec/r38_debt_aging.py --json /tmp/x.json` 看 overdue 明细。 【r49 裁决=执行完毕｜唯一入口 05-exec/r46_mark_verdict.py 已注册为常驻门（run_gates id=mark_verdict_fixtures），本轮 5 条裁决全部经它写入；r49 追加第⑥重对账与混合行尾错位根因修（夹具 t9/t10）】

- [x] **【P0·下轮首推 W-14（r44 新立，优先级最高）】** 给 REPEAT 立棘轮第 9 指标 repeat_debt_items。存在理由（D59）：本轮 OVERDUE 从 16 压到 1 里有 11 条是靠「降级为长期看守」实现的；若降级项没有独立指标，「降级」就成了新的免检通道，等于把债务换个格子。取值面 by_class.REPEAT，须与 overdue/deferred 同等 fail-closed。 【r46 裁决=挂账至 r49｜契约分代必填需先设计，本轮产能给了 W-16 工具化】 【r49 裁决=执行完毕（并纠正 r46 误挂）｜第 9 指标 repeat_debt_items 已于 r45 落地（提交 8d7fb56，取值面 05-exec/ratchet_gate.py 的 _debt_class_state）；r46 却在本条头部写了延期、原因文本讲的是 W-17 —— 本轮到期追讨抓到，已立 W-22 做写时对账】

- [x] **【P0·本轮落地 W-22（r49 新立）】** 裁决写入器加第⑥重对账：条目**自身编号**已被近期提交主题宣布落地却仍写延期 ⇒ 拒写（动因 = r46 我把 W-17 的延期写到已落地的 W-14 行上，3 轮后才被到期追讨抓到）。 【r49 裁决=执行完毕｜第⑥重对账已落地于 05-exec/r46_mark_verdict.py 的 landed_contradiction + item_own_id，且**本轮首跑即拦住我自己的 W-14 裁决**（因由文本引用了旧标记原文，随即加头部锚定修精度）】
