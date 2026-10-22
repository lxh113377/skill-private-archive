# 07-next-steps.part85.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R120b-7（r120b 登记，P2）【r123 定位 / r124 收口】** root_face runner 内外不一致：**根因不是并发，是夹具三处真缺陷**。① 汇总 JSON 提取用正则 `\{.*\}`，贪婪式在 stdout 多字典时串味、非贪婪 `.*?` 跨行匹配到嵌套内错误闭合点（JSONDecodeError column 71）、无嵌套 `[^{}]*` 匹配不到（汇总是嵌套字典）⇒ 正则对嵌套结构不可靠，改为 `_extract_summary()` 括号配平。② f10 判据要求键名相同，而 handoff.py 的汇总键是**传入参数原样**（"." vs "自建skill优化"）属显示层 ⇒ 恒假红，改为比较**值**。③ f12 抓到我自己留下的 `.bak`（正是它要防的形态），已清。修后 **12/12 全 PASS**，36 门 PASS=37。

- [x] **R120b-3（r120b 登记，P1·转办）** `DOMAIN_KEYWORDS.system` 补中文「提示词」（r120 定位的域失配根因：中文「提示词」在 creative 表不在 system 表）。属焚诀 eval 只读红线 ⇒ 只能转办，提案第 8 条已在册。 【r124 裁决=挂账至 r126｜转办件：DOMAIN_KEYWORDS.system 补中文「提示词」属焚诀 eval 只读红线，提案第 8 条已在 transmit_proposals.json；归属方未动作前本仓无实施面】 【r127 裁决=挂账至 r128｜转办件：DOMAIN_KEYWORDS 中文「提示词」属 eval 只读红线，提案第 8 条在册】 【r127 裁决=降级｜REPEAT 升级裁决：DOMAIN_KEYWORDS 中文「提示词」同属 eval 只读红线，提案第 8 条在册两轮未动作——降级为长期看守】

- [x] **R120b-5（r120b 登记，P1·新增）【r123/r124 定性收口】** 「该看哪个指标」的答案已被 r123 生产实测裁决：**两个指标回答不同问题，都该看**——`top1 翻转`答「命中率」（官方分口径），`margin`答「抗扰动稳健性」。r120b 与 r122 结论相反不是因为谁错，而是**问题不同**。r123 实测：3 件语料调整官方分三轮均 90.1% 不变（top1 口径零效果），但 margin +80%/+169%（稳健性真实提升）。⇒ 固化为 R123-3（分列报告）+ `05-exec/r123_margin_cf.py` 三态判定（HARDENED_AND_ROBUST / MARGIN_ONLY / NO_GAIN，禁二值）。另一教训：r122 单行 encode 沙箱对 baseline 高估 33%-105% 是**方法论缺陷**（R122-2 已修），与指标选择无关。

- [x] **R120-1（r120 登记，P2）** 把「域失配面」纳入季度巡检常驻段（现为一次性脚本 `_temp/r120_dom_partition.py`）：21.9% 是结构性面，会随注册表增删漂移，一次性量过即过期。取值：`python 05-exec/r120_dom_partition.py --json <件>`（脚本需先从 _temp 固化到 05-exec）。 【r124 销账：r120b 已把域失配面固化为 05-exec/r120_domain_face.py 并接入季度巡检第 ⑪ 段（r120b 报告 §1），一次性脚本已退役 ⇒ 本条完成】

- [x] **R123-6（r123 登记，P1；r130 二次改号避撞——R123-4/R123-5 均已被并行会话占用）** margin 沙箱口径校准自检：凡用沙箱做决策的轮次，先跑一次「修好后 baseline 与生产实测 3/3 一致」才算校准（`python 05-exec/r123_margin_cf.py` 的 baseline 对 `_temp/r122_margin.py` 的生产读数）。本轮教训：单行 encode 对 baseline 高估 33%-105%，未校准的沙箱把有益改动误判成无益。 【r127 收口：r125 机器腿判据自抓（A-java-problem 乱配）+ 修后校准验证（baseline 与生产 3/3 一致）即本条「校准自检」的实践；销账】
