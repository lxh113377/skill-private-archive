# 07-next-steps.part133.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R159-2（r159 登记，P1，到期 r161）** **gate_run_freshness 的自指延迟与聚合复跑耦合**：该门读**上一行**门禁台账，本轮修完的账下一轮才被承认（AGENTS 排障 row 7 明载「再跑一次即自愈」）。但聚合 runner 对 FAIL 门**自动复跑一次**并把复跑结果写回同一轮读数，导致「复跑 PASS 但初跑 FAIL」仍判真红 ⇒ 每轮固定贡献 1 项红，掩盖真红。建议：元门类（meta:True）豁免复跑判真红逻辑，或把「自愈延迟一轮」写进门表语义。取值：python 05-exec/r32_gate_freshness.py --json <件> 的 [FRESH:FAIL] 行 + runner 的 per_gate 复跑记录。 【r162 裁决=降级（转长期看守）｜r162 实测两次自愈成功（提交后首跑 FAIL=1 仅 freshness，原样重跑一次即 [GATES:PASS] PASS=63），自愈成本约 80s 门禁运行；该条要求的「元门类豁免复跑判真红逻辑」会同步削弱 R125 立的瞬态识别（并行会话常态），且本轮产能已用于 R159-1 收口。无数值面需棘轮看守（属流程纪律非度量），禁滚新到期日（X-17），由 AGENTS 排障速查 row 7 承载（再跑一次即自愈，别为消延迟改台账）。】

- [x] **R157-3（r157 登记，P2，到期=季度巡检）** **外部 HTTPS 失败须三路对账后才准定性为网络缺口**（学习计划 G-2a）：本轮一手——git push/gh api 三连 TLS 0A000126，我第一反应是「网络挂了」；实测 TCP 443 True、.NET SslStream 握手 Tls13 成功、代理 CONNECT 返 200、curl.exe（Schannel 后端）--noproxy 直连 api.github.com 成功，唯 Python ssl 一律 UNEXPECTED_EOF ⇒ 真因是本地代理截 Python TLS，绕行 = 仓内 --local 空代理覆盖（不动全局）。判据：任何「网络/凭据缺口」结论须同时给三条腿读数（TCP / schannel / Python-ssl），缺一律写未取证。取值：python ./_temp/r157_api.py、git config --local --get http.proxy。 【r160 裁决=降级（转长期看守）｜第 2 次到期；三条腿对账纪律已由 r157 学习计划成文，常驻化载体 = 季度巡检 r113_quarterly_audit.py（本仓不另建独立门，避免第二真相源）。数值面无棘轮指标可看守（属流程纪律非度量），故降级为看守型而非待办型；禁滚新到期日（X-17）】

- [x] **R157-4（r157 登记，P2，到期=季度巡检）** **对标结论的取值命令须指向上游实物**（学习计划 G-3a）：本轮候选 issue 被自家实测证伪——我拿本地 fork 的 brainstorming/SKILL.md（含 allowed-tools 与 AskUserQuestion）推断上游缺陷，拉上游 HEAD（codeload tar.gz，SKILL.md 10073 字符）实测两者皆无 ⇒ 那是我方定制。同族第二次（r94 跨仓截断读数）。判据：报告里任一对上游的断言，取值命令须含 codeload.github.com 或 api.github.com/repos/<owner>，禁本地副本充数。取值：python ./_temp/r157_g1.py。 【r160 裁决=降级（转长期看守）｜第 2 次到期；「取值命令须指向上游实物」已成文于 r157 学习计划，常驻载体 = 季度巡检抽样复核 + md_claim_face（第 25 门）对 live 报告的取值命令检查。无数值面需棘轮看守，禁滚新到期日（X-17）】

