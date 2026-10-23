# 07-next-steps.part134.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R157-5（r157 登记，P3，到期=季度巡检）** **跨坐标系与 Windows 引号层级并入排障速查表**（学习计划 G-4a）：本轮 4 次同类成本——① os.path.join 在 Win 拼反斜杠查 tar 的 POSIX 成员名致 KeyError（正解 posixpath）；② tarfile 未 close 就 os.remove 致 PermissionError WinError 32；③ PowerShell 5.1 丢弃空串参数致 git config --local http.proxy  静默无效（正解 subprocess argv 或字面引号对）；④ 生成脚本里 GOOD = ..., 尾逗号把 str 变 tuple 致 replace TypeError。取值：python ./_temp/r157_g5.py、python ./_temp/r157_proxy.py。 【r160 裁决=降级（转长期看守）｜第 2 次到期；跨坐标系/引号层级四条已由 r157 学习计划 G-4a 成文（本轮 r160 自抓 1 处同族：run_code 里用 new 作变量名触发 TS 解析错 Expected ident——JS 保留字不能作标识符，已改 replacement），并入排障速查表属文档维护动作，随季度巡检一并处理。禁滚新到期日（X-17）】

- [x] **R157-6（r157 登记，P2，到期=季度巡检）** **判据零命中须附阳性对照腿**（学习计划 G-5a，#32 第①/④形态再犯）：死链判据 v1 报 superpowers 0 条 / anthropics 3 条，逐条复核发现 v1 自身两处缺陷（目录集漏中间层、行内反引号未跳）⇒ 0 不可信；修成 v2 才得可信读数（1 条且为模板占位符 [Title](URL) / 0 条）。建议：给 md/链接类判据补「输出 0 之前须有一次已知非空面复跑」的常驻腿，**前置是先量误报率**（对标 r137 分级原则，防把并行会话挡在门外）。取值：python ./_temp/r157_g7.py（v1）⇄ python ./_temp/r157_g8.py（v2）。 【r160 裁决=降级（转长期看守）｜第 2 次到期；「零命中须附阳性对照」纪律已由 #32 形态表 + 第 61 门 selftest_census_face 的自证三腿（无齿面/死旗面/对照面）承载——普查面本身就是「输出 0 之前先证报得出非 0」的常驻化。前置「先量误报率」仍未做（属接线前必修项），故不升为阻断门；禁滚新到期日（X-17）】

- [x] **R157-7（r157 登记，P3，不封顶）** **上游 issue 前置三门**（学习计划 G-6）：本轮四条候选全部被自家实测证伪，未提交 issue——性质不是凭据缺口（token 实测 login 可读、含 repo scope、限流 4987/5000）也不是平台缺口（gh 与 curl 双路可用），是没找到真缺陷。三门 = ① 阳性对照 ② 上游实物复核 ③ 查重（实测 /search/issues?q=repo:obra/superpowers+AskUserQuestion 返 33 条，未证伪极可能提重复且错的）。按 X-10 禁到期自动关闭，机会型长期挂。取值：python ./_temp/r157_tok.py、python ./_temp/r157_g1.py。 【r160 裁决=保留｜机会型不封顶（X-10 禁到期自动关闭）；前置三门已成文，本轮无新候选可提（r160 全程在本仓内工作，未产生对上游的断言）。数值面 = 上游仓出现本账号提交的 issue 数（当前 0，取值 gh api 只回显身份不回显 token）】

