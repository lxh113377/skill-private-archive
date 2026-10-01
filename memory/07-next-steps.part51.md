# 07-next-steps.part51.md

<!-- 本卷为 07-next-steps.part50.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P1·待办 W-35（r53 新立）】** 入口文档对证据面的可发现性：r53 实测 `06-benchmark/` 有 60+ 份机器可读件，而 `README.md` 指向它的链接数 = **0**（对手 `addyosmani/agent-skills` 一份 README 挂 50 个文件链接）。已补「证据面导航」节（19 链接 / 死链 0，由 `05-exec/r53_handles_fixtures.py` h8/h9 锁死）；残余 = 六阶段产物地图那批**纯文本路径**尚未改成链接（逐节替换，禁为凑数造死链）。 【r54 裁决=执行完毕｜README 读序 5 条与六阶段产物地图的纯文本路径全部改为可点链接，全文链接 24 个（其中指向 06-benchmark 19 个）、死链自检 0；可发现性由 05-exec/r53_handles_fixtures.py 的 h8/h9 常驻断言（链接数>0 且 <=2 倍件数，禁凑数堆死链）】

- [x] **【P1·待办 W-36（r53 新立）】** 指标取值源必须声明**再生周期**，超期取到值也要判 unknown：r53 暴露的真问题不是那 3 个假阳性陈旧面，而是"没有任何地方声明每个指标多久必须重算"——`catalog_grand_chars` 的源件若真 33 轮不重跑，棘轮就在跟历史快照比，而数字看起来完全正常。做法 = `inject_ratchet_baseline*.json` 每指标加 `max_age_days`，`ratchet_gate` 取值时校验证据件 mtime，超期 ⇒ 该指标进 unknown（不阻断任务，守 r25 否决）。取值 `python 05-exec/ratchet_gate.py`。 【r54 裁决=执行完毕｜ratchet_gate 新增 METRIC_SOURCES/METRIC_REFRESH_DAYS/source_age_days/face_metric_refresh/refresh_status，9 指标逐个声明预算且 CLI 打印「再生周期」行；STALE 转 unknown（陈旧源件不配当现值参与棘轮比对），UNVERIFIED 不转（活体扫描本无源件，判红等于逼我造假源件）；真机 9/9 在预算内 ⇒ 接线时误报率 0，夹具 12 例含 g5/g7 配置形态反例】

- [x] **【P1·待办 W-37（r54 新立）】** 把「再生预算」从代码里搬进可校验面：现在 `METRIC_REFRESH_DAYS` 只存在于 `05-exec/ratchet_gate.py`，契约看不见它——有人把某项删了，`collect_metrics` 会静默少一项而不报错。做法 = 让 `inject_ratchet_baseline*.json` 承载 `refresh_days` 字段（与 ratchet_metric_set_matches 同一集合全等口径），代码只读不写；先写夹具反例（基线里缺某指标预算 ⇒ 判红）看红再接线。 【r56 裁决=执行完毕｜预算已入基线件 refresh_days（schema v1→v2），契约 ratchet_refresh_days_matches 做集合全等；--update 不得改写预算面；夹具 10 例含无静默回落反例。取值 python 05-exec/r56_budget_fixtures.py】

- [x] **【P2·待办 W-38（r54 新立）】** 再生健康度进趋势线：台账已有 `face_status`（判据自证面），再补 `refresh_stale_count`（本轮有几个指标源件超期），使"漏跑探针"从一次性告警变成可看斜率的列。取值 `python 05-exec/ratchet_gate.py` 看「再生周期」行；接线前先确认 9/9 在预算内（r54 实测误报率 0）。 【r56 裁决=执行完毕｜refresh_stale_count 进 debt_runs.jsonl（分代点 19:15，旧行不追溯）；取不到记 None 不记 0；t78/t79/t80 三向锁死】
