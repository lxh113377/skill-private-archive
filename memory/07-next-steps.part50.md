# 07-next-steps.part50.md

<!-- 本卷为 07-next-steps.part49.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P1·下轮首推 W-34（r52 新立）】** 报告正文关键数字改为**引用台账字段**而非抄写数值（动因 = r52 实测：对手 README 正文数字 0–1 个、徽章 1–5 个，量化结论交给每次作业再生的产物；我方 06-benchmark 共 939 处数字声明、0 个再生背书，于是 r38 那个含 PR 的 open_issues 能无命令跑 12 轮）。做法 = 先做 3 个试点（OVERDUE 现值 / 台账行数 / 常驻门数），由 `05-exec/r38_debt_aging.py` 与 `run_gates.py` 打印「可引用句柄」行，报告只写句柄与字段名；量一轮后再决定是否推广。 【r53 裁决=执行完毕（限定）｜make_handles + resolve_handle 落地于 05-exec/r38_debt_aging.py：句柄含 artifact/field/selector/command 四件，解不出（文件缺/形状不全/台账空）一律 None 不返 0，并做「写台账→解句柄」闭环守恒（h7/h7b）；账龄尺输出增打「可引用句柄」行供报告直接引用。残余 = 历史面 755 处数字按 R241 不回改，只保证 r53 起新增数字走句柄。注册第 16 道门 handles_readme_fixtures】

- [x] **【P1·待办 W-35（r53 新立）】** 入口文档对证据面的可发现性：r53 实测 `06-benchmark/` 有 60+ 份机器可读件，而 `README.md` 指向它的链接数 = **0**（对手 `addyosmani/agent-skills` 一份 README 挂 50 个文件链接）。已补「证据面导航」节（19 链接 / 死链 0，由 `05-exec/r53_handles_fixtures.py` h8/h9 锁死）；残余 = 六阶段产物地图那批**纯文本路径**尚未改成链接（逐节替换，禁为凑数造死链）。 【r54 裁决=执行完毕｜README 读序 5 条与六阶段产物地图的纯文本路径全部改为可点链接，全文链接 24 个（其中指向 06-benchmark 19 个）、死链自检 0；可发现性由 05-exec/r53_handles_fixtures.py 的 h8/h9 常驻断言（链接数>0 且 <=2 倍件数，禁凑数堆死链）】

- [x] **【P1·待办 W-36（r53 新立）】** 指标取值源必须声明**再生周期**，超期取到值也要判 unknown：r53 暴露的真问题不是那 3 个假阳性陈旧面，而是"没有任何地方声明每个指标多久必须重算"——`catalog_grand_chars` 的源件若真 33 轮不重跑，棘轮就在跟历史快照比，而数字看起来完全正常。做法 = `inject_ratchet_baseline*.json` 每指标加 `max_age_days`，`ratchet_gate` 取值时校验证据件 mtime，超期 ⇒ 该指标进 unknown（不阻断任务，守 r25 否决）。取值 `python 05-exec/ratchet_gate.py`。 【r54 裁决=执行完毕｜ratchet_gate 新增 METRIC_SOURCES/METRIC_REFRESH_DAYS/source_age_days/face_metric_refresh/refresh_status，9 指标逐个声明预算且 CLI 打印「再生周期」行；STALE 转 unknown（陈旧源件不配当现值参与棘轮比对），UNVERIFIED 不转（活体扫描本无源件，判红等于逼我造假源件）；真机 9/9 在预算内 ⇒ 接线时误报率 0，夹具 12 例含 g5/g7 配置形态反例】

- [x] **【P1·待办 W-37（r54 新立）】** 把「再生预算」从代码里搬进可校验面：现在 `METRIC_REFRESH_DAYS` 只存在于 `05-exec/ratchet_gate.py`，契约看不见它——有人把某项删了，`collect_metrics` 会静默少一项而不报错。做法 = 让 `inject_ratchet_baseline*.json` 承载 `refresh_days` 字段（与 ratchet_metric_set_matches 同一集合全等口径），代码只读不写；先写夹具反例（基线里缺某指标预算 ⇒ 判红）看红再接线。 【r56 裁决=执行完毕｜预算已入基线件 refresh_days（schema v1→v2），契约 ratchet_refresh_days_matches 做集合全等；--update 不得改写预算面；夹具 10 例含无静默回落反例。取值 python 05-exec/r56_budget_fixtures.py】
