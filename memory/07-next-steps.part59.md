# 07-next-steps.part59.md

<!-- 本卷为 07-next-steps.md 的延续（r109 I-7 人工重切，零增减） -->

> 上一卷：`07-next-steps.part58.md`；本组首卷 `07-next-steps.part57.md` 含路由。

- [ ] **【P1·承接 R60-3（r108 xlsx 半边执行完毕）】** xlsx 可跑验证腿 1→3（同尺判据 `^(python|node) scripts/` ≥3 成立）+ 2 条实测坏腿如实登记（`validate.py` 对 .xlsx 落 `case _:` 打印不支持、`recalc.py` Windows `AF_UNIX` 崩；根因读自自带源码），版本 1.0.1→1.0.2 并新建 `## 版本历史` 段（改前无该节 ⇒ C13 此前对本件免疫）；主文件被自身新增顶破 12,288B（`skill_size_report.check()` 点名「新增超限技能 xlsx」）⇒ 同轮分卷 `references/verification.md` 收口回 11,703B WITHIN。提交 `2960ac1b`+`7bdf8e6d`。**一手教训**：我先按 docx 形态写 5 条腿，逐条实测后 2 条虚报 ⇒ **验证段每条腿必须自跑并留回执；跑不通的写进「跑不通」小节，禁删掉不提**。取值：`python -c "import io;print(sum(1 for l in io.open(r'D:/global_skills/xlsx/SKILL.md',encoding='utf-8') if l.startswith(('python scripts/','node scripts/'))))"`（期望 ≥3） 【r108 裁决=执行完毕｜pdf 0 条腿的同类缺口另条在册 I-8】
