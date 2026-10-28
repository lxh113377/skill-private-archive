# 07-next-steps.part42.md

<!-- 本卷为 07-next-steps.part33.md 的延续 -->

## 最近对话摘要（历史）

- [x] **阶段4 首批：A族 P0 整改** —— 拆卷 `f8bc12f`（85,508B→3,827B）+ 回归修复 `V3.37.1`；A-get-memory 死链 `5bcb550`；版本号/平台名清理

## P1 / P2（已全部销账）
- [ ] R113-7 需求2 字面缺口：余 56 件 unknown + 143 件盲区仍无替代检索面（每一个现有 skill 都应有候选清单）（由 flow 登记；状态: todo） 【r260 裁决=降级（转长期看守）｜r260 把「每个现有 skill 都应有候选清单」做到位：191/191 行有候选面（MATCHED 166 / FAMILY_ONLY 12 / NO_OS_CANDIDATE 13、守恒 191==191、c1_fail=0、need_c2_human=191、影子 IDENTICAL），另补 HIGH 前 20 件的**定向**检索（20/20 OK、60 slot 字段零缺失、负控必不存在词 total_count=0）与非 GitHub 五源面（120 cell）。残余具名：身份档 unknown=64 与同源探针 unverified=17（覆盖率 0.2094、盲区 151）属结构面，转长期看守由 provenance tiers + swap_gate counts 每轮显形，禁读成无缺口。取值：python 05-exec/r113_quarterly_audit.py --offline --out-dir <新目录>；python -c 读 r260_directed_search.json 与 r260_nongithub_face.json。】
- [ ] R113-2 本地升级可机查：把「本地是否升过级」接进可复算面（pin content_key 不含本地哈希的盲区）（由 flow 登记；状态: todo） 【r260 裁决=结案｜r260 由判据取代人工结案（同 R252-2 先例）：该债要防的是「升级把本地增量抹掉」，此风险现已由 r112 链的 local_only 单调面常驻看守并本轮实测复现 —— test-driven-development 43→51、hyperframes-registry 9→17、obsidian-bases 0→2 且 upstream_only=0/jaccard 0.9932，三笔零丢失；主线性 merge-base --is-ancestor f01842b0 HEAD rc=0。content_key 本身不含本地哈希的盲区保留为已知边界（联网 --refresh 面未复算，本轮 --offline）。取值：python 05-exec/r112_swap_gate.py --scan <p> --probe <u> --json <件>；git -C D:/global_skills merge-base --is-ancestor f01842b0 HEAD; echo 0。】
- [ ] R113-1 季度巡检节律：每季度跑 r113_quarterly_audit.py 并按维护规范 05 节规则裁决（由 flow 登记；状态: todo） 【r260 裁决=结案｜r260 接线完成：新增 05-exec/r260_quarterly_cadence.py（季产物超龄即叫，纯 stdlib、CI 可跑）+ .github/workflows/quarterly_audit.yml（cron 0 22 1 1,4,7,10 * = 每季度首日 06:00 UTC+8，三条 uses 全 pin 且 gh api 复算可解析）+ 注册第 112 门 quarterly_cadence_face（12 腿含必须仍红与变异腿；负控三向 rc=2/红/红）。深度巡检本体不进 CI 的理由具名：X-1 + 现扫受管根与 managed venv 依赖 ⇒ CI 必假红；CI 承担「盯人」与 gate_run_freshness 反向同思路。取值：python 05-exec/r260_quarterly_cadence.py → [CADENCE:PASS]；python 05-exec/r130_gate_table_reconcile.py → 门表 113。】
- [x] R112-4 「取数失败不得销毁证据」范式推广扫全库取数脚本（由 flow 登记；状态: todo）
- [x] R112-3 15 件 UNVERIFIED 换候选源重取或显式转「非同源/无上游」（由 flow 登记；状态: todo）
