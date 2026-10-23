# 07-next-steps.part59.md

<!-- 本卷为 07-next-steps.md 的延续（r109 I-7 人工重切，零增减） -->

> 上一卷：`07-next-steps.part58.md`；本组首卷 `07-next-steps.part57.md` 含路由。

- [ ] **【P1·承接 R60-3（r108 xlsx 半边执行完毕）】** xlsx 可跑验证腿 1→3（同尺判据 `^(python|node) scripts/` ≥3 成立）+ 2 条实测坏腿如实登记（`validate.py` 对 .xlsx 落 `case _:` 打印不支持、`recalc.py` Windows `AF_UNIX` 崩；根因读自自带源码），版本 1.0.1→1.0.2 并新建 `## 版本历史` 段（改前无该节 ⇒ C13 此前对本件免疫）；主文件被自身新增顶破 12,288B（`skill_size_report.check()` 点名「新增超限技能 xlsx」）⇒ 同轮分卷 `references/verification.md` 收口回 11,703B WITHIN。提交 `2960ac1b`+`7bdf8e6d`。**一手教训**：我先按 docx 形态写 5 条腿，逐条实测后 2 条虚报 ⇒ **验证段每条腿必须自跑并留回执；跑不通的写进「跑不通」小节，禁删掉不提**。取值：`python -c "import io;print(sum(1 for l in io.open(r'D:/global_skills/xlsx/SKILL.md',encoding='utf-8') if l.startswith(('python scripts/','node scripts/'))))"`（期望 ≥3） 【r108 裁决=执行完毕｜pdf 0 条腿的同类缺口另条在册 I-8】
- [ ] **【P2·新立 I-8（r108 对标同尺）】** `pdf/SKILL.md` 可跑验证段实测 **0 条**（同尺 docx=17 / xlsx 改后=3）。判据与 xlsx 同形态。前提同 R60-3：走 rule_editor + version bump + 历史行 + rebuild 窗口。取值：`python -c "import io;print(sum(1 for l in io.open(r'D:/global_skills/pdf/SKILL.md',encoding='utf-8') if l.startswith(('python scripts/','node scripts/'))))"` 【r108 登记】
- [ ] **【P2·新立 I-5（r108 对标确定落后项）】** 受管根 `D:\global_skills` 根**实测 0 件 .md**（`readdir` 全量，非搜索命中）vs 对手 spec-kit 根 12 件 .md（含 CONTRIBUTING/SECURITY/SUPPORT/DEVELOPMENT/CHANGELOG）/ anthropics 2 件 ⇒ 「技能仓的规矩」目前只活在 A-skill-manager 铁律与 memory 台账里，新会话或外部贡献者必然漏项（本轮 W-45 就是该缺口的产物）。**不擅立**：CONTRIBUTING 属全库规矩外显，须老大点头口径（谁可改/走什么链/怎么测）。取值：`Get-ChildItem D:\global_skills -Filter *.md -File` 【r108 登记·待裁】
- [ ] **【P2·新立 I-6（r108 可发现性差距）】** 判据面命名与对手不可比：spec-kit 389 / superpowers 87 个 `tests/` 文件，我方 `05-exec/` 130 个 py（其中 29 个 `*_fixtures.py` 常驻门）**但无 tests/ 目录** ⇒ 功能等价、可发现性差。方案 = 加一份「门⇄夹具⇄判据」索引（README 或 docs/），**禁物理搬迁**（会把 29 道门的 script 路径全打挂）。取值：`ls 05-exec/*_fixtures.py | wc -l`（实测 29） 【r108 登记·待裁】
- [ ] **【P1·承接 W-32（r108 复算，未动）】** `inject_union_bytes=86,900B` 超硬顶 65,536B（+21,364）。本轮复算：`ratchet_gate.py` 打印同值；焚诀 C31 侧口径余量 1,569B（2.4%）已亮「再有一次技能增长即破硬顶」⇒ 该告警**已从装饰性变成临界面**。三选一仍待老大点名（实减 / 重设硬顶并逐因归因 / 显式豁免）。取值：`python 05-exec/ratchet_gate.py` + managed venv `python 焚诀/eval/verify_truth_consistency.py` 读 C31 行 【r108 裁决=保留（转裁定）｜第 4 轮未消】

## r108 对既有台账的复算校正（R241：原文不改，只在此具名）
