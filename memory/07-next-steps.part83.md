# 07-next-steps.part83.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R122-3（r122 登记，P2）【r123 已固化】** 对抗场景测试：已并入 05-exec/r123_margin_cf.py —— 把该件 domain 临时改成错误域，量「域错分后是否仍 hit」。判定口径三态（HARDENED_AND_ROBUST / MARGIN_ONLY / NO_GAIN），禁二值：margin 提升但对抗翻车 = MARGIN_ONLY 禁落地（提的正是脆弱面）。

- [x] **R120-2（r120 登记，P2）** `domain_exposure` 二分判据（掩护/暴露）常驻：区分「潜在脆弱」与「真实伤害」，防下轮又拿 21.9% 当缺口数（r120 实测 59 题域失配里仅 4 题真实暴露、1 题真失败）。 【r124 销账：domain_exposure 二分判据（掩护/暴露）已入 r120_domain_face.py 的 exposure 子面（exposed_n/real_fail_n 双数），r120b 报告 §1 ⇒ 本条完成】

- [x] **R120-3（r120 登记，P2；r123 收口：部分恢复）** 域暴露题语料加固：**生产实测裁决** pixelle-api-ensure 0.0596→0.1073（+80%）与 data-visualization 0.0533→0.1434（+169%）**有益，已保留**（受管根 fccabff）；brainstorming 0.0991→0.0865（−12%）**有害，已回滚**。⚠️ 过程两轮翻转如实留痕：r122 落地 3 件（f957117）→ r123 首轮回滚全部（3760ce0）→ r123 复测生产 margin 发现回滚回错 → 恢复前两件。根因 = r122 的 margin 沙箱只 encode description 单行，而生产语料是 SKILL.md 前 800 字符（build_indexes.py 明文口径），单行编码对 baseline 高估约 2 倍。修复 = 05-exec/r123_margin_cf.py（候选 description 换回原文取前 800 字再 encode，与 build_indexes 同源）+ 对抗腿（域错分后是否仍 hit）；验证：修好沙箱 baseline 与生产实测 3/3 完全一致。官方分三轮状态均 90.1%/276/291 不变。

- [x] **R120-4（r120 登记，P2）** `route_trace` 生产面纳入巡检：r120 首次分析即证明「缺口在合成题面不在真实使用」（332 唯一真实 query / LOW 仅 3），该面应每季复量。 【r124 销账：route_trace 生产面已固化为 05-exec/r120_trace_face.py 并接入季度巡检第 ⑫ 段，带守恒与规模口径警示（r120b 报告 §3）⇒ 本条完成】

- [x] **R133-1（r133 登记，P1）** W-47 对账 t1 假绿 1 条（gsap 做滚动触发动画：exp=gsap，route=libreoffice-draw）：**根因 = 并行会话今日注册的 LibreOffice 系 5 件改变了 tag/bge 打分**（「Draw/流程图」触发词抢答），判据快照 tag_closure_r127 是旧语料时代产物。归属：LibreOffice 5 件注册方（并行会话）——需重跑 tag_closure 对账快照 + 判据面同步。取值：`python 05-exec/r128_ruler_reconcile.py --face 06-benchmark/tag_closure_r127_2026-10-20.json --verdict-field actually_hit --json <件>`（实测 一致=278 假绿=1）。R269 不代修。 【r137 裁决=挂账至并行会话收口（LibreOffice 件注册方）｜R269 不代收；到期判据 = 其 tag_closure 快照重跑后 t1b 转绿】 【r137 裁决=挂账至 r137｜LibreOffice 件注册方（并行会话）收口：其 tag_closure 快照重跑后 t1b 转绿即销；R269 不代收】 【r140 裁决=挂账至 r142｜并行会话 R133-R135 系二轮追讨合规续挂（其 r136/r137/r138 已在收口进程中，见 DECIDED 45）；R269 不代收口】 【r151 裁决=销账｜r151 实测假绿 0：python 05-exec/r128_w47_reconcile_fixtures.py 8/8 通过（t1b 假绿腿由历轮 FAIL 转 PASS）；根因链（语料 182→190 → gsap 英文语料被中文件抢 → 源侧补中文 → 归属方 19:39 重建 BGE）已全线收口】
