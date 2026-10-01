# 07-next-steps.part49.md

<!-- 本卷为 07-next-steps.part48.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P0·下轮首推 W-30（r51 新立）】** 把「外部数字须带独立第二路取值」从 JSON 证据件推广到**非 JSON 引用面**：`06-benchmark/*.md` 报告与 `comparison.md` 里的数字目前只靠人工带命令。做法 = 先跑只读统计（数字紧邻 60 字内无可复算命令者计数）量出误报率，再决定是否进阻断链（r25 用户否决拦任务的闸门 ⇒ 未量出低误报前只报告不阻断）。取值起点：`python 05-exec/baseline_contract_scan.py` 已管住 json 面，md 面另写 `r52_md_claim_face_scan.py`。 【r52 裁决=执行完毕｜新工具 05-exec/r52_md_claim_face_scan.py 已落地并注册为第 15 道门（md_claim_face，走 r52_mdclaim_fixtures 20 例）。窗口 ±12 行与单位集按抽样 14 条判读确定；全量敞口 60.4%→17.8%，可整改面 184 声明 / 0 敞口（历史面 755 处按 R241 只登记不回改）】

- [x] **【P1·待办 W-31（r51 新立）】** 契约 pattern 自身的陈旧面检查：r51 实测 `debt_aging_r3*.json` 让 r40 起的全部证据件落在受检面外（零命中判红抓不到，因为它仍命中十份旧件）。做法 = 在 `validate_contracts` 里对每个 pattern 计算「命中集内最大轮号」与当前轮号之差，超阈值即打印陈旧告警（先打印不阻断，量一轮误报再接线）。 【r52 裁决=执行完毕｜face_pattern_staleness 已进 baseline_contract_scan 且首跑抓到 3 个陈旧面（skill_structure_rubric 最新 r29 落后 22 轮等）；三态反例 t29–t32 入 r19 夹具；按 r25 否决只报告不判红，陈旧后果另立 W-33 清根因】

- [x] **【P1·待办 W-33（r52 新立）】** 契约 pattern 里**写死轮号**的形态须清掉：`noise_falsepositive_r37_*.json` 把 r37 编进 pattern ⇒ 按构造永远看不到任何后继件（该判据只会随轮次变成僵尸声明）。改法 = pattern 去轮号（`noise_falsepositive_r*.json`）或把件迁 archive 并在契约注明"一次性基线，不参与逐轮看守"。取值 `python 05-exec/baseline_contract_scan.py` 看 ⚠️ 陈旧面 行（r52 首跑抓到 3 个，另两个是 skill_structure_rubric 与真陈旧）。 【r53 裁决=执行完毕（并改判据）｜pattern 已去轮号（noise_falsepositive_*.json），但真根因不是命名而是「名字≠新鲜度」：face_pattern_staleness 首版按 _rNN 判，把本轮刚重跑的日期名件（catalog_attention_tax_2026-09-24.json，值已从 45,250 降到 45,173）误判成落后 33 轮，3 个陈旧面全是假阳性；已改 mtime 优先 + 轮号兜底 + basis 标注，真机陈旧面 3→0，夹具 t33/t34 锁死两向。取值 python 05-exec/baseline_contract_scan.py】

- [x] **【P1·下轮首推 W-34（r52 新立）】** 报告正文关键数字改为**引用台账字段**而非抄写数值（动因 = r52 实测：对手 README 正文数字 0–1 个、徽章 1–5 个，量化结论交给每次作业再生的产物；我方 06-benchmark 共 939 处数字声明、0 个再生背书，于是 r38 那个含 PR 的 open_issues 能无命令跑 12 轮）。做法 = 先做 3 个试点（OVERDUE 现值 / 台账行数 / 常驻门数），由 `05-exec/r38_debt_aging.py` 与 `run_gates.py` 打印「可引用句柄」行，报告只写句柄与字段名；量一轮后再决定是否推广。 【r53 裁决=执行完毕（限定）｜make_handles + resolve_handle 落地于 05-exec/r38_debt_aging.py：句柄含 artifact/field/selector/command 四件，解不出（文件缺/形状不全/台账空）一律 None 不返 0，并做「写台账→解句柄」闭环守恒（h7/h7b）；账龄尺输出增打「可引用句柄」行供报告直接引用。残余 = 历史面 755 处数字按 R241 不回改，只保证 r53 起新增数字走句柄。注册第 16 道门 handles_readme_fixtures】
