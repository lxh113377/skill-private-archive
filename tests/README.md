# tests/ — 判据可发现性索引（I-6 承接，r110 改造3）

> **本目录是路由壳，不是测试本体**（X-1 边界：禁把技能语料复制进本归档仓造第二真相源）。
> 判据与夹具的权威源 = `05-exec/`（130 个 py，其中 29 个 `*_fixtures.py` 为常驻门）。
> 取值：`python -c "import glob;print(len(glob.glob('05-exec/*.py')),len(glob.glob('05-exec/*_fixtures.py')))"`（实测 130 / 29）。

## 一条命令跑全部判据

```powershell
python 05-exec/run_gates.py --json 06-benchmark/<新件>.json
```

> 29 门聚合，逐门独立不短路；三态 PASS / FAIL / UNVERIFIED（rc=0 但标记不见一律不算绿）。
> 门数以 runner 自述为准（取值：`python 05-exec/run_gates.py` 末二行），禁按本表手数。

## 常驻门清单（29 门，id 取自 GATES 表）

| 门 id | 脚本 | 一句话 |
|---|---|---|
| r19_scan_fixtures | `05-exec/r19_scan_fixtures.py` | 扫描器口径夹具 |
| r19_baseline_contract_fixtures | `05-exec/r19_baseline_contract_fixtures.py` | 基线契约夹具 |
| baseline_contract_scan | `05-exec/baseline_contract_scan.py` | 06-benchmark 证据件结构契约 |
| ratchet_gate | `05-exec/ratchet_gate.py` | 注入面/度量只降不升棘轮 |
| control_char_scan | `05-exec/control_char_scan.py` | 非法控制符扫描 |
| tracked_empty_check | `05-exec/r35_tracked_empty.py` | tracked 文本件非空 |
| mark_verdict_fixtures | `05-exec/r46_mark_verdict_fixtures.py` | 裁决标记锚点写入 |
| refresh_budget_fixtures | `05-exec/r54_refresh_fixtures.py` | 再生周期声明接线 |
| handles_readme_fixtures | `05-exec/r53_handles_fixtures.py` | 句柄可解与 README 零死链 |
| md_claim_face | `05-exec/r52_md_claim_face_scan.py` | 报告数字须挂取值命令 |
| retrieval_fixtures | `05-exec/r51_retrieval_fixtures.py` | 对手面引用取值域 |
| root_face_fixtures | `05-exec/r55_rootface_fixtures.py` | 噪声门登记面双向 |
| budget_contract_fixtures | `05-exec/r56_budget_fixtures.py` | 预算声明契约 |
| evidence_face_fixtures | `05-exec/r56_artifact_face_fixtures.py` | 证据件生成器覆盖 |
| baseline_note_fixtures | `05-exec/r55_note_fixtures.py` | 棘轮留账只增不减 |
| input_face_fixtures | `05-exec/r49_face_fixtures.py` | 判据输入面守恒 |
| authority_face_fixtures | `05-exec/r50_face_fixtures.py` | 权威源扫描面 |
| scan_inputs_fixtures | `05-exec/r40_scan_inputs_fixtures.py` | 声明==实存 |
| debt_ledger_fixtures | `05-exec/r39_debt_ledger_fixtures.py` | 账龄台账行契约 |
| noise_tracked_stub | `05-exec/r37_noise_tracked_stub.py` | 噪声门不误判已跟踪件 |
| gate_run_freshness | `05-exec/r32_gate_freshness.py` | 门禁自身活性 |
| roster_partition_fixtures | `05-exec/r60_roster_fixtures.py` | 名册分域自洽 |
| py_syntax_guard | `05-exec/r58_py_syntax_guard.py` | 05-exec 全部 py 可解析 |
| action_pin_guard | `05-exec/r58_action_pin_fixtures.py` | CI 动作 pin 不可变 SHA |
| retired_face | `05-exec/r59_retired_face.py` | 退役件磁盘残留 |
| generator_face | `05-exec/r66_generator_gate_fixtures.py` | pattern⇄生成器在位 |
| input_pin_face | `05-exec/r67_input_pin_fixtures.py` | junction 钉在权威源 |
| debt_face_freshness | `05-exec/r105_debt_face_freshness_fixtures.py` | 账龄件相对新鲜前置 |
| retired_reflow_fixtures | `05-exec/r59_retired_face.py` | 退役回流写入方归因 |

> 表内脚本路径为相对仓根写法；实际文件名以 `05-exec/` 磁盘为准（部分门与夹具同文件，部分门读多脚本）。
> 对照取值：`Get-ChildItem 05-exec -Filter *_fixtures.py | % { $_.BaseName }`（29 项，r110 实测）。

## 为什么没有 pytest

本仓判据形态 = 「判据脚本 + 夹具 + 变异腿」，退出码语义 0/1/2（对齐 `workflow_gate.py`、`wflow`），
由 `run_gates.py` 聚合；对手（spec-kit 390 / superpowers 87 个 tests/ 文件）是 pytest 形态。
形态不同但功能等价，本目录解决的是「第三方一眼找到并本地跑」的可发现性缺口（r108 §2-1）。

## 相关

- 门禁与取值命令总表：`AGENTS.md` §门禁与取值命令
- 执行证据索引：`05-exec/README.md`
- 判据变异测试（按需）：`python 05-exec/r19_fixture_mutation_check.py`
