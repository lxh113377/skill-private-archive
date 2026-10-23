# 07-next-steps.part130.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R151-6（r151 登记，P2·转办焚诀 eval 侧，到期=季度巡检）** **ingress 新建件抢答 6 条**（query「写个脚本定期备份数据库」exp=tencent-cos-skill__skillhub got=libreoffice-base，读数含重复）：期望侧判定权在焚诀 eval，本仓 r148 已判语料处方 0/2 有效**不得照搬**（#46）。取值：`python 05-exec/r133_new_skill_ingress.py --json <件>` 读 face.new_skill_preempt_n。 【r156 裁决=降级（转长期看守）｜期望归属判定权与训练集在焚诀 eval 侧，本仓无可开处方（r148 实测 0/2 有效，#46 禁照搬；X-14/X-22 已给可解析取值面）。数值仍由 r133 ingress 的 new_skill_preempt_n 看守，禁滚新到期日（X-17）】

- [x] **R151-7（r151 登记，P2，到期=季度巡检）** **归属判据可达性仍无告警链**（R149-4 同族）：函数改名/删除时本面 rc=2 显形但不通知适配，靠人肉发现。建议并入 `r113_quarterly_audit.py` 固定步。取值：`python 05-exec/r149_derived_freshness.py` 不可达态首行。 【r156 裁决=降级（转长期看守）｜r151 已把该缺口从「静默」推进到「rc=2 UNVERIFIED + 首行显形 + S6/S7/S8 三腿常驻」，剩余部分需接季度巡检（r113）而非本仓独立件；不滚新到期日（X-17），由第 56 门不可达态看守】

- [x] **R151-8（r151 登记，P1，到期 r153）** **引用面补「取值命令须真出产物」腿**：本轮自抓——报告与提案里把条件③的取值写成 `python 05-exec/r128_w47_reconcile_fixtures.py --json <件>`，而该夹具**无 argparse**（取值：`Select-String -Path 05-exec/r128_w47_reconcile_fixtures.py -Pattern argparse`，实测 0 命中），--json 被静默忽略、不落快照（实测 Test-Path 该快照名 => False）。**md_claim_face 判「敞口 0」放行 ⇒ 它只验「有没有命令」，验不出「命令形态对不对」**。建议补腿：引用面里指向 `--json <件>` 的命令，须能在 05-exec/ 找到 argparse 声明或该产物真实存在。已修两处：`06-benchmark/transmit_proposals.json` 的 acceptance_r151（2 处）与本报告 §3/§6b。取值：`python 05-exec/r52_md_claim_face_scan.py --json <件>`。 【r156 裁决=降级（转长期看守）｜本轮已把两处失真改掉且 md_claim_face 敞口复算 = 0（取值：python 05-exec/r52_md_claim_face_scan.py --json <件>）。补「命令须可解析出 argparse 声明/产物真实存在」属引用面增强，非阻断项；由该门敞口读数常驻看守，禁滚新到期日（X-17）】

