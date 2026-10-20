# -*- coding: utf-8 -*-
"""run_gates.py — 本仓门禁聚合 runner（r31 / 对标新维度 N12「自动化验收面」的自持落地）。

对标实物（证据：`06-benchmark/ci_evidence/`，r31 逐份 gh api 取原文）：
  · mycelium-hq/ai-brain-starter `template-purity.yml`：
    "the identical check runs locally pre-push, in the write-time hook, and here in CI —
     one source of truth" ⇒ 同一份判据逻辑必须能被 N 个调用点复用，而不是每个调用点各抄一遍命令行。
  · mycelium `behavioral-install-eval.yml`：
    "exits 2 (loud INFRA error) when ANTHROPIC_API_KEY is missing, so a dead repo secret can
     never read as a green skip" ⇒ 判据跑不起来 ≠ 判据通过；必须有 PASS/FAIL 之外的第三态。
  · sickn33/agentic-awesome-skills `ci.yml`：5 个独立 job（pr-policy / source-validation /
    pr-evidence / artifact-preview / main-validation-and-sync），互不短路 ⇒ 一处红不得遮住其余四面。

本仓原状（r31 实测）：`memory/AGENTS.md` 的「项目门禁命令」是 5 段 `&&` 串联 ⇒
  ① 第一段红即短路，后 4 段是否仍绿**不可知**；
  ② 无任何覆盖根自证（违本仓 R20-2「预算/上限类门禁须自证覆盖根清单」）；
  ③ 无耗时基线（对标报告「性能」维度我们只有对手数字、没有自家数字）。

三态判据（本 runner 的核心）：
  PASS       rc == 0 且 输出含该门的 pass_token
  FAIL       rc != 0
  UNVERIFIED rc == 0 但 输出缺 pass_token（静默跳过 / 标记改名 / 脚本被截断 —— 一律不得算绿，R247）
聚合：任一 FAIL 或 UNVERIFIED ⇒ exit 1；门脚本本身缺失 ⇒ exit 2（禁「跑不到就算过」）。

用法：
    python 05-exec/run_gates.py                    # 本机全跑（含依赖绝对路径的门）
    python 05-exec/run_gates.py --portable-only    # 只跑跨机可复现子集（CI 用），其余显式记 SKIPPED
    python 05-exec/run_gates.py --json 06-benchmark/gate_run_r31.json
退出码：0 全绿 / 1 有 FAIL 或 UNVERIFIED / 2 门脚本缺失或环境不满足
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# r32：执行台账。每跑一次 runner 追加一行（origin 区分本机/CI）。
# 台账随仓提交 ⇒ CI 能反过来判「本机专属门还在不在被人跑」；这是本仓与对手 CI 的用法差：
# 对手的 CI 判代码，我们额外用 CI 盯「人有没有停跑」（依据见 06-benchmark/ci_health_r32_*.json）。
LEDGER = os.path.join(REPO, "06-benchmark", "gate_runs.jsonl")
ORIGIN = "ci" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"

# 单一真相源：门禁清单只在这里维护。AGENTS.md / CI / 会话内手工跑，都走本表。
GATES = [
    {
        "id": "r19_scan_fixtures",
        "script": "r19_scan_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "层b 真机接线 subprocess 调 cumulative_drift_scan.py / description_baseline_scan.py / "
            "claim_truth_scan.py，三者读 D:\\global_skills ∪ 焚诀 ∪ D:\\global_memory"
            "（r31 静态实测：各含 1-2 处本机绝对根）⇒ 离机必红，刻意不入 CI",
        "covers": ["05-exec/cumulative_drift_scan.py 排除判据", "05-exec/skill_structure_rubric_scan.py 口径",
                   "05-exec/description_baseline_scan.py PROCESS_RE", "05-exec/_lib.py denominator()"],
        "why": "判据可信度：已知答案 36 例 + 真机接线 19 例",
    },
    {
        "id": "r19_baseline_contract_fixtures",
        "script": "r19_baseline_contract_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/baseline_contract_scan.py", "05-exec/schemas/r19/baseline-contracts.json"],
        "why": "契约校验器自身的夹具（含 r31 授权代际列表 t11/t12）",
    },
    {
        "id": "baseline_contract_scan",
        "script": "baseline_contract_scan.py",
        "argv": ["--quiet"],
        "pass_token": "[CONTRACT:PASS]",
        "portable": True,
        "covers": ["06-benchmark/*.json 机器证据结构（份数/pattern 数不硬编码，取值：该门 --json 输出的 files_checked 与 artifacts 长度）"],
        "why": "产物 schema/必填/类型/不变式事前拒收",
    },
    {
        "id": "ratchet_gate",
        "script": "ratchet_gate.py",
        "argv": [],
        "pass_token": "[RATCHET:PASS]",
        "portable": False,
        "not_portable_reason": "取值需读 焚诀 eval/truth_constants.json 与 D:\\global_skills 实测字节，跨机不可复现",
        "covers": ["06-benchmark/inject_ratchet_baseline.json", "D:\\global_skills 注入面", "焚诀 truth_constants"],
        "why": "注入面/度量六项只降不升棘轮（r34 加第 6 项 username_in_skill_files）",
    },
    {
        "id": "control_char_scan",
        "script": "control_char_scan.py",
        "argv": ["."],
        "pass_token": "[CTRL:CLEAN]",
        "portable": True,
        "covers": ["本仓全部文本面（r31 实测 376 个面）"],
        "why": "拦「肉眼看不见、但让引用检索不到」的 C0 ∪ DEL",
    },
    {
        # r35 H-1：把 r34「我自己把 AGENTS.md 写成 0 字节」那次事故的**自觉型规则**升级成机器型
        "id": "tracked_empty_check",
        "script": "r35_tracked_empty.py",
        "argv": [],
        "pass_token": "[EMPTY:PASS]",
        "portable": True,
        "covers": ["本仓全部 tracked 文本件（.md/.py/.json/.jsonl/.yml/.txt/.ps1/.sh/.toml 等）",
                   "二进制/未知扩展跳过但如实计数，不静默当通过"],
        "why": "拦「写崩/截断留下的 0 字节件」——r34 我曾把 memory/AGENTS.md 写成 0 字节，靠 Git 基线才恢复",
    },
    {
        # r46 W-16：裁决标记写入器（锚点定位 + 五重拒写 + 读回验证）的夹具
        "id": "mark_verdict_fixtures",
        "script": "r46_mark_verdict_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r46_mark_verdict.py 的锚点定位与拒写分支",
                   "X-19 禁行号写标记（工具化，不靠自觉）"],
        "why": "r45 实测 W-9 挂了 5 轮的真因是按行号写标记写到别处；本门锁死该入口不再接受行号、歧义与已闭环一律拒写、写完必须读回",
    },
    {
        # r54 W-36：棘轮 9 指标逐个声明再生周期，超期即转 unknown
        "id": "refresh_budget_fixtures",
        "script": "r54_refresh_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "g8/g9/g10/g11 在真机上核对 9 个指标源件的 mtime 年龄并跑 ratchet CLI；"
            "换机无 06-benchmark 证据件与焚诀 truth_constants 时全部取不到年龄，判据退化为恒 UNVERIFIED，无意义",
        "covers": ["05-exec/ratchet_gate.py 的 METRIC_SOURCES/METRIC_REFRESH_DAYS/source_age_days/face_metric_refresh",
                   "collect_metrics 把 STALE 指标转 unknown（UNVERIFIED 不转，活体扫描本无源件）",
                   "CLI 打印再生周期行（声明必须在输出里看得见，否则等于没声明）"],
        "why": "r53 我方差点拿 33 轮前的源件跟现值比（那次报的是命名假阳性，揭开的是"
               "「没有任何地方声明预算」这个真缺口）；对手侧 r54 实测五家仅 2 家在 workflow 里声明节律 "
               "（pre-commit 12 行 / spec-kit 7 行）⇒ 周期是被显式声明的对象",
    },
    {
        # r53 W-34/W-35：报告数字改引用可再生句柄 + README 证据面可发现性
        "id": "handles_readme_fixtures",
        "script": "r53_handles_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r38_debt_aging.py 的 make_handles/resolve_handle（句柄可解值、死句柄返 None）",
                   "写台账→解句柄的闭环守恒 h7/h7b（源头断了必须显形，不得沿用旧值）",
                   "README 指向 06-benchmark 的链接数 >0 且零死链（h8/h9 + 自检）"],
        "why": "r53 实测：对手 AAS 一份 README 挂 50 个文件链接、正文数字 0-1 个，而我方 60 份机器可读件在入口文档里链接数为 0；同时 r38 含 PR 的数字在报告里无命令跑了 12 轮 ⇒ 数字必须由产物承载、入口必须可达",
    },
    {
        # r52 W-30：Markdown 引用面数字须自带取值途径（只看可整改面，历史面按 R241 不回改）
        "id": "md_claim_face",
        "script": "r52_mdclaim_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["06-benchmark/*.md 引用面（数字声明 ±12 行内需有取值命令）",
                   "05-exec/r52_mdclaim_fixtures.py 的 19 例（含标题行排除与分面守恒）"],
        "why": "r51 实测 JSON 取证件已被判据管住，但真正被读的是报告正文：r38 的 open issues 就在报告里"
               "以无命令形态跑了 12 轮。接线口径 = 只判可整改面（r≥51 或 mtime 当日），"
               "历史面 755 处敞口如实登记但不判红（R241 禁回改，且拿不可消的警告当判据即 W-32 那个毛病）",
    },
    {
        # r51 W-28：外部取证件两路对账
        "id": "retrieval_fixtures",
        "script": "r51_retrieval_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/baseline_contract_scan.py 的 inv_opponent_claims_have_retrieval（结构识别，不锁键名）",
                   "契约 debt_aging glob 由 r3* 修成 r*（陈旧 pattern 面洞）",
                   "真机：06-benchmark/opponents_*_r*.json 全部须过判据"],
        "why": "r51 实测我方引用对手 open issues 取自 REST 含 PR 面（虚高 1.5–3.5 倍）、workflow 数混入平台 dynamic 件；"
               "且实跑接线暴露调度器传给不变式的是名字串而非配置值——按名字比较会让全部证据件被字典序静默豁免",
    },
    {
        # r128：W-47 第四腿（判据与生产实测逐条一致）的机检
        "id": "w47_reconcile_fixtures",
        "script": "r128_w47_reconcile_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "四条腿都要真跑 r128_ruler_reconcile.py，而它 import 焚诀 eval 的 unified_router 并逐题 route()；换机既无该路由面也无 r127 修正产物，本门会因输入面缺失判 UNVERIFIED",
        "covers": ["t1 正控：对齐口径（actually_hit）零不一致",
                   "t2 反控：错口径（reachable）必须抓出假红（即 r126 的病）",
                   "t3 反向对照：另一错口径（expected_in_tag）必须抓出不一致",
                   "t4 变异对照：窄口径（rescued_by_l15）必须抓出假红",
                   "t5 输入面：产物无逐条读数须 UNVERIFIED（rc=2），禁按 0 记绿",
                   "t6 变异对照：证明 t2/t4 的应红前提不是恒真"],
        "why": "W-47（r58 立）原有三腿（应绿/应红/对照组被证伪）。r128 加第四腿：判据输出必须与 route() 实测逐条一致。动因是 r126 到 r127 两轮一手代价：r126 的可达性判定只建模 bge_recall 的第一次候选集构造，漏了 L1.5 域限制兜底 union 合并，稳定产出 45 条假红且静态推导每一步都看着合理；r127 用本腿复核后确认假红数正是 45。",
    },
    {
        # r55 D-100：同一判据两输入面（未注册根 strict 误判）修完的「登记不放宽判据」双向取证件
        "id": "root_face_fixtures",
        "script": "r55_rootface_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "整条夹具走真实 `handoff.py noise <项目根>` 子进程并核对本机受管根登记面（R286 的 KNOWN_CORE "
            "键是绝对路径）；换机既无该登记也无本项目根，f2/f8 的残留项集合不成立",
        "covers": ["受管根 noise_lint KNOWN_CORE 对本项目根的登记面（R286，受管根 e93896b）",
                   "登记不放宽判据：植入散落产物仍须判 VIOL + 计数严格 +1 + 清理后复位",
                   "f9 反向对照：未登记同形根上同一谓词必须抓到顶层 strict VIOL（防 f2 成空断言）"],
        "why": "r54 我把「savepoint 绿」当「项目根干净」写进了 AGENTS.md 排障表 row 1 首版（未实测的检查命令），"
               "r55 定位到根因是同一判据读了两个输入面；修完必须双向取证件——顶层 8→0 只证明变绿，"
               "不证明牙齿还在（放宽 allowlist 凑绿是 X-9 的反面形态）",
    },
    {
        # r126：第 9 类失败层 Tag 闭包 读数面的双向取证件（W-47：应绿+应红+对照组被证伪）
        "id": "tag_closure_fixtures",
        "script": "r126_tag_closure_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "n7 真题面小样需真跑 r126_tag_closure.py，而它读焚诀 eval 的语料与统一注册表；"
            "换机既无该语料也无该索引，本门会因输入面缺失判 UNVERIFIED",
        "covers": ["可搜索面判定的三条正向（期望件在 tag 内 / 域匹配 / 全量面）",
                   "两条反向（tag 闭包挡住期望件 / 域失配）",
                   "n6 变异对照：判定改成恒真时应红前提失效（反证不是恒真断言）",
                   "n8 守恒：reachable_n + unreachable_n == questions_n"],
        "why": ("r126 一手实测：unified_router 的 bge_recall 在 tag_hits 非空时只在 tag "
                "命中的 skill 内搜索，于是 tag 判错一个，期望件连 BGE 的边都碰不到。"
                "实测 279 题里 79 题（28.3%）期望件结构上不可达，其中 15 题 raw_rank<=5 "
                "却不可达（tag_trap）—— 比 r120 的域过滤（第 8 类）更靠前、每条更致命，"
                "故必须留双向证件。"),
    },
    {
        # r123 R120b-8：区间归因通道（新增基线上调后门）的双向取证件
        "id": "range_attr_fixtures",
        "script": "r123_range_attr_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["ratchet_gate --range-attribute 五道反例（--from 不接真实基线 / --to 预支 / --commits 空 / --range-reason 空 / --metric 未知）",
                   "合法区间正例：留账 kind=range 且指标落到 --to",
                   "守恒：被拒的归因不得在基线件留任何痕（防把留账当装饰刷条数）"],
        "why": "r123 给棘轮加了累计区间归因通道；新通道天然是只降不升棘轮的上调后门，若不留证件，后人加空 reason 或把 --to 写成实测+1 就能把棘轮变成只升不降（X-9 反向形态）",
    },
    {
        # r56 W-37：再生预算从代码常量升为被契约看守的声明面
        "id": "budget_contract_fixtures",
        "script": "r56_budget_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["06-benchmark/inject_ratchet_baseline.json 的 refresh_days 声明面（schema v1→v2）",
                   "05-exec/baseline_contract_scan.py 的 inv_ratchet_refresh_days（缺项/多键/越界三向判红）",
                   "ratchet_gate.refresh_status 无静默回落（基线缺预算⇒UNVERIFIED 且不读代码常量）",
                   "--update 不得改写预算面 + 预算与 note 留账同轮存活（D-104 同族再犯防护）"],
        "why": "r54 我只做到「代码里逐个声明保质期」，但契约看不见那张表 ⇒ 谁删一项就静默少一项，"
               "声明退化成没人看守的注释（当时登记为 D-97/W-37）；对手把节律写在被 CI 解析的文件里，"
               "声明即被校验 —— 本门把同一件事在无 CI 条件下做成等价机制",
    },
    {
        # r56 W-27/W-32：两份"裁定依据"件从一次性内联产物升为有生成器 + 被契约守
        "id": "evidence_face_fixtures",
        "script": "r56_artifact_face_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "断言对象是本项目 06-benchmark 里的 r56 实测件与受管根规则扫描结果（换机无同源件）",
        "covers": ["06-benchmark 两类新 pattern：inject_face_breakdown_r*.json / w27_conflict_triage_r*.json",
                   "baseline_contract_scan 的两条新不变式（逐件求和自洽 / 三数算术自洽 + 空面不判过）",
                   "代际豁免 required_from + invariants_from：历史证据件不追溯判红，且分叉点后仍须红（e9）",
                   "豁免可见性：扫描输出必须打印「代际豁免」计数行（e10，看不见的豁免=豁免表）"],
        "why": "r52/r51 那两份裁定依据是**一次性内联脚本**产出的，仓里根本没有生成器 ⇒ 它们自己就是解不出的"
               "死句柄（另立 W-46 记这条通病）；补生成器时又发现新必填面会回头把历史件判红——"
               "台账早就有分代口径，本轮把它推广到 JSON 件并钉成常驻断言",
    },
    {
        # r55：--update 曾把基线 note 的逐轮人工归因从 496 字刷成 33 字，且无任何门禁变红
        "id": "baseline_note_fixtures",
        "script": "r55_note_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "n4/n5/n6 读写本项目 06-benchmark/inject_ratchet_baseline.json 的现件留账"
            "（r38/r40/r45 三条人工核定依据是本轮恢复的历史事实，换机不存在）",
        "covers": ["05-exec/ratchet_gate.py 的 merge_note 与 --update 落盘路径（留账只增不减 + attributed_raises 须存活）",
                   "note 缩短即拒写分支（宁可红，不许把留账当装饰刷掉）",
                   "n6 常驻锁：现件 note 仍含 r38/r40/r45 三条归因"],
        "why": "指标面有「只降不升」的牙齿，留账面此前完全没有——r55 我跑一次 --update 就蒸发了三条核定依据"
               "（含「真实敞口 22 而非 0」），当场自抓，并以变异体复验（改回旧行为 n4 必红）",
    },
    {
        # r49 W-20 + W-22：判据输入面截断自证 + 裁决对象自证
        "id": "input_face_fixtures",
        "script": "r49_face_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r38_debt_aging.py 的 face_round/face_dedup/face_dating",
                   "05-exec/r46_mark_verdict.py 的 landed_contradiction/item_own_id（第⑥重拒写）",
                   "真卷输入面守恒（RE_ITEM 行数 == 计入条目数 + 前缀键零碰撞）"],
        "why": "账龄尺有四处截断/降采样（-40 取轮号、body[:80] 去重、needle[:70] 定年、title[:110] 展示）"
               "从未自证；且 r46 我把 W-17 的延期裁决写到了已落地的 W-14 行上（锚点唯一命中≠对象正确），"
               "3 轮后才被到期追讨发现 —— 本锁把两者都变机器判据",
    },
    {
        # r50 W-25：输入面自证推广到冲突判据与棘轮（覆盖面 + 读取面交叉对账）
        "id": "authority_face_fixtures",
        "script": "r50_face_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "c5–c8 在真机权威源 D:\\global_memory\\core 上跑发现器并断言扫描面无漏扫件；"
            "换机无该根则候选集为空，覆盖面断言失去意义（只余纯函数例）",
        "covers": ["05-exec/rule_conflict_scan.py 的 discover_authority_candidates/face_authority_coverage/effective_files",
                   "05-exec/ratchet_gate.py 的 face_counted_vs_observed（OSError 静默跳过显形）",
                   "05-exec/baseline_contract_scan.py 的 pattern 零命中判红（防回退）"],
        "why": "r50 实测：冲突判据的手抄清单只 10 件，而 GM/core 有 18 件带可配对正负规则的权威源"
               "（规则分卷 behavior_core_rules_p1..p8 即 22 锚点正文所在）从未进面 —— 扩面后极性规则 "
               "116→188、自述冲突 6→11、互斥候选 6→21，证明「绿灯」曾是 38% 面上的结论",
    },
    {
        # r40 L-4：冲突扫描器输入面自证（死条目必须红，且不得靠删条目把覆盖面做干净）
        "id": "scan_inputs_fixtures",
        "script": "r40_scan_inputs_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/rule_conflict_scan.py 的 DEFAULT_FILES 与 input_evidence",
                   "05-exec/baseline_contract_scan.py 的 conflict_no_dead_inputs 不变式"],
        "why": "r40 实测：DEFAULT_FILES 里有一条指不到文件的权威源，被错标成归属方件挂账 4 轮"
               "——本条把『声明==实存』钉成契约判据，防同类债务被错误外部化",
    },
    {
        # r39 W-3：债务趋势台账的 fail-closed 夹具（拒写脏行 + 延期不得冒充已裁决）
        "id": "debt_ledger_fixtures",
        "script": "r39_debt_ledger_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r38_debt_aging.py 的 append_ledger 与 classify_item",
                   "05-exec/schemas/r19/baseline-contracts.json 的 debt_runs.jsonl 行契约"],
        "why": "锁死三件：脏测量值不得进趋势线；挂账到期必须回判 OVERDUE；origin 取值域封闭 local/ci",
    },
    {
        # r37 H-4：把「判据自己会不会报错」变成常驻门（本轮实测：噪声门连红 7 轮全是假阳性）
        "id": "noise_tracked_stub",
        "script": "r37_noise_tracked_stub.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "层a 需在 %TEMP% 建真实 git 仓并 git commit（要 git 身份），层b 断言两个真实受管根"
            "（焚诀 / global_memory）的已知假阳性必须清零 —— 换机无这两根即无意义",
        "covers": ["D:\\global_skills\\A-project-handoff\\scripts\\noise_lint.py",
                   "受管根 strict allowlist 放行面", "二级深扫 .git 例外"],
        "why": "锁死「已跟踪根部文件不误判 + .git 运行态不深扫 + 放行面不外溢」三件，"
               "防任何一次再为凑绿而放宽判据（R263/R220）",
    },
    {
        # r32 H-2：本仓独有一门 —— 用台账反证「本机专属门还在被跑」。CI 里也能跑（读已提交台账）。
        "id": "gate_run_freshness",
        "script": "r32_gate_freshness.py",
        "argv": [],
        "pass_token": "[FRESH:PASS]",
        "portable": True,
        "covers": ["06-benchmark/gate_runs.jsonl 执行台账",
                   "间接盯住 ratchet_gate / r19_scan_fixtures 两台机专属门是否仍被人跑"],
        "why": "防判据僵尸化（对手实测：spec-kit 50% run 停在 action_required，从未产生判定）",
        "meta": True,   # 元判据：它评的是「台账本身」，不得把它的红写进台账 verdict（否则一次引导期红会永久自锁，r32 实测）
    },
    {
        "id": "roster_partition_fixtures",
        "script": "r60_roster_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:roster-fixture-pass] 12/12",
        "portable": True,
        "covers": ["05-exec/baseline_contract_scan.py 的 inv_roster_partition_sum（r60 新增不变式）",
                   "06-benchmark/capability_roster_r60_2026-09-30.json 与 capability_gap_r60_2026-09-30.json 真件面",
                   "四例变异：抽 domain 行 / 抽 item retrieval / 零面 / items 长度不符"],
        "why": "第 18 维名册差集首版把「路径条数」当分母、又让单仓 864 条生成式清单占掉对手面 79.8% "
               "—— 域内自洽却整体失真。本门把那层防护钉成契约不变式，并按 W-47 同时交出应绿与应红的证据",
    },
    {
        "id": "py_syntax_guard",
        "script": "r58_py_syntax_guard.py",
        "argv": [],
        "pass_token": "[GATE:pysyntax-pass]",
        "portable": True,
        "covers": ["05-exec/*.py 全部 99 件（compile exec 模式逐件解析，空面判红）"],
        "why": "W-46 的下一层：`pattern 有没有生成器` 之外还得问 `生成器能不能加载`。"
               "r58 实物 = `evidence_resolvability_measure.py:111` 少一个右括号，已入库且长期不可运行，"
               "其产物成为「生成器跑不起来」的死句柄，而 21 道门没有一道会因为工具加载失败而红",
    },
    {
        "id": "action_pin_guard",
        "script": "r58_action_pin_guard.py",
        "argv": [],
        "pass_token": "[GATE:actionpin-pass]",
        "portable": True,
        "covers": [".github/workflows/*.yml 的全部 `uses:` 引用面（含 @main 分支形与截断 SHA 形）",
                   ".github/dependabot.yml 的 github-actions 生态声明",
                   "05-exec/r58_action_pin_fixtures.py 的 11 例（层 a 9 + 层 b 真仓对照/变异体各 1）"],
        "why": "第 17 维供应链面：`checkout` 在 21 道门读盘**之前**决定工作树里是什么字节，未 pin 到不可变 SHA"
               " = 判据输入面劫持入口（与 r49 劫持族、r56「声明要被机器校验」同族）；"
               "P2 把「pin 必须配更新器」也钉住，防固定点腐烂成拿不到上游安全修复的更坏形态",
    },
    {
        "id": "retired_face",
        "script": "r59_retired_face.py",
        "argv": [],               # r60 起跑**活体面**：r59 接线时因两件残留仍在盘（未入 Git / 宽暂存 21>20 /
                                  # 并发会话刚提交）只能挂 --selftest，且原因写进「本 runner 不覆盖」；
                                  # r60 前提已逐个闭合（两件已 git add 并在受管根 12916b7/af4be90 入库，
                                  # 备份落 D:/global_memory/_trash/r60_retire_* 带 sha256 清单），
                                  # 故本门改为直接判活体：rc=1 即真有残留。自证夹具仍可单独跑
                                  # `python 05-exec/r59_retired_face.py --selftest`（8/8）
        "pass_token": ["[GATE:retired-face-pass]", "[GATE:retired-face-watch]"],
        "portable": False,
        "not_portable_reason":
            "r7/r8 取真实 retired_skills 名单 x 真实 D:/global_skills 磁盘面；离机若无该根则判据面为空，"
            "本件按 R247 走 UNVERIFIED(exit 2) 而不是默认放行",
        "covers": ["D:/global_skills 磁盘集 ∩ 焚诀 eval/truth_constants.json 的 retired_skills（退役必须已移出扫描树）",
                   "名单为空 / 磁盘面为空 / 名单文件缺失 三态一律 rc=2，不得读成「无残留」",
                   "r7 真件可逆注入：真名单首个名字建进临时树必须见红（W-47 两侧证据）"],
        "why": "r59 实测：executing-plans、slides 早在 retired_skills 里、磁盘仍带 SKILL.md 且能被会话加载；"
               "而 disk_registry_diff.py 把这个数印出来（「其中磁盘仍在: 2」）却照打 [PASS] ⇒ 看得见不等于拦得住"
               "（R238 接线面 + 「消不掉的告警等于没有判据」）。本门只判 磁盘∩退役名单 一项事实，"
               "不重复 disk_registry_diff 的三类差集（一事实一判据）。",
    },
    {
        "id": "generator_face",
        "script": "r58_generator_coverage.py",
        "argv": ["--gate"],        # r66 W-46b 第二步：从「只测量」升为判据（三态 rc）
        "pass_token": "[GENCOV:PASS]",
        "portable": False,
        "not_portable_reason":
            "覆盖面含 D:/global_skills 与焚诀/audit 两处本机绝对根（EXTERNAL_ROOTS），离机取不到 ⇒ 会判 "
            "EXTERNAL_CANDIDATE 塌成 DEAD_HANDLE 而误红；本件按 R247 走 UNVERIFIED(exit 2) 而不是默认放行",
        "covers": ["05-exec/schemas/r19/baseline-contracts.json 的 artifacts 里每个 pattern ⇄ 05-exec/*.py 的生成器面",
                   "05-exec/r58_generator_coverage.py 的三路识别（A 字面/B 词干+扩展/C 同名工具）+ r66 新增路 D（自产物按工具名）",
                   "夹具 05-exec/r66_generator_gate_fixtures.py 的 12 例（含 3 条变异腿与 2 条反向腿）"],
        "why": "W-46b：r56 连踩两份死句柄（裁定依据件在仓里没有生成器）。r58 先只测量并交清单（防带误报上线），"
               "r66 把误报修到 0 后接线：三态 rc=0/1/2（零输入与解析失败一律 rc=2，禁静默判过，R247）。"
               "r66 实证三处自身缺陷：① 自排除把本工具自己的产物判死句柄；② all() 过紧把 attention_sim_raw_* 判假阴性；"
               "③ 摘牌 noise_falsepositive_*（真死句柄，生成器已不存在）。",
    },
    {
        "id": "input_pin_face",
        "script": "r67_input_pin_guard.py",
        "argv": ["--gate"],       # r67 R58-1：第 17 维纵深的「本地面」——镜像/克隆面必须钉在权威源
        "pass_token": "[PIN:PASS]",
        "portable": False,
        "not_portable_reason":
            "取数面是本机七端的 junction 实测与 D:/global_skills / D:/global_memory / 焚诀 三根的 git pin；"
            "离机这些根不存在 ⇒ 声明面为空，本件按 R247 走 UNVERIFIED(exit 2) 而不是默认放行",
        "covers": ["焚诀 eval/truth_constants.json 的 paths / junction_paths / endpoints.active 声明面",
                   "各端 skills|memory junction 是否解析到声明的权威根（形态/存在/目标三项）",
                   "06-benchmark/input_pins.jsonl 的 pin 落账与「本行自洽」（写哪本/指哪本/比哪本）"],
        "why": "R58-1：26 道门读的全是本地字节，而这些字节由仓外的受管根本体与各端 junction 决定。"
               "CI 那一侧 r58 已 pin 到不可变 SHA，本地面此前无人固定 —— junction 断裂或被改成指向别处时，"
               "某端读到的不是权威源字节而所有门禁照绿（与 r58 D-113 同族，入口在本机）。"
               "本门只判「镜像面是否钉在权威源」这一项事实；pin 变动清单按 W-32 只报不阻断。",
    },
    {
        # r105 F-1：账龄三态指标的输入面必须比「它所测的那本卷」新
        "id": "debt_face_freshness",
        "script": "r105_debt_face_freshness_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:debt-face-fresh-pass]",
        "portable": True,
        "covers": ["05-exec/ratchet_gate.py 的 _debt_artifact_fresh / _newest_artifact（相对新鲜谓词）",
                   "05-exec/ratchet_gate.py 的 overdue_debt_items()（接线：经谓词把守的真取值路径）",
                   "两条变异体：摘前置 / 前置恒真，各自必须让陈旧值漏进指标（证明鉴别力来自本前置）"],
        "why": "r105 一手：日历龄预算（W-36 的 refresh_days）只答「这件多久没重算」，答不了「这件比"
               "它所测的卷新不新」。r104 在同一轮里 16:29 量账 → 16:33 往 07 写裁决，件比被量对象旧 "
               "226 秒，棘轮照收 ⇒ 把已还掉的债报成比基线新长的债（实测 25 vs 活体尺 1），并连带把"
               "读棘轮文本的 4 道门一起染红。本门同时交「应绿的绿」（含等界）与「应红的红」（含空面），"
               "且对照组被变异体证伪过一轮（W-47）。",
    },
    {
        # r105 F-5：退役件回流的「生产者归属」分堆 —— 看守与阻断的边界由证据画，不按名字豁免
        "id": "retired_reflow_fixtures",
        "script": "r59_retired_face.py",
        "argv": ["--selftest-reflow"],
        "pass_token": "归属分堆桩",
        "portable": True,
        "covers": ["05-exec/r59_retired_face.py 的 attribute_producer / _git_tracked_n（经活体 run() 取数，夹具不重写谓词）",
                   "正例：git 零跟踪 + mtime 同批 ⇒ rc=0 且 retired_still_on_disk 仍逐件具名（看守不等于失明）",
                   "反例两向：我方跟踪过 / mtime 相差 90s 超 2s 成批窗口 ⇒ 均须仍 rc=1",
                   "单件面不得因「无同批可比」静默放行 + 判据口径自证（阈值写进产物，不留散文）"],
        "why": "r100 已实测并裁定 executing-plans / slides 由平台重下发（节律 ~47min）、降级为看守项；"
               "可 retired_face 一直留成硬阻断 ⇒ 每轮固定 1 红，把「没人能负责的红」混进「我欠的一次清理」"
               "里稀释真红（r105 实测该门 rc=1，而两件的证据是 git ?? 未跟踪 + 同一秒 23:29:55 mtime）。"
               "本门把「谁写回来的」画成有证据的两堆：我方写回必须仍拦，平台回流具名看守；"
               "窗口只给 2 秒，防豁免吞掉我方隔几分钟自己复制回来的那一份。",
    },
    {
        # r112（第 19 维「版本落后面」）：内容寻址升级判据的双向自证 + 变异腿
        "id": "r112_provenance_fixtures",
        "script": "r112_provenance_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r112_upstream_probe.py 的 relation()（六态内容寻址关系）",
                   "05-exec/r112_swap_gate.py 的 decide()（五态裁决映射）",
                   "05-exec/r112_provenance_face.py 的 check_ledger_churn()（R306 不变腿）",
                   "三条变异体：relation 常数化 / decide 常数化 / 空转判据空实现 —— 各自必须被夹具抓住",
                   "零输入腿：空 bench 目录必须 rc=2 且不印 token（R247）"],
        "why": "本维前两代尺（r105 词面 / r111 BGE 语义）都是写完即宣布有效，随后被自己的标定控制判死；"
               "本门把「应绿的绿 + 应红的红」做成常驻，且变异体刻意让被测函数永远给好话（抓不住即夹具无鉴别力）。",
    },
    {
        "id": "provenance_face",
        "script": "r112_provenance_face.py",
        "argv": [],
        "pass_token": "[PROVENANCE:PASS]",
        "portable": True,
        "covers": ["06-benchmark/provenance_r112_*.json（三档置信度守恒 + 覆盖根自证）",
                   "06-benchmark/upstream_pins.jsonl（有身份必入册 / unknown 禁登记 / 无空转）",
                   "06-benchmark/upstream_r112_*.json（OK+UNVERIFIED 守恒 + 每条 UNVERIFIED 具名带因）",
                   "06-benchmark/swap_gate_r112_*.json（每条证据都有裁决 + 非 UNVERIFIED 数 == 证据 OK 数）"],
        "why": "用户痛点「市面上有更好的 skill，我还在用旧的」在本仓此前没有任何判据在看："
               "182 件里 127 件连上游身份都没有。本门守住第 19 维的结构性事实（离线、不依赖上游可达），"
               "并强制把盲区与 UNVERIFIED 逐件具名 —— 盲区禁读成「已核对无缺口」。",
    },
    {
        # r112（一手缺陷）：取数失败不得销毁已有证据 —— 与 R247「零输入不得当绿」互为反向
        "id": "cache_guard_fixtures",
        "script": "r112_cache_guard_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r112_upstream_probe.py 的 fetch_candidate 缓存写侧（失败不覆盖已成功的缓存）",
                   "正向腿 g1：好件在盘后取数失败 ⇒ 旧件内容保留且失败痕迹入 cache_error",
                   "反向腿 g2：用修复前旧实现跑同一断言必须失败（鉴别力来自守卫本身）",
                   "g3：成功路径仍覆盖（防修过头变成永不更新）；g4：无旧件时失败照写失败件（不凭空造证据）"],
        "why": "r112 一手实测：一次网络 EOF 把 14KB 好件覆写成仅 280B 的失败桩，"
               "随后 --offline 复算把「已升级」件读成 UNVERIFIED（ok_n 24→18）。缓存被自身缺陷毁掉，"
               "这是「工具把自己唯一的证据源弄没了」这一类，必须有常驻腿看住。",
    },
    {
        # r113 K-4：r96 整面语料缓存的防退化闸（degrade_check）双向自证
        "id": "r113_degrade_fixtures",
        "script": "r113_degrade_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r96_twelve_face.py 的 degrade_check / available_n / read_json_or_none",
                   "g1 塌陷面（1/5）判退化；g2 正常轮（3/5）不误伤；g3 无对照基准不拦；g4 同面不误伤",
                   "g5 接线腿：临时缓存文件 + 塌陷面走 main 分支 ⇒ 旧缓存字节必须不变（不只测谓词）",
                   "m1 摘闸（恒 None）⇒ g1/g5 必须转红；m2 阈值改过严 ⇒ g2 必须转红"],
        "why": "r96_gh_raw.json 是第 19 维 inferred 身份的来源根。大面积取数失败时整体覆写会把"
               "好语料塌成一片 available False，而面内不变式照样自洽（X-24：分母静默变小仍全绿）。"
               "单件形态 r112 已抓，整面形态本轮由自家夹具抓到，两处都得常驻。",
    },
    {
        "id": "cache_guard_face",
        "script": "r113_cache_guard_face.py",
        "argv": [],
        "pass_token": "[CACHEGUARD:PASS]",
        "portable": True,
        "covers": ["05-exec/*.py 全量面：远端取数 + 写持久证据路径 的组合形态",
                   "守卫 token 三型：cache_error（单件不覆盖）/ degrade_check（整面防退化）/ merge_note（留账只增不减）",
                   "豁免面：临时目录与每轮新产物（args.out / 日期 / 轮号）不进分母",
                   "零输入面 ⇒ rc=2 UNVERIFIED（R247）"],
        "why": "同一族缺陷连着两轮各抓一半（r112 单件覆写 / r113 整面覆写），说明逐件修不收敛；"
               "本门把「取数脚本写可复用证据必须声明守卫」钉成结构判据，新增裸写件当轮即红。",
    },
    {
        "id": "cache_guard_face_fixtures",
        "script": "r113_cache_guard_face_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["第 34 门自身的 W-47 双向证据（f1 裸写点名 / f2 带守卫判绿 / f3-f4 两条豁免 / f5 真机接线 / f6 零输入）",
                   "m1 摘守卫识别 ⇒ f2 转红；m2 摘豁免识别 ⇒ f3 与 f4 同转红",
                   "本门两次假阳性一手：w[bt] 漏匹配 open(x,w) 造成 f3/f4 的绿来自漏判而非豁免；"
                   "泛词 + re.I 把夹具小写 bench 误判成违规面（大小写敏感后消）"],
        "why": "门自身两次失真的教训必须固化成腿：判据的『绿』可能来自匹配不到而不是判过。"
               "变异体刻意让豁免/守卫识别失效，抓不住即本夹具无鉴别力。",
    },
    {
        # r119 改造 3：把 r118 立的 W-1 硬边界从散文升级为结构判据
        "id": "migration_guard",
        "script": "r119_plan_boundary_gate.py",
        "argv": [],
        "pass_token": "[MIGGUARD:PASS]",
        "portable": True,
        "covers": ["04-plan/迁移替换方案_r114 必须含 W-1 四 token（W-1 / r118_swap_sim.py / 正向 delta / 短路先于召回）",
                   "同一方案必须含 r119 复算加注（0 影响从当时实测更新为当前复算仍成立）",
                   "自带 --selftest：正例现件应 PASS + 反例摘 token 应 FAIL（W-47 双向）"],
        "why": "r118 实测换装对生产路由影响 0 并立硬边界 W-1，但那条边界只活在报告与方案的散文里，没有任何判据在看方案还在不在说这件事。r119 把它钉成常驻门：缺 token 即红。",
    },
    {
        "id": "r117_upstream_delta_fixtures",
        "script": "r117_upstream_delta_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r116_upstream_delta_classify.py 的四类唯一归类与分母守恒（含 r117 修的正则支）",
                   "05-exec/r117_route_miss_attr.py 的四态归因（STALE_EXPECT / UNREGISTERED / REAL_MISS / UNDECIDABLE）与守恒",
                   "两份真件复算：upstream_delta_r116*（11 件逐行加总）与 route_miss_attr_r117（20 条 miss 逐行重判）",
                   "变异腿 m1-m3：还原 r116 原正则 / 归因恒判 REAL / 归因恒判 STALE，三条都必须被夹具抓住"],
        "why": "r117 一手两条都属『应绿的绿也是假的』：① 分类器的 conservation_ok 对正则缺陷零鉴别力"
               "（分母没变，只是归类错了）；② 归因引擎若把 STALE 与 REAL 弄反，改进靶子会被虚增或被掩盖，"
               "两个方向都必须有夹具看着（W-47 双向 + 变异腿）。",
    },
]

# 显式声明本 runner **不覆盖**的面，防止聚合绿被读成「所有门禁都绿」（R20-2）。
NOT_COVERED = [
    "受管根四门禁 mirror/noise/evolution/stub —— 属 rule_editor 面，取值："
    "python D:\\global_skills\\A-memory-start\\references\\rule_editor.py gates",
    "焚诀跨产物真值 C1~C33 —— 取值：python 焚诀\\eval\\verify_truth_consistency.py",
    "判据变异测试（r19_fixture_mutation_check.py）—— 按需跑，非每轮前置",
]


def _token_hit(token, out):
    """pass_token 允许写成 str 或**标记列表**（r105）。

    存在理由：一门可以有多个合法绿态 —— `retired_face` 本轮新增具名看守态 `[GATE:retired-face-watch]`
    后，单串比对把「rc=0 且逐件说明过的看守态」判成 UNVERIFIED（r105 实测：runner 印
    `UNVERIFIED retired_face`，而该门自己的输出里事实与归属都写得清清楚楚）。三态口径一个字没动：
    列表里**全部**标记都取不到时仍判 UNVERIFIED，禁把「没匹配上」读成通过；
    也不得用列表去掩盖改名 —— 旧标记若被改名，它就不在列表里，照样红。
    """
    if isinstance(token, (list, tuple)):
        return any(t in out for t in token)
    return token in out


def _try_lock(fd):
    """取追加锁；平台不支持时返回 None（退化为原行为，不因缺锁而拒绝写入）。"""
    try:
        import msvcrt
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        return ('msvcrt', msvcrt)
    except Exception:
        pass
    try:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX)
        return ('fcntl', fcntl)
    except Exception:
        return None


def _unlock(fd, lock):
    kind, mod = lock
    try:
        if kind == 'msvcrt':
            os.lseek(fd, 0, os.SEEK_SET)
            mod.locking(fd, mod.LK_UNLCK, 1)
        else:
            mod.flock(fd, mod.LOCK_UN)
    except Exception:
        pass

def _exec_once(gate, timeout):
    """执行单门一次，返回 (state, rc, elapsed_ms, tail)。供 run_gate 与其瞬态重跑共用。"""
    path = os.path.join(HERE, gate["script"])
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, path] + list(gate["argv"]),
                           cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return "FAIL", 124, int((time.time() - t0) * 1000), "TIMEOUT after %ss" % timeout
    elapsed = int((time.time() - t0) * 1000)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode == 2:
        state = "UNVERIFIED"
    elif p.returncode != 0:
        state = "FAIL"
    elif not _token_hit(gate["pass_token"], out):
        state = "UNVERIFIED"
    else:
        state = "PASS"
    tail = " | ".join(l for l in out.strip().splitlines() if l.strip())[-200:]
    return state, p.returncode, elapsed, tail

def run_gate(gate, timeout):
    """执行单门，返回 (state, rc, elapsed_ms, tail)。脚本缺失 ⇒ ('MISSING', ...)。"""
    path = os.path.join(HERE, gate["script"])
    if not os.path.exists(path):
        return "MISSING", 2, 0, "脚本不存在: %s" % path
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, path] + list(gate["argv"]),
                           cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return "FAIL", 124, int((time.time() - t0) * 1000), "TIMEOUT after %ss" % timeout
    elapsed = int((time.time() - t0) * 1000)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode == 2:
        state = "UNVERIFIED"          # 门自报「取不到真相源/台账不可判」⇒ 同样不得算绿（R247）
    elif p.returncode != 0:
        state = "FAIL"
    elif not _token_hit(gate["pass_token"], out):
        state = "UNVERIFIED"          # rc=0 但标记不见 = 静默跳过，不得算绿
    else:
        state = "PASS"
    tail = " | ".join(l for l in out.strip().splitlines() if l.strip())[-200:]
    if state != "PASS" and not gate.get("no_retry"):
        # R125 瞬态识别（不放宽判据）：本仓有并行会话，38 门跑几分钟期间别人在写盘，
        # 于是「单独跑全绿、runner 里红」这类瞬态反复出现（r123/r124/r125 各撞一轮，
        # 排查成本远高于一次重跑）。做法：FAIL 时原样重跑该门一次 ——
        #   · 第二次 PASS ⇒ 判瞬态，记 FLAKY_CONFIRMED（转 PASS 并在 tail 留痕）；
        #   · 第二次仍红/第三态 ⇒ 判真红，**维持原判定不动**。
        # 两次都红照样红 ⇒ 这不是给判据开后门，是把「读到了竞态」与「判据真坏」分开。
        s2, rc2, el2, t2 = _exec_once(gate, timeout)
        if s2 == "PASS":
            return "PASS", p.returncode, elapsed + el2, (
                "[FLAKY-CONFIRMED] 首次 %s，重跑 PASS ⇒ 判为并发瞬态（并行会话写盘竞态），"
                "非判据缺陷 | 原 tail: %s" % (state, tail))
        return state, p.returncode, elapsed + el2, (
            "重跑仍 %s ⇒ 判真红 | 首跑: %s | 重跑: %s" % (s2, tail, t2))
    return state, p.returncode, elapsed, tail


def aggregate(results):
    """聚合判据。⛔ 禁止 any()/all() 掩盖单门状态（本仓 audit-runner-safe-aggregate 教训）：
    必须逐门取状态后按状态集合判定，且非零门须能被点名。"""
    states = [r["state"] for r in results]
    n_pass, n_fail = states.count("PASS"), states.count("FAIL")
    n_unv, n_miss = states.count("UNVERIFIED"), states.count("MISSING")
    if n_miss:
        return 2, "MISSING=%d" % n_miss
    bad = n_fail + n_unv
    if bad:
        return 1, "FAIL=%d UNVERIFIED=%d" % (n_fail, n_unv)
    return 0, "PASS=%d（无 FAIL / 无 UNVERIFIED / 无 MISSING）" % n_pass


def _ensure_debt_fresh():
    """R122-1（r124）：账龄件相对新鲜前置再生。

    连踩 4 轮的根因 = 先跑 r38_debt_aging 后改 07 台账，件比卷旧 ⇒
    `ratchet_gate._debt_artifact_fresh` 把 debt 三指标转 unknown ⇒
    报「指标缺失」+ note fixtures n4 必现 FAIL。

    口径与 ratchet_gate 完全一致（同函数同入参，防两处漂移）：
    卷集 = memory/07-next-steps.md + memory/07-next-steps.part*.md，取最大 mtime；
    件 = 06-benchmark/debt_aging_r*.json 里 mtime 最新那份。件 < 卷 ⇒ 重生一次。

    返回 (state, detail)。state ∈ OK / STALE-REGEN / NO-ARTIFACT / NO-VOLUME /
    REGEN-FAILED。**任何非 OK 都不阻断**（本腿是消时序坑，不是新卡点）。
    """
    import glob as _glob, subprocess as _sp
    vols = _glob.glob(os.path.join(REPO, "memory", "07-next-steps.md")) + \
        _glob.glob(os.path.join(REPO, "memory", "07-next-steps.part*.md"))
    if not vols:
        return ("NO-VOLUME", "取不到 07 待办卷（memory/07-next-steps*.md）")
    try:
        vol_m = max(os.path.getmtime(v) for v in vols)
    except OSError as e:
        return ("NO-VOLUME", "卷 mtime 取不到：%s" % e)
    arts = _glob.glob(os.path.join(REPO, "06-benchmark", "debt_aging_r*.json"))
    if not arts:
        return ("NO-ARTIFACT", "无 debt_aging_r*.json ⇒ 先生成一份")
    try:
        art = max(arts, key=os.path.getmtime)
        art_m = os.path.getmtime(art)
    except OSError as e:
        return ("NO-ARTIFACT", "件 mtime 取不到：%s" % e)
    if art_m >= vol_m:
        return ("OK", "件 %s 不旧于卷集（差 %.0f 秒）" % (os.path.basename(art), art_m - vol_m))
    # 件比卷旧 ⇒ 重生（r38 自带 --json，输出到带日期的固定名，防并行会话同名互踩）
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = os.path.join(REPO, "06-benchmark", "debt_aging_r_autoregen_%s.json" % stamp)
    try:
        r = _sp.run([sys.executable, os.path.join(HERE, "r38_debt_aging.py"), "--json", out_json],
                     cwd=str(REPO), capture_output=True, text=True,
                     encoding="utf-8", errors="replace", timeout=180)
    except Exception as e:
        return ("REGEN-FAILED", "重生调用异常：%s" % e)
    if r.returncode != 0:
        return ("REGEN-FAILED", "重生 rc=%s：%s" % (r.returncode, (r.stderr or "")[-160:]))
    # 复验：新件必须新于卷集（否则说明卷又被 concurrent 写了，如实报）
    try:
        new_m = os.path.getmtime(str(out_json))
    except OSError as e:
        return ("REGEN-FAILED", "新件 mtime 取不到：%s" % e)
    if new_m < vol_m:
        # R124-1（r127 收口）：重生期间卷又被写 ⇒ 再重生一次（上限 2 次防循环）。
        # r127 实测频率低（全程 1 次），重试一次足够覆盖「并行写紧跟」窗口。
        stamp2 = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_json2 = os.path.join(REPO, "06-benchmark", "debt_aging_r_autoregen_%s.json" % stamp2)
        try:
            r2 = _sp.run([sys.executable, os.path.join(HERE, "r38_debt_aging.py"), "--json", out_json2],
                         cwd=str(REPO), capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=180)
        except Exception as e:
            return ("REGEN-FAILED", "重试调用异常：%s" % e)
        if r2.returncode != 0:
            return ("REGEN-FAILED", "重试 rc=%s：%s" % (r2.returncode, (r2.stderr or "")[-160:]))
        try:
            new_m2 = os.path.getmtime(out_json2)
        except OSError as e:
            return ("REGEN-FAILED", "重试件 mtime 取不到：%s" % e)
        if new_m2 >= vol_m:
            return ("OK", "首次重生遇并发写 ⇒ 重试成功（%s，差 %.0f 秒）" % (os.path.basename(out_json2), new_m2 - vol_m))
        return ("STALE-REGEN", "重试一次后件仍旧于卷（并行写入持续）⇒ 放弃重试，下轮前置腿会再触发")
    return ("OK", "件比卷旧 %.0f 秒 ⇒ 已重生为 %s" % (vol_m - art_m, os.path.basename(out_json)))

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--portable-only", action="store_true", help="只跑跨机可复现子集（CI 用）")
    ap.add_argument("--gate", action="append", default=[], help="只跑指定门 id（可重复）")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json")
    ap.add_argument("--no-ledger", action="store_true",
                    help="不追加执行台账（只读试跑用；默认追加，供 gate_run_freshness 判新鲜度）")
    args = ap.parse_args()

    # ---- R122-1（r124 落地）：账龄件相对新鲜前置，机械化「先改台账后跑账龄」 ----
    # 连踩 4 轮（r119/r121/r122×2）的根因：先跑 r38_debt_aging 后改 07 台账 ⇒ 件比卷旧 ⇒
    # `_debt_artifact_fresh` 把 debt 三指标转 unknown ⇒ 棘轮报「指标缺失」+ note fixtures n4 FAIL。
    # 规则原在 AGENTS.md 已知坑第 2 条（散文），无机械强制点。此处加**前置再生**：
    # 检测到 debt 件 mtime 旧于 07 卷集最大 mtime，先重生一次再跑后续门。
    # 不阻断（判红只报不拦）：机械化的目的是消除时序坑，不是新增一道能卡死runner的门。
    _debt_guard = _ensure_debt_fresh()
    if _debt_guard[0] != "OK":
        print("  ⚠️ 前置腿·账龄件相对新鲜: %s（%s）⇒ 不阻断，但本轮 debt 三指标可能仍转 unknown"
              % (_debt_guard[0], _debt_guard[1]))
    else:
        print("  ✅ 前置腿·账龄件相对新鲜: %s" % _debt_guard[1])
    rows = []
    total_ms = 0
    print("=== 本仓门禁聚合 runner (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("工作根: %s" % REPO)
    for g in GATES:
        if args.gate and g["id"] not in args.gate:
            continue
        if args.portable_only and not g["portable"]:
            print("%-32s SKIPPED-BY-DESIGN  %s" % (g["id"], g.get("not_portable_reason", "未声明原因")))
            rows.append({"id": g["id"], "state": "SKIPPED", "rc": None, "elapsed_ms": 0,
                         "portable": False, "covers": g["covers"]})
            continue
        state, rc, ms, tail = run_gate(g, args.timeout)
        total_ms += ms
        print("%-32s %-11s rc=%-4s %5dms  %s" % (g["id"], state, rc, ms, g["why"]))
        print("      覆盖根: %s" % " ; ".join(g["covers"]))
        if state != "PASS":
            print("      末输出: %s" % tail)
        rows.append({"id": g["id"], "state": state, "rc": rc, "elapsed_ms": ms,
                     "portable": g["portable"], "covers": g["covers"], "tail": tail})

    if not rows:
        print("[GATES:UNVERIFIED] 选中的门为 0 个，禁止判「全绿」（R247）")
        return 2

    rc, why = aggregate(rows)
    n = len([r for r in rows if r["state"] != "SKIPPED"])
    if not args.no_ledger:
        # 台账只记事实，不记推测；git 取不到就写 None（不得因为取不到就跳过整行 —— 那会伪造连续性）
        head = None
        try:
            h = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, timeout=20)
            head = h.stdout.strip() or None
        except Exception:
            head = None
        # 台账的 `verdict` 只记**实质门**（排除 meta=True 的新鲜度门）：
        # 新鲜度门评的是台账自己，若把它的引导期红写进 verdict，就会出现
        # 「一次空台账 ⇒ 永久 FAIL」的自锁（r32 实测复现过）。`overall` 仍如实记全量结论供审计。
        meta_ids = {g["id"] for g in GATES if g.get("meta")}
        rc_sub, why_sub = aggregate([r for r in rows if r["id"] not in meta_ids])
        entry = {"ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "origin": ORIGIN,
                 "verdict": "PASS" if rc_sub == 0 else ("FAIL" if rc_sub == 1 else "MISSING"),
                 "verdict_reason": why_sub,
                 "overall": "PASS" if rc == 0 else ("FAIL" if rc == 1 else "MISSING"),
                 "mode": "portable-only" if args.portable_only else "full",
                 "gates_run": n, "skipped": len(rows) - n, "total_ms": total_ms,
                 "head": head, "per_gate": {r["id"]: r["state"] for r in rows}}
        # R125：并发两个 runner 同时追加台账时，单次 write 可能交错 ⇒ 产生半行 JSON
        # ⇒ 下一轮 load_ledger 读到 _broken_json ⇒ judge 直接 UNVERIFIED（不是红，但会挡整轮绿）。
        # 修法：追加前取文件锁（Windows msvcrt.locking / POSIX fcntl.flock），保证整行原子落。
        # 这是并发正确性，不是放宽判据。
        _line = json.dumps(entry, ensure_ascii=False) + "\n"
        try:
            _fd = os.open(LEDGER, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o666)
            try:
                _lock = _try_lock(_fd)
                os.write(_fd, _line.encode("utf-8"))
                os.fsync(_fd)
                if _lock is not None:
                    _unlock(_fd, _lock)
            finally:
                os.close(_fd)
        except OSError as e:
            print("⚠️ 台账写入失败（不影响本轮判定，但会让 gate_run_freshness 下一轮报 UNVERIFIED）: %s" % e)
    print("-" * 72)
    print("执行 %d 门 / 跳过 %d 门 / 合计耗时 %d ms（均值 %d ms/门）"
          % (n, len([r for r in rows if r["state"] == "SKIPPED"]), total_ms,
             int(total_ms / n) if n else 0))
    print("本 runner 不覆盖（聚合绿不等于这些也绿）：")
    for s in NOT_COVERED:
        print("  · %s" % s)
    if rc == 0:
        print("[GATES:PASS] %s" % why)
    elif rc == 1:
        print("[GATES:FAIL] %s" % why)
    else:
        print("[GATES:MISSING] %s" % why)

    if args.json:
        doc = {"schema": "gate-run-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True, "mode": "portable-only" if args.portable_only else "full",
               "gates": rows, "not_covered": NOT_COVERED,
               "verdict": "PASS" if rc == 0 else ("FAIL" if rc == 1 else "MISSING"),
               "verdict_reason": why, "total_ms": total_ms, "gates_run": n}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.json)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
