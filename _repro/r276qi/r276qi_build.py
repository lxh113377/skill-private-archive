# -*- coding: utf-8 -*-
import io, json, os, datetime
ROOT = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
S = json.load(io.open(os.path.join(ROOT, "_repro", "r276qi", "work", "r276qi_stats.json"), encoding="utf-8"))
BY = {}
for _f in S["faces"]:
    BY[_f["id"]] = _f
f1, f2, f3, f4, f5 = BY["F1"], BY["F2"], BY["F3"], BY["F4"], BY["F5"]
skroot = "D:/global_skills"
reg = [n for n in sorted(os.listdir(skroot)) if os.path.isdir(os.path.join(skroot, n)) and os.path.isfile(os.path.join(skroot, n, "SKILL.md"))]
sideset = set(n for n in reg if os.path.isfile(os.path.join(skroot, n, ".upstream")))
noside = [n for n in reg if n not in sideset]

def F(fid, name, caliber, reading, ev, extra):
    d = {"face_id": fid, "face": name, "input_file": BY[fid]["file"], "input_state": BY[fid]["input_state"],
         "denom_caliber": caliber, "denom": BY[fid]["denom"], "covered": BY[fid]["covered"],
         "uncovered": BY[fid]["uncovered"], "uncovered_names": BY[fid]["uncovered_names"],
         "reading": reading, "evidence": ev}
    d.update(extra)
    return d

faces = [
 F("F1", "版本通道一（tag，上游 release 标签）",
   "A=版本通道入口：在册且声明 .upstream 的 skill 件数；B=登记口径：在册带 SKILL.md 的全库 skill 件数",
   "37/55 判出版本关系（AHEAD 22 + BEHIND 15）；18/55 上游不发 release ⇒ tag 通道无解；另有 136/191 件无 .upstream 入口（71.2%）根本进不了本通道",
   "已实测：读 r263_declared_upstream_face.json（generated_at 2026-10-29T01:36:49），rows=55 与磁盘 .upstream 扫描同为 55",
   {"denom_registry": f1.get("denom_registry"), "entry_uncovered_n": f1.get("entry_uncovered_n"), "by_rel": f1.get("by_rel")}),
 F("F2", "版本通道二（提交级，免 release 信号）",
   "A=继承 F1 面入口（有 .upstream 的 55 件）；不含登记库余量 136 件",
   "55/55 均有非 UNAVAILABLE 判定（QUIESCENT 45 + UPSTREAM_MOVED 10）；对 F1 的 18 件无 release 件全部给出互补判定 18/18；date_source 全为 git；1 件 capped（计数触页上限，为下限而非精确值）",
   "已实测：读 r271_version_channel2.json（generated_at 2026-10-29T19:06:33），by_verdict 与 unknown_release_covered_n 字段齐",
   {"unknown_release_n": f2.get("unknown_release_n"), "unknown_release_covered_n": f2.get("unknown_release_covered_n"), "date_source_mix": f2.get("date_source_mix"), "capped_n": f2.get("capped_n"), "by_verdict": f2.get("by_verdict")}),
 F("F3", "替代面（候选池矩阵，件级替代结论）",
   "C=全登记库技能件：矩阵 face.local_n=191，与磁盘带 SKILL.md 扫描的 191 同分母（可对账）",
   "166/191 件级唯一匹配（MATCHED）；12 件仅家族级（FAMILY_ONLY）；13 件无 OS 候选（NO_OS_CANDIDATE）⇒ 合计 25/191=13.1% 无件级替代结论；维护过滤剔掉 82 个陈旧/归档候选、影响 58 行",
   "已实测：读 r262_matrix_bodied.json（generated_at 2026-10-28T10:50:11+00:00），conservation.sum_verdicts=191 ok=true",
   {"partial": f3.get("partial"), "partial_names": f3.get("partial_names"), "by_verdict": f3.get("by_verdict"), "maintenance_trimmed_total": f3.get("maintenance_trimmed_total"), "maintenance_rows_affected": f3.get("maintenance_rows_affected")}),
 F("F4", "替代面（侧车语义分类，BEHIND 可读性）",
   "A=继承 F1 面入口（55 件有 .upstream 的 skill）",
   "51/55 已分类（SAME_LINEAGE 47 + TOOL 2 + COLLECTION 2）；4 件 UNKNOWN 交人读（分类器拒绝猜）；BEHIND 且同源 = 13 件（版本落后对它们才有采用含义）",
   "已实测：读 r264_sidecar_semantics.json（generated_at 2026-10-29T02:00:49），by_semantics 与 same_lineage_behind 齐",
   {"by_semantics": f4.get("by_semantics"), "same_lineage_behind_n": f4.get("same_lineage_behind_n")}),
 F("F5", "巡检节奏面（季产物龄期看门狗）",
   "D=受监控季产物面：quarterly*/audit.json 取最新一份（分母=1）",
   "1/1 在限内：最新季产物 06-benchmark/quarterly_r260c/2026Q4/audit.json 龄期 0.3 天 ≤ 上限 100 天，rc=0；但 watch_scope 只覆盖 quarterly*/audit.json 一类，版本三件与替代面两件无龄期看门狗",
   "已实测：读 quarterly_cadence_latest.json（generated_at 2026-10-28T16:26:30，rc=0）；复跑命令 python 05-exec/r260_quarterly_cadence.py 期望 [CADENCE:PASS]",
   {"watch_scope": f5.get("watch_scope"), "newest_audit": f5.get("newest_audit"), "reading": f5.get("reading"), "max_days": f5.get("max_days")}),
]

J = S["joins"]
缺口 = [
 {"id": "G1", "title": "版本通道入口缺口：136/191=71.2% 的件无 .upstream，版本问题对它们无通道",
  "from_reading": "F1 entry_uncovered_n=136 / 分母 191（71.2%）",
  "named": noside[:10], "severity": "高",
  "note": "该 136 件连通道入口都没有；其中 120 件在替代面有件级 MATCHED 候选（可作回填来源），8 件连替代候选也没有（见 G7）"},
 {"id": "G2", "title": "tag 通道内无 release 缺口：18/55=32.7% 上游不发 release，tag 判不了",
  "from_reading": "F1 by_rel.UNKNOWN_UPSTREAM_RELEASE=18 / 分母 55（32.7%）",
  "named": f1.get("uncovered_names"), "severity": "中",
  "note": "已被 F2 提交级通道互补覆盖 18/18（unknown_release_covered_n=18）；但 F2 自身无龄期看门狗（见 G5）"},
 {"id": "G3", "title": "替代面件级缺口：25/191=13.1% 无件级替代结论",
  "from_reading": "F3 NO_OS_CANDIDATE=13 + FAMILY_ONLY=12 = 25 / 分母 191（13.1%）",
  "named": (f3.get("uncovered_names") or []) + (f3.get("partial_names") or []), "severity": "高",
  "note": "13 件无 OS 候选 + 12 件仅家族级；回答「有没有更优替代」时这 25 件给不出名字"},
 {"id": "G4", "title": "侧车语义缺口：4/55=7.3% 分类器拒猜，交人读",
  "from_reading": "F4 by_semantics.UNKNOWN=4 / 分母 55（7.3%）",
  "named": f4.get("uncovered_names"), "severity": "中",
  "note": "这 4 件的 BEHIND/AHEAD 不可直接当作版本落后采用与否的判据"},
 {"id": "G5", "title": "节奏面只盯季产物一件；版本/替代四件无龄期看门狗",
  "from_reading": "F5 watch_scope=[quarterly*/audit.json]（1 类）；F1/F2/F3/F4 的 generated_at 无任何超龄告警面",
  "named": ["r263_declared_upstream_face.json", "r271_version_channel2.json", "r264_sidecar_semantics.json", "r262_matrix_bodied.json"],
  "severity": "高",
  "note": "四件陈旧不会被叫；季度巡检读到的可能是过期读数"},
 {"id": "G6", "title": "无跨面合并决策件：落后/动了/同源/有无替代只能人工 join",
  "from_reading": "join 读数 落后且同源=13、落后且上游动了=2、无tag但上游动了=3；无任何单件把这些合成结论",
  "named": sorted(set(J["落后且同源(BEHIND x SAME_LINEAGE)"]) | set(J["落后且上游动了(BEHIND x UPSTREAM_MOVED)"]) | set(J["无tag但上游动了(UNKNOWN_RELEASE x UPSTREAM_MOVED)"])),
  "severity": "高",
  "note": "「跟还是换」需要同时看四面，现机制缺这一面"},
 {"id": "G7", "title": "两头黑集合：8/191=4.2% 既无版本通道入口也无替代候选",
  "from_reading": "join 无侧车且无替代候选=8 / 分母 191（4.2%）",
  "named": J["无侧车且无替代候选(NOSIDE x NO_OS_CANDIDATE)"], "severity": "高",
  "note": "这些件季度巡检给不出任何可执行结论，须优先补入口或补候选"},
]

改进 = [
 {"id": "I1", "target": "05-exec/r260_quarterly_cadence.py 的 newest_audit()（扩展为多面龄期扫描；禁改既有 06-benchmark 件）",
  "expected_coverage_change": "F5 watch_scope 由 1 类→5 面（audit + r263 + r271 + r264 + r262），任一件超 max_days 判红；F5 覆盖 1→5",
  "verify_cmd": "python 05-exec/r260_quarterly_cadence.py --max-days 100 --json _repro/r276qi/work/r276qi_cad_after.json",
  "verify_expect": "期望末行 [CADENCE:PASS] 且 reading 列出 5 面",
  "negctrl": "把 _repro/r276qi/work/r276qi_negctrl 负控目录里某一面 generated_at 造旧 >100 天 ⇒ 期望 [CADENCE:FAIL] 并点名该件"},
 {"id": "I2", "target": "新增 05-exec/r277_sidecar_backfill_proposal.py（只读：用 r262 件级 MATCHED 候选反查候选 .upstream，产出建议件，不改受管根）",
  "expected_coverage_change": "F1 入口覆盖 55/191 具备回填来源 120 件（join 无侧车但有件级替代=120）⇒ 入口未覆盖 136 可降至理论 16",
  "verify_cmd": "python -B _repro/r276qi/work/r276qi_collect.py --out _repro/r276qi/work/r276qi_stats_after.json",
  "verify_expect": "期望末行 [QI:PASS] 且 F1 entry_uncovered_n < 136",
  "negctrl": "把建议件路径指向不存在 ⇒ 期望 [QI:UNVERIFIED] unverified=[F1]，禁止读成无缺口"},
 {"id": "I3", "target": "新增 06-benchmark/r277_quarterly_verdict.json（把 F1.rel x F2.verdict x F4.semantics x F3.verdict 合成每件跟/换/观察/无解四态）",
  "expected_coverage_change": "G6/G7 合并为单件四态结论；缺口条目由 7 条收敛到约 4 条（G1/G3/G5 仍在）",
  "verify_cmd": null, "verify_cmd_unavailable": "该面此列原指向一件在任何盘上都已不存在的脚本（r300 实测），故置空且不留路径形态文字",
  "verify_expect": "期望末行 [VERDICT] rows=191",
  "negctrl": "去掉 F4 语义面重跑 ⇒ 期望报语义缺失态而非默认 SAME_LINEAGE"},
]

executability = [
 {"face": "F1 版本通道一(tag)", "produce_cmd": "python 05-exec/r263_declared_upstream_face.py", "produce_file": "06-benchmark/r263_declared_upstream_face.json",
  "consumer": "F2/F4（读 face_in）+ 人读", "missing_degrade": "自身无 .upstream ⇒ rc=2 [UPSTREAM:UNVERIFIED]；对下游 F2/F4 各报 [VC2/SEM:UNVERIFIED] rc=2（实测负控）"},
 {"face": "F2 版本通道二(提交级)", "produce_cmd": "python 05-exec/r271_version_channel2.py", "produce_file": "06-benchmark/r271_version_channel2.json",
  "consumer": "人读/季度决策", "missing_degrade": "r263 输入缺 ⇒ rc=2 [VC2:UNVERIFIED]（已实测负控）"},
 {"face": "F3 替代面(候选池矩阵)", "produce_cmd": "python 05-exec/r114_replacement_scan.py --offline", "produce_file": "06-benchmark/r262_matrix_bodied.json",
  "consumer": "r262_license_body_pack.py + 人读/替代结论", "missing_degrade": "缓存缺则须联网；面缺 ⇒ 决策件须返回 UNVERIFIED，禁补 0"},
 {"face": "F4 替代面(侧车语义)", "produce_cmd": "python 05-exec/r264_sidecar_semantics.py", "produce_file": "06-benchmark/r264_sidecar_semantics.json",
  "consumer": "人读/BEHIND 语义过滤", "missing_degrade": "r263 输入缺 ⇒ rc=2 [SEM:UNVERIFIED]（已实测负控）"},
 {"face": "F5 巡检节奏面", "produce_cmd": "python 05-exec/r260_quarterly_cadence.py --json 06-benchmark/quarterly_cadence_latest.json", "produce_file": "06-benchmark/quarterly_cadence_latest.json",
  "consumer": "CI/人", "missing_degrade": "季产物缺或 generated_at 不可析 ⇒ rc=2 [CADENCE:UNVERIFIED]，禁记绿"},
]

doc = {
 "schema": "quarterly-inspection-dryrun-v1",
 "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
 "provenance_cmd": "python -B _repro/r276qi/work/r276qi_collect.py --out _repro/r276qi/work/r276qi_stats.json && python -B _repro/r276qi/work/r276qi_build.py",
 "readonly": True,
 "scope": {"bench_dir": "06-benchmark", "skills_root": "D:/global_skills", "registry": S["registry"]},
 "caliber_note": "R260-9 分母点名 —— 全库口径=191（D:/global_skills 下含 SKILL.md 的目录数，与 r262 face.local_n=191 同分母可对账）；通道入口口径=55（声明 .upstream 的件数，r263 自报 55 与磁盘扫描一致）；维护范围口径=77（00-scope/自建skill清单.md，HIGH 51 + MID 26）本演练未采用，改用则 F1/F2/F4 与 F3 分母须全部重算，禁混用；F5 分母=1（受监控季产物面最新一份）。",
 "faces": faces,
 "缺口": 缺口,
 "改进": 改进,
 "executability": executability,
 "negative_control": {
   "method": "把 F4 的输入件 r264_sidecar_semantics.json 指向不存在（_repro/r276qi/work/r276qi_negctrl 副本目录中故意缺失该件）",
   "observed": "F4 input_state=ABSENT denom=None covered=None uncovered=None；[QI:UNVERIFIED] unverified=[F4]；RC=2",
   "positive_leg": "四面齐 ⇒ [QI:PASS] faces=5 unverified=0；RC=0",
   "assertion": "输入件缺失 / 不可析一律 UNVERIFIED，绝不静默当成无缺口（R247）"},
 "joins": J,
 "evidence_states": {"F1": "已实测", "F2": "已实测", "F3": "已实测", "F4": "已实测", "F5": "已实测", "negative_control": "已实测"},
}
OUT = os.path.join(ROOT, "06-benchmark", "r276_quarterly_inspection_dryrun.json")
io.open(OUT, "w", encoding="utf-8", newline=chr(10)).write(json.dumps(doc, ensure_ascii=False, indent=1))
print("[BUILD] faces=%d 缺口=%d 改进=%d exec=%d" % (len(faces), len(缺口), len(改进), len(executability)))
print("JSON ->", OUT)